"""Data coordinator for the DIVA integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
import logging
from pathlib import Path
import re
from typing import Any

from homeassistant.components.calendar.const import (
    CalendarEntityFeature,
    DATA_COMPONENT as CALENDAR_DATA_COMPONENT,
    EVENT_DESCRIPTION,
    EVENT_END,
    EVENT_LOCATION,
    EVENT_START,
    EVENT_SUMMARY,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    APPROVAL_ACTION_CARE,
    APPROVAL_ACTION_CHECKLIST,
    APPROVAL_ACTION_FEED,
    APPROVAL_ACTION_FINISH_WALK,
    APPROVAL_ACTION_MEDICATION,
    APPROVAL_ACTION_VACCINE,
    CALENDAR_IMPORT_POLL_INTERVAL,
    CALENDAR_CONFLICT_RESOLUTION_CALENDAR_WINS,
    CALENDAR_CONFLICT_RESOLUTION_DISMISS,
    CALENDAR_CONFLICT_RESOLUTION_DIVA_WINS,
    CALENDAR_SOURCE_OF_TRUTH_CALENDAR,
    CALENDAR_SOURCE_OF_TRUTH_DIVA,
    CALENDAR_SOURCE_OF_TRUTH_MANUAL_REVIEW,
    CALENDAR_SYNC_DEFAULT_DAYS,
    CAMERA_EVENT_CALENDAR_SYNCED,
    CAMERA_EVENT_OPERATIONS_REPORT,
    CONF_ACTION_NAME,
    CONF_BIRTHDATE,
    CONF_DOSE,
    CONF_DUE_DATE,
    CONF_HUB_NAME,
    CONF_MEDICATION_COURSES,
    CONF_MEDICATION_NAME,
    CONF_MEDICATION_ROUTE,
    CONF_MEDICATION_TIMES,
    CONF_NAME,
    CONF_NOTES,
    CONF_PETS,
    CONF_PET_ID,
    CONF_PET_SCHEMA,
    CONF_RECURRENCE_MONTHS,
    CONF_ROUTINE_CATEGORY,
    CONF_SHOW_EDITOR_IN_SIDEBAR,
    CONF_START_DATE,
    CONF_END_DATE,
    CONF_VACCINE_DOSE_ID,
    CONF_VACCINE_NAME,
    CONF_VACCINE_OVERRIDES,
    DOMAIN,
    HUB_IDENTIFIER_PREFIX,
    INTEGRATION_VERSION,
    RUNTIME_JSON_FILENAME,
    ROUTINE_TYPE_CARE,
    ROUTINE_TYPE_FEED,
    ROUTINE_TYPE_MEDICATION,
    ROUTINE_TYPE_WALK,
    RUNTIME_STORAGE_BACKEND,
    SIGNAL_CAPTURE_FOOD_REFERENCE,
    SIGNAL_CAPTURE_WATER_REFERENCE,
    PET_SCHEMA_VERSION,
    STORAGE_KEY,
    STORAGE_VERSION,
    UPDATE_INTERVAL,
)
from .events import build_notice_payload, notice_event_type
from .pet import (
    CameraAnalysis,
    PetContext,
    PetEngine,
    PetNotice,
    PetProfile,
    ScheduleException,
    ScheduledEvent,
    PetSnapshot,
    analyze_frame,
    decode_image_bytes,
    generate_pet_id,
    normalize_behavior_type,
    normalize_pet_config_record,
    parse_schedule_exceptions,
    serialize_diva_entry_settings_v3,
    serialize_pet_config_record_v3,
)
from .recommendations import evaluate_pet
from .storage import DivaJSONStorage

_LOGGER = logging.getLogger(__name__)

HOME_STATES = {"home", "on"}
ACTIVE_SIGNAL_STATES = {"on", "problem", "detected", "true", "alert"}
BLE_ROOM_PRIORITY = 5
CAMERA_ROOM_INTERACTION_PRIORITY = 6
CAMERA_ROOM_MOTION_PRIORITY = 3
ROOM_FUSION_MULTI_SOURCE_BONUS = 1
ROOM_FUSION_BLE_CAMERA_BONUS = 1
ROOM_FUSION_STICKY_BONUS = 1
CAMERA_ROOM_SIGNAL_WINDOW_SECONDS = 180.0
CAMERA_ROOM_MOTION_THRESHOLD = 0.08
REPORT_JOB_HISTORY_LIMIT = 40
GENERATED_REPORT_HISTORY_LIMIT = 20


@dataclass(slots=True)
class PetCameraRuntime:
    """Runtime state for camera monitoring of a pet."""

    last_image: bytes | None = None
    last_analysis: dict[str, Any] = field(default_factory=dict)
    previous_frame: Any = None
    food_reference: Any = None
    water_reference: Any = None
    signals: set[str] = field(default_factory=set)


@dataclass(slots=True)
class ManagedPet:
    """Runtime wrapper for a configured pet."""

    profile: PetProfile
    engine: PetEngine
    camera: PetCameraRuntime = field(default_factory=PetCameraRuntime)


class DivaCoordinator(DataUpdateCoordinator[dict[str, PetSnapshot]]):
    """Manage runtime state for the DIVA multi-pet hub."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the DIVA coordinator."""
        self.entry = entry
        settings = _entry_settings(entry)
        self.hub_name: str = settings[CONF_HUB_NAME]
        self.hub_identifier = f"{HUB_IDENTIFIER_PREFIX}_{entry.entry_id}"
        self._pets: dict[str, ManagedPet] = {
            pet_data[CONF_PET_ID]: ManagedPet(
                profile := PetProfile.from_dict(pet_data),
                PetEngine(profile),
            )
            for pet_data in settings[CONF_PETS]
        }
        self._store: Store[dict[str, Any]] = Store(
            hass,
            STORAGE_VERSION,
            f"{STORAGE_KEY}.{entry.entry_id}",
        )
        self._runtime_store = DivaJSONStorage(hass, RUNTIME_JSON_FILENAME)
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            config_entry=entry,
            update_interval=UPDATE_INTERVAL,
            always_update=False,
        )

    async def _async_setup(self) -> None:
        """Restore persisted runtime state before the first refresh."""
        stored = await self._runtime_store.async_load_entry(self.entry.entry_id)
        needs_runtime_migration = _stored_runtime_entry_needs_migration(stored)
        stored_pets = stored.get("pets", {})
        imported_legacy_store = False
        if not stored_pets:
            legacy = await self._store.async_load() or {}
            legacy_pets = legacy.get(CONF_PETS, {})
            if isinstance(legacy_pets, dict):
                stored_pets = {
                    pet_id: {"runtime": payload}
                    for pet_id, payload in legacy_pets.items()
                    if isinstance(payload, dict)
                }
                imported_legacy_store = bool(stored_pets)
        for pet_id, managed in self._pets.items():
            stored_pet = stored_pets.get(pet_id, {})
            if isinstance(stored_pet, dict) and "runtime" in stored_pet:
                managed.engine.restore(stored_pet.get("runtime"))
            elif isinstance(stored_pet, dict):
                managed.engine.restore(stored_pet)
        if needs_runtime_migration or imported_legacy_store:
            await self._async_save_runtime_state()

    async def _async_update_data(self) -> dict[str, PetSnapshot]:
        """Refresh runtime data and return the latest snapshot map."""
        now = dt_util.now()
        snapshots: dict[str, PetSnapshot] = {}
        notices_to_fire: list[tuple[PetProfile, PetNotice]] = []

        for pet_id, managed in self._pets.items():
            notices: list[PetNotice] = []
            if managed.profile.has_external_calendars:
                notices.extend(await self._async_poll_external_calendars(pet_id, managed, now))
            if managed.profile.camera_entity_id:
                analysis = await self._async_run_camera_analysis(managed)
                if analysis is not None:
                    notices.extend(managed.engine.apply_camera_analysis(now, analysis))
                    managed.camera.last_analysis = {
                        "captured_at_ts": now.timestamp(),
                        "food_empty": analysis.food_empty,
                        "water_empty": analysis.water_empty,
                        "food_interaction": analysis.food_interaction,
                        "water_interaction": analysis.water_interaction,
                        **analysis.debug,
                    }

            context = self._build_pet_context(managed, now)
            snapshot, refresh_notices = managed.engine.refresh(now, context)
            notices.extend(refresh_notices)
            snapshot, insight_notices, active_anomalies, sent_recommendations = evaluate_pet(
                snapshot,
                managed.engine.state,
                now,
                context,
            )
            notices.extend(insight_notices)

            managed.engine.update_active_anomalies(active_anomalies)
            managed.engine.update_recommendations_sent(sent_recommendations)
            managed.engine.set_stress_score(snapshot.stress_score)
            managed.engine.append_records(notices)
            snapshots[pet_id] = snapshot
            notices_to_fire.extend((managed.profile, notice) for notice in notices)

        await self._async_save_runtime_state()
        await self._async_fire_notices(notices_to_fire)
        return snapshots

    @property
    def pet_ids(self) -> tuple[str, ...]:
        """Return known pet ids."""
        return tuple(self._pets)

    @property
    def pets(self) -> dict[str, ManagedPet]:
        """Return managed pets."""
        return self._pets

    def get_snapshot(self, pet_id: str) -> PetSnapshot:
        """Return the latest snapshot for a pet."""
        return self.data[pet_id]

    def get_profile(self, pet_id: str) -> PetProfile:
        """Return the profile for a pet."""
        return self._pets[pet_id].profile

    def get_camera_image(self, pet_id: str) -> bytes | None:
        """Return the latest analyzed camera image for a pet."""
        return self._pets[pet_id].camera.last_image

    def get_camera_analysis(self, pet_id: str) -> dict[str, Any]:
        """Return the latest camera analysis for a pet."""
        return self._pets[pet_id].camera.last_analysis

    def get_timeline(self, pet_id: str, *, hours: int = 24) -> list[dict[str, Any]]:
        """Return the next timeline events for a pet."""
        now = dt_util.now()
        end = now + timedelta(hours=hours)
        events = self.timeline_events(pet_id, now, end)
        return [event.as_dict() for event in events]

    def timeline_events(self, pet_id: str, start, end):
        """Return raw scheduled events for a pet and time window."""
        managed = self._pets[pet_id]
        return managed.engine.timeline_events(start, end, self._build_pet_context(managed))

    async def async_register_devices(self) -> None:
        """Register the hub and pet devices in the device registry."""
        device_registry = dr.async_get(self.hass)
        device_registry.async_get_or_create(
            config_entry_id=self.entry.entry_id,
            identifiers={(DOMAIN, self.hub_identifier)},
            name=self.hub_name,
            manufacturer="DIVA",
            model="Pet Guardian Hub",
            sw_version=INTEGRATION_VERSION,
            entry_type=DeviceEntryType.SERVICE,
        )
        for pet_id, managed in self._pets.items():
            profile = managed.profile
            device_registry.async_get_or_create(
                config_entry_id=self.entry.entry_id,
                identifiers={(DOMAIN, pet_id)},
                name=profile.name,
                manufacturer="DIVA",
                model=f"{profile.species.title()} Guardian Profile",
                sw_version=INTEGRATION_VERSION,
                via_device=(DOMAIN, self.hub_identifier),
            )

    async def async_feed_now(
        self,
        pet_id: str,
        grams: float | None = None,
        *,
        meal_type: str | None = None,
        food_name: str | None = None,
        requested_by: str | None = None,
        bypass_approval: bool = False,
    ) -> None:
        """Trigger an immediate feeding for a pet."""
        managed = self._pets[pet_id]
        now = dt_util.now()
        if not bypass_approval and self._requires_approval(managed, APPROVAL_ACTION_FEED):
            await self._async_apply_pet_notices(
                pet_id,
                managed.engine.queue_action_approval(
                    now,
                    action_name=APPROVAL_ACTION_FEED,
                    category=ROUTINE_TYPE_FEED,
                    payload={
                        "grams": grams,
                        "meal_type": meal_type,
                        "food_name": food_name,
                    },
                    requested_by=requested_by,
                    note=food_name or meal_type,
                ),
            )
            return
        await self._async_apply_pet_notices(
            pet_id,
            managed.engine.feed_now(now, grams, meal_type=meal_type, food_name=food_name),
            capture_food_reference=True,
        )

    async def async_skip_feeding(self, pet_id: str) -> None:
        """Skip the current feeding window for a pet."""
        await self._async_apply_pet_notices(pet_id, self._pets[pet_id].engine.skip_feeding(dt_util.now()))

    async def async_delay_feeding(self, pet_id: str, minutes: int) -> None:
        """Delay the next feeding for a pet."""
        await self._async_apply_pet_notices(
            pet_id,
            self._pets[pet_id].engine.delay_feeding(dt_util.now(), minutes),
        )

    async def async_start_walk(self, pet_id: str) -> None:
        """Start a walk for a pet."""
        await self._async_apply_pet_notices(pet_id, self._pets[pet_id].engine.start_walk(dt_util.now()))

    async def async_finish_walk(
        self,
        pet_id: str,
        *,
        requested_by: str | None = None,
        bypass_approval: bool = False,
    ) -> None:
        """Finish a walk for a pet."""
        managed = self._pets[pet_id]
        now = dt_util.now()
        if not bypass_approval and self._requires_approval(managed, APPROVAL_ACTION_FINISH_WALK):
            await self._async_apply_pet_notices(
                pet_id,
                managed.engine.queue_action_approval(
                    now,
                    action_name=APPROVAL_ACTION_FINISH_WALK,
                    category=ROUTINE_TYPE_WALK,
                    payload={},
                    requested_by=requested_by,
                ),
            )
            return
        await self._async_apply_pet_notices(pet_id, managed.engine.finish_walk(now))

    async def async_refill_food(self, pet_id: str) -> None:
        """Mark food as refilled for a pet."""
        await self._async_apply_pet_notices(
            pet_id,
            self._pets[pet_id].engine.refill_food(dt_util.now()),
            capture_food_reference=True,
        )

    async def async_refill_water(self, pet_id: str) -> None:
        """Mark water as refilled for a pet."""
        await self._async_apply_pet_notices(
            pet_id,
            self._pets[pet_id].engine.refill_water(dt_util.now()),
            capture_water_reference=True,
        )

    async def async_set_food_portion(self, pet_id: str, grams: float) -> None:
        """Update the configured food portion for a pet."""
        self._pets[pet_id].engine.set_food_portion(grams)
        await self._async_persist_and_refresh()

    async def async_set_daily_calories(self, pet_id: str, calories: float) -> None:
        """Update the configured daily calories for a pet."""
        self._pets[pet_id].engine.set_daily_calories(calories)
        await self._async_persist_and_refresh()

    async def async_set_weight_goal_min(self, pet_id: str, value: float) -> None:
        """Update the lower weight goal bound for a pet."""
        self._pets[pet_id].engine.set_weight_goal_min(value)
        await self._async_persist_and_refresh()

    async def async_set_weight_goal_max(self, pet_id: str, value: float) -> None:
        """Update the upper weight goal bound for a pet."""
        self._pets[pet_id].engine.set_weight_goal_max(value)
        await self._async_persist_and_refresh()

    async def async_set_diet_mode(self, pet_id: str, diet_mode: str) -> None:
        """Update the configured diet mode for a pet."""
        self._pets[pet_id].engine.set_diet_mode(diet_mode)
        await self._async_persist_and_refresh()

    async def async_set_manual_mode(self, pet_id: str, mode: str) -> None:
        """Update the active manual mode for a pet."""
        self._pets[pet_id].engine.set_manual_mode(mode)
        await self._async_persist_and_refresh()

    async def async_add_schedule_exception(self, pet_id: str, payload: dict[str, Any]) -> None:
        """Persist a one-off schedule exception for a pet."""
        parsed = parse_schedule_exceptions([payload], pet_id=pet_id)
        if not parsed:
            return
        exception: ScheduleException = parsed[0]
        self._pets[pet_id].engine.add_runtime_exception(exception)
        await self._async_persist_and_refresh()

    async def async_log_care_action(
        self,
        pet_id: str,
        action: str,
        *,
        actor: str | None = None,
        note: str | None = None,
        category: str = "care",
        bypass_approval: bool = False,
    ) -> None:
        """Append a care journal item for a pet."""
        managed = self._pets[pet_id]
        now = dt_util.now()
        if not bypass_approval and self._requires_approval(managed, APPROVAL_ACTION_CARE):
            await self._async_apply_pet_notices(
                pet_id,
                managed.engine.queue_action_approval(
                    now,
                    action_name=APPROVAL_ACTION_CARE,
                    category=category,
                    payload={
                        "action": action,
                        "actor": actor,
                        "note": note,
                        "category": category,
                    },
                    requested_by=actor,
                    note=note or action,
                ),
            )
            return
        await self._async_apply_pet_notices(
            pet_id,
            managed.engine.log_care_action(
                now,
                action,
                actor=actor,
                note=note,
                category=category,
            ),
        )

    async def async_log_medication_dose(
        self,
        pet_id: str,
        medication_name: str,
        *,
        dose: str | None = None,
        actor: str | None = None,
        note: str | None = None,
        bypass_approval: bool = False,
    ) -> None:
        """Log a medication administration for a pet."""
        managed = self._pets[pet_id]
        now = dt_util.now()
        if not bypass_approval and self._requires_approval(managed, APPROVAL_ACTION_MEDICATION):
            await self._async_apply_pet_notices(
                pet_id,
                managed.engine.queue_action_approval(
                    now,
                    action_name=APPROVAL_ACTION_MEDICATION,
                    category=ROUTINE_TYPE_MEDICATION,
                    payload={
                        "medication_name": medication_name,
                        "dose": dose,
                        "actor": actor,
                        "note": note,
                    },
                    requested_by=actor,
                    note=note or medication_name,
                ),
            )
            return
        await self._async_apply_pet_notices(
            pet_id,
            managed.engine.log_medication_dose(
                now,
                medication_name,
                dose=dose,
                actor=actor,
                note=note,
            ),
        )

    async def async_log_symptom(
        self,
        pet_id: str,
        symptom_name: str,
        *,
        severity_score: float,
        duration_hours: float | None = None,
        note: str | None = None,
        source: str = "manual",
    ) -> None:
        """Record a symptom observation for a pet."""
        await self._async_apply_pet_notices(
            pet_id,
            self._pets[pet_id].engine.log_symptom(
                dt_util.now(),
                symptom_name,
                severity_score=severity_score,
                duration_hours=duration_hours,
                note=note,
                source=source,
            ),
        )

    async def async_report_behavior(
        self,
        pet_id: str,
        behavior_type: str,
        *,
        severity: str = "warning",
        message: str | None = None,
        source: str = "manual",
    ) -> None:
        """Record a behavior anomaly for a pet."""
        await self._async_apply_pet_notices(
            pet_id,
            self._pets[pet_id].engine.report_behavior(
                dt_util.now(),
                behavior_type,
                severity=severity,
                message=message,
                source=source,
            ),
        )

    async def async_observe_behavior(
        self,
        pet_id: str,
        behavior_type: str,
        *,
        severity: str = "warning",
        message: str | None = None,
        source: str = "vision_pipeline",
        confidence: float = 0.85,
        duration_seconds: int | None = None,
        model_name: str | None = None,
        evidence: dict[str, Any] | None = None,
    ) -> None:
        """Record an external behavior observation for a pet."""
        await self._async_apply_pet_notices(
            pet_id,
            self._pets[pet_id].engine.observe_behavior(
                dt_util.now(),
                behavior_type,
                severity=severity,
                message=message,
                source=source,
                confidence=confidence,
                duration_seconds=duration_seconds,
                model_name=model_name,
                evidence=evidence,
            ),
        )

    async def async_start_recovery_plan(
        self,
        pet_id: str,
        title: str,
        *,
        expected_days: int,
        note: str | None = None,
    ) -> None:
        """Start a recovery plan for a pet."""
        await self._async_apply_pet_notices(
            pet_id,
            self._pets[pet_id].engine.start_recovery_plan(
                dt_util.now(),
                title,
                expected_days=expected_days,
                note=note,
            ),
        )

    async def async_complete_vaccine_dose(
        self,
        pet_id: str,
        *,
        dose_id: str | None = None,
        vaccine_name: str | None = None,
        note: str | None = None,
        requested_by: str | None = None,
        bypass_approval: bool = False,
    ) -> None:
        """Mark a vaccine dose as completed."""
        managed = self._pets[pet_id]
        now = dt_util.now()
        if not bypass_approval and self._requires_approval(managed, APPROVAL_ACTION_VACCINE):
            await self._async_apply_pet_notices(
                pet_id,
                managed.engine.queue_action_approval(
                    now,
                    action_name=APPROVAL_ACTION_VACCINE,
                    category=ROUTINE_TYPE_MEDICATION,
                    payload={
                        "dose_id": dose_id,
                        "vaccine_name": vaccine_name,
                        "note": note,
                    },
                    requested_by=requested_by,
                    note=note or vaccine_name or dose_id,
                ),
            )
            return
        await self._async_apply_pet_notices(
            pet_id,
            managed.engine.complete_vaccine_dose(
                now,
                dose_id=dose_id,
                vaccine_name=vaccine_name,
                note=note,
            ),
        )

    async def async_complete_checklist_item(
        self,
        pet_id: str,
        checklist_id: str,
        *,
        actor: str | None = None,
        note: str | None = None,
        source: str = "manual",
        bypass_approval: bool = False,
    ) -> None:
        """Mark an operational checklist item complete."""
        managed = self._pets[pet_id]
        now = dt_util.now()
        if not bypass_approval and self._checklist_requires_approval(managed, checklist_id):
            await self._async_apply_pet_notices(
                pet_id,
                managed.engine.queue_action_approval(
                    now,
                    action_name=APPROVAL_ACTION_CHECKLIST,
                    category=self._checklist_category(managed, checklist_id),
                    payload={
                        "checklist_id": checklist_id,
                        "actor": actor,
                        "note": note,
                        "source": source,
                    },
                    requested_by=actor,
                    note=note or checklist_id,
                    source=source,
                ),
            )
            return
        await self._async_apply_pet_notices(
            pet_id,
            managed.engine.complete_checklist_item(
                now,
                checklist_id,
                actor=actor,
                note=note,
                source=source,
            ),
        )

    async def async_approve_action(
        self,
        pet_id: str,
        approval_id: str,
        *,
        approved_by: str | None = None,
        note: str | None = None,
    ) -> None:
        """Approve and execute a previously queued action."""
        managed = self._pets[pet_id]
        now = dt_util.now()
        approval = managed.engine.get_pending_approval(approval_id)
        action_name = str(approval.get(CONF_ACTION_NAME, "")).strip()
        action_payload = dict(approval.get("payload", {}))
        action_notices, capture_food_reference, capture_water_reference = self._execute_approved_action(
            managed,
            now,
            action_name=action_name,
            payload=action_payload,
        )
        _approved, approval_notices = managed.engine.approve_pending_action(
            now,
            approval_id,
            approved_by=approved_by,
            note=note,
        )
        await self._async_apply_pet_notices(
            pet_id,
            [*approval_notices, *action_notices],
            capture_food_reference=capture_food_reference,
            capture_water_reference=capture_water_reference,
        )

    async def async_generate_vet_report(
        self,
        pet_id: str,
        *,
        report_format: str = "txt",
        history_days: int = 30,
    ) -> str:
        """Generate a text-first vet report for automation handoff."""
        return await self._async_generate_report(
            pet_id,
            report_kind="vet",
            report_format=report_format,
            history_days=history_days,
            build_report=lambda now, snapshot, managed: managed.engine.build_vet_report(
                now,
                snapshot,
                history_days=history_days,
            ),
            success_notice_name="vet_report_generated",
        )

    async def async_generate_operations_report(
        self,
        pet_id: str,
        *,
        report_format: str = "txt",
        history_days: int = 7,
    ) -> str:
        """Generate an operations summary report for automation handoff."""
        return await self._async_generate_report(
            pet_id,
            report_kind="operations",
            report_format=report_format,
            history_days=history_days,
            build_report=lambda now, snapshot, managed: managed.engine.build_operations_report(
                now,
                snapshot,
                history_days=history_days,
            ),
            success_notice_name=CAMERA_EVENT_OPERATIONS_REPORT,
        )

    async def _async_generate_report(
        self,
        pet_id: str,
        *,
        report_kind: str,
        report_format: str,
        history_days: int,
        build_report,
        success_notice_name: str,
    ) -> str:
        """Generate a report file and track its lifecycle."""
        managed = self._pets[pet_id]
        now = dt_util.now()
        job = self._start_report_job(
            managed,
            report_kind=report_kind,
            report_format=report_format,
            history_days=history_days,
            requested_at=now,
        )
        await self._async_save_runtime_state()
        await self.async_request_refresh()
        if self.data and pet_id in self.data:
            snapshot = self.data[pet_id]
        else:
            snapshot, refresh_notices = managed.engine.refresh(now, self._build_pet_context(managed, now))
            managed.engine.append_records(refresh_notices)
        try:
            report = build_report(now, snapshot, managed)
            report_path = await self._async_write_report_file(
                report_format=report_format,
                report=report,
            )
        except Exception as err:
            finished_at = dt_util.now()
            self._finish_report_job(
                managed,
                job_id=job["job_id"],
                status="failed",
                finished_at=finished_at,
                error=str(err),
            )
            notices = [
                PetNotice(
                    category="event",
                    name=f"{report_kind}_report_failed",
                    timestamp=finished_at.isoformat(),
                    severity="warning",
                    message=str(err),
                    data={
                        "job_id": job["job_id"],
                        "report_kind": report_kind,
                        "report_format": report_format,
                        "history_days": history_days,
                        "error": str(err),
                    },
                )
            ]
            managed.engine.append_records(notices)
            await self._async_save_runtime_state()
            await self._async_fire_notices((managed.profile, notice) for notice in notices)
            await self.async_request_refresh()
            raise

        finished_at = dt_util.now()
        self._finish_report_job(
            managed,
            job_id=job["job_id"],
            status="completed",
            finished_at=finished_at,
            report_path=report_path,
            caption=report["caption"],
        )
        managed.engine.state.generated_reports.append(
            {
                "job_id": job["job_id"],
                "path": report_path,
                "generated_at": finished_at.isoformat(),
                "format": report_format,
                "history_days": history_days,
                "caption": report["caption"],
                "report_kind": report_kind,
                "status": "completed",
            }
        )
        managed.engine.state.generated_reports = managed.engine.state.generated_reports[-GENERATED_REPORT_HISTORY_LIMIT:]
        notices = [
            PetNotice(
                category="event",
                name=success_notice_name,
                timestamp=finished_at.isoformat(),
                data={
                    "job_id": job["job_id"],
                    "report_path": report_path,
                    "report_format": report_format,
                    "history_days": history_days,
                    "report_kind": report_kind,
                    "telegram_caption": report["caption"],
                    **report["summary"],
                },
            )
        ]
        managed.engine.append_records(notices)
        await self._async_save_runtime_state()
        await self._async_fire_notices((managed.profile, notice) for notice in notices)
        await self.async_request_refresh()
        return report_path

    async def _async_write_report_file(
        self,
        *,
        report_format: str,
        report: dict[str, Any],
    ) -> str:
        """Write a report file in the requested format."""
        reports_dir = self.hass.config.path("diva_reports")
        if report_format == "txt":
            return await self.hass.async_add_executor_job(
                _write_text_report_file,
                reports_dir,
                report["filename"],
                report["content"],
            )
        if report_format == "pdf":
            pdf_filename = report["filename"].replace(".txt", ".pdf")
            return await self.hass.async_add_executor_job(
                _write_pdf_report_file,
                reports_dir,
                pdf_filename,
                report["content"],
                report["caption"],
            )
        raise ValueError("Unsupported report format")

    def _start_report_job(
        self,
        managed: ManagedPet,
        *,
        report_kind: str,
        report_format: str,
        history_days: int,
        requested_at,
    ) -> dict[str, Any]:
        """Create a running report job record."""
        job = {
            "job_id": _report_job_id(managed.profile.pet_id, report_kind, requested_at),
            "report_kind": report_kind,
            "report_format": report_format,
            "history_days": history_days,
            "status": "running",
            "requested_at": requested_at.isoformat(),
        }
        managed.engine.state.report_jobs.append(job)
        managed.engine.state.report_jobs = managed.engine.state.report_jobs[-REPORT_JOB_HISTORY_LIMIT:]
        return job

    def _finish_report_job(
        self,
        managed: ManagedPet,
        *,
        job_id: str,
        status: str,
        finished_at,
        report_path: str | None = None,
        caption: str | None = None,
        error: str | None = None,
    ) -> None:
        """Update a tracked report job with its terminal state."""
        for record in reversed(managed.engine.state.report_jobs):
            if record.get("job_id") != job_id:
                continue
            record["status"] = status
            record["finished_at"] = finished_at.isoformat()
            if report_path is not None:
                record["report_path"] = report_path
            if caption is not None:
                record["caption"] = caption
            if error is not None:
                record["error"] = error
            else:
                record.pop("error", None)
            return

    async def async_upsert_medication_course(self, pet_id: str, payload: dict[str, Any]) -> None:
        """Create or replace a medication course in the pet profile."""
        await self._async_update_pet_profile(
            pet_id,
            lambda pet: _upsert_medication_course_dict(pet, payload),
        )

    async def async_remove_medication_course(self, pet_id: str, medication_name: str) -> None:
        """Remove a medication course by name."""
        await self._async_update_pet_profile(
            pet_id,
            lambda pet: _remove_medication_course_dict(pet, medication_name),
        )

    async def async_upsert_vaccine_override(self, pet_id: str, payload: dict[str, Any]) -> None:
        """Create or replace a vaccine override in the pet profile."""
        await self._async_update_pet_profile(
            pet_id,
            lambda pet: _upsert_vaccine_override_dict(pet, payload),
        )

    async def async_remove_vaccine_override(
        self,
        pet_id: str,
        *,
        dose_id: str | None = None,
        vaccine_name: str | None = None,
    ) -> None:
        """Remove a vaccine override by dose id or vaccine name."""
        await self._async_update_pet_profile(
            pet_id,
            lambda pet: _remove_vaccine_override_dict(pet, dose_id=dose_id, vaccine_name=vaccine_name),
        )

    async def async_log_weight(
        self,
        pet_id: str,
        weight_kg: float,
        *,
        actor: str | None = None,
        note: str | None = None,
        source: str = "manual",
    ) -> None:
        """Record a new weight measurement."""
        await self._async_apply_pet_notices(
            pet_id,
            self._pets[pet_id].engine.record_weight(
                dt_util.now(),
                weight_kg,
                actor=actor,
                note=note,
                source=source,
            ),
        )

    async def async_reschedule_vaccine(
        self,
        pet_id: str,
        *,
        due_date: str,
        dose_id: str | None = None,
        vaccine_name: str | None = None,
        note: str | None = None,
    ) -> None:
        """Reschedule a vaccine reminder."""
        await self._async_apply_pet_notices(
            pet_id,
            self._pets[pet_id].engine.reschedule_vaccine(
                dt_util.now(),
                dose_id=dose_id,
                vaccine_name=vaccine_name,
                due_date=dt_util.parse_date(due_date),
                note=note,
            ),
        )

    async def async_cancel_vaccine(
        self,
        pet_id: str,
        *,
        dose_id: str | None = None,
        vaccine_name: str | None = None,
        reason: str | None = None,
    ) -> None:
        """Cancel a vaccine reminder."""
        await self._async_apply_pet_notices(
            pet_id,
            self._pets[pet_id].engine.cancel_vaccine(
                dt_util.now(),
                dose_id=dose_id,
                vaccine_name=vaccine_name,
                reason=reason,
            ),
        )

    async def async_sync_pet_calendar(self, pet_id: str, *, days: int = CALENDAR_SYNC_DEFAULT_DAYS) -> int:
        """Reconcile DIVA with linked external calendars in both directions."""
        managed = self._pets[pet_id]
        counts, notices = await self._async_reconcile_external_calendars(
            pet_id,
            managed,
            dt_util.now(),
            days=days,
            allow_outbound=True,
            allow_import=True,
        )
        total_changes = counts["created"] + counts["updated"] + counts["deleted"] + counts["imported"]
        if total_changes or counts["skipped"] or counts["conflicts"]:
            notices.append(
                PetNotice(
                    category="event",
                    name=CAMERA_EVENT_CALENDAR_SYNCED,
                    timestamp=dt_util.now().isoformat(),
                    data={
                        **counts,
                        "days": days,
                        "calendars": list(managed.profile.external_calendar_entity_ids),
                    },
                )
            )
            managed.engine.append_records(notices)
            await self._async_save_runtime_state()
            await self._async_fire_notices((managed.profile, notice) for notice in notices)
            await self.async_request_refresh()
        return total_changes

    async def _async_poll_external_calendars(
        self,
        pet_id: str,
        managed: ManagedPet,
        now,
    ) -> list[PetNotice]:
        """Poll linked calendars for inbound edits on a throttled cadence."""
        notices: list[PetNotice] = []
        for calendar_entity_id in managed.profile.external_calendar_entity_ids:
            last_polled = managed.engine.last_calendar_polled_at(calendar_entity_id)
            if last_polled and now - last_polled < CALENDAR_IMPORT_POLL_INTERVAL:
                continue
            counts, imported = await self._async_reconcile_external_calendars(
                pet_id,
                managed,
                now,
                days=CALENDAR_SYNC_DEFAULT_DAYS,
                allow_outbound=False,
                allow_import=True,
                calendar_entity_ids=(calendar_entity_id,),
            )
            managed.engine.set_calendar_polled_at(calendar_entity_id, now)
            if counts["imported"] or counts["conflicts"]:
                notices.extend(imported)
        return notices

    async def async_resolve_calendar_conflict(
        self,
        pet_id: str,
        *,
        conflict_id: str,
        resolution: str,
        actor: str | None = None,
        note: str | None = None,
    ) -> None:
        """Resolve a calendar sync conflict for a single pet."""
        managed = self._pets[pet_id]
        conflict = managed.engine.find_calendar_conflict(conflict_id)
        if conflict is None:
            raise HomeAssistantError(f"Unknown DIVA calendar conflict: {conflict_id}")
        if resolution not in {
            CALENDAR_CONFLICT_RESOLUTION_DIVA_WINS,
            CALENDAR_CONFLICT_RESOLUTION_CALENDAR_WINS,
            CALENDAR_CONFLICT_RESOLUTION_DISMISS,
        }:
            raise HomeAssistantError(f"Unsupported calendar conflict resolution: {resolution}")

        calendar_entity_id = str(conflict.get("calendar_entity_id") or "").strip()
        sync_key = str(conflict.get("sync_key") or "").strip()
        if not calendar_entity_id or not sync_key:
            raise HomeAssistantError("Calendar conflict record is missing calendar_entity_id or sync_key")

        source_of_truth = managed.profile.calendar_source_of_truth(calendar_entity_id)
        now = dt_util.now()
        notices: list[PetNotice] = []

        if resolution != CALENDAR_CONFLICT_RESOLUTION_DISMISS:
            component = self.hass.data.get(CALENDAR_DATA_COMPONENT)
            if component is None:
                raise HomeAssistantError("Home Assistant calendar component is not available")

            entity = component.get_entity(calendar_entity_id)
            if entity is None:
                raise HomeAssistantError(f"Linked calendar entity is unavailable: {calendar_entity_id}")

            features = CalendarEntityFeature(getattr(entity, "supported_features", 0) or 0)
            start, end = _calendar_conflict_window(conflict, now)
            try:
                external_events = await entity.async_get_events(self.hass, start, end)
            except Exception as err:  # pragma: no cover - backend-specific path
                raise HomeAssistantError(f"Failed to read {calendar_entity_id}: {err}") from err

            current_external = {
                sync_key_candidate: event
                for event in external_events
                if (sync_key_candidate := _extract_diva_sync_key(getattr(event, "description", None))) is not None
            }.get(sync_key)
            context = self._build_pet_context(managed, now)
            base_by_key = {
                event.event_id: event
                for event in managed.engine.timeline_events(
                    start,
                    end,
                    context,
                    include_calendar_overrides=False,
                )
            }
            effective_by_key = {
                event.event_id: event
                for event in managed.engine.timeline_events(
                    start,
                    end,
                    context,
                    include_calendar_overrides=True,
                )
            }
            base_event = base_by_key.get(sync_key)
            effective_event = effective_by_key.get(sync_key)

            if resolution == CALENDAR_CONFLICT_RESOLUTION_CALENDAR_WINS:
                if current_external is None:
                    if base_event is not None:
                        notices.extend(
                            managed.engine.upsert_calendar_override(
                                calendar_entity_id,
                                sync_key=sync_key,
                                mode="skip",
                                event=None,
                                external_uid=None,
                                source_of_truth=source_of_truth,
                                imported_at=now,
                            )
                        )
                        managed.engine.record_calendar_sync_state(
                            calendar_entity_id,
                            sync_key=sync_key,
                            external_uid=None,
                            event_payload=None,
                            direction="manual_resolution",
                            state="manual_review_skip",
                            source_of_truth=source_of_truth,
                            last_seen_at=now,
                        )
                    else:
                        managed.engine.record_calendar_sync_state(
                            calendar_entity_id,
                            sync_key=sync_key,
                            external_uid=None,
                            event_payload=None,
                            direction="manual_resolution",
                            state="already_absent",
                            source_of_truth=source_of_truth,
                            last_seen_at=now,
                        )
                else:
                    imported_event = _external_event_to_scheduled_event(
                        current_external,
                        sync_key=sync_key,
                        fallback=base_event or effective_event,
                        pet_id=managed.profile.pet_id,
                    )
                    mode = "replace" if base_event is not None else "custom"
                    notices.extend(
                        managed.engine.upsert_calendar_override(
                            calendar_entity_id,
                            sync_key=sync_key,
                            mode=mode,
                            event=imported_event,
                            external_uid=getattr(current_external, "uid", None),
                            source_of_truth=source_of_truth,
                            imported_at=now,
                        )
                    )
                    managed.engine.record_calendar_sync_state(
                        calendar_entity_id,
                        sync_key=sync_key,
                        external_uid=getattr(current_external, "uid", None),
                        event_payload=imported_event,
                        direction="manual_resolution",
                        state=f"manual_review_{mode}",
                        source_of_truth=source_of_truth,
                        last_seen_at=now,
                    )
            elif resolution == CALENDAR_CONFLICT_RESOLUTION_DIVA_WINS:
                desired_event = effective_event
                state, external_uid = await self._async_apply_outbound_calendar_event(
                    entity,
                    features=features,
                    existing=current_external,
                    desired=desired_event,
                )
                managed.engine.clear_calendar_override(calendar_entity_id, sync_key)
                managed.engine.record_calendar_sync_state(
                    calendar_entity_id,
                    sync_key=sync_key,
                    external_uid=external_uid,
                    event_payload=desired_event,
                    direction="manual_resolution",
                    state=state,
                    source_of_truth=source_of_truth,
                    last_seen_at=now,
                )

        notices.extend(
            managed.engine.resolve_calendar_conflict(
                conflict_id,
                resolution=resolution,
                resolved_at=now,
                actor=actor,
                note=note,
            )
        )
        await self._async_apply_pet_notices(pet_id, notices)

    async def _async_apply_outbound_calendar_event(
        self,
        entity,
        *,
        features: CalendarEntityFeature,
        existing,
        desired: ScheduledEvent | None,
    ) -> tuple[str, str | None]:
        """Create, update, or delete a single linked calendar event."""
        if existing is None:
            if desired is None:
                return "already_absent", None
            if not features & CalendarEntityFeature.CREATE_EVENT:
                raise HomeAssistantError("The linked calendar does not support creating events")
            await entity.async_create_event(**_external_event_payload(desired))
            return "created", None

        existing_uid = getattr(existing, "uid", None)
        if desired is None:
            if not existing_uid or not features & CalendarEntityFeature.DELETE_EVENT:
                raise HomeAssistantError("The linked calendar does not support deleting this event")
            await entity.async_delete_event(existing_uid, recurrence_id=getattr(existing, "recurrence_id", None))
            return "deleted", existing_uid

        if _events_match(existing, desired):
            return "synced", existing_uid

        payload = _external_event_payload(desired)
        if existing_uid and features & CalendarEntityFeature.UPDATE_EVENT:
            await entity.async_update_event(existing_uid, payload, recurrence_id=getattr(existing, "recurrence_id", None))
            return "updated", existing_uid
        if (
            existing_uid
            and features & CalendarEntityFeature.DELETE_EVENT
            and features & CalendarEntityFeature.CREATE_EVENT
        ):
            await entity.async_delete_event(existing_uid, recurrence_id=getattr(existing, "recurrence_id", None))
            await entity.async_create_event(**payload)
            return "recreated", existing_uid
        raise HomeAssistantError("The linked calendar cannot apply this conflict resolution")

    async def _async_reconcile_external_calendars(
        self,
        pet_id: str,
        managed: ManagedPet,
        now,
        *,
        days: int,
        allow_outbound: bool,
        allow_import: bool,
        calendar_entity_ids: tuple[str, ...] | None = None,
    ) -> tuple[dict[str, int], list[PetNotice]]:
        """Reconcile external calendars against the DIVA timeline."""
        calendars = calendar_entity_ids or managed.profile.external_calendar_entity_ids
        counts = {"created": 0, "updated": 0, "deleted": 0, "skipped": 0, "imported": 0, "conflicts": 0}
        notices: list[PetNotice] = []
        if not calendars:
            return counts, notices

        component = self.hass.data.get(CALENDAR_DATA_COMPONENT)
        if component is None:
            return counts, notices

        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now + timedelta(days=max(1, days))
        context = self._build_pet_context(managed, now)

        for calendar_entity_id in calendars:
            entity = component.get_entity(calendar_entity_id)
            if entity is None:
                counts["skipped"] += 1
                continue

            features = CalendarEntityFeature(getattr(entity, "supported_features", 0) or 0)
            try:
                external_events = await entity.async_get_events(self.hass, start, end)
            except Exception as err:  # pragma: no cover - backend-specific path
                _LOGGER.warning("Failed to read events from %s: %s", calendar_entity_id, err)
                counts["skipped"] += 1
                continue

            synced_external = {
                sync_key: event
                for event in external_events
                if (sync_key := _extract_diva_sync_key(getattr(event, "description", None))) is not None
            }
            base_by_key = {
                event.event_id: event
                for event in managed.engine.timeline_events(
                    start,
                    end,
                    context,
                    include_calendar_overrides=False,
                )
            }
            effective_by_key = {
                event.event_id: event
                for event in managed.engine.timeline_events(
                    start,
                    end,
                    context,
                    include_calendar_overrides=True,
                )
            }
            source_of_truth = managed.profile.calendar_source_of_truth(calendar_entity_id)

            if allow_import:
                imported_any, calendar_notices, calendar_counts = self._import_external_calendar_differences(
                    managed,
                    calendar_entity_id,
                    source_of_truth=source_of_truth,
                    now=now,
                    base_by_key=base_by_key,
                    effective_by_key=effective_by_key,
                    synced_external=synced_external,
                )
                notices.extend(calendar_notices)
                for key, value in calendar_counts.items():
                    counts[key] += value
                if imported_any:
                    effective_by_key = {
                        event.event_id: event
                        for event in managed.engine.timeline_events(
                            start,
                            end,
                            context,
                            include_calendar_overrides=True,
                        )
                    }

            if not allow_outbound:
                continue

            synced_external = {
                sync_key: event
                for sync_key, event in synced_external.items()
            }
            for sync_key, desired in effective_by_key.items():
                existing = synced_external.pop(sync_key, None)
                if existing is None:
                    if source_of_truth != CALENDAR_SOURCE_OF_TRUTH_DIVA:
                        counts["skipped"] += 1
                        continue
                    try:
                        state, external_uid = await self._async_apply_outbound_calendar_event(
                            entity,
                            features=features,
                            existing=None,
                            desired=desired,
                        )
                    except HomeAssistantError:
                        counts["skipped"] += 1
                        continue
                    counts["created"] += 1
                    managed.engine.mark_calendar_event_synced(calendar_entity_id, sync_key)
                    managed.engine.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
                    managed.engine.record_calendar_sync_state(
                        calendar_entity_id,
                        sync_key=sync_key,
                        external_uid=external_uid,
                        event_payload=desired,
                        direction="outbound",
                        state=state,
                        source_of_truth=source_of_truth,
                        last_seen_at=now,
                    )
                    continue

                if _events_match(existing, desired):
                    managed.engine.mark_calendar_event_synced(calendar_entity_id, sync_key)
                    managed.engine.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
                    managed.engine.record_calendar_sync_state(
                        calendar_entity_id,
                        sync_key=sync_key,
                        external_uid=getattr(existing, "uid", None),
                        event_payload=desired,
                        direction="roundtrip",
                        state="synced",
                        source_of_truth=source_of_truth,
                        last_seen_at=now,
                    )
                    continue

                if source_of_truth != CALENDAR_SOURCE_OF_TRUTH_DIVA:
                    counts["skipped"] += 1
                    continue

                try:
                    state, external_uid = await self._async_apply_outbound_calendar_event(
                        entity,
                        features=features,
                        existing=existing,
                        desired=desired,
                    )
                except HomeAssistantError:
                    counts["skipped"] += 1
                    continue
                counts["updated"] += 1
                managed.engine.mark_calendar_event_synced(calendar_entity_id, sync_key)
                managed.engine.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
                managed.engine.record_calendar_sync_state(
                    calendar_entity_id,
                    sync_key=sync_key,
                    external_uid=external_uid,
                    event_payload=desired,
                    direction="outbound",
                    state=state,
                    source_of_truth=source_of_truth,
                    last_seen_at=now,
                )

            for sync_key, existing in synced_external.items():
                if source_of_truth != CALENDAR_SOURCE_OF_TRUTH_DIVA:
                    counts["skipped"] += 1
                    continue
                try:
                    state, external_uid = await self._async_apply_outbound_calendar_event(
                        entity,
                        features=features,
                        existing=existing,
                        desired=None,
                    )
                except HomeAssistantError:
                    counts["skipped"] += 1
                    continue
                counts["deleted"] += 1
                managed.engine.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
                managed.engine.record_calendar_sync_state(
                    calendar_entity_id,
                    sync_key=sync_key,
                    external_uid=external_uid,
                    event_payload=None,
                    direction="outbound",
                    state=state,
                    source_of_truth=source_of_truth,
                    last_seen_at=now,
                )
        return counts, notices

    def _import_external_calendar_differences(
        self,
        managed: ManagedPet,
        calendar_entity_id: str,
        *,
        source_of_truth: str,
        now,
        base_by_key: dict[str, ScheduledEvent],
        effective_by_key: dict[str, ScheduledEvent],
        synced_external: dict[str, Any],
    ) -> tuple[bool, list[PetNotice], dict[str, int]]:
        """Apply inbound calendar edits according to the configured policy."""
        changed = False
        notices: list[PetNotice] = []
        counts = {"imported": 0, "conflicts": 0, "skipped": 0}

        for sync_key, base_event in base_by_key.items():
            external = synced_external.get(sync_key)
            effective_event = effective_by_key.get(sync_key)
            override = managed.engine.calendar_override_record(calendar_entity_id, sync_key)

            if external is None:
                if source_of_truth == CALENDAR_SOURCE_OF_TRUTH_CALENDAR:
                    notices.extend(
                        managed.engine.upsert_calendar_override(
                            calendar_entity_id,
                            sync_key=sync_key,
                            mode="skip",
                            event=None,
                            external_uid=None,
                            source_of_truth=source_of_truth,
                            imported_at=now,
                        )
                    )
                    managed.engine.record_calendar_sync_state(
                        calendar_entity_id,
                        sync_key=sync_key,
                        external_uid=None,
                        event_payload=None,
                        direction="inbound",
                        state="imported_skip",
                        source_of_truth=source_of_truth,
                        last_seen_at=now,
                    )
                    managed.engine.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
                    counts["imported"] += 1
                    changed = True
                elif source_of_truth == CALENDAR_SOURCE_OF_TRUTH_MANUAL_REVIEW:
                    if override is not None and override.get("mode") == "skip":
                        managed.engine.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
                        managed.engine.record_calendar_sync_state(
                            calendar_entity_id,
                            sync_key=sync_key,
                            external_uid=None,
                            event_payload=None,
                            direction="roundtrip",
                            state="synced_override",
                            source_of_truth=source_of_truth,
                            last_seen_at=now,
                        )
                        continue
                    conflict_notices = managed.engine.record_calendar_conflict(
                        calendar_entity_id,
                        sync_key=sync_key,
                        conflict_type="deleted_external",
                        reason="External calendar deleted a DIVA event",
                        source_of_truth=source_of_truth,
                        external_uid=None,
                        base_event=base_event,
                        effective_event=effective_event,
                        external_event=None,
                        occurred_at=now,
                    )
                    notices.extend(conflict_notices)
                    if conflict_notices:
                        counts["conflicts"] += 1
                continue

            if _events_match(external, base_event):
                managed.engine.clear_calendar_override(calendar_entity_id, sync_key)
                managed.engine.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
                managed.engine.record_calendar_sync_state(
                    calendar_entity_id,
                    sync_key=sync_key,
                    external_uid=getattr(external, "uid", None),
                    event_payload=base_event,
                    direction="roundtrip",
                    state="synced",
                    source_of_truth=source_of_truth,
                    last_seen_at=now,
                )
                continue

            if effective_event is not None and _events_match(external, effective_event):
                managed.engine.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
                managed.engine.record_calendar_sync_state(
                    calendar_entity_id,
                    sync_key=sync_key,
                    external_uid=getattr(external, "uid", None),
                    event_payload=effective_event,
                    direction="roundtrip",
                    state="synced_override",
                    source_of_truth=source_of_truth,
                    last_seen_at=now,
                )
                continue

            if source_of_truth == CALENDAR_SOURCE_OF_TRUTH_CALENDAR:
                imported_event = _external_event_to_scheduled_event(
                    external,
                    sync_key=sync_key,
                    fallback=base_event,
                    pet_id=managed.profile.pet_id,
                )
                notices.extend(
                    managed.engine.upsert_calendar_override(
                        calendar_entity_id,
                        sync_key=sync_key,
                        mode="replace",
                        event=imported_event,
                        external_uid=getattr(external, "uid", None),
                        source_of_truth=source_of_truth,
                        imported_at=now,
                    )
                )
                managed.engine.record_calendar_sync_state(
                    calendar_entity_id,
                    sync_key=sync_key,
                    external_uid=getattr(external, "uid", None),
                    event_payload=imported_event,
                    direction="inbound",
                    state="imported_override",
                    source_of_truth=source_of_truth,
                    last_seen_at=now,
                )
                managed.engine.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
                counts["imported"] += 1
                changed = True
                continue

            if source_of_truth == CALENDAR_SOURCE_OF_TRUTH_MANUAL_REVIEW:
                conflict_notices = managed.engine.record_calendar_conflict(
                    calendar_entity_id,
                    sync_key=sync_key,
                    conflict_type="diverged",
                    reason="External calendar diverged from DIVA event",
                    source_of_truth=source_of_truth,
                    external_uid=getattr(external, "uid", None),
                    base_event=base_event,
                    effective_event=effective_event,
                    external_event=_external_event_snapshot(external),
                    occurred_at=now,
                )
                notices.extend(conflict_notices)
                if conflict_notices:
                    counts["conflicts"] += 1

        for sync_key, external in synced_external.items():
            if sync_key in base_by_key:
                continue
            effective_event = effective_by_key.get(sync_key)
            if effective_event is not None and _events_match(external, effective_event):
                managed.engine.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
                managed.engine.record_calendar_sync_state(
                    calendar_entity_id,
                    sync_key=sync_key,
                    external_uid=getattr(external, "uid", None),
                    event_payload=effective_event,
                    direction="roundtrip",
                    state="synced_override",
                    source_of_truth=source_of_truth,
                    last_seen_at=now,
                )
                continue
            if source_of_truth == CALENDAR_SOURCE_OF_TRUTH_CALENDAR:
                imported_event = _external_event_to_scheduled_event(
                    external,
                    sync_key=sync_key,
                    fallback=None,
                    pet_id=managed.profile.pet_id,
                )
                notices.extend(
                    managed.engine.upsert_calendar_override(
                        calendar_entity_id,
                        sync_key=sync_key,
                        mode="custom",
                        event=imported_event,
                        external_uid=getattr(external, "uid", None),
                        source_of_truth=source_of_truth,
                        imported_at=now,
                    )
                )
                managed.engine.record_calendar_sync_state(
                    calendar_entity_id,
                    sync_key=sync_key,
                    external_uid=getattr(external, "uid", None),
                    event_payload=imported_event,
                    direction="inbound",
                    state="imported_custom",
                    source_of_truth=source_of_truth,
                    last_seen_at=now,
                )
                managed.engine.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
                counts["imported"] += 1
                changed = True
                continue
            if source_of_truth == CALENDAR_SOURCE_OF_TRUTH_MANUAL_REVIEW:
                conflict_notices = managed.engine.record_calendar_conflict(
                    calendar_entity_id,
                    sync_key=sync_key,
                    conflict_type="unmanaged_external",
                    reason="External calendar contains an unmanaged DIVA-marked event",
                    source_of_truth=source_of_truth,
                    external_uid=getattr(external, "uid", None),
                    base_event=None,
                    effective_event=effective_event,
                    external_event=_external_event_snapshot(external),
                    occurred_at=now,
                )
                notices.extend(conflict_notices)
                if conflict_notices:
                    counts["conflicts"] += 1
        return changed, notices, counts

    async def _async_apply_pet_notices(
        self,
        pet_id: str,
        notices: list[PetNotice],
        *,
        capture_food_reference: bool = False,
        capture_water_reference: bool = False,
    ) -> None:
        """Persist pet state changes, publish notices, and refresh snapshots."""
        managed = self._pets[pet_id]
        if capture_food_reference:
            managed.camera.signals.add(SIGNAL_CAPTURE_FOOD_REFERENCE)
        if capture_water_reference:
            managed.camera.signals.add(SIGNAL_CAPTURE_WATER_REFERENCE)
        managed.engine.append_records(notices)
        await self._async_save_runtime_state()
        await self._async_fire_notices((managed.profile, notice) for notice in notices)
        await self.async_request_refresh()

    async def _async_update_pet_profile(
        self,
        pet_id: str,
        mutate,
    ) -> None:
        """Persist a profile mutation into the config entry and runtime."""
        managed = self._pets[pet_id]
        updated_pet = mutate(dict(managed.profile.as_dict()))
        updated_profile = PetProfile.from_dict(updated_pet)
        managed.profile = updated_profile
        managed.engine.profile = updated_profile

        settings = _entry_settings(self.entry)
        settings[CONF_PETS] = [
            updated_profile.as_dict() if existing[CONF_PET_ID] == pet_id else existing
            for existing in settings[CONF_PETS]
        ]
        self.hass.config_entries.async_update_entry(
            self.entry,
            title=settings[CONF_HUB_NAME],
            data=serialize_diva_entry_settings_v3(
                hub_name=settings[CONF_HUB_NAME],
                show_editor_in_sidebar=settings.get(CONF_SHOW_EDITOR_IN_SIDEBAR, True),
                pets=settings[CONF_PETS],
            ),
            options={},
        )
        await self._async_persist_and_refresh()

    def _requires_approval(self, managed: ManagedPet, action_name: str) -> bool:
        """Return whether a profile requires approval for an action."""
        return action_name in managed.profile.approval_required_actions

    def _checklist_requires_approval(self, managed: ManagedPet, checklist_id: str) -> bool:
        """Return whether a checklist completion should be queued for approval."""
        if APPROVAL_ACTION_CHECKLIST in managed.profile.approval_required_actions:
            return True
        item = next(
            (entry for entry in managed.profile.checklist_items if entry.checklist_id == checklist_id),
            None,
        )
        if item is None:
            raise ValueError("Unknown checklist item")
        return item.requires_approval

    def _checklist_category(self, managed: ManagedPet, checklist_id: str) -> str:
        """Return the category of a checklist item."""
        item = next(
            (entry for entry in managed.profile.checklist_items if entry.checklist_id == checklist_id),
            None,
        )
        if item is None:
            raise ValueError("Unknown checklist item")
        return item.category

    def _execute_approved_action(
        self,
        managed: ManagedPet,
        now,
        *,
        action_name: str,
        payload: dict[str, Any],
    ) -> tuple[list[PetNotice], bool, bool]:
        """Execute a stored approval payload and return notices plus capture flags."""
        if action_name == APPROVAL_ACTION_FEED:
            notices = managed.engine.feed_now(
                now,
                payload.get("grams"),
                meal_type=payload.get("meal_type"),
                food_name=payload.get("food_name"),
            )
            return notices, True, False
        if action_name == APPROVAL_ACTION_FINISH_WALK:
            return managed.engine.finish_walk(now), False, False
        if action_name == APPROVAL_ACTION_CARE:
            notices = managed.engine.log_care_action(
                now,
                str(payload.get("action", "care")),
                actor=payload.get("actor"),
                note=payload.get("note"),
                category=str(payload.get("category", ROUTINE_TYPE_CARE)),
            )
            return notices, False, False
        if action_name == APPROVAL_ACTION_MEDICATION:
            notices = managed.engine.log_medication_dose(
                now,
                str(payload.get("medication_name", "")),
                dose=payload.get("dose"),
                actor=payload.get("actor"),
                note=payload.get("note"),
            )
            return notices, False, False
        if action_name == APPROVAL_ACTION_VACCINE:
            notices = managed.engine.complete_vaccine_dose(
                now,
                dose_id=payload.get("dose_id"),
                vaccine_name=payload.get("vaccine_name"),
                note=payload.get("note"),
            )
            return notices, False, False
        if action_name == APPROVAL_ACTION_CHECKLIST:
            notices = managed.engine.complete_checklist_item(
                now,
                str(payload.get("checklist_id", "")),
                actor=payload.get("actor"),
                note=payload.get("note"),
                source=str(payload.get("source", "approval")),
            )
            return notices, False, False
        raise ValueError(f"Unsupported approval action: {action_name}")

    async def _async_persist_and_refresh(self) -> None:
        """Persist state and refresh the coordinator."""
        await self._async_save_runtime_state()
        await self.async_request_refresh()

    async def _async_save_runtime_state(self) -> None:
        """Persist the hub runtime state into the root-level JSON backend."""
        await self._runtime_store.async_save_entry(
            self.entry.entry_id,
            self._storage_payload(),
        )

    async def _async_fire_notices(self, items) -> None:
        """Publish DIVA runtime notices onto the Home Assistant event bus."""
        for profile, notice in items:
            self.hass.bus.async_fire(
                notice_event_type(notice),
                build_notice_payload(profile, notice),
            )

    async def _async_run_camera_analysis(self, managed: ManagedPet) -> CameraAnalysis | None:
        """Fetch a camera image and derive bowl state information for a pet."""
        if not managed.profile.camera_entity_id:
            return None
        try:
            from homeassistant.components.camera import async_get_image

            image = await async_get_image(
                self.hass,
                managed.profile.camera_entity_id,
                timeout=10,
            )
            frame, analysis = await self.hass.async_add_executor_job(
                _process_camera_image,
                image.content,
                managed.camera.previous_frame,
                managed.profile.food_bowl_area,
                managed.profile.water_bowl_area,
                managed.camera.food_reference,
                managed.camera.water_reference,
            )
            managed.camera.last_image = image.content
            if SIGNAL_CAPTURE_FOOD_REFERENCE in managed.camera.signals:
                managed.camera.food_reference = frame.copy()
                managed.camera.signals.remove(SIGNAL_CAPTURE_FOOD_REFERENCE)
            if SIGNAL_CAPTURE_WATER_REFERENCE in managed.camera.signals:
                managed.camera.water_reference = frame.copy()
                managed.camera.signals.remove(SIGNAL_CAPTURE_WATER_REFERENCE)
            managed.camera.previous_frame = frame
            return analysis
        except Exception as err:  # pragma: no cover - runtime integration path
            _LOGGER.warning(
                "Camera analysis failed for %s: %s",
                managed.profile.name,
                err,
            )
            return None

    def diagnostics_payload(self) -> dict[str, Any]:
        """Return a diagnostics-friendly runtime payload."""
        return {
            "hub_name": self.hub_name,
            "storage": {
                "backend": RUNTIME_STORAGE_BACKEND,
                "path": str(self._runtime_store.path),
            },
            "pets": {
                pet_id: {
                    "profile": managed.profile.as_dict(),
                    "profile_v3": managed.profile.as_v3_dict(),
                    "runtime": managed.engine.serialize(),
                    "runtime_sections": _runtime_sections(managed.engine.state),
                    "snapshot": self.data.get(pet_id).as_dict() if self.data and pet_id in self.data else None,
                    "timeline": self.get_timeline(pet_id),
                    "camera": {
                        "enabled": bool(managed.profile.camera_entity_id),
                        "camera_entity_id": managed.profile.camera_entity_id,
                        "analysis": managed.camera.last_analysis,
                        "has_reference_food": managed.camera.food_reference is not None,
                        "has_reference_water": managed.camera.water_reference is not None,
                    },
                }
                for pet_id, managed in self._pets.items()
            },
        }

    def _storage_payload(self) -> dict[str, Any]:
        """Build the persisted JSON payload for this DIVA hub entry."""
        return {
            CONF_PET_SCHEMA: PET_SCHEMA_VERSION,
            "hub_name": self.hub_name,
            "storage_backend": RUNTIME_STORAGE_BACKEND,
            "pets": {
                pet_id: {
                    "profile": managed.profile.as_v3_dict(),
                    "runtime": managed.engine.serialize(),
                    "runtime_sections": _runtime_sections(managed.engine.state),
                    "snapshot": self.data.get(pet_id).as_dict() if self.data and pet_id in self.data else None,
                    "timeline": self.get_timeline(pet_id),
                    "camera": {
                        "enabled": bool(managed.profile.camera_entity_id),
                        "camera_entity_id": managed.profile.camera_entity_id,
                        "food_bowl_area": (
                            managed.profile.food_bowl_area.as_dict()
                            if managed.profile.food_bowl_area
                            else None
                        ),
                        "water_bowl_area": (
                            managed.profile.water_bowl_area.as_dict()
                            if managed.profile.water_bowl_area
                            else None
                        ),
                        "analysis": managed.camera.last_analysis,
                    },
                }
                for pet_id, managed in self._pets.items()
            },
        }

    def _build_pet_context(self, managed: ManagedPet, now=None) -> PetContext:
        """Read HA entities linked to the pet and convert them to context."""
        now = now or dt_util.now()
        profile = managed.profile
        gps_state = _entity_state(self.hass, profile.gps_tracker_entity_id)
        ble_state = _entity_state(self.hass, profile.ble_tracker_entity_id)
        gps_latitude, gps_longitude, gps_accuracy_m = _extract_tracker_coordinates(
            self.hass,
            profile.gps_tracker_entity_id,
        )
        caregiver_home_count = sum(
            1
            for entity_id in profile.household_presence_entity_ids
            if _is_home_state(_entity_state(self.hass, entity_id))
        )
        outside_temperature = _extract_temperature(self.hass, profile.weather_entity_id)
        current_room, room_sources = _resolve_room_presence(
            self.hass,
            profile,
            ble_state=ble_state,
            camera_analysis=managed.camera.last_analysis,
            now=now,
            previous_room=managed.engine.state.current_room,
        )
        current_zone, geofence_breached, distance_from_safe_zone_m = _resolve_zone_context(
            profile,
            gps_state=gps_state,
            latitude=gps_latitude,
            longitude=gps_longitude,
        )
        active_behavior_signals = tuple(
            sorted(
                {
                    signal
                    for entity_id in profile.behavior_signal_entity_ids
                    if (signal := _active_behavior_signal(self.hass, entity_id)) is not None
                }
            )
        )
        pet_home = current_zone is not None or gps_state in (None, "home")
        return PetContext(
            gps_tracker_state=gps_state,
            ble_tracker_state=ble_state,
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude,
            gps_accuracy_m=gps_accuracy_m,
            caregiver_home_count=caregiver_home_count,
            home_alone=caregiver_home_count == 0 and pet_home,
            outside_temperature_c=outside_temperature,
            current_zone=current_zone,
            geofence_breached=geofence_breached,
            distance_from_safe_zone_m=distance_from_safe_zone_m,
            current_room=current_room,
            room_presence_sources=room_sources,
            active_behavior_signals=active_behavior_signals,
        )


def _process_camera_image(
    image_bytes: bytes,
    previous_frame,
    food_area,
    water_area,
    food_reference,
    water_reference,
):
    """Decode and analyze a camera frame in the executor."""
    frame = decode_image_bytes(image_bytes)
    analysis = analyze_frame(
        frame,
        previous_frame,
        food_area,
        water_area,
        food_reference,
        water_reference,
    )
    return frame, analysis


def _write_text_report_file(base_path: str, filename: str, content: str) -> str:
    """Write a generated text vet report to disk."""
    reports_dir = Path(base_path)
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / filename
    path.write_text(content, encoding="utf-8")
    return str(path)


def _write_pdf_report_file(base_path: str, filename: str, content: str, title: str) -> str:
    """Write a generated PDF vet report to disk."""
    reports_dir = Path(base_path)
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / filename
    path.write_bytes(_render_simple_pdf(title=title, text=content))
    return str(path)


def _report_job_id(pet_id: str, report_kind: str, requested_at) -> str:
    """Build a stable runtime identifier for a report export job."""
    return f"{pet_id}:report:{report_kind}:{int(requested_at.timestamp() * 1000)}"


def _render_simple_pdf(*, title: str, text: str) -> bytes:
    """Render a minimal multi-page PDF without external dependencies."""
    page_width = 595
    page_height = 842
    margin_left = 50
    margin_top = 70
    line_height = 14
    max_lines = 48
    raw_lines = [title, ""] + text.splitlines()
    chunks = [raw_lines[index : index + max_lines] for index in range(0, len(raw_lines), max_lines)] or [[""]]

    objects: list[bytes] = []
    page_ids: list[int] = []

    font_obj_id = 1
    pages_obj_id = 2
    next_obj_id = 3

    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(b"")

    for chunk in chunks:
        page_obj_id = next_obj_id
        content_obj_id = next_obj_id + 1
        next_obj_id += 2
        page_ids.append(page_obj_id)

        lines = [b"BT", b"/F1 11 Tf"]
        y = page_height - margin_top
        for line in chunk:
            safe = (
                line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
                .encode("latin-1", "replace")
            )
            lines.append(f"1 0 0 1 {margin_left} {y} Tm".encode())
            lines.append(b"(" + safe + b") Tj")
            y -= line_height
        lines.append(b"ET")
        stream = b"\n".join(lines)
        objects.append(
            f"<< /Type /Page /Parent {pages_obj_id} 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 {font_obj_id} 0 R >> >> /Contents {content_obj_id} 0 R >>".encode()
        )
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream")

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()

    catalog_obj_id = next_obj_id
    objects.append(f"<< /Type /Catalog /Pages {pages_obj_id} 0 R >>".encode())

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_obj_id} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode()
    )
    return bytes(pdf)


def _runtime_sections(state) -> dict[str, Any]:
    """Build typed runtime sections for persisted JSON diagnostics/storage."""
    return {
        "medical": {
            "medication_log": state.medication_log[-40:],
            "symptom_log": state.symptom_log[-40:],
            "completed_vaccine_doses": dict(state.completed_vaccine_doses),
            "vaccine_runtime_overrides": dict(state.vaccine_runtime_overrides),
            "active_recovery_plan": state.active_recovery_plan,
            "weight_history": state.weight_history[-40:],
        },
        "mobility": {
            "gps_history": state.gps_history[-200:],
            "current_walk_route": state.current_walk_route[-200:],
            "last_walk_route": state.last_walk_route[-200:],
            "room_history": state.room_history[-80:],
            "room_dwell_today_minutes": dict(state.room_dwell_today_minutes),
            "zone_visits_today": dict(state.zone_visits_today),
            "separation_minutes_today": state.separation_minutes_today,
        },
        "behavior": {
            "behavior_reports": state.behavior_reports[-40:],
            "behavior_observations": state.behavior_observations[-40:],
            "active_anomalies": sorted(state.active_anomalies),
            "latest_behavior_profile": state.latest_behavior_profile,
            "latest_behavior_summary": state.latest_behavior_summary,
        },
        "operations": {
            "pending_approvals": state.pending_approvals[-40:],
            "checklist_completions": state.checklist_completions[-80:],
            "journal_entries": state.journal_entries[-80:],
        },
        "reports": {
            "generated_reports": state.generated_reports[-40:],
            "report_jobs": state.report_jobs[-40:],
        },
    }


def _stored_runtime_entry_needs_migration(payload: dict[str, Any]) -> bool:
    """Return whether a persisted runtime entry should be rewritten to the canonical v3 shape."""
    if not payload:
        return False
    if int(payload.get(CONF_PET_SCHEMA, 0) or 0) < PET_SCHEMA_VERSION:
        return True
    if payload.get("storage_backend") != RUNTIME_STORAGE_BACKEND:
        return True

    stored_pets = payload.get("pets")
    if not isinstance(stored_pets, dict):
        return True

    for stored_pet in stored_pets.values():
        if not isinstance(stored_pet, dict):
            return True
        if "runtime" not in stored_pet or not isinstance(stored_pet.get("runtime"), dict):
            return True
        if "snapshot" not in stored_pet:
            return True
        if not isinstance(stored_pet.get("timeline"), list):
            return True
        if not isinstance(stored_pet.get("camera"), dict):
            return True
        if not isinstance(stored_pet.get("runtime_sections"), dict):
            return True

        stored_profile = stored_pet.get("profile")
        if not isinstance(stored_profile, dict):
            return True
        canonical_profile = serialize_pet_config_record_v3(normalize_pet_config_record(dict(stored_profile)))
        if stored_profile != canonical_profile:
            return True

    return False


def _entry_settings(entry: ConfigEntry) -> dict[str, Any]:
    """Return merged hub settings from a config entry."""
    if entry.options.get(CONF_PETS):
        return {
            CONF_HUB_NAME: entry.options.get(CONF_HUB_NAME, entry.title),
            CONF_PET_SCHEMA: int(entry.options.get(CONF_PET_SCHEMA, entry.data.get(CONF_PET_SCHEMA, 0)) or 0),
            CONF_SHOW_EDITOR_IN_SIDEBAR: entry.options.get(
                CONF_SHOW_EDITOR_IN_SIDEBAR,
                entry.data.get(CONF_SHOW_EDITOR_IN_SIDEBAR, True),
            ),
            CONF_PETS: [normalize_pet_config_record(dict(pet)) for pet in entry.options.get(CONF_PETS, [])],
        }
    if CONF_PETS in entry.data:
        return {
            CONF_HUB_NAME: entry.data.get(CONF_HUB_NAME, entry.title),
            CONF_PET_SCHEMA: int(entry.data.get(CONF_PET_SCHEMA, 0) or 0),
            CONF_SHOW_EDITOR_IN_SIDEBAR: entry.data.get(CONF_SHOW_EDITOR_IN_SIDEBAR, True),
            CONF_PETS: [normalize_pet_config_record(dict(pet)) for pet in entry.data.get(CONF_PETS, [])],
        }

    legacy_pet = dict(entry.data)
    legacy_pet.setdefault(
        CONF_PET_ID,
        generate_pet_id(
            f"{legacy_pet.get(CONF_NAME, 'pet')}_{legacy_pet.get(CONF_BIRTHDATE, '')}_{legacy_pet.get('species', '')}"
        ),
    )
    return {
        CONF_HUB_NAME: entry.title,
        CONF_PET_SCHEMA: 0,
        CONF_SHOW_EDITOR_IN_SIDEBAR: entry.data.get(CONF_SHOW_EDITOR_IN_SIDEBAR, True),
        CONF_PETS: [legacy_pet],
    }


def _entity_state(hass: HomeAssistant, entity_id: str | None) -> str | None:
    if not entity_id:
        return None
    state = hass.states.get(entity_id)
    if state is None:
        return None
    if state.state in {"unknown", "unavailable"}:
        return None
    return state.state


def _is_home_state(state: str | None) -> bool:
    if state is None:
        return False
    return state.lower() in HOME_STATES


def _extract_temperature(hass: HomeAssistant, entity_id: str | None) -> float | None:
    if not entity_id:
        return None
    state = hass.states.get(entity_id)
    if state is None:
        return None
    try:
        return float(state.state)
    except (TypeError, ValueError):
        pass
    for key in ("temperature", "current_temperature"):
        value = state.attributes.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _extract_tracker_coordinates(
    hass: HomeAssistant,
    entity_id: str | None,
) -> tuple[float | None, float | None, float | None]:
    state = hass.states.get(entity_id) if entity_id else None
    if state is None:
        return None, None, None
    try:
        latitude = float(state.attributes.get("latitude"))
        longitude = float(state.attributes.get("longitude"))
    except (TypeError, ValueError):
        return None, None, None
    try:
        gps_accuracy_m = float(state.attributes.get("gps_accuracy"))
    except (TypeError, ValueError):
        gps_accuracy_m = None
    return latitude, longitude, gps_accuracy_m


def _resolve_zone_context(
    profile: PetProfile,
    *,
    gps_state: str | None,
    latitude: float | None,
    longitude: float | None,
) -> tuple[str | None, bool, float | None]:
    """Resolve the current named zone and safe-zone state."""
    if latitude is None or longitude is None:
        if gps_state in {None, "home"} and profile.safe_zones:
            return profile.safe_zones[0].name, False, 0.0
        return (gps_state if gps_state not in {None, "not_home"} else None), False, None

    nearest_distance: float | None = None
    current_zone: str | None = None
    for safe_zone in profile.safe_zones:
        distance = safe_zone.distance_m(latitude, longitude)
        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
        if safe_zone.contains(latitude, longitude):
            current_zone = safe_zone.name
            nearest_distance = max(0.0, distance - safe_zone.radius_m)
            break

    if current_zone is not None:
        return current_zone, False, round(nearest_distance or 0.0, 1)
    if profile.safe_zones:
        return gps_state if gps_state not in {None, "not_home"} else "outside_safe_zone", True, round(nearest_distance or 0.0, 1)
    return gps_state if gps_state not in {None, "not_home"} else None, False, None


def _resolve_room_presence(
    hass: HomeAssistant,
    profile: PetProfile,
    *,
    ble_state: str | None,
    camera_analysis: dict[str, Any] | None,
    now,
    previous_room: str | None = None,
) -> tuple[str | None, tuple[str, ...]]:
    """Resolve the current room from configured sources, BLE, and camera."""
    candidates: dict[str, dict[str, Any]] = {}
    for source in profile.room_presence_sources:
        state = hass.states.get(source.entity_id)
        if state is None:
            continue
        state_value = str(state.state).strip()
        if _room_source_active(state_value, source.match_state, source.room_name):
            _add_room_candidate(
                candidates,
                room_name=source.room_name,
                score=source.priority,
                source=source.entity_id,
                source_type="configured",
            )

    ble_room = _ble_room_name(ble_state)
    if ble_room:
        _add_room_candidate(
            candidates,
            room_name=ble_room,
            score=BLE_ROOM_PRIORITY,
            source=profile.ble_tracker_entity_id or "ble_tracker",
            source_type="ble",
        )

    camera_score = _camera_room_score(camera_analysis, now)
    if profile.camera_room_name and camera_score is not None:
        _add_room_candidate(
            candidates,
            room_name=profile.camera_room_name,
            score=camera_score,
            source=profile.camera_entity_id or "camera",
            source_type="camera",
        )

    if not candidates:
        return None, ()
    previous_normalized = _normalize_room_name(previous_room)
    for candidate in candidates.values():
        if len(candidate["source_types"]) > 1:
            candidate["score"] += (len(candidate["source_types"]) - 1) * ROOM_FUSION_MULTI_SOURCE_BONUS
        if {"ble", "camera"}.issubset(candidate["source_types"]):
            candidate["score"] += ROOM_FUSION_BLE_CAMERA_BONUS
        if previous_normalized and candidate["normalized"] == previous_normalized:
            candidate["score"] += ROOM_FUSION_STICKY_BONUS

    resolved = sorted(
        candidates.values(),
        key=lambda item: (-item["score"], -len(item["sources"]), item["room_name"]),
    )[0]
    return resolved["room_name"], tuple(sorted(resolved["sources"]))


def _add_room_candidate(
    candidates: dict[str, dict[str, Any]],
    *,
    room_name: str,
    score: int,
    source: str,
    source_type: str,
) -> None:
    """Merge a room candidate into the fusion map."""
    normalized = _normalize_room_name(room_name)
    if not normalized:
        return
    candidate = candidates.setdefault(
        normalized,
        {
            "normalized": normalized,
            "room_name": room_name,
            "score": 0,
            "sources": set(),
            "source_types": set(),
            "label_source": source_type,
        },
    )
    candidate["score"] += score
    candidate["sources"].add(source)
    candidate["source_types"].add(source_type)
    if _room_label_priority(source_type) > _room_label_priority(candidate["label_source"]):
        candidate["room_name"] = room_name
        candidate["label_source"] = source_type


def _room_label_priority(source_type: str) -> int:
    """Prefer configured labels over camera labels over BLE-derived labels."""
    if source_type == "configured":
        return 3
    if source_type == "camera":
        return 2
    return 1


def _normalize_room_name(room_name: str | None) -> str:
    """Normalize room naming across BLE, camera, and configured sources."""
    if room_name is None:
        return ""
    return " ".join(str(room_name).replace("_", " ").strip().lower().split())


def _ble_room_name(ble_state: str | None) -> str | None:
    """Convert a BLE tracker state into a room-like label when possible."""
    if not ble_state:
        return None
    normalized = ble_state.strip().lower()
    if normalized in HOME_STATES | {"not_home", "away", "off", "unknown", "unavailable"}:
        return None
    return ble_state.replace("_", " ").title()


def _camera_room_score(camera_analysis: dict[str, Any] | None, now) -> int | None:
    """Return a fusion score for the latest camera room signal."""
    if not camera_analysis:
        return None
    captured_at_ts = camera_analysis.get("captured_at_ts")
    try:
        if captured_at_ts is None or now.timestamp() - float(captured_at_ts) > CAMERA_ROOM_SIGNAL_WINDOW_SECONDS:
            return None
    except (TypeError, ValueError, AttributeError):
        return None
    if camera_analysis.get("food_interaction") or camera_analysis.get("water_interaction"):
        return CAMERA_ROOM_INTERACTION_PRIORITY
    try:
        if float(camera_analysis.get("frame_motion", 0.0) or 0.0) >= CAMERA_ROOM_MOTION_THRESHOLD:
            return CAMERA_ROOM_MOTION_PRIORITY
    except (TypeError, ValueError):
        return None
    return None


def _room_source_active(state_value: str, match_state: str | None, room_name: str) -> bool:
    """Return whether the state should be treated as active for a room source."""
    normalized_state = state_value.strip().lower()
    if not normalized_state or normalized_state in {"unknown", "unavailable", "off", "idle"}:
        return False
    if match_state is not None:
        return normalized_state == match_state.strip().lower()
    if normalized_state in ACTIVE_SIGNAL_STATES | HOME_STATES | {"occupied", "present", "open"}:
        return True
    return normalized_state == room_name.strip().lower()


def _active_behavior_signal(hass: HomeAssistant, entity_id: str) -> str | None:
    state = hass.states.get(entity_id)
    if state is None:
        return None
    if str(state.state).lower() not in ACTIVE_SIGNAL_STATES:
        return None
    source = f"{entity_id} {state.attributes.get('friendly_name', '')}".lower()
    if "vomit" in source:
        return normalize_behavior_type("vomiting")
    if "cough" in source:
        return normalize_behavior_type("cough")
    if "limp" in source:
        return normalize_behavior_type("limping")
    if "gait" in source:
        return normalize_behavior_type("gait")
    if "restless" in source or "pacing" in source:
        return normalize_behavior_type("restlessness")
    if "stress" in source or "anxiety" in source:
        return "stress_signal"
    return normalize_behavior_type(entity_id.split(".", 1)[-1])


def _sync_marker(sync_key: str) -> str:
    return f"[DIVA_SYNC_KEY:{sync_key}]"


def _extract_diva_sync_key(description: str | None) -> str | None:
    if not description:
        return None
    match = re.search(r"\[DIVA_SYNC_KEY:(?P<key>[^\]]+)\]", description)
    if not match:
        return None
    return match.group("key")


def _description_without_sync_marker(description: str | None) -> str:
    if not description:
        return ""
    return re.sub(r"\s*\[DIVA_SYNC_KEY:[^\]]+\]\s*", "", description).strip()


def _external_event_payload(event) -> dict[str, Any]:
    description = _description_without_sync_marker(event.description)
    marker = _sync_marker(event.event_id)
    description = f"{description}\n{marker}" if description else marker
    return {
        EVENT_START: event.start,
        EVENT_END: event.end,
        EVENT_SUMMARY: event.summary,
        EVENT_DESCRIPTION: description,
        EVENT_LOCATION: event.location,
    }


def _external_event_to_scheduled_event(
    external,
    *,
    sync_key: str,
    fallback: ScheduledEvent | None,
    pet_id: str,
) -> ScheduledEvent:
    """Convert an external calendar event into a DIVA scheduled event."""
    category = _infer_event_category_from_external(external, fallback)
    description = _description_without_sync_marker(getattr(external, "description", None))
    metadata = dict(fallback.metadata) if fallback is not None else {}
    metadata["imported_from_calendar"] = True
    metadata["external_uid"] = getattr(external, "uid", None)
    return ScheduledEvent(
        event_id=sync_key,
        pet_id=pet_id,
        category=category,
        summary=getattr(external, "summary", None) or (fallback.summary if fallback else "Imported calendar event"),
        start=getattr(external, "start", None) or (fallback.start if fallback is not None else dt_util.now()),
        end=getattr(external, "end", None) or (fallback.end if fallback is not None else dt_util.now() + timedelta(minutes=30)),
        description=description or (fallback.description if fallback is not None else ""),
        location=getattr(external, "location", None) or (fallback.location if fallback is not None else None),
        metadata=metadata,
    )


def _infer_event_category_from_external(external, fallback: ScheduledEvent | None) -> str:
    """Infer a DIVA category from an external event description."""
    description = _description_without_sync_marker(getattr(external, "description", None)).lower()
    for prefix in ("routine:", "appointment:"):
        if prefix in description:
            tail = description.split(prefix, 1)[1].splitlines()[0].strip()
            if tail:
                return tail
    return fallback.category if fallback is not None else "care"


def _events_match(existing, desired) -> bool:
    return (
        getattr(existing, "summary", None) == desired.summary
        and getattr(existing, "start", None) == desired.start
        and getattr(existing, "end", None) == desired.end
        and (getattr(existing, "location", None) or None) == (desired.location or None)
        and _description_without_sync_marker(getattr(existing, "description", None))
        == _description_without_sync_marker(desired.description)
    )


def _external_event_snapshot(external) -> dict[str, Any]:
    """Serialize a linked calendar event for diagnostics and conflict review."""
    return {
        "uid": getattr(external, "uid", None),
        "recurrence_id": getattr(external, "recurrence_id", None),
        "summary": getattr(external, "summary", None),
        "start": getattr(getattr(external, "start", None), "isoformat", lambda: None)(),
        "end": getattr(getattr(external, "end", None), "isoformat", lambda: None)(),
        "description": _description_without_sync_marker(getattr(external, "description", None)),
        "location": getattr(external, "location", None),
    }


def _calendar_conflict_window(conflict: dict[str, Any], now) -> tuple[Any, Any]:
    """Return a fetch window wide enough to inspect the current conflicting event."""
    candidates = []
    for key in ("base_event", "effective_event", "external_event"):
        payload = conflict.get(key)
        if not isinstance(payload, dict):
            continue
        start = dt_util.parse_datetime(payload.get("start"))
        end = dt_util.parse_datetime(payload.get("end"))
        if start is not None:
            candidates.append(start)
        if end is not None:
            candidates.append(end)
    if not candidates:
        return (
            now - timedelta(days=1),
            now + timedelta(days=CALENDAR_SYNC_DEFAULT_DAYS),
        )
    return (
        min(candidates) - timedelta(days=1),
        max(candidates) + timedelta(days=1),
    )


def _upsert_medication_course_dict(pet: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Upsert a medication course in a pet payload."""
    medication_name = str(payload.get(CONF_MEDICATION_NAME, "")).strip()
    if not medication_name:
        raise ValueError("Medication name is required")
    items = [dict(item) for item in pet.get(CONF_MEDICATION_COURSES, []) or [] if item]
    normalized = {
        CONF_MEDICATION_NAME: medication_name,
        CONF_DOSE: str(payload.get(CONF_DOSE, "")).strip() or "recorded",
        CONF_MEDICATION_TIMES: str(payload.get(CONF_MEDICATION_TIMES, "")).strip() or "09:00",
        CONF_START_DATE: str(payload.get(CONF_START_DATE, "")).strip() or dt_util.now().date().isoformat(),
    }
    if route := str(payload.get(CONF_MEDICATION_ROUTE, "")).strip():
        normalized[CONF_MEDICATION_ROUTE] = route
    if end_date := str(payload.get(CONF_END_DATE, "")).strip():
        normalized[CONF_END_DATE] = end_date
    if notes := str(payload.get(CONF_NOTES, "")).strip():
        normalized[CONF_NOTES] = notes
    updated = False
    for index, item in enumerate(items):
        if str(item.get(CONF_MEDICATION_NAME, "")).strip().lower() == medication_name.lower():
            items[index] = normalized
            updated = True
            break
    if not updated:
        items.append(normalized)
    pet[CONF_MEDICATION_COURSES] = items
    return pet


def _remove_medication_course_dict(pet: dict[str, Any], medication_name: str) -> dict[str, Any]:
    """Remove a medication course from a pet payload."""
    name = medication_name.strip().lower()
    if not name:
        raise ValueError("Medication name is required")
    pet[CONF_MEDICATION_COURSES] = [
        item
        for item in pet.get(CONF_MEDICATION_COURSES, []) or []
        if str(item.get(CONF_MEDICATION_NAME, "")).strip().lower() != name
    ]
    return pet


def _upsert_vaccine_override_dict(pet: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Upsert a vaccine override in a pet payload."""
    dose_id = str(payload.get(CONF_VACCINE_DOSE_ID, "")).strip()
    vaccine_name = str(payload.get(CONF_VACCINE_NAME, "")).strip()
    if not dose_id and not vaccine_name:
        raise ValueError("Vaccine dose id or vaccine name is required")
    if not dose_id:
        dose_id = f"{pet.get(CONF_PET_ID, 'pet')}:{vaccine_name.lower().replace(' ', '_')}"
    normalized = {
        CONF_VACCINE_DOSE_ID: dose_id,
        CONF_VACCINE_NAME: vaccine_name or dose_id,
        CONF_DUE_DATE: str(payload.get(CONF_DUE_DATE, "")).strip() or dt_util.now().date().isoformat(),
        CONF_ROUTINE_CATEGORY: str(payload.get(CONF_ROUTINE_CATEGORY, "vet")).strip() or "vet",
        "source": "custom_ui",
    }
    if recurrence := payload.get(CONF_RECURRENCE_MONTHS):
        normalized[CONF_RECURRENCE_MONTHS] = int(recurrence)
    if notes := str(payload.get(CONF_NOTES, "")).strip():
        normalized[CONF_NOTES] = notes
    items = [dict(item) for item in pet.get(CONF_VACCINE_OVERRIDES, []) or [] if item]
    updated = False
    for index, item in enumerate(items):
        same_dose = str(item.get(CONF_VACCINE_DOSE_ID, "")).strip() == dose_id
        same_name = vaccine_name and str(item.get(CONF_VACCINE_NAME, "")).strip().lower() == vaccine_name.lower()
        if same_dose or same_name:
            items[index] = normalized
            updated = True
            break
    if not updated:
        items.append(normalized)
    pet[CONF_VACCINE_OVERRIDES] = items
    return pet


def _remove_vaccine_override_dict(
    pet: dict[str, Any],
    *,
    dose_id: str | None = None,
    vaccine_name: str | None = None,
) -> dict[str, Any]:
    """Remove a vaccine override from a pet payload."""
    normalized_dose_id = (dose_id or "").strip()
    normalized_name = (vaccine_name or "").strip().lower()
    if not normalized_dose_id and not normalized_name:
        raise ValueError("Vaccine dose id or vaccine name is required")
    pet[CONF_VACCINE_OVERRIDES] = [
        item
        for item in pet.get(CONF_VACCINE_OVERRIDES, []) or []
        if not (
            (normalized_dose_id and str(item.get(CONF_VACCINE_DOSE_ID, "")).strip() == normalized_dose_id)
            or (
                normalized_name
                and str(item.get(CONF_VACCINE_NAME, "")).strip().lower() == normalized_name
            )
        )
    ]
    return pet

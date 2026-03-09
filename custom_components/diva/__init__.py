"""Set up the DIVA integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_APPROVAL_ID,
    CONF_APPROVED_BY,
    CONF_BIRTHDATE,
    CONF_CONFLICT_ID,
    CONF_DOSE,
    CONF_DUE_DATE,
    CONF_DURATION_HOURS,
    CONF_END_DATE,
    CONF_EXPECTED_DAYS,
    CONF_NOTES,
    CONF_HISTORY_DAYS,
    CONF_HUB_NAME,
    CONF_MEDICATION_NAME,
    CONF_MEDICATION_ROUTE,
    CONF_MEDICATION_TIMES,
    CONF_NAME,
    CONF_OPERATION_MODE,
    CONF_PETS,
    CONF_PET_ID,
    CONF_PET_SCHEMA,
    CONF_FOOD_NAME,
    CONF_REASON,
    CONF_RESOLUTION,
    CONF_REPORT_FORMAT,
    CONF_SHOW_EDITOR_IN_SIDEBAR,
    CONF_WEIGHT,
    CONF_ROUTINE_CATEGORY,
    CONF_ROUTINE_DURATION_MINUTES,
    CONF_ROUTINE_EXCEPTION_ACTION,
    CONF_ROUTINE_EXCEPTION_DATE,
    CONF_ROUTINE_EXCEPTION_TIME,
    CONF_ROUTINE_LABEL,
    CONF_ROUTINE_LOCATION,
    CONF_ROUTINE_MEAL_TYPE,
    CONF_ROUTINE_PORTION_GRAMS,
    CONF_RECURRENCE_MONTHS,
    CONF_SEVERITY_SCORE,
    CONF_START_DATE,
    CONF_SYMPTOM_NAME,
    CONF_RECOVERY_TITLE,
    CONF_VACCINE_DOSE_ID,
    CONF_VACCINE_NAME,
    DOMAIN,
    MEAL_TYPES,
    OPERATION_MODES,
    CALENDAR_CONFLICT_RESOLUTION_OPTIONS,
    ROUTINE_CATEGORIES,
    ROUTINE_EXCEPTION_ACTIONS,
    PLATFORMS,
    SERVICE_ADD_SCHEDULE_EXCEPTION,
    SERVICE_APPLY_MODE,
    SERVICE_APPROVE_ACTION,
    SERVICE_COMPLETE_CHECKLIST_ITEM,
    SERVICE_DELAY_FEEDING,
    SERVICE_FEED_PET,
    SERVICE_FINISH_WALK,
    SERVICE_GENERATE_OPERATIONS_REPORT,
    SERVICE_LOG_CARE_ACTION,
    SERVICE_LOG_MEDICATION_DOSE,
    SERVICE_LOG_SYMPTOM,
    SERVICE_OBSERVE_BEHAVIOR,
    SERVICE_REPORT_BEHAVIOR,
    SERVICE_START_RECOVERY_PLAN,
    SERVICE_SKIP_FEEDING,
    SERVICE_START_WALK,
    SERVICE_SYNC_CALENDAR,
    SERVICE_COMPLETE_VACCINE_DOSE,
    SERVICE_GENERATE_VET_REPORT,
    SERVICE_LOG_WEIGHT,
    SERVICE_REMOVE_MEDICATION_COURSE,
    SERVICE_REMOVE_VACCINE_OVERRIDE,
    SERVICE_RESCHEDULE_VACCINE,
    SERVICE_RESOLVE_CALENDAR_CONFLICT,
    SERVICE_CANCEL_VACCINE,
    SERVICE_UPSERT_MEDICATION_COURSE,
    SERVICE_UPSERT_VACCINE_OVERRIDE,
    DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
)
from .pet import generate_pet_id, normalize_pet_config_record, serialize_diva_entry_settings_v3

DivaConfigEntry = ConfigEntry

SERVICE_TARGET_BASE = {
    vol.Optional(CONF_PET_ID): cv.string,
    vol.Optional(ATTR_DEVICE_ID): vol.Any(cv.string, [cv.string]),
}
SERVICE_FEED_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Optional("portion"): vol.Coerce(float),
        vol.Optional(CONF_ROUTINE_MEAL_TYPE): vol.In(MEAL_TYPES),
        vol.Optional(CONF_FOOD_NAME): cv.string,
    }
)
SERVICE_DELAY_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required("minutes"): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
    }
)
SERVICE_SYNC_CALENDAR_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Optional("days", default=14): vol.All(vol.Coerce(int), vol.Range(min=1, max=90)),
    }
)
SERVICE_RESOLVE_CALENDAR_CONFLICT_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required(CONF_CONFLICT_ID): cv.string,
        vol.Required(CONF_RESOLUTION): vol.In(CALENDAR_CONFLICT_RESOLUTION_OPTIONS),
        vol.Optional("note"): cv.string,
    }
)
SERVICE_LOG_CARE_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required("action"): cv.string,
        vol.Optional("actor"): cv.string,
        vol.Optional("note"): cv.string,
        vol.Optional("category", default="care"): cv.string,
    }
)
SERVICE_LOG_MEDICATION_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required(CONF_MEDICATION_NAME): cv.string,
        vol.Optional(CONF_DOSE): cv.string,
        vol.Optional("actor"): cv.string,
        vol.Optional("note"): cv.string,
    }
)
SERVICE_UPSERT_MEDICATION_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required(CONF_MEDICATION_NAME): cv.string,
        vol.Optional(CONF_DOSE): cv.string,
        vol.Optional("times"): cv.string,
        vol.Optional("start_date"): cv.string,
        vol.Optional("end_date"): cv.string,
        vol.Optional("route"): cv.string,
        vol.Optional(CONF_NOTES): cv.string,
    }
)
SERVICE_REMOVE_MEDICATION_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required(CONF_MEDICATION_NAME): cv.string,
    }
)
SERVICE_LOG_SYMPTOM_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required(CONF_SYMPTOM_NAME): cv.string,
        vol.Optional(CONF_SEVERITY_SCORE, default=3): vol.All(vol.Coerce(float), vol.Range(min=1, max=5)),
        vol.Optional(CONF_DURATION_HOURS): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=24)),
        vol.Optional("note"): cv.string,
        vol.Optional("source", default="manual"): cv.string,
    }
)
SERVICE_RECOVERY_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required(CONF_RECOVERY_TITLE): cv.string,
        vol.Required(CONF_EXPECTED_DAYS): vol.All(vol.Coerce(int), vol.Range(min=1, max=365)),
        vol.Optional("note"): cv.string,
    }
)
SERVICE_COMPLETE_VACCINE_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Optional(CONF_VACCINE_DOSE_ID): cv.string,
        vol.Optional(CONF_VACCINE_NAME): cv.string,
        vol.Optional("note"): cv.string,
    }
)
SERVICE_UPSERT_VACCINE_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Optional(CONF_VACCINE_DOSE_ID): cv.string,
        vol.Optional(CONF_VACCINE_NAME): cv.string,
        vol.Optional(CONF_DUE_DATE): cv.string,
        vol.Optional("recurrence_months"): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
        vol.Optional("category"): cv.string,
        vol.Optional(CONF_NOTES): cv.string,
    }
)
SERVICE_REMOVE_VACCINE_OVERRIDE_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Optional(CONF_VACCINE_DOSE_ID): cv.string,
        vol.Optional(CONF_VACCINE_NAME): cv.string,
    }
)
SERVICE_VET_REPORT_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Optional(CONF_REPORT_FORMAT, default="txt"): vol.In(["txt", "pdf"]),
        vol.Optional(CONF_HISTORY_DAYS, default=30): vol.All(vol.Coerce(int), vol.Range(min=1, max=365)),
    }
)
SERVICE_OPERATIONS_REPORT_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Optional(CONF_REPORT_FORMAT, default="txt"): vol.In(["txt", "pdf"]),
        vol.Optional(CONF_HISTORY_DAYS, default=7): vol.All(vol.Coerce(int), vol.Range(min=1, max=365)),
    }
)
SERVICE_WEIGHT_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required(CONF_WEIGHT): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=200)),
        vol.Optional("actor"): cv.string,
        vol.Optional("note"): cv.string,
        vol.Optional("source", default="manual"): cv.string,
    }
)
SERVICE_RESCHEDULE_VACCINE_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Optional(CONF_VACCINE_DOSE_ID): cv.string,
        vol.Optional(CONF_VACCINE_NAME): cv.string,
        vol.Required(CONF_DUE_DATE): cv.string,
        vol.Optional("note"): cv.string,
    }
)
SERVICE_CANCEL_VACCINE_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Optional(CONF_VACCINE_DOSE_ID): cv.string,
        vol.Optional(CONF_VACCINE_NAME): cv.string,
        vol.Optional(CONF_REASON): cv.string,
    }
)
SERVICE_REPORT_BEHAVIOR_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required("behavior_type"): cv.string,
        vol.Optional("severity", default="warning"): vol.In(["info", "warning", "critical"]),
        vol.Optional("message"): cv.string,
        vol.Optional("source", default="manual"): cv.string,
    }
)
SERVICE_OBSERVE_BEHAVIOR_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required("behavior_type"): cv.string,
        vol.Optional("severity", default="warning"): vol.In(["info", "warning", "critical"]),
        vol.Optional("message"): cv.string,
        vol.Optional("source", default="vision_pipeline"): cv.string,
        vol.Optional("confidence", default=0.85): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
        vol.Optional("duration_seconds"): vol.All(vol.Coerce(int), vol.Range(min=1, max=86400)),
        vol.Optional("model_name"): cv.string,
    }
)
SERVICE_COMPLETE_CHECKLIST_ITEM_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required("checklist_id"): cv.string,
        vol.Optional("actor"): cv.string,
        vol.Optional("note"): cv.string,
        vol.Optional("source", default="manual"): cv.string,
    }
)
SERVICE_APPROVE_ACTION_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required(CONF_APPROVAL_ID): cv.string,
        vol.Optional(CONF_APPROVED_BY): cv.string,
        vol.Optional("note"): cv.string,
    }
)
SERVICE_SIMPLE_SCHEMA = vol.Schema(SERVICE_TARGET_BASE)
SERVICE_APPLY_MODE_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required(CONF_OPERATION_MODE): vol.In(OPERATION_MODES),
    }
)
SERVICE_ADD_EXCEPTION_SCHEMA = vol.Schema(
    {
        **SERVICE_TARGET_BASE,
        vol.Required(CONF_ROUTINE_EXCEPTION_DATE): cv.string,
        vol.Required(CONF_ROUTINE_EXCEPTION_ACTION): vol.In(ROUTINE_EXCEPTION_ACTIONS),
        vol.Required(CONF_ROUTINE_CATEGORY): vol.In(ROUTINE_CATEGORIES),
        vol.Optional(CONF_ROUTINE_EXCEPTION_TIME): cv.string,
        vol.Optional(CONF_ROUTINE_DURATION_MINUTES): vol.Coerce(int),
        vol.Optional(CONF_ROUTINE_LABEL): cv.string,
        vol.Optional(CONF_ROUTINE_MEAL_TYPE): cv.string,
        vol.Optional(CONF_ROUTINE_PORTION_GRAMS): vol.Coerce(float),
        vol.Optional(CONF_ROUTINE_LOCATION): cv.string,
        vol.Optional(CONF_NOTES): cv.string,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the DIVA integration domain."""
    hass.data.setdefault(DOMAIN, {})
    from .frontend import async_setup_frontend

    await async_setup_frontend(hass)
    await _async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: DivaConfigEntry) -> bool:
    """Set up DIVA from a config entry."""
    from .coordinator import DivaCoordinator
    from .frontend import async_setup_frontend

    await async_setup_frontend(hass)
    coordinator = DivaCoordinator(hass, entry)
    entry.runtime_data = coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_register_devices()
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DivaConfigEntry) -> bool:
    """Unload a DIVA config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if not _has_active_coordinators(hass):
            from .frontend import async_unload_frontend

            await async_unload_frontend(hass)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: DivaConfigEntry) -> None:
    """Reload DIVA when a config entry changes."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate legacy entries to the multi-pet hub v3 config shape."""
    if entry.version >= 3:
        return True

    if CONF_PETS in entry.data:
        pets = [normalize_pet_config_record(dict(pet)) for pet in entry.data.get(CONF_PETS, [])]
        hass.config_entries.async_update_entry(
            entry,
            version=3,
            data=serialize_diva_entry_settings_v3(
                hub_name=entry.data.get(CONF_HUB_NAME, entry.title),
                show_editor_in_sidebar=entry.data.get(
                    CONF_SHOW_EDITOR_IN_SIDEBAR,
                    DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
                ),
                pets=pets,
            ),
            options=(
                serialize_diva_entry_settings_v3(
                    hub_name=entry.options.get(CONF_HUB_NAME, entry.data.get(CONF_HUB_NAME, entry.title)),
                    show_editor_in_sidebar=entry.options.get(
                        CONF_SHOW_EDITOR_IN_SIDEBAR,
                        entry.data.get(CONF_SHOW_EDITOR_IN_SIDEBAR, DEFAULT_SHOW_EDITOR_IN_SIDEBAR),
                    ),
                    pets=[normalize_pet_config_record(dict(pet)) for pet in entry.options.get(CONF_PETS, [])],
                )
                if entry.options.get(CONF_PETS)
                else {}
            ),
        )
        return True

    legacy_pet = dict(entry.data)
    legacy_pet.setdefault(
        CONF_PET_ID,
        generate_pet_id(
            f"{legacy_pet.get(CONF_NAME, 'pet')}_{legacy_pet.get(CONF_BIRTHDATE, '')}_{legacy_pet.get('species', '')}"
        ),
    )
    hass.config_entries.async_update_entry(
        entry,
        title=entry.title,
        version=3,
        data=serialize_diva_entry_settings_v3(
            hub_name=entry.title,
            show_editor_in_sidebar=DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
            pets=[legacy_pet],
        ),
        options={},
    )
    return True


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:
    """Allow removing a pet device from the DIVA hub."""
    settings = _entry_settings(config_entry)
    diva_identifiers = {identifier for identifier in device_entry.identifiers if identifier[0] == DOMAIN}
    if not diva_identifiers:
        return False

    pet_ids = {identifier for _domain, identifier in diva_identifiers if identifier != f"hub_{config_entry.entry_id}"}
    if not pet_ids:
        return False

    pet_id = next(iter(pet_ids))
    remaining = [pet for pet in settings[CONF_PETS] if pet[CONF_PET_ID] != pet_id]
    if len(remaining) == len(settings[CONF_PETS]) or not remaining:
        return False

    hass.config_entries.async_update_entry(
        config_entry,
        title=settings[CONF_HUB_NAME],
        data=serialize_diva_entry_settings_v3(
            hub_name=settings[CONF_HUB_NAME],
            show_editor_in_sidebar=settings.get(
                CONF_SHOW_EDITOR_IN_SIDEBAR,
                DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
            ),
            pets=remaining,
        ),
        options={},
    )
    await hass.config_entries.async_reload(config_entry.entry_id)
    return True


async def _async_setup_services(hass: HomeAssistant) -> None:
    """Register DIVA services once."""
    services_key = "services_registered"
    if hass.data[DOMAIN].get(services_key):
        return

    async def handle_feed_pet(call: ServiceCall) -> None:
        targets = _resolve_target_pets(hass, call)
        portion = call.data.get("portion")
        meal_type = call.data.get(CONF_ROUTINE_MEAL_TYPE)
        food_name = call.data.get(CONF_FOOD_NAME)
        requested_by = call.context.user_id
        for coordinator, pet_id in targets:
            await coordinator.async_feed_now(
                pet_id,
                portion,
                meal_type=meal_type,
                food_name=food_name,
                requested_by=requested_by,
            )

    async def handle_skip_feeding(call: ServiceCall) -> None:
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_skip_feeding(pet_id)

    async def handle_delay_feeding(call: ServiceCall) -> None:
        minutes = int(call.data["minutes"])
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_delay_feeding(pet_id, minutes)

    async def handle_start_walk(call: ServiceCall) -> None:
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_start_walk(pet_id)

    async def handle_finish_walk(call: ServiceCall) -> None:
        requested_by = call.context.user_id
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_finish_walk(pet_id, requested_by=requested_by)

    async def handle_sync_calendar(call: ServiceCall) -> None:
        days = int(call.data.get("days", 14))
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_sync_pet_calendar(pet_id, days=days)

    async def handle_resolve_calendar_conflict(call: ServiceCall) -> None:
        conflict_id = str(call.data[CONF_CONFLICT_ID])
        resolution = str(call.data[CONF_RESOLUTION])
        note = call.data.get("note")
        actor = call.context.user_id
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_resolve_calendar_conflict(
                pet_id,
                conflict_id=conflict_id,
                resolution=resolution,
                actor=actor,
                note=note,
            )

    async def handle_log_care_action(call: ServiceCall) -> None:
        action = str(call.data["action"])
        actor = call.data.get("actor") or call.context.user_id
        note = call.data.get("note")
        category = str(call.data.get("category", "care"))
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_log_care_action(
                pet_id,
                action,
                actor=actor,
                note=note,
                category=category,
            )

    async def handle_log_medication_dose(call: ServiceCall) -> None:
        medication_name = str(call.data[CONF_MEDICATION_NAME])
        dose = call.data.get(CONF_DOSE)
        actor = call.data.get("actor") or call.context.user_id
        note = call.data.get("note")
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_log_medication_dose(
                pet_id,
                medication_name,
                dose=dose,
                actor=actor,
                note=note,
            )

    async def handle_upsert_medication_course(call: ServiceCall) -> None:
        payload = {
            CONF_MEDICATION_NAME: call.data[CONF_MEDICATION_NAME],
            CONF_DOSE: call.data.get(CONF_DOSE),
            CONF_MEDICATION_TIMES: call.data.get("times"),
            CONF_START_DATE: call.data.get("start_date"),
            CONF_END_DATE: call.data.get("end_date"),
            CONF_MEDICATION_ROUTE: call.data.get("route"),
            CONF_NOTES: call.data.get(CONF_NOTES),
        }
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_upsert_medication_course(pet_id, payload)

    async def handle_remove_medication_course(call: ServiceCall) -> None:
        medication_name = str(call.data[CONF_MEDICATION_NAME])
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_remove_medication_course(pet_id, medication_name)

    async def handle_log_symptom(call: ServiceCall) -> None:
        symptom_name = str(call.data[CONF_SYMPTOM_NAME])
        severity_score = float(call.data.get(CONF_SEVERITY_SCORE, 3))
        duration_hours = call.data.get(CONF_DURATION_HOURS)
        note = call.data.get("note")
        source = str(call.data.get("source", "manual"))
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_log_symptom(
                pet_id,
                symptom_name,
                severity_score=severity_score,
                duration_hours=None if duration_hours is None else float(duration_hours),
                note=note,
                source=source,
            )

    async def handle_report_behavior(call: ServiceCall) -> None:
        behavior_type = str(call.data["behavior_type"])
        severity = str(call.data.get("severity", "warning"))
        message = call.data.get("message")
        source = str(call.data.get("source", "manual"))
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_report_behavior(
                pet_id,
                behavior_type,
                severity=severity,
                message=message,
                source=source,
            )

    async def handle_observe_behavior(call: ServiceCall) -> None:
        behavior_type = str(call.data["behavior_type"])
        severity = str(call.data.get("severity", "warning"))
        message = call.data.get("message")
        source = str(call.data.get("source", "vision_pipeline"))
        confidence = float(call.data.get("confidence", 0.85))
        duration_seconds = call.data.get("duration_seconds")
        model_name = call.data.get("model_name")
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_observe_behavior(
                pet_id,
                behavior_type,
                severity=severity,
                message=message,
                source=source,
                confidence=confidence,
                duration_seconds=int(duration_seconds) if duration_seconds is not None else None,
                model_name=model_name,
            )

    async def handle_apply_mode(call: ServiceCall) -> None:
        mode = str(call.data[CONF_OPERATION_MODE])
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_set_manual_mode(pet_id, mode)

    async def handle_start_recovery_plan(call: ServiceCall) -> None:
        title = str(call.data[CONF_RECOVERY_TITLE])
        expected_days = int(call.data[CONF_EXPECTED_DAYS])
        note = call.data.get("note")
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_start_recovery_plan(
                pet_id,
                title,
                expected_days=expected_days,
                note=note,
            )

    async def handle_complete_vaccine_dose(call: ServiceCall) -> None:
        dose_id = call.data.get(CONF_VACCINE_DOSE_ID)
        vaccine_name = call.data.get(CONF_VACCINE_NAME)
        note = call.data.get("note")
        requested_by = call.context.user_id
        if not dose_id and not vaccine_name:
            raise HomeAssistantError("Specify vaccine_dose_id or vaccine_name")
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_complete_vaccine_dose(
                pet_id,
                dose_id=dose_id,
                vaccine_name=vaccine_name,
                note=note,
                requested_by=requested_by,
            )

    async def handle_upsert_vaccine_override(call: ServiceCall) -> None:
        payload = {
            CONF_VACCINE_DOSE_ID: call.data.get(CONF_VACCINE_DOSE_ID),
            CONF_VACCINE_NAME: call.data.get(CONF_VACCINE_NAME),
            CONF_DUE_DATE: call.data.get(CONF_DUE_DATE),
            CONF_RECURRENCE_MONTHS: call.data.get("recurrence_months"),
            CONF_ROUTINE_CATEGORY: call.data.get("category"),
            CONF_NOTES: call.data.get(CONF_NOTES),
        }
        if not payload.get(CONF_VACCINE_DOSE_ID) and not payload.get(CONF_VACCINE_NAME):
            raise HomeAssistantError("Specify vaccine_dose_id or vaccine_name")
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_upsert_vaccine_override(pet_id, payload)

    async def handle_remove_vaccine_override(call: ServiceCall) -> None:
        dose_id = call.data.get(CONF_VACCINE_DOSE_ID)
        vaccine_name = call.data.get(CONF_VACCINE_NAME)
        if not dose_id and not vaccine_name:
            raise HomeAssistantError("Specify vaccine_dose_id or vaccine_name")
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_remove_vaccine_override(
                pet_id,
                dose_id=dose_id,
                vaccine_name=vaccine_name,
            )

    async def handle_generate_vet_report(call: ServiceCall) -> None:
        report_format = str(call.data.get(CONF_REPORT_FORMAT, "txt"))
        history_days = int(call.data.get(CONF_HISTORY_DAYS, 30))
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_generate_vet_report(
                pet_id,
                report_format=report_format,
                history_days=history_days,
            )

    async def handle_complete_checklist_item(call: ServiceCall) -> None:
        checklist_id = str(call.data["checklist_id"])
        actor = call.data.get("actor") or call.context.user_id
        note = call.data.get("note")
        source = str(call.data.get("source", "manual"))
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_complete_checklist_item(
                pet_id,
                checklist_id,
                actor=actor,
                note=note,
                source=source,
            )

    async def handle_approve_action(call: ServiceCall) -> None:
        approval_id = str(call.data[CONF_APPROVAL_ID])
        approved_by = call.data.get(CONF_APPROVED_BY) or call.context.user_id
        note = call.data.get("note")
        targets = (
            _resolve_target_pets(hass, call)
            if call.data.get(CONF_PET_ID) or call.data.get(ATTR_DEVICE_ID)
            else _resolve_target_pets_from_approval_id(hass, approval_id)
        )
        for coordinator, pet_id in targets:
            await coordinator.async_approve_action(
                pet_id,
                approval_id,
                approved_by=approved_by,
                note=note,
            )

    async def handle_generate_operations_report(call: ServiceCall) -> None:
        report_format = str(call.data.get(CONF_REPORT_FORMAT, "txt"))
        history_days = int(call.data.get(CONF_HISTORY_DAYS, 7))
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_generate_operations_report(
                pet_id,
                report_format=report_format,
                history_days=history_days,
            )

    async def handle_log_weight(call: ServiceCall) -> None:
        weight_kg = float(call.data[CONF_WEIGHT])
        actor = call.data.get("actor") or call.context.user_id
        note = call.data.get("note")
        source = str(call.data.get("source", "manual"))
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_log_weight(
                pet_id,
                weight_kg,
                actor=actor,
                note=note,
                source=source,
            )

    async def handle_reschedule_vaccine(call: ServiceCall) -> None:
        due_date = str(call.data[CONF_DUE_DATE])
        dose_id = call.data.get(CONF_VACCINE_DOSE_ID)
        vaccine_name = call.data.get(CONF_VACCINE_NAME)
        note = call.data.get("note")
        if not dose_id and not vaccine_name:
            raise HomeAssistantError("Specify vaccine_dose_id or vaccine_name")
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_reschedule_vaccine(
                pet_id,
                due_date=due_date,
                dose_id=dose_id,
                vaccine_name=vaccine_name,
                note=note,
            )

    async def handle_cancel_vaccine(call: ServiceCall) -> None:
        dose_id = call.data.get(CONF_VACCINE_DOSE_ID)
        vaccine_name = call.data.get(CONF_VACCINE_NAME)
        reason = call.data.get(CONF_REASON)
        if not dose_id and not vaccine_name:
            raise HomeAssistantError("Specify vaccine_dose_id or vaccine_name")
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_cancel_vaccine(
                pet_id,
                dose_id=dose_id,
                vaccine_name=vaccine_name,
                reason=reason,
            )

    async def handle_add_schedule_exception(call: ServiceCall) -> None:
        payload = {
            key: value
            for key, value in call.data.items()
            if key
            in {
                CONF_ROUTINE_EXCEPTION_DATE,
                CONF_ROUTINE_EXCEPTION_ACTION,
                CONF_ROUTINE_CATEGORY,
                CONF_ROUTINE_EXCEPTION_TIME,
                CONF_ROUTINE_DURATION_MINUTES,
                CONF_ROUTINE_LABEL,
                CONF_ROUTINE_MEAL_TYPE,
                CONF_ROUTINE_PORTION_GRAMS,
                CONF_ROUTINE_LOCATION,
                CONF_NOTES,
            }
        }
        for coordinator, pet_id in _resolve_target_pets(hass, call):
            await coordinator.async_add_schedule_exception(pet_id, payload)

    hass.services.async_register(DOMAIN, SERVICE_FEED_PET, handle_feed_pet, schema=SERVICE_FEED_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SKIP_FEEDING, handle_skip_feeding, schema=SERVICE_SIMPLE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_DELAY_FEEDING, handle_delay_feeding, schema=SERVICE_DELAY_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_START_WALK, handle_start_walk, schema=SERVICE_SIMPLE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_FINISH_WALK, handle_finish_walk, schema=SERVICE_SIMPLE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SYNC_CALENDAR, handle_sync_calendar, schema=SERVICE_SYNC_CALENDAR_SCHEMA)
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESOLVE_CALENDAR_CONFLICT,
        handle_resolve_calendar_conflict,
        schema=SERVICE_RESOLVE_CALENDAR_CONFLICT_SCHEMA,
    )
    hass.services.async_register(DOMAIN, SERVICE_LOG_CARE_ACTION, handle_log_care_action, schema=SERVICE_LOG_CARE_SCHEMA)
    hass.services.async_register(
        DOMAIN,
        SERVICE_LOG_MEDICATION_DOSE,
        handle_log_medication_dose,
        schema=SERVICE_LOG_MEDICATION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPSERT_MEDICATION_COURSE,
        handle_upsert_medication_course,
        schema=SERVICE_UPSERT_MEDICATION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_MEDICATION_COURSE,
        handle_remove_medication_course,
        schema=SERVICE_REMOVE_MEDICATION_SCHEMA,
    )
    hass.services.async_register(DOMAIN, SERVICE_LOG_SYMPTOM, handle_log_symptom, schema=SERVICE_LOG_SYMPTOM_SCHEMA)
    hass.services.async_register(
        DOMAIN,
        SERVICE_REPORT_BEHAVIOR,
        handle_report_behavior,
        schema=SERVICE_REPORT_BEHAVIOR_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_OBSERVE_BEHAVIOR,
        handle_observe_behavior,
        schema=SERVICE_OBSERVE_BEHAVIOR_SCHEMA,
    )
    hass.services.async_register(DOMAIN, SERVICE_APPLY_MODE, handle_apply_mode, schema=SERVICE_APPLY_MODE_SCHEMA)
    hass.services.async_register(
        DOMAIN,
        SERVICE_START_RECOVERY_PLAN,
        handle_start_recovery_plan,
        schema=SERVICE_RECOVERY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_COMPLETE_VACCINE_DOSE,
        handle_complete_vaccine_dose,
        schema=SERVICE_COMPLETE_VACCINE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPSERT_VACCINE_OVERRIDE,
        handle_upsert_vaccine_override,
        schema=SERVICE_UPSERT_VACCINE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_VACCINE_OVERRIDE,
        handle_remove_vaccine_override,
        schema=SERVICE_REMOVE_VACCINE_OVERRIDE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_VET_REPORT,
        handle_generate_vet_report,
        schema=SERVICE_VET_REPORT_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_COMPLETE_CHECKLIST_ITEM,
        handle_complete_checklist_item,
        schema=SERVICE_COMPLETE_CHECKLIST_ITEM_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_APPROVE_ACTION,
        handle_approve_action,
        schema=SERVICE_APPROVE_ACTION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_OPERATIONS_REPORT,
        handle_generate_operations_report,
        schema=SERVICE_OPERATIONS_REPORT_SCHEMA,
    )
    hass.services.async_register(DOMAIN, SERVICE_LOG_WEIGHT, handle_log_weight, schema=SERVICE_WEIGHT_SCHEMA)
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESCHEDULE_VACCINE,
        handle_reschedule_vaccine,
        schema=SERVICE_RESCHEDULE_VACCINE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CANCEL_VACCINE,
        handle_cancel_vaccine,
        schema=SERVICE_CANCEL_VACCINE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_SCHEDULE_EXCEPTION,
        handle_add_schedule_exception,
        schema=SERVICE_ADD_EXCEPTION_SCHEMA,
    )
    hass.data[DOMAIN][services_key] = True


def _resolve_target_pets(hass: HomeAssistant, call: ServiceCall) -> list[tuple[Any, str]]:
    """Resolve a service call to one or more pet targets."""
    coordinators = [value for value in hass.data.get(DOMAIN, {}).values() if hasattr(value, "pets")]
    if not coordinators:
        raise HomeAssistantError("No DIVA pets are configured")

    if pet_id := call.data.get(CONF_PET_ID):
        selected = [(coordinator, pet_id) for coordinator in coordinators if pet_id in coordinator.pets]
        if not selected:
            raise HomeAssistantError(f"Unknown DIVA pet_id: {pet_id}")
        return selected

    device_ids = call.data.get(ATTR_DEVICE_ID)
    if device_ids:
        device_id_list = [device_ids] if isinstance(device_ids, str) else list(device_ids)
        device_registry = dr.async_get(hass)
        selected: list[tuple[Any, str]] = []
        for device_id in device_id_list:
            device = device_registry.async_get(device_id)
            if device is None:
                continue
            diva_identifiers = [identifier for identifier in device.identifiers if identifier[0] == DOMAIN]
            for _domain, identifier in diva_identifiers:
                for coordinator in coordinators:
                    if identifier in coordinator.pets:
                        selected.append((coordinator, identifier))
        if not selected:
            raise HomeAssistantError("No DIVA pets matched the requested device target")
        return selected

    all_pets = [(coordinator, pet_id) for coordinator in coordinators for pet_id in coordinator.pet_ids]
    if len(all_pets) == 1:
        return all_pets

    raise HomeAssistantError("Specify pet_id or device_id when multiple DIVA pets exist")


def _entry_settings(entry: ConfigEntry) -> dict[str, Any]:
    """Return merged hub settings from a config entry."""
    if entry.options.get(CONF_PETS):
        return {
            CONF_HUB_NAME: entry.options.get(CONF_HUB_NAME, entry.title),
            CONF_PET_SCHEMA: int(entry.options.get(CONF_PET_SCHEMA, entry.data.get(CONF_PET_SCHEMA, 0)) or 0),
            CONF_SHOW_EDITOR_IN_SIDEBAR: entry.options.get(
                CONF_SHOW_EDITOR_IN_SIDEBAR,
                entry.data.get(CONF_SHOW_EDITOR_IN_SIDEBAR, DEFAULT_SHOW_EDITOR_IN_SIDEBAR),
            ),
            CONF_PETS: [normalize_pet_config_record(dict(pet)) for pet in entry.options.get(CONF_PETS, [])],
        }
    if CONF_PETS in entry.data:
        return {
            CONF_HUB_NAME: entry.data.get(CONF_HUB_NAME, entry.title),
            CONF_PET_SCHEMA: int(entry.data.get(CONF_PET_SCHEMA, 0) or 0),
            CONF_SHOW_EDITOR_IN_SIDEBAR: entry.data.get(
                CONF_SHOW_EDITOR_IN_SIDEBAR,
                DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
            ),
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
        CONF_SHOW_EDITOR_IN_SIDEBAR: entry.data.get(
            CONF_SHOW_EDITOR_IN_SIDEBAR,
            DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
        ),
        CONF_PETS: [legacy_pet],
    }


def _has_active_coordinators(hass: HomeAssistant) -> bool:
    """Return whether any DIVA config entry coordinators remain loaded."""
    return any(hasattr(value, "pet_ids") for value in hass.data.get(DOMAIN, {}).values())


def _resolve_target_pets_from_approval_id(hass: HomeAssistant, approval_id: str) -> list[tuple[Any, str]]:
    """Resolve a queued approval id to its owning DIVA pet."""
    pet_id = approval_id.split(":approval:", 1)[0].strip()
    if not pet_id:
        raise HomeAssistantError("Invalid approval id")
    coordinators = [value for value in hass.data.get(DOMAIN, {}).values() if hasattr(value, "pets")]
    selected = [(coordinator, pet_id) for coordinator in coordinators if pet_id in coordinator.pets]
    if not selected:
        raise HomeAssistantError(f"Unknown DIVA approval target: {approval_id}")
    return selected

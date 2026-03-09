import asyncio
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

from custom_components.diva.const import (
    CALENDAR_SOURCE_OF_TRUTH_CALENDAR,
    CALENDAR_SOURCE_OF_TRUTH_DIVA,
    CAMERA_EVENT_CALENDAR_SYNCED,
)
from custom_components.diva.coordinator import (
    DivaCoordinator,
    _extract_diva_sync_key,
)
from custom_components.diva.pet import CalendarLink, PetEngine, PetProfile, ScheduledEvent
from homeassistant.components.calendar.const import (
    CalendarEntityFeature,
    DATA_COMPONENT as CALENDAR_DATA_COMPONENT,
)


UTC = timezone.utc


class FakeCalendarEntity:
    def __init__(self, *, features: CalendarEntityFeature, events=None) -> None:
        self.supported_features = features
        self.events = list(events or [])
        self.created: list[dict] = []
        self.updated: list[tuple[str, dict, str | None]] = []
        self.deleted: list[tuple[str, str | None]] = []

    async def async_get_events(self, hass, start, end):
        return list(self.events)

    async def async_create_event(self, **payload) -> None:
        self.created.append(payload)

    async def async_update_event(self, uid, payload, recurrence_id=None) -> None:
        self.updated.append((uid, payload, recurrence_id))

    async def async_delete_event(self, uid, recurrence_id=None) -> None:
        self.deleted.append((uid, recurrence_id))


class FakeCalendarComponent:
    def __init__(self, entity: FakeCalendarEntity | None) -> None:
        self._entity = entity

    def get_entity(self, entity_id: str):
        if entity_id != "calendar.family":
            return None
        return self._entity


def _scheduled_event(*, suffix: str = "1", summary: str = "Feed", offset_minutes: int = 0) -> ScheduledEvent:
    start = datetime(2026, 3, 9, 8, 0, tzinfo=UTC) + timedelta(minutes=offset_minutes)
    return ScheduledEvent(
        event_id=f"event-{suffix}",
        pet_id="don_abrikos_a1b2c3",
        category="feed",
        summary=summary,
        start=start,
        end=start + timedelta(minutes=15),
        description="Routine: feed",
        location="Kitchen",
    )


def _profile(source_of_truth: str) -> PetProfile:
    return PetProfile(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="English Cocker Spaniel",
        birthdate=date(2020, 1, 1),
        weight_kg=12.4,
        diet_mode="adult",
        calendar_links=(
            CalendarLink(
                calendar_entity_id="calendar.family",
                source_of_truth=source_of_truth,
            ),
        ),
        external_calendar_entity_ids=("calendar.family",),
    )


def _external_event(event: ScheduledEvent, *, summary: str | None = None):
    return SimpleNamespace(
        uid=f"uid-{event.event_id}",
        recurrence_id=None,
        summary=summary or event.summary,
        start=event.start,
        end=event.end,
        description=f"{event.description}\n[DIVA_SYNC_KEY:{event.event_id}]",
        location=event.location,
    )


def _coordinator() -> DivaCoordinator:
    return object.__new__(DivaCoordinator)


def _sync_coordinator(
    *,
    source_of_truth: str,
    entity: FakeCalendarEntity,
    base_events: list[ScheduledEvent],
    effective_events: list[ScheduledEvent],
) -> tuple[DivaCoordinator, SimpleNamespace]:
    coordinator = _coordinator()
    profile = _profile(source_of_truth)
    engine = PetEngine(profile)
    managed = SimpleNamespace(profile=profile, engine=engine)
    coordinator._pets = {profile.pet_id: managed}
    coordinator.hass = SimpleNamespace(
        data={CALENDAR_DATA_COMPONENT: FakeCalendarComponent(entity)},
        states=SimpleNamespace(get=lambda entity_id: None),
    )
    coordinator.data = {}
    coordinator._build_pet_context = lambda _managed, now=None: SimpleNamespace()

    async def _noop_save() -> None:
        return None

    async def _noop_fire(items) -> None:
        return None

    async def _noop_refresh() -> None:
        return None

    coordinator._async_save_runtime_state = _noop_save
    coordinator._async_fire_notices = _noop_fire
    coordinator.async_request_refresh = _noop_refresh

    def _timeline_events(start, end, context, include_calendar_overrides=True):
        return list(effective_events if include_calendar_overrides else base_events)

    managed.engine.timeline_events = _timeline_events
    return coordinator, managed


def test_apply_outbound_calendar_event_creates_new_event_with_sync_marker() -> None:
    coordinator = _coordinator()
    entity = FakeCalendarEntity(features=CalendarEntityFeature.CREATE_EVENT)
    desired = _scheduled_event()

    state, external_uid = asyncio.run(
        DivaCoordinator._async_apply_outbound_calendar_event(
            coordinator,
            entity,
            features=CalendarEntityFeature.CREATE_EVENT,
            existing=None,
            desired=desired,
        )
    )

    assert state == "created"
    assert external_uid is None
    assert len(entity.created) == 1
    assert entity.created[0]["summary"] == desired.summary
    assert _extract_diva_sync_key(entity.created[0]["description"]) == desired.event_id


def test_apply_outbound_calendar_event_updates_existing_event() -> None:
    coordinator = _coordinator()
    entity = FakeCalendarEntity(features=CalendarEntityFeature.UPDATE_EVENT)
    desired = _scheduled_event(summary="Updated feed")
    existing = _external_event(_scheduled_event(summary="Old feed"))

    state, external_uid = asyncio.run(
        DivaCoordinator._async_apply_outbound_calendar_event(
            coordinator,
            entity,
            features=CalendarEntityFeature.UPDATE_EVENT,
            existing=existing,
            desired=desired,
        )
    )

    assert state == "updated"
    assert external_uid == existing.uid
    assert entity.updated == [
        (
            existing.uid,
            entity.updated[0][1],
            None,
        )
    ]
    assert entity.updated[0][1]["summary"] == "Updated feed"
    assert _extract_diva_sync_key(entity.updated[0][1]["description"]) == desired.event_id


def test_apply_outbound_calendar_event_deletes_stale_event() -> None:
    coordinator = _coordinator()
    entity = FakeCalendarEntity(features=CalendarEntityFeature.DELETE_EVENT)
    existing = _external_event(_scheduled_event())

    state, external_uid = asyncio.run(
        DivaCoordinator._async_apply_outbound_calendar_event(
            coordinator,
            entity,
            features=CalendarEntityFeature.DELETE_EVENT,
            existing=existing,
            desired=None,
        )
    )

    assert state == "deleted"
    assert external_uid == existing.uid
    assert entity.deleted == [(existing.uid, None)]


def test_import_external_calendar_difference_creates_replace_override() -> None:
    coordinator = _coordinator()
    profile = _profile(CALENDAR_SOURCE_OF_TRUTH_CALENDAR)
    engine = PetEngine(profile)
    managed = SimpleNamespace(profile=profile, engine=engine)
    now = datetime(2026, 3, 9, 12, 0, tzinfo=UTC)
    base_event = _scheduled_event()
    external = _external_event(base_event, summary="Imported feed from calendar")

    changed, notices, counts = coordinator._import_external_calendar_differences(
        managed,
        "calendar.family",
        source_of_truth=CALENDAR_SOURCE_OF_TRUTH_CALENDAR,
        now=now,
        base_by_key={base_event.event_id: base_event},
        effective_by_key={base_event.event_id: base_event},
        synced_external={base_event.event_id: external},
    )

    assert changed is True
    assert counts == {"imported": 1, "conflicts": 0, "skipped": 0}
    assert len(notices) == 1
    override = engine.calendar_override_record("calendar.family", base_event.event_id)
    assert override is not None
    assert override["mode"] == "replace"
    assert override["event"]["summary"] == "Imported feed from calendar"
    assert engine.state.calendar_sync_state["calendar.family"]["events"][base_event.event_id]["last_state"] == "imported_override"


def test_import_external_calendar_difference_preserves_suppressed_conflict_count() -> None:
    coordinator = _coordinator()
    profile = _profile("manual_review")
    engine = PetEngine(profile)
    managed = SimpleNamespace(profile=profile, engine=engine)
    now = datetime(2026, 3, 9, 12, 0, tzinfo=UTC)
    base_event = _scheduled_event()
    external = _external_event(base_event, summary="Imported feed from calendar")

    conflict = engine.record_calendar_conflict(
        "calendar.family",
        sync_key=base_event.event_id,
        conflict_type="diverged",
        reason="External calendar diverged from DIVA event",
        source_of_truth="manual_review",
        external_uid=external.uid,
        base_event=base_event,
        effective_event=base_event,
        external_event={
            "uid": external.uid,
            "summary": external.summary,
            "start": external.start.isoformat(),
            "end": external.end.isoformat(),
            "description": base_event.description,
            "location": external.location,
        },
        occurred_at=now,
    )
    engine.resolve_calendar_conflict(
        engine.state.calendar_conflicts[0]["conflict_id"],
        resolution="dismiss",
        resolved_at=now,
    )

    changed, notices, counts = coordinator._import_external_calendar_differences(
        managed,
        "calendar.family",
        source_of_truth="manual_review",
        now=now + timedelta(minutes=1),
        base_by_key={base_event.event_id: base_event},
        effective_by_key={base_event.event_id: base_event},
        synced_external={base_event.event_id: external},
    )

    assert conflict
    assert changed is False
    assert notices == []
    assert counts == {"imported": 0, "conflicts": 0, "skipped": 0}


def test_async_sync_pet_calendar_creates_external_event() -> None:
    desired = _scheduled_event()
    entity = FakeCalendarEntity(features=CalendarEntityFeature.CREATE_EVENT)
    coordinator, managed = _sync_coordinator(
        source_of_truth=CALENDAR_SOURCE_OF_TRUTH_DIVA,
        entity=entity,
        base_events=[desired],
        effective_events=[desired],
    )

    changes = asyncio.run(
        DivaCoordinator.async_sync_pet_calendar(
            coordinator,
            managed.profile.pet_id,
            days=14,
        )
    )

    assert changes == 1
    assert len(entity.created) == 1
    assert entity.created[0]["summary"] == desired.summary
    assert managed.engine.state.calendar_sync_state["calendar.family"]["events"][desired.event_id]["last_state"] == "created"
    assert managed.engine.state.recent_records[-1]["name"] == CAMERA_EVENT_CALENDAR_SYNCED


def test_async_sync_pet_calendar_updates_external_event() -> None:
    desired = _scheduled_event(summary="Updated feed")
    existing = _external_event(_scheduled_event(summary="Old feed"))
    entity = FakeCalendarEntity(
        features=CalendarEntityFeature.UPDATE_EVENT,
        events=[existing],
    )
    coordinator, managed = _sync_coordinator(
        source_of_truth=CALENDAR_SOURCE_OF_TRUTH_DIVA,
        entity=entity,
        base_events=[desired],
        effective_events=[desired],
    )

    changes = asyncio.run(
        DivaCoordinator.async_sync_pet_calendar(
            coordinator,
            managed.profile.pet_id,
            days=14,
        )
    )

    assert changes == 1
    assert entity.updated
    assert entity.updated[0][0] == existing.uid
    assert entity.updated[0][1]["summary"] == "Updated feed"
    assert managed.engine.state.calendar_sync_state["calendar.family"]["events"][desired.event_id]["last_state"] == "updated"


def test_async_sync_pet_calendar_deletes_stale_external_event() -> None:
    stale = _external_event(_scheduled_event())
    entity = FakeCalendarEntity(
        features=CalendarEntityFeature.DELETE_EVENT,
        events=[stale],
    )
    coordinator, managed = _sync_coordinator(
        source_of_truth=CALENDAR_SOURCE_OF_TRUTH_DIVA,
        entity=entity,
        base_events=[],
        effective_events=[],
    )

    changes = asyncio.run(
        DivaCoordinator.async_sync_pet_calendar(
            coordinator,
            managed.profile.pet_id,
            days=14,
        )
    )

    assert changes == 1
    assert entity.deleted == [(stale.uid, None)]
    assert managed.engine.state.calendar_sync_state["calendar.family"]["events"]["event-1"]["last_state"] == "deleted"


def test_async_sync_pet_calendar_imports_external_override() -> None:
    base_event = _scheduled_event()
    external = _external_event(base_event, summary="Imported feed from calendar")
    entity = FakeCalendarEntity(
        features=CalendarEntityFeature.CREATE_EVENT | CalendarEntityFeature.UPDATE_EVENT | CalendarEntityFeature.DELETE_EVENT,
        events=[external],
    )
    coordinator, managed = _sync_coordinator(
        source_of_truth=CALENDAR_SOURCE_OF_TRUTH_CALENDAR,
        entity=entity,
        base_events=[base_event],
        effective_events=[base_event],
    )

    changes = asyncio.run(
        DivaCoordinator.async_sync_pet_calendar(
            coordinator,
            managed.profile.pet_id,
            days=14,
        )
    )

    assert changes == 1
    override = managed.engine.calendar_override_record("calendar.family", base_event.event_id)
    assert override is not None
    assert override["mode"] == "replace"
    assert override["event"]["summary"] == "Imported feed from calendar"
    assert entity.created == []
    assert entity.updated == []
    assert entity.deleted == []
    assert managed.engine.state.calendar_sync_state["calendar.family"]["events"][base_event.event_id]["last_state"] == "imported_override"

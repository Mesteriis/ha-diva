from datetime import date, datetime, timezone

from custom_components.diva.const import (
    CALENDAR_CONFLICT_RESOLUTION_DISMISS,
    CALENDAR_SOURCE_OF_TRUTH_CALENDAR,
    CALENDAR_SOURCE_OF_TRUTH_DIVA,
    CALENDAR_SOURCE_OF_TRUTH_MANUAL_REVIEW,
)
from custom_components.diva.pet import (
    CalendarLink,
    PetContext,
    PetEngine,
    PetProfile,
    ScheduledEvent,
    parse_calendar_links,
)


UTC = timezone.utc


def _profile() -> PetProfile:
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
                source_of_truth=CALENDAR_SOURCE_OF_TRUTH_CALENDAR,
            ),
        ),
    )


def test_parse_calendar_links_supports_policy_and_fallbacks() -> None:
    links = parse_calendar_links(
        [{"calendar_entity_id": "calendar.family", "source_of_truth": "calendar"}],
        fallback_entity_ids=["calendar.legacy"],
    )
    assert links[0].calendar_entity_id == "calendar.family"
    assert links[0].source_of_truth == CALENDAR_SOURCE_OF_TRUTH_CALENDAR

    fallback = parse_calendar_links(None, fallback_entity_ids=["calendar.legacy"])
    assert fallback[0].calendar_entity_id == "calendar.legacy"
    assert fallback[0].source_of_truth == CALENDAR_SOURCE_OF_TRUTH_DIVA


def test_calendar_replace_and_skip_overrides_change_timeline() -> None:
    engine = PetEngine(_profile())
    start = datetime(2026, 3, 9, 0, 0, tzinfo=UTC)
    end = datetime(2026, 3, 10, 0, 0, tzinfo=UTC)

    base_event = engine.timeline_events(start, end, PetContext())[0]
    imported = ScheduledEvent(
        event_id=base_event.event_id,
        pet_id=base_event.pet_id,
        category=base_event.category,
        summary="Imported feeding from Google Calendar",
        start=base_event.start.replace(hour=9, minute=30),
        end=base_event.end.replace(hour=9, minute=45),
        description="Imported override",
        location="Kitchen",
    )

    engine.upsert_calendar_override(
        "calendar.family",
        sync_key=base_event.event_id,
        mode="replace",
        event=imported,
        external_uid="abc-1",
        source_of_truth=CALENDAR_SOURCE_OF_TRUTH_CALENDAR,
        imported_at=start,
    )
    replaced = next(
        event for event in engine.timeline_events(start, end, PetContext()) if event.event_id == base_event.event_id
    )
    assert replaced.summary == "Imported feeding from Google Calendar"
    assert replaced.location == "Kitchen"

    engine.upsert_calendar_override(
        "calendar.family",
        sync_key=base_event.event_id,
        mode="skip",
        event=None,
        external_uid=None,
        source_of_truth=CALENDAR_SOURCE_OF_TRUTH_CALENDAR,
        imported_at=start,
    )
    skipped = [event for event in engine.timeline_events(start, end, PetContext()) if event.event_id == base_event.event_id]
    assert skipped == []


def test_calendar_custom_override_adds_external_event_into_timeline() -> None:
    engine = PetEngine(_profile())
    start = datetime(2026, 3, 9, 0, 0, tzinfo=UTC)
    end = datetime(2026, 3, 10, 0, 0, tzinfo=UTC)

    imported = ScheduledEvent(
        event_id="external:custom:1",
        pet_id=engine.profile.pet_id,
        category="care",
        summary="Imported grooming visit",
        start=datetime(2026, 3, 9, 16, 0, tzinfo=UTC),
        end=datetime(2026, 3, 9, 17, 0, tzinfo=UTC),
        description="Imported custom event",
        location="Studio",
    )
    engine.upsert_calendar_override(
        "calendar.family",
        sync_key=imported.event_id,
        mode="custom",
        event=imported,
        external_uid="abc-2",
        source_of_truth=CALENDAR_SOURCE_OF_TRUTH_CALENDAR,
        imported_at=start,
    )

    events = engine.timeline_events(start, end, PetContext())
    assert any(event.summary == "Imported grooming visit" for event in events)


def test_calendar_conflicts_are_deduplicated_and_dismiss_can_suppress_reopen() -> None:
    profile = PetProfile(
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
                source_of_truth=CALENDAR_SOURCE_OF_TRUTH_MANUAL_REVIEW,
            ),
        ),
    )
    engine = PetEngine(profile)
    start = datetime(2026, 3, 9, 0, 0, tzinfo=UTC)
    end = datetime(2026, 3, 10, 0, 0, tzinfo=UTC)
    base_event = engine.timeline_events(start, end, PetContext())[0]

    notices = engine.record_calendar_conflict(
        "calendar.family",
        sync_key=base_event.event_id,
        conflict_type="diverged",
        reason="External calendar diverged from DIVA event",
        source_of_truth=CALENDAR_SOURCE_OF_TRUTH_MANUAL_REVIEW,
        external_uid="evt-1",
        base_event=base_event,
        effective_event=base_event,
        external_event={
            "uid": "evt-1",
            "summary": "External change",
            "start": base_event.start.isoformat(),
            "end": base_event.end.isoformat(),
            "description": "Changed externally",
            "location": None,
        },
        occurred_at=start,
    )
    assert len(notices) == 1
    assert len(engine.state.calendar_conflicts) == 1

    duplicate = engine.record_calendar_conflict(
        "calendar.family",
        sync_key=base_event.event_id,
        conflict_type="diverged",
        reason="External calendar diverged from DIVA event",
        source_of_truth=CALENDAR_SOURCE_OF_TRUTH_MANUAL_REVIEW,
        external_uid="evt-1",
        base_event=base_event,
        effective_event=base_event,
        external_event={
            "uid": "evt-1",
            "summary": "External change",
            "start": base_event.start.isoformat(),
            "end": base_event.end.isoformat(),
            "description": "Changed externally",
            "location": None,
        },
        occurred_at=start,
    )
    assert duplicate == []
    assert len(engine.state.calendar_conflicts) == 1

    conflict_id = engine.state.calendar_conflicts[0]["conflict_id"]
    resolution_notices = engine.resolve_calendar_conflict(
        conflict_id,
        resolution=CALENDAR_CONFLICT_RESOLUTION_DISMISS,
        resolved_at=start,
        actor="tester",
    )
    assert len(resolution_notices) == 1
    assert engine.state.calendar_conflicts == []
    assert engine.state.calendar_conflict_resolutions[-1]["resolution"] == CALENDAR_CONFLICT_RESOLUTION_DISMISS

    suppressed = engine.record_calendar_conflict(
        "calendar.family",
        sync_key=base_event.event_id,
        conflict_type="diverged",
        reason="External calendar diverged from DIVA event",
        source_of_truth=CALENDAR_SOURCE_OF_TRUTH_MANUAL_REVIEW,
        external_uid="evt-1",
        base_event=base_event,
        effective_event=base_event,
        external_event={
            "uid": "evt-1",
            "summary": "External change",
            "start": base_event.start.isoformat(),
            "end": base_event.end.isoformat(),
            "description": "Changed externally",
            "location": None,
        },
        occurred_at=start.replace(hour=1),
    )
    assert suppressed == []
    assert engine.state.calendar_conflicts == []

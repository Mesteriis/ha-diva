import asyncio
from datetime import date, datetime, timezone
from types import SimpleNamespace

from custom_components.diva.binary_sensor import async_setup_entry as setup_binary_sensors
from custom_components.diva.button import async_setup_entry as setup_buttons
from custom_components.diva.calendar import async_setup_entry as setup_calendars
from custom_components.diva.camera import async_setup_entry as setup_cameras
from custom_components.diva.device_tracker import async_setup_entry as setup_device_trackers
from custom_components.diva.number import async_setup_entry as setup_numbers
from custom_components.diva.pet import PetContext, PetEngine, PetProfile
from custom_components.diva.select import async_setup_entry as setup_selects
from custom_components.diva.sensor import async_setup_entry as setup_sensors
from homeassistant.config_entries import ConfigEntry


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
        camera_entity_id="camera.pet_guardian",
        external_calendar_entity_ids=("calendar.family",),
    )


def _build_runtime():
    profile = _profile()
    engine = PetEngine(profile)
    now = datetime(2026, 3, 9, 12, 0, tzinfo=UTC)
    snapshot, notices = engine.refresh(now, PetContext())
    engine.append_records(notices)
    engine.state.gps_history.append(
        {
            "timestamp": now.isoformat(),
            "latitude": 40.4168,
            "longitude": -3.7038,
        }
    )
    engine.state.generated_reports.append(
        {
            "job_id": "don_abrikos_a1b2c3:report:vet:1",
            "path": "/config/diva_reports/don-vet.pdf",
            "generated_at": now.isoformat(),
            "format": "pdf",
            "history_days": 14,
            "caption": "Vet report",
            "report_kind": "vet",
            "status": "completed",
        }
    )
    engine.state.report_jobs.append(
        {
            "job_id": "don_abrikos_a1b2c3:report:vet:1",
            "report_kind": "vet",
            "report_format": "pdf",
            "history_days": 14,
            "status": "completed",
            "requested_at": now.isoformat(),
            "finished_at": now.isoformat(),
            "report_path": "/config/diva_reports/don-vet.pdf",
        }
    )
    managed = SimpleNamespace(
        profile=profile,
        engine=engine,
        camera=SimpleNamespace(last_image=b"frame", last_analysis={"camera": "pet_guardian"}),
    )
    coordinator = SimpleNamespace(
        data={profile.pet_id: snapshot},
        _pets={profile.pet_id: managed},
        pets={profile.pet_id: managed},
        pet_ids=(profile.pet_id,),
        hub_identifier="hub_entry_1",
        coordinator_now=now,
        get_profile=lambda pet_id: managed.profile,
        get_snapshot=lambda pet_id: snapshot,
        get_camera_image=lambda pet_id: managed.camera.last_image,
        get_camera_analysis=lambda pet_id: managed.camera.last_analysis,
        timeline_events=lambda pet_id, start, end: [],
        async_request_refresh=_async_noop,
        async_feed_now=_async_noop,
        async_refill_food=_async_noop,
        async_refill_water=_async_noop,
        async_start_walk=_async_noop,
        async_finish_walk=_async_noop,
        async_sync_pet_calendar=_async_noop,
        async_generate_vet_report=_async_noop,
        async_generate_operations_report=_async_noop,
        async_set_food_portion=_async_noop,
        async_set_daily_calories=_async_noop,
        async_set_weight_goal_min=_async_noop,
        async_set_weight_goal_max=_async_noop,
        async_set_diet_mode=_async_noop,
        async_set_manual_mode=_async_noop,
    )
    return coordinator


async def _async_noop(*args, **kwargs):
    return None


def _collect_entities(setup_entry, coordinator):
    entry = ConfigEntry()
    entry.runtime_data = coordinator
    added = []

    def _add_entities(entities):
        added.extend(list(entities))

    asyncio.run(setup_entry(None, entry, _add_entities))
    return added


def test_entity_platforms_create_medical_mobility_and_reporting_entities() -> None:
    coordinator = _build_runtime()

    sensor_entities = _collect_entities(setup_sensors, coordinator)
    button_entities = _collect_entities(setup_buttons, coordinator)
    number_entities = _collect_entities(setup_numbers, coordinator)
    select_entities = _collect_entities(setup_selects, coordinator)
    binary_sensor_entities = _collect_entities(setup_binary_sensors, coordinator)
    camera_entities = _collect_entities(setup_cameras, coordinator)
    calendar_entities = _collect_entities(setup_calendars, coordinator)
    tracker_entities = _collect_entities(setup_device_trackers, coordinator)

    sensor_ids = {entity._attr_unique_id for entity in sensor_entities}
    button_ids = {entity._attr_unique_id for entity in button_entities}
    number_ids = {entity._attr_unique_id for entity in number_entities}
    select_ids = {entity._attr_unique_id for entity in select_entities}
    binary_sensor_ids = {entity._attr_unique_id for entity in binary_sensor_entities}
    camera_ids = {entity._attr_unique_id for entity in camera_entities}
    calendar_ids = {entity._attr_unique_id for entity in calendar_entities}
    tracker_ids = {entity._attr_unique_id for entity in tracker_entities}

    assert "don_abrikos_a1b2c3-active_medications" in sensor_ids
    assert "don_abrikos_a1b2c3-recovery_status" in sensor_ids
    assert "don_abrikos_a1b2c3-generated_reports" in sensor_ids
    assert "don_abrikos_a1b2c3-walk_distance_today" in sensor_ids
    assert "don_abrikos_a1b2c3-current_zone" in sensor_ids
    assert "don_abrikos_a1b2c3-room_heatmap" in sensor_ids

    assert "don_abrikos_a1b2c3-sync_calendar" in button_ids
    assert "don_abrikos_a1b2c3-generate_vet_report" in button_ids
    assert "don_abrikos_a1b2c3-generate_operations_report" in button_ids

    assert "don_abrikos_a1b2c3-weight_goal_min" in number_ids
    assert "don_abrikos_a1b2c3-weight_goal_max" in number_ids

    assert "don_abrikos_a1b2c3-diet_mode" in select_ids
    assert "don_abrikos_a1b2c3-operation_mode" in select_ids

    assert "don_abrikos_a1b2c3-home_alone" in binary_sensor_ids
    assert "don_abrikos_a1b2c3-geofence_breached" in binary_sensor_ids

    assert camera_ids == {"don_abrikos_a1b2c3-monitor"}
    assert calendar_ids == {"don_abrikos_a1b2c3-timeline"}
    assert tracker_ids == {"don_abrikos_a1b2c3-location"}

    generated_reports_entity = next(
        entity for entity in sensor_entities if entity._attr_unique_id == "don_abrikos_a1b2c3-generated_reports"
    )
    assert generated_reports_entity.extra_state_attributes["jobs_by_status"] == {"completed": 1}

    camera_entity = camera_entities[0]
    assert asyncio.run(camera_entity.async_camera_image()) == b"frame"
    assert camera_entity.extra_state_attributes["source_camera"] == "camera.pet_guardian"

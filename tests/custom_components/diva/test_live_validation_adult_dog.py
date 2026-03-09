import asyncio
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

import custom_components.diva.coordinator as coordinator_module
from custom_components.diva.coordinator import DivaCoordinator, ManagedPet
from custom_components.diva.pet import CameraAnalysis, PetEngine, PetProfile, parse_room_presence_sources, parse_safe_zones


UTC = timezone.utc


class FakeStates:
    def __init__(self) -> None:
        self._states: dict[str, SimpleNamespace] = {}

    def set(self, entity_id: str, state: str, **attributes) -> None:
        self._states[entity_id] = SimpleNamespace(state=state, attributes=attributes)

    def get(self, entity_id: str):
        return self._states.get(entity_id)


def _profile() -> PetProfile:
    return PetProfile(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="English Cocker Spaniel",
        birthdate=date(2020, 1, 1),
        weight_kg=12.4,
        diet_mode="adult",
        gps_tracker_entity_id="device_tracker.don_gps",
        ble_tracker_entity_id="sensor.don_ble_room",
        camera_entity_id="camera.pet_guardian",
        camera_room_name="Kitchen",
        weather_entity_id="sensor.outdoor_temperature",
        household_presence_entity_ids=("person.alex",),
        safe_zones=parse_safe_zones(
            [
                {
                    "zone_name": "Home",
                    "latitude": 40.4168,
                    "longitude": -3.7038,
                    "radius_m": 120,
                }
            ]
        ),
        room_presence_sources=parse_room_presence_sources(
            [
                {
                    "room_name": "Living room",
                    "entity_id": "binary_sensor.living_room_presence",
                    "match_state": "on",
                    "priority": 4,
                }
            ]
        ),
    )


def _build_coordinator(states: FakeStates) -> tuple[DivaCoordinator, ManagedPet]:
    profile = _profile()
    engine = PetEngine(profile)
    coordinator = object.__new__(DivaCoordinator)
    coordinator.hass = SimpleNamespace(states=states)
    managed = ManagedPet(profile=profile, engine=engine)
    coordinator._pets = {profile.pet_id: managed}
    coordinator.data = {}

    async def _noop_save() -> None:
        return None

    async def _noop_fire(items) -> None:
        return None

    async def _noop_poll(*args, **kwargs):
        return []

    coordinator._async_save_runtime_state = _noop_save
    coordinator._async_fire_notices = _noop_fire
    coordinator._async_poll_external_calendars = _noop_poll
    return coordinator, managed


def test_adult_dog_runtime_validation_flow_covers_gps_ble_and_camera(monkeypatch) -> None:
    states = FakeStates()
    coordinator, managed = _build_coordinator(states)
    profile = managed.profile
    engine = managed.engine

    states.set(
        profile.gps_tracker_entity_id,
        "home",
        latitude=40.4168,
        longitude=-3.7038,
        gps_accuracy=8,
    )
    states.set(profile.ble_tracker_entity_id, "kitchen")
    states.set(profile.weather_entity_id, "22.5")
    states.set("person.alex", "home")
    states.set("binary_sensor.living_room_presence", "off")

    engine.feed_now(datetime(2026, 3, 9, 8, 58, tzinfo=UTC), grams=90, meal_type="dry", food_name="Main kibble")

    async def _run_tick(now: datetime, analysis: CameraAnalysis | None):
        monkeypatch.setattr(coordinator_module.dt_util, "now", lambda: now)

        async def _camera(_managed):
            return analysis

        coordinator._async_run_camera_analysis = _camera
        snapshots = await DivaCoordinator._async_update_data(coordinator)
        coordinator.data = snapshots
        return snapshots[profile.pet_id]

    first_snapshot = asyncio.run(
        _run_tick(
            datetime(2026, 3, 9, 9, 0, tzinfo=UTC),
            CameraAnalysis(
                frame_motion_score=0.12,
                food_motion_score=0.2,
                food_interaction=True,
            ),
        )
    )

    assert first_snapshot.current_zone == "Home"
    assert first_snapshot.current_room == "Kitchen"
    assert set(first_snapshot.room_presence_sources) == {"camera.pet_guardian", "sensor.don_ble_room"}
    assert first_snapshot.food_today_grams == 90.0
    assert first_snapshot.camera_enabled is True
    assert first_snapshot.outside_temperature_c == 22.5
    assert first_snapshot.home_alone is False

    states.set(profile.ble_tracker_entity_id, "living_room")
    states.set("person.alex", "not_home")
    states.set("binary_sensor.living_room_presence", "on")

    second_snapshot = asyncio.run(
        _run_tick(
            datetime(2026, 3, 9, 9, 5, tzinfo=UTC),
            None,
        )
    )

    assert second_snapshot.current_zone == "Home"
    assert second_snapshot.current_room == "Living room"
    assert second_snapshot.room_presence_sources == (
        "binary_sensor.living_room_presence",
        "sensor.don_ble_room",
    )
    assert second_snapshot.home_alone is True
    assert second_snapshot.separation_score > 0

    states.set(
        profile.gps_tracker_entity_id,
        "not_home",
        latitude=40.4300,
        longitude=-3.7000,
        gps_accuracy=12,
    )
    states.set(profile.ble_tracker_entity_id, "unknown")
    states.set("binary_sensor.living_room_presence", "off")

    third_snapshot = asyncio.run(
        _run_tick(
            datetime(2026, 3, 9, 10, 0, tzinfo=UTC),
            None,
        )
    )

    assert third_snapshot.current_zone == "outside_safe_zone"
    assert third_snapshot.geofence_breached is True
    assert third_snapshot.distance_from_safe_zone_m is not None
    assert third_snapshot.distance_from_safe_zone_m > 1000
    assert third_snapshot.current_room is None
    assert managed.engine.state.room_history[-1]["room_name"] is None

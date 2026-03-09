from datetime import date, datetime, timezone

from custom_components.diva.pet import (
    PetContext,
    PetEngine,
    PetProfile,
    parse_room_presence_sources,
    parse_safe_zones,
)


UTC = timezone.utc


def _mobility_profile() -> PetProfile:
    return PetProfile(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="English Cocker Spaniel",
        birthdate=date(2020, 1, 1),
        weight_kg=12.4,
        diet_mode="adult",
        camera_room_name="Kitchen",
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
                    "entity_id": "binary_sensor.don_abrikos_living_room",
                    "match_state": "on",
                    "priority": 4,
                }
            ]
        ),
    )


def test_room_and_geofence_tracking_emit_notices() -> None:
    engine = PetEngine(_mobility_profile())
    inside = datetime(2026, 3, 9, 9, 0, tzinfo=UTC)

    first_snapshot, first_notices = engine.refresh(
        inside,
        PetContext(
            gps_tracker_state="home",
            gps_latitude=40.4168,
            gps_longitude=-3.7038,
            current_zone="Home",
            current_room="Living room",
            room_presence_sources=("binary_sensor.don_abrikos_living_room",),
        ),
    )

    assert first_snapshot.current_zone == "Home"
    assert first_snapshot.current_room == "Living room"
    assert {notice.name for notice in first_notices} >= {"zone_changed", "room_changed"}

    outside = inside.replace(hour=10)
    second_snapshot, second_notices = engine.refresh(
        outside,
        PetContext(
            gps_tracker_state="not_home",
            gps_latitude=40.4300,
            gps_longitude=-3.7000,
            current_zone="outside_safe_zone",
            geofence_breached=True,
            distance_from_safe_zone_m=1369.6,
            current_room="Kitchen",
            room_presence_sources=("camera.pet_guardian",),
            home_alone=True,
        ),
    )

    assert second_snapshot.geofence_breached is True
    assert second_snapshot.current_room == "Kitchen"
    assert second_snapshot.current_zone == "outside_safe_zone"
    assert second_snapshot.separation_score > 0
    assert {notice.name for notice in second_notices} >= {"left_safe_zone", "geofence_breach", "room_changed"}


def test_walk_route_summary_and_distance_are_recorded() -> None:
    engine = PetEngine(_mobility_profile())
    started_at = datetime(2026, 3, 9, 7, 0, tzinfo=UTC)

    engine.start_walk(started_at)
    engine.refresh(
        started_at.replace(minute=5),
        PetContext(gps_latitude=40.4168, gps_longitude=-3.7038, current_zone="Home"),
    )
    engine.refresh(
        started_at.replace(minute=20),
        PetContext(gps_latitude=40.4200, gps_longitude=-3.7000, current_zone="Home"),
    )
    engine.refresh(
        started_at.replace(minute=35),
        PetContext(gps_latitude=40.4230, gps_longitude=-3.6960, current_zone="Home"),
    )

    notices = engine.finish_walk(started_at.replace(minute=40))

    assert notices[0].name == "walk_finished"
    assert notices[0].data["distance_km"] > 0.5
    assert engine.state.last_walk_summary is not None
    assert engine.state.last_walk_summary["route_summary"] is not None
    assert engine.state.last_walk_summary["point_count"] >= 3
    assert len(engine.state.last_walk_route) >= 3
    assert engine.state.current_walk_route == []


def test_room_preferences_are_derived_from_recent_history() -> None:
    engine = PetEngine(_mobility_profile())
    engine.state.daily_history = [
        {
            "date": "2026-03-07",
            "room_dwell_today_minutes": {"Living room": 140.0, "Kitchen": 20.0},
        },
        {
            "date": "2026-03-08",
            "room_dwell_today_minutes": {"Living room": 90.0, "Kitchen": 10.0},
        },
    ]
    engine.state.room_dwell_today_minutes = {"Living room": 60.0, "Kitchen": 5.0}

    snapshot, _ = engine.refresh(datetime(2026, 3, 9, 18, 0, tzinfo=UTC), PetContext(current_room="Living room"))

    assert snapshot.preferred_rooms[0] == "Living room"
    assert "Kitchen" in snapshot.avoided_rooms

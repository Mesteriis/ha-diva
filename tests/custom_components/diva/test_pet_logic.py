from datetime import date, datetime, timezone

from custom_components.diva.pet import (
    CameraAnalysis,
    PetContext,
    PetEngine,
    PetProfile,
    normalize_avatar_reference,
    parse_food_catalog,
    parse_food_transition_plan,
    parse_feeding_schedule,
    parse_schedule_exceptions,
    parse_walk_schedule,
)


def _profile() -> PetProfile:
    return PetProfile(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="Poodle",
        birthdate=date(2020, 1, 1),
        weight_kg=8.2,
        diet_mode="adult",
    )


def test_feed_and_camera_eating_flow() -> None:
    engine = PetEngine(_profile())
    now = datetime(2026, 3, 8, 8, 0, tzinfo=timezone.utc)

    notices = engine.feed_now(now)
    assert notices[0].name == "food_served"
    assert engine.state.pending_meal_grams > 0

    notices = engine.apply_camera_analysis(
        now.replace(minute=5),
        CameraAnalysis(frame_motion_score=0.1, food_motion_score=0.2, food_interaction=True),
    )
    assert {notice.name for notice in notices} >= {"pet_eating", "food_eaten"}
    assert engine.state.food_today_grams > 0
    assert engine.state.pending_meal_grams == 0
    assert engine.state.calories_consumed_today > 0


def test_food_catalog_and_transition_are_applied() -> None:
    profile = PetProfile(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="Poodle",
        birthdate=date(2020, 1, 1),
        weight_kg=8.2,
        diet_mode="adult",
        food_catalog=parse_food_catalog(
            [
                {"food_name": "Old kibble", "food_brand": "Brand A", "food_kind": "main_food", "meal_type": "dry", "kcal_per_gram": 3.8},
                {"food_name": "New kibble", "food_brand": "Brand B", "food_kind": "main_food", "meal_type": "dry", "kcal_per_gram": 4.1},
                {"food_name": "Training treat", "food_brand": "Brand T", "food_kind": "treats", "meal_type": "treat", "kcal_per_gram": 4.5},
            ]
        ),
        food_transition_plan=parse_food_transition_plan(
            [
                {
                    "transition_date": "2026-03-08",
                    "from_food_name": "Old kibble",
                    "to_food_name": "New kibble",
                    "from_percent": 50,
                    "to_percent": 50,
                }
            ]
        ),
    )
    engine = PetEngine(profile)
    now = datetime(2026, 3, 8, 8, 0, tzinfo=timezone.utc)
    engine.state.current_day = now.date().isoformat()

    feed_notices = engine.feed_now(now, grams=40, meal_type="treat", food_name="Training treat")
    assert feed_notices[0].data["food_name"] == "Training treat"
    engine.apply_camera_analysis(
        now.replace(minute=5),
        CameraAnalysis(frame_motion_score=0.1, food_motion_score=0.2, food_interaction=True),
    )
    snapshot, _ = engine.refresh(now.replace(hour=18), PetContext())

    assert snapshot.treat_calories_today > 0
    assert snapshot.active_food_transition == "Old kibble 50% -> New kibble 50%"
    assert engine.state.food_today_grams_by_food["Training treat"] == 40.0
    assert snapshot.feeding_quality_score < 100.0


def test_schedule_parsers_accept_multiline_text() -> None:
    feeding = parse_feeding_schedule("09:30|wet|Breakfast|80|daily", pet_id="don")
    walks = parse_walk_schedule("09:00|30|Morning walk|weekdays", pet_id="don")

    assert feeding[0].meal_type == "wet"
    assert feeding[0].portion_grams == 80.0
    assert walks[0].duration_minutes == 30
    assert walks[0].weekdays == (0, 1, 2, 3, 4)


def test_structured_routine_objects_and_exceptions_drive_timeline() -> None:
    profile = PetProfile(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="Poodle",
        birthdate=date(2020, 1, 1),
        weight_kg=8.2,
        diet_mode="adult",
        feeding_routines=parse_feeding_schedule(
            [
                {"time": "09:30", "days": ["mon"], "label": "Breakfast", "duration_minutes": 15, "meal_type": "wet", "portion_grams": 80},
            ],
            pet_id="don_abrikos_a1b2c3",
        ),
        walk_routines=parse_walk_schedule(
            [
                {"time": "13:00", "days": ["mon"], "label": "Midday walk", "duration_minutes": 30, "location": "Park"},
                {"time": "17:00", "days": ["mon"], "label": "Afternoon walk", "duration_minutes": 30, "location": "Park"},
            ],
            pet_id="don_abrikos_a1b2c3",
        ),
    )
    engine = PetEngine(profile)
    engine.add_runtime_exception(
        parse_schedule_exceptions(
            [{"date": "2026-03-09", "action": "move", "category": "walk", "new_time": "20:30", "label": "Late walk"}],
            pet_id=profile.pet_id,
        )[0]
    )

    start = datetime(2026, 3, 9, 0, 0, tzinfo=timezone.utc)
    events = engine.timeline_events(start, start.replace(hour=23, minute=59), PetContext(outside_temperature_c=31.0))

    summaries = [event.summary for event in events]
    assert "Breakfast" in summaries
    assert "Late walk" in summaries
    assert all("Midday walk" not in summary for summary in summaries)
    assert all("Afternoon walk" not in summary for summary in summaries)


def test_heat_mode_marks_midday_walks() -> None:
    profile = PetProfile(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="Poodle",
        birthdate=date(2020, 1, 1),
        weight_kg=8.2,
        diet_mode="adult",
        walk_routines=parse_walk_schedule(
            [{"time": "14:00", "days": ["mon"], "label": "Midday walk", "duration_minutes": 30, "location": "Park"}],
            pet_id="don_abrikos_a1b2c3",
        ),
    )

    engine = PetEngine(profile)
    start = datetime(2026, 3, 9, 0, 0, tzinfo=timezone.utc)
    events = engine.timeline_events(start, start.replace(hour=23, minute=59), PetContext(outside_temperature_c=31.0))
    walk_event = next(event for event in events if event.category == "walk")

    assert walk_event.summary.endswith("[heat-risk]")
    assert "heat" in walk_event.metadata["active_modes"]


def test_avatar_reference_normalization() -> None:
    assert normalize_avatar_reference("www/diva/avatars/don.png") == "/local/diva/avatars/don.png"
    assert normalize_avatar_reference("/config/www/diva/avatars/don.png") == "/local/diva/avatars/don.png"
    assert normalize_avatar_reference("https://example.com/don.png") == "https://example.com/don.png"
    assert normalize_avatar_reference("") is None


def test_report_behavior_creates_anomaly_notice() -> None:
    engine = PetEngine(_profile())
    notices = engine.report_behavior(
        datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc),
        "limping",
        severity="warning",
    )

    assert {notice.category for notice in notices} == {"event", "anomaly"}
    assert notices[1].name == "limping_detected"

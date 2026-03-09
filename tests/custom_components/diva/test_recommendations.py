from datetime import date, datetime, timezone

from custom_components.diva.pet import PetContext, PetRuntimeState, PetSnapshot
from custom_components.diva.recommendations import evaluate_pet


def test_low_activity_water_and_home_alone_generate_notices() -> None:
    runtime = PetRuntimeState(
        weight_kg=8.2,
        diet_mode="adult",
        food_portion_grams=120.0,
        daily_calories=420.0,
        food_today_grams=20.0,
        water_today_ml=30.0,
        daily_history=[
            {
                "date": "2026-03-01",
                "food_today_grams": 110.0,
                "water_today_ml": 250.0,
                "activity_points_today": 18.0,
                "sleep_minutes_today": 480.0,
            }
        ]
        * 3,
    )
    snapshot = PetSnapshot(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="Poodle",
        birthdate=date(2020, 1, 1).isoformat(),
        weight_kg=8.2,
        diet_mode="adult",
        food_today_grams=20.0,
        water_today_ml=30.0,
        last_feeding_at=None,
        next_feeding_at=None,
        next_walk_at=None,
        next_care_at=None,
        next_vet_visit_at=None,
        last_seen_eating_at=None,
        activity_level=5.0,
        sleep_duration_hours=1.0,
        health_score=92.0,
        stress_score=0.0,
        recommended_food_portion_grams=120.0,
        daily_calories=420.0,
        food_portion_grams=120.0,
        hungry=True,
        needs_walk=True,
        food_bowl_empty=False,
        water_bowl_empty=False,
        sleeping=False,
        anomaly_detected=False,
    )

    updated_snapshot, notices, active, sent = evaluate_pet(
        snapshot,
        runtime,
        datetime(2026, 3, 8, 18, 0, tzinfo=timezone.utc),
        PetContext(home_alone=True, outside_temperature_c=29.0),
    )

    assert updated_snapshot.anomaly_detected is True
    assert updated_snapshot.stress_score > 0
    assert "low_water_intake" in active
    assert any(notice.category == "recommendation" for notice in notices)
    assert "activity_low" in sent
    assert "home_alone" in sent


def test_illness_mode_relaxes_low_activity_recommendation() -> None:
    runtime = PetRuntimeState(
        weight_kg=8.2,
        diet_mode="adult",
        food_portion_grams=120.0,
        daily_calories=420.0,
        manual_mode="illness",
        food_today_grams=90.0,
        water_today_ml=180.0,
    )
    snapshot = PetSnapshot(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="Poodle",
        birthdate=date(2020, 1, 1).isoformat(),
        weight_kg=8.2,
        diet_mode="adult",
        food_today_grams=90.0,
        water_today_ml=180.0,
        last_feeding_at=None,
        next_feeding_at=None,
        next_walk_at=None,
        next_care_at=None,
        next_vet_visit_at=None,
        last_seen_eating_at=None,
        activity_level=18.0,
        sleep_duration_hours=4.0,
        health_score=92.0,
        stress_score=0.0,
        recommended_food_portion_grams=120.0,
        daily_calories=420.0,
        food_portion_grams=120.0,
        hungry=False,
        needs_walk=False,
        food_bowl_empty=False,
        water_bowl_empty=False,
        sleeping=False,
        anomaly_detected=False,
        operation_mode="illness",
        active_modes=("illness",),
    )

    _updated_snapshot, notices, _active, sent = evaluate_pet(
        snapshot,
        runtime,
        datetime(2026, 3, 8, 18, 0, tzinfo=timezone.utc),
        PetContext(home_alone=False, outside_temperature_c=20.0),
    )

    assert "activity_low" not in sent
    assert all(notice.name != "activity_low" for notice in notices)


def test_high_treat_share_generates_nutrition_recommendation() -> None:
    runtime = PetRuntimeState(
        weight_kg=8.2,
        diet_mode="adult",
        food_portion_grams=120.0,
        daily_calories=420.0,
        food_today_grams=60.0,
        calories_consumed_today=180.0,
        treat_calories_today=120.0,
        food_eaten_today_by_type={"treat": 40.0, "dry": 20.0},
        food_served_today_grams=60.0,
        feeding_quality_score=60.0,
    )
    snapshot = PetSnapshot(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="Poodle",
        birthdate=date(2020, 1, 1).isoformat(),
        weight_kg=8.2,
        diet_mode="adult",
        food_today_grams=60.0,
        water_today_ml=220.0,
        last_feeding_at=None,
        next_feeding_at=None,
        next_walk_at=None,
        next_care_at=None,
        next_vet_visit_at=None,
        last_seen_eating_at=None,
        activity_level=35.0,
        sleep_duration_hours=5.0,
        health_score=92.0,
        stress_score=0.0,
        recommended_food_portion_grams=120.0,
        daily_calories=420.0,
        food_portion_grams=120.0,
        hungry=False,
        needs_walk=False,
        food_bowl_empty=False,
        water_bowl_empty=False,
        sleeping=False,
        anomaly_detected=False,
        feeding_quality_score=60.0,
        calories_consumed_today=180.0,
        treat_calories_today=120.0,
    )

    _updated_snapshot, notices, _active, sent = evaluate_pet(
        snapshot,
        runtime,
        datetime(2026, 3, 8, 16, 0, tzinfo=timezone.utc),
        PetContext(home_alone=False, outside_temperature_c=20.0),
    )

    assert "treats_high" in sent
    assert "feeding_quality_low" in sent
    assert any(notice.name == "treats_high" for notice in notices)

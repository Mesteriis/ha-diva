from datetime import date, datetime, timezone

from custom_components.diva.pet import PetContext, PetEngine, PetProfile
from custom_components.diva.recommendations import evaluate_pet


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
    )


def test_observe_behavior_records_provenance_and_confidence() -> None:
    engine = PetEngine(_profile())
    notices = engine.observe_behavior(
        datetime(2026, 3, 9, 10, 0, tzinfo=UTC),
        "cough",
        severity="warning",
        source="vision_pipeline",
        confidence=0.91,
        duration_seconds=12,
        model_name="pet-ai-v1",
        message="Dry cough detected",
    )

    observation = engine.state.behavior_observations[-1]
    assert observation["type"] == "cough_detected"
    assert observation["source"] == "vision_pipeline"
    assert observation["confidence"] == 0.91
    assert observation["model_name"] == "pet-ai-v1"
    assert {notice.name for notice in notices} >= {"behavior_observed", "cough_detected"}


def test_sleep_quality_long_inactivity_and_baseline_drift_are_explainable() -> None:
    engine = PetEngine(_profile())
    engine.state.daily_history = [
        {
            "date": "2026-03-01",
            "food_today_grams": 130.0,
            "water_today_ml": 420.0,
            "activity_points_today": 18.0,
            "sleep_minutes_today": 500.0,
        }
    ] * 5
    engine.state.food_today_grams = 35.0
    engine.state.water_today_ml = 110.0
    engine.state.activity_points_today = 2.0
    engine.state.sleep_minutes_today = 140.0
    engine.state.sleep_interruptions_today = 5
    engine.state.last_activity_at = "2026-03-09T10:00:00+00:00"
    engine.observe_behavior(
        datetime(2026, 3, 9, 12, 0, tzinfo=UTC),
        "restlessness",
        severity="warning",
        source="camera_model",
        confidence=0.88,
    )

    snapshot, _ = engine.refresh(datetime(2026, 3, 9, 16, 30, tzinfo=UTC), PetContext(home_alone=True))
    updated_snapshot, notices, active, sent = evaluate_pet(
        snapshot,
        engine.state,
        datetime(2026, 3, 9, 16, 30, tzinfo=UTC),
        PetContext(home_alone=True),
    )

    assert updated_snapshot.sleep_quality_score < 65
    assert updated_snapshot.inactivity_duration_minutes >= 390
    assert updated_snapshot.baseline_drift_score >= 40
    assert updated_snapshot.behavior_profile is not None
    assert updated_snapshot.behavior_summary is not None
    assert updated_snapshot.stress_factors
    assert "sleep_quality_drop" in sent
    assert "baseline_drift" in sent
    assert "subtle_shift" in sent
    assert "long_inactivity" in active
    assert "baseline_drift" in active
    assert any(notice.name == "stress_high" for notice in notices)

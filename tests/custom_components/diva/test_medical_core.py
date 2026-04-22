from datetime import date, datetime, timezone

from custom_components.diva.pet import (
    PetContext,
    PetEngine,
    PetProfile,
    parse_allergies,
    parse_chronic_conditions,
    parse_contraindications,
    parse_diagnoses,
    parse_medical_history,
    parse_medication_courses,
)
from custom_components.diva.recommendations import evaluate_pet


UTC = timezone.utc


def _medical_profile() -> PetProfile:
    return PetProfile(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="English Cocker Spaniel",
        birthdate=date(2020, 1, 1),
        weight_kg=12.4,
        diet_mode="adult",
        body_condition_score=7.0,
        medical_country="ES",
        medical_region="es_general",
        regional_policy="es_general",
        vaccine_profile="spain_dog_default",
        vet_override=True,
        medication_courses=parse_medication_courses(
            [
                {
                    "medication_name": "Apoquel",
                    "dose": "1 tablet",
                    "medication_times": "08:00,20:00",
                    "start_date": "2026-03-01",
                    "end_date": "2026-03-31",
                    "medication_route": "oral",
                }
            ]
        ),
        chronic_conditions=parse_chronic_conditions(
            [
                {
                    "condition_name": "Atopic dermatitis",
                    "condition_status": "active",
                    "monitor_interval_days": 30,
                }
            ]
        ),
        diagnoses=parse_diagnoses(
            [
                {
                    "diagnosis_name": "Atopic dermatitis",
                    "diagnosis_status": "active",
                    "diagnosed_on": "2024-04-15",
                    "notes": "Dermatology confirmed",
                }
            ]
        ),
        allergies=parse_allergies(
            [
                {
                    "allergen": "Chicken protein",
                    "reaction": "itching flare",
                    "notes": "Use hydrolyzed diet if symptoms worsen",
                }
            ]
        ),
        contraindications=parse_contraindications(
            [
                {
                    "contraindication": "High-impact agility",
                    "reason": "Joint inflammation risk",
                    "notes": "Prefer controlled walks",
                }
            ]
        ),
        medical_history=parse_medical_history(
            [
                {
                    "history_date": "2025-11-20",
                    "history_title": "GI episode",
                    "history_category": "illness",
                    "notes": "Resolved after bland diet",
                }
            ]
        ),
    )


def test_medication_timeline_and_overdue_detection() -> None:
    engine = PetEngine(_medical_profile())
    now = datetime(2026, 3, 9, 11, 0, tzinfo=UTC)

    snapshot, _ = engine.refresh(now, PetContext())
    day_events = engine.timeline_events(
        datetime(2026, 3, 9, 0, 0, tzinfo=UTC),
        datetime(2026, 3, 9, 23, 59, tzinfo=UTC),
        PetContext(),
    )

    assert snapshot.active_medications == ("Apoquel",)
    assert snapshot.overdue_medications == ("Apoquel",)
    assert snapshot.next_medication_at == "2026-03-09T20:00:00+00:00"
    assert any(event.category == "medication" and event.summary == "Apoquel dose" for event in day_events)


def test_spain_cocker_vaccine_plan_and_completion() -> None:
    profile = _medical_profile()
    engine = PetEngine(profile)
    today = date(2026, 3, 9)

    plan = profile.vaccine_plan(today)
    rabies = next(item for item in plan if item.vaccine_name == "Rabies booster review")

    assert any(item.vaccine_name == "Leptospirosis annual booster" for item in plan)
    assert any(item.vaccine_name == "Leishmaniosis prevention review" for item in plan)
    assert "cocker" in (rabies.notes or "").lower()

    engine.complete_vaccine_dose(datetime(2026, 3, 9, 10, 0, tzinfo=UTC), dose_id=rabies.dose_id)

    assert engine.state.completed_vaccine_doses[rabies.dose_id] == "2026-03-09"
    assert rabies.next_due_date(date(2026, 3, 9)) == date(2027, 3, 9)


def test_spain_puppy_leish_review_due_date_is_stable() -> None:
    profile = PetProfile.from_dict(
        {
            **_medical_profile().as_dict(),
            "birthdate": "2025-09-01",
        }
    )

    plan = profile.vaccine_plan(date(2026, 3, 18))
    leish = next(item for item in plan if item.vaccine_name == "Leishmaniosis prevention review")

    assert leish.due_date == date(2026, 2, 28)


def test_vaccine_profile_regional_policy_and_vet_override() -> None:
    base = _medical_profile()
    no_override = PetProfile.from_dict(
        {
            **base.as_dict(),
            "regional_policy": "madrid",
            "vaccine_profile": "dog_default",
            "vet_override": False,
            "vaccine_overrides": [
                {
                    "vaccine_dose_id": f"{base.pet_id}:rabies_review",
                    "vaccine_name": "Rabies booster review",
                    "due_date": "2026-04-10",
                    "category": "regional",
                    "notes": "Manual override should be ignored",
                }
            ],
        }
    )

    plan = no_override.vaccine_plan(date(2026, 3, 9))
    rabies = next(item for item in plan if item.vaccine_name == "Rabies booster review")

    assert all("Leishmaniosis" not in item.vaccine_name for item in plan)
    assert rabies.due_date == date(2026, 3, 9)
    assert "Madrid overlay" in (rabies.notes or "")

    with_override = PetProfile.from_dict(
        {
            **base.as_dict(),
            "regional_policy": "custom",
            "vaccine_profile": "spain_dog_default",
            "vet_override": True,
            "vaccine_overrides": [
                {
                    "vaccine_dose_id": f"{base.pet_id}:rabies_review",
                    "vaccine_name": "Rabies booster review",
                    "due_date": "2026-04-10",
                    "category": "regional",
                    "notes": "Manual override should win",
                }
            ],
        }
    )

    overridden = next(item for item in with_override.vaccine_plan(date(2026, 3, 9)) if item.vaccine_name == "Rabies booster review")
    assert overridden.due_date == date(2026, 4, 10)


def test_vaccine_reschedule_cancel_and_weight_trend() -> None:
    engine = PetEngine(_medical_profile())
    now = datetime(2026, 3, 9, 10, 0, tzinfo=UTC)
    rabies = next(item for item in engine.profile.vaccine_plan(now.date()) if "Rabies" in item.vaccine_name)

    engine.record_weight(now.replace(day=1), 12.4, source="manual")
    engine.record_weight(now, 11.9, source="manual")
    reschedule = engine.reschedule_vaccine(
        now,
        dose_id=rabies.dose_id,
        due_date=date(2026, 3, 20),
        note="Deferred by vet",
    )
    snapshot, _ = engine.refresh(now, PetContext())
    effective_rabies = next(item for item in engine._effective_vaccine_plan(now.date()) if item.dose_id == rabies.dose_id)

    assert reschedule[0].name == "vaccine_rescheduled"
    assert effective_rabies.due_date == date(2026, 3, 20)
    assert snapshot.vaccine_status in {"due_soon", "overdue"}
    assert snapshot.weight_trend_kg == -0.5

    canceled = engine.cancel_vaccine(now, dose_id=rabies.dose_id, reason="Given elsewhere")
    snapshot_after_cancel, _ = engine.refresh(now, PetContext())

    assert canceled[0].name == "vaccine_canceled"
    assert all("Rabies" not in item.vaccine_name for item in engine._effective_vaccine_plan(now.date()))
    assert snapshot_after_cancel.vaccine_status in {"scheduled", "due_soon", "clear"}


def test_symptom_recovery_and_vet_report() -> None:
    engine = PetEngine(_medical_profile())
    logged_at = datetime(2026, 3, 9, 9, 0, tzinfo=UTC)

    symptom_notices = engine.log_symptom(
        logged_at,
        "cough",
        severity_score=4.5,
        note="Dry cough",
        duration_hours=6.0,
    )
    recovery_notices = engine.start_recovery_plan(logged_at, "Post-op rest", expected_days=10, note="Short walks only")
    snapshot, _ = engine.refresh(logged_at.replace(hour=12), PetContext())
    report = engine.build_vet_report(logged_at.replace(hour=12), snapshot, history_days=7)

    assert any(notice.name == "symptom_logged" for notice in symptom_notices)
    assert any(notice.name == "recovery_plan_started" for notice in recovery_notices)
    assert snapshot.recovery_status == "active"
    assert snapshot.symptom_severity_score > 0
    assert engine.state.symptom_log[-1]["duration_hours"] == 6.0
    assert "DIVA Veterinary Summary" in report["content"]
    assert "Diagnoses" in report["content"]
    assert "Allergies" in report["content"]
    assert "Contraindications" in report["content"]
    assert "Medical history" in report["content"]
    assert "duration 6.0 h" in report["content"]
    assert "Recent symptoms" in report["content"]
    assert "Recovery status: active" in report["content"]


def test_medical_profile_roundtrip_includes_structured_fields() -> None:
    profile = _medical_profile()

    restored = PetProfile.from_dict(profile.as_dict())

    assert restored.diagnoses[0].name == "Atopic dermatitis"
    assert restored.allergies[0].allergen == "Chicken protein"
    assert restored.contraindications[0].item == "High-impact agility"
    assert restored.medical_history[0].title == "GI episode"


def test_medical_recommendations_and_anomalies() -> None:
    engine = PetEngine(_medical_profile())
    now = datetime(2026, 3, 9, 18, 0, tzinfo=UTC)

    engine.log_symptom(now.replace(hour=9), "vomiting", severity_score=4.2, source="manual")
    engine.start_recovery_plan(now.replace(hour=9), "GI recovery", expected_days=1)
    engine.state.active_recovery_plan["expected_end"] = "2026-03-08T09:00:00+00:00"
    snapshot, _ = engine.refresh(now, PetContext(home_alone=True, outside_temperature_c=29.0))

    updated_snapshot, notices, active, sent = evaluate_pet(
        snapshot,
        engine.state,
        now,
        PetContext(home_alone=True, outside_temperature_c=29.0),
    )

    assert updated_snapshot.anomaly_detected is True
    assert "medication_overdue" in active
    assert "vaccine_overdue" in active
    assert "symptom_escalation" in active
    assert "recovery_delay" in active
    assert "medication_due" in sent
    assert "vaccine_due" in sent
    assert any(notice.name == "medication_due" for notice in notices)

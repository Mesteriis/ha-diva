from datetime import date, datetime, timezone

from custom_components.diva.const import APPROVAL_ACTION_CARE
from custom_components.diva.pet import (
    PetContext,
    PetEngine,
    PetProfile,
    parse_care_roles,
    parse_care_shifts,
    parse_checklist_items,
)


UTC = timezone.utc


def _profile() -> PetProfile:
    pet_id = "don_abrikos_a1b2c3"
    return PetProfile(
        pet_id=pet_id,
        name="Don Abrikos",
        species="dog",
        breed="English Cocker Spaniel",
        birthdate=date(2020, 1, 1),
        weight_kg=12.4,
        diet_mode="adult",
        care_roles=parse_care_roles(
            [
                {"caregiver": "Alex", "role": "owner"},
                {"caregiver": "Maria", "role": "medical lead"},
            ]
        ),
        care_shifts=parse_care_shifts(
            [
                {
                    "label": "Morning shift",
                    "caregiver": "Alex",
                    "role": "owner",
                    "start_time": "08:00",
                    "end_time": "12:00",
                    "days": ["mon", "tue", "wed", "thu", "fri"],
                }
            ],
            pet_id=pet_id,
        ),
        checklist_items=parse_checklist_items(
            [
                {
                    "label": "Brush coat",
                    "frequency": "daily",
                    "category": "grooming",
                    "caregiver": "Alex",
                },
                {
                    "label": "Check ears",
                    "frequency": "weekly",
                    "category": "care",
                    "caregiver": "Maria",
                    "requires_approval": True,
                },
            ],
            pet_id=pet_id,
        ),
        approval_required_actions=(APPROVAL_ACTION_CARE,),
    )


def test_shift_resolution_and_checklist_progress() -> None:
    engine = PetEngine(_profile())
    now = datetime(2026, 3, 9, 9, 0, tzinfo=UTC)

    snapshot, _ = engine.refresh(now, PetContext())

    assert snapshot.current_shift == "Morning shift: Alex (owner)"
    assert snapshot.checklist_progress_pct == 0.0
    assert set(snapshot.pending_checklist_items) == {"Brush coat", "Check ears"}

    engine.complete_checklist_item(now, engine.profile.checklist_items[0].checklist_id, actor="Alex")
    updated, _ = engine.refresh(now.replace(hour=10), PetContext())

    assert updated.checklist_progress_pct == 50.0
    assert updated.pending_checklist_items == ("Check ears",)


def test_approval_queue_and_approval_notice_flow() -> None:
    engine = PetEngine(_profile())
    requested_at = datetime(2026, 3, 9, 8, 30, tzinfo=UTC)

    notices = engine.queue_action_approval(
        requested_at,
        action_name=APPROVAL_ACTION_CARE,
        category="care",
        payload={"action": "medication_given"},
        requested_by="Alex",
        note="Needs lead confirmation",
    )

    assert notices[0].name == "approval_requested"
    approval_id = engine.state.pending_approvals[0]["approval_id"]

    approval, approved_notices = engine.approve_pending_action(
        requested_at.replace(hour=9),
        approval_id,
        approved_by="Maria",
        note="Confirmed",
    )

    assert approval["approved_by"] == "Maria"
    assert approval["approval_note"] == "Confirmed"
    assert approved_notices[0].name == "action_approved"
    assert engine.state.pending_approvals == []


def test_pending_approval_lookup_is_non_destructive() -> None:
    engine = PetEngine(_profile())
    requested_at = datetime(2026, 3, 9, 8, 30, tzinfo=UTC)

    engine.queue_action_approval(
        requested_at,
        action_name=APPROVAL_ACTION_CARE,
        category="care",
        payload={"action": "medication_given"},
        requested_by="Alex",
    )
    approval_id = engine.state.pending_approvals[0]["approval_id"]

    approval = engine.get_pending_approval(approval_id)

    assert approval["approval_id"] == approval_id
    assert len(engine.state.pending_approvals) == 1


def test_operations_report_contains_audit_and_summary() -> None:
    engine = PetEngine(_profile())
    engine.state.daily_history = [
        {
            "date": "2026-03-07",
            "food_today_grams": 180.0,
            "activity_points_today": 20.0,
            "sleep_minutes_today": 520.0,
            "water_today_ml": 410.0,
        },
        {
            "date": "2026-03-08",
            "food_today_grams": 175.0,
            "activity_points_today": 18.0,
            "sleep_minutes_today": 500.0,
            "water_today_ml": 390.0,
        },
    ]
    engine.state.food_today_grams = 160.0
    engine.state.activity_points_today = 12.0
    engine.state.sleep_minutes_today = 480.0
    engine.complete_checklist_item(
        datetime(2026, 3, 9, 9, 0, tzinfo=UTC),
        engine.profile.checklist_items[0].checklist_id,
        actor="Alex",
    )
    engine.queue_action_approval(
        datetime(2026, 3, 9, 9, 15, tzinfo=UTC),
        action_name=APPROVAL_ACTION_CARE,
        category="care",
        payload={"action": "grooming"},
        requested_by="Alex",
    )

    now = datetime(2026, 3, 9, 10, 0, tzinfo=UTC)
    snapshot, _ = engine.refresh(now, PetContext())
    report = engine.build_operations_report(now, snapshot)

    assert "DIVA Operations Summary" in report["content"]
    assert "Current shift: Morning shift: Alex (owner)" in report["content"]
    assert "Pending approvals: 1" in report["content"]
    assert "Brush coat" not in report["content"]
    assert "Check ears" in report["content"]
    assert report["summary"]["pending_approvals_count"] == 1

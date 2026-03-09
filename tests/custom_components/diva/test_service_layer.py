import asyncio
from datetime import date, datetime, time, timezone
from types import SimpleNamespace

import pytest

from custom_components.diva import (
    DOMAIN,
    SERVICE_ADD_EXCEPTION_SCHEMA,
    SERVICE_OBSERVE_BEHAVIOR_SCHEMA,
    _build_behavior_observation_payload,
    _build_schedule_exception_payload,
    _resolve_target_pets,
)
from custom_components.diva.const import APPROVAL_ACTION_CARE
from custom_components.diva.coordinator import DivaCoordinator
from custom_components.diva.pet import PetEngine, PetProfile
from homeassistant.exceptions import HomeAssistantError


def _profile() -> PetProfile:
    return PetProfile.from_dict(
        {
            "pet_id": "don_abrikos_a1b2c3",
            "name": "Don Abrikos",
            "species": "dog",
            "breed": "English Cocker Spaniel",
            "birthdate": "2020-01-01",
            "weight": 12.4,
            "diet_mode": "adult",
        }
    )


def test_add_exception_schema_normalizes_python_date_and_time_values() -> None:
    normalized = SERVICE_ADD_EXCEPTION_SCHEMA(
        {
            "date": date(2026, 3, 9),
            "action": "move",
            "category": "walk",
            "new_time": time(20, 30),
        }
    )

    assert normalized["date"] == "2026-03-09"
    assert normalized["new_time"] == "20:30"


def test_add_exception_payload_requires_time_for_move_and_add() -> None:
    call = SimpleNamespace(
        data={
            "date": "2026-03-09",
            "action": "move",
            "category": "walk",
        }
    )

    with pytest.raises(HomeAssistantError, match="new_time is required"):
        _build_schedule_exception_payload(call)


def test_add_exception_payload_rejects_feed_only_fields_for_non_feed_categories() -> None:
    call = SimpleNamespace(
        data={
            "date": "2026-03-09",
            "action": "add",
            "category": "walk",
            "new_time": "20:30",
            "meal_type": "wet",
        }
    )

    with pytest.raises(HomeAssistantError, match="meal_type is only supported"):
        _build_schedule_exception_payload(call)


def test_resolve_target_pets_deduplicates_duplicate_device_targets() -> None:
    class FakeRegistry:
        def async_get(self, device_id: str):
            if device_id != "device-1":
                return None
            return SimpleNamespace(identifiers={(DOMAIN, "don_abrikos_a1b2c3")})

    coordinator = SimpleNamespace(
        pets={"don_abrikos_a1b2c3": object()},
        pet_ids=("don_abrikos_a1b2c3",),
    )
    hass = SimpleNamespace(data={DOMAIN: {"entry-1": coordinator}})
    call = SimpleNamespace(data={"device_id": ["device-1", "device-1"]})

    import custom_components.diva as diva_module

    previous = diva_module.dr.async_get
    diva_module.dr.async_get = lambda hass_obj: FakeRegistry()
    try:
        targets = _resolve_target_pets(hass, call)
    finally:
        diva_module.dr.async_get = previous

    assert targets == [(coordinator, "don_abrikos_a1b2c3")]


def test_observe_behavior_payload_accepts_frigate_adapter_metadata() -> None:
    call = SimpleNamespace(
        data=SERVICE_OBSERVE_BEHAVIOR_SCHEMA(
            {
                "behavior_type": "vomiting",
                "adapter": "frigate",
                "adapter_payload": {
                    "type": "update",
                    "topic": "frigate/events",
                    "after": {
                        "id": "1718987128.947436-g92ztx",
                        "camera": "kitchen_cam",
                        "label": "dog",
                        "sub_label": ["vomiting", 0.93],
                        "score": 0.82,
                        "top_score": 0.91,
                        "start_time": 1718987128.0,
                        "end_time": 1718987134.0,
                        "current_zones": ["kitchen"],
                        "entered_zones": ["kitchen"],
                        "has_clip": True,
                        "has_snapshot": True,
                    },
                },
            }
        )
    )

    payload = _build_behavior_observation_payload(call)

    assert payload["source"] == "frigate"
    assert payload["confidence"] == 0.91
    assert payload["duration_seconds"] == 6
    assert payload["model_name"] == "frigate"
    assert payload["message"] == "Frigate detected vomiting on kitchen_cam in kitchen"
    assert payload["evidence"]["adapter"] == "frigate"
    assert payload["evidence"]["frigate"]["event_id"] == "1718987128.947436-g92ztx"
    assert payload["evidence"]["frigate"]["topic"] == "frigate/events"


def test_observe_behavior_payload_prefers_explicit_values_over_adapter_defaults() -> None:
    call = SimpleNamespace(
        data=SERVICE_OBSERVE_BEHAVIOR_SCHEMA(
            {
                "behavior_type": "restlessness",
                "adapter": "frigate",
                "adapter_payload": {
                    "type": "classification",
                    "id": "evt-1",
                    "camera": "hallway_cam",
                    "sub_label": "pacing",
                    "score": 0.64,
                },
                "source": "frigate_rule",
                "confidence": 0.77,
                "message": "Pacing confirmed by automation",
                "model_name": "custom-rule",
                "duration_seconds": 15,
                "evidence": {"rule_id": "night_pacing"},
            }
        )
    )

    payload = _build_behavior_observation_payload(call)

    assert payload["source"] == "frigate_rule"
    assert payload["confidence"] == 0.77
    assert payload["message"] == "Pacing confirmed by automation"
    assert payload["model_name"] == "custom-rule"
    assert payload["duration_seconds"] == 15
    assert payload["evidence"]["rule_id"] == "night_pacing"
    assert payload["evidence"]["frigate"]["camera"] == "hallway_cam"


def test_observe_behavior_payload_rejects_adapter_payload_without_adapter() -> None:
    call = SimpleNamespace(
        data=SERVICE_OBSERVE_BEHAVIOR_SCHEMA(
            {
                "behavior_type": "cough",
                "adapter_payload": {"type": "update", "id": "evt-1"},
            }
        )
    )

    with pytest.raises(HomeAssistantError, match="adapter is required"):
        _build_behavior_observation_payload(call)


def test_async_approve_action_keeps_pending_approval_when_execution_fails() -> None:
    profile = _profile()
    engine = PetEngine(profile)
    requested_at = datetime(2026, 3, 9, 8, 30, tzinfo=timezone.utc)

    engine.queue_action_approval(
        requested_at,
        action_name=APPROVAL_ACTION_CARE,
        category="care",
        payload={"action": "grooming"},
        requested_by="Alex",
    )
    approval_id = engine.state.pending_approvals[0]["approval_id"]

    coordinator = object.__new__(DivaCoordinator)
    coordinator._pets = {
        profile.pet_id: SimpleNamespace(
            engine=engine,
            profile=profile,
        )
    }

    async def _unexpected_apply(*args, **kwargs) -> None:
        raise AssertionError("_async_apply_pet_notices should not run when execution fails")

    def _fail_execute(*args, **kwargs):
        raise ValueError("boom")

    coordinator._async_apply_pet_notices = _unexpected_apply
    coordinator._execute_approved_action = _fail_execute

    with pytest.raises(ValueError, match="boom"):
        asyncio.run(
            DivaCoordinator.async_approve_action(
                coordinator,
                profile.pet_id,
                approval_id,
                approved_by="Maria",
            )
        )

    assert engine.state.pending_approvals[0]["approval_id"] == approval_id

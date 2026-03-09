"""Service-dispatch integration tests for DIVA."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, time, timezone

import pytest

pytest.importorskip("homeassistant")
pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant.exceptions import HomeAssistantError  # noqa: E402
from homeassistant.helpers import device_registry as dr  # noqa: E402

from custom_components.diva.const import (  # noqa: E402
    APPROVAL_ACTION_CARE,
    CONF_APPROVAL_REQUIRED_ACTIONS,
    CONF_PET_ID,
    DOMAIN,
    EVENT_DIVA_EVENT,
    SERVICE_ADD_SCHEDULE_EXCEPTION,
    SERVICE_APPROVE_ACTION,
    SERVICE_FEED_PET,
    SERVICE_LOG_CARE_ACTION,
)

from .common import async_setup_diva_runtime, diva_test_entry_data  # noqa: E402


pytestmark = pytest.mark.asyncio


UTC = timezone.utc


async def test_add_schedule_exception_service_accepts_python_date_and_time_objects(
    hass,
    enable_custom_integrations,
) -> None:
    """The registered service should normalize Python date/time values from the caller."""
    entry = await async_setup_diva_runtime(hass)
    coordinator = hass.data[DOMAIN][entry.entry_id]

    await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_SCHEDULE_EXCEPTION,
        {
            CONF_PET_ID: "don_abrikos",
            "date": date(2026, 3, 9),
            "action": "add",
            "category": "walk",
            "new_time": time(20, 30),
            "label": "Late walk",
            "location": "Park",
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    events = coordinator.timeline_events(
        "don_abrikos",
        datetime(2026, 3, 9, 0, 0, tzinfo=UTC),
        datetime(2026, 3, 10, 0, 0, tzinfo=UTC),
    )

    matching = [event for event in events if event.summary == "Late walk"]
    assert len(matching) == 1
    assert matching[0].start.hour == 20
    assert matching[0].start.minute == 30
    assert matching[0].location == "Park"


async def test_feed_service_deduplicates_duplicate_device_targets(
    hass,
    enable_custom_integrations,
) -> None:
    """A duplicate device target list should still execute the service once per pet."""
    entry = await async_setup_diva_runtime(hass)

    device_registry = dr.async_get(hass)
    don_device = device_registry.async_get_device(identifiers={(DOMAIN, "don_abrikos")})
    assert don_device is not None

    events = []
    cancel = hass.bus.async_listen(EVENT_DIVA_EVENT, events.append)
    try:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_FEED_PET,
            {
                "device_id": [don_device.id, don_device.id],
                "portion": 120,
            },
            blocking=True,
        )
        await hass.async_block_till_done()
    finally:
        cancel()

    matched = [
        event for event in events if event.data.get("pet") == "don_abrikos" and event.data.get("event") == "food_served"
    ]
    assert len(matched) == 1


async def test_approve_action_service_keeps_pending_approval_if_execution_fails(
    hass,
    enable_custom_integrations,
    monkeypatch,
) -> None:
    """A failed execution after approval lookup must not consume the queued approval."""
    data = deepcopy(diva_test_entry_data())
    data["pets"][0][CONF_APPROVAL_REQUIRED_ACTIONS] = [APPROVAL_ACTION_CARE]
    entry = await async_setup_diva_runtime(hass, data=data)
    coordinator = hass.data[DOMAIN][entry.entry_id]

    await hass.services.async_call(
        DOMAIN,
        SERVICE_LOG_CARE_ACTION,
        {
            CONF_PET_ID: "don_abrikos",
            "action": "grooming_done",
            "actor": "Alex",
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    pending = coordinator.pets["don_abrikos"].engine.state.pending_approvals
    assert len(pending) == 1
    approval_id = pending[0]["approval_id"]

    def _boom(*args, **kwargs):
        raise ValueError("approval execution failed")

    monkeypatch.setattr(coordinator, "_execute_approved_action", _boom)

    with pytest.raises(HomeAssistantError, match="approval execution failed"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_APPROVE_ACTION,
            {
                CONF_PET_ID: "don_abrikos",
                "approval_id": approval_id,
                "approved_by": "Maria",
            },
            blocking=True,
        )

    pending_after = coordinator.pets["don_abrikos"].engine.state.pending_approvals
    assert len(pending_after) == 1
    assert pending_after[0]["approval_id"] == approval_id


async def test_add_schedule_exception_service_rejects_feed_only_fields_for_walks(
    hass,
    enable_custom_integrations,
) -> None:
    """The runtime service API should reject meal fields for non-feeding exceptions."""
    await async_setup_diva_runtime(hass)

    with pytest.raises(HomeAssistantError, match="meal_type is only supported for feed schedule exceptions"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ADD_SCHEDULE_EXCEPTION,
            {
                CONF_PET_ID: "don_abrikos",
                "date": "2026-03-09",
                "action": "add",
                "category": "walk",
                "new_time": "20:30",
                "meal_type": "wet",
            },
            blocking=True,
        )

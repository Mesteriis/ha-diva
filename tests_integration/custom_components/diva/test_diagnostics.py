"""Diagnostics smoke tests for DIVA."""

from __future__ import annotations

import pytest

pytest.importorskip("homeassistant")
pytest.importorskip("pytest_homeassistant_custom_component")

from custom_components.diva.const import (  # noqa: E402
    CONF_PET_ID,
    DOMAIN,
    EVENT_DIVA_EVENT,
    SERVICE_FEED_PET,
)
from custom_components.diva.diagnostics import async_get_config_entry_diagnostics  # noqa: E402

from .common import async_setup_diva_runtime  # noqa: E402


pytestmark = pytest.mark.asyncio


async def test_diagnostics_include_pet_state_camera_config_and_recent_events(
    hass,
    enable_custom_integrations,
) -> None:
    """Diagnostics should expose the configured pets, entity states, and recent events."""
    entry = await async_setup_diva_runtime(hass)

    events = []
    cancel = hass.bus.async_listen(EVENT_DIVA_EVENT, events.append)
    try:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_FEED_PET,
            {
                CONF_PET_ID: "don_abrikos",
                "portion": 100,
            },
            blocking=True,
        )
        await hass.async_block_till_done()
    finally:
        cancel()

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)

    assert diagnostics["hub"]["name"]
    assert "don_abrikos" in diagnostics["pet_config"]
    assert diagnostics["entity_states"]
    assert "don_abrikos" in diagnostics["camera_settings"]
    assert diagnostics["recent_events"]["don_abrikos"]
    assert any(event.data.get("event") == "food_served" for event in events)

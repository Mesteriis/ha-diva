"""Real Home Assistant runtime smoke tests for DIVA."""

from __future__ import annotations

import pytest

pytest.importorskip("homeassistant")
pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant.helpers import device_registry as dr, entity_registry as er  # noqa: E402

from custom_components.diva.const import (  # noqa: E402
    CONF_PET_ID,
    DOMAIN,
    EVENT_DIVA_EVENT,
    SERVICE_FEED_PET,
)

from .common import async_setup_diva_runtime  # noqa: E402


pytestmark = pytest.mark.asyncio


async def test_setup_registers_hub_pet_devices_and_entities(
    hass,
    enable_custom_integrations,
) -> None:
    """DIVA should materialize a hub device and pet-scoped entities."""
    entry = await async_setup_diva_runtime(hass)

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    hub_device = device_registry.async_get_device(identifiers={(DOMAIN, f"hub_{entry.entry_id}")})
    don_device = device_registry.async_get_device(identifiers={(DOMAIN, "don_abrikos")})
    murka_device = device_registry.async_get_device(identifiers={(DOMAIN, "murka")})

    assert hub_device is not None
    assert don_device is not None
    assert murka_device is not None

    assert entity_registry.async_get_entity_id("sensor", DOMAIN, "don_abrikos-food_today") is not None
    assert entity_registry.async_get_entity_id("sensor", DOMAIN, "murka-food_today") is not None
    assert entity_registry.async_get_entity_id("binary_sensor", DOMAIN, "don_abrikos-hungry") is not None
    assert entity_registry.async_get_entity_id("button", DOMAIN, "don_abrikos-feed_now") is not None


async def test_feed_service_fires_diva_event_for_target_pet(
    hass,
    enable_custom_integrations,
) -> None:
    """A pet-targeted service call should publish a DIVA event."""
    await async_setup_diva_runtime(hass)

    events = []
    cancel = hass.bus.async_listen(EVENT_DIVA_EVENT, events.append)
    try:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_FEED_PET,
            {
                CONF_PET_ID: "don_abrikos",
                "portion": 120,
            },
            blocking=True,
        )
        await hass.async_block_till_done()
    finally:
        cancel()

    assert any(
        event.data.get("pet") == "don_abrikos" and event.data.get("event") == "food_served"
        for event in events
    )

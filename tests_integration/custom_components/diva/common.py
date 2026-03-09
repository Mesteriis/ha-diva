"""Shared helpers for DIVA Home Assistant integration tests."""

from __future__ import annotations

from typing import Any

from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.diva.const import (
    CONF_BIRTHDATE,
    CONF_BREED,
    CONF_CAMERA_ENTITY_ID,
    CONF_DIET_MODE,
    CONF_FOOD_BOWL_AREA,
    CONF_HUB_NAME,
    CONF_NAME,
    CONF_PETS,
    CONF_PET_ID,
    CONF_SPECIES,
    CONF_WATER_BOWL_AREA,
    CONF_WEIGHT,
    DEFAULT_HUB_NAME,
    DIET_MODE_ADULT,
    DOMAIN,
)


def diva_test_entry_data() -> dict[str, Any]:
    """Return deterministic multi-pet config entry data for DIVA tests."""
    return {
        CONF_HUB_NAME: DEFAULT_HUB_NAME,
        CONF_PETS: [
            {
                CONF_PET_ID: "don_abrikos",
                CONF_NAME: "Don Abrikos",
                CONF_SPECIES: "dog",
                CONF_BREED: "Corgi",
                CONF_BIRTHDATE: "2020-05-10",
                CONF_WEIGHT: 8.2,
                CONF_DIET_MODE: DIET_MODE_ADULT,
                CONF_CAMERA_ENTITY_ID: None,
                CONF_FOOD_BOWL_AREA: None,
                CONF_WATER_BOWL_AREA: None,
            },
            {
                CONF_PET_ID: "murka",
                CONF_NAME: "Murka",
                CONF_SPECIES: "cat",
                CONF_BREED: "Siberian",
                CONF_BIRTHDATE: "2021-09-01",
                CONF_WEIGHT: 4.4,
                CONF_DIET_MODE: DIET_MODE_ADULT,
                CONF_CAMERA_ENTITY_ID: None,
                CONF_FOOD_BOWL_AREA: None,
                CONF_WATER_BOWL_AREA: None,
            },
        ],
    }


async def async_setup_diva_runtime(hass, *, data: dict[str, Any] | None = None) -> MockConfigEntry:
    """Set up a real Home Assistant runtime for DIVA smoke tests."""
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    entry = MockConfigEntry(
        domain=DOMAIN,
        title=(data or {}).get(CONF_HUB_NAME, DEFAULT_HUB_NAME),
        data=data or diva_test_entry_data(),
        version=2,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry

"""Config flow smoke tests for DIVA."""

from __future__ import annotations

import pytest

pytest.importorskip("homeassistant")
pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant import config_entries  # noqa: E402
from homeassistant.data_entry_flow import FlowResultType  # noqa: E402

from custom_components.diva.const import (  # noqa: E402
    CONF_BIRTHDATE,
    CONF_BREED,
    CONF_DIET_MODE,
    CONF_NAME,
    CONF_PETS,
    CONF_SPECIES,
    CONF_WEIGHT,
    DEFAULT_HUB_NAME,
    DIET_MODE_ADULT,
    DOMAIN,
)

from .common import async_setup_diva_runtime  # noqa: E402


pytestmark = pytest.mark.asyncio


async def test_user_flow_creates_multi_pet_hub_entry(
    hass,
    enable_custom_integrations,
) -> None:
    """The user flow should create a hub entry with the first pet profile."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data={
            CONF_NAME: "Don Abrikos",
            CONF_SPECIES: "dog",
            CONF_BREED: "Corgi",
            CONF_BIRTHDATE: "2020-05-10",
            CONF_WEIGHT: 8.2,
            CONF_DIET_MODE: DIET_MODE_ADULT,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == DEFAULT_HUB_NAME
    assert len(result["data"][CONF_PETS]) == 1
    assert result["data"][CONF_PETS][0][CONF_NAME] == "Don Abrikos"


async def test_options_flow_can_add_a_second_pet(
    hass,
    enable_custom_integrations,
) -> None:
    """The options flow should support adding more pets to one DIVA hub."""
    entry = await async_setup_diva_runtime(hass)

    menu = await hass.config_entries.options.async_init(entry.entry_id)
    assert menu["type"] is FlowResultType.MENU

    add_pet = await hass.config_entries.options.async_configure(
        menu["flow_id"],
        {"next_step_id": "add_pet"},
    )
    assert add_pet["type"] is FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        add_pet["flow_id"],
        user_input={
            CONF_NAME: "Barsik",
            CONF_SPECIES: "cat",
            CONF_BREED: "British Shorthair",
            CONF_BIRTHDATE: "2022-02-02",
            CONF_WEIGHT: 4.9,
            CONF_DIET_MODE: DIET_MODE_ADULT,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_HUB_NAME] == DEFAULT_HUB_NAME
    assert len(result["data"][CONF_PETS]) == 3

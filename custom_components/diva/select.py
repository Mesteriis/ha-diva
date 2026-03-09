"""Select platform for DIVA."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import EntityCategory

from . import DivaConfigEntry
from .const import DIET_MODES, OPERATION_MODES
from .coordinator import DivaCoordinator
from .entity import DivaPetEntity


async def async_setup_entry(hass, entry: DivaConfigEntry, async_add_entities) -> None:
    """Set up DIVA select entities."""
    coordinator = entry.runtime_data
    entities = []
    for pet_id in coordinator.pet_ids:
        entities.append(DivaDietModeSelect(coordinator, pet_id))
        entities.append(DivaOperationModeSelect(coordinator, pet_id))
    async_add_entities(entities)


class DivaDietModeSelect(DivaPetEntity, SelectEntity):
    """Representation of the pet diet mode selector."""

    _attr_translation_key = "diet_mode"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(DIET_MODES)
    _attr_icon = "mdi:food-variant"

    def __init__(self, coordinator: DivaCoordinator, pet_id: str) -> None:
        """Initialize the diet mode selector."""
        super().__init__(coordinator, pet_id, "diet_mode")

    @property
    def current_option(self) -> str:
        """Return the current diet mode."""
        return self.pet_snapshot.diet_mode

    async def async_select_option(self, option: str) -> None:
        """Select a new diet mode."""
        await self.coordinator.async_set_diet_mode(self.pet_id, option)


class DivaOperationModeSelect(DivaPetEntity, SelectEntity):
    """Representation of the pet operation mode selector."""

    _attr_translation_key = "operation_mode"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(OPERATION_MODES)
    _attr_icon = "mdi:calendar-sync"

    def __init__(self, coordinator: DivaCoordinator, pet_id: str) -> None:
        """Initialize the operation mode selector."""
        super().__init__(coordinator, pet_id, "operation_mode")

    @property
    def current_option(self) -> str:
        """Return the current manual operation mode."""
        return self.pet_snapshot.operation_mode

    async def async_select_option(self, option: str) -> None:
        """Select a new operation mode."""
        await self.coordinator.async_set_manual_mode(self.pet_id, option)

"""Number platform for DIVA."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.helpers.entity import EntityCategory

from . import DivaConfigEntry
from .coordinator import DivaCoordinator
from .entity import DivaPetEntity


@dataclass(frozen=True, kw_only=True)
class DivaNumberDescription(NumberEntityDescription):
    """Describe a DIVA number entity."""

    value_fn: Callable[[object], float]
    set_fn: Callable[[DivaCoordinator, str, float], Awaitable[None]]


NUMBERS: tuple[DivaNumberDescription, ...] = (
    DivaNumberDescription(
        key="food_portion",
        translation_key="food_portion",
        native_min_value=10,
        native_max_value=1000,
        native_step=1,
        native_unit_of_measurement="g",
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:scale",
        value_fn=lambda snapshot: snapshot.food_portion_grams,
        set_fn=lambda coordinator, pet_id, value: coordinator.async_set_food_portion(pet_id, value),
    ),
    DivaNumberDescription(
        key="daily_calories",
        translation_key="daily_calories",
        native_min_value=100,
        native_max_value=3000,
        native_step=10,
        native_unit_of_measurement="kcal",
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:fire",
        value_fn=lambda snapshot: snapshot.daily_calories,
        set_fn=lambda coordinator, pet_id, value: coordinator.async_set_daily_calories(pet_id, value),
    ),
    DivaNumberDescription(
        key="weight_goal_min",
        translation_key="weight_goal_min",
        native_min_value=0.1,
        native_max_value=200,
        native_step=0.1,
        native_unit_of_measurement="kg",
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:arrow-down-bold-box-outline",
        value_fn=lambda snapshot: snapshot.weight_goal_min_kg or 0.1,
        set_fn=lambda coordinator, pet_id, value: coordinator.async_set_weight_goal_min(pet_id, value),
    ),
    DivaNumberDescription(
        key="weight_goal_max",
        translation_key="weight_goal_max",
        native_min_value=0.1,
        native_max_value=200,
        native_step=0.1,
        native_unit_of_measurement="kg",
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:arrow-up-bold-box-outline",
        value_fn=lambda snapshot: snapshot.weight_goal_max_kg or 0.1,
        set_fn=lambda coordinator, pet_id, value: coordinator.async_set_weight_goal_max(pet_id, value),
    ),
)


async def async_setup_entry(hass, entry: DivaConfigEntry, async_add_entities) -> None:
    """Set up DIVA number entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        DivaNumberEntity(coordinator, pet_id, description)
        for pet_id in coordinator.pet_ids
        for description in NUMBERS
    )


class DivaNumberEntity(DivaPetEntity, NumberEntity):
    """Representation of a DIVA number."""

    entity_description: DivaNumberDescription

    def __init__(self, coordinator: DivaCoordinator, pet_id: str, description: DivaNumberDescription) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, pet_id, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float:
        """Return the current number value."""
        return float(self.entity_description.value_fn(self.pet_snapshot))

    async def async_set_native_value(self, value: float) -> None:
        """Persist the new value."""
        await self.entity_description.set_fn(self.coordinator, self.pet_id, value)

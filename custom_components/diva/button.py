"""Button platform for DIVA."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from . import DivaConfigEntry
from .coordinator import DivaCoordinator
from .entity import DivaPetEntity


@dataclass(frozen=True, kw_only=True)
class DivaButtonDescription(ButtonEntityDescription):
    """Describe a DIVA button."""

    press_fn: Callable[[DivaCoordinator, str], Awaitable[None]]


BUTTONS: tuple[DivaButtonDescription, ...] = (
    DivaButtonDescription(
        key="feed_now",
        translation_key="feed_now",
        icon="mdi:food",
        press_fn=lambda coordinator, pet_id: coordinator.async_feed_now(pet_id),
    ),
    DivaButtonDescription(
        key="refill_food",
        translation_key="refill_food",
        icon="mdi:bowl-mix",
        press_fn=lambda coordinator, pet_id: coordinator.async_refill_food(pet_id),
    ),
    DivaButtonDescription(
        key="refill_water",
        translation_key="refill_water",
        icon="mdi:cup-water",
        press_fn=lambda coordinator, pet_id: coordinator.async_refill_water(pet_id),
    ),
    DivaButtonDescription(
        key="start_walk",
        translation_key="start_walk",
        icon="mdi:walk",
        press_fn=lambda coordinator, pet_id: coordinator.async_start_walk(pet_id),
    ),
    DivaButtonDescription(
        key="finish_walk",
        translation_key="finish_walk",
        icon="mdi:check-bold",
        press_fn=lambda coordinator, pet_id: coordinator.async_finish_walk(pet_id),
    ),
    DivaButtonDescription(
        key="sync_calendar",
        translation_key="sync_calendar",
        icon="mdi:calendar-sync",
        press_fn=lambda coordinator, pet_id: coordinator.async_sync_pet_calendar(pet_id),
    ),
    DivaButtonDescription(
        key="generate_vet_report",
        translation_key="generate_vet_report",
        icon="mdi:file-heart-outline",
        press_fn=lambda coordinator, pet_id: coordinator.async_generate_vet_report(pet_id),
    ),
    DivaButtonDescription(
        key="generate_operations_report",
        translation_key="generate_operations_report",
        icon="mdi:file-document-outline",
        press_fn=lambda coordinator, pet_id: coordinator.async_generate_operations_report(pet_id),
    ),
)


async def async_setup_entry(hass, entry: DivaConfigEntry, async_add_entities) -> None:
    """Set up DIVA button entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        DivaButtonEntity(coordinator, pet_id, description)
        for pet_id in coordinator.pet_ids
        for description in BUTTONS
    )


class DivaButtonEntity(DivaPetEntity, ButtonEntity):
    """Representation of a DIVA button."""

    entity_description: DivaButtonDescription

    def __init__(self, coordinator: DivaCoordinator, pet_id: str, description: DivaButtonDescription) -> None:
        """Initialize the button."""
        super().__init__(coordinator, pet_id, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Handle a button press."""
        await self.entity_description.press_fn(self.coordinator, self.pet_id)

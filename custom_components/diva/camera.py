"""Camera platform for DIVA."""

from __future__ import annotations

from typing import Any

from homeassistant.components.camera import Camera
from homeassistant.helpers.entity import EntityCategory

from . import DivaConfigEntry
from .coordinator import DivaCoordinator
from .entity import DivaPetEntity


async def async_setup_entry(hass, entry: DivaConfigEntry, async_add_entities) -> None:
    """Set up DIVA camera entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        DivaPetCamera(coordinator, pet_id)
        for pet_id in coordinator.pet_ids
        if coordinator.get_profile(pet_id).camera_entity_id
    )


class DivaPetCamera(DivaPetEntity, Camera):
    """A diagnostic camera that exposes the last analyzed pet frame."""

    _attr_translation_key = "monitor"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, coordinator: DivaCoordinator, pet_id: str) -> None:
        """Initialize the DIVA diagnostic camera."""
        Camera.__init__(self)
        DivaPetEntity.__init__(self, coordinator, pet_id, "monitor")

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        """Return the most recent analyzed camera frame."""
        image = self.coordinator.get_camera_image(self.pet_id)
        if image is None:
            await self.coordinator.async_request_refresh()
            image = self.coordinator.get_camera_image(self.pet_id)
        return image

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the latest analysis metadata."""
        return {
            "source_camera": self.coordinator.get_profile(self.pet_id).camera_entity_id,
            **self.coordinator.get_camera_analysis(self.pet_id),
        }

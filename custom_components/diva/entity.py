"""Shared entity helpers for DIVA."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, INTEGRATION_VERSION
from .coordinator import DivaCoordinator
from .pet import PetSnapshot


class DivaPetEntity(CoordinatorEntity[DivaCoordinator]):
    """Base class for pet-scoped DIVA entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DivaCoordinator, pet_id: str, unique_key: str) -> None:
        """Initialize a DIVA pet entity."""
        super().__init__(coordinator, context=pet_id)
        self.pet_id = pet_id
        profile = coordinator.get_profile(pet_id)
        self._attr_unique_id = f"{pet_id}-{unique_key}"
        self._attr_entity_picture = profile.avatar
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, pet_id)},
            name=profile.name,
            manufacturer="DIVA",
            model=f"{profile.species.title()} Guardian Profile",
            sw_version=INTEGRATION_VERSION,
            via_device=(DOMAIN, coordinator.hub_identifier),
        )

    @property
    def pet_snapshot(self) -> PetSnapshot:
        """Return the current snapshot for this pet."""
        return self.coordinator.get_snapshot(self.pet_id)

    @property
    def available(self) -> bool:
        """Return if this pet entity is available."""
        return super().available and self.pet_id in self.coordinator.data

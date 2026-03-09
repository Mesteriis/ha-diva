"""Binary sensor platform for DIVA."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription

from . import DivaConfigEntry
from .coordinator import DivaCoordinator
from .entity import DivaPetEntity


@dataclass(frozen=True, kw_only=True)
class DivaBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a DIVA binary sensor."""

    value_fn: Callable[[object], bool]


BINARY_SENSORS: tuple[DivaBinarySensorDescription, ...] = (
    DivaBinarySensorDescription(
        key="hungry",
        translation_key="hungry",
        icon="mdi:food-off",
        value_fn=lambda snapshot: snapshot.hungry,
    ),
    DivaBinarySensorDescription(
        key="needs_walk",
        translation_key="needs_walk",
        icon="mdi:dog-side",
        value_fn=lambda snapshot: snapshot.needs_walk,
    ),
    DivaBinarySensorDescription(
        key="food_bowl_empty",
        translation_key="food_bowl_empty",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda snapshot: snapshot.food_bowl_empty,
    ),
    DivaBinarySensorDescription(
        key="water_bowl_empty",
        translation_key="water_bowl_empty",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda snapshot: snapshot.water_bowl_empty,
    ),
    DivaBinarySensorDescription(
        key="sleeping",
        translation_key="sleeping",
        icon="mdi:sleep",
        value_fn=lambda snapshot: snapshot.sleeping,
    ),
    DivaBinarySensorDescription(
        key="home_alone",
        translation_key="home_alone",
        icon="mdi:home-account",
        value_fn=lambda snapshot: snapshot.home_alone,
    ),
    DivaBinarySensorDescription(
        key="geofence_breached",
        translation_key="geofence_breached",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda snapshot: snapshot.geofence_breached,
    ),
    DivaBinarySensorDescription(
        key="anomaly_detected",
        translation_key="anomaly_detected",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda snapshot: snapshot.anomaly_detected,
    ),
)


async def async_setup_entry(hass, entry: DivaConfigEntry, async_add_entities) -> None:
    """Set up DIVA binary sensor entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        DivaBinarySensorEntity(coordinator, pet_id, description)
        for pet_id in coordinator.pet_ids
        for description in BINARY_SENSORS
    )


class DivaBinarySensorEntity(DivaPetEntity, BinarySensorEntity):
    """Representation of a DIVA binary sensor."""

    entity_description: DivaBinarySensorDescription

    def __init__(self, coordinator: DivaCoordinator, pet_id: str, description: DivaBinarySensorDescription) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, pet_id, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return the binary sensor state."""
        return self.entity_description.value_fn(self.pet_snapshot)

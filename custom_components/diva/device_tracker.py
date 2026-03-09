"""Device tracker platform for DIVA."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity

from . import DivaConfigEntry
from .coordinator import DivaCoordinator
from .entity import DivaPetEntity


async def async_setup_entry(hass, entry: DivaConfigEntry, async_add_entities) -> None:
    """Set up DIVA pet location entities."""
    coordinator = entry.runtime_data
    async_add_entities(DivaPetLocationEntity(coordinator, pet_id) for pet_id in coordinator.pet_ids)


class DivaPetLocationEntity(DivaPetEntity, TrackerEntity):
    """Expose the current pet position as a synthetic device tracker."""

    _attr_translation_key = "pet_location"
    _attr_icon = "mdi:crosshairs-gps"

    def __init__(self, coordinator: DivaCoordinator, pet_id: str) -> None:
        """Initialize the DIVA tracker entity."""
        super().__init__(coordinator, pet_id, "location")

    @property
    def latitude(self) -> float | None:
        """Return the last known latitude."""
        point = _latest_point(self.coordinator, self.pet_id)
        return point.get("latitude") if point is not None else None

    @property
    def longitude(self) -> float | None:
        """Return the last known longitude."""
        point = _latest_point(self.coordinator, self.pet_id)
        return point.get("longitude") if point is not None else None

    @property
    def source_type(self) -> SourceType:
        """Return the tracker source type."""
        return SourceType.GPS

    @property
    def location_accuracy(self) -> int:
        """Return the synthetic tracker accuracy in meters."""
        return 15

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional route-oriented map attributes."""
        managed = self.coordinator.pets[self.pet_id]
        snapshot = self.pet_snapshot
        current_route = managed.engine.state.current_walk_route
        last_route = managed.engine.state.last_walk_route
        latest = _latest_point(self.coordinator, self.pet_id)
        return {
            "pet_id": self.pet_id,
            "pet_name": self.coordinator.get_profile(self.pet_id).name,
            "active_walk": managed.engine.state.walk_active,
            "gps_tracker_state": snapshot.gps_tracker_state,
            "current_zone": snapshot.current_zone,
            "current_room": snapshot.current_room,
            "current_route_points": current_route,
            "last_route_points": last_route,
            "last_walk_distance_km": snapshot.last_walk_distance_km,
            "last_walk_duration_minutes": snapshot.last_walk_duration_minutes,
            "last_walk_route_summary": snapshot.last_walk_route_summary,
            "last_walk_summary": managed.engine.state.last_walk_summary,
            "last_seen_position_at": latest.get("timestamp") if latest is not None else None,
        }

    @property
    def available(self) -> bool:
        """Return if tracker coordinates are available."""
        return super().available and _latest_point(self.coordinator, self.pet_id) is not None



def _latest_point(coordinator: DivaCoordinator, pet_id: str) -> dict[str, Any] | None:
    """Return the best currently known location point for a pet."""
    state = coordinator.pets[pet_id].engine.state
    for series in (state.gps_history, state.current_walk_route, state.last_walk_route):
        if series:
            point = series[-1]
            latitude = point.get("latitude")
            longitude = point.get("longitude")
            if isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
                return {
                    "timestamp": point.get("timestamp"),
                    "latitude": round(float(latitude), 6),
                    "longitude": round(float(longitude), 6),
                }
    return None

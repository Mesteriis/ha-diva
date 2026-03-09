"""Diagnostics support for DIVA."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers import entity_registry as er

from . import DivaConfigEntry
from .const import DOMAIN


async def async_get_config_entry_diagnostics(hass, entry: DivaConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a DIVA config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entity_registry = er.async_get(hass)
    entity_entries = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    entity_states: dict[str, Any] = {}
    for entity_entry in entity_entries:
        state = hass.states.get(entity_entry.entity_id)
        entity_states[entity_entry.entity_id] = {
            "state": state.state if state else None,
            "attributes": dict(state.attributes) if state else None,
        }

    return {
        "entry": {
            "title": entry.title,
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "storage": {
            "backend": "json_root",
            "path": str(coordinator._runtime_store.path),
        },
        "hub": {
            "name": coordinator.hub_name,
            "identifier": coordinator.hub_identifier,
        },
        "pet_config": {pet_id: managed.profile.as_dict() for pet_id, managed in coordinator.pets.items()},
        "pet_config_v3": {pet_id: managed.profile.as_v3_dict() for pet_id, managed in coordinator.pets.items()},
        "entity_states": entity_states,
        "camera_settings": {
            pet_id: {
                "camera_entity_id": managed.profile.camera_entity_id,
                "food_bowl_area": managed.profile.food_bowl_area.as_dict() if managed.profile.food_bowl_area else None,
                "water_bowl_area": managed.profile.water_bowl_area.as_dict() if managed.profile.water_bowl_area else None,
                "analysis": managed.camera.last_analysis,
            }
            for pet_id, managed in coordinator.pets.items()
        },
        "timeline": {pet_id: coordinator.get_timeline(pet_id) for pet_id in coordinator.pet_ids},
        "recent_events": {pet_id: managed.engine.state.recent_records for pet_id, managed in coordinator.pets.items()},
        "journal": {pet_id: managed.engine.state.journal_entries for pet_id, managed in coordinator.pets.items()},
        "runtime": coordinator.diagnostics_payload(),
    }

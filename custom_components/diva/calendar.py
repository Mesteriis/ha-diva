"""Calendar platform for DIVA."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util import dt as dt_util

from . import DivaConfigEntry
from .coordinator import DivaCoordinator
from .entity import DivaPetEntity


async def async_setup_entry(hass, entry: DivaConfigEntry, async_add_entities) -> None:
    """Set up DIVA calendar entities."""
    coordinator = entry.runtime_data
    async_add_entities(DivaTimelineCalendarEntity(coordinator, pet_id) for pet_id in coordinator.pet_ids)


class DivaTimelineCalendarEntity(DivaPetEntity, CalendarEntity):
    """Pet timeline calendar entity."""

    _attr_translation_key = "timeline"
    _attr_icon = "mdi:calendar-heart"

    def __init__(self, coordinator: DivaCoordinator, pet_id: str) -> None:
        """Initialize the timeline calendar."""
        super().__init__(coordinator, pet_id, "timeline")

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        now = dt_util.now()
        events = self.coordinator.timeline_events(self.pet_id, now, now + timedelta(days=30))
        if not events:
            return None
        next_event = events[0]
        return CalendarEvent(
            start=next_event.start,
            end=next_event.end,
            summary=next_event.summary,
            description=next_event.description,
            location=next_event.location,
            uid=next_event.event_id,
        )

    async def async_get_events(self, hass, start_date, end_date):
        """Return the upcoming pet timeline events in the selected range."""
        events = self.coordinator.timeline_events(self.pet_id, start_date, end_date)
        return [
            CalendarEvent(
                start=event.start,
                end=event.end,
                summary=event.summary,
                description=event.description,
                location=event.location,
                uid=event.event_id,
            )
            for event in events
        ]

"""Event payload helpers for DIVA."""

from __future__ import annotations

from typing import Any

from .const import (
    ATTR_EVENT,
    ATTR_PET,
    ATTR_PET_NAME,
    ATTR_RECOMMENDATION,
    ATTR_SEVERITY,
    ATTR_TIMESTAMP,
    ATTR_TYPE,
    EVENT_DIVA_ANOMALY,
    EVENT_DIVA_EVENT,
    EVENT_DIVA_RECOMMENDATION,
)
from .pet import PetNotice, PetProfile


def notice_event_type(notice: PetNotice) -> str:
    """Return the Home Assistant event type for a notice."""
    if notice.category == "anomaly":
        return EVENT_DIVA_ANOMALY
    if notice.category == "recommendation":
        return EVENT_DIVA_RECOMMENDATION
    return EVENT_DIVA_EVENT


def build_notice_payload(profile: PetProfile, notice: PetNotice) -> dict[str, Any]:
    """Build the event payload for a runtime notice."""
    payload: dict[str, Any] = {
        ATTR_PET: profile.slug,
        ATTR_PET_NAME: profile.name,
        ATTR_TIMESTAMP: notice.timestamp,
    }
    if notice.category == "anomaly":
        payload[ATTR_TYPE] = notice.name
        payload[ATTR_SEVERITY] = notice.severity
    elif notice.category == "recommendation":
        payload[ATTR_RECOMMENDATION] = notice.message or notice.name
    else:
        payload[ATTR_EVENT] = notice.name

    if notice.message and notice.category != "recommendation":
        payload["message"] = notice.message
    if notice.data:
        payload.update(notice.data)
    return payload

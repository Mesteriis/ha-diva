"""Capability adapters for external behavior and vision providers."""

from __future__ import annotations

from typing import Any, Mapping


FRIGATE_BEHAVIOR_ADAPTERS = {"frigate", "frigate_event"}


def adapt_behavior_observation(
    adapter: str | None,
    payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Normalize adapter-specific metadata for a behavior observation."""
    if adapter is None:
        return {}
    normalized = str(adapter).strip().lower()
    if not normalized:
        return {}
    if normalized in FRIGATE_BEHAVIOR_ADAPTERS:
        return _adapt_frigate_behavior_observation(payload)
    raise ValueError(f"Unsupported behavior adapter: {adapter}")


def _adapt_frigate_behavior_observation(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    """Normalize Frigate MQTT payloads into DIVA behavior metadata."""
    if payload is None:
        raise ValueError("adapter_payload is required for the frigate adapter")
    if not isinstance(payload, Mapping):
        raise ValueError("adapter_payload must be an object")

    root = dict(payload)
    event = _frigate_event_payload(root)
    sub_label, sub_label_score = _extract_frigate_sub_label(event.get("sub_label"))
    description = _coerce_optional_str(root.get("description")) or _coerce_optional_str(event.get("description"))
    camera = _coerce_optional_str(event.get("camera")) or _coerce_optional_str(root.get("camera"))
    label = _coerce_optional_str(event.get("label")) or _coerce_optional_str(root.get("label"))
    model_name = (
        _coerce_optional_str(root.get("model"))
        or _coerce_optional_str(event.get("model"))
        or "frigate"
    )
    confidence = _first_float(
        event.get("top_score"),
        event.get("score"),
        root.get("score"),
        sub_label_score,
    )
    start_time = _coerce_float(event.get("start_time")) or _coerce_float(root.get("start_time"))
    end_time = _coerce_float(event.get("end_time")) or _coerce_float(root.get("end_time"))

    evidence = {
        "adapter": "frigate",
        "frigate": {
            "message_type": _coerce_optional_str(root.get("type")),
            "event_id": _coerce_optional_str(event.get("id")) or _coerce_optional_str(root.get("id")),
            "camera": camera,
            "label": label,
            "sub_label": sub_label,
            "current_zones": _string_list(event.get("current_zones")),
            "entered_zones": _string_list(event.get("entered_zones")),
            "has_clip": _coerce_optional_bool(event.get("has_clip")),
            "has_snapshot": _coerce_optional_bool(event.get("has_snapshot")),
            "model": _coerce_optional_str(root.get("model")) or _coerce_optional_str(event.get("model")),
            "description": description,
            "score": _coerce_float(event.get("score")) or _coerce_float(root.get("score")),
            "top_score": _coerce_float(event.get("top_score")),
            "start_time": start_time,
            "end_time": end_time,
            "topic": _coerce_optional_str(root.get("topic")),
        },
    }

    if sub_label_score is not None:
        evidence["frigate"]["sub_label_score"] = sub_label_score

    duration_seconds: int | None = None
    if start_time is not None and end_time is not None and end_time >= start_time:
        duration_seconds = max(1, int(round(end_time - start_time)))

    return {
        "source": "frigate",
        "confidence": confidence,
        "duration_seconds": duration_seconds,
        "model_name": model_name,
        "message": _frigate_message(
            description=description,
            camera=camera,
            label=label,
            sub_label=sub_label,
            current_zones=evidence["frigate"]["current_zones"],
            entered_zones=evidence["frigate"]["entered_zones"],
        ),
        "evidence": evidence,
    }


def _frigate_event_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    after = payload.get("after")
    before = payload.get("before")
    if isinstance(after, Mapping):
        return dict(after)
    if isinstance(before, Mapping):
        return dict(before)
    return dict(payload)


def _extract_frigate_sub_label(value: Any) -> tuple[str | None, float | None]:
    if isinstance(value, (list, tuple)):
        label = _coerce_optional_str(value[0]) if value else None
        score = _coerce_float(value[1]) if len(value) > 1 else None
        return label, score
    if isinstance(value, str):
        return value.strip() or None, None
    return None, None


def _frigate_message(
    *,
    description: str | None,
    camera: str | None,
    label: str | None,
    sub_label: str | None,
    current_zones: list[str],
    entered_zones: list[str],
) -> str | None:
    if description:
        return description
    subject = sub_label or label
    if not subject and not camera:
        return None
    pieces = []
    if subject:
        pieces.append(f"Frigate detected {subject}")
    else:
        pieces.append("Frigate detected activity")
    if camera:
        pieces.append(f"on {camera}")
    zones = current_zones or entered_zones
    if zones:
        pieces.append(f"in {zones[0]}")
    return " ".join(pieces)


def _string_list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [item for item in (_coerce_optional_str(item) for item in value) if item]
    item = _coerce_optional_str(value)
    return [item] if item else []


def _coerce_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _coerce_optional_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "on", "yes", "1"}:
        return True
    if text in {"false", "off", "no", "0"}:
        return False
    return None


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_float(*values: Any) -> float | None:
    for value in values:
        numeric = _coerce_float(value)
        if numeric is not None:
            return numeric
    return None

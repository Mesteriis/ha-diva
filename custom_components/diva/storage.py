"""JSON-backed storage helpers for DIVA runtime data."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)
_STORAGE_FILE_VERSION = 1


class DivaJSONStorage:
    """Persist DIVA runtime data into a JSON file in the HA config root."""

    def __init__(self, hass: HomeAssistant, filename: str) -> None:
        """Initialize the storage wrapper."""
        self.hass = hass
        self.path = Path(hass.config.path(filename))
        self._lock = asyncio.Lock()

    async def async_load_entry(self, entry_id: str) -> dict[str, Any]:
        """Load the storage payload for a config entry."""
        async with self._lock:
            payload = await self.hass.async_add_executor_job(self._read_file)
            payload, migrated = _normalize_storage_payload_for_entry(payload, entry_id)
            if migrated:
                await self.hass.async_add_executor_job(self._write_file, payload)
        entries = payload.get("entries", {})
        if not isinstance(entries, dict):
            return {}
        entry = entries.get(entry_id, {})
        return entry if isinstance(entry, dict) else {}

    async def async_save_entry(self, entry_id: str, data: dict[str, Any]) -> None:
        """Persist the storage payload for a config entry."""
        async with self._lock:
            payload = await self.hass.async_add_executor_job(self._read_file)
            payload, _ = _normalize_storage_payload_for_entry(payload, entry_id)
            entries = payload["entries"]
            entries[entry_id] = data
            payload["version"] = _STORAGE_FILE_VERSION
            payload["updated_at"] = dt_util.utcnow().isoformat()
            await self.hass.async_add_executor_job(self._write_file, payload)

    def _read_file(self) -> dict[str, Any]:
        """Read the full JSON storage file from disk."""
        if not self.path.exists():
            return _empty_storage_payload()

        try:
            raw = self.path.read_bytes()
        except OSError as err:
            _LOGGER.warning("Unable to read DIVA runtime JSON at %s: %s", self.path, err)
            return _empty_storage_payload()

        try:
            payload, normalized = _load_json_payload(raw)
        except json.JSONDecodeError as err:
            _LOGGER.warning("Invalid DIVA runtime JSON at %s: %s", self.path, err)
            return _empty_storage_payload()

        if normalized != raw:
            _LOGGER.warning("Self-healing malformed DIVA runtime JSON at %s", self.path)
            self._write_file(payload)

        if isinstance(payload, dict):
            return payload
        _LOGGER.warning("Unexpected DIVA runtime JSON structure at %s", self.path)
        return _empty_storage_payload()

    def _write_file(self, data: dict[str, Any]) -> None:
        """Atomically write the full JSON storage file to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=True, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, self.path)


def _load_json_payload(raw: bytes) -> tuple[dict[str, Any], bytes]:
    """Parse and normalize possibly malformed runtime JSON bytes."""
    normalized = raw.rstrip(b"\x00")
    text = normalized.decode("utf-8")
    decoder = json.JSONDecoder()
    payload, end = decoder.raw_decode(text)
    trailing = text[end:].strip()
    if trailing:
        normalized = normalized[:end]
    return payload, json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def _empty_storage_payload() -> dict[str, Any]:
    """Return the canonical empty runtime storage payload."""
    return {
        "version": _STORAGE_FILE_VERSION,
        "entries": {},
    }


def _normalize_storage_payload_for_entry(
    payload: dict[str, Any],
    entry_id: str,
) -> tuple[dict[str, Any], bool]:
    """Normalize legacy runtime storage layouts into the canonical entries map."""
    canonical = _empty_storage_payload()
    migrated = False

    if not isinstance(payload, dict):
        return canonical, False

    updated_at = payload.get("updated_at")
    if isinstance(updated_at, str):
        canonical["updated_at"] = updated_at

    if _looks_like_runtime_entry_payload(payload):
        canonical["entries"] = {entry_id: payload}
        return canonical, True

    entries = payload.get("entries")
    if isinstance(entries, dict):
        canonical_entries: dict[str, dict[str, Any]] = {}
        for stored_entry_id, entry_payload in entries.items():
            if isinstance(entry_payload, dict):
                canonical_entries[str(stored_entry_id)] = entry_payload
            else:
                migrated = True
        canonical["entries"] = canonical_entries
        migrated = migrated or payload.get("version") != _STORAGE_FILE_VERSION
        return canonical, migrated

    legacy_entries = {
        str(stored_entry_id): entry_payload
        for stored_entry_id, entry_payload in payload.items()
        if stored_entry_id not in {"version", "updated_at"} and isinstance(entry_payload, dict)
    }
    if legacy_entries:
        canonical["entries"] = legacy_entries
        return canonical, True

    return canonical, bool(payload)


def _looks_like_runtime_entry_payload(payload: dict[str, Any]) -> bool:
    """Return whether the payload looks like a single runtime entry body."""
    return isinstance(payload.get("pets"), dict) or isinstance(payload.get("hub_name"), str)

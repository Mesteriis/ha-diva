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
        entries = payload.get("entries", {})
        if not isinstance(entries, dict):
            return {}
        entry = entries.get(entry_id, {})
        return entry if isinstance(entry, dict) else {}

    async def async_save_entry(self, entry_id: str, data: dict[str, Any]) -> None:
        """Persist the storage payload for a config entry."""
        async with self._lock:
            payload = await self.hass.async_add_executor_job(self._read_file)
            entries = payload.setdefault("entries", {})
            if not isinstance(entries, dict):
                entries = {}
                payload["entries"] = entries
            entries[entry_id] = data
            payload["version"] = 1
            payload["updated_at"] = dt_util.utcnow().isoformat()
            await self.hass.async_add_executor_job(self._write_file, payload)

    def _read_file(self) -> dict[str, Any]:
        """Read the full JSON storage file from disk."""
        if not self.path.exists():
            return {
                "version": 1,
                "entries": {},
            }

        try:
            raw = self.path.read_bytes()
        except OSError as err:
            _LOGGER.warning("Unable to read DIVA runtime JSON at %s: %s", self.path, err)
            return {
                "version": 1,
                "entries": {},
            }

        try:
            payload, normalized = _load_json_payload(raw)
        except json.JSONDecodeError as err:
            _LOGGER.warning("Invalid DIVA runtime JSON at %s: %s", self.path, err)
            return {
                "version": 1,
                "entries": {},
            }

        if normalized != raw:
            _LOGGER.warning("Self-healing malformed DIVA runtime JSON at %s", self.path)
            self._write_file(payload)

        if isinstance(payload, dict):
            return payload
        _LOGGER.warning("Unexpected DIVA runtime JSON structure at %s", self.path)
        return {
            "version": 1,
            "entries": {},
        }

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

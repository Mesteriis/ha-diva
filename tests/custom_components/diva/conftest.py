"""Minimal import stubs for pure DIVA unit tests."""

from __future__ import annotations

import enum
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

homeassistant = types.ModuleType("homeassistant")
config_entries = types.ModuleType("homeassistant.config_entries")
const = types.ModuleType("homeassistant.const")
core = types.ModuleType("homeassistant.core")
exceptions = types.ModuleType("homeassistant.exceptions")
helpers = types.ModuleType("homeassistant.helpers")
helpers_cv = types.ModuleType("homeassistant.helpers.config_validation")
helpers_dr = types.ModuleType("homeassistant.helpers.device_registry")
helpers_typing = types.ModuleType("homeassistant.helpers.typing")


class Platform(str, enum.Enum):
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    BUTTON = "button"
    NUMBER = "number"
    SELECT = "select"
    CAMERA = "camera"
    CALENDAR = "calendar"
    DEVICE_TRACKER = "device_tracker"


class ConfigEntry:
    pass


class HomeAssistant:
    pass


class ServiceCall:
    data: dict


class HomeAssistantError(Exception):
    pass


const.Platform = Platform
const.ATTR_DEVICE_ID = "device_id"
config_entries.ConfigEntry = ConfigEntry
core.HomeAssistant = HomeAssistant
core.ServiceCall = ServiceCall
exceptions.HomeAssistantError = HomeAssistantError
helpers_cv.string = str
helpers_dr.async_get = lambda hass: None
helpers_typing.ConfigType = dict

sys.modules.setdefault("homeassistant", homeassistant)
sys.modules.setdefault("homeassistant.config_entries", config_entries)
sys.modules.setdefault("homeassistant.const", const)
sys.modules.setdefault("homeassistant.core", core)
sys.modules.setdefault("homeassistant.exceptions", exceptions)
sys.modules.setdefault("homeassistant.helpers", helpers)
sys.modules.setdefault("homeassistant.helpers.config_validation", helpers_cv)
sys.modules.setdefault("homeassistant.helpers.device_registry", helpers_dr)
sys.modules.setdefault("homeassistant.helpers.typing", helpers_typing)

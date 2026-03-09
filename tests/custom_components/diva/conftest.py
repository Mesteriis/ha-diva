"""Minimal import stubs for pure DIVA unit tests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import enum
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

homeassistant = types.ModuleType("homeassistant")
config_entries = types.ModuleType("homeassistant.config_entries")
const = types.ModuleType("homeassistant.const")
core = types.ModuleType("homeassistant.core")
data_entry_flow = types.ModuleType("homeassistant.data_entry_flow")
exceptions = types.ModuleType("homeassistant.exceptions")
helpers = types.ModuleType("homeassistant.helpers")
helpers_cv = types.ModuleType("homeassistant.helpers.config_validation")
helpers_dr = types.ModuleType("homeassistant.helpers.device_registry")
helpers_entity = types.ModuleType("homeassistant.helpers.entity")
helpers_selector = types.ModuleType("homeassistant.helpers.selector")
helpers_storage = types.ModuleType("homeassistant.helpers.storage")
helpers_typing = types.ModuleType("homeassistant.helpers.typing")
helpers_update_coordinator = types.ModuleType("homeassistant.helpers.update_coordinator")
components = types.ModuleType("homeassistant.components")
components_binary_sensor = types.ModuleType("homeassistant.components.binary_sensor")
components_button = types.ModuleType("homeassistant.components.button")
components_camera = types.ModuleType("homeassistant.components.camera")
components_calendar = types.ModuleType("homeassistant.components.calendar")
components_calendar_const = types.ModuleType("homeassistant.components.calendar.const")
components_device_tracker = types.ModuleType("homeassistant.components.device_tracker")
components_device_tracker_config_entry = types.ModuleType("homeassistant.components.device_tracker.config_entry")
components_number = types.ModuleType("homeassistant.components.number")
components_select = types.ModuleType("homeassistant.components.select")
components_sensor = types.ModuleType("homeassistant.components.sensor")
util = types.ModuleType("homeassistant.util")
util_dt = types.ModuleType("homeassistant.util.dt")


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
    def __init__(self, *, data=None, options=None, title="DIVA") -> None:
        self.data = data or {}
        self.options = options or {}
        self.title = title


class ConfigFlow:
    def __init_subclass__(cls, **kwargs) -> None:
        return None

    async def async_set_unique_id(self, unique_id: str) -> None:
        self._unique_id = unique_id

    def _abort_if_unique_id_configured(self) -> None:
        return None

    def async_show_form(self, **kwargs):
        return {"type": "form", **kwargs}

    def async_create_entry(self, **kwargs):
        return {"type": "create_entry", **kwargs}

    def async_abort(self, **kwargs):
        return {"type": "abort", **kwargs}


class OptionsFlow:
    def async_show_form(self, **kwargs):
        return {"type": "form", **kwargs}

    def async_create_entry(self, **kwargs):
        return {"type": "create_entry", **kwargs}

    def async_abort(self, **kwargs):
        return {"type": "abort", **kwargs}


class HomeAssistant:
    pass


class ServiceCall:
    data: dict


class HomeAssistantError(Exception):
    pass


class DeviceEntryType(str, enum.Enum):
    SERVICE = "service"


class CalendarEntityFeature(enum.IntFlag):
    CREATE_EVENT = 1
    DELETE_EVENT = 2
    UPDATE_EVENT = 4


class Store:
    def __init__(self, *args, **kwargs) -> None:
        self._data = None

    async def async_load(self):
        return self._data


class DataUpdateCoordinator:
    def __class_getitem__(cls, item):
        return cls

    def __init__(self, *args, **kwargs) -> None:
        self.data = {}

    async def async_request_refresh(self) -> None:
        return None


class CoordinatorEntity:
    def __class_getitem__(cls, item):
        return cls

    def __init__(self, coordinator, context=None) -> None:
        self.coordinator = coordinator
        self.context = context

    @property
    def available(self) -> bool:
        return True


class DeviceInfo(dict):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class EntityCategory(str, enum.Enum):
    CONFIG = "config"
    DIAGNOSTIC = "diagnostic"


class _SelectorBase:
    def __init__(self, config=None) -> None:
        self.config = config

    def __call__(self, value):
        return value


class DateSelector(_SelectorBase):
    pass


class EntitySelector(_SelectorBase):
    pass


class EntitySelectorConfig(dict):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class NumberSelector(_SelectorBase):
    pass


class NumberSelectorConfig(dict):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class NumberSelectorMode(str, enum.Enum):
    BOX = "box"


class SelectOptionDict(dict):
    def __init__(self, *, value, label) -> None:
        super().__init__(value=value, label=label)
        self.value = value
        self.label = label


class SelectSelector(_SelectorBase):
    pass


class SelectSelectorConfig(dict):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class SelectSelectorMode(str, enum.Enum):
    DROPDOWN = "dropdown"


class TextSelector(_SelectorBase):
    pass


class TextSelectorConfig(dict):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class _EntityBase:
    pass


class SensorEntity(_EntityBase):
    pass


class BinarySensorEntity(_EntityBase):
    pass


class ButtonEntity(_EntityBase):
    pass


class NumberEntity(_EntityBase):
    pass


class SelectEntity(_EntityBase):
    pass


class Camera(_EntityBase):
    def __init__(self) -> None:
        return None


class CalendarEntity(_EntityBase):
    pass


class TrackerEntity(_EntityBase):
    pass


class SensorDeviceClass(str, enum.Enum):
    TIMESTAMP = "timestamp"


class BinarySensorDeviceClass(str, enum.Enum):
    PROBLEM = "problem"


class NumberMode(str, enum.Enum):
    BOX = "box"


class SourceType(str, enum.Enum):
    GPS = "gps"


@dataclass(frozen=True, kw_only=True)
class _DescriptionBase:
    key: str
    translation_key: str | None = None
    icon: str | None = None
    entity_category: EntityCategory | None = None
    device_class: object | None = None
    native_unit_of_measurement: str | None = None
    mode: object | None = None
    native_min_value: float | None = None
    native_max_value: float | None = None
    native_step: float | None = None


class SensorEntityDescription(_DescriptionBase):
    pass


class BinarySensorEntityDescription(_DescriptionBase):
    pass


class ButtonEntityDescription(_DescriptionBase):
    pass


class NumberEntityDescription(_DescriptionBase):
    pass


@dataclass(frozen=True, kw_only=True)
class CalendarEvent:
    start: object
    end: object
    summary: str
    description: str | None = None
    location: str | None = None
    uid: str | None = None


def selector(config):
    return {"selector": config}


def section(schema, options=None):
    return {"schema": schema, "options": options or {}}


def callback(func):
    return func


const.Platform = Platform
const.ATTR_DEVICE_ID = "device_id"
config_entries.ConfigEntry = ConfigEntry
config_entries.ConfigFlow = ConfigFlow
config_entries.ConfigFlowResult = dict
config_entries.OptionsFlow = OptionsFlow
core.HomeAssistant = HomeAssistant
core.ServiceCall = ServiceCall
core.callback = callback
exceptions.HomeAssistantError = HomeAssistantError
data_entry_flow.section = section
helpers_cv.string = str
helpers_dr.async_get = lambda hass: None
helpers_dr.DeviceEntryType = DeviceEntryType
helpers_entity.CoordinatorEntity = CoordinatorEntity
helpers_entity.DeviceInfo = DeviceInfo
helpers_entity.EntityCategory = EntityCategory
helpers_selector.DateSelector = DateSelector
helpers_selector.EntitySelector = EntitySelector
helpers_selector.EntitySelectorConfig = EntitySelectorConfig
helpers_selector.NumberSelector = NumberSelector
helpers_selector.NumberSelectorConfig = NumberSelectorConfig
helpers_selector.NumberSelectorMode = NumberSelectorMode
helpers_selector.SelectOptionDict = SelectOptionDict
helpers_selector.SelectSelector = SelectSelector
helpers_selector.SelectSelectorConfig = SelectSelectorConfig
helpers_selector.SelectSelectorMode = SelectSelectorMode
helpers_selector.TextSelector = TextSelector
helpers_selector.TextSelectorConfig = TextSelectorConfig
helpers_selector.selector = selector
helpers_storage.Store = Store
helpers_typing.ConfigType = dict
helpers_update_coordinator.DataUpdateCoordinator = DataUpdateCoordinator
helpers_update_coordinator.CoordinatorEntity = CoordinatorEntity
helpers.config_validation = helpers_cv
helpers.device_registry = helpers_dr
helpers.entity = helpers_entity
helpers.selector = helpers_selector
helpers.storage = helpers_storage
helpers.typing = helpers_typing
helpers.update_coordinator = helpers_update_coordinator
components_binary_sensor.BinarySensorDeviceClass = BinarySensorDeviceClass
components_binary_sensor.BinarySensorEntity = BinarySensorEntity
components_binary_sensor.BinarySensorEntityDescription = BinarySensorEntityDescription
components_button.ButtonEntity = ButtonEntity
components_button.ButtonEntityDescription = ButtonEntityDescription
components_camera.Camera = Camera
components_calendar.CalendarEntity = CalendarEntity
components_calendar.CalendarEvent = CalendarEvent
components_calendar_const.CalendarEntityFeature = CalendarEntityFeature
components_calendar_const.DATA_COMPONENT = "calendar_component"
components_calendar_const.EVENT_DESCRIPTION = "description"
components_calendar_const.EVENT_END = "end"
components_calendar_const.EVENT_LOCATION = "location"
components_calendar_const.EVENT_START = "start"
components_calendar_const.EVENT_SUMMARY = "summary"
components_device_tracker.SourceType = SourceType
components_device_tracker_config_entry.TrackerEntity = TrackerEntity
components_number.NumberEntity = NumberEntity
components_number.NumberEntityDescription = NumberEntityDescription
components_number.NumberMode = NumberMode
components_select.SelectEntity = SelectEntity
components_sensor.SensorDeviceClass = SensorDeviceClass
components_sensor.SensorEntity = SensorEntity
components_sensor.SensorEntityDescription = SensorEntityDescription
util_dt.now = lambda: datetime.now(timezone.utc)
util_dt.utcnow = lambda: datetime.now(timezone.utc)
util_dt.parse_date = lambda value: value if isinstance(value, date) else date.fromisoformat(str(value))
homeassistant.components = components
homeassistant.helpers = helpers
homeassistant.util = util
components.binary_sensor = components_binary_sensor
components.button = components_button
components.camera = components_camera
components.calendar = components_calendar
components.device_tracker = components_device_tracker
components.number = components_number
components.select = components_select
components.sensor = components_sensor
components_calendar.const = components_calendar_const
components_device_tracker.config_entry = components_device_tracker_config_entry
util.dt = util_dt

sys.modules.setdefault("homeassistant", homeassistant)
sys.modules.setdefault("homeassistant.config_entries", config_entries)
sys.modules.setdefault("homeassistant.const", const)
sys.modules.setdefault("homeassistant.core", core)
sys.modules.setdefault("homeassistant.data_entry_flow", data_entry_flow)
sys.modules.setdefault("homeassistant.exceptions", exceptions)
sys.modules.setdefault("homeassistant.helpers", helpers)
sys.modules.setdefault("homeassistant.helpers.config_validation", helpers_cv)
sys.modules.setdefault("homeassistant.helpers.device_registry", helpers_dr)
sys.modules.setdefault("homeassistant.helpers.entity", helpers_entity)
sys.modules.setdefault("homeassistant.helpers.selector", helpers_selector)
sys.modules.setdefault("homeassistant.helpers.storage", helpers_storage)
sys.modules.setdefault("homeassistant.helpers.typing", helpers_typing)
sys.modules.setdefault("homeassistant.helpers.update_coordinator", helpers_update_coordinator)
sys.modules.setdefault("homeassistant.components", components)
sys.modules.setdefault("homeassistant.components.binary_sensor", components_binary_sensor)
sys.modules.setdefault("homeassistant.components.button", components_button)
sys.modules.setdefault("homeassistant.components.camera", components_camera)
sys.modules.setdefault("homeassistant.components.calendar", components_calendar)
sys.modules.setdefault("homeassistant.components.calendar.const", components_calendar_const)
sys.modules.setdefault("homeassistant.components.device_tracker", components_device_tracker)
sys.modules.setdefault("homeassistant.components.device_tracker.config_entry", components_device_tracker_config_entry)
sys.modules.setdefault("homeassistant.components.number", components_number)
sys.modules.setdefault("homeassistant.components.select", components_select)
sys.modules.setdefault("homeassistant.components.sensor", components_sensor)
sys.modules.setdefault("homeassistant.util", util)
sys.modules.setdefault("homeassistant.util.dt", util_dt)

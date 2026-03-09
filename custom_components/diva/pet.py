"""Pure domain logic for the DIVA pet guardian integration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time, timedelta
import hashlib
import io
from math import asin, cos, pow, radians, sin, sqrt
from typing import Any, Iterable, Sequence

import numpy as np
from PIL import Image

from .const import (
    ANOMALY_GAIT,
    ANOMALY_COUGH,
    ANOMALY_LIMPING,
    ANOMALY_GEOFENCE_BREACH,
    ANOMALY_RESTLESSNESS,
    ANOMALY_SYMPTOM_ESCALATION,
    ANOMALY_VOMITING,
    CAMERA_EMPTY_SIMILARITY_THRESHOLD,
    CAMERA_EVENT_BEHAVIOR_OBSERVED,
    CAMERA_EVENT_BEHAVIOR_REPORTED,
    CAMERA_EVENT_CARE_LOGGED,
    CAMERA_EVENT_CALENDAR_CONFLICT,
    CAMERA_EVENT_CALENDAR_CONFLICT_RESOLVED,
    CAMERA_EVENT_CALENDAR_IMPORTED,
    CAMERA_EVENT_CHECKLIST_COMPLETED,
    CAMERA_EVENT_DRINKING,
    CAMERA_EVENT_EATING,
    CAMERA_EVENT_ACTION_APPROVED,
    CAMERA_EVENT_APPROVAL_REQUESTED,
    CAMERA_EVENT_GEOFENCE_BREACH,
    CAMERA_EVENT_GEOFENCE_CLEARED,
    CAMERA_EVENT_FOOD_EATEN,
    CAMERA_EVENT_FOOD_EMPTY,
    CAMERA_EVENT_FOOD_IGNORED,
    CAMERA_EVENT_FOOD_REFILLED,
    CAMERA_EVENT_ROOM_CHANGED,
    CAMERA_EVENT_FOOD_SERVED,
    CAMERA_EVENT_ROUTINE_DUE,
    CAMERA_EVENT_VET_DUE,
    CAMERA_EVENT_WALK_FINISHED,
    CAMERA_EVENT_WALK_STARTED,
    CAMERA_EVENT_WATER_EMPTY,
    CAMERA_EVENT_WATER_REFILLED,
    CAMERA_EVENT_ZONE_CHANGED,
    CAMERA_MOTION_THRESHOLD,
    CAMERA_TEXTURE_THRESHOLD,
    APPROVAL_ACTION_OPTIONS,
    CHECKLIST_FREQUENCIES,
    CHECKLIST_FREQUENCY_DAILY,
    CHECKLIST_FREQUENCY_WEEKLY,
    CALENDAR_CONFLICT_RESOLUTION_CALENDAR_WINS,
    CALENDAR_CONFLICT_RESOLUTION_DISMISS,
    CALENDAR_CONFLICT_RESOLUTION_DIVA_WINS,
    CALENDAR_SOURCE_OF_TRUTH_DIVA,
    CALENDAR_SOURCE_OF_TRUTH_OPTIONS,
    CONF_ACTION_NAME,
    CONF_ALLERGEN,
    CONF_ALLERGIES,
    CONF_APPROVAL_ID,
    CONF_APPROVAL_REQUIRED_ACTIONS,
    CONF_APPROVED_BY,
    CONF_AVATAR,
    CONF_BEHAVIOR_SIGNAL_ENTITY_IDS,
    CONF_BIRTHDATE,
    CONF_BREED,
    CONF_BLE_TRACKER_ENTITY_ID,
    CONF_BODY_CONDITION_SCORE,
    CONF_CAMERA_ROOM_NAME,
    CONF_CAMERA_ENTITY_ID,
    CONF_CALENDAR_ENTITY_ID,
    CONF_CALENDAR_LINKS,
    CONF_CAREGIVER,
    CONF_CARE_ROLES,
    CONF_CAREGIVERS,
    CONF_CARE_ROUTINES,
    CONF_CARE_SCHEDULE,
    CONF_CARE_SHIFTS,
    CONF_CHECKLIST_FREQUENCY,
    CONF_CHECKLIST_ITEMS,
    CONF_CHRONIC_CONDITIONS,
    CONF_COLD_THRESHOLD_C,
    CONF_CONTRAINDICATION,
    CONF_CONTRAINDICATIONS,
    CONF_CONDITION_NAME,
    CONF_CONDITION_STATUS,
    CONF_DEFAULT_MANUAL_MODE,
    CONF_DIAGNOSED_ON,
    CONF_DIAGNOSES,
    CONF_DIAGNOSIS_NAME,
    CONF_DIAGNOSIS_STATUS,
    CONF_DIET_MODE,
    CONF_DOSE,
    CONF_DURATION_HOURS,
    CONF_DUE_DATE,
    CONF_END_DATE,
    CONF_EXTERNAL_CALENDAR_ENTITY_IDS,
    CONF_FEEDING_SCHEDULE,
    CONF_FEEDING_ROUTINES,
    CONF_FOOD_BRAND,
    CONF_FOOD_BOWL_AREA,
    CONF_FOOD_CATALOG,
    CONF_FOOD_KIND,
    CONF_FOOD_NAME,
    CONF_FOOD_TRANSITION_PLAN,
    CONF_GPS_TRACKER_ENTITY_ID,
    CONF_HEAT_THRESHOLD_C,
    CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS,
    CONF_HUB_NAME,
    CONF_INSURANCE_POLICY,
    CONF_HISTORY_CATEGORY,
    CONF_HISTORY_DATE,
    CONF_HISTORY_TITLE,
    CONF_MEDICAL_COUNTRY,
    CONF_MEDICAL_HISTORY,
    CONF_MEDICAL_REGION,
    CONF_MEDICATION_COURSES,
    CONF_MEDICATION_NAME,
    CONF_MEDICATION_ROUTE,
    CONF_MEDICATION_TIMES,
    CONF_MICROCHIP_ID,
    CONF_MONITOR_INTERVAL_DAYS,
    CONF_NAME,
    CONF_NOTES,
    CONF_PASSPORT_NUMBER,
    CONF_PETS,
    CONF_PET_ID,
    CONF_PET_SCHEMA,
    CONF_PET_SECTION_ANALYTICS,
    CONF_PET_SECTION_EXTERNAL_LINKS,
    CONF_PET_SECTION_MEDICAL,
    CONF_PET_SECTION_PLAN,
    CONF_PET_SECTION_PROFILE,
    CONF_PRIMARY_VET,
    CONF_REGIONAL_POLICY,
    CONF_REQUIRES_APPROVAL,
    CONF_ROLE,
    CONF_ROOM_MATCH_STATE,
    CONF_ROOM_NAME,
    CONF_ROOM_PRESENCE_SOURCES,
    CONF_ROOM_SOURCE_PRIORITY,
    CONF_REASON,
    CONF_RECURRENCE_MONTHS,
    CONF_REACTION,
    CONF_ROUTINE_CATEGORY,
    CONF_ROUTINE_DAYS,
    CONF_ROUTINE_DURATION_MINUTES,
    CONF_ROUTINE_EXCEPTION_ACTION,
    CONF_ROUTINE_EXCEPTION_DATE,
    CONF_ROUTINE_EXCEPTION_TIME,
    CONF_ROUTINE_EXCEPTIONS,
    CONF_ROUTINE_LABEL,
    CONF_ROUTINE_LOCATION,
    CONF_ROUTINE_MEAL_TYPE,
    CONF_ROUTINE_PORTION_GRAMS,
    CONF_ROUTINE_TIME,
    CONF_SHIFT_END_TIME,
    CONF_SHIFT_START_TIME,
    CONF_SHOW_EDITOR_IN_SIDEBAR,
    CONF_SOURCE_OF_TRUTH,
    CONF_SPECIES,
    CONF_START_DATE,
    CONF_TO_FOOD_NAME,
    CONF_TO_PERCENT,
    CONF_TRANSITION_DATE,
    CONF_VACCINE_PROFILE,
    CONF_VACCINE_OVERRIDES,
    CONF_VACCINE_STATUS,
    CONF_VACCINE_DOSE_ID,
    CONF_VACCINE_NAME,
    CONF_VET_OVERRIDE,
    CONF_VET_APPOINTMENTS,
    CONF_VET_PHONE,
    CONF_WALK_SCHEDULE,
    CONF_WALK_ROUTINES,
    CONF_WATER_BOWL_AREA,
    CONF_SAFE_ZONES,
    CONF_WEATHER_ADAPTATION,
    CONF_WEATHER_ENTITY_ID,
    CONF_WEIGHT,
    CONF_WEIGHT_GOAL_MAX_KG,
    CONF_WEIGHT_GOAL_MIN_KG,
    CONF_ZONE_LATITUDE,
    CONF_ZONE_LONGITUDE,
    CONF_ZONE_NAME,
    CONF_ZONE_RADIUS_M,
    CONF_KCAL_PER_GRAM,
    CONF_FROM_FOOD_NAME,
    CONF_FROM_PERCENT,
    DEFAULT_BODY_CONDITION_SCORE,
    DEFAULT_KCAL_PER_GRAM,
    DEFAULT_COLD_THRESHOLD_C,
    DAILY_HISTORY_LIMIT,
    DEFAULT_CARE_DURATION_MINUTES,
    DEFAULT_DAILY_WATER_PER_KG_ML,
    DEFAULT_FEEDING_DURATION_MINUTES,
    DEFAULT_FEEDING_SCHEDULES,
    DEFAULT_FOOD_IGNORE_MINUTES,
    DEFAULT_HEAT_THRESHOLD_C,
    DEFAULT_INTERACTION_COOLDOWN_MINUTES,
    DEFAULT_SLEEP_AFTER_MINUTES,
    DEFAULT_VET_DURATION_MINUTES,
    DEFAULT_WALK_DURATION_MINUTES,
    DEFAULT_WATER_SIP_ML,
    DEFAULT_WEIGHT_GOAL_MARGIN_KG,
    DIET_MODES,
    DIET_MODE_ADULT,
    FOOD_KIND_MAIN,
    FOOD_KIND_MEDICAL,
    FOOD_KIND_SUPPLEMENTS,
    FOOD_KIND_TREATS,
    FOOD_KINDS,
    JOURNAL_RECORD_LIMIT,
    MEAL_TYPE_DRY,
    MEAL_TYPE_MEDICATION,
    MEAL_TYPE_SUPPLEMENT,
    MEAL_TYPE_TREAT,
    MEAL_TYPES,
    OPERATION_MODE_ILLNESS,
    OPERATION_MODE_NORMAL,
    OPERATION_MODE_VACATION,
    RECENT_RECORD_LIMIT,
    ROUTINE_CATEGORIES,
    ROUTINE_EXCEPTION_ACTIONS,
    ROUTINE_EXCEPTION_ADD,
    ROUTINE_EXCEPTION_MOVE,
    ROUTINE_EXCEPTION_SKIP,
    ROUTINE_TYPE_CARE,
    ROUTINE_TYPE_FEED,
    ROUTINE_TYPE_GROOMING,
    ROUTINE_TYPE_MEDICATION,
    ROUTINE_TYPE_PLAY,
    ROUTINE_TYPE_TRAINING,
    ROUTINE_TYPE_VET,
    ROUTINE_TYPE_WALK,
    SCHEDULE_DUE_WINDOW_MINUTES,
    PET_SCHEMA_VERSION,
    VACCINE_PROFILE_AUTO,
    VACCINE_PROFILE_DOG_DEFAULT,
    VACCINE_PROFILE_OPTIONS,
    VACCINE_PROFILE_SPAIN_DOG_DEFAULT,
    VET_REMINDER_WINDOW_MINUTES,
    DEFAULT_MEDICAL_COUNTRY,
    DEFAULT_MEDICAL_REGION,
)

try:
    import cv2  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    cv2 = None

ALL_WEEKDAYS = (0, 1, 2, 3, 4, 5, 6)
WEEKDAY_ALIASES: dict[str, tuple[int, ...]] = {
    "mon": (0,),
    "monday": (0,),
    "tue": (1,),
    "tues": (1,),
    "tuesday": (1,),
    "wed": (2,),
    "wednesday": (2,),
    "thu": (3,),
    "thurs": (3,),
    "thursday": (3,),
    "fri": (4,),
    "friday": (4,),
    "sat": (5,),
    "saturday": (5,),
    "sun": (6,),
    "sunday": (6,),
    "daily": ALL_WEEKDAYS,
    "everyday": ALL_WEEKDAYS,
    "weekdays": (0, 1, 2, 3, 4),
    "weekends": (5, 6),
}


@dataclass(slots=True)
class BowlArea:
    """A rectangular bowl area in a camera frame."""

    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_value(cls, value: str | dict[str, Any] | None) -> BowlArea | None:
        """Parse a bowl area from a user supplied value."""
        if value in (None, "", {}):
            return None
        if isinstance(value, dict):
            try:
                return cls(
                    x=int(value["x"]),
                    y=int(value["y"]),
                    width=int(value["width"]),
                    height=int(value["height"]),
                )
            except (KeyError, TypeError, ValueError) as err:
                raise ValueError("Invalid bowl area mapping") from err

        parts = [part.strip() for part in value.split(",")]
        if len(parts) != 4:
            raise ValueError("Area must use x,y,width,height format")
        try:
            x, y, width, height = (int(part) for part in parts)
        except ValueError as err:
            raise ValueError("Area must contain integers") from err
        if min(x, y, width, height) < 0 or width == 0 or height == 0:
            raise ValueError("Area values must be positive")
        return cls(x=x, y=y, width=width, height=height)

    def as_dict(self) -> dict[str, int]:
        """Return the area as a dictionary."""
        return asdict(self)

    def crop(self, frame: np.ndarray | None) -> np.ndarray | None:
        """Crop this region from the provided frame."""
        if frame is None:
            return None
        max_y, max_x = frame.shape[:2]
        start_x = max(0, min(self.x, max_x))
        start_y = max(0, min(self.y, max_y))
        end_x = max(start_x, min(self.x + self.width, max_x))
        end_y = max(start_y, min(self.y + self.height, max_y))
        if end_x - start_x < 2 or end_y - start_y < 2:
            return None
        return frame[start_y:end_y, start_x:end_x]


@dataclass(slots=True)
class RoutineEntry:
    """A recurring daily/weekly routine entry."""

    routine_id: str
    category: str
    time_of_day: time
    label: str
    duration_minutes: int
    weekdays: tuple[int, ...] = ALL_WEEKDAYS
    meal_type: str | None = None
    portion_grams: float | None = None
    location: str | None = None
    notes: str | None = None

    def occurs_on(self, day: date) -> bool:
        """Return if the routine applies on the given day."""
        return day.weekday() in self.weekdays

    def as_dict(self) -> dict[str, Any]:
        """Serialize the routine for config storage."""
        payload: dict[str, Any] = {
            CONF_ROUTINE_TIME: self.time_of_day.strftime("%H:%M"),
            CONF_ROUTINE_DAYS: [_weekday_name(value) for value in self.weekdays],
            CONF_ROUTINE_LABEL: self.label,
            CONF_ROUTINE_DURATION_MINUTES: self.duration_minutes,
        }
        if self.category not in {ROUTINE_TYPE_FEED, ROUTINE_TYPE_WALK, ROUTINE_TYPE_CARE}:
            payload[CONF_ROUTINE_CATEGORY] = self.category
        if self.meal_type is not None:
            payload[CONF_ROUTINE_MEAL_TYPE] = self.meal_type
        if self.portion_grams is not None:
            payload[CONF_ROUTINE_PORTION_GRAMS] = self.portion_grams
        if self.location is not None:
            payload[CONF_ROUTINE_LOCATION] = self.location
        if self.notes is not None:
            payload[CONF_NOTES] = self.notes
        return payload

    def occurrence(self, pet_id: str, day: date, tzinfo) -> ScheduledEvent:
        """Build a concrete scheduled event for a day."""
        start = datetime.combine(day, self.time_of_day, tzinfo=tzinfo)
        end = start + timedelta(minutes=max(1, self.duration_minutes))
        summary = self.label
        description_parts: list[str] = [f"Routine: {self.category}"]
        if self.meal_type:
            description_parts.append(f"Meal type: {self.meal_type}")
        if self.portion_grams is not None:
            description_parts.append(f"Portion: {self.portion_grams} g")
        if self.notes:
            description_parts.append(self.notes)
        return ScheduledEvent(
            event_id=f"{self.routine_id}:{day.isoformat()}",
            pet_id=pet_id,
            category=self.category,
            summary=summary,
            start=start,
            end=end,
            description="\n".join(description_parts),
            location=self.location,
            metadata={
                "routine_id": self.routine_id,
                "weekdays": list(self.weekdays),
                "meal_type": self.meal_type,
                "portion_grams": self.portion_grams,
            },
        )


@dataclass(slots=True)
class AppointmentEntry:
    """A dated appointment such as a vet visit."""

    appointment_id: str
    category: str
    starts_at: datetime
    label: str
    duration_minutes: int
    location: str | None = None
    notes: str | None = None

    def to_event(self, pet_id: str, tzinfo) -> ScheduledEvent:
        """Convert the appointment into a scheduled event."""
        start = _ensure_tz(self.starts_at, tzinfo)
        end = start + timedelta(minutes=max(1, self.duration_minutes))
        description_parts = [f"Appointment: {self.category}"]
        if self.notes:
            description_parts.append(self.notes)
        return ScheduledEvent(
            event_id=self.appointment_id,
            pet_id=pet_id,
            category=self.category,
            summary=self.label,
            start=start,
            end=end,
            description="\n".join(description_parts),
            location=self.location,
            metadata={"appointment_id": self.appointment_id},
        )


@dataclass(slots=True)
class ScheduledEvent:
    """A concrete scheduled timeline event."""

    event_id: str
    pet_id: str
    category: str
    summary: str
    start: datetime
    end: datetime
    description: str = ""
    location: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Serialize the scheduled event."""
        return {
            "event_id": self.event_id,
            "pet_id": self.pet_id,
            "category": self.category,
            "summary": self.summary,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "description": self.description,
            "location": self.location,
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class SafeZone:
    """A named circular safe zone for GPS tracking."""

    zone_id: str
    name: str
    latitude: float
    longitude: float
    radius_m: float

    def contains(self, latitude: float, longitude: float) -> bool:
        """Return whether the point is inside the zone radius."""
        return _haversine_m(self.latitude, self.longitude, latitude, longitude) <= self.radius_m

    def distance_m(self, latitude: float, longitude: float) -> float:
        """Return the point distance to the zone center in meters."""
        return round(_haversine_m(self.latitude, self.longitude, latitude, longitude), 1)

    def as_dict(self) -> dict[str, Any]:
        """Serialize the safe zone."""
        return {
            CONF_ZONE_NAME: self.name,
            CONF_ZONE_LATITUDE: round(self.latitude, 6),
            CONF_ZONE_LONGITUDE: round(self.longitude, 6),
            CONF_ZONE_RADIUS_M: round(self.radius_m, 1),
        }


@dataclass(slots=True)
class RoomPresenceSource:
    """A room signal source used to resolve indoor presence."""

    room_name: str
    entity_id: str
    match_state: str | None = None
    priority: int = 1

    def as_dict(self) -> dict[str, Any]:
        """Serialize the room source."""
        payload: dict[str, Any] = {
            CONF_ROOM_NAME: self.room_name,
            "entity_id": self.entity_id,
            CONF_ROOM_SOURCE_PRIORITY: self.priority,
        }
        if self.match_state is not None:
            payload[CONF_ROOM_MATCH_STATE] = self.match_state
        return payload


@dataclass(slots=True)
class CareRole:
    """A caregiver role assignment."""

    caregiver: str
    role: str
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the caregiver role."""
        payload: dict[str, Any] = {
            CONF_CAREGIVER: self.caregiver,
            CONF_ROLE: self.role,
        }
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload


@dataclass(slots=True)
class CareShift:
    """A weekly recurring caregiver shift."""

    shift_id: str
    label: str
    caregiver: str
    role: str | None
    start_time: time
    end_time: time
    weekdays: tuple[int, ...] = ALL_WEEKDAYS
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the caregiver shift."""
        payload: dict[str, Any] = {
            CONF_ROUTINE_LABEL: self.label,
            CONF_CAREGIVER: self.caregiver,
            CONF_SHIFT_START_TIME: self.start_time.strftime("%H:%M"),
            CONF_SHIFT_END_TIME: self.end_time.strftime("%H:%M"),
            CONF_ROUTINE_DAYS: [_weekday_name(value) for value in self.weekdays],
        }
        if self.role:
            payload[CONF_ROLE] = self.role
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload

    def is_active(self, when: datetime) -> bool:
        """Return whether the shift is active at the given time."""
        if when.weekday() not in self.weekdays:
            return False
        current = when.timetz().replace(tzinfo=None)
        if self.start_time <= self.end_time:
            return self.start_time <= current < self.end_time
        return current >= self.start_time or current < self.end_time

    def next_start(self, when: datetime) -> datetime | None:
        """Return the next shift start after the given time."""
        tzinfo = when.tzinfo
        for offset in range(0, 8):
            day = when.date() + timedelta(days=offset)
            if day.weekday() not in self.weekdays:
                continue
            candidate = datetime.combine(day, self.start_time, tzinfo=tzinfo)
            if candidate > when:
                return candidate
        return None


@dataclass(slots=True)
class ChecklistItem:
    """A recurring operational checklist item."""

    checklist_id: str
    label: str
    frequency: str
    category: str
    caregiver: str | None = None
    requires_approval: bool = False
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the checklist item."""
        payload: dict[str, Any] = {
            CONF_ROUTINE_LABEL: self.label,
            CONF_CHECKLIST_FREQUENCY: self.frequency,
            CONF_ROUTINE_CATEGORY: self.category,
            CONF_REQUIRES_APPROVAL: self.requires_approval,
        }
        if self.caregiver:
            payload[CONF_CAREGIVER] = self.caregiver
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload


@dataclass(slots=True)
class FoodCatalogEntry:
    """A configured food item available for the pet."""

    name: str
    brand: str | None = None
    kind: str = FOOD_KIND_MAIN
    meal_type: str = MEAL_TYPE_DRY
    kcal_per_gram: float = DEFAULT_KCAL_PER_GRAM
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the food entry."""
        payload: dict[str, Any] = {
            CONF_FOOD_NAME: self.name,
            CONF_FOOD_KIND: self.kind,
            CONF_ROUTINE_MEAL_TYPE: self.meal_type,
            CONF_KCAL_PER_GRAM: self.kcal_per_gram,
        }
        if self.brand:
            payload[CONF_FOOD_BRAND] = self.brand
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload


@dataclass(slots=True)
class FoodTransitionStep:
    """A dated transition step between two foods."""

    transition_date: date
    from_food_name: str
    to_food_name: str
    from_percent: int
    to_percent: int
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the transition step."""
        payload: dict[str, Any] = {
            CONF_TRANSITION_DATE: self.transition_date.isoformat(),
            CONF_FROM_FOOD_NAME: self.from_food_name,
            CONF_TO_FOOD_NAME: self.to_food_name,
            CONF_FROM_PERCENT: self.from_percent,
            CONF_TO_PERCENT: self.to_percent,
        }
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload

    def summary(self) -> str:
        """Return a human-readable transition summary."""
        return f"{self.from_food_name} {self.from_percent}% -> {self.to_food_name} {self.to_percent}%"


@dataclass(slots=True)
class MedicationCourse:
    """A medication course with dated administration slots."""

    medication_id: str
    name: str
    dose: str
    times: tuple[time, ...]
    start_date: date
    end_date: date | None = None
    route: str | None = None
    notes: str | None = None

    def is_active_on(self, day: date) -> bool:
        """Return whether the medication course is active on a day."""
        if day < self.start_date:
            return False
        if self.end_date is not None and day > self.end_date:
            return False
        return True

    def occurrences(self, pet_id: str, start: datetime, end: datetime) -> list[ScheduledEvent]:
        """Return concrete medication reminders for a time window."""
        tzinfo = start.tzinfo or end.tzinfo
        if tzinfo is None:
            return []
        events: list[ScheduledEvent] = []
        current_day = start.date()
        while current_day <= end.date():
            if self.is_active_on(current_day):
                for slot in self.times:
                    starts_at = datetime.combine(current_day, slot, tzinfo=tzinfo)
                    ends_at = starts_at + timedelta(minutes=10)
                    if starts_at < end and ends_at > start:
                        description = [f"Medication: {self.name}", f"Dose: {self.dose}"]
                        if self.route:
                            description.append(f"Route: {self.route}")
                        if self.notes:
                            description.append(self.notes)
                        events.append(
                            ScheduledEvent(
                                event_id=f"{self.medication_id}:{current_day.isoformat()}:{slot.strftime('%H%M')}",
                                pet_id=pet_id,
                                category=ROUTINE_TYPE_MEDICATION,
                                summary=f"{self.name} dose",
                                start=starts_at,
                                end=ends_at,
                                description="\n".join(description),
                                metadata={
                                    "medication_id": self.medication_id,
                                    "medication_name": self.name,
                                    "dose": self.dose,
                                },
                            )
                        )
            current_day += timedelta(days=1)
        return events

    def as_dict(self) -> dict[str, Any]:
        """Serialize the medication course."""
        payload: dict[str, Any] = {
            CONF_MEDICATION_NAME: self.name,
            CONF_DOSE: self.dose,
            CONF_MEDICATION_TIMES: ", ".join(slot.strftime("%H:%M") for slot in self.times),
            CONF_START_DATE: self.start_date.isoformat(),
        }
        if self.end_date is not None:
            payload[CONF_END_DATE] = self.end_date.isoformat()
        if self.route:
            payload[CONF_MEDICATION_ROUTE] = self.route
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload


@dataclass(slots=True)
class ChronicCondition:
    """A chronic condition that requires ongoing monitoring."""

    name: str
    status: str = "monitoring"
    monitor_interval_days: int = 30
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the chronic condition."""
        payload: dict[str, Any] = {
            CONF_CONDITION_NAME: self.name,
            CONF_CONDITION_STATUS: self.status,
            CONF_MONITOR_INTERVAL_DAYS: self.monitor_interval_days,
        }
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload


@dataclass(slots=True)
class DiagnosisEntry:
    """A structured medical diagnosis."""

    name: str
    status: str = "active"
    diagnosed_on: date | None = None
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the diagnosis entry."""
        payload: dict[str, Any] = {
            CONF_DIAGNOSIS_NAME: self.name,
            CONF_DIAGNOSIS_STATUS: self.status,
        }
        if self.diagnosed_on is not None:
            payload[CONF_DIAGNOSED_ON] = self.diagnosed_on.isoformat()
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload


@dataclass(slots=True)
class AllergyEntry:
    """A structured allergy entry."""

    allergen: str
    reaction: str | None = None
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the allergy entry."""
        payload: dict[str, Any] = {
            CONF_ALLERGEN: self.allergen,
        }
        if self.reaction:
            payload[CONF_REACTION] = self.reaction
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload


@dataclass(slots=True)
class ContraindicationEntry:
    """A structured contraindication entry."""

    item: str
    reason: str | None = None
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the contraindication entry."""
        payload: dict[str, Any] = {
            CONF_CONTRAINDICATION: self.item,
        }
        if self.reason:
            payload[CONF_REASON] = self.reason
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload


@dataclass(slots=True)
class MedicalHistoryEntry:
    """A dated medical history record."""

    history_date: date
    title: str
    category: str = "general"
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the history entry."""
        payload: dict[str, Any] = {
            CONF_HISTORY_DATE: self.history_date.isoformat(),
            CONF_HISTORY_TITLE: self.title,
            CONF_HISTORY_CATEGORY: self.category,
        }
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload


@dataclass(slots=True)
class VaccinePlanEntry:
    """A default or custom vaccine schedule entry."""

    dose_id: str
    vaccine_name: str
    due_date: date
    category: str
    source: str
    recurrence_months: int | None = None
    notes: str | None = None

    def next_due_date(self, completed_at: date | None) -> date | None:
        """Return the next due date for this vaccine entry."""
        if completed_at is None:
            return self.due_date
        if self.recurrence_months is None:
            return None
        return _add_months(completed_at, self.recurrence_months)

    def to_event(self, pet_id: str, tzinfo, completed_at: date | None) -> ScheduledEvent | None:
        """Convert the vaccine entry into a scheduled event."""
        next_due = self.next_due_date(completed_at)
        if next_due is None:
            return None
        starts_at = datetime.combine(next_due, time(hour=9), tzinfo=tzinfo)
        ends_at = starts_at + timedelta(minutes=DEFAULT_VET_DURATION_MINUTES)
        description = [f"Vaccine: {self.vaccine_name}", f"Protocol: {self.source}"]
        if self.notes:
            description.append(self.notes)
        return ScheduledEvent(
            event_id=f"vaccine:{self.dose_id}",
            pet_id=pet_id,
            category=ROUTINE_TYPE_VET,
            summary=self.vaccine_name,
            start=starts_at,
            end=ends_at,
            description="\n".join(description),
            metadata={
                "vaccine_dose_id": self.dose_id,
                "vaccine_name": self.vaccine_name,
                "vaccine_category": self.category,
                "vaccine_source": self.source,
            },
        )

    def as_dict(self) -> dict[str, Any]:
        """Serialize the vaccine plan entry."""
        payload: dict[str, Any] = {
            CONF_VACCINE_DOSE_ID: self.dose_id,
            CONF_VACCINE_NAME: self.vaccine_name,
            CONF_DUE_DATE: self.due_date.isoformat(),
            CONF_ROUTINE_CATEGORY: self.category,
            "source": self.source,
        }
        if self.recurrence_months is not None:
            payload[CONF_RECURRENCE_MONTHS] = self.recurrence_months
        if self.notes:
            payload[CONF_NOTES] = self.notes
        return payload


@dataclass(slots=True)
class ScheduleException:
    """A date-bound override for the regular routine plan."""

    exception_id: str
    exception_date: date
    action: str
    category: str
    label: str | None = None
    time_of_day: time | None = None
    duration_minutes: int | None = None
    meal_type: str | None = None
    portion_grams: float | None = None
    location: str | None = None
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the exception into config/runtime storage."""
        payload: dict[str, Any] = {
            CONF_ROUTINE_EXCEPTION_DATE: self.exception_date.isoformat(),
            CONF_ROUTINE_EXCEPTION_ACTION: self.action,
            CONF_ROUTINE_CATEGORY: self.category,
        }
        if self.label:
            payload[CONF_ROUTINE_LABEL] = self.label
        if self.time_of_day is not None:
            payload[CONF_ROUTINE_EXCEPTION_TIME] = self.time_of_day.strftime("%H:%M")
        if self.duration_minutes is not None:
            payload[CONF_ROUTINE_DURATION_MINUTES] = self.duration_minutes
        if self.meal_type is not None:
            payload[CONF_ROUTINE_MEAL_TYPE] = self.meal_type
        if self.portion_grams is not None:
            payload[CONF_ROUTINE_PORTION_GRAMS] = self.portion_grams
        if self.location is not None:
            payload[CONF_ROUTINE_LOCATION] = self.location
        if self.notes is not None:
            payload[CONF_NOTES] = self.notes
        return payload

    def to_event(self, pet_id: str, tzinfo) -> ScheduledEvent | None:
        """Convert an add/move exception to a one-off scheduled event."""
        if self.action not in {ROUTINE_EXCEPTION_ADD, ROUTINE_EXCEPTION_MOVE} or self.time_of_day is None:
            return None
        duration = self.duration_minutes or _default_duration_for_category(self.category)
        start = datetime.combine(self.exception_date, self.time_of_day, tzinfo=tzinfo)
        end = start + timedelta(minutes=max(1, duration))
        summary = self.label or _default_label_for_category(self.category)
        description_parts = [f"Exception: {self.action}", f"Routine: {self.category}"]
        if self.meal_type:
            description_parts.append(f"Meal type: {self.meal_type}")
        if self.portion_grams is not None:
            description_parts.append(f"Portion: {self.portion_grams} g")
        if self.notes:
            description_parts.append(self.notes)
        return ScheduledEvent(
            event_id=f"{self.exception_id}:{self.exception_date.isoformat()}",
            pet_id=pet_id,
            category=self.category,
            summary=summary,
            start=start,
            end=end,
            description="\n".join(description_parts),
            location=self.location,
            metadata={
                "exception_id": self.exception_id,
                "exception_action": self.action,
                "exception_date": self.exception_date.isoformat(),
            },
        )


@dataclass(slots=True)
class CalendarLink:
    """Calendar sync configuration for a linked external calendar."""

    calendar_entity_id: str
    source_of_truth: str = CALENDAR_SOURCE_OF_TRUTH_DIVA

    def as_dict(self) -> dict[str, Any]:
        """Serialize the calendar link."""
        return {
            CONF_CALENDAR_ENTITY_ID: self.calendar_entity_id,
            CONF_SOURCE_OF_TRUTH: self.source_of_truth,
        }


@dataclass(slots=True)
class PetProfileSection:
    """Identity/profile section for v3 pet config records."""

    pet_id: str
    name: str
    species: str
    breed: str
    birthdate: str
    weight: float
    diet_mode: str
    avatar: str | None = None

    @classmethod
    def from_flat_dict(cls, data: dict[str, Any]) -> PetProfileSection:
        """Build the section from a flat pet dict."""
        return cls(
            pet_id=str(data[CONF_PET_ID]),
            name=str(data[CONF_NAME]),
            species=str(data[CONF_SPECIES]),
            breed=str(data[CONF_BREED]),
            birthdate=str(data[CONF_BIRTHDATE]),
            weight=float(data[CONF_WEIGHT]),
            diet_mode=str(data[CONF_DIET_MODE]),
            avatar=normalize_avatar_reference(data.get(CONF_AVATAR)),
        )

    def as_dict(self) -> dict[str, Any]:
        """Serialize the section."""
        return {
            CONF_PET_ID: self.pet_id,
            CONF_NAME: self.name,
            CONF_SPECIES: self.species,
            CONF_BREED: self.breed,
            CONF_BIRTHDATE: self.birthdate,
            CONF_WEIGHT: self.weight,
            CONF_DIET_MODE: self.diet_mode,
            CONF_AVATAR: self.avatar,
        }


@dataclass(slots=True)
class PetPlanSection:
    """Planning section for v3 pet config records."""

    feeding_schedule: str = ""
    walk_schedule: str = ""
    care_schedule: str = ""
    vet_appointments: str = ""
    caregivers: str = ""
    feeding_routines: list[dict[str, Any]] = field(default_factory=list)
    walk_routines: list[dict[str, Any]] = field(default_factory=list)
    care_routines: list[dict[str, Any]] = field(default_factory=list)
    routine_exceptions: list[dict[str, Any]] = field(default_factory=list)
    care_roles: list[dict[str, Any]] = field(default_factory=list)
    care_shifts: list[dict[str, Any]] = field(default_factory=list)
    checklist_items: list[dict[str, Any]] = field(default_factory=list)
    approval_required_actions: list[str] = field(default_factory=list)
    default_manual_mode: str = OPERATION_MODE_NORMAL
    food_catalog: list[dict[str, Any]] = field(default_factory=list)
    food_transition_plan: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_flat_dict(cls, data: dict[str, Any]) -> PetPlanSection:
        """Build the section from a flat pet dict."""
        return cls(
            feeding_schedule=_normalize_multiline_text(data.get(CONF_FEEDING_SCHEDULE)),
            walk_schedule=_normalize_multiline_text(data.get(CONF_WALK_SCHEDULE)),
            care_schedule=_normalize_multiline_text(data.get(CONF_CARE_SCHEDULE)),
            vet_appointments=_normalize_multiline_text(data.get(CONF_VET_APPOINTMENTS)),
            caregivers=_normalize_multiline_text(data.get(CONF_CAREGIVERS)),
            feeding_routines=list(data.get(CONF_FEEDING_ROUTINES, []) or []),
            walk_routines=list(data.get(CONF_WALK_ROUTINES, []) or []),
            care_routines=list(data.get(CONF_CARE_ROUTINES, []) or []),
            routine_exceptions=list(data.get(CONF_ROUTINE_EXCEPTIONS, []) or []),
            care_roles=list(data.get(CONF_CARE_ROLES, []) or []),
            care_shifts=list(data.get(CONF_CARE_SHIFTS, []) or []),
            checklist_items=list(data.get(CONF_CHECKLIST_ITEMS, []) or []),
            approval_required_actions=list(data.get(CONF_APPROVAL_REQUIRED_ACTIONS, []) or []),
            default_manual_mode=_parse_manual_mode(data.get(CONF_DEFAULT_MANUAL_MODE)),
            food_catalog=list(data.get(CONF_FOOD_CATALOG, []) or []),
            food_transition_plan=list(data.get(CONF_FOOD_TRANSITION_PLAN, []) or []),
        )

    def as_dict(self) -> dict[str, Any]:
        """Serialize the section."""
        return {
            CONF_FEEDING_SCHEDULE: self.feeding_schedule,
            CONF_WALK_SCHEDULE: self.walk_schedule,
            CONF_CARE_SCHEDULE: self.care_schedule,
            CONF_VET_APPOINTMENTS: self.vet_appointments,
            CONF_CAREGIVERS: self.caregivers,
            CONF_FEEDING_ROUTINES: self.feeding_routines,
            CONF_WALK_ROUTINES: self.walk_routines,
            CONF_CARE_ROUTINES: self.care_routines,
            CONF_ROUTINE_EXCEPTIONS: self.routine_exceptions,
            CONF_CARE_ROLES: self.care_roles,
            CONF_CARE_SHIFTS: self.care_shifts,
            CONF_CHECKLIST_ITEMS: self.checklist_items,
            CONF_APPROVAL_REQUIRED_ACTIONS: self.approval_required_actions,
            CONF_DEFAULT_MANUAL_MODE: self.default_manual_mode,
            CONF_FOOD_CATALOG: self.food_catalog,
            CONF_FOOD_TRANSITION_PLAN: self.food_transition_plan,
        }


@dataclass(slots=True)
class PetMedicalSection:
    """Medical section for v3 pet config records."""

    medical_country: str = DEFAULT_MEDICAL_COUNTRY
    medical_region: str = DEFAULT_MEDICAL_REGION
    regional_policy: str = DEFAULT_MEDICAL_REGION
    vaccine_profile: str = VACCINE_PROFILE_AUTO
    vet_override: bool = True
    body_condition_score: float = DEFAULT_BODY_CONDITION_SCORE
    weight_goal_min_kg: float | None = None
    weight_goal_max_kg: float | None = None
    passport_number: str | None = None
    microchip_id: str | None = None
    insurance_policy: str | None = None
    primary_vet: str | None = None
    vet_phone: str | None = None
    medication_courses: list[dict[str, Any]] = field(default_factory=list)
    chronic_conditions: list[dict[str, Any]] = field(default_factory=list)
    diagnoses: list[dict[str, Any]] = field(default_factory=list)
    allergies: list[dict[str, Any]] = field(default_factory=list)
    contraindications: list[dict[str, Any]] = field(default_factory=list)
    medical_history: list[dict[str, Any]] = field(default_factory=list)
    vaccine_overrides: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_flat_dict(cls, data: dict[str, Any]) -> PetMedicalSection:
        """Build the section from a flat pet dict."""
        return cls(
            medical_country=(_coerce_optional_str(data.get(CONF_MEDICAL_COUNTRY)) or DEFAULT_MEDICAL_COUNTRY).upper(),
            medical_region=_coerce_optional_str(data.get(CONF_MEDICAL_REGION)) or DEFAULT_MEDICAL_REGION,
            regional_policy=_coerce_optional_str(data.get(CONF_REGIONAL_POLICY)) or _coerce_optional_str(data.get(CONF_MEDICAL_REGION)) or DEFAULT_MEDICAL_REGION,
            vaccine_profile=_parse_vaccine_profile(data.get(CONF_VACCINE_PROFILE)),
            vet_override=bool(data.get(CONF_VET_OVERRIDE, True)),
            body_condition_score=float(data.get(CONF_BODY_CONDITION_SCORE, DEFAULT_BODY_CONDITION_SCORE)),
            weight_goal_min_kg=_parse_optional_float(data.get(CONF_WEIGHT_GOAL_MIN_KG)),
            weight_goal_max_kg=_parse_optional_float(data.get(CONF_WEIGHT_GOAL_MAX_KG)),
            passport_number=_coerce_optional_str(data.get(CONF_PASSPORT_NUMBER)),
            microchip_id=_coerce_optional_str(data.get(CONF_MICROCHIP_ID)),
            insurance_policy=_coerce_optional_str(data.get(CONF_INSURANCE_POLICY)),
            primary_vet=_coerce_optional_str(data.get(CONF_PRIMARY_VET)),
            vet_phone=_coerce_optional_str(data.get(CONF_VET_PHONE)),
            medication_courses=list(data.get(CONF_MEDICATION_COURSES, []) or []),
            chronic_conditions=list(data.get(CONF_CHRONIC_CONDITIONS, []) or []),
            diagnoses=list(data.get(CONF_DIAGNOSES, []) or []),
            allergies=list(data.get(CONF_ALLERGIES, []) or []),
            contraindications=list(data.get(CONF_CONTRAINDICATIONS, []) or []),
            medical_history=list(data.get(CONF_MEDICAL_HISTORY, []) or []),
            vaccine_overrides=list(data.get(CONF_VACCINE_OVERRIDES, []) or []),
        )

    def as_dict(self) -> dict[str, Any]:
        """Serialize the section."""
        return {
            CONF_MEDICAL_COUNTRY: self.medical_country,
            CONF_MEDICAL_REGION: self.medical_region,
            CONF_REGIONAL_POLICY: self.regional_policy,
            CONF_VACCINE_PROFILE: self.vaccine_profile,
            CONF_VET_OVERRIDE: self.vet_override,
            CONF_BODY_CONDITION_SCORE: self.body_condition_score,
            CONF_WEIGHT_GOAL_MIN_KG: self.weight_goal_min_kg,
            CONF_WEIGHT_GOAL_MAX_KG: self.weight_goal_max_kg,
            CONF_PASSPORT_NUMBER: self.passport_number,
            CONF_MICROCHIP_ID: self.microchip_id,
            CONF_INSURANCE_POLICY: self.insurance_policy,
            CONF_PRIMARY_VET: self.primary_vet,
            CONF_VET_PHONE: self.vet_phone,
            CONF_MEDICATION_COURSES: self.medication_courses,
            CONF_CHRONIC_CONDITIONS: self.chronic_conditions,
            CONF_DIAGNOSES: self.diagnoses,
            CONF_ALLERGIES: self.allergies,
            CONF_CONTRAINDICATIONS: self.contraindications,
            CONF_MEDICAL_HISTORY: self.medical_history,
            CONF_VACCINE_OVERRIDES: self.vaccine_overrides,
        }


@dataclass(slots=True)
class PetAnalyticsSection:
    """Analytics/tuning section for v3 pet config records."""

    weather_adaptation: bool = True
    heat_threshold_c: float = DEFAULT_HEAT_THRESHOLD_C
    cold_threshold_c: float = DEFAULT_COLD_THRESHOLD_C

    @classmethod
    def from_flat_dict(cls, data: dict[str, Any]) -> PetAnalyticsSection:
        """Build the section from a flat pet dict."""
        return cls(
            weather_adaptation=bool(data.get(CONF_WEATHER_ADAPTATION, True)),
            heat_threshold_c=float(data.get(CONF_HEAT_THRESHOLD_C, DEFAULT_HEAT_THRESHOLD_C)),
            cold_threshold_c=float(data.get(CONF_COLD_THRESHOLD_C, DEFAULT_COLD_THRESHOLD_C)),
        )

    def as_dict(self) -> dict[str, Any]:
        """Serialize the section."""
        return {
            CONF_WEATHER_ADAPTATION: self.weather_adaptation,
            CONF_HEAT_THRESHOLD_C: self.heat_threshold_c,
            CONF_COLD_THRESHOLD_C: self.cold_threshold_c,
        }


@dataclass(slots=True)
class PetExternalLinksSection:
    """External links/entities section for v3 pet config records."""

    calendar_links: list[dict[str, Any]] = field(default_factory=list)
    external_calendar_entity_ids: list[str] = field(default_factory=list)
    gps_tracker_entity_id: str | None = None
    ble_tracker_entity_id: str | None = None
    safe_zones: list[dict[str, Any]] = field(default_factory=list)
    room_presence_sources: list[dict[str, Any]] = field(default_factory=list)
    household_presence_entity_ids: list[str] = field(default_factory=list)
    weather_entity_id: str | None = None
    behavior_signal_entity_ids: list[str] = field(default_factory=list)
    camera_entity_id: str | None = None
    camera_room_name: str | None = None
    food_bowl_area: Any = None
    water_bowl_area: Any = None

    @classmethod
    def from_flat_dict(cls, data: dict[str, Any]) -> PetExternalLinksSection:
        """Build the section from a flat pet dict."""
        return cls(
            calendar_links=list(data.get(CONF_CALENDAR_LINKS, []) or []),
            external_calendar_entity_ids=list(data.get(CONF_EXTERNAL_CALENDAR_ENTITY_IDS, []) or []),
            gps_tracker_entity_id=_coerce_optional_str(data.get(CONF_GPS_TRACKER_ENTITY_ID)),
            ble_tracker_entity_id=_coerce_optional_str(data.get(CONF_BLE_TRACKER_ENTITY_ID)),
            safe_zones=list(data.get(CONF_SAFE_ZONES, []) or []),
            room_presence_sources=list(data.get(CONF_ROOM_PRESENCE_SOURCES, []) or []),
            household_presence_entity_ids=list(data.get(CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS, []) or []),
            weather_entity_id=_coerce_optional_str(data.get(CONF_WEATHER_ENTITY_ID)),
            behavior_signal_entity_ids=list(data.get(CONF_BEHAVIOR_SIGNAL_ENTITY_IDS, []) or []),
            camera_entity_id=_coerce_optional_str(data.get(CONF_CAMERA_ENTITY_ID)),
            camera_room_name=_coerce_optional_str(data.get(CONF_CAMERA_ROOM_NAME)),
            food_bowl_area=data.get(CONF_FOOD_BOWL_AREA),
            water_bowl_area=data.get(CONF_WATER_BOWL_AREA),
        )

    def as_dict(self) -> dict[str, Any]:
        """Serialize the section."""
        return {
            CONF_CALENDAR_LINKS: self.calendar_links,
            CONF_EXTERNAL_CALENDAR_ENTITY_IDS: self.external_calendar_entity_ids,
            CONF_GPS_TRACKER_ENTITY_ID: self.gps_tracker_entity_id,
            CONF_BLE_TRACKER_ENTITY_ID: self.ble_tracker_entity_id,
            CONF_SAFE_ZONES: self.safe_zones,
            CONF_ROOM_PRESENCE_SOURCES: self.room_presence_sources,
            CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS: self.household_presence_entity_ids,
            CONF_WEATHER_ENTITY_ID: self.weather_entity_id,
            CONF_BEHAVIOR_SIGNAL_ENTITY_IDS: self.behavior_signal_entity_ids,
            CONF_CAMERA_ENTITY_ID: self.camera_entity_id,
            CONF_CAMERA_ROOM_NAME: self.camera_room_name,
            CONF_FOOD_BOWL_AREA: self.food_bowl_area,
            CONF_WATER_BOWL_AREA: self.water_bowl_area,
        }


@dataclass(slots=True)
class PetConfigV3:
    """Versioned pet config record with explicit sections."""

    profile: PetProfileSection
    plan: PetPlanSection
    medical: PetMedicalSection
    analytics: PetAnalyticsSection
    external_links: PetExternalLinksSection
    schema_version: int = PET_SCHEMA_VERSION

    @classmethod
    def from_flat_dict(cls, data: dict[str, Any]) -> PetConfigV3:
        """Build a v3 record from a flat config dict."""
        return cls(
            profile=PetProfileSection.from_flat_dict(data),
            plan=PetPlanSection.from_flat_dict(data),
            medical=PetMedicalSection.from_flat_dict(data),
            analytics=PetAnalyticsSection.from_flat_dict(data),
            external_links=PetExternalLinksSection.from_flat_dict(data),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PetConfigV3:
        """Build a v3 record from nested or flat storage."""
        if not _is_pet_config_v3(data):
            return cls.from_flat_dict(data)
        flat: dict[str, Any] = {}
        for section_name in (
            CONF_PET_SECTION_PROFILE,
            CONF_PET_SECTION_PLAN,
            CONF_PET_SECTION_MEDICAL,
            CONF_PET_SECTION_ANALYTICS,
            CONF_PET_SECTION_EXTERNAL_LINKS,
        ):
            section = data.get(section_name, {})
            if isinstance(section, dict):
                flat.update(section)
        return cls.from_flat_dict(flat)

    def as_flat_dict(self) -> dict[str, Any]:
        """Flatten the v3 record to the runtime-friendly dict."""
        flat: dict[str, Any] = {}
        flat.update(self.profile.as_dict())
        flat.update(self.plan.as_dict())
        flat.update(self.medical.as_dict())
        flat.update(self.analytics.as_dict())
        flat.update(self.external_links.as_dict())
        return flat

    def as_dict(self) -> dict[str, Any]:
        """Serialize the record as nested v3 payload."""
        return {
            CONF_PET_SCHEMA: self.schema_version,
            CONF_PET_SECTION_PROFILE: self.profile.as_dict(),
            CONF_PET_SECTION_PLAN: self.plan.as_dict(),
            CONF_PET_SECTION_MEDICAL: self.medical.as_dict(),
            CONF_PET_SECTION_ANALYTICS: self.analytics.as_dict(),
            CONF_PET_SECTION_EXTERNAL_LINKS: self.external_links.as_dict(),
        }


def _is_pet_config_v3(data: dict[str, Any]) -> bool:
    """Return whether the payload is a nested v3 pet config record."""
    return int(data.get(CONF_PET_SCHEMA, 0) or 0) >= PET_SCHEMA_VERSION and isinstance(
        data.get(CONF_PET_SECTION_PROFILE),
        dict,
    )


def normalize_pet_config_record(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize a pet config record to the flat runtime-friendly shape."""
    return PetConfigV3.from_dict(data).as_flat_dict()


def serialize_pet_config_record_v3(data: dict[str, Any]) -> dict[str, Any]:
    """Serialize a flat pet config record into the nested v3 shape."""
    return PetConfigV3.from_flat_dict(normalize_pet_config_record(data)).as_dict()


def serialize_diva_entry_settings_v3(
    *,
    hub_name: str,
    show_editor_in_sidebar: bool,
    pets: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Serialize hub settings and pet list into the v3 config entry shape."""
    return {
        CONF_HUB_NAME: hub_name,
        CONF_SHOW_EDITOR_IN_SIDEBAR: show_editor_in_sidebar,
        CONF_PET_SCHEMA: PET_SCHEMA_VERSION,
        CONF_PETS: [serialize_pet_config_record_v3(pet) for pet in pets],
    }


@dataclass(slots=True)
class PetProfile:
    """Static pet profile information."""

    pet_id: str
    name: str
    species: str
    breed: str
    birthdate: date
    weight_kg: float
    diet_mode: str
    avatar: str | None = None
    camera_entity_id: str | None = None
    camera_room_name: str | None = None
    food_bowl_area: BowlArea | None = None
    water_bowl_area: BowlArea | None = None
    feeding_schedule_text: str = ""
    walk_schedule_text: str = ""
    care_schedule_text: str = ""
    vet_appointments_text: str = ""
    caregivers_text: str = ""
    care_roles: tuple[CareRole, ...] = ()
    care_shifts: tuple[CareShift, ...] = ()
    checklist_items: tuple[ChecklistItem, ...] = ()
    approval_required_actions: tuple[str, ...] = ()
    default_manual_mode: str = OPERATION_MODE_NORMAL
    weather_adaptation: bool = True
    heat_threshold_c: float = DEFAULT_HEAT_THRESHOLD_C
    cold_threshold_c: float = DEFAULT_COLD_THRESHOLD_C
    food_catalog: tuple[FoodCatalogEntry, ...] = ()
    food_transition_plan: tuple[FoodTransitionStep, ...] = ()
    calendar_links: tuple[CalendarLink, ...] = ()
    external_calendar_entity_ids: tuple[str, ...] = ()
    passport_number: str | None = None
    microchip_id: str | None = None
    insurance_policy: str | None = None
    primary_vet: str | None = None
    vet_phone: str | None = None
    gps_tracker_entity_id: str | None = None
    ble_tracker_entity_id: str | None = None
    safe_zones: tuple[SafeZone, ...] = ()
    room_presence_sources: tuple[RoomPresenceSource, ...] = ()
    household_presence_entity_ids: tuple[str, ...] = ()
    weather_entity_id: str | None = None
    behavior_signal_entity_ids: tuple[str, ...] = ()
    medical_country: str = DEFAULT_MEDICAL_COUNTRY
    medical_region: str = DEFAULT_MEDICAL_REGION
    regional_policy: str = DEFAULT_MEDICAL_REGION
    vaccine_profile: str = VACCINE_PROFILE_AUTO
    vet_override: bool = True
    body_condition_score: float = DEFAULT_BODY_CONDITION_SCORE
    weight_goal_min_kg: float | None = None
    weight_goal_max_kg: float | None = None
    medication_courses: tuple[MedicationCourse, ...] = ()
    chronic_conditions: tuple[ChronicCondition, ...] = ()
    diagnoses: tuple[DiagnosisEntry, ...] = ()
    allergies: tuple[AllergyEntry, ...] = ()
    contraindications: tuple[ContraindicationEntry, ...] = ()
    medical_history: tuple[MedicalHistoryEntry, ...] = ()
    vaccine_overrides: tuple[VaccinePlanEntry, ...] = ()
    feeding_routines: tuple[RoutineEntry, ...] = ()
    walk_routines: tuple[RoutineEntry, ...] = ()
    care_routines: tuple[RoutineEntry, ...] = ()
    routine_exceptions: tuple[ScheduleException, ...] = ()
    vet_appointments: tuple[AppointmentEntry, ...] = ()
    caregivers: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PetProfile:
        """Create a profile from config entry data."""
        data = normalize_pet_config_record(data)
        feeding_schedule_text = _normalize_multiline_text(data.get(CONF_FEEDING_SCHEDULE))
        walk_schedule_text = _normalize_multiline_text(data.get(CONF_WALK_SCHEDULE))
        care_schedule_text = _normalize_multiline_text(data.get(CONF_CARE_SCHEDULE))
        vet_appointments_text = _normalize_multiline_text(data.get(CONF_VET_APPOINTMENTS))
        caregivers_text = _normalize_multiline_text(data.get(CONF_CAREGIVERS))
        diet_mode = str(data[CONF_DIET_MODE])
        feeding_routines = parse_feeding_schedule(
            data.get(CONF_FEEDING_ROUTINES, feeding_schedule_text),
            pet_id=str(data[CONF_PET_ID]),
        )
        walk_routines = parse_walk_schedule(
            data.get(CONF_WALK_ROUTINES, walk_schedule_text),
            pet_id=str(data[CONF_PET_ID]),
        )
        care_routines = parse_care_schedule(
            data.get(CONF_CARE_ROUTINES, care_schedule_text),
            pet_id=str(data[CONF_PET_ID]),
        )
        routine_exceptions = parse_schedule_exceptions(
            data.get(CONF_ROUTINE_EXCEPTIONS),
            pet_id=str(data[CONF_PET_ID]),
        )
        food_catalog = parse_food_catalog(data.get(CONF_FOOD_CATALOG))
        food_transition_plan = parse_food_transition_plan(data.get(CONF_FOOD_TRANSITION_PLAN))
        medication_courses = parse_medication_courses(data.get(CONF_MEDICATION_COURSES))
        chronic_conditions = parse_chronic_conditions(data.get(CONF_CHRONIC_CONDITIONS))
        diagnoses = parse_diagnoses(data.get(CONF_DIAGNOSES))
        allergies = parse_allergies(data.get(CONF_ALLERGIES))
        contraindications = parse_contraindications(data.get(CONF_CONTRAINDICATIONS))
        medical_history = parse_medical_history(data.get(CONF_MEDICAL_HISTORY))
        vaccine_overrides = parse_vaccine_overrides(data.get(CONF_VACCINE_OVERRIDES))
        calendar_links = parse_calendar_links(
            data.get(CONF_CALENDAR_LINKS),
            fallback_entity_ids=data.get(CONF_EXTERNAL_CALENDAR_ENTITY_IDS),
        )
        care_roles = parse_care_roles(data.get(CONF_CARE_ROLES))
        care_shifts = parse_care_shifts(data.get(CONF_CARE_SHIFTS), pet_id=str(data[CONF_PET_ID]))
        checklist_items = parse_checklist_items(data.get(CONF_CHECKLIST_ITEMS), pet_id=str(data[CONF_PET_ID]))
        safe_zones = parse_safe_zones(data.get(CONF_SAFE_ZONES))
        room_presence_sources = parse_room_presence_sources(data.get(CONF_ROOM_PRESENCE_SOURCES))
        weight_goal_min = _parse_optional_float(data.get(CONF_WEIGHT_GOAL_MIN_KG))
        weight_goal_max = _parse_optional_float(data.get(CONF_WEIGHT_GOAL_MAX_KG))
        return cls(
            pet_id=str(data[CONF_PET_ID]),
            name=str(data[CONF_NAME]),
            species=str(data[CONF_SPECIES]),
            breed=str(data[CONF_BREED]),
            birthdate=_parse_date(data[CONF_BIRTHDATE]),
            weight_kg=float(data[CONF_WEIGHT]),
            diet_mode=diet_mode,
            avatar=normalize_avatar_reference(data.get(CONF_AVATAR)),
            camera_entity_id=_coerce_optional_str(data.get(CONF_CAMERA_ENTITY_ID)),
            camera_room_name=_coerce_optional_str(data.get(CONF_CAMERA_ROOM_NAME)),
            food_bowl_area=BowlArea.from_value(data.get(CONF_FOOD_BOWL_AREA)),
            water_bowl_area=BowlArea.from_value(data.get(CONF_WATER_BOWL_AREA)),
            feeding_schedule_text=feeding_schedule_text,
            walk_schedule_text=walk_schedule_text,
            care_schedule_text=care_schedule_text,
            vet_appointments_text=vet_appointments_text,
            caregivers_text=caregivers_text,
            care_roles=care_roles,
            care_shifts=care_shifts,
            checklist_items=checklist_items,
            approval_required_actions=parse_approval_required_actions(data.get(CONF_APPROVAL_REQUIRED_ACTIONS)),
            default_manual_mode=_parse_manual_mode(data.get(CONF_DEFAULT_MANUAL_MODE)),
            weather_adaptation=bool(data.get(CONF_WEATHER_ADAPTATION, True)),
            heat_threshold_c=float(data.get(CONF_HEAT_THRESHOLD_C, DEFAULT_HEAT_THRESHOLD_C)),
            cold_threshold_c=float(data.get(CONF_COLD_THRESHOLD_C, DEFAULT_COLD_THRESHOLD_C)),
            food_catalog=food_catalog,
            food_transition_plan=food_transition_plan,
            calendar_links=calendar_links,
            external_calendar_entity_ids=tuple(link.calendar_entity_id for link in calendar_links),
            passport_number=_coerce_optional_str(data.get(CONF_PASSPORT_NUMBER)),
            microchip_id=_coerce_optional_str(data.get(CONF_MICROCHIP_ID)),
            insurance_policy=_coerce_optional_str(data.get(CONF_INSURANCE_POLICY)),
            primary_vet=_coerce_optional_str(data.get(CONF_PRIMARY_VET)),
            vet_phone=_coerce_optional_str(data.get(CONF_VET_PHONE)),
            gps_tracker_entity_id=_coerce_optional_str(data.get(CONF_GPS_TRACKER_ENTITY_ID)),
            ble_tracker_entity_id=_coerce_optional_str(data.get(CONF_BLE_TRACKER_ENTITY_ID)),
            safe_zones=safe_zones,
            room_presence_sources=room_presence_sources,
            household_presence_entity_ids=_normalize_entity_list(data.get(CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS)),
            weather_entity_id=_coerce_optional_str(data.get(CONF_WEATHER_ENTITY_ID)),
            behavior_signal_entity_ids=_normalize_entity_list(data.get(CONF_BEHAVIOR_SIGNAL_ENTITY_IDS)),
            medical_country=(_coerce_optional_str(data.get(CONF_MEDICAL_COUNTRY)) or DEFAULT_MEDICAL_COUNTRY).upper(),
            medical_region=_coerce_optional_str(data.get(CONF_MEDICAL_REGION)) or DEFAULT_MEDICAL_REGION,
            regional_policy=_coerce_optional_str(data.get(CONF_REGIONAL_POLICY)) or _coerce_optional_str(data.get(CONF_MEDICAL_REGION)) or DEFAULT_MEDICAL_REGION,
            vaccine_profile=_parse_vaccine_profile(data.get(CONF_VACCINE_PROFILE)),
            vet_override=bool(data.get(CONF_VET_OVERRIDE, True)),
            body_condition_score=float(data.get(CONF_BODY_CONDITION_SCORE, DEFAULT_BODY_CONDITION_SCORE)),
            weight_goal_min_kg=weight_goal_min,
            weight_goal_max_kg=weight_goal_max,
            medication_courses=medication_courses,
            chronic_conditions=chronic_conditions,
            diagnoses=diagnoses,
            allergies=allergies,
            contraindications=contraindications,
            medical_history=medical_history,
            vaccine_overrides=vaccine_overrides,
            feeding_routines=feeding_routines,
            walk_routines=walk_routines,
            care_routines=care_routines,
            routine_exceptions=routine_exceptions,
            vet_appointments=parse_vet_appointments(vet_appointments_text, pet_id=str(data[CONF_PET_ID])),
            caregivers=_normalize_name_list(caregivers_text),
        )

    def as_dict(self) -> dict[str, Any]:
        """Serialize the profile."""
        return {
            CONF_PET_ID: self.pet_id,
            CONF_NAME: self.name,
            CONF_SPECIES: self.species,
            CONF_BREED: self.breed,
            CONF_BIRTHDATE: self.birthdate.isoformat(),
            CONF_WEIGHT: self.weight_kg,
            CONF_DIET_MODE: self.diet_mode,
            CONF_AVATAR: self.avatar,
            CONF_CAMERA_ENTITY_ID: self.camera_entity_id,
            CONF_CAMERA_ROOM_NAME: self.camera_room_name,
            CONF_FOOD_BOWL_AREA: self.food_bowl_area.as_dict() if self.food_bowl_area else None,
            CONF_WATER_BOWL_AREA: self.water_bowl_area.as_dict() if self.water_bowl_area else None,
            CONF_FEEDING_SCHEDULE: self.feeding_schedule_text,
            CONF_WALK_SCHEDULE: self.walk_schedule_text,
            CONF_CARE_SCHEDULE: self.care_schedule_text,
            CONF_VET_APPOINTMENTS: self.vet_appointments_text,
            CONF_FEEDING_ROUTINES: [routine.as_dict() for routine in self.feeding_routines],
            CONF_WALK_ROUTINES: [routine.as_dict() for routine in self.walk_routines],
            CONF_CARE_ROUTINES: [routine.as_dict() for routine in self.care_routines],
            CONF_ROUTINE_EXCEPTIONS: [exception.as_dict() for exception in self.routine_exceptions],
            CONF_CARE_ROLES: [item.as_dict() for item in self.care_roles],
            CONF_CARE_SHIFTS: [item.as_dict() for item in self.care_shifts],
            CONF_CHECKLIST_ITEMS: [item.as_dict() for item in self.checklist_items],
            CONF_APPROVAL_REQUIRED_ACTIONS: list(self.approval_required_actions),
            CONF_DEFAULT_MANUAL_MODE: self.default_manual_mode,
            CONF_WEATHER_ADAPTATION: self.weather_adaptation,
            CONF_HEAT_THRESHOLD_C: self.heat_threshold_c,
            CONF_COLD_THRESHOLD_C: self.cold_threshold_c,
            CONF_FOOD_CATALOG: [item.as_dict() for item in self.food_catalog],
            CONF_FOOD_TRANSITION_PLAN: [step.as_dict() for step in self.food_transition_plan],
            CONF_CALENDAR_LINKS: [link.as_dict() for link in self.calendar_links],
            CONF_EXTERNAL_CALENDAR_ENTITY_IDS: list(self.external_calendar_entity_ids),
            CONF_PASSPORT_NUMBER: self.passport_number,
            CONF_MICROCHIP_ID: self.microchip_id,
            CONF_INSURANCE_POLICY: self.insurance_policy,
            CONF_PRIMARY_VET: self.primary_vet,
            CONF_VET_PHONE: self.vet_phone,
            CONF_GPS_TRACKER_ENTITY_ID: self.gps_tracker_entity_id,
            CONF_BLE_TRACKER_ENTITY_ID: self.ble_tracker_entity_id,
            CONF_SAFE_ZONES: [zone.as_dict() for zone in self.safe_zones],
            CONF_ROOM_PRESENCE_SOURCES: [source.as_dict() for source in self.room_presence_sources],
            CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS: list(self.household_presence_entity_ids),
            CONF_WEATHER_ENTITY_ID: self.weather_entity_id,
            CONF_BEHAVIOR_SIGNAL_ENTITY_IDS: list(self.behavior_signal_entity_ids),
            CONF_MEDICAL_COUNTRY: self.medical_country,
            CONF_MEDICAL_REGION: self.medical_region,
            CONF_REGIONAL_POLICY: self.regional_policy,
            CONF_VACCINE_PROFILE: self.vaccine_profile,
            CONF_VET_OVERRIDE: self.vet_override,
            CONF_BODY_CONDITION_SCORE: self.body_condition_score,
            CONF_WEIGHT_GOAL_MIN_KG: self.weight_goal_min_kg,
            CONF_WEIGHT_GOAL_MAX_KG: self.weight_goal_max_kg,
            CONF_MEDICATION_COURSES: [course.as_dict() for course in self.medication_courses],
            CONF_CHRONIC_CONDITIONS: [condition.as_dict() for condition in self.chronic_conditions],
            CONF_DIAGNOSES: [entry.as_dict() for entry in self.diagnoses],
            CONF_ALLERGIES: [entry.as_dict() for entry in self.allergies],
            CONF_CONTRAINDICATIONS: [entry.as_dict() for entry in self.contraindications],
            CONF_MEDICAL_HISTORY: [entry.as_dict() for entry in self.medical_history],
            CONF_VACCINE_OVERRIDES: [entry.as_dict() for entry in self.vaccine_overrides],
            CONF_CAREGIVERS: self.caregivers_text,
        }

    def as_v3_dict(self) -> dict[str, Any]:
        """Serialize the profile into the nested v3 config shape."""
        return serialize_pet_config_record_v3(self.as_dict())

    @property
    def slug(self) -> str:
        """Return the normalized slug for events."""
        return self.pet_id

    @property
    def age_years(self) -> float:
        """Return the pet age in years."""
        return max(0.0, (date.today() - self.birthdate).days / 365.25)

    @property
    def has_external_calendars(self) -> bool:
        """Return if this pet is linked to external calendars."""
        return bool(self.external_calendar_entity_ids)

    def calendar_source_of_truth(self, calendar_entity_id: str) -> str:
        """Return the configured source-of-truth policy for a linked calendar."""
        for link in self.calendar_links:
            if link.calendar_entity_id == calendar_entity_id:
                return link.source_of_truth
        return CALENDAR_SOURCE_OF_TRUTH_DIVA

    def effective_feeding_routines(self) -> tuple[RoutineEntry, ...]:
        """Return configured feeding routines or diet defaults."""
        if self.feeding_routines:
            return self.feeding_routines
        routines: list[RoutineEntry] = []
        for index, slot in enumerate(
            DEFAULT_FEEDING_SCHEDULES.get(self.diet_mode, DEFAULT_FEEDING_SCHEDULES[DIET_MODE_ADULT])
        ):
            hour, minute = (int(value) for value in slot.split(":"))
            routines.append(
                RoutineEntry(
                    routine_id=f"{self.pet_id}:feed_default:{index}",
                    category=ROUTINE_TYPE_FEED,
                    time_of_day=time(hour=hour, minute=minute),
                    label=f"{self.name} feeding",
                    duration_minutes=DEFAULT_FEEDING_DURATION_MINUTES,
                    weekdays=ALL_WEEKDAYS,
                    meal_type=MEAL_TYPE_DRY,
                )
            )
        return tuple(routines)

    def food_entry_by_name(self, name: str | None) -> FoodCatalogEntry | None:
        """Return a catalog entry by configured name."""
        if not name:
            return None
        normalized = name.strip().lower()
        for item in self.food_catalog:
            if item.name.lower() == normalized:
                return item
        return None

    def default_food_for_meal_type(self, meal_type: str) -> FoodCatalogEntry | None:
        """Return the best matching food entry for a meal type."""
        kind_priority = {
            MEAL_TYPE_TREAT: FOOD_KIND_TREATS,
            MEAL_TYPE_MEDICATION: FOOD_KIND_MEDICAL,
            MEAL_TYPE_SUPPLEMENT: FOOD_KIND_SUPPLEMENTS,
        }
        expected_kind = kind_priority.get(meal_type, FOOD_KIND_MAIN)
        for item in self.food_catalog:
            if item.kind == expected_kind and item.meal_type == meal_type:
                return item
        for item in self.food_catalog:
            if item.kind == expected_kind:
                return item
        for item in self.food_catalog:
            if item.meal_type == meal_type:
                return item
        return self.food_catalog[0] if self.food_catalog else None

    def active_food_transition(self, day: date) -> FoodTransitionStep | None:
        """Return the latest active transition step for a day."""
        active = [step for step in self.food_transition_plan if step.transition_date <= day]
        if not active:
            return None
        return max(active, key=lambda step: step.transition_date)

    def default_main_food_kcal_per_gram(self) -> float:
        """Return the calorie density for the primary main food."""
        for item in self.food_catalog:
            if item.kind == FOOD_KIND_MAIN:
                return item.kcal_per_gram
        return DEFAULT_KCAL_PER_GRAM

    def all_routines(self) -> tuple[RoutineEntry, ...]:
        """Return all recurring routines."""
        return self.effective_feeding_routines() + self.walk_routines + self.care_routines

    def vaccine_plan(self, today: date) -> tuple[VaccinePlanEntry, ...]:
        """Return the derived vaccine plan for the pet."""
        default_plan = build_default_vaccine_plan(
            pet_id=self.pet_id,
            species=self.species,
            breed=self.breed,
            birthdate=self.birthdate,
            today=today,
            country=self.medical_country,
            region=self.medical_region,
            regional_policy=self.regional_policy,
            vaccine_profile=self.vaccine_profile,
        )
        merged: dict[str, VaccinePlanEntry] = {entry.dose_id: entry for entry in default_plan}
        for entry in self.vaccine_overrides:
            if entry.dose_id in merged and not self.vet_override:
                continue
            merged[entry.dose_id] = entry
        return tuple(sorted(merged.values(), key=lambda item: (item.due_date, item.vaccine_name)))

    def upcoming_events(self, start: datetime, end: datetime) -> list[ScheduledEvent]:
        """Return scheduled events within a time window."""
        tzinfo = start.tzinfo or end.tzinfo
        events: list[ScheduledEvent] = []
        start_day = start.date()
        end_day = end.date()
        for routine in self.all_routines():
            for offset in range((end_day - start_day).days + 1):
                day = start_day + timedelta(days=offset)
                if not routine.occurs_on(day):
                    continue
                event = routine.occurrence(self.pet_id, day, tzinfo)
                if event.start < end and event.end > start:
                    events.append(event)
        for appointment in self.vet_appointments:
            event = appointment.to_event(self.pet_id, tzinfo)
            if event.start < end and event.end > start:
                events.append(event)
        return sorted(events, key=lambda item: item.start)


@dataclass(slots=True)
class PetNotice:
    """A runtime event, anomaly, or recommendation."""

    category: str
    name: str
    timestamp: str
    severity: str = "info"
    message: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Serialize the notice."""
        payload = {
            "category": self.category,
            "name": self.name,
            "timestamp": self.timestamp,
            "severity": self.severity,
        }
        if self.message is not None:
            payload["message"] = self.message
        if self.data:
            payload["data"] = self.data
        return payload


@dataclass(slots=True)
class CameraAnalysis:
    """The result of a camera image analysis pass."""

    frame_motion_score: float
    food_motion_score: float = 0.0
    water_motion_score: float = 0.0
    food_empty: bool | None = None
    water_empty: bool | None = None
    food_interaction: bool = False
    water_interaction: bool = False
    debug: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class BehaviorObservation:
    """A normalized behavior observation from manual, camera, BLE, or external AI."""

    observation_type: str
    timestamp: str
    severity: str = "warning"
    source: str = "manual"
    confidence: float = 1.0
    duration_seconds: int | None = None
    model_name: str | None = None
    message: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Serialize the observation."""
        payload: dict[str, Any] = {
            "type": self.observation_type,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "source": self.source,
            "confidence": round(max(0.0, min(1.0, self.confidence)), 3),
        }
        if self.duration_seconds is not None:
            payload["duration_seconds"] = int(self.duration_seconds)
        if self.model_name:
            payload["model_name"] = self.model_name
        if self.message:
            payload["message"] = self.message
        if self.evidence:
            payload["evidence"] = dict(self.evidence)
        return payload


@dataclass(slots=True)
class PetContext:
    """External Home Assistant signals merged into the pet model."""

    gps_tracker_state: str | None = None
    ble_tracker_state: str | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    gps_accuracy_m: float | None = None
    caregiver_home_count: int = 0
    home_alone: bool = False
    outside_temperature_c: float | None = None
    current_zone: str | None = None
    geofence_breached: bool = False
    distance_from_safe_zone_m: float | None = None
    current_room: str | None = None
    room_presence_sources: tuple[str, ...] = ()
    active_behavior_signals: tuple[str, ...] = ()


@dataclass(slots=True)
class PetRuntimeState:
    """Persisted runtime state for a pet."""

    weight_kg: float
    diet_mode: str
    food_portion_grams: float
    daily_calories: float
    manual_mode: str = OPERATION_MODE_NORMAL
    weight_goal_min_kg: float | None = None
    weight_goal_max_kg: float | None = None
    food_today_grams: float = 0.0
    water_today_ml: float = 0.0
    food_served_today_grams: float = 0.0
    food_ignored_today_grams: float = 0.0
    calories_consumed_today: float = 0.0
    treat_calories_today: float = 0.0
    food_eaten_today_by_type: dict[str, float] = field(default_factory=dict)
    food_served_today_by_type: dict[str, float] = field(default_factory=dict)
    food_ignored_today_by_type: dict[str, float] = field(default_factory=dict)
    food_today_grams_by_food: dict[str, float] = field(default_factory=dict)
    last_feeding_at: str | None = None
    last_seen_eating_at: str | None = None
    last_drinking_at: str | None = None
    last_walk_started_at: str | None = None
    last_walk_finished_at: str | None = None
    last_activity_at: str | None = None
    walk_active: bool = False
    activity_points_today: float = 0.0
    sleep_minutes_today: float = 0.0
    sleeping: bool = False
    last_tick_at: str | None = None
    current_day: str = field(default_factory=lambda: date.today().isoformat())
    pending_meal_grams: float = 0.0
    pending_meal_type: str | None = None
    pending_food_name: str | None = None
    pending_food_kcal_per_gram: float | None = None
    pending_meal_served_at: str | None = None
    manual_next_feeding_at: str | None = None
    food_bowl_empty: bool = False
    water_bowl_empty: bool = False
    active_anomalies: dict[str, str] = field(default_factory=dict)
    sent_recommendations_today: list[str] = field(default_factory=list)
    recent_records: list[dict[str, Any]] = field(default_factory=list)
    journal_entries: list[dict[str, Any]] = field(default_factory=list)
    daily_history: list[dict[str, Any]] = field(default_factory=list)
    behavior_reports: list[dict[str, Any]] = field(default_factory=list)
    behavior_observations: list[dict[str, Any]] = field(default_factory=list)
    pending_approvals: list[dict[str, Any]] = field(default_factory=list)
    checklist_completions: list[dict[str, Any]] = field(default_factory=list)
    medication_log: list[dict[str, Any]] = field(default_factory=list)
    symptom_log: list[dict[str, Any]] = field(default_factory=list)
    active_recovery_plan: dict[str, Any] | None = None
    completed_vaccine_doses: dict[str, str] = field(default_factory=dict)
    vaccine_runtime_overrides: dict[str, dict[str, Any]] = field(default_factory=dict)
    generated_reports: list[dict[str, Any]] = field(default_factory=list)
    weight_history: list[dict[str, Any]] = field(default_factory=list)
    runtime_routine_exceptions: list[dict[str, Any]] = field(default_factory=list)
    emitted_schedule_keys: list[str] = field(default_factory=list)
    calendar_sync_registry: dict[str, list[str]] = field(default_factory=dict)
    calendar_sync_state: dict[str, dict[str, Any]] = field(default_factory=dict)
    calendar_import_overrides: list[dict[str, Any]] = field(default_factory=list)
    calendar_conflicts: list[dict[str, Any]] = field(default_factory=list)
    calendar_conflict_resolutions: list[dict[str, Any]] = field(default_factory=list)
    stress_score: float = 0.0
    feeding_quality_score: float = 100.0
    gps_history: list[dict[str, Any]] = field(default_factory=list)
    current_walk_route: list[dict[str, Any]] = field(default_factory=list)
    last_walk_route: list[dict[str, Any]] = field(default_factory=list)
    last_walk_summary: dict[str, Any] | None = None
    room_history: list[dict[str, Any]] = field(default_factory=list)
    room_dwell_today_minutes: dict[str, float] = field(default_factory=dict)
    zone_visits_today: dict[str, int] = field(default_factory=dict)
    current_room: str | None = None
    current_zone: str | None = None
    geofence_breached: bool = False
    separation_minutes_today: float = 0.0
    sleep_interruptions_today: int = 0
    active_minutes_by_hour: dict[str, float] = field(default_factory=dict)
    sleep_minutes_by_hour: dict[str, float] = field(default_factory=dict)
    latest_behavior_profile: str | None = None
    latest_behavior_summary: str | None = None
    latest_behavior_factors: list[str] = field(default_factory=list)
    latest_baseline_drift_score: float = 0.0
    latest_weekly_summary: str | None = None

    @classmethod
    def create(cls, profile: PetProfile) -> PetRuntimeState:
        """Create an initial runtime state from the profile."""
        daily_calories = calculate_daily_calories(profile.weight_kg, profile.diet_mode)
        return cls(
            weight_kg=profile.weight_kg,
            diet_mode=profile.diet_mode,
            manual_mode=profile.default_manual_mode,
            weight_goal_min_kg=profile.weight_goal_min_kg
            if profile.weight_goal_min_kg is not None
            else round(max(0.1, profile.weight_kg - DEFAULT_WEIGHT_GOAL_MARGIN_KG), 1),
            weight_goal_max_kg=profile.weight_goal_max_kg
            if profile.weight_goal_max_kg is not None
            else round(profile.weight_kg + DEFAULT_WEIGHT_GOAL_MARGIN_KG, 1),
            food_portion_grams=calculate_recommended_portion(
                profile.weight_kg,
                profile.diet_mode,
                daily_calories,
                kcal_per_gram=profile.default_main_food_kcal_per_gram(),
            ),
            daily_calories=daily_calories,
            weight_history=[
                {
                    "timestamp": datetime.combine(date.today(), time.min).isoformat(),
                    "weight_kg": round(profile.weight_kg, 2),
                    "source": "profile",
                }
            ],
        )

    @classmethod
    def from_dict(cls, profile: PetProfile, payload: dict[str, Any]) -> PetRuntimeState:
        """Restore persisted runtime state."""
        restored = cls.create(profile)
        for key, value in payload.items():
            if hasattr(restored, key):
                setattr(restored, key, value)
        return restored

    def as_dict(self) -> dict[str, Any]:
        """Serialize runtime state."""
        return asdict(self)


@dataclass(slots=True)
class PetSnapshot:
    """Derived pet snapshot consumed by Home Assistant entities."""

    pet_id: str
    name: str
    species: str
    breed: str
    birthdate: str
    weight_kg: float
    diet_mode: str
    food_today_grams: float
    water_today_ml: float
    last_feeding_at: str | None
    next_feeding_at: str | None
    next_walk_at: str | None
    next_care_at: str | None
    next_vet_visit_at: str | None
    last_seen_eating_at: str | None
    activity_level: float
    sleep_duration_hours: float
    health_score: float
    stress_score: float
    recommended_food_portion_grams: float
    daily_calories: float
    food_portion_grams: float
    hungry: bool
    needs_walk: bool
    food_bowl_empty: bool
    water_bowl_empty: bool
    sleeping: bool
    anomaly_detected: bool
    sleep_quality_score: float = 100.0
    feeding_quality_score: float = 100.0
    calories_consumed_today: float = 0.0
    treat_calories_today: float = 0.0
    next_medication_at: str | None = None
    next_vaccine_at: str | None = None
    active_medications: tuple[str, ...] = ()
    overdue_medications: tuple[str, ...] = ()
    vaccine_status: str = "ok"
    recovery_status: str = "none"
    recovery_progress_pct: float = 0.0
    symptom_severity_score: float = 0.0
    body_condition_score: float = DEFAULT_BODY_CONDITION_SCORE
    weight_trend_kg: float = 0.0
    weight_goal_min_kg: float | None = None
    weight_goal_max_kg: float | None = None
    chronic_conditions: tuple[str, ...] = ()
    routine_status: str | None = None
    active_food_transition: str | None = None
    operation_mode: str = OPERATION_MODE_NORMAL
    active_modes: tuple[str, ...] = ()
    gps_tracker_state: str | None = None
    ble_tracker_state: str | None = None
    current_zone: str | None = None
    geofence_breached: bool = False
    distance_from_safe_zone_m: float | None = None
    current_room: str | None = None
    room_presence_sources: tuple[str, ...] = ()
    walk_distance_km: float = 0.0
    walk_distance_today_km: float = 0.0
    last_walk_distance_km: float = 0.0
    last_walk_duration_minutes: float = 0.0
    last_walk_route_summary: str | None = None
    separation_score: float = 0.0
    inactivity_duration_minutes: float = 0.0
    baseline_drift_score: float = 0.0
    behavior_profile: str | None = None
    behavior_summary: str | None = None
    current_shift: str | None = None
    next_shift_at: str | None = None
    pending_approvals_count: int = 0
    checklist_progress_pct: float = 100.0
    pending_checklist_items: tuple[str, ...] = ()
    today_vs_baseline: str | None = None
    weekly_summary: str | None = None
    operations_summary: str | None = None
    calendar_sync_status: str = "not_linked"
    calendar_conflicts_count: int = 0
    generated_reports_count: int = 0
    stress_factors: tuple[str, ...] = ()
    subtle_anomalies: tuple[str, ...] = ()
    latest_behavior_observation_at: str | None = None
    preferred_rooms: tuple[str, ...] = ()
    avoided_rooms: tuple[str, ...] = ()
    caregiver_home_count: int = 0
    home_alone: bool = False
    outside_temperature_c: float | None = None
    active_behavior_signals: tuple[str, ...] = ()
    active_anomalies: tuple[str, ...] = ()
    camera_enabled: bool = False

    def as_dict(self) -> dict[str, Any]:
        """Serialize the snapshot."""
        return asdict(self)


@dataclass(slots=True)
class RoutineSubEngine:
    """Routine-focused façade over the pet engine."""

    owner: "PetEngine"

    def upcoming_events(self, start: datetime, end: datetime) -> list[ScheduledEvent]:
        """Return upcoming scheduled events."""
        return self.owner.profile.upcoming_events(start, end)

    def needs_walk(self, now: datetime, context: PetContext) -> bool:
        """Return whether the pet needs a walk."""
        return self.owner._needs_walk(now, context)

    def next_feeding_at(self, now: datetime, context: PetContext) -> str | None:
        """Return the next feeding timestamp."""
        return self.owner._resolve_next_feeding(now, context)

    def next_walk_at(self, now: datetime, context: PetContext) -> str | None:
        """Return the next walk timestamp."""
        return self.owner._resolve_next_walk(now, context)


@dataclass(slots=True)
class NutritionSubEngine:
    """Nutrition-focused façade over the pet engine."""

    owner: "PetEngine"

    def feeding_quality_score(self) -> float:
        """Return the current feeding quality score."""
        return round(_calculate_feeding_quality_score(self.owner.state), 1)

    def recommended_portion_grams(self) -> float:
        """Return the recommended portion based on current runtime state."""
        return round(
            calculate_recommended_portion(
                self.owner.state.weight_kg,
                self.owner.state.diet_mode,
                self.owner.state.daily_calories,
                kcal_per_gram=self.owner.profile.default_main_food_kcal_per_gram(),
            ),
            1,
        )


@dataclass(slots=True)
class MedicalSubEngine:
    """Medical-focused façade over the pet engine."""

    owner: "PetEngine"

    def recovery_status(self, now: datetime) -> str:
        """Return current recovery status."""
        return self.owner._recovery_status(now)

    def recovery_progress_pct(self, now: datetime) -> float:
        """Return current recovery progress."""
        return self.owner._recovery_progress_pct(now)

    def symptom_severity(self, now: datetime) -> float:
        """Return current symptom severity score."""
        return round(self.owner._symptom_severity(now), 1)

    def vaccine_status(self, now: datetime) -> str:
        """Return current vaccine status."""
        return self.owner._vaccine_status(now)

    def next_vaccine_at(self, today: date) -> str | None:
        """Return next vaccine due timestamp."""
        return self.owner._next_vaccine_due(today)


@dataclass(slots=True)
class MobilitySubEngine:
    """Mobility-focused façade over the pet engine."""

    owner: "PetEngine"

    def separation_score(self, now: datetime, context: PetContext) -> float:
        """Return current separation score."""
        return round(self.owner._separation_score(now, context), 1)

    def room_preferences(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Return preferred and avoided rooms."""
        return self.owner._room_preferences()

    def walk_distance_today_km(self, now: datetime) -> float:
        """Return today's walked distance."""
        return self.owner._walk_distance_today_km(now)


@dataclass(slots=True)
class BehaviorSubEngine:
    """Behavior-focused façade over the pet engine."""

    owner: "PetEngine"

    def sleep_quality_score(self, now: datetime) -> float:
        """Return sleep quality score."""
        return round(self.owner._sleep_quality_score(now), 1)

    def inactivity_duration_minutes(self, now: datetime) -> float:
        """Return inactivity streak."""
        return round(self.owner._inactivity_duration_minutes(now), 1)


@dataclass(slots=True)
class ReportingSubEngine:
    """Reporting façade over the pet engine."""

    owner: "PetEngine"

    def build_vet_report(self, now: datetime, snapshot: PetSnapshot, *, history_days: int = 30) -> dict[str, Any]:
        """Build vet report."""
        return self.owner.build_vet_report(now, snapshot, history_days=history_days)

    def build_operations_report(
        self,
        now: datetime,
        snapshot: PetSnapshot,
        *,
        history_days: int = 7,
    ) -> dict[str, Any]:
        """Build operations report."""
        return self.owner.build_operations_report(now, snapshot, history_days=history_days)


class PetEngine:
    """Pure state machine for pet tracking logic."""

    def __init__(self, profile: PetProfile, runtime: PetRuntimeState | None = None) -> None:
        """Initialize the engine."""
        self.profile = profile
        self.state = runtime or PetRuntimeState.create(profile)
        self.routines = RoutineSubEngine(self)
        self.nutrition = NutritionSubEngine(self)
        self.medical = MedicalSubEngine(self)
        self.mobility = MobilitySubEngine(self)
        self.behavior = BehaviorSubEngine(self)
        self.reporting = ReportingSubEngine(self)

    def restore(self, payload: dict[str, Any] | None) -> None:
        """Restore runtime state if available."""
        if payload:
            self.state = PetRuntimeState.from_dict(self.profile, payload)

    def serialize(self) -> dict[str, Any]:
        """Serialize the runtime state."""
        return self.state.as_dict()

    def set_food_portion(self, grams: float) -> None:
        """Update the configured food portion."""
        self.state.food_portion_grams = max(10.0, round(float(grams), 1))

    def set_daily_calories(self, calories: float) -> None:
        """Update the configured daily calories."""
        self.state.daily_calories = max(100.0, round(float(calories), 1))

    def set_weight_goal_min(self, value: float) -> None:
        """Update the lower weight goal bound."""
        self.state.weight_goal_min_kg = round(max(0.1, float(value)), 1)
        if (
            self.state.weight_goal_max_kg is not None
            and self.state.weight_goal_min_kg > self.state.weight_goal_max_kg
        ):
            self.state.weight_goal_max_kg = self.state.weight_goal_min_kg

    def set_weight_goal_max(self, value: float) -> None:
        """Update the upper weight goal bound."""
        self.state.weight_goal_max_kg = round(max(0.1, float(value)), 1)
        if (
            self.state.weight_goal_min_kg is not None
            and self.state.weight_goal_max_kg < self.state.weight_goal_min_kg
        ):
            self.state.weight_goal_min_kg = self.state.weight_goal_max_kg

    def record_weight(
        self,
        now: datetime,
        weight_kg: float,
        *,
        actor: str | None = None,
        note: str | None = None,
        source: str = "manual",
    ) -> list[PetNotice]:
        """Record a new body weight measurement."""
        rounded = round(max(0.1, float(weight_kg)), 2)
        self.state.weight_kg = rounded
        self.state.weight_history.append(
            {
                "timestamp": now.isoformat(),
                "weight_kg": rounded,
                "actor": actor,
                "note": note,
                "source": source,
            }
        )
        self.state.weight_history = self.state.weight_history[-120:]
        self._append_journal(
            now.isoformat(),
            action="weight_logged",
            actor=actor,
            category="health",
            note=note,
            data={"weight_kg": rounded, "source": source},
        )
        return [
            PetNotice(
                category="event",
                name="weight_logged",
                timestamp=now.isoformat(),
                data={"weight_kg": rounded, "source": source, "actor": actor},
            )
        ]

    def set_diet_mode(self, diet_mode: str) -> None:
        """Update the configured diet mode."""
        if diet_mode not in DIET_MODES:
            raise ValueError(f"Unsupported diet mode: {diet_mode}")
        self.profile.diet_mode = diet_mode
        self.state.diet_mode = diet_mode
        self.state.food_portion_grams = calculate_recommended_portion(
            self.state.weight_kg,
            diet_mode,
            self.state.daily_calories,
            kcal_per_gram=self.profile.default_main_food_kcal_per_gram(),
        )
        self.state.manual_next_feeding_at = None

    def set_manual_mode(self, mode: str) -> None:
        """Update the active manual operation mode."""
        self.state.manual_mode = _parse_manual_mode(mode)

    def add_runtime_exception(self, exception: ScheduleException) -> None:
        """Append a one-off schedule exception to runtime storage."""
        stored = [item for item in self.state.runtime_routine_exceptions if not _is_past_exception(item)]
        stored.append(exception.as_dict())
        self.state.runtime_routine_exceptions = stored[-60:]

    def feed_now(
        self,
        now: datetime,
        grams: float | None = None,
        meal_type: str | None = None,
        food_name: str | None = None,
    ) -> list[PetNotice]:
        """Register a feeding event."""
        portion = round(float(grams if grams is not None else self.state.food_portion_grams), 1)
        portion = max(1.0, portion)
        timestamp = now.isoformat()
        effective_meal_type = meal_type or self.state.pending_meal_type or MEAL_TYPE_DRY
        food_entry = self.profile.food_entry_by_name(food_name) or self.profile.default_food_for_meal_type(effective_meal_type)
        effective_food_name = food_name or (food_entry.name if food_entry else None)
        kcal_per_gram = food_entry.kcal_per_gram if food_entry else DEFAULT_KCAL_PER_GRAM
        self.state.food_served_today_grams += portion
        _increment_counter(self.state.food_served_today_by_type, effective_meal_type, portion)
        self.state.pending_meal_grams += portion
        self.state.pending_meal_type = effective_meal_type
        self.state.pending_food_name = effective_food_name
        self.state.pending_food_kcal_per_gram = kcal_per_gram
        self.state.pending_meal_served_at = timestamp
        self.state.last_feeding_at = timestamp
        self.state.manual_next_feeding_at = None
        self.state.food_bowl_empty = False
        self._mark_activity(now)
        self._append_journal(
            timestamp,
            action="feed",
            category=ROUTINE_TYPE_FEED,
            note=f"Served {portion} g",
            data={
                "portion_grams": portion,
                "meal_type": self.state.pending_meal_type,
                "food_name": effective_food_name,
                "kcal_per_gram": kcal_per_gram,
            },
        )
        return [
            PetNotice(
                category="event",
                name=CAMERA_EVENT_FOOD_SERVED,
                timestamp=timestamp,
                data={
                    "portion_grams": portion,
                    "meal_type": self.state.pending_meal_type,
                    "food_name": effective_food_name,
                },
            )
        ]

    def skip_feeding(self, now: datetime) -> list[PetNotice]:
        """Skip the current feeding and schedule the next one."""
        self.state.manual_next_feeding_at = self._compute_next_feeding(now, skip_slots=1)
        self._append_journal(
            now.isoformat(),
            action="skip_feeding",
            category=ROUTINE_TYPE_FEED,
            note="Feeding skipped",
            data={"next_feeding": self.state.manual_next_feeding_at},
        )
        return [
            PetNotice(
                category="event",
                name="feeding_skipped",
                timestamp=now.isoformat(),
                data={"next_feeding": self.state.manual_next_feeding_at},
            )
        ]

    def delay_feeding(self, now: datetime, minutes: int) -> list[PetNotice]:
        """Delay the next feeding."""
        delayed_until = now + timedelta(minutes=minutes)
        self.state.manual_next_feeding_at = delayed_until.isoformat()
        self._append_journal(
            now.isoformat(),
            action="delay_feeding",
            category=ROUTINE_TYPE_FEED,
            note=f"Feeding delayed by {minutes} minutes",
            data={"minutes": minutes, "next_feeding": self.state.manual_next_feeding_at},
        )
        return [
            PetNotice(
                category="event",
                name="feeding_delayed",
                timestamp=now.isoformat(),
                data={"minutes": minutes, "next_feeding": self.state.manual_next_feeding_at},
            )
        ]

    def refill_food(self, now: datetime) -> list[PetNotice]:
        """Mark the food bowl as refilled."""
        self.state.food_bowl_empty = False
        self._mark_activity(now)
        self._append_journal(now.isoformat(), action="refill_food", category=ROUTINE_TYPE_FEED)
        return [PetNotice(category="event", name=CAMERA_EVENT_FOOD_REFILLED, timestamp=now.isoformat())]

    def refill_water(self, now: datetime) -> list[PetNotice]:
        """Mark the water bowl as refilled."""
        self.state.water_bowl_empty = False
        self._mark_activity(now)
        self._append_journal(now.isoformat(), action="refill_water", category="water")
        return [PetNotice(category="event", name=CAMERA_EVENT_WATER_REFILLED, timestamp=now.isoformat())]

    def start_walk(self, now: datetime) -> list[PetNotice]:
        """Start a walk session."""
        self.state.walk_active = True
        self.state.last_walk_started_at = now.isoformat()
        self.state.current_walk_route = []
        self._mark_activity(now)
        self._append_journal(now.isoformat(), action="start_walk", category=ROUTINE_TYPE_WALK)
        return [PetNotice(category="event", name=CAMERA_EVENT_WALK_STARTED, timestamp=now.isoformat())]

    def finish_walk(self, now: datetime) -> list[PetNotice]:
        """Finish a walk session and accrue activity points."""
        started_at = _parse_datetime(self.state.last_walk_started_at) or now
        minutes = max(1.0, (now - started_at).total_seconds() / 60.0)
        route_points = [dict(point) for point in self.state.current_walk_route]
        walk_distance_km = round(_route_distance_km(route_points), 3)
        route_summary = _build_route_summary(route_points)
        self.state.last_walk_summary = {
            "started_at": started_at.isoformat(),
            "finished_at": now.isoformat(),
            "duration_minutes": round(minutes, 1),
            "distance_km": walk_distance_km,
            "route_summary": route_summary,
            "point_count": len(route_points),
        }
        self.state.last_walk_route = route_points[-200:]
        self.state.current_walk_route = []
        self.state.walk_active = False
        self.state.last_walk_finished_at = now.isoformat()
        self.state.activity_points_today += min(45.0, minutes / 2.0)
        self._mark_activity(now)
        self._append_journal(
            now.isoformat(),
            action="finish_walk",
            category=ROUTINE_TYPE_WALK,
            note=f"Walk duration {round(minutes, 1)} min",
            data={
                "duration_minutes": round(minutes, 1),
                "distance_km": walk_distance_km,
                "route_summary": route_summary,
            },
        )
        return [
            PetNotice(
                category="event",
                name=CAMERA_EVENT_WALK_FINISHED,
                timestamp=now.isoformat(),
                data={
                    "duration_minutes": round(minutes, 1),
                    "distance_km": walk_distance_km,
                    "route_summary": route_summary,
                },
            )
        ]

    def log_care_action(
        self,
        now: datetime,
        action: str,
        *,
        actor: str | None = None,
        note: str | None = None,
        category: str = ROUTINE_TYPE_CARE,
    ) -> list[PetNotice]:
        """Add a care journal entry."""
        timestamp = now.isoformat()
        self._append_journal(
            timestamp,
            action=action,
            actor=actor,
            category=category,
            note=note,
        )
        return [
            PetNotice(
                category="event",
                name=CAMERA_EVENT_CARE_LOGGED,
                timestamp=timestamp,
                data={"action": action, "actor": actor, "category": category, "note": note},
            )
        ]

    def queue_action_approval(
        self,
        now: datetime,
        *,
        action_name: str,
        category: str,
        payload: dict[str, Any],
        requested_by: str | None = None,
        note: str | None = None,
        source: str = "manual",
    ) -> list[PetNotice]:
        """Queue a critical action for approval instead of executing it."""
        approval_id = f"{self.profile.pet_id}:approval:{len(self.state.pending_approvals) + 1}:{int(now.timestamp())}"
        record = {
            CONF_APPROVAL_ID: approval_id,
            CONF_ACTION_NAME: action_name,
            CONF_ROUTINE_CATEGORY: category,
            "created_at": now.isoformat(),
            "requested_by": requested_by,
            "source": source,
            "note": note,
            "payload": dict(payload),
            "status": "pending",
        }
        self.state.pending_approvals.append(record)
        self.state.pending_approvals = self.state.pending_approvals[-100:]
        self._append_journal(
            now.isoformat(),
            action="approval_requested",
            actor=requested_by,
            category=category,
            note=note or action_name,
            data=record,
        )
        return [
            PetNotice(
                category="event",
                name=CAMERA_EVENT_APPROVAL_REQUESTED,
                timestamp=now.isoformat(),
                data=record,
            )
        ]

    def approve_pending_action(
        self,
        now: datetime,
        approval_id: str,
        *,
        approved_by: str | None = None,
        note: str | None = None,
    ) -> tuple[dict[str, Any], list[PetNotice]]:
        """Approve a queued action and return its stored payload."""
        for index, record in enumerate(self.state.pending_approvals):
            if record.get(CONF_APPROVAL_ID) != approval_id:
                continue
            approval = dict(record)
            approval["approved_at"] = now.isoformat()
            approval[CONF_APPROVED_BY] = approved_by
            if note:
                approval["approval_note"] = note
            del self.state.pending_approvals[index]
            self._append_journal(
                now.isoformat(),
                action="approval_granted",
                actor=approved_by,
                category=str(approval.get(CONF_ROUTINE_CATEGORY, "operations")),
                note=note or str(approval.get(CONF_ACTION_NAME)),
                data=approval,
            )
            return approval, [
                PetNotice(
                    category="event",
                    name=CAMERA_EVENT_ACTION_APPROVED,
                    timestamp=now.isoformat(),
                    data=approval,
                )
            ]
        raise ValueError("Unknown approval id")

    def complete_checklist_item(
        self,
        now: datetime,
        checklist_id: str,
        *,
        actor: str | None = None,
        note: str | None = None,
        source: str = "manual",
    ) -> list[PetNotice]:
        """Mark a checklist item complete for its current period."""
        item = next((entry for entry in self.profile.checklist_items if entry.checklist_id == checklist_id), None)
        if item is None:
            raise ValueError("Unknown checklist item")
        period_key = _checklist_period_key(item.frequency, now)
        record = {
            "checklist_id": checklist_id,
            "label": item.label,
            "frequency": item.frequency,
            "completed_at": now.isoformat(),
            "actor": actor,
            "note": note,
            "source": source,
            "period_key": period_key,
        }
        self.state.checklist_completions = [
            entry
            for entry in self.state.checklist_completions
            if not (entry.get("checklist_id") == checklist_id and entry.get("period_key") == period_key)
        ]
        self.state.checklist_completions.append(record)
        self.state.checklist_completions = self.state.checklist_completions[-200:]
        self._append_journal(
            now.isoformat(),
            action="checklist_completed",
            actor=actor,
            category=item.category,
            note=note or item.label,
            data=record,
        )
        return [
            PetNotice(
                category="event",
                name=CAMERA_EVENT_CHECKLIST_COMPLETED,
                timestamp=now.isoformat(),
                data=record,
            )
        ]

    def log_medication_dose(
        self,
        now: datetime,
        medication_name: str,
        *,
        dose: str | None = None,
        actor: str | None = None,
        note: str | None = None,
    ) -> list[PetNotice]:
        """Record that a medication dose was administered."""
        course = next(
            (item for item in self.profile.medication_courses if item.name.lower() == medication_name.strip().lower()),
            None,
        )
        effective_name = course.name if course else medication_name.strip()
        effective_dose = dose or (course.dose if course else None) or "recorded"
        timestamp = now.isoformat()
        self.state.medication_log.append(
            {
                "medication_name": effective_name,
                "dose": effective_dose,
                "timestamp": timestamp,
                "actor": actor,
                "note": note,
            }
        )
        self.state.medication_log = self.state.medication_log[-JOURNAL_RECORD_LIMIT:]
        self._append_journal(
            timestamp,
            action="medication_given",
            actor=actor,
            category=ROUTINE_TYPE_MEDICATION,
            note=note or effective_name,
            data={"medication_name": effective_name, "dose": effective_dose},
        )
        return [
            PetNotice(
                category="event",
                name="medication_logged",
                timestamp=timestamp,
                data={"medication_name": effective_name, "dose": effective_dose, "actor": actor},
            )
        ]

    def log_symptom(
        self,
        now: datetime,
        symptom_name: str,
        *,
        severity_score: float,
        note: str | None = None,
        source: str = "manual",
        duration_hours: float | None = None,
    ) -> list[PetNotice]:
        """Record a symptom observation."""
        timestamp = now.isoformat()
        severity = max(1.0, min(5.0, float(severity_score)))
        normalized_duration = None if duration_hours is None else max(0.1, float(duration_hours))
        self.state.symptom_log.append(
            {
                "symptom_name": symptom_name.strip(),
                "severity_score": severity,
                "timestamp": timestamp,
                "note": note,
                "source": source,
                CONF_DURATION_HOURS: normalized_duration,
            }
        )
        self.state.symptom_log = self.state.symptom_log[-JOURNAL_RECORD_LIMIT:]
        self._append_journal(
            timestamp,
            action="symptom_logged",
            category="health",
            note=note or symptom_name,
            data={
                "symptom_name": symptom_name.strip(),
                "severity_score": severity,
                "source": source,
                CONF_DURATION_HOURS: normalized_duration,
            },
        )
        notices = [
            PetNotice(
                category="event",
                name="symptom_logged",
                timestamp=timestamp,
                data={
                    "symptom_name": symptom_name.strip(),
                    "severity_score": severity,
                    "source": source,
                    CONF_DURATION_HOURS: normalized_duration,
                },
            )
        ]
        if severity >= 4.0:
            notices.append(
                PetNotice(
                    category="anomaly",
                    name=ANOMALY_SYMPTOM_ESCALATION,
                    timestamp=timestamp,
                    severity="critical" if severity >= 4.5 else "warning",
                    message=f"Symptom severity increased: {symptom_name.strip()}",
                    data={
                        "symptom_name": symptom_name.strip(),
                        "severity_score": severity,
                        "source": source,
                        CONF_DURATION_HOURS: normalized_duration,
                    },
                )
            )
        return notices

    def start_recovery_plan(
        self,
        now: datetime,
        title: str,
        *,
        expected_days: int,
        note: str | None = None,
    ) -> list[PetNotice]:
        """Start or replace the active recovery plan."""
        expected_days = max(1, int(expected_days))
        timestamp = now.isoformat()
        self.state.active_recovery_plan = {
            "title": title.strip(),
            "started_at": timestamp,
            "expected_end": (now + timedelta(days=expected_days)).isoformat(),
            "expected_days": expected_days,
            "note": note,
            "status": "active",
        }
        if self.state.manual_mode == OPERATION_MODE_NORMAL:
            self.state.manual_mode = OPERATION_MODE_ILLNESS
        self._append_journal(
            timestamp,
            action="recovery_plan_started",
            category="health",
            note=note or title.strip(),
            data={"title": title.strip(), "expected_days": expected_days},
        )
        return [
            PetNotice(
                category="event",
                name="recovery_plan_started",
                timestamp=timestamp,
                data={"title": title.strip(), "expected_days": expected_days},
            )
        ]

    def complete_vaccine_dose(
        self,
        now: datetime,
        *,
        dose_id: str | None = None,
        vaccine_name: str | None = None,
        note: str | None = None,
    ) -> list[PetNotice]:
        """Mark a vaccine dose as completed."""
        target = self._find_vaccine_entry(now.date(), dose_id=dose_id, vaccine_name=vaccine_name)
        if target is None:
            raise ValueError("Unknown vaccine dose")
        self.state.completed_vaccine_doses[target.dose_id] = now.date().isoformat()
        self.state.vaccine_runtime_overrides.pop(target.dose_id, None)
        self._append_journal(
            now.isoformat(),
            action="vaccine_completed",
            category="health",
            note=note or target.vaccine_name,
            data={"vaccine_dose_id": target.dose_id, "vaccine_name": target.vaccine_name},
        )
        return [
            PetNotice(
                category="event",
                name="vaccine_completed",
                timestamp=now.isoformat(),
                data={"vaccine_dose_id": target.dose_id, "vaccine_name": target.vaccine_name},
            )
        ]

    def reschedule_vaccine(
        self,
        now: datetime,
        *,
        dose_id: str | None = None,
        vaccine_name: str | None = None,
        due_date: date,
        note: str | None = None,
    ) -> list[PetNotice]:
        """Override a vaccine due date."""
        target = self._find_vaccine_entry(now.date(), dose_id=dose_id, vaccine_name=vaccine_name)
        if target is None:
            raise ValueError("Unknown vaccine dose")
        override = self.state.vaccine_runtime_overrides.setdefault(target.dose_id, {})
        override.update(
            {
                CONF_DUE_DATE: due_date.isoformat(),
                CONF_VACCINE_STATUS: "scheduled",
                CONF_NOTES: note,
            }
        )
        self._append_journal(
            now.isoformat(),
            action="vaccine_rescheduled",
            category="health",
            note=note or target.vaccine_name,
            data={"vaccine_dose_id": target.dose_id, "due_date": due_date.isoformat()},
        )
        return [
            PetNotice(
                category="event",
                name="vaccine_rescheduled",
                timestamp=now.isoformat(),
                data={
                    "vaccine_dose_id": target.dose_id,
                    "vaccine_name": target.vaccine_name,
                    "due_date": due_date.isoformat(),
                },
            )
        ]

    def cancel_vaccine(
        self,
        now: datetime,
        *,
        dose_id: str | None = None,
        vaccine_name: str | None = None,
        reason: str | None = None,
    ) -> list[PetNotice]:
        """Cancel a vaccine reminder."""
        target = self._find_vaccine_entry(now.date(), dose_id=dose_id, vaccine_name=vaccine_name)
        if target is None:
            raise ValueError("Unknown vaccine dose")
        override = self.state.vaccine_runtime_overrides.setdefault(target.dose_id, {})
        override.update(
            {
                CONF_VACCINE_STATUS: "canceled",
                CONF_REASON: reason,
            }
        )
        self._append_journal(
            now.isoformat(),
            action="vaccine_canceled",
            category="health",
            note=reason or target.vaccine_name,
            data={"vaccine_dose_id": target.dose_id},
        )
        return [
            PetNotice(
                category="event",
                name="vaccine_canceled",
                timestamp=now.isoformat(),
                data={
                    "vaccine_dose_id": target.dose_id,
                    "vaccine_name": target.vaccine_name,
                    "reason": reason,
                },
            )
        ]

    def observe_behavior(
        self,
        now: datetime,
        behavior_type: str,
        *,
        severity: str = "warning",
        source: str = "manual",
        confidence: float = 1.0,
        duration_seconds: int | None = None,
        model_name: str | None = None,
        message: str | None = None,
        evidence: dict[str, Any] | None = None,
    ) -> list[PetNotice]:
        """Record a normalized behavior observation with provenance."""
        normalized = normalize_behavior_type(behavior_type)
        observation = BehaviorObservation(
            observation_type=normalized,
            timestamp=now.isoformat(),
            severity=severity,
            source=source,
            confidence=max(0.0, min(1.0, float(confidence))),
            duration_seconds=max(1, int(duration_seconds)) if duration_seconds is not None else None,
            model_name=_coerce_optional_str(model_name),
            message=message,
            evidence=dict(evidence or {}),
        )
        self.state.behavior_observations.append(observation.as_dict())
        self.state.behavior_observations = self.state.behavior_observations[-JOURNAL_RECORD_LIMIT:]
        self._append_journal(
            observation.timestamp,
            action="behavior_observed",
            category="behavior",
            note=message or normalized,
            data=observation.as_dict(),
        )
        notices = [
            PetNotice(
                category="event",
                name=CAMERA_EVENT_BEHAVIOR_OBSERVED,
                timestamp=observation.timestamp,
                data=observation.as_dict(),
            )
        ]
        if normalized in {
            ANOMALY_VOMITING,
            ANOMALY_LIMPING,
            ANOMALY_GAIT,
            ANOMALY_COUGH,
            ANOMALY_RESTLESSNESS,
        }:
            notices.append(
                PetNotice(
                    category="anomaly",
                    name=normalized,
                    timestamp=observation.timestamp,
                    severity=severity,
                    message=message or _default_behavior_message(normalized),
                    data=observation.as_dict(),
                )
            )
        return notices

    def report_behavior(
        self,
        now: datetime,
        behavior_type: str,
        *,
        severity: str = "warning",
        message: str | None = None,
        source: str = "manual",
    ) -> list[PetNotice]:
        """Register an observed behavior issue."""
        normalized = normalize_behavior_type(behavior_type)
        timestamp = now.isoformat()
        report = {
            "type": normalized,
            "severity": severity,
            "message": message,
            "source": source,
            "timestamp": timestamp,
        }
        self.state.behavior_reports.append(report)
        self.state.behavior_reports = self.state.behavior_reports[-RECENT_RECORD_LIMIT:]
        observed_notices = self.observe_behavior(
            now,
            behavior_type,
            severity=severity,
            source=source,
            confidence=1.0,
            message=message,
        )
        anomaly_notices = [notice for notice in observed_notices if notice.category == "anomaly"]
        event_notices = [notice for notice in observed_notices if notice.category != "anomaly"]
        return [
            PetNotice(
                category="event",
                name=CAMERA_EVENT_BEHAVIOR_REPORTED,
                timestamp=timestamp,
                data={"type": normalized, "severity": severity, "source": source},
            ),
            *anomaly_notices,
            *event_notices,
        ]

    def apply_camera_analysis(self, now: datetime, analysis: CameraAnalysis) -> list[PetNotice]:
        """Apply camera-derived signals to runtime state."""
        notices: list[PetNotice] = []
        timestamp = now.isoformat()

        if analysis.frame_motion_score > 0:
            self.state.activity_points_today += min(2.5, analysis.frame_motion_score * 10)

        if analysis.food_empty is not None and analysis.food_empty != self.state.food_bowl_empty:
            self.state.food_bowl_empty = analysis.food_empty
            if analysis.food_empty:
                notices.append(PetNotice(category="event", name=CAMERA_EVENT_FOOD_EMPTY, timestamp=timestamp))

        if analysis.water_empty is not None and analysis.water_empty != self.state.water_bowl_empty:
            self.state.water_bowl_empty = analysis.water_empty
            if analysis.water_empty:
                notices.append(PetNotice(category="event", name=CAMERA_EVENT_WATER_EMPTY, timestamp=timestamp))

        if analysis.food_interaction and self._interaction_allowed(now, self.state.last_seen_eating_at):
            self.state.last_seen_eating_at = timestamp
            self._mark_activity(now)
            notices.append(
                PetNotice(
                    category="event",
                    name=CAMERA_EVENT_EATING,
                    timestamp=timestamp,
                    data={"motion_score": round(analysis.food_motion_score, 3)},
                )
            )
            if self.state.pending_meal_grams > 0:
                eaten_grams = round(self.state.pending_meal_grams, 1)
                food_name = self.state.pending_food_name
                meal_type = self.state.pending_meal_type
                kcal_per_gram = self.state.pending_food_kcal_per_gram or DEFAULT_KCAL_PER_GRAM
                self.state.food_today_grams += eaten_grams
                if meal_type:
                    _increment_counter(self.state.food_eaten_today_by_type, meal_type, eaten_grams)
                if food_name:
                    _increment_counter(self.state.food_today_grams_by_food, food_name, eaten_grams)
                calories = round(eaten_grams * kcal_per_gram, 1)
                self.state.calories_consumed_today += calories
                if meal_type == MEAL_TYPE_TREAT:
                    self.state.treat_calories_today += calories
                self.state.pending_meal_grams = 0.0
                self.state.pending_meal_type = None
                self.state.pending_food_name = None
                self.state.pending_food_kcal_per_gram = None
                self.state.pending_meal_served_at = None
                notices.append(
                    PetNotice(
                        category="event",
                        name=CAMERA_EVENT_FOOD_EATEN,
                        timestamp=timestamp,
                        data={
                            "grams": eaten_grams,
                            "meal_type": meal_type,
                            "food_name": food_name,
                            "calories": calories,
                        },
                    )
                )

        if analysis.water_interaction and self._interaction_allowed(now, self.state.last_drinking_at):
            drank = round(max(5.0, DEFAULT_WATER_SIP_ML * (1 + analysis.water_motion_score)), 1)
            self.state.water_today_ml += drank
            self.state.last_drinking_at = timestamp
            self._mark_activity(now)
            notices.append(
                PetNotice(
                    category="event",
                    name=CAMERA_EVENT_DRINKING,
                    timestamp=timestamp,
                    data={"milliliters": drank, "motion_score": round(analysis.water_motion_score, 3)},
                )
            )

        return notices

    def refresh(self, now: datetime, context: PetContext | None = None) -> tuple[PetSnapshot, list[PetNotice]]:
        """Advance runtime state and produce the latest snapshot."""
        context = context or PetContext()
        notices: list[PetNotice] = []
        self._roll_day_if_needed(now)
        self._accumulate_sleep(now)
        notices.extend(self._track_mobility(now, context))

        if self.state.pending_meal_served_at:
            pending_since = _parse_datetime(self.state.pending_meal_served_at)
            if pending_since and now - pending_since >= timedelta(minutes=DEFAULT_FOOD_IGNORE_MINUTES):
                ignored = round(self.state.pending_meal_grams, 1)
                if ignored > 0:
                    if self.state.pending_meal_type:
                        _increment_counter(self.state.food_ignored_today_by_type, self.state.pending_meal_type, ignored)
                    self.state.food_ignored_today_grams += ignored
                    notices.append(
                        PetNotice(
                            category="event",
                            name=CAMERA_EVENT_FOOD_IGNORED,
                            timestamp=now.isoformat(),
                            data={
                                "grams": ignored,
                                "meal_type": self.state.pending_meal_type,
                                "food_name": self.state.pending_food_name,
                            },
                        )
                    )
                self.state.pending_meal_grams = 0.0
                self.state.pending_meal_type = None
                self.state.pending_food_name = None
                self.state.pending_food_kcal_per_gram = None
                self.state.pending_meal_served_at = None

        active_modes = self._active_modes(context)
        notices.extend(self._emit_due_schedule_notices(now, context))

        next_feeding_at = self.routines.next_feeding_at(now, context)
        next_walk_at = self.routines.next_walk_at(now, context)
        next_care_at = self._resolve_next_care(now, context)
        next_medication_at = self._resolve_next_medication(now, context)
        next_vet_visit_at = self._resolve_next_vet_visit(now, context)
        next_vaccine_at = self.medical.next_vaccine_at(now.date())
        weight_trend = self._weight_trend_kg(now)
        vaccine_status = self.medical.vaccine_status(now)
        active_medications = tuple(
            sorted(course.name for course in self.profile.medication_courses if course.is_active_on(now.date()))
        )
        overdue_medications = tuple(sorted(self._overdue_medication_names(now)))
        recovery_status = self.medical.recovery_status(now)
        recovery_progress_pct = self.medical.recovery_progress_pct(now)
        symptom_severity = self.medical.symptom_severity(now)
        hungry = bool(next_feeding_at and now >= _parse_datetime(next_feeding_at))
        needs_walk = self.profile.species.lower() == "dog" and self.routines.needs_walk(now, context)
        activity_level = round(min(100.0, self.state.activity_points_today * 4.0), 1)
        sleep_duration_hours = round(self.state.sleep_minutes_today / 60.0, 2)
        feeding_quality_score = self.nutrition.feeding_quality_score()
        active_transition = self.profile.active_food_transition(now.date())
        walk_distance_km = round(_route_distance_km(self.state.current_walk_route), 3)
        walk_distance_today_km = self.mobility.walk_distance_today_km(now)
        last_walk_summary = self.state.last_walk_summary or {}
        preferred_rooms, avoided_rooms = self.mobility.room_preferences()
        separation_score = self.mobility.separation_score(now, context)
        inactivity_duration_minutes = self.behavior.inactivity_duration_minutes(now)
        sleep_quality_score = self.behavior.sleep_quality_score(now)
        latest_behavior_observation_at = self._latest_behavior_observation_at()
        current_shift = self._current_shift(now)
        next_shift = self._next_shift(now)
        checklist_progress_pct, pending_checklist_items = self._checklist_progress(now)
        today_vs_baseline = self._today_vs_baseline_summary(
            activity_level=activity_level,
            sleep_duration_hours=sleep_duration_hours,
        )
        weekly_summary = self._weekly_summary(now)
        operations_summary = self._operations_summary(
            current_shift=current_shift,
            pending_approvals_count=len(self.state.pending_approvals),
            checklist_progress_pct=checklist_progress_pct,
            pending_checklist_items=pending_checklist_items,
        )
        recommended_portion = self.nutrition.recommended_portion_grams()
        health_score = round(
            max(
                0.0,
                min(
                    100.0,
                    _calculate_health_score(
                        food_ratio=(
                            self.state.calories_consumed_today / max(self.state.daily_calories, 1.0)
                            if self.state.calories_consumed_today > 0
                            else self.state.food_today_grams / max(recommended_portion, 1.0)
                        ),
                        water_ratio=(self.state.water_today_ml / max(daily_water_target_ml(self.state.weight_kg), 1.0)),
                        activity_ratio=activity_level / 100.0,
                        anomaly_count=len(self.state.active_anomalies),
                    ),
                    - abs(self.profile.body_condition_score - 5.0) * 3.0
                    - symptom_severity * 0.2
                    - len(self.profile.chronic_conditions) * 2.0,
                    - max(0.0, abs(weight_trend) - 0.2) * 4.0,
                ),
            ),
            1,
        )

        snapshot = PetSnapshot(
            pet_id=self.profile.pet_id,
            name=self.profile.name,
            species=self.profile.species,
            breed=self.profile.breed,
            birthdate=self.profile.birthdate.isoformat(),
            weight_kg=round(self.state.weight_kg, 2),
            diet_mode=self.state.diet_mode,
            food_today_grams=round(self.state.food_today_grams, 1),
            water_today_ml=round(self.state.water_today_ml, 1),
            last_feeding_at=self.state.last_feeding_at,
            next_feeding_at=next_feeding_at,
            next_walk_at=next_walk_at,
            next_care_at=next_care_at,
            next_vet_visit_at=next_vet_visit_at,
            last_seen_eating_at=self.state.last_seen_eating_at,
            activity_level=activity_level,
            sleep_duration_hours=sleep_duration_hours,
            sleep_quality_score=sleep_quality_score,
            health_score=health_score,
            stress_score=round(self.state.stress_score, 1),
            feeding_quality_score=feeding_quality_score,
            recommended_food_portion_grams=recommended_portion,
            daily_calories=round(self.state.daily_calories, 1),
            calories_consumed_today=round(self.state.calories_consumed_today, 1),
            treat_calories_today=round(self.state.treat_calories_today, 1),
            next_medication_at=next_medication_at,
            next_vaccine_at=next_vaccine_at,
            active_medications=active_medications,
            overdue_medications=overdue_medications,
            vaccine_status=vaccine_status,
            recovery_status=recovery_status,
            recovery_progress_pct=recovery_progress_pct,
            symptom_severity_score=symptom_severity,
            body_condition_score=round(self.profile.body_condition_score, 1),
            weight_trend_kg=weight_trend,
            weight_goal_min_kg=self.state.weight_goal_min_kg,
            weight_goal_max_kg=self.state.weight_goal_max_kg,
            chronic_conditions=tuple(condition.name for condition in self.profile.chronic_conditions),
            food_portion_grams=round(self.state.food_portion_grams, 1),
            hungry=hungry,
            needs_walk=needs_walk,
            food_bowl_empty=self.state.food_bowl_empty,
            water_bowl_empty=self.state.water_bowl_empty,
            sleeping=self.state.sleeping,
            anomaly_detected=bool(self.state.active_anomalies),
            routine_status=self._build_routine_status(
                next_feeding_at,
                next_walk_at,
                next_care_at,
                next_medication_at,
                next_vet_visit_at,
                active_modes,
            ),
            active_food_transition=active_transition.summary() if active_transition else None,
            operation_mode=self.state.manual_mode,
            active_modes=active_modes,
            current_zone=context.current_zone or self.state.current_zone,
            geofence_breached=context.geofence_breached or self.state.geofence_breached,
            distance_from_safe_zone_m=context.distance_from_safe_zone_m,
            current_room=context.current_room or self.state.current_room,
            room_presence_sources=context.room_presence_sources,
            walk_distance_km=walk_distance_km,
            walk_distance_today_km=walk_distance_today_km,
            last_walk_distance_km=round(float(last_walk_summary.get("distance_km", 0.0)), 3),
            last_walk_duration_minutes=round(float(last_walk_summary.get("duration_minutes", 0.0)), 1),
            last_walk_route_summary=last_walk_summary.get("route_summary"),
            separation_score=separation_score,
            inactivity_duration_minutes=inactivity_duration_minutes,
            baseline_drift_score=round(self.state.latest_baseline_drift_score, 1),
            behavior_profile=self.state.latest_behavior_profile,
            behavior_summary=self.state.latest_behavior_summary,
            current_shift=current_shift,
            next_shift_at=next_shift.isoformat() if next_shift is not None else None,
            pending_approvals_count=len(self.state.pending_approvals),
            checklist_progress_pct=checklist_progress_pct,
            pending_checklist_items=pending_checklist_items,
            today_vs_baseline=today_vs_baseline,
            weekly_summary=weekly_summary,
            operations_summary=operations_summary,
            calendar_sync_status=self._calendar_sync_status(),
            calendar_conflicts_count=len(self.state.calendar_conflicts),
            generated_reports_count=len(self.state.generated_reports),
            stress_factors=tuple(self.state.latest_behavior_factors),
            subtle_anomalies=tuple(),
            latest_behavior_observation_at=latest_behavior_observation_at,
            preferred_rooms=preferred_rooms,
            avoided_rooms=avoided_rooms,
            active_anomalies=tuple(sorted(self.state.active_anomalies)),
            camera_enabled=bool(self.profile.camera_entity_id),
        )
        self.state.last_tick_at = now.isoformat()
        self.state.feeding_quality_score = feeding_quality_score
        return snapshot, notices

    def append_records(self, notices: list[PetNotice]) -> None:
        """Append notices to the recent record buffer."""
        if not notices:
            return
        self.state.recent_records.extend(notice.as_dict() for notice in notices)
        self.state.recent_records = self.state.recent_records[-RECENT_RECORD_LIMIT:]

    def update_active_anomalies(self, active_anomalies: dict[str, str]) -> None:
        """Update active anomalies tracked by the engine."""
        self.state.active_anomalies = dict(active_anomalies)

    def update_recommendations_sent(self, keys: set[str]) -> None:
        """Persist deduplicated recommendations state."""
        self.state.sent_recommendations_today = sorted(keys)

    def set_stress_score(self, score: float) -> None:
        """Persist the derived stress score."""
        self.state.stress_score = round(max(0.0, min(100.0, score)), 1)

    def is_calendar_event_synced(self, calendar_entity_id: str, event_key: str) -> bool:
        """Return if the event was already synced to the external calendar."""
        return event_key in self.state.calendar_sync_registry.get(calendar_entity_id, [])

    def mark_calendar_event_synced(self, calendar_entity_id: str, event_key: str) -> None:
        """Track that an external calendar event has been created."""
        synced = self.state.calendar_sync_registry.setdefault(calendar_entity_id, [])
        if event_key not in synced:
            synced.append(event_key)
            self.state.calendar_sync_registry[calendar_entity_id] = synced[-200:]

    def record_calendar_sync_state(
        self,
        calendar_entity_id: str,
        *,
        sync_key: str,
        external_uid: str | None,
        event_payload: ScheduledEvent | None,
        direction: str,
        state: str,
        source_of_truth: str,
        last_seen_at: datetime,
    ) -> None:
        """Persist sync metadata for an external calendar event."""
        calendar_state = self.state.calendar_sync_state.setdefault(
            calendar_entity_id,
            {"events": {}, "last_sync_state": "idle"},
        )
        events = calendar_state.setdefault("events", {})
        payload_hash = _scheduled_event_hash(event_payload) if event_payload is not None else None
        events[sync_key] = {
            "sync_key": sync_key,
            "external_uid": external_uid,
            "last_payload_hash": payload_hash,
            "last_direction": direction,
            "last_state": state,
            "source_of_truth": source_of_truth,
            "last_seen_at": last_seen_at.isoformat(),
            "event": event_payload.as_dict() if event_payload is not None else None,
        }
        if len(events) > 400:
            keys = list(events)[:-400]
            for key in keys:
                events.pop(key, None)
        calendar_state["last_sync_state"] = state
        calendar_state["source_of_truth"] = source_of_truth
        calendar_state["last_sync_at"] = last_seen_at.isoformat()

    def set_calendar_polled_at(self, calendar_entity_id: str, when: datetime) -> None:
        """Track when a linked calendar was last polled for inbound changes."""
        calendar_state = self.state.calendar_sync_state.setdefault(
            calendar_entity_id,
            {"events": {}, "last_sync_state": "idle"},
        )
        calendar_state["last_polled_at"] = when.isoformat()

    def last_calendar_polled_at(self, calendar_entity_id: str) -> datetime | None:
        """Return when the linked calendar was last polled."""
        calendar_state = self.state.calendar_sync_state.get(calendar_entity_id) or {}
        return _parse_datetime(calendar_state.get("last_polled_at"))

    def upsert_calendar_override(
        self,
        calendar_entity_id: str,
        *,
        sync_key: str,
        mode: str,
        event: ScheduledEvent | None,
        external_uid: str | None,
        source_of_truth: str,
        imported_at: datetime,
    ) -> list[PetNotice]:
        """Apply or replace an imported calendar override."""
        record = {
            "calendar_entity_id": calendar_entity_id,
            "sync_key": sync_key,
            "mode": mode,
            "external_uid": external_uid,
            "source_of_truth": source_of_truth,
            "imported_at": imported_at.isoformat(),
            "event": event.as_dict() if event is not None else None,
        }
        self.state.calendar_import_overrides = [
            item
            for item in self.state.calendar_import_overrides
            if not (
                item.get("calendar_entity_id") == calendar_entity_id
                and item.get("sync_key") == sync_key
            )
        ]
        self.state.calendar_import_overrides.append(record)
        self.state.calendar_import_overrides = self.state.calendar_import_overrides[-300:]
        self._append_journal(
            imported_at.isoformat(),
            action="calendar_imported",
            category="calendar",
            note=f"{mode}:{sync_key}",
            data=record,
        )
        return [
            PetNotice(
                category="event",
                name=CAMERA_EVENT_CALENDAR_IMPORTED,
                timestamp=imported_at.isoformat(),
                data={
                    "calendar_entity_id": calendar_entity_id,
                    "sync_key": sync_key,
                    "mode": mode,
                    "external_uid": external_uid,
                    "source_of_truth": source_of_truth,
                },
            )
        ]

    def clear_calendar_override(self, calendar_entity_id: str, sync_key: str) -> None:
        """Remove a stored imported calendar override."""
        self.state.calendar_import_overrides = [
            item
            for item in self.state.calendar_import_overrides
            if not (
                item.get("calendar_entity_id") == calendar_entity_id
                and item.get("sync_key") == sync_key
            )
        ]

    def calendar_override_record(
        self,
        calendar_entity_id: str,
        sync_key: str,
    ) -> dict[str, Any] | None:
        """Return a stored calendar override for a specific calendar link and sync key."""
        for item in reversed(self.state.calendar_import_overrides):
            if (
                item.get("calendar_entity_id") == calendar_entity_id
                and item.get("sync_key") == sync_key
            ):
                return item
        return None

    def find_calendar_conflict(self, conflict_id: str) -> dict[str, Any] | None:
        """Return a tracked calendar conflict by id."""
        for item in reversed(self.state.calendar_conflicts):
            if item.get("conflict_id") == conflict_id:
                return item
        return None

    def clear_calendar_conflict(self, conflict_id: str) -> dict[str, Any] | None:
        """Remove and return a single calendar conflict."""
        removed: dict[str, Any] | None = None
        remaining: list[dict[str, Any]] = []
        for item in self.state.calendar_conflicts:
            if item.get("conflict_id") == conflict_id and removed is None:
                removed = item
                continue
            remaining.append(item)
        self.state.calendar_conflicts = remaining
        return removed

    def clear_calendar_conflicts_for_sync(self, calendar_entity_id: str, sync_key: str) -> None:
        """Clear all open conflicts for a specific calendar link and sync key."""
        self.state.calendar_conflicts = [
            item
            for item in self.state.calendar_conflicts
            if not (
                item.get("calendar_entity_id") == calendar_entity_id
                and item.get("sync_key") == sync_key
            )
        ]

    def record_calendar_conflict(
        self,
        calendar_entity_id: str,
        *,
        sync_key: str,
        conflict_type: str,
        reason: str,
        source_of_truth: str,
        external_uid: str | None,
        base_event: ScheduledEvent | None,
        effective_event: ScheduledEvent | None,
        external_event: dict[str, Any] | None,
        occurred_at: datetime,
    ) -> list[PetNotice]:
        """Persist a calendar sync conflict."""
        conflict_signature = _calendar_conflict_signature(
            calendar_entity_id=calendar_entity_id,
            sync_key=sync_key,
            conflict_type=conflict_type,
            reason=reason,
            base_event=base_event,
            effective_event=effective_event,
            external_event=external_event,
        )
        if any(item.get("conflict_signature") == conflict_signature for item in self.state.calendar_conflicts):
            return []
        if self._is_calendar_conflict_suppressed(conflict_signature):
            return []

        self.clear_calendar_conflicts_for_sync(calendar_entity_id, sync_key)
        record = {
            "conflict_id": _calendar_conflict_id(calendar_entity_id, sync_key, conflict_type, occurred_at),
            "calendar_entity_id": calendar_entity_id,
            "sync_key": sync_key,
            "conflict_type": conflict_type,
            "conflict_signature": conflict_signature,
            "reason": reason,
            "source_of_truth": source_of_truth,
            "external_uid": external_uid,
            "occurred_at": occurred_at.isoformat(),
            "base_event": base_event.as_dict() if base_event is not None else None,
            "effective_event": effective_event.as_dict() if effective_event is not None else None,
            "external_event": dict(external_event) if external_event is not None else None,
        }
        self.state.calendar_conflicts.append(record)
        self.state.calendar_conflicts = self.state.calendar_conflicts[-120:]
        self._append_journal(
            occurred_at.isoformat(),
            action="calendar_conflict",
            category="calendar",
            note=reason,
            data=record,
        )
        return [
            PetNotice(
                category="event",
                name=CAMERA_EVENT_CALENDAR_CONFLICT,
                timestamp=occurred_at.isoformat(),
                severity="warning",
                message=reason,
                data=record,
            )
        ]

    def resolve_calendar_conflict(
        self,
        conflict_id: str,
        *,
        resolution: str,
        resolved_at: datetime,
        actor: str | None = None,
        note: str | None = None,
    ) -> list[PetNotice]:
        """Resolve a tracked calendar conflict and record the outcome."""
        if resolution not in {
            CALENDAR_CONFLICT_RESOLUTION_DIVA_WINS,
            CALENDAR_CONFLICT_RESOLUTION_CALENDAR_WINS,
            CALENDAR_CONFLICT_RESOLUTION_DISMISS,
        }:
            raise ValueError(f"Unsupported calendar conflict resolution: {resolution}")
        conflict = self.clear_calendar_conflict(conflict_id)
        if conflict is None:
            return []
        resolution_record = {
            "conflict_id": conflict_id,
            "calendar_entity_id": conflict.get("calendar_entity_id"),
            "sync_key": conflict.get("sync_key"),
            "conflict_signature": conflict.get("conflict_signature"),
            "resolution": resolution,
            "resolved_at": resolved_at.isoformat(),
            "actor": actor,
            "note": note,
        }
        self.state.calendar_conflict_resolutions.append(resolution_record)
        self.state.calendar_conflict_resolutions = self.state.calendar_conflict_resolutions[-200:]
        self._append_journal(
            resolved_at.isoformat(),
            action="calendar_conflict_resolved",
            category="calendar",
            note=f"{resolution}:{conflict.get('sync_key')}",
            data={**conflict, **resolution_record},
        )
        return [
            PetNotice(
                category="event",
                name=CAMERA_EVENT_CALENDAR_CONFLICT_RESOLVED,
                timestamp=resolved_at.isoformat(),
                data={
                    "conflict_id": conflict_id,
                    "calendar_entity_id": conflict.get("calendar_entity_id"),
                    "sync_key": conflict.get("sync_key"),
                    "resolution": resolution,
                    "actor": actor,
                    "note": note,
                },
            )
        ]

    def _is_calendar_conflict_suppressed(self, conflict_signature: str) -> bool:
        """Return whether a dismissed conflict should stay suppressed until it changes."""
        return any(
            item.get("resolution") == CALENDAR_CONFLICT_RESOLUTION_DISMISS
            and item.get("conflict_signature") == conflict_signature
            for item in self.state.calendar_conflict_resolutions
        )

    def timeline_events(
        self,
        start: datetime,
        end: datetime,
        context: PetContext | None = None,
        *,
        include_calendar_overrides: bool = True,
    ) -> list[ScheduledEvent]:
        """Return the effective timeline for a window."""
        context = context or PetContext()
        active_modes = self._active_modes(context)
        events = self.profile.upcoming_events(start, end)
        events.extend(self._medication_events(start, end))
        events.extend(self._vaccine_events(start, end))
        exceptions = self._schedule_exceptions()
        filtered: list[ScheduledEvent] = []
        for event in events:
            if event.category == ROUTINE_TYPE_VET:
                filtered.append(event)
                continue
            if any(_exception_skips_event(exception, event) for exception in exceptions):
                continue
            filtered.append(_apply_modes_to_event(event, active_modes, context))

        tzinfo = start.tzinfo or end.tzinfo
        for exception in exceptions:
            exception_event = exception.to_event(self.profile.pet_id, tzinfo)
            if exception_event is None:
                continue
            if not (start <= exception_event.start < end):
                continue
            filtered.append(_apply_modes_to_event(exception_event, active_modes, context))

        if include_calendar_overrides:
            filtered = self._apply_calendar_overrides(filtered, start, end)

        filtered.sort(key=lambda item: item.start)
        return filtered

    def _medication_events(self, start: datetime, end: datetime) -> list[ScheduledEvent]:
        events: list[ScheduledEvent] = []
        for course in self.profile.medication_courses:
            events.extend(course.occurrences(self.profile.pet_id, start, end))
        return events

    def _vaccine_events(self, start: datetime, end: datetime) -> list[ScheduledEvent]:
        tzinfo = start.tzinfo or end.tzinfo
        if tzinfo is None:
            return []
        events: list[ScheduledEvent] = []
        for item in self._effective_vaccine_plan(start.date()):
            event = item.to_event(self.profile.pet_id, tzinfo, None)
            if event is not None and event.start < end and event.end > start:
                events.append(event)
        return events

    def _next_vaccine_due(self, today: date) -> str | None:
        candidates: list[date] = []
        for item in self._effective_vaccine_plan(today):
            due_date = item.next_due_date(None)
            if due_date is not None:
                candidates.append(due_date)
        if not candidates:
            return None
        return min(candidates).isoformat()

    def _effective_vaccine_plan(self, today: date) -> tuple[VaccinePlanEntry, ...]:
        """Return vaccine entries with completion and runtime overrides applied."""
        entries: list[VaccinePlanEntry] = []
        for item in self.profile.vaccine_plan(today):
            runtime_override = self.state.vaccine_runtime_overrides.get(item.dose_id, {})
            status = str(runtime_override.get(CONF_VACCINE_STATUS, "scheduled"))
            if status == "canceled":
                continue
            completed_at = _parse_date_optional(self.state.completed_vaccine_doses.get(item.dose_id))
            due_date = item.next_due_date(completed_at)
            if due_date is None:
                continue
            if runtime_override.get(CONF_DUE_DATE):
                due_date = _parse_date(runtime_override[CONF_DUE_DATE])
            notes = item.notes
            if runtime_override.get(CONF_NOTES):
                notes = f"{notes or ''}\nOverride: {runtime_override[CONF_NOTES]}".strip()
            entries.append(
                VaccinePlanEntry(
                    dose_id=item.dose_id,
                    vaccine_name=item.vaccine_name,
                    due_date=due_date,
                    category=item.category,
                    source=item.source,
                    recurrence_months=item.recurrence_months,
                    notes=notes,
                )
            )
        return tuple(sorted(entries, key=lambda item: (item.due_date, item.vaccine_name)))

    def _find_vaccine_entry(
        self,
        today: date,
        *,
        dose_id: str | None = None,
        vaccine_name: str | None = None,
    ) -> VaccinePlanEntry | None:
        """Locate a vaccine entry by id or human name."""
        plan = self._effective_vaccine_plan(today)
        if dose_id:
            return next((item for item in plan if item.dose_id == dose_id), None)
        if vaccine_name:
            matches = [item for item in plan if item.vaccine_name.lower() == vaccine_name.strip().lower()]
            if matches:
                return sorted(matches, key=lambda item: item.due_date)[0]
        return None

    def _overdue_medication_names(self, now: datetime) -> list[str]:
        overdue: list[str] = []
        for course in self.profile.medication_courses:
            if not course.is_active_on(now.date()):
                continue
            for slot in course.times:
                scheduled_at = datetime.combine(now.date(), slot, tzinfo=now.tzinfo)
                if scheduled_at > now:
                    continue
                if now - scheduled_at > timedelta(hours=2) and not _medication_taken_around(
                    self.state.medication_log,
                    course.name,
                    scheduled_at,
                    window_minutes=150,
                ):
                    overdue.append(course.name)
                    break
        return overdue

    def _symptom_severity(self, now: datetime) -> float:
        score = 0.0
        for entry in self.state.symptom_log[-40:]:
            observed_at = _parse_datetime(entry.get("timestamp"))
            if observed_at is None:
                continue
            age_hours = max(0.0, (now - observed_at).total_seconds() / 3600.0)
            if age_hours > 168:
                continue
            raw = float(entry.get("severity_score", 0.0))
            weight = max(0.15, 1.0 - age_hours / 168.0)
            score = max(score, raw * 20.0 * weight)
        return max(0.0, min(100.0, score))

    def _recovery_status(self, now: datetime) -> str:
        plan = self.state.active_recovery_plan
        if not plan:
            return "none"
        expected_end = _parse_datetime(plan.get("expected_end"))
        if expected_end is not None and now > expected_end:
            return "overdue"
        return str(plan.get("status", "active"))

    def _recovery_progress_pct(self, now: datetime) -> float:
        """Estimate recovery plan progress relative to its expected duration."""
        plan = self.state.active_recovery_plan
        if not plan:
            return 0.0
        started_at = _parse_datetime(plan.get("started_at"))
        expected_end = _parse_datetime(plan.get("expected_end"))
        if started_at is None or expected_end is None or expected_end <= started_at:
            return 0.0
        total = (expected_end - started_at).total_seconds()
        elapsed = max(0.0, min(total, (now - started_at).total_seconds()))
        return round(max(0.0, min(100.0, (elapsed / total) * 100.0)), 1)

    def _walk_distance_today_km(self, now: datetime) -> float:
        """Return today's total walked distance including the active walk."""
        total = 0.0
        for entry in self.state.journal_entries[-120:]:
            if entry.get("action") != "finish_walk":
                continue
            timestamp = _parse_datetime(entry.get("timestamp"))
            if timestamp is None or timestamp.date() != now.date():
                continue
            total += float(dict(entry.get("data") or {}).get("distance_km", 0.0))
        total += _route_distance_km(self.state.current_walk_route)
        return round(total, 3)

    def _weight_trend_kg(self, now: datetime) -> float:
        history = []
        for entry in self.state.weight_history[-60:]:
            observed_at = _parse_datetime(entry.get("timestamp"))
            if observed_at is None or now - observed_at > timedelta(days=14):
                continue
            history.append(entry)
        if not history:
            return 0.0
        return round(float(self.state.weight_kg) - float(history[0].get("weight_kg", self.state.weight_kg)), 2)

    def _vaccine_status(self, now: datetime) -> str:
        next_due = self._next_vaccine_due(now.date())
        if not next_due:
            return "clear"
        due_date = _parse_date_optional(next_due)
        if due_date is None:
            return "unknown"
        if due_date < now.date():
            return "overdue"
        if due_date <= now.date() + timedelta(days=14):
            return "due_soon"
        return "scheduled"

    def _current_shift(self, now: datetime) -> str | None:
        """Return the active caregiver shift summary."""
        for shift in self.profile.care_shifts:
            if shift.is_active(now):
                role = f" ({shift.role})" if shift.role else ""
                return f"{shift.label}: {shift.caregiver}{role}"
        return None

    def _next_shift(self, now: datetime) -> datetime | None:
        """Return the next caregiver shift start."""
        candidates = [shift.next_start(now) for shift in self.profile.care_shifts]
        future = [candidate for candidate in candidates if candidate is not None]
        if not future:
            return None
        return min(future)

    def _checklist_progress(self, now: datetime) -> tuple[float, tuple[str, ...]]:
        """Return checklist completion percent and pending labels."""
        due_items = self._due_checklist_items(now)
        if not due_items:
            return 100.0, ()
        completed = 0
        pending: list[str] = []
        for item in due_items:
            if self._is_checklist_complete(item, now):
                completed += 1
            else:
                pending.append(item.label)
        return round((completed / len(due_items)) * 100.0, 1), tuple(pending)

    def _due_checklist_items(self, now: datetime) -> tuple[ChecklistItem, ...]:
        """Return currently due checklist items."""
        return tuple(self.profile.checklist_items)

    def _is_checklist_complete(self, item: ChecklistItem, now: datetime) -> bool:
        """Return whether the checklist item is complete for the current period."""
        period_key = _checklist_period_key(item.frequency, now)
        return any(
            entry.get("checklist_id") == item.checklist_id and entry.get("period_key") == period_key
            for entry in self.state.checklist_completions
        )

    def _today_vs_baseline_summary(self, *, activity_level: float, sleep_duration_hours: float) -> str:
        """Compare today's metrics with the recent baseline."""
        history = self.state.daily_history[-7:]
        if not history:
            return "No baseline yet"
        baseline_food = sum(float(item.get("food_today_grams", 0.0)) for item in history) / len(history)
        baseline_activity = sum(float(item.get("activity_points_today", 0.0)) for item in history) / len(history) * 4.0
        baseline_sleep = sum(float(item.get("sleep_minutes_today", 0.0)) for item in history) / len(history) / 60.0
        food_delta = round(self.state.food_today_grams - baseline_food, 1)
        activity_delta = round(activity_level - baseline_activity, 1)
        sleep_delta = round(sleep_duration_hours - baseline_sleep, 1)
        return f"Food {food_delta:+} g, activity {activity_delta:+}%, sleep {sleep_delta:+} h"

    def _weekly_summary(self, now: datetime) -> str:
        """Build a compact weekly operations summary."""
        history = self.state.daily_history[-7:]
        if not history:
            return "No weekly summary yet"
        avg_food = round(sum(float(item.get("food_today_grams", 0.0)) for item in history) / len(history), 1)
        avg_water = round(sum(float(item.get("water_today_ml", 0.0)) for item in history) / len(history), 1)
        avg_activity = round(sum(float(item.get("activity_points_today", 0.0)) for item in history) / len(history) * 4.0, 1)
        approvals = len([entry for entry in self.state.journal_entries[-80:] if entry.get("action") == "approval_granted"])
        completed_checklists = len(
            [entry for entry in self.state.checklist_completions if _parse_datetime(entry.get("completed_at")) and now - _parse_datetime(entry.get("completed_at")) <= timedelta(days=7)]
        )
        summary = (
            f"7d avg food {avg_food} g, water {avg_water} mL, activity {avg_activity}%, "
            f"approved actions {approvals}, checklist completions {completed_checklists}"
        )
        self.state.latest_weekly_summary = summary
        return summary

    def _operations_summary(
        self,
        *,
        current_shift: str | None,
        pending_approvals_count: int,
        checklist_progress_pct: float,
        pending_checklist_items: Sequence[str],
    ) -> str:
        """Return a compact operations center summary string."""
        shift_summary = current_shift or "No active shift"
        checklist_summary = f"{checklist_progress_pct:.0f}% checklist"
        approval_summary = f"{pending_approvals_count} approvals"
        pending_summary = f"{len(pending_checklist_items)} pending tasks"
        return " | ".join((shift_summary, checklist_summary, approval_summary, pending_summary))

    def _calendar_sync_status(self) -> str:
        """Return a compact status label for linked calendar health."""
        if not self.profile.external_calendar_entity_ids:
            return "not_linked"
        if self.state.calendar_conflicts:
            return "attention"
        sync_states = [
            str(item.get("last_sync_state", "")).strip().lower()
            for item in self.state.calendar_sync_state.values()
            if isinstance(item, dict) and str(item.get("last_sync_state", "")).strip()
        ]
        if not sync_states:
            return "idle"
        if any(state.startswith("imported") for state in sync_states):
            return "imported"
        if any(state in {"created", "updated", "deleted", "recreated"} for state in sync_states):
            return "changed"
        if any(state.startswith("synced") for state in sync_states):
            return "synced"
        return sync_states[-1]

    def build_vet_report(self, now: datetime, snapshot: PetSnapshot, *, history_days: int = 30) -> dict[str, Any]:
        """Build a text-first veterinary summary package."""
        history = self.state.daily_history[-max(1, history_days):]
        vaccine_plan = self._effective_vaccine_plan(now.date())
        pending_vaccines = [
            item
            for item in vaccine_plan
            if item.next_due_date(None) is not None
        ]
        lines = [
            "DIVA Veterinary Summary",
            f"Generated: {now.isoformat()}",
            f"Pet: {self.profile.name}",
            f"Species/Breed: {self.profile.species} / {self.profile.breed}",
            f"Birthdate: {self.profile.birthdate.isoformat()}",
            f"Weight: {snapshot.weight_kg} kg",
            f"Weight trend (14d): {snapshot.weight_trend_kg:+.2f} kg",
            f"Weight goal range: {snapshot.weight_goal_min_kg or 'n/a'} - {snapshot.weight_goal_max_kg or 'n/a'} kg",
            f"Body condition score: {snapshot.body_condition_score}/9",
            f"Primary vet: {self.profile.primary_vet or 'n/a'}",
            f"Vet phone: {self.profile.vet_phone or 'n/a'}",
            f"Passport: {self.profile.passport_number or 'n/a'}",
            f"Microchip: {self.profile.microchip_id or 'n/a'}",
            f"Insurance: {self.profile.insurance_policy or 'n/a'}",
            f"Vaccine profile: {self.profile.vaccine_profile}",
            f"Regional policy: {self.profile.regional_policy}",
            f"Vet override enabled: {'yes' if self.profile.vet_override else 'no'}",
            "",
            "Current status",
            f"- Health score: {snapshot.health_score}",
            f"- Stress score: {snapshot.stress_score}",
            f"- Food today: {snapshot.food_today_grams} g",
            f"- Water today: {snapshot.water_today_ml} mL",
            f"- Activity level: {snapshot.activity_level}%",
            f"- Sleep: {snapshot.sleep_duration_hours} h",
            f"- Sleep quality: {snapshot.sleep_quality_score}%",
            f"- Recovery status: {snapshot.recovery_status}",
            f"- Symptom severity: {snapshot.symptom_severity_score}",
            f"- Behavior profile: {snapshot.behavior_profile or 'n/a'}",
            f"- Behavior summary: {snapshot.behavior_summary or 'n/a'}",
            "",
            "Active medications",
        ]
        if self.profile.medication_courses:
            for course in self.profile.medication_courses:
                lines.append(
                    f"- {course.name}: {course.dose} at {', '.join(slot.strftime('%H:%M') for slot in course.times)}"
                )
        else:
            lines.append("- none")
        lines.extend(["", "Chronic conditions"])
        if self.profile.chronic_conditions:
            for condition in self.profile.chronic_conditions:
                lines.append(
                    f"- {condition.name}: {condition.status} (review every {condition.monitor_interval_days} days)"
                )
        else:
            lines.append("- none")
        lines.extend(["", "Diagnoses"])
        if self.profile.diagnoses:
            for diagnosis in self.profile.diagnoses:
                diagnosed_on = diagnosis.diagnosed_on.isoformat() if diagnosis.diagnosed_on is not None else "n/a"
                suffix = f" | {diagnosis.notes}" if diagnosis.notes else ""
                lines.append(f"- {diagnosis.name}: {diagnosis.status} (diagnosed {diagnosed_on}){suffix}")
        else:
            lines.append("- none")
        lines.extend(["", "Allergies"])
        if self.profile.allergies:
            for allergy in self.profile.allergies:
                reaction = allergy.reaction or "reaction not specified"
                suffix = f" | {allergy.notes}" if allergy.notes else ""
                lines.append(f"- {allergy.allergen}: {reaction}{suffix}")
        else:
            lines.append("- none")
        lines.extend(["", "Contraindications"])
        if self.profile.contraindications:
            for contraindication in self.profile.contraindications:
                reason = contraindication.reason or "reason not specified"
                suffix = f" | {contraindication.notes}" if contraindication.notes else ""
                lines.append(f"- {contraindication.item}: {reason}{suffix}")
        else:
            lines.append("- none")
        lines.extend(["", "Recent symptoms"])
        recent_symptoms = [
            item for item in self.state.symptom_log[-20:] if _parse_datetime(item.get("timestamp")) is not None
        ]
        if recent_symptoms:
            for item in recent_symptoms[-10:]:
                duration = _parse_optional_float(item.get(CONF_DURATION_HOURS))
                duration_text = f", duration {duration:.1f} h" if duration is not None else ""
                note = _coerce_optional_str(item.get("note"))
                note_text = f" | {note}" if note else ""
                lines.append(
                    f"- {item.get('timestamp')}: {item.get('symptom_name')} severity {item.get('severity_score')} ({item.get('source')}{duration_text}){note_text}"
                )
        else:
            lines.append("- none")
        lines.extend(["", "Vaccination plan"])
        if pending_vaccines:
            for item in pending_vaccines:
                due_date = item.next_due_date(None)
                lines.append(f"- {item.vaccine_name}: due {due_date.isoformat() if due_date else 'n/a'} ({item.source})")
        else:
            lines.append("- none")
        lines.extend(["", "Weight history"])
        if self.state.weight_history:
            for item in self.state.weight_history[-10:]:
                lines.append(
                    f"- {item.get('timestamp')}: {item.get('weight_kg')} kg ({item.get('source', 'manual')})"
                )
        else:
            lines.append("- none")
        lines.extend(["", "Medical history"])
        if self.profile.medical_history:
            for entry in self.profile.medical_history[-10:]:
                suffix = f" | {entry.notes}" if entry.notes else ""
                lines.append(f"- {entry.history_date.isoformat()}: [{entry.category}] {entry.title}{suffix}")
        else:
            lines.append("- none")
        lines.extend(["", "Recent day history"])
        if history:
            for item in history[-10:]:
                lines.append(
                    f"- {item.get('date')}: food {item.get('food_today_grams', 0)} g, water {item.get('water_today_ml', 0)} mL, activity {item.get('activity_points_today', 0)} pts"
                )
        else:
            lines.append("- none")

        caption = f"{self.profile.name}: vet summary from DIVA"
        return {
            "filename": f"{self.profile.pet_id}_{now.strftime('%Y%m%d_%H%M%S')}_vet_report.txt",
            "content": "\n".join(lines) + "\n",
            "caption": caption,
            "summary": {
                "pending_vaccines": [item.vaccine_name for item in pending_vaccines],
                "active_medications": list(snapshot.active_medications),
                "chronic_conditions": list(snapshot.chronic_conditions),
                "diagnoses": [item.name for item in self.profile.diagnoses],
                "allergies": [item.allergen for item in self.profile.allergies],
                "contraindications": [item.item for item in self.profile.contraindications],
                "recovery_status": snapshot.recovery_status,
            },
        }

    def build_operations_report(self, now: datetime, snapshot: PetSnapshot, *, history_days: int = 7) -> dict[str, Any]:
        """Build an operations-focused summary package."""
        history = self.state.daily_history[-max(1, history_days):]
        lines = [
            "DIVA Operations Summary",
            f"Generated: {now.isoformat()}",
            f"Pet: {self.profile.name}",
            f"Current shift: {snapshot.current_shift or 'none'}",
            f"Next shift: {snapshot.next_shift_at or 'n/a'}",
            f"Checklist progress: {snapshot.checklist_progress_pct}%",
            f"Pending approvals: {snapshot.pending_approvals_count}",
            f"Today vs baseline: {snapshot.today_vs_baseline or 'n/a'}",
            f"Weekly summary: {snapshot.weekly_summary or 'n/a'}",
            "",
            "Pending checklist items",
        ]
        if snapshot.pending_checklist_items:
            for item in snapshot.pending_checklist_items:
                lines.append(f"- {item}")
        else:
            lines.append("- none")
        lines.extend(["", "Pending approvals"])
        if self.state.pending_approvals:
            for item in self.state.pending_approvals[-20:]:
                lines.append(
                    f"- {item.get(CONF_APPROVAL_ID)}: {item.get(CONF_ACTION_NAME)} requested by {item.get('requested_by') or 'unknown'}"
                )
        else:
            lines.append("- none")
        lines.extend(["", "Recent audit log"])
        for item in self.state.journal_entries[-20:]:
            lines.append(
                f"- {item.get('timestamp')}: {item.get('action')} ({item.get('category')}) by {item.get('actor') or 'system'}"
            )
        lines.extend(["", "Recent history"])
        for item in history:
            lines.append(
                f"- {item.get('date')}: food {item.get('food_today_grams', 0)} g, activity {item.get('activity_points_today', 0)} pts, sleep {item.get('sleep_minutes_today', 0)} min"
            )
        return {
            "filename": f"{self.profile.pet_id}_{now.strftime('%Y%m%d_%H%M%S')}_operations_report.txt",
            "content": "\n".join(lines) + "\n",
            "caption": f"{self.profile.name}: operations summary from DIVA",
            "summary": {
                "pending_approvals_count": snapshot.pending_approvals_count,
                "checklist_progress_pct": snapshot.checklist_progress_pct,
                "current_shift": snapshot.current_shift,
            },
        }

    def _resolve_next_feeding(self, now: datetime, context: PetContext | None = None) -> str | None:
        if self.state.manual_next_feeding_at:
            manual = _parse_datetime(self.state.manual_next_feeding_at)
            if manual and manual > now:
                return manual.isoformat()
            self.state.manual_next_feeding_at = None
        event = self._next_timeline_event(now, ROUTINE_TYPE_FEED, context)
        return event.start.isoformat() if event else None

    def _compute_next_feeding(self, now: datetime, skip_slots: int = 0, context: PetContext | None = None) -> str | None:
        future = self._future_timeline_events(now, ROUTINE_TYPE_FEED, context, limit=max(1, skip_slots + 1))
        if not future:
            return None
        index = min(skip_slots, len(future) - 1)
        return future[index].start.isoformat()

    def _resolve_next_walk(self, now: datetime, context: PetContext | None = None) -> str | None:
        event = self._next_timeline_event(now, ROUTINE_TYPE_WALK, context)
        return event.start.isoformat() if event else None

    def _resolve_next_care(self, now: datetime, context: PetContext | None = None) -> str | None:
        event = self._next_timeline_event(now, "care_group", context)
        return event.start.isoformat() if event else None

    def _resolve_next_medication(self, now: datetime, context: PetContext | None = None) -> str | None:
        event = self._next_timeline_event(now, ROUTINE_TYPE_MEDICATION, context)
        return event.start.isoformat() if event else None

    def _resolve_next_vet_visit(self, now: datetime, context: PetContext | None = None) -> str | None:
        event = self._next_timeline_event(now, ROUTINE_TYPE_VET, context)
        return event.start.isoformat() if event else None

    def _interaction_allowed(self, now: datetime, last_seen: str | None) -> bool:
        previous = _parse_datetime(last_seen)
        if previous is None:
            return True
        return now - previous >= timedelta(minutes=DEFAULT_INTERACTION_COOLDOWN_MINUTES)

    def _needs_walk(self, now: datetime, context: PetContext | None = None) -> bool:
        if self.state.walk_active:
            return False
        if self.profile.walk_routines:
            previous_due = self._latest_timeline_event(now, ROUTINE_TYPE_WALK, context)
            if previous_due is None:
                return False
            last_walk = _parse_datetime(self.state.last_walk_finished_at)
            return last_walk is None or last_walk < previous_due.start
        last_walk = _parse_datetime(self.state.last_walk_finished_at)
        if last_walk is None:
            return True
        return now - last_walk >= timedelta(hours=8)

    def _track_mobility(self, now: datetime, context: PetContext) -> list[PetNotice]:
        """Persist mobility context and emit room/zone notices."""
        notices: list[PetNotice] = []
        last_tick = _parse_datetime(self.state.last_tick_at) or now
        elapsed_minutes = max(0.0, min(5.0, (now - last_tick).total_seconds() / 60.0))

        if self.state.current_room and elapsed_minutes > 0:
            self.state.room_dwell_today_minutes[self.state.current_room] = round(
                self.state.room_dwell_today_minutes.get(self.state.current_room, 0.0) + elapsed_minutes,
                1,
            )
        if context.home_alone and elapsed_minutes > 0:
            self.state.separation_minutes_today = round(self.state.separation_minutes_today + elapsed_minutes, 1)

        point = self._gps_point(context)
        if point is not None:
            self._append_gps_point(now, point)
            if self.state.walk_active:
                self._append_walk_point(now, point)

        if context.current_room and context.current_room != self.state.current_room:
            previous_room = self.state.current_room
            self.state.current_room = context.current_room
            self.state.room_history.append(
                {
                    "timestamp": now.isoformat(),
                    "room_name": context.current_room,
                    "previous_room": previous_room,
                    "sources": list(context.room_presence_sources),
                }
            )
            self.state.room_history = self.state.room_history[-120:]
            notices.append(
                PetNotice(
                    category="event",
                    name=CAMERA_EVENT_ROOM_CHANGED,
                    timestamp=now.isoformat(),
                    data={
                        "room_name": context.current_room,
                        "previous_room": previous_room,
                        "sources": list(context.room_presence_sources),
                    },
                )
            )

        if context.current_zone != self.state.current_zone:
            previous_zone = self.state.current_zone
            self.state.current_zone = context.current_zone
            if context.current_zone:
                _increment_counter(self.state.zone_visits_today, context.current_zone, 1)
            notices.append(
                PetNotice(
                    category="event",
                    name=CAMERA_EVENT_ZONE_CHANGED,
                    timestamp=now.isoformat(),
                    data={
                        "zone_name": context.current_zone,
                        "previous_zone": previous_zone,
                        "distance_from_safe_zone_m": context.distance_from_safe_zone_m,
                    },
                )
            )

        if context.geofence_breached != self.state.geofence_breached:
            self.state.geofence_breached = context.geofence_breached
            if context.geofence_breached:
                notices.append(
                    PetNotice(
                        category="event",
                        name=CAMERA_EVENT_GEOFENCE_BREACH,
                        timestamp=now.isoformat(),
                        data={
                            "zone_name": context.current_zone,
                            "distance_from_safe_zone_m": context.distance_from_safe_zone_m,
                        },
                    )
                )
                notices.append(
                    PetNotice(
                        category="anomaly",
                        name=ANOMALY_GEOFENCE_BREACH,
                        timestamp=now.isoformat(),
                        severity="warning",
                        message="Pet is outside configured safe zones.",
                        data={
                            "zone_name": context.current_zone,
                            "distance_from_safe_zone_m": context.distance_from_safe_zone_m,
                        },
                    )
                )
            else:
                notices.append(
                    PetNotice(
                        category="event",
                        name=CAMERA_EVENT_GEOFENCE_CLEARED,
                        timestamp=now.isoformat(),
                        data={"zone_name": context.current_zone},
                    )
                )
        return notices

    def _mark_activity(self, now: datetime) -> None:
        if self.state.sleeping:
            self.state.sleep_interruptions_today += 1
        self.state.last_activity_at = now.isoformat()
        self.state.sleeping = False
        hour_key = str(now.hour)
        self.state.active_minutes_by_hour[hour_key] = round(
            self.state.active_minutes_by_hour.get(hour_key, 0.0) + 1.0,
            1,
        )

    def _roll_day_if_needed(self, now: datetime) -> None:
        if self.state.current_day == now.date().isoformat():
            return
        self.state.daily_history.append(
            {
                "date": self.state.current_day,
                "food_today_grams": round(self.state.food_today_grams, 1),
                "water_today_ml": round(self.state.water_today_ml, 1),
                "activity_points_today": round(self.state.activity_points_today, 1),
                "sleep_minutes_today": round(self.state.sleep_minutes_today, 1),
                "stress_score": round(self.state.stress_score, 1),
                "calories_consumed_today": round(self.state.calories_consumed_today, 1),
                "treat_calories_today": round(self.state.treat_calories_today, 1),
                "feeding_quality_score": round(self.state.feeding_quality_score, 1),
                "room_dwell_today_minutes": dict(self.state.room_dwell_today_minutes),
                "zone_visits_today": dict(self.state.zone_visits_today),
                "separation_minutes_today": round(self.state.separation_minutes_today, 1),
                "sleep_interruptions_today": self.state.sleep_interruptions_today,
                "active_minutes_by_hour": dict(self.state.active_minutes_by_hour),
                "sleep_minutes_by_hour": dict(self.state.sleep_minutes_by_hour),
            }
        )
        self.state.daily_history = self.state.daily_history[-DAILY_HISTORY_LIMIT:]
        self.state.current_day = now.date().isoformat()
        self.state.food_today_grams = 0.0
        self.state.water_today_ml = 0.0
        self.state.food_served_today_grams = 0.0
        self.state.food_ignored_today_grams = 0.0
        self.state.calories_consumed_today = 0.0
        self.state.treat_calories_today = 0.0
        self.state.food_eaten_today_by_type = {}
        self.state.food_served_today_by_type = {}
        self.state.food_ignored_today_by_type = {}
        self.state.food_today_grams_by_food = {}
        self.state.activity_points_today = 0.0
        self.state.sleep_minutes_today = 0.0
        self.state.sent_recommendations_today = []
        self.state.active_anomalies = {}
        self.state.stress_score = 0.0
        self.state.feeding_quality_score = 100.0
        self.state.room_dwell_today_minutes = {}
        self.state.zone_visits_today = {}
        self.state.separation_minutes_today = 0.0
        self.state.sleep_interruptions_today = 0
        self.state.active_minutes_by_hour = {}
        self.state.sleep_minutes_by_hour = {}
        self.state.emitted_schedule_keys = [
            key for key in self.state.emitted_schedule_keys if not key.endswith(f":{now.date().isoformat()}")
        ][-200:]

    def _accumulate_sleep(self, now: datetime) -> None:
        last_tick = _parse_datetime(self.state.last_tick_at) or now
        inactive_since = _parse_datetime(self.state.last_activity_at)
        self.state.sleeping = bool(
            inactive_since
            and not self.state.walk_active
            and now - inactive_since >= timedelta(minutes=DEFAULT_SLEEP_AFTER_MINUTES)
        )
        if self.state.sleeping:
            elapsed_minutes = max(0.0, (now - last_tick).total_seconds() / 60.0)
            slept = min(elapsed_minutes, 5.0)
            self.state.sleep_minutes_today += slept
            hour_key = str(now.hour)
            self.state.sleep_minutes_by_hour[hour_key] = round(
                self.state.sleep_minutes_by_hour.get(hour_key, 0.0) + slept,
                1,
            )

    def _emit_due_schedule_notices(self, now: datetime, context: PetContext | None = None) -> list[PetNotice]:
        notices: list[PetNotice] = []
        window_start = now - timedelta(minutes=SCHEDULE_DUE_WINDOW_MINUTES)
        routine_events = self.timeline_events(window_start, now + timedelta(minutes=1), context)
        for event in routine_events:
            if event.start > now:
                continue
            if event.category == ROUTINE_TYPE_VET:
                if now - event.start > timedelta(minutes=VET_REMINDER_WINDOW_MINUTES):
                    continue
                event_key = f"vet:{event.event_id}:{event.start.isoformat()}"
                if event_key in self.state.emitted_schedule_keys:
                    continue
                notices.append(
                    PetNotice(
                        category="event",
                        name=CAMERA_EVENT_VET_DUE,
                        timestamp=now.isoformat(),
                        data={
                            "summary": event.summary,
                            "scheduled_for": event.start.isoformat(),
                            "location": event.location,
                        },
                    )
                )
                self.state.emitted_schedule_keys.append(event_key)
                continue

            if now - event.start > timedelta(minutes=SCHEDULE_DUE_WINDOW_MINUTES):
                continue
            event_key = f"routine:{event.event_id}:{event.start.date().isoformat()}"
            if event_key in self.state.emitted_schedule_keys:
                continue
            notices.append(
                PetNotice(
                    category="event",
                    name=CAMERA_EVENT_ROUTINE_DUE,
                    timestamp=now.isoformat(),
                    data={
                        "routine_category": event.category,
                        "summary": event.summary,
                        "scheduled_for": event.start.isoformat(),
                        "active_modes": list(event.metadata.get("active_modes", [])),
                    },
                )
            )
            self.state.emitted_schedule_keys.append(event_key)

        self.state.emitted_schedule_keys = self.state.emitted_schedule_keys[-200:]
        return notices

    def _build_routine_status(
        self,
        next_feeding_at: str | None,
        next_walk_at: str | None,
        next_care_at: str | None,
        next_medication_at: str | None,
        next_vet_visit_at: str | None,
        active_modes: tuple[str, ...],
    ) -> str | None:
        candidates = [
            ("Feeding", _parse_datetime(next_feeding_at)),
            ("Walk", _parse_datetime(next_walk_at)),
            ("Care", _parse_datetime(next_care_at)),
            ("Medication", _parse_datetime(next_medication_at)),
            ("Vet", _parse_datetime(next_vet_visit_at)),
        ]
        future = [(label, value) for label, value in candidates if value is not None]
        if not future:
            return None
        label, value = min(future, key=lambda item: item[1])
        suffix = f" [{' / '.join(active_modes)}]" if active_modes else ""
        return f"{label} at {value.strftime('%H:%M')}{suffix}"

    def _active_modes(self, context: PetContext) -> tuple[str, ...]:
        modes: list[str] = []
        manual_mode = _parse_manual_mode(self.state.manual_mode or self.profile.default_manual_mode)
        if manual_mode != OPERATION_MODE_NORMAL:
            modes.append(manual_mode)
        if self.profile.weather_adaptation and context.outside_temperature_c is not None:
            if context.outside_temperature_c >= self.profile.heat_threshold_c:
                modes.append("heat")
            elif context.outside_temperature_c <= self.profile.cold_threshold_c:
                modes.append("winter")
        if context.home_alone:
            modes.append("home_alone")
        return tuple(dict.fromkeys(modes))

    def _apply_calendar_overrides(
        self,
        events: list[ScheduledEvent],
        start: datetime,
        end: datetime,
    ) -> list[ScheduledEvent]:
        """Apply imported calendar overrides to the effective timeline."""
        by_key = {event.event_id: event for event in events}
        resolved: list[ScheduledEvent] = []
        for event in events:
            override = self._calendar_override(event.event_id)
            if override is None:
                resolved.append(event)
                continue
            mode = str(override.get("mode", "")).strip()
            if mode == "skip":
                continue
            imported = _scheduled_event_from_override(
                override,
                default_pet_id=self.profile.pet_id,
                fallback=event,
            )
            resolved.append(imported or event)

        for override in self.state.calendar_import_overrides:
            if str(override.get("mode", "")).strip() != "custom":
                continue
            sync_key = str(override.get("sync_key", "")).strip()
            if not sync_key or sync_key in by_key:
                continue
            imported = _scheduled_event_from_override(override, default_pet_id=self.profile.pet_id, fallback=None)
            if imported is None:
                continue
            if imported.start < end and imported.end > start:
                resolved.append(imported)
        return resolved

    def _calendar_override(self, sync_key: str) -> dict[str, Any] | None:
        """Return a stored imported override by DIVA sync key."""
        for item in reversed(self.state.calendar_import_overrides):
            if item.get("sync_key") == sync_key:
                return item
        return None

    def _schedule_exceptions(self) -> tuple[ScheduleException, ...]:
        runtime_exceptions = parse_schedule_exceptions(
            self.state.runtime_routine_exceptions,
            pet_id=self.profile.pet_id,
        )
        active: list[ScheduleException] = []
        today = date.today()
        for exception in self.profile.routine_exceptions + runtime_exceptions:
            if exception.exception_date >= today - timedelta(days=1):
                active.append(exception)
        return tuple(active)

    def _future_timeline_events(
        self,
        now: datetime,
        category: str,
        context: PetContext | None,
        *,
        limit: int = 5,
    ) -> list[ScheduledEvent]:
        future = [
            event
            for event in self.timeline_events(now, now + timedelta(days=8), context)
            if event.start > now and _event_matches_category(event, category)
        ]
        return future[:limit]

    def _next_timeline_event(
        self,
        now: datetime,
        category: str,
        context: PetContext | None,
    ) -> ScheduledEvent | None:
        future = self._future_timeline_events(now, category, context, limit=1)
        return future[0] if future else None

    def _latest_timeline_event(
        self,
        now: datetime,
        category: str,
        context: PetContext | None,
    ) -> ScheduledEvent | None:
        due_events = [
            event
            for event in self.timeline_events(now - timedelta(days=2), now + timedelta(minutes=1), context)
            if event.start <= now and _event_matches_category(event, category)
        ]
        if not due_events:
            return None
        return max(due_events, key=lambda item: item.start)

    def _append_journal(
        self,
        timestamp: str,
        *,
        action: str,
        category: str,
        actor: str | None = None,
        note: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        entry: dict[str, Any] = {
            "timestamp": timestamp,
            "action": action,
            "category": category,
        }
        if actor:
            entry["actor"] = actor
        if note:
            entry["note"] = note
        if data:
            entry["data"] = dict(data)
        self.state.journal_entries.append(entry)
        self.state.journal_entries = self.state.journal_entries[-JOURNAL_RECORD_LIMIT:]

    def _gps_point(self, context: PetContext) -> tuple[float, float] | None:
        """Return the current GPS point if available."""
        if context.gps_latitude is None or context.gps_longitude is None:
            return None
        return (context.gps_latitude, context.gps_longitude)

    def _append_gps_point(self, now: datetime, point: tuple[float, float]) -> None:
        """Persist a GPS point in runtime history."""
        last_point = self.state.gps_history[-1] if self.state.gps_history else None
        if last_point is not None:
            last_ts = _parse_datetime(last_point.get("timestamp"))
            last_lat = _coerce_float(last_point.get("latitude"))
            last_lon = _coerce_float(last_point.get("longitude"))
            if (
                last_ts is not None
                and last_lat is not None
                and last_lon is not None
                and now - last_ts < timedelta(minutes=5)
                and _haversine_m(last_lat, last_lon, point[0], point[1]) < 15.0
            ):
                return
        self.state.gps_history.append(
            {
                "timestamp": now.isoformat(),
                "latitude": round(point[0], 6),
                "longitude": round(point[1], 6),
            }
        )
        self.state.gps_history = self.state.gps_history[-400:]

    def _append_walk_point(self, now: datetime, point: tuple[float, float]) -> None:
        """Persist a GPS point into the active walk route."""
        last_point = self.state.current_walk_route[-1] if self.state.current_walk_route else None
        if last_point is not None:
            last_lat = _coerce_float(last_point.get("latitude"))
            last_lon = _coerce_float(last_point.get("longitude"))
            if last_lat is not None and last_lon is not None and _haversine_m(last_lat, last_lon, point[0], point[1]) < 8.0:
                return
        self.state.current_walk_route.append(
            {
                "timestamp": now.isoformat(),
                "latitude": round(point[0], 6),
                "longitude": round(point[1], 6),
            }
        )
        self.state.current_walk_route = self.state.current_walk_route[-200:]

    def _room_preferences(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Return preferred and avoided rooms from the recent dwell history."""
        dwell: dict[str, float] = {}
        for item in self.state.daily_history[-7:]:
            for room_name, minutes in dict(item.get("room_dwell_today_minutes", {})).items():
                dwell[room_name] = dwell.get(room_name, 0.0) + float(minutes)
        for room_name, minutes in self.state.room_dwell_today_minutes.items():
            dwell[room_name] = dwell.get(room_name, 0.0) + float(minutes)

        preferred = tuple(
            room_name
            for room_name, minutes in sorted(dwell.items(), key=lambda item: item[1], reverse=True)[:3]
            if minutes > 0 and (max(dwell.values(), default=0.0) == 0 or minutes >= max(dwell.values(), default=0.0) * 0.3)
        )
        top_minutes = max(dwell.values(), default=0.0)
        known_rooms = {
            source.room_name for source in self.profile.room_presence_sources
        }
        if self.profile.camera_room_name:
            known_rooms.add(self.profile.camera_room_name)
        avoided = tuple(
            room
            for room in sorted(known_rooms)
            if room not in preferred and (dwell.get(room, 0.0) < 15.0 or (top_minutes > 0 and dwell.get(room, 0.0) <= top_minutes * 0.2))
        )
        return preferred, avoided[:3]

    def _separation_score(self, now: datetime, context: PetContext) -> float:
        """Estimate separation pressure from time alone and location context."""
        score = min(60.0, self.state.separation_minutes_today / 4.0)
        if context.home_alone:
            score += 15.0
        if context.geofence_breached:
            score += 25.0
        if self.state.current_room and self.state.room_dwell_today_minutes.get(self.state.current_room, 0.0) >= 180.0:
            score += 10.0
        return max(0.0, min(100.0, score))

    def _inactivity_duration_minutes(self, now: datetime) -> float:
        """Return the current inactivity streak in minutes."""
        last_activity = _parse_datetime(self.state.last_activity_at)
        if last_activity is None:
            return 0.0
        return max(0.0, (now - last_activity).total_seconds() / 60.0)

    def _sleep_quality_score(self, now: datetime) -> float:
        """Estimate sleep quality from duration, interruptions, and baseline."""
        baseline_hours = 0.0
        sample = self.state.daily_history[-7:]
        if sample:
            baseline_hours = sum(float(item.get("sleep_minutes_today", 0.0)) for item in sample) / len(sample) / 60.0
        baseline_hours = baseline_hours or 8.0
        duration_ratio = min(1.0, self.state.sleep_minutes_today / max(baseline_hours * 60.0, 1.0))
        interruption_penalty = min(35.0, self.state.sleep_interruptions_today * 6.0)
        daytime_sleep_penalty = 0.0
        if 9 <= now.hour <= 21 and self.state.sleep_minutes_by_hour:
            daytime_minutes = sum(
                float(minutes)
                for hour, minutes in self.state.sleep_minutes_by_hour.items()
                if 9 <= int(hour) <= 21
            )
            if self.state.sleep_minutes_today > 0:
                daytime_sleep_penalty = min(20.0, (daytime_minutes / self.state.sleep_minutes_today) * 20.0)
        score = 100.0 * duration_ratio - interruption_penalty - daytime_sleep_penalty
        return max(0.0, min(100.0, score))

    def _latest_behavior_observation_at(self) -> str | None:
        """Return the timestamp of the latest behavior observation/report."""
        timestamps = [
            item.get("timestamp")
            for item in (self.state.behavior_observations[-1:] + self.state.behavior_reports[-1:])
            if item.get("timestamp")
        ]
        if not timestamps:
            return None
        return max(timestamps)


def generate_pet_id(name: str) -> str:
    """Generate a stable, human-readable pet id from the pet name."""
    normalized = "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")
    normalized = "_".join(part for part in normalized.split("_") if part)
    digest = hashlib.sha1(name.encode("utf-8"), usedforsecurity=False).hexdigest()[:6]
    return f"{normalized or 'pet'}_{digest}"


def calculate_daily_calories(weight_kg: float, diet_mode: str) -> float:
    """Estimate daily calories using a lightweight veterinary heuristic."""
    rer = 70.0 * pow(max(weight_kg, 0.5), 0.75)
    multiplier = {
        "puppy": 2.0,
        "adult": 1.6,
        "senior": 1.2,
        "diet": 1.0,
        "medical": 1.1,
    }.get(diet_mode, 1.6)
    return round(rer * multiplier, 1)


def calculate_recommended_portion(
    weight_kg: float,
    diet_mode: str,
    daily_calories: float | None = None,
    *,
    kcal_per_gram: float = DEFAULT_KCAL_PER_GRAM,
) -> float:
    """Convert calories into a suggested food portion in grams per feeding."""
    calories = daily_calories if daily_calories is not None else calculate_daily_calories(weight_kg, diet_mode)
    meals_per_day = len(DEFAULT_FEEDING_SCHEDULES.get(diet_mode, DEFAULT_FEEDING_SCHEDULES[DIET_MODE_ADULT]))
    return round((calories / max(meals_per_day, 1)) / max(kcal_per_gram, 0.1), 1)


def daily_water_target_ml(weight_kg: float) -> float:
    """Return the daily water target for a pet."""
    return round(max(100.0, weight_kg * DEFAULT_DAILY_WATER_PER_KG_ML), 1)


def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    """Decode an image into an RGB numpy array."""
    with Image.open(io.BytesIO(image_bytes)) as image:
        return np.array(image.convert("RGB"))


def analyze_frame(
    frame: np.ndarray,
    previous_frame: np.ndarray | None,
    food_area: BowlArea | None,
    water_area: BowlArea | None,
    food_reference: np.ndarray | None = None,
    water_reference: np.ndarray | None = None,
) -> CameraAnalysis:
    """Analyze a camera frame for bowl state and interaction signals."""
    gray_frame = _to_gray(frame)
    prev_gray = _to_gray(previous_frame) if previous_frame is not None else None
    frame_motion = _mean_abs_diff(gray_frame, prev_gray)

    food_crop = food_area.crop(frame) if food_area else None
    food_prev = food_area.crop(previous_frame) if food_area else None
    food_ref = food_area.crop(food_reference) if food_area else None
    water_crop = water_area.crop(frame) if water_area else None
    water_prev = water_area.crop(previous_frame) if water_area else None
    water_ref = water_area.crop(water_reference) if water_area else None

    food_motion = _mean_abs_diff(_to_gray(food_crop), _to_gray(food_prev))
    water_motion = _mean_abs_diff(_to_gray(water_crop), _to_gray(water_prev))
    food_contours = _contour_motion_ratio(food_crop, food_prev)
    water_contours = _contour_motion_ratio(water_crop, water_prev)
    food_texture = _edge_density(_to_gray(food_crop))
    water_texture = _edge_density(_to_gray(water_crop))
    food_similarity = _reference_similarity(food_crop, food_ref)
    water_similarity = _reference_similarity(water_crop, water_ref)
    water_std = float(np.std(_to_gray(water_crop))) if water_crop is not None else 0.0

    food_empty = None
    if food_crop is not None:
        if food_similarity is not None:
            food_empty = food_similarity < CAMERA_EMPTY_SIMILARITY_THRESHOLD
        else:
            food_empty = food_texture < CAMERA_TEXTURE_THRESHOLD

    water_empty = None
    if water_crop is not None:
        if water_similarity is not None:
            water_empty = water_similarity < CAMERA_EMPTY_SIMILARITY_THRESHOLD
        else:
            water_empty = water_texture < CAMERA_TEXTURE_THRESHOLD and water_std < 0.07

    return CameraAnalysis(
        frame_motion_score=round(frame_motion, 4),
        food_motion_score=round(food_motion + food_contours, 4),
        water_motion_score=round(water_motion + water_contours, 4),
        food_empty=food_empty,
        water_empty=water_empty,
        food_interaction=(food_motion >= CAMERA_MOTION_THRESHOLD or food_contours >= 0.02),
        water_interaction=(water_motion >= CAMERA_MOTION_THRESHOLD or water_contours >= 0.02),
        debug={
            "frame_motion": round(frame_motion, 4),
            "food_texture": round(food_texture, 4),
            "water_texture": round(water_texture, 4),
            "food_similarity": round(food_similarity, 4) if food_similarity is not None else -1.0,
            "water_similarity": round(water_similarity, 4) if water_similarity is not None else -1.0,
            "food_contours": round(food_contours, 4),
            "water_contours": round(water_contours, 4),
        },
    )


def parse_feeding_schedule(text: Any, *, pet_id: str) -> tuple[RoutineEntry, ...]:
    """Parse feeding routines from structured objects or legacy multiline text."""
    routines: list[RoutineEntry] = []
    if isinstance(text, Sequence) and not isinstance(text, (str, bytes)):
        for index, item in enumerate(text):
            if not item:
                continue
            routines.append(
                _parse_routine_object(
                    item,
                    pet_id=pet_id,
                    index=index,
                    default_category=ROUTINE_TYPE_FEED,
                )
            )
        return tuple(routines)
    for index, line in enumerate(_iter_lines(text)):
        parts = [part.strip() for part in line.split("|")]
        if not parts:
            continue
        clock = _parse_clock(parts[0])
        meal_type = (parts[1] if len(parts) > 1 and parts[1] else MEAL_TYPE_DRY).lower()
        if meal_type not in MEAL_TYPES:
            raise ValueError(f"Unsupported meal type: {meal_type}")
        label = parts[2] if len(parts) > 2 and parts[2] else f"{meal_type.title()} feeding"
        portion = _parse_optional_float(parts[3] if len(parts) > 3 else None)
        weekdays = _parse_weekdays(parts[4] if len(parts) > 4 else None)
        duration = _parse_optional_int(parts[5] if len(parts) > 5 else None) or DEFAULT_FEEDING_DURATION_MINUTES
        routines.append(
            RoutineEntry(
                routine_id=f"{pet_id}:feed:{index}",
                category=ROUTINE_TYPE_FEED,
                time_of_day=clock,
                label=label,
                duration_minutes=duration,
                weekdays=weekdays,
                meal_type=meal_type,
                portion_grams=portion,
            )
        )
    return tuple(routines)


def parse_walk_schedule(text: Any, *, pet_id: str) -> tuple[RoutineEntry, ...]:
    """Parse walk routines from structured objects or legacy multiline text."""
    routines: list[RoutineEntry] = []
    if isinstance(text, Sequence) and not isinstance(text, (str, bytes)):
        for index, item in enumerate(text):
            if not item:
                continue
            routines.append(
                _parse_routine_object(
                    item,
                    pet_id=pet_id,
                    index=index,
                    default_category=ROUTINE_TYPE_WALK,
                )
            )
        return tuple(routines)
    for index, line in enumerate(_iter_lines(text)):
        parts = [part.strip() for part in line.split("|")]
        clock = _parse_clock(parts[0])
        duration = _parse_optional_int(parts[1] if len(parts) > 1 else None) or DEFAULT_WALK_DURATION_MINUTES
        label = parts[2] if len(parts) > 2 and parts[2] else "Walk"
        weekdays = _parse_weekdays(parts[3] if len(parts) > 3 else None)
        location = parts[4] if len(parts) > 4 and parts[4] else None
        routines.append(
            RoutineEntry(
                routine_id=f"{pet_id}:walk:{index}",
                category=ROUTINE_TYPE_WALK,
                time_of_day=clock,
                label=label,
                duration_minutes=duration,
                weekdays=weekdays,
                location=location,
            )
        )
    return tuple(routines)


def parse_care_schedule(text: Any, *, pet_id: str) -> tuple[RoutineEntry, ...]:
    """Parse care routines from structured objects or legacy multiline text."""
    routines: list[RoutineEntry] = []
    if isinstance(text, Sequence) and not isinstance(text, (str, bytes)):
        for index, item in enumerate(text):
            if not item:
                continue
            routines.append(
                _parse_routine_object(
                    item,
                    pet_id=pet_id,
                    index=index,
                    default_category=ROUTINE_TYPE_CARE,
                )
            )
        return tuple(routines)
    for index, line in enumerate(_iter_lines(text)):
        parts = [part.strip() for part in line.split("|")]
        clock = _parse_clock(parts[0])
        category = (parts[1] if len(parts) > 1 and parts[1] else ROUTINE_TYPE_CARE).lower()
        label = parts[2] if len(parts) > 2 and parts[2] else category.title()
        duration = _parse_optional_int(parts[3] if len(parts) > 3 else None) or DEFAULT_CARE_DURATION_MINUTES
        weekdays = _parse_weekdays(parts[4] if len(parts) > 4 else None)
        location = parts[5] if len(parts) > 5 and parts[5] else None
        notes = parts[6] if len(parts) > 6 and parts[6] else None
        routines.append(
            RoutineEntry(
                routine_id=f"{pet_id}:care:{index}",
                category=category,
                time_of_day=clock,
                label=label,
                duration_minutes=duration,
                weekdays=weekdays,
                location=location,
                notes=notes,
            )
        )
    return tuple(routines)


def parse_vet_appointments(text: Any, *, pet_id: str) -> tuple[AppointmentEntry, ...]:
    """Parse dated vet and care appointments."""
    appointments: list[AppointmentEntry] = []
    for index, line in enumerate(_iter_lines(text)):
        parts = [part.strip() for part in line.split("|")]
        starts_at = _parse_datetime_text(parts[0])
        label = parts[1] if len(parts) > 1 and parts[1] else "Vet visit"
        duration = _parse_optional_int(parts[2] if len(parts) > 2 else None) or DEFAULT_VET_DURATION_MINUTES
        location = parts[3] if len(parts) > 3 and parts[3] else None
        category = (parts[4] if len(parts) > 4 and parts[4] else ROUTINE_TYPE_VET).lower()
        notes = parts[5] if len(parts) > 5 and parts[5] else None
        appointments.append(
            AppointmentEntry(
                appointment_id=f"{pet_id}:appointment:{index}:{starts_at.isoformat()}",
                category=category,
                starts_at=starts_at,
                label=label,
                duration_minutes=duration,
                location=location,
                notes=notes,
            )
        )
    return tuple(sorted(appointments, key=lambda item: item.starts_at))


def parse_schedule_exceptions(value: Any, *, pet_id: str) -> tuple[ScheduleException, ...]:
    """Parse routine exceptions from structured config/runtime payload."""
    if value in (None, "", []):
        return ()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        exceptions: list[ScheduleException] = []
        for index, item in enumerate(value):
            if not item:
                continue
            if not isinstance(item, dict):
                raise ValueError("Routine exceptions must be objects")
            action = str(item.get(CONF_ROUTINE_EXCEPTION_ACTION, ROUTINE_EXCEPTION_SKIP)).strip().lower()
            if action not in ROUTINE_EXCEPTION_ACTIONS:
                raise ValueError(f"Unsupported exception action: {action}")
            category = str(item.get(CONF_ROUTINE_CATEGORY, ROUTINE_TYPE_CARE)).strip().lower()
            if category not in ROUTINE_CATEGORIES:
                raise ValueError(f"Unsupported exception category: {category}")
            exception_date = _parse_date(item[CONF_ROUTINE_EXCEPTION_DATE])
            time_value = item.get(CONF_ROUTINE_EXCEPTION_TIME)
            time_of_day = _parse_clock(str(time_value)) if time_value not in (None, "") else None
            duration = _parse_optional_int(item.get(CONF_ROUTINE_DURATION_MINUTES))
            if action in {ROUTINE_EXCEPTION_ADD, ROUTINE_EXCEPTION_MOVE} and time_of_day is None:
                raise ValueError("Add and move exceptions require a time")
            exceptions.append(
                ScheduleException(
                    exception_id=f"{pet_id}:exception:{index}",
                    exception_date=exception_date,
                    action=action,
                    category=category,
                    label=_coerce_optional_str(item.get(CONF_ROUTINE_LABEL)),
                    time_of_day=time_of_day,
                    duration_minutes=duration,
                    meal_type=_coerce_optional_str(item.get(CONF_ROUTINE_MEAL_TYPE)),
                    portion_grams=_parse_optional_float(item.get(CONF_ROUTINE_PORTION_GRAMS)),
                    location=_coerce_optional_str(item.get(CONF_ROUTINE_LOCATION)),
                    notes=_coerce_optional_str(item.get(CONF_NOTES)),
                )
            )
        return tuple(sorted(exceptions, key=lambda item: (item.exception_date, item.category, item.action)))
    raise ValueError("Routine exceptions must be a list of objects")


def parse_safe_zones(value: Any) -> tuple[SafeZone, ...]:
    """Parse configured safe zones from structured payload."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Safe zones must be a list of objects")
    zones: list[SafeZone] = []
    for index, item in enumerate(value):
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Safe zones must be objects")
        zone_name = str(item.get(CONF_ZONE_NAME, "")).strip()
        if not zone_name:
            raise ValueError("Safe zone name is required")
        latitude = float(item.get(CONF_ZONE_LATITUDE))
        longitude = float(item.get(CONF_ZONE_LONGITUDE))
        radius_m = max(5.0, float(item.get(CONF_ZONE_RADIUS_M, 100.0)))
        zones.append(
            SafeZone(
                zone_id=f"safe_zone_{index}_{zone_name.lower().replace(' ', '_')}",
                name=zone_name,
                latitude=latitude,
                longitude=longitude,
                radius_m=radius_m,
            )
        )
    return tuple(zones)


def parse_room_presence_sources(value: Any) -> tuple[RoomPresenceSource, ...]:
    """Parse room presence sources from structured payload."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Room presence sources must be a list of objects")
    sources: list[RoomPresenceSource] = []
    for item in value:
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Room presence sources must be objects")
        room_name = str(item.get(CONF_ROOM_NAME, "")).strip()
        entity_id = str(item.get("entity_id", "")).strip()
        if not room_name or not entity_id:
            raise ValueError("Room presence source requires room_name and entity_id")
        sources.append(
            RoomPresenceSource(
                room_name=room_name,
                entity_id=entity_id,
                match_state=_coerce_optional_str(item.get(CONF_ROOM_MATCH_STATE)),
                priority=max(1, int(item.get(CONF_ROOM_SOURCE_PRIORITY, 1))),
            )
        )
    return tuple(sources)


def parse_calendar_links(
    value: Any,
    *,
    fallback_entity_ids: Any = None,
) -> tuple[CalendarLink, ...]:
    """Parse linked external calendar configuration."""
    if value in (None, "", []):
        fallback = _normalize_entity_list(fallback_entity_ids)
        return tuple(
            CalendarLink(calendar_entity_id=entity_id)
            for entity_id in fallback
        )
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Calendar links must be a list of objects")
    links: list[CalendarLink] = []
    for item in value:
        if not item:
            continue
        if isinstance(item, str):
            links.append(CalendarLink(calendar_entity_id=item.strip()))
            continue
        if not isinstance(item, dict):
            raise ValueError("Calendar links must be objects")
        calendar_entity_id = str(item.get(CONF_CALENDAR_ENTITY_ID, "")).strip()
        if not calendar_entity_id:
            raise ValueError("Calendar link requires calendar_entity_id")
        source_of_truth = str(
            item.get(CONF_SOURCE_OF_TRUTH, CALENDAR_SOURCE_OF_TRUTH_DIVA)
        ).strip().lower()
        if source_of_truth not in CALENDAR_SOURCE_OF_TRUTH_OPTIONS:
            raise ValueError(f"Unsupported calendar source_of_truth: {source_of_truth}")
        links.append(
            CalendarLink(
                calendar_entity_id=calendar_entity_id,
                source_of_truth=source_of_truth,
            )
        )
    unique: dict[str, CalendarLink] = {link.calendar_entity_id: link for link in links if link.calendar_entity_id}
    return tuple(unique.values())


def parse_care_roles(value: Any) -> tuple[CareRole, ...]:
    """Parse configured caregiver roles."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Care roles must be a list of objects")
    roles: list[CareRole] = []
    for item in value:
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Care roles must be objects")
        caregiver = str(item.get(CONF_CAREGIVER, "")).strip()
        role = str(item.get(CONF_ROLE, "")).strip()
        if not caregiver or not role:
            raise ValueError("Care role requires caregiver and role")
        roles.append(CareRole(caregiver=caregiver, role=role, notes=_coerce_optional_str(item.get(CONF_NOTES))))
    return tuple(roles)


def parse_care_shifts(value: Any, *, pet_id: str) -> tuple[CareShift, ...]:
    """Parse caregiver shift definitions."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Care shifts must be a list of objects")
    shifts: list[CareShift] = []
    for index, item in enumerate(value):
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Care shifts must be objects")
        label = str(item.get(CONF_ROUTINE_LABEL, "")).strip()
        caregiver = str(item.get(CONF_CAREGIVER, "")).strip()
        if not label or not caregiver:
            raise ValueError("Care shift requires label and caregiver")
        start_time = _parse_clock(str(item.get(CONF_SHIFT_START_TIME)))
        end_time = _parse_clock(str(item.get(CONF_SHIFT_END_TIME)))
        weekdays = _parse_weekdays(item.get(CONF_ROUTINE_DAYS))
        shifts.append(
            CareShift(
                shift_id=f"{pet_id}:shift:{index}",
                label=label,
                caregiver=caregiver,
                role=_coerce_optional_str(item.get(CONF_ROLE)),
                start_time=start_time,
                end_time=end_time,
                weekdays=weekdays,
                notes=_coerce_optional_str(item.get(CONF_NOTES)),
            )
        )
    return tuple(shifts)


def parse_checklist_items(value: Any, *, pet_id: str) -> tuple[ChecklistItem, ...]:
    """Parse operational checklist templates."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Checklist items must be a list of objects")
    items: list[ChecklistItem] = []
    for index, item in enumerate(value):
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Checklist items must be objects")
        label = str(item.get(CONF_ROUTINE_LABEL, "")).strip()
        if not label:
            raise ValueError("Checklist item requires a label")
        frequency = str(item.get(CONF_CHECKLIST_FREQUENCY, CHECKLIST_FREQUENCY_DAILY)).strip().lower()
        if frequency not in CHECKLIST_FREQUENCIES:
            raise ValueError(f"Unsupported checklist frequency: {frequency}")
        category = str(item.get(CONF_ROUTINE_CATEGORY, ROUTINE_TYPE_CARE)).strip().lower()
        items.append(
            ChecklistItem(
                checklist_id=f"{pet_id}:checklist:{index}",
                label=label,
                frequency=frequency,
                category=category,
                caregiver=_coerce_optional_str(item.get(CONF_CAREGIVER)),
                requires_approval=bool(item.get(CONF_REQUIRES_APPROVAL, False)),
                notes=_coerce_optional_str(item.get(CONF_NOTES)),
            )
        )
    return tuple(items)


def parse_approval_required_actions(value: Any) -> tuple[str, ...]:
    """Parse approval-required action names."""
    if value in (None, "", []):
        return ()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        actions = [str(item).strip() for item in value if str(item).strip()]
    else:
        actions = [str(value).strip()]
    invalid = [item for item in actions if item not in APPROVAL_ACTION_OPTIONS]
    if invalid:
        raise ValueError(f"Unsupported approval action: {invalid[0]}")
    return tuple(dict.fromkeys(actions))


def parse_food_catalog(value: Any) -> tuple[FoodCatalogEntry, ...]:
    """Parse food catalog entries from structured config payload."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Food catalog must be a list of objects")
    foods: list[FoodCatalogEntry] = []
    for item in value:
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Food catalog entries must be objects")
        kind = str(item.get(CONF_FOOD_KIND, FOOD_KIND_MAIN)).strip().lower()
        if kind not in FOOD_KINDS:
            raise ValueError(f"Unsupported food kind: {kind}")
        meal_type = str(item.get(CONF_ROUTINE_MEAL_TYPE, MEAL_TYPE_DRY)).strip().lower()
        if meal_type not in MEAL_TYPES:
            raise ValueError(f"Unsupported meal type: {meal_type}")
        foods.append(
            FoodCatalogEntry(
                name=str(item[CONF_FOOD_NAME]).strip(),
                brand=_coerce_optional_str(item.get(CONF_FOOD_BRAND)),
                kind=kind,
                meal_type=meal_type,
                kcal_per_gram=max(0.1, float(item.get(CONF_KCAL_PER_GRAM, DEFAULT_KCAL_PER_GRAM))),
                notes=_coerce_optional_str(item.get(CONF_NOTES)),
            )
        )
    return tuple(foods)


def parse_food_transition_plan(value: Any) -> tuple[FoodTransitionStep, ...]:
    """Parse a dated food transition plan."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Food transition plan must be a list of objects")
    plan: list[FoodTransitionStep] = []
    for item in value:
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Food transition entries must be objects")
        from_percent = int(item.get(CONF_FROM_PERCENT, 0))
        to_percent = int(item.get(CONF_TO_PERCENT, 0))
        if from_percent < 0 or to_percent < 0 or from_percent + to_percent != 100:
            raise ValueError("Transition percentages must be non-negative and sum to 100")
        plan.append(
            FoodTransitionStep(
                transition_date=_parse_date(item[CONF_TRANSITION_DATE]),
                from_food_name=str(item[CONF_FROM_FOOD_NAME]).strip(),
                to_food_name=str(item[CONF_TO_FOOD_NAME]).strip(),
                from_percent=from_percent,
                to_percent=to_percent,
                notes=_coerce_optional_str(item.get(CONF_NOTES)),
            )
        )
    return tuple(sorted(plan, key=lambda step: step.transition_date))


def parse_medication_courses(value: Any) -> tuple[MedicationCourse, ...]:
    """Parse medication courses from structured config payload."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Medication courses must be a list of objects")
    courses: list[MedicationCourse] = []
    for index, item in enumerate(value):
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Medication course entries must be objects")
        times = _parse_time_list(item.get(CONF_MEDICATION_TIMES))
        if not times:
            raise ValueError("Medication times are required")
        courses.append(
            MedicationCourse(
                medication_id=f"medication:{index}:{str(item[CONF_MEDICATION_NAME]).strip().lower().replace(' ', '_')}",
                name=str(item[CONF_MEDICATION_NAME]).strip(),
                dose=str(item.get(CONF_DOSE, "")).strip() or "recorded",
                times=times,
                start_date=_parse_date(item.get(CONF_START_DATE) or date.today().isoformat()),
                end_date=_parse_date_optional(item.get(CONF_END_DATE)),
                route=_coerce_optional_str(item.get(CONF_MEDICATION_ROUTE)),
                notes=_coerce_optional_str(item.get(CONF_NOTES)),
            )
        )
    return tuple(courses)


def parse_chronic_conditions(value: Any) -> tuple[ChronicCondition, ...]:
    """Parse chronic conditions from structured config payload."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Chronic conditions must be a list of objects")
    conditions: list[ChronicCondition] = []
    for item in value:
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Chronic condition entries must be objects")
        conditions.append(
            ChronicCondition(
                name=str(item[CONF_CONDITION_NAME]).strip(),
                status=_coerce_optional_str(item.get(CONF_CONDITION_STATUS)) or "monitoring",
                monitor_interval_days=max(1, int(item.get(CONF_MONITOR_INTERVAL_DAYS, 30))),
                notes=_coerce_optional_str(item.get(CONF_NOTES)),
            )
        )
    return tuple(conditions)


def parse_diagnoses(value: Any) -> tuple[DiagnosisEntry, ...]:
    """Parse diagnoses from structured config payload."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Diagnoses must be a list of objects")
    diagnoses: list[DiagnosisEntry] = []
    for item in value:
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Diagnosis entries must be objects")
        diagnoses.append(
            DiagnosisEntry(
                name=str(item[CONF_DIAGNOSIS_NAME]).strip(),
                status=_coerce_optional_str(item.get(CONF_DIAGNOSIS_STATUS)) or "active",
                diagnosed_on=_parse_date_optional(item.get(CONF_DIAGNOSED_ON)),
                notes=_coerce_optional_str(item.get(CONF_NOTES)),
            )
        )
    return tuple(diagnoses)


def parse_allergies(value: Any) -> tuple[AllergyEntry, ...]:
    """Parse allergies from structured config payload."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Allergies must be a list of objects")
    allergies: list[AllergyEntry] = []
    for item in value:
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Allergy entries must be objects")
        allergies.append(
            AllergyEntry(
                allergen=str(item[CONF_ALLERGEN]).strip(),
                reaction=_coerce_optional_str(item.get(CONF_REACTION)),
                notes=_coerce_optional_str(item.get(CONF_NOTES)),
            )
        )
    return tuple(allergies)


def parse_contraindications(value: Any) -> tuple[ContraindicationEntry, ...]:
    """Parse contraindications from structured config payload."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Contraindications must be a list of objects")
    contraindications: list[ContraindicationEntry] = []
    for item in value:
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Contraindication entries must be objects")
        contraindications.append(
            ContraindicationEntry(
                item=str(item[CONF_CONTRAINDICATION]).strip(),
                reason=_coerce_optional_str(item.get(CONF_REASON)),
                notes=_coerce_optional_str(item.get(CONF_NOTES)),
            )
        )
    return tuple(contraindications)


def parse_medical_history(value: Any) -> tuple[MedicalHistoryEntry, ...]:
    """Parse dated medical history entries from structured config payload."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Medical history must be a list of objects")
    history: list[MedicalHistoryEntry] = []
    for item in value:
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Medical history entries must be objects")
        history.append(
            MedicalHistoryEntry(
                history_date=_parse_date(item[CONF_HISTORY_DATE]),
                title=str(item[CONF_HISTORY_TITLE]).strip(),
                category=_coerce_optional_str(item.get(CONF_HISTORY_CATEGORY)) or "general",
                notes=_coerce_optional_str(item.get(CONF_NOTES)),
            )
        )
    return tuple(sorted(history, key=lambda entry: (entry.history_date, entry.title)))


def _parse_vaccine_profile(value: Any) -> str:
    """Normalize a configured vaccine profile."""
    normalized = str(value or VACCINE_PROFILE_AUTO).strip().lower()
    if normalized not in VACCINE_PROFILE_OPTIONS:
        return VACCINE_PROFILE_AUTO
    return normalized


def parse_vaccine_overrides(value: Any) -> tuple[VaccinePlanEntry, ...]:
    """Parse editable vaccine overrides from config payload."""
    if value in (None, "", []):
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Vaccine overrides must be a list of objects")
    entries: list[VaccinePlanEntry] = []
    for index, item in enumerate(value):
        if not item:
            continue
        if not isinstance(item, dict):
            raise ValueError("Vaccine override entries must be objects")
        due_date = _parse_date(item.get(CONF_DUE_DATE) or item.get(CONF_START_DATE))
        entries.append(
            VaccinePlanEntry(
                dose_id=_coerce_optional_str(item.get(CONF_VACCINE_DOSE_ID)) or f"override:{index}",
                vaccine_name=str(item[CONF_VACCINE_NAME]).strip(),
                due_date=due_date,
                category=_coerce_optional_str(item.get(CONF_ROUTINE_CATEGORY)) or "custom",
                source=_coerce_optional_str(item.get("source")) or "manual_override",
                recurrence_months=_parse_optional_int(item.get(CONF_RECURRENCE_MONTHS)),
                notes=_coerce_optional_str(item.get(CONF_NOTES)),
            )
        )
    return tuple(sorted(entries, key=lambda item: (item.due_date, item.vaccine_name)))


def normalize_behavior_type(value: str) -> str:
    """Normalize a behavior type to canonical anomaly keys."""
    lowered = value.strip().lower().replace(" ", "_")
    mapping = {
        "vomit": ANOMALY_VOMITING,
        "vomiting": ANOMALY_VOMITING,
        "cough": ANOMALY_COUGH,
        "coughing": ANOMALY_COUGH,
        "limp": ANOMALY_LIMPING,
        "limping": ANOMALY_LIMPING,
        "gait": ANOMALY_GAIT,
        "gait_change": ANOMALY_GAIT,
        "gait_change_detected": ANOMALY_GAIT,
        "restless": ANOMALY_RESTLESSNESS,
        "restlessness": ANOMALY_RESTLESSNESS,
        "pacing": ANOMALY_RESTLESSNESS,
    }
    return mapping.get(lowered, lowered)


def _parse_routine_object(
    item: Any,
    *,
    pet_id: str,
    index: int,
    default_category: str,
) -> RoutineEntry:
    if not isinstance(item, dict):
        raise ValueError("Routine entries must be objects")
    category = str(item.get(CONF_ROUTINE_CATEGORY, default_category)).strip().lower()
    if default_category == ROUTINE_TYPE_FEED:
        category = ROUTINE_TYPE_FEED
    elif default_category == ROUTINE_TYPE_WALK:
        category = ROUTINE_TYPE_WALK
    elif category not in ROUTINE_CATEGORIES:
        raise ValueError(f"Unsupported routine category: {category}")
    clock = _parse_clock(str(item[CONF_ROUTINE_TIME]))
    weekdays = _parse_weekdays(item.get(CONF_ROUTINE_DAYS))
    duration = _parse_optional_int(item.get(CONF_ROUTINE_DURATION_MINUTES)) or _default_duration_for_category(category)
    label = _coerce_optional_str(item.get(CONF_ROUTINE_LABEL)) or _default_label_for_category(category)
    meal_type = None
    portion_grams = None
    if category == ROUTINE_TYPE_FEED:
        meal_type = str(item.get(CONF_ROUTINE_MEAL_TYPE, MEAL_TYPE_DRY)).strip().lower()
        if meal_type not in MEAL_TYPES:
            raise ValueError(f"Unsupported meal type: {meal_type}")
        portion_grams = _parse_optional_float(item.get(CONF_ROUTINE_PORTION_GRAMS))
    return RoutineEntry(
        routine_id=f"{pet_id}:{default_category}:{index}",
        category=category,
        time_of_day=clock,
        label=label,
        duration_minutes=duration,
        weekdays=weekdays,
        meal_type=meal_type,
        portion_grams=portion_grams,
        location=_coerce_optional_str(item.get(CONF_ROUTINE_LOCATION)),
        notes=_coerce_optional_str(item.get(CONF_NOTES)),
    )


def _default_duration_for_category(category: str) -> int:
    return {
        ROUTINE_TYPE_FEED: DEFAULT_FEEDING_DURATION_MINUTES,
        ROUTINE_TYPE_WALK: DEFAULT_WALK_DURATION_MINUTES,
        ROUTINE_TYPE_CARE: DEFAULT_CARE_DURATION_MINUTES,
        ROUTINE_TYPE_PLAY: DEFAULT_CARE_DURATION_MINUTES,
        ROUTINE_TYPE_GROOMING: DEFAULT_CARE_DURATION_MINUTES,
        ROUTINE_TYPE_TRAINING: DEFAULT_CARE_DURATION_MINUTES,
        ROUTINE_TYPE_MEDICATION: 10,
        ROUTINE_TYPE_VET: DEFAULT_VET_DURATION_MINUTES,
    }.get(category, DEFAULT_CARE_DURATION_MINUTES)


def _default_label_for_category(category: str) -> str:
    return {
        ROUTINE_TYPE_FEED: "Feeding",
        ROUTINE_TYPE_WALK: "Walk",
        ROUTINE_TYPE_CARE: "Care",
        ROUTINE_TYPE_PLAY: "Play",
        ROUTINE_TYPE_GROOMING: "Grooming",
        ROUTINE_TYPE_TRAINING: "Training",
        ROUTINE_TYPE_MEDICATION: "Medication",
        ROUTINE_TYPE_VET: "Vet visit",
    }.get(category, category.replace("_", " ").title())


def _weekday_name(value: int) -> str:
    mapping = {
        0: "mon",
        1: "tue",
        2: "wed",
        3: "thu",
        4: "fri",
        5: "sat",
        6: "sun",
    }
    return mapping.get(value, "mon")


def _parse_manual_mode(value: Any) -> str:
    mode = _coerce_optional_str(value) or OPERATION_MODE_NORMAL
    if mode not in {OPERATION_MODE_NORMAL, OPERATION_MODE_VACATION, OPERATION_MODE_ILLNESS}:
        raise ValueError(f"Unsupported operation mode: {mode}")
    return mode


def _exception_skips_event(exception: ScheduleException, event: ScheduledEvent) -> bool:
    if event.start.date() != exception.exception_date:
        return False
    if exception.action == ROUTINE_EXCEPTION_ADD:
        return False
    if exception.category == ROUTINE_TYPE_CARE:
        return _is_care_category(event.category)
    return event.category == exception.category


def _event_matches_category(event: ScheduledEvent, category: str) -> bool:
    if category == "care_group":
        return _is_care_category(event.category)
    return event.category == category


def _is_care_category(category: str) -> bool:
    return category in {
        ROUTINE_TYPE_CARE,
        ROUTINE_TYPE_PLAY,
        ROUTINE_TYPE_GROOMING,
        ROUTINE_TYPE_TRAINING,
        ROUTINE_TYPE_MEDICATION,
    }


def _apply_modes_to_event(
    event: ScheduledEvent,
    active_modes: tuple[str, ...],
    context: PetContext,
) -> ScheduledEvent:
    if not active_modes:
        return event
    summary = event.summary
    start = event.start
    end = event.end
    description = event.description
    metadata = dict(event.metadata)
    metadata["active_modes"] = list(active_modes)

    if "heat" in active_modes and event.category == ROUTINE_TYPE_WALK and 11 <= start.hour < 19:
        summary = f"{summary} [heat-risk]"
        description = "\n".join(filter(None, [description, "Heat mode: keep the walk to cooler hours."]))

    if "winter" in active_modes and event.category == ROUTINE_TYPE_WALK:
        duration_minutes = max(10, int((end - start).total_seconds() / 60 * 0.75))
        end = start + timedelta(minutes=duration_minutes)
        summary = f"{summary} [winter]"
        description = "\n".join(filter(None, [description, "Winter mode: shorten the walk and protect paws."]))

    if OPERATION_MODE_ILLNESS in active_modes:
        if event.category == ROUTINE_TYPE_WALK:
            duration_minutes = max(10, int((end - start).total_seconds() / 60 * 0.5))
            end = start + timedelta(minutes=duration_minutes)
        if _is_care_category(event.category) and event.category in {ROUTINE_TYPE_PLAY, ROUTINE_TYPE_TRAINING}:
            summary = f"{summary} [light]"
        description = "\n".join(filter(None, [description, "Illness mode is active."]))

    if OPERATION_MODE_VACATION in active_modes:
        description = "\n".join(filter(None, [description, "Vacation mode is active."]))

    if "home_alone" in active_modes:
        description = "\n".join(filter(None, [description, "Home-alone mode is active."]))

    return ScheduledEvent(
        event_id=event.event_id,
        pet_id=event.pet_id,
        category=event.category,
        summary=summary,
        start=start,
        end=end,
        description=description,
        location=event.location,
        metadata=metadata,
    )


def _is_past_exception(payload: dict[str, Any]) -> bool:
    try:
        exception_date = _parse_date(payload.get(CONF_ROUTINE_EXCEPTION_DATE))
    except Exception:
        return True
    return exception_date < date.today() - timedelta(days=1)


def _increment_counter(target: dict[str, float], key: str, value: float) -> None:
    target[key] = round(float(target.get(key, 0.0)) + float(value), 1)


def _calculate_health_score(food_ratio: float, water_ratio: float, activity_ratio: float, anomaly_count: int) -> float:
    """Calculate an overall pet health score."""
    normalized_food = min(food_ratio, 1.0)
    normalized_water = min(water_ratio, 1.0)
    normalized_activity = min(activity_ratio, 1.0)
    penalty = anomaly_count * 7.5
    return (normalized_food * 35.0) + (normalized_water * 30.0) + (normalized_activity * 35.0) - penalty


def _calculate_feeding_quality_score(runtime: PetRuntimeState) -> float:
    """Estimate feeding quality from served/eaten/ignored/treat balance."""
    if runtime.food_served_today_grams <= 0:
        return 100.0
    served = max(runtime.food_served_today_grams, 1.0)
    eaten_ratio = min(1.0, runtime.food_today_grams / served)
    ignored_ratio = min(1.0, runtime.food_ignored_today_grams / served)
    treat_ratio = 0.0
    eaten_total = max(runtime.food_today_grams, 1.0)
    treat_grams = runtime.food_eaten_today_by_type.get(MEAL_TYPE_TREAT, 0.0)
    if treat_grams > 0:
        treat_ratio = min(1.0, treat_grams / eaten_total)
    score = 100.0
    score -= (1.0 - eaten_ratio) * 30.0
    score -= ignored_ratio * 45.0
    score -= max(0.0, treat_ratio - 0.2) * 40.0
    return max(0.0, min(100.0, score))


def _reference_similarity(current: np.ndarray | None, reference: np.ndarray | None) -> float | None:
    if current is None or reference is None:
        return None
    current_gray = _to_gray(current)
    reference_gray = _to_gray(reference)
    min_y = min(current_gray.shape[0], reference_gray.shape[0])
    min_x = min(current_gray.shape[1], reference_gray.shape[1])
    if min_y == 0 or min_x == 0:
        return None
    current_gray = current_gray[:min_y, :min_x]
    reference_gray = reference_gray[:min_y, :min_x]
    return max(0.0, 1.0 - float(np.mean(np.abs(current_gray - reference_gray))))


def _edge_density(gray: np.ndarray | None) -> float:
    if gray is None or gray.size == 0:
        return 0.0
    grad_y = np.abs(np.diff(gray, axis=0)).mean() if gray.shape[0] > 1 else 0.0
    grad_x = np.abs(np.diff(gray, axis=1)).mean() if gray.shape[1] > 1 else 0.0
    return float(grad_x + grad_y)


def _mean_abs_diff(current: np.ndarray | None, previous: np.ndarray | None) -> float:
    if current is None or previous is None:
        return 0.0
    min_y = min(current.shape[0], previous.shape[0])
    min_x = min(current.shape[1], previous.shape[1])
    if min_y == 0 or min_x == 0:
        return 0.0
    delta = np.abs(current[:min_y, :min_x] - previous[:min_y, :min_x])
    return float(np.mean(delta))


def _contour_motion_ratio(current: np.ndarray | None, previous: np.ndarray | None) -> float:
    if cv2 is None or current is None or previous is None:
        return 0.0
    current_gray = (_to_gray(current) * 255.0).astype(np.uint8)
    previous_gray = (_to_gray(previous) * 255.0).astype(np.uint8)
    min_y = min(current_gray.shape[0], previous_gray.shape[0])
    min_x = min(current_gray.shape[1], previous_gray.shape[1])
    if min_y == 0 or min_x == 0:
        return 0.0
    delta = cv2.absdiff(current_gray[:min_y, :min_x], previous_gray[:min_y, :min_x])
    _, thresh = cv2.threshold(delta, 24, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area = float(sum(cv2.contourArea(contour) for contour in contours))
    total = float(min_y * min_x)
    return area / total if total else 0.0


def _to_gray(frame: np.ndarray | None) -> np.ndarray | None:
    if frame is None:
        return None
    if frame.ndim == 2:
        return frame.astype(np.float32) / 255.0
    return frame.mean(axis=2).astype(np.float32) / 255.0


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return parsed


def _parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _parse_date_optional(value: Any) -> date | None:
    if value in (None, ""):
        return None
    return _parse_date(value)


def _parse_datetime_text(value: str) -> datetime:
    normalized = value.strip().replace("T", " ")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as err:
        raise ValueError("Use YYYY-MM-DD HH:MM format") from err


def _parse_clock(value: str) -> time:
    try:
        return time.fromisoformat(value.strip())
    except ValueError as err:
        raise ValueError("Use HH:MM time format") from err


def _parse_optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _parse_optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return round(float(value), 1)


def _parse_time_list(value: Any) -> tuple[time, ...]:
    if value in (None, ""):
        return ()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        tokens = [str(item).strip() for item in value if str(item).strip()]
    else:
        tokens = [token.strip() for token in str(value).replace(";", ",").split(",") if token.strip()]
    parsed = tuple(_parse_clock(token) for token in tokens)
    return tuple(sorted(parsed))


def _parse_weekdays(value: Any) -> tuple[int, ...]:
    if value in (None, ""):
        return ALL_WEEKDAYS
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        tokens = [str(token).strip().lower() for token in value if str(token).strip()]
    else:
        tokens = [token.strip().lower() for token in str(value).replace(";", ",").split(",") if token.strip()]
    weekdays: list[int] = []
    for token in tokens:
        if token in WEEKDAY_ALIASES:
            weekdays.extend(WEEKDAY_ALIASES[token])
            continue
        if token.isdigit() and 0 <= int(token) <= 6:
            weekdays.append(int(token))
            continue
        raise ValueError(f"Unsupported weekday token: {token}")
    unique = tuple(sorted(set(weekdays)))
    return unique or ALL_WEEKDAYS


def _coerce_optional_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _normalize_multiline_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def _normalize_entity_list(value: Any) -> tuple[str, ...]:
    if value in (None, "", []):
        return ()
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(",") if item.strip())
    if isinstance(value, Sequence):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return ()


def _scheduled_event_hash(event: ScheduledEvent | None) -> str | None:
    """Return a stable hash for a scheduled event payload."""
    if event is None:
        return None
    payload = "|".join(
        (
            event.event_id,
            event.category,
            event.summary,
            event.start.isoformat(),
            event.end.isoformat(),
            event.description or "",
            event.location or "",
        )
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def _calendar_conflict_id(
    calendar_entity_id: str,
    sync_key: str,
    conflict_type: str,
    occurred_at: datetime,
) -> str:
    """Return a stable identifier for a calendar conflict record."""
    payload = "|".join((calendar_entity_id, sync_key, conflict_type, occurred_at.isoformat()))
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _calendar_conflict_signature(
    *,
    calendar_entity_id: str,
    sync_key: str,
    conflict_type: str,
    reason: str,
    base_event: ScheduledEvent | None,
    effective_event: ScheduledEvent | None,
    external_event: dict[str, Any] | None,
) -> str:
    """Return a signature for the current conflict shape."""
    payload = "|".join(
        (
            calendar_entity_id,
            sync_key,
            conflict_type,
            reason,
            _scheduled_event_hash(base_event) or "",
            _scheduled_event_hash(effective_event) or "",
            _event_payload_hash(external_event) or "",
        )
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def _event_payload_hash(payload: dict[str, Any] | None) -> str | None:
    """Return a stable hash for a serialized external event snapshot."""
    if payload is None:
        return None
    normalized = "|".join(
        (
            str(payload.get("uid") or ""),
            str(payload.get("recurrence_id") or ""),
            str(payload.get("summary") or ""),
            str(payload.get("start") or ""),
            str(payload.get("end") or ""),
            str(payload.get("description") or ""),
            str(payload.get("location") or ""),
        )
    )
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()


def _scheduled_event_from_override(
    override: dict[str, Any],
    *,
    default_pet_id: str,
    fallback: ScheduledEvent | None,
) -> ScheduledEvent | None:
    """Deserialize a stored calendar override into a scheduled event."""
    event_payload = override.get("event")
    if not isinstance(event_payload, dict):
        return fallback
    try:
        start = _parse_datetime(str(event_payload.get("start")))
        end = _parse_datetime(str(event_payload.get("end")))
        if start is None or end is None:
            return fallback
        return ScheduledEvent(
            event_id=str(event_payload.get("event_id") or override.get("sync_key") or (fallback.event_id if fallback else "")),
            pet_id=str(event_payload.get("pet_id") or default_pet_id),
            category=str(event_payload.get("category") or (fallback.category if fallback else ROUTINE_TYPE_CARE)),
            summary=str(event_payload.get("summary") or (fallback.summary if fallback else "Imported calendar event")),
            start=start,
            end=end,
            description=str(event_payload.get("description") or (fallback.description if fallback else "")),
            location=event_payload.get("location") or (fallback.location if fallback else None),
            metadata=dict(event_payload.get("metadata") or (fallback.metadata if fallback else {})),
        )
    except (TypeError, ValueError):
        return fallback


def _normalize_name_list(value: Any) -> tuple[str, ...]:
    text = _normalize_multiline_text(value)
    if not text:
        return ()
    if "," in text and "\n" not in text:
        parts = text.split(",")
    else:
        parts = text.splitlines()
    return tuple(part.strip() for part in parts if part.strip())


def _iter_lines(value: Any) -> Iterable[str]:
    text = _normalize_multiline_text(value)
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        yield stripped


def _add_months(value: date, months: int) -> date:
    year = value.year + (value.month - 1 + months) // 12
    month = (value.month - 1 + months) % 12 + 1
    day = min(value.day, _days_in_month(year, month))
    return date(year, month, day)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return (next_month - timedelta(days=1)).day


def _medication_taken_around(
    medication_log: list[dict[str, Any]],
    medication_name: str,
    scheduled_at: datetime,
    *,
    window_minutes: int,
) -> bool:
    window = timedelta(minutes=max(1, window_minutes))
    for item in medication_log[-80:]:
        if str(item.get("medication_name", "")).strip().lower() != medication_name.strip().lower():
            continue
        taken_at = _parse_datetime(item.get("timestamp"))
        if taken_at is None:
            continue
        if abs(taken_at - scheduled_at) <= window:
            return True
    return False


def build_default_vaccine_plan(
    *,
    pet_id: str,
    species: str,
    breed: str,
    birthdate: date,
    today: date,
    country: str,
    region: str,
    regional_policy: str,
    vaccine_profile: str,
) -> tuple[VaccinePlanEntry, ...]:
    """Build a pragmatic default vaccine plan from WSAVA + Spain overlays."""
    if species.strip().lower() != "dog":
        return ()

    plan: list[VaccinePlanEntry] = []
    country_code = country.strip().upper() or DEFAULT_MEDICAL_COUNTRY
    region_code = region.strip().lower() or DEFAULT_MEDICAL_REGION
    policy_code = regional_policy.strip().lower() or region_code or DEFAULT_MEDICAL_REGION
    profile_code = _resolve_vaccine_profile(
        vaccine_profile=vaccine_profile,
        country_code=country_code,
        species=species,
    )
    age_days = max(0, (today - birthdate).days)
    under_one_year = age_days < 365
    breed_note = _breed_vaccine_note(breed)
    source = "WSAVA 2024 + Spain OCV overlay"

    def add(
        code: str,
        vaccine_name: str,
        due_date: date,
        category: str,
        *,
        recurrence_months: int | None = None,
        notes: str | None = None,
    ) -> None:
        merged_notes = notes or ""
        if breed_note:
            merged_notes = f"{merged_notes}\n{breed_note}".strip()
        plan.append(
            VaccinePlanEntry(
                dose_id=f"{pet_id}:{code}",
                vaccine_name=vaccine_name,
                due_date=due_date,
                category=category,
                source=source,
                recurrence_months=recurrence_months,
                notes=merged_notes or None,
            )
        )

    if under_one_year:
        add("dhp_8w", "DHP puppy series", birthdate + timedelta(weeks=8), "core", notes="Core puppy priming dose.")
        add("dhp_12w", "DHP puppy series", birthdate + timedelta(weeks=12), "core", notes="Core puppy booster.")
        add("dhp_16w", "DHP final puppy dose", birthdate + timedelta(weeks=16), "core", notes="Final puppy core dose.")
        add(
            "dhp_adult_booster",
            "DHP adult booster",
            birthdate + timedelta(days=365),
            "core",
            recurrence_months=36,
            notes="Adult core booster after the puppy series.",
        )
        add(
            "rabies_initial",
            "Rabies vaccination",
            birthdate + timedelta(weeks=12),
            "regional",
            recurrence_months=12 if profile_code == VACCINE_PROFILE_SPAIN_DOG_DEFAULT else 36,
            notes="Spain overlay keeps rabies on an annual review cadence."
            if profile_code == VACCINE_PROFILE_SPAIN_DOG_DEFAULT
            else "Baseline adult rabies review cadence.",
        )
        if profile_code == VACCINE_PROFILE_SPAIN_DOG_DEFAULT:
            add("lepto_8w", "Leptospirosis primary", birthdate + timedelta(weeks=8), "regional")
            add("lepto_12w", "Leptospirosis booster", birthdate + timedelta(weeks=12), "regional")
            add(
                "lepto_annual",
                "Leptospirosis annual booster",
                birthdate + timedelta(days=365),
                "regional",
                recurrence_months=12,
                notes="High-priority annual review for Spain exposure patterns.",
            )
            add(
                "leish_annual",
                "Leishmaniosis prevention review",
                max(birthdate + timedelta(days=180), today),
                "endemic",
                recurrence_months=12,
                notes="Spain endemic overlay for leishmaniosis risk review.",
            )
    else:
        add(
            "dhp_review",
            "DHP core booster review",
            today,
            "core",
            recurrence_months=36,
            notes="Adult rolling review when historical vaccine records are not imported.",
        )
        add(
            "rabies_review",
            "Rabies booster review",
            today,
            "regional",
            recurrence_months=12 if profile_code == VACCINE_PROFILE_SPAIN_DOG_DEFAULT else 36,
            notes="Adult rolling review when historical vaccine records are not imported.",
        )
        if profile_code == VACCINE_PROFILE_SPAIN_DOG_DEFAULT:
            add(
                "lepto_review",
                "Leptospirosis annual booster",
                today,
                "regional",
                recurrence_months=12,
                notes="Adult Spain default booster cadence.",
            )
            add(
                "leish_review",
                "Leishmaniosis prevention review",
                today,
                "endemic",
                recurrence_months=12,
                notes="Annual review for endemic Spanish regions.",
            )

    regional_note = _regional_vaccine_policy_note(policy_code)
    if regional_note:
        for item in plan:
            item.notes = f"{item.notes or ''}\n{regional_note}".strip()

    return tuple(plan)


def _breed_vaccine_note(breed: str) -> str | None:
    lowered = breed.strip().lower()
    if "cocker" in lowered:
        return (
            "English/Cocker Spaniel overlay: no breed-specific core timing change is defined; "
            "keep the Spain dog default and review leptospirosis/leishmaniosis exposure with the vet."
        )
    return None


def _resolve_vaccine_profile(*, vaccine_profile: str, country_code: str, species: str) -> str:
    """Resolve auto vaccine profile selection."""
    if species.strip().lower() != "dog":
        return VACCINE_PROFILE_DOG_DEFAULT
    if vaccine_profile == VACCINE_PROFILE_AUTO:
        return VACCINE_PROFILE_SPAIN_DOG_DEFAULT if country_code == "ES" else VACCINE_PROFILE_DOG_DEFAULT
    return vaccine_profile


def _regional_vaccine_policy_note(policy_code: str) -> str | None:
    """Return a pragmatic regional vaccine policy note."""
    normalized = policy_code.strip().lower()
    if not normalized or normalized in {DEFAULT_MEDICAL_REGION, "es_general"}:
        return None
    notes = {
        "andalucia": "Regional policy: Andalucia overlay keeps endemic vector prevention and annual review high priority.",
        "madrid": "Regional policy: Madrid overlay keeps urban/travel rabies and leptospirosis review visible in the plan.",
        "cataluna": "Regional policy: Cataluna overlay keeps rabies review explicit and recommends checking local veterinary requirements.",
        "galicia": "Regional policy: Galicia overlay recommends confirming current rabies legal requirements with the veterinarian while keeping clinical review reminders active.",
        "canarias": "Regional policy: Canarias overlay highlights travel and vector-borne disease review year-round.",
        "valencia": "Regional policy: Valencia overlay highlights rabies, leptospirosis, and travel review with the vet.",
        "custom": "Regional policy: custom overlay active; verify cadence and legal requirements with the veterinarian.",
    }
    return notes.get(normalized, f"Regional policy: {normalized}")


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the distance between two coordinates in meters."""
    earth_radius_m = 6_371_000.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    origin_lat = radians(lat1)
    target_lat = radians(lat2)
    arc = sin(d_lat / 2) ** 2 + cos(origin_lat) * cos(target_lat) * sin(d_lon / 2) ** 2
    return 2 * earth_radius_m * asin(sqrt(arc))


def _route_distance_km(points: Sequence[dict[str, Any]]) -> float:
    """Return the cumulative route distance in kilometers."""
    distance_m = 0.0
    previous: tuple[float, float] | None = None
    for point in points:
        latitude = _coerce_float(point.get("latitude"))
        longitude = _coerce_float(point.get("longitude"))
        if latitude is None or longitude is None:
            continue
        current = (latitude, longitude)
        if previous is not None:
            distance_m += _haversine_m(previous[0], previous[1], current[0], current[1])
        previous = current
    return round(distance_m / 1000.0, 3)


def _build_route_summary(points: Sequence[dict[str, Any]]) -> str | None:
    """Build a compact summary for a recorded walk route."""
    if len(points) < 2:
        return None
    start = points[0]
    end = points[-1]
    return (
        f"{len(points)} pts, "
        f"{start.get('latitude')},{start.get('longitude')} -> "
        f"{end.get('latitude')},{end.get('longitude')}"
    )


def _checklist_period_key(frequency: str, when: datetime) -> str:
    """Return the completion period key for a checklist item."""
    if frequency == CHECKLIST_FREQUENCY_WEEKLY:
        iso_year, iso_week, _ = when.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    return when.date().isoformat()


def _future_events_from_routines(
    routines: Sequence[RoutineEntry],
    now: datetime,
    pet_id: str,
    *,
    limit: int = 5,
) -> list[ScheduledEvent]:
    if not routines:
        return []
    events: list[ScheduledEvent] = []
    for day_offset in range(0, 8):
        day = now.date() + timedelta(days=day_offset)
        for routine in routines:
            if not routine.occurs_on(day):
                continue
            event = routine.occurrence(pet_id, day, now.tzinfo)
            if event.start > now:
                events.append(event)
    events.sort(key=lambda item: item.start)
    return events[:limit]


def _next_event_from_routines(
    routines: Sequence[RoutineEntry],
    now: datetime,
    pet_id: str,
) -> ScheduledEvent | None:
    future = _future_events_from_routines(routines, now, pet_id, limit=1)
    return future[0] if future else None


def _latest_due_event(
    routines: Sequence[RoutineEntry],
    now: datetime,
    pet_id: str,
) -> ScheduledEvent | None:
    due_events: list[ScheduledEvent] = []
    for day_offset in range(0, 2):
        day = now.date() - timedelta(days=day_offset)
        for routine in routines:
            if not routine.occurs_on(day):
                continue
            event = routine.occurrence(pet_id, day, now.tzinfo)
            if event.start <= now:
                due_events.append(event)
    if not due_events:
        return None
    return max(due_events, key=lambda item: item.start)


def _next_appointment_event(
    appointments: Sequence[AppointmentEntry],
    now: datetime,
    pet_id: str,
) -> ScheduledEvent | None:
    future = [appointment.to_event(pet_id, now.tzinfo) for appointment in appointments]
    future = [event for event in future if event.start > now]
    if not future:
        return None
    return min(future, key=lambda item: item.start)


def _ensure_tz(value: datetime, tzinfo) -> datetime:
    if value.tzinfo is not None:
        return value
    return value.replace(tzinfo=tzinfo)


def _coerce_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _default_behavior_message(behavior_type: str) -> str:
    messages = {
        ANOMALY_VOMITING: "Vomiting observed. Review food, hydration, and contact a veterinarian if repeated.",
        ANOMALY_COUGH: "Coughing observed. Monitor respiratory signs and record progression.",
        ANOMALY_LIMPING: "Limping observed. Reduce load and monitor mobility.",
        ANOMALY_GAIT: "Gait change observed. Review mobility and camera footage.",
        ANOMALY_RESTLESSNESS: "Restlessness observed. Review stressors, enrichment, and separation context.",
    }
    return messages.get(behavior_type, behavior_type.replace("_", " ").title())


def normalize_avatar_reference(value: Any) -> str | None:
    """Normalize an avatar value into a HA-friendly entity_picture reference."""
    text = _coerce_optional_str(value)
    if text is None:
        return None

    normalized = text.strip()
    if not normalized:
        return None

    if normalized.startswith("/config/www/"):
        return f"/local/{normalized.removeprefix('/config/www/')}"
    if normalized.startswith("/www/"):
        return f"/local/{normalized.removeprefix('/www/')}"
    if normalized.startswith("www/"):
        return f"/local/{normalized.removeprefix('www/')}"
    if normalized.startswith(("http://", "https://", "/local/", "/media/local/", "data:image/")):
        return normalized

    image_extensions = (".png", ".jpg", ".jpeg", ".webp", ".gif")
    if normalized.lower().endswith(image_extensions):
        stripped = normalized.lstrip("/")
        if stripped.startswith("local/"):
            return f"/{stripped}"
        return f"/local/{stripped}"

    return normalized

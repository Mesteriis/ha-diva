"""Config flow for the DIVA integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult
from homeassistant.core import callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers.selector import (
    DateSelector,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    selector,
)

from .const import (
    CONF_ALLERGEN,
    CONF_ALLERGIES,
    CONF_AVATAR,
    CONF_BEHAVIOR_SIGNAL_ENTITY_IDS,
    CONF_BIRTHDATE,
    CONF_BLE_TRACKER_ENTITY_ID,
    CONF_BODY_CONDITION_SCORE,
    CONF_BREED,
    CONF_CAMERA_ROOM_NAME,
    CONF_CAMERA_ENTITY_ID,
    CONF_CALENDAR_ENTITY_ID,
    CONF_CALENDAR_LINKS,
    CONF_CAREGIVER,
    CONF_CARE_ROLES,
    CONF_CAREGIVERS,
    CONF_CARE_SHIFTS,
    CONF_CARE_ROUTINES,
    CONF_CARE_SCHEDULE,
    CONF_CHECKLIST_FREQUENCY,
    CONF_CHECKLIST_ITEMS,
    CONF_COLD_THRESHOLD_C,
    CONF_CHRONIC_CONDITIONS,
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
    CONF_HISTORY_CATEGORY,
    CONF_HISTORY_DATE,
    CONF_HISTORY_TITLE,
    CONF_HUB_NAME,
    CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS,
    CONF_INSURANCE_POLICY,
    CONF_MICROCHIP_ID,
    CONF_MEDICAL_COUNTRY,
    CONF_MEDICAL_HISTORY,
    CONF_MEDICAL_REGION,
    CONF_MEDICATION_COURSES,
    CONF_MEDICATION_NAME,
    CONF_MEDICATION_ROUTE,
    CONF_MEDICATION_TIMES,
    CONF_MONITOR_INTERVAL_DAYS,
    CONF_NAME,
    CONF_NOTES,
    CONF_APPROVAL_REQUIRED_ACTIONS,
    CONF_PASSPORT_NUMBER,
    CONF_PETS,
    CONF_PET_ID,
    CONF_PET_SCHEMA,
    CONF_PRIMARY_VET,
    CONF_REASON,
    CONF_REGIONAL_POLICY,
    CONF_REQUIRES_APPROVAL,
    CONF_ROLE,
    CONF_ROOM_MATCH_STATE,
    CONF_ROOM_NAME,
    CONF_ROOM_PRESENCE_SOURCES,
    CONF_ROOM_SOURCE_PRIORITY,
    CONF_RECURRENCE_MONTHS,
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
    CONF_REACTION,
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
    CONF_VACCINE_DOSE_ID,
    CONF_VACCINE_NAME,
    CONF_VACCINE_STATUS,
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
    APPROVAL_ACTION_OPTIONS,
    CALENDAR_SOURCE_OF_TRUTH_OPTIONS,
    CHECKLIST_FREQUENCIES,
    DEFAULT_COLD_THRESHOLD_C,
    DEFAULT_BODY_CONDITION_SCORE,
    DEFAULT_HEAT_THRESHOLD_C,
    DEFAULT_HUB_NAME,
    DEFAULT_MEDICAL_COUNTRY,
    DEFAULT_MEDICAL_REGION,
    DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
    DIET_MODES,
    DOMAIN,
    FOOD_KINDS,
    MEAL_TYPES,
    OPERATION_MODES,
    ROUTINE_CATEGORIES,
    ROUTINE_EXCEPTION_ACTIONS,
    VACCINE_PROFILE_OPTIONS,
    CONF_KCAL_PER_GRAM,
    CONF_FROM_FOOD_NAME,
    CONF_FROM_PERCENT,
)
from .pet import (
    BowlArea,
    generate_pet_id,
    normalize_pet_config_record,
    normalize_avatar_reference,
    parse_calendar_links,
    parse_approval_required_actions,
    parse_care_roles,
    parse_chronic_conditions,
    parse_care_shifts,
    parse_checklist_items,
    parse_food_catalog,
    parse_food_transition_plan,
    parse_schedule_exceptions,
    parse_medication_courses,
    parse_room_presence_sources,
    parse_safe_zones,
    parse_vaccine_overrides,
    parse_care_schedule,
    parse_feeding_schedule,
    parse_vet_appointments,
    parse_walk_schedule,
    serialize_diva_entry_settings_v3,
)

BEHAVIOR_SECTION = "behavior_settings"
CALENDAR_SECTION = "calendar_settings"
CAMERA_SECTION = "camera_settings"
MEDICAL_SECTION = "medical_settings"
NUTRITION_SECTION = "nutrition_settings"
OPERATIONS_SECTION = "operations_settings"
PASSPORT_SECTION = "passport_settings"
ROUTINE_SECTION = "routine_settings"
SELECTED_PET = "selected_pet"
TRACKING_SECTION = "tracking_settings"
HUB_UNIQUE_ID = "diva_hub"

WEEKDAY_OPTIONS = [
    SelectOptionDict(value="mon", label="Mon"),
    SelectOptionDict(value="tue", label="Tue"),
    SelectOptionDict(value="wed", label="Wed"),
    SelectOptionDict(value="thu", label="Thu"),
    SelectOptionDict(value="fri", label="Fri"),
    SelectOptionDict(value="sat", label="Sat"),
    SelectOptionDict(value="sun", label="Sun"),
]


class DivaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DIVA."""

    VERSION = 3

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial setup flow."""
        errors: dict[str, str] = {}
        if user_input is not None:
            cleaned_pet, errors = _validate_pet_input(user_input)
            if not errors:
                await self.async_set_unique_id(HUB_UNIQUE_ID)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=DEFAULT_HUB_NAME,
                    data=serialize_diva_entry_settings_v3(
                        hub_name=DEFAULT_HUB_NAME,
                        show_editor_in_sidebar=DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
                        pets=[cleaned_pet],
                    ),
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_user_schema(user_input),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Reconfigure hub metadata."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if entry is None:
            return self.async_abort(reason="entry_not_found")

        current = _entry_settings(entry)
        errors: dict[str, str] = {}
        if user_input is not None:
            hub_name = str(user_input[CONF_HUB_NAME]).strip()
            if not hub_name:
                errors[CONF_HUB_NAME] = "invalid_hub_name"
            else:
                self.hass.config_entries.async_update_entry(
                    entry,
                    title=hub_name,
                    data=serialize_diva_entry_settings_v3(
                        hub_name=hub_name,
                        show_editor_in_sidebar=current.get(
                            CONF_SHOW_EDITOR_IN_SIDEBAR,
                            DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
                        ),
                        pets=current[CONF_PETS],
                    ),
                    options={},
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HUB_NAME,
                        default=current.get(CONF_HUB_NAME, DEFAULT_HUB_NAME),
                    ): TextSelector(),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> config_entries.OptionsFlow:
        """Return the DIVA options flow."""
        return DivaOptionsFlow(config_entry)


class DivaOptionsFlow(config_entries.OptionsFlow):
    """Manage pets inside the DIVA hub."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the options flow handler."""
        self._entry = entry
        self._settings = _entry_settings(entry)
        self._selected_pet_id: str | None = None

    async def async_step_init(self, _user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Show the maintenance menu."""
        options = ["hub_settings", "add_pet"]
        if self._settings[CONF_PETS]:
            options.extend(["edit_pet_select", "remove_pet"])
        return self.async_show_menu(step_id="init", menu_options=options)

    async def async_step_hub_settings(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Edit hub-level DIVA settings."""
        if user_input is not None:
            self._settings[CONF_SHOW_EDITOR_IN_SIDEBAR] = bool(
                user_input.get(CONF_SHOW_EDITOR_IN_SIDEBAR, DEFAULT_SHOW_EDITOR_IN_SIDEBAR)
            )
            return self.async_create_entry(
                title="",
                data=serialize_diva_entry_settings_v3(
                    hub_name=self._settings[CONF_HUB_NAME],
                    show_editor_in_sidebar=self._settings.get(
                        CONF_SHOW_EDITOR_IN_SIDEBAR,
                        DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
                    ),
                    pets=self._settings[CONF_PETS],
                ),
            )

        return self.async_show_form(
            step_id="hub_settings",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SHOW_EDITOR_IN_SIDEBAR,
                        default=self._settings.get(
                            CONF_SHOW_EDITOR_IN_SIDEBAR,
                            DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
                        ),
                    ): selector({"boolean": {}})
                }
            ),
        )

    async def async_step_add_pet(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Add a pet profile."""
        errors: dict[str, str] = {}
        if user_input is not None:
            cleaned_pet, errors = _validate_pet_input(
                user_input,
                existing_pet_ids={pet[CONF_PET_ID] for pet in self._settings[CONF_PETS]},
            )
            if not errors:
                self._settings[CONF_PETS].append(cleaned_pet)
                return self.async_create_entry(
                    title="",
                    data=serialize_diva_entry_settings_v3(
                        hub_name=self._settings[CONF_HUB_NAME],
                        show_editor_in_sidebar=self._settings.get(
                            CONF_SHOW_EDITOR_IN_SIDEBAR,
                            DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
                        ),
                        pets=self._settings[CONF_PETS],
                    ),
                )

        return self.async_show_form(
            step_id="add_pet",
            data_schema=_build_pet_schema(user_input),
            errors=errors,
        )

    async def async_step_edit_pet_select(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Select which pet to edit."""
        if not self._settings[CONF_PETS]:
            return self.async_abort(reason="no_pets")

        if user_input is not None:
            self._selected_pet_id = str(user_input[SELECTED_PET])
            return await self.async_step_edit_pet()

        return self.async_show_form(
            step_id="edit_pet_select",
            data_schema=vol.Schema(
                {
                    vol.Required(SELECTED_PET): SelectSelector(
                        SelectSelectorConfig(
                            options=_pet_options(self._settings[CONF_PETS]),
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )

    async def async_step_edit_pet(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Edit the selected pet profile."""
        pet = _find_pet(self._settings[CONF_PETS], self._selected_pet_id)
        if pet is None:
            return self.async_abort(reason="pet_not_found")

        errors: dict[str, str] = {}
        if user_input is not None:
            cleaned_pet, errors = _validate_pet_input(
                user_input,
                existing_pet_ids={existing[CONF_PET_ID] for existing in self._settings[CONF_PETS]},
                editing_pet_id=pet[CONF_PET_ID],
            )
            if not errors:
                cleaned_pet[CONF_PET_ID] = pet[CONF_PET_ID]
                self._settings[CONF_PETS] = [
                    cleaned_pet if existing[CONF_PET_ID] == pet[CONF_PET_ID] else existing
                    for existing in self._settings[CONF_PETS]
                ]
                return self.async_create_entry(
                    title="",
                    data=serialize_diva_entry_settings_v3(
                        hub_name=self._settings[CONF_HUB_NAME],
                        show_editor_in_sidebar=self._settings.get(
                            CONF_SHOW_EDITOR_IN_SIDEBAR,
                            DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
                        ),
                        pets=self._settings[CONF_PETS],
                    ),
                )

        return self.async_show_form(
            step_id="edit_pet",
            data_schema=_build_pet_schema(_pet_defaults_for_form(pet)),
            errors=errors,
        )

    async def async_step_remove_pet(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Select which pet to remove."""
        if not self._settings[CONF_PETS]:
            return self.async_abort(reason="no_pets")
        if len(self._settings[CONF_PETS]) == 1:
            return self.async_abort(reason="cannot_remove_last_pet")

        if user_input is not None:
            self._selected_pet_id = str(user_input[SELECTED_PET])
            return await self.async_step_remove_pet_confirm()

        return self.async_show_form(
            step_id="remove_pet",
            data_schema=vol.Schema(
                {
                    vol.Required(SELECTED_PET): SelectSelector(
                        SelectSelectorConfig(
                            options=_pet_options(self._settings[CONF_PETS]),
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )

    async def async_step_remove_pet_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Confirm pet removal."""
        pet = _find_pet(self._settings[CONF_PETS], self._selected_pet_id)
        if pet is None:
            return self.async_abort(reason="pet_not_found")

        if user_input is not None:
            if user_input.get("confirm"):
                self._settings[CONF_PETS] = [
                    existing
                    for existing in self._settings[CONF_PETS]
                    if existing[CONF_PET_ID] != pet[CONF_PET_ID]
                ]
                return self.async_create_entry(
                    title="",
                    data=serialize_diva_entry_settings_v3(
                        hub_name=self._settings[CONF_HUB_NAME],
                        show_editor_in_sidebar=self._settings.get(
                            CONF_SHOW_EDITOR_IN_SIDEBAR,
                            DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
                        ),
                        pets=self._settings[CONF_PETS],
                    ),
                )
            return self.async_abort(reason="not_confirmed")

        return self.async_show_form(
            step_id="remove_pet_confirm",
            data_schema=vol.Schema({vol.Required("confirm", default=False): bool}),
            description_placeholders={"pet_name": pet[CONF_NAME]},
        )


def _build_user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    return vol.Schema(_build_pet_schema_fields(defaults or {}))


def _build_pet_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    return vol.Schema(_build_pet_schema_fields(defaults or {}))


def _routine_object_selector(*, category: str) -> Any:
    fields: dict[str, Any] = {
        CONF_ROUTINE_TIME: {"selector": {"time": {}}},
        CONF_ROUTINE_DAYS: {
            "selector": {
                "select": {
                    "options": [{"value": option.value, "label": option.label} for option in WEEKDAY_OPTIONS],
                    "multiple": True,
                    "mode": "dropdown",
                }
            }
        },
        CONF_ROUTINE_LABEL: {"selector": {"text": {}}},
        CONF_ROUTINE_DURATION_MINUTES: {
            "selector": {"number": {"min": 5, "max": 240, "step": 5, "mode": "box"}}
        },
    }
    if category == CONF_FEEDING_ROUTINES:
        fields[CONF_ROUTINE_MEAL_TYPE] = {
            "selector": {
                "select": {
                    "options": [{"value": meal_type, "label": meal_type} for meal_type in MEAL_TYPES],
                    "mode": "dropdown",
                }
            }
        }
        fields[CONF_ROUTINE_PORTION_GRAMS] = {
            "selector": {"number": {"min": 1, "max": 2000, "step": 1, "mode": "box"}}
        }
    if category in {CONF_WALK_ROUTINES, CONF_CARE_ROUTINES}:
        fields[CONF_ROUTINE_LOCATION] = {"selector": {"text": {}}}
    if category == CONF_CARE_ROUTINES:
        fields[CONF_ROUTINE_CATEGORY] = {
            "selector": {
                "select": {
                    "options": [{"value": item, "label": item} for item in ROUTINE_CATEGORIES if item != "feed"],
                    "mode": "dropdown",
                }
            }
        }
        fields[CONF_NOTES] = {"selector": {"text": {"multiline": True}}}

    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_ROUTINE_LABEL,
                "description_field": CONF_ROUTINE_TIME,
                "fields": fields,
            }
        }
    )


def _exceptions_object_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_ROUTINE_LABEL,
                "description_field": CONF_ROUTINE_EXCEPTION_DATE,
                "fields": {
                    CONF_ROUTINE_EXCEPTION_DATE: {"selector": {"date": {}}},
                    CONF_ROUTINE_EXCEPTION_ACTION: {
                        "selector": {
                            "select": {
                                "options": [
                                    {"value": action, "label": action} for action in ROUTINE_EXCEPTION_ACTIONS
                                ],
                                "mode": "dropdown",
                            }
                        }
                    },
                    CONF_ROUTINE_CATEGORY: {
                        "selector": {
                            "select": {
                                "options": [
                                    {"value": category, "label": category} for category in ROUTINE_CATEGORIES
                                ],
                                "mode": "dropdown",
                            }
                        }
                    },
                    CONF_ROUTINE_EXCEPTION_TIME: {"selector": {"time": {}}},
                    CONF_ROUTINE_DURATION_MINUTES: {
                        "selector": {"number": {"min": 5, "max": 240, "step": 5, "mode": "box"}}
                    },
                    CONF_ROUTINE_LABEL: {"selector": {"text": {}}},
                    CONF_ROUTINE_MEAL_TYPE: {
                        "selector": {
                            "select": {
                                "options": [{"value": meal_type, "label": meal_type} for meal_type in MEAL_TYPES],
                                "mode": "dropdown",
                            }
                        }
                    },
                    CONF_ROUTINE_PORTION_GRAMS: {
                        "selector": {"number": {"min": 1, "max": 2000, "step": 1, "mode": "box"}}
                    },
                    CONF_ROUTINE_LOCATION: {"selector": {"text": {}}},
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _food_catalog_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_FOOD_NAME,
                "description_field": CONF_FOOD_BRAND,
                "fields": {
                    CONF_FOOD_NAME: {"selector": {"text": {}}},
                    CONF_FOOD_BRAND: {"selector": {"text": {}}},
                    CONF_FOOD_KIND: {
                        "selector": {
                            "select": {
                                "options": [{"value": value, "label": value} for value in FOOD_KINDS],
                                "mode": "dropdown",
                            }
                        }
                    },
                    CONF_ROUTINE_MEAL_TYPE: {
                        "selector": {
                            "select": {
                                "options": [{"value": meal_type, "label": meal_type} for meal_type in MEAL_TYPES],
                                "mode": "dropdown",
                            }
                        }
                    },
                    CONF_KCAL_PER_GRAM: {
                        "selector": {"number": {"min": 0.1, "max": 10.0, "step": 0.1, "mode": "box"}}
                    },
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _food_transition_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_TO_FOOD_NAME,
                "description_field": CONF_TRANSITION_DATE,
                "fields": {
                    CONF_TRANSITION_DATE: {"selector": {"date": {}}},
                    CONF_FROM_FOOD_NAME: {"selector": {"text": {}}},
                    CONF_TO_FOOD_NAME: {"selector": {"text": {}}},
                    CONF_FROM_PERCENT: {
                        "selector": {"number": {"min": 0, "max": 100, "step": 5, "mode": "box"}}
                    },
                    CONF_TO_PERCENT: {
                        "selector": {"number": {"min": 0, "max": 100, "step": 5, "mode": "box"}}
                    },
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _calendar_links_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_CALENDAR_ENTITY_ID,
                "description_field": CONF_SOURCE_OF_TRUTH,
                "fields": {
                    CONF_CALENDAR_ENTITY_ID: {
                        "selector": {
                            "entity": {
                                "filter": {
                                    "domain": "calendar",
                                }
                            }
                        }
                    },
                    CONF_SOURCE_OF_TRUTH: {
                        "selector": {
                            "select": {
                                "options": [
                                    {"value": value, "label": value}
                                    for value in CALENDAR_SOURCE_OF_TRUTH_OPTIONS
                                ],
                                "mode": "dropdown",
                            }
                        }
                    },
                },
            }
        }
    )


def _medication_courses_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_MEDICATION_NAME,
                "description_field": CONF_MEDICATION_TIMES,
                "fields": {
                    CONF_MEDICATION_NAME: {"selector": {"text": {}}},
                    CONF_DOSE: {"selector": {"text": {}}},
                    CONF_MEDICATION_TIMES: {"selector": {"text": {}}},
                    CONF_START_DATE: {"selector": {"date": {}}},
                    CONF_END_DATE: {"selector": {"date": {}}},
                    CONF_MEDICATION_ROUTE: {"selector": {"text": {}}},
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _chronic_conditions_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_CONDITION_NAME,
                "description_field": CONF_CONDITION_STATUS,
                "fields": {
                    CONF_CONDITION_NAME: {"selector": {"text": {}}},
                    CONF_CONDITION_STATUS: {"selector": {"text": {}}},
                    CONF_MONITOR_INTERVAL_DAYS: {
                        "selector": {"number": {"min": 1, "max": 365, "step": 1, "mode": "box"}}
                    },
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _diagnoses_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_DIAGNOSIS_NAME,
                "description_field": CONF_DIAGNOSIS_STATUS,
                "fields": {
                    CONF_DIAGNOSIS_NAME: {"selector": {"text": {}}},
                    CONF_DIAGNOSIS_STATUS: {"selector": {"text": {}}},
                    CONF_DIAGNOSED_ON: {"selector": {"date": {}}},
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _allergies_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_ALLERGEN,
                "description_field": CONF_REACTION,
                "fields": {
                    CONF_ALLERGEN: {"selector": {"text": {}}},
                    CONF_REACTION: {"selector": {"text": {}}},
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _contraindications_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_CONTRAINDICATION,
                "description_field": CONF_REASON,
                "fields": {
                    CONF_CONTRAINDICATION: {"selector": {"text": {}}},
                    CONF_REASON: {"selector": {"text": {}}},
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _medical_history_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_HISTORY_TITLE,
                "description_field": CONF_HISTORY_DATE,
                "fields": {
                    CONF_HISTORY_DATE: {"selector": {"date": {}}},
                    CONF_HISTORY_TITLE: {"selector": {"text": {}}},
                    CONF_HISTORY_CATEGORY: {"selector": {"text": {}}},
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _vaccine_overrides_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_VACCINE_NAME,
                "description_field": CONF_DUE_DATE,
                "fields": {
                    CONF_VACCINE_DOSE_ID: {"selector": {"text": {}}},
                    CONF_VACCINE_NAME: {"selector": {"text": {}}},
                    CONF_DUE_DATE: {"selector": {"date": {}}},
                    CONF_ROUTINE_CATEGORY: {"selector": {"text": {}}},
                    CONF_RECURRENCE_MONTHS: {
                        "selector": {"number": {"min": 1, "max": 60, "step": 1, "mode": "box"}}
                    },
                    CONF_VACCINE_STATUS: {"selector": {"text": {}}},
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _safe_zones_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_ZONE_NAME,
                "description_field": CONF_ZONE_RADIUS_M,
                "fields": {
                    CONF_ZONE_NAME: {"selector": {"text": {}}},
                    CONF_ZONE_LATITUDE: {
                        "selector": {"number": {"min": -90.0, "max": 90.0, "step": 0.000001, "mode": "box"}}
                    },
                    CONF_ZONE_LONGITUDE: {
                        "selector": {"number": {"min": -180.0, "max": 180.0, "step": 0.000001, "mode": "box"}}
                    },
                    CONF_ZONE_RADIUS_M: {
                        "selector": {"number": {"min": 5.0, "max": 10000.0, "step": 5.0, "mode": "box"}}
                    },
                },
            }
        }
    )


def _room_presence_sources_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_ROOM_NAME,
                "description_field": "entity_id",
                "fields": {
                    CONF_ROOM_NAME: {"selector": {"text": {}}},
                    "entity_id": {"selector": {"text": {}}},
                    CONF_ROOM_MATCH_STATE: {"selector": {"text": {}}},
                    CONF_ROOM_SOURCE_PRIORITY: {
                        "selector": {"number": {"min": 1, "max": 10, "step": 1, "mode": "box"}}
                    },
                },
            }
        }
    )


def _care_roles_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_CAREGIVER,
                "description_field": CONF_ROLE,
                "fields": {
                    CONF_CAREGIVER: {"selector": {"text": {}}},
                    CONF_ROLE: {"selector": {"text": {}}},
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _care_shifts_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_ROUTINE_LABEL,
                "description_field": CONF_CAREGIVER,
                "fields": {
                    CONF_ROUTINE_LABEL: {"selector": {"text": {}}},
                    CONF_CAREGIVER: {"selector": {"text": {}}},
                    CONF_ROLE: {"selector": {"text": {}}},
                    CONF_SHIFT_START_TIME: {"selector": {"time": {}}},
                    CONF_SHIFT_END_TIME: {"selector": {"time": {}}},
                    CONF_ROUTINE_DAYS: {
                        "selector": {
                            "select": {
                                "options": [{"value": option.value, "label": option.label} for option in WEEKDAY_OPTIONS],
                                "multiple": True,
                                "mode": "dropdown",
                            }
                        }
                    },
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _checklist_items_selector() -> Any:
    return selector(
        {
            "object": {
                "multiple": True,
                "label_field": CONF_ROUTINE_LABEL,
                "description_field": CONF_ROUTINE_CATEGORY,
                "fields": {
                    CONF_ROUTINE_LABEL: {"selector": {"text": {}}},
                    CONF_CHECKLIST_FREQUENCY: {
                        "selector": {
                            "select": {
                                "options": [{"value": item, "label": item} for item in CHECKLIST_FREQUENCIES],
                                "mode": "dropdown",
                            }
                        }
                    },
                    CONF_ROUTINE_CATEGORY: {
                        "selector": {
                            "select": {
                                "options": [{"value": item, "label": item} for item in ROUTINE_CATEGORIES],
                                "mode": "dropdown",
                            }
                        }
                    },
                    CONF_CAREGIVER: {"selector": {"text": {}}},
                    CONF_REQUIRES_APPROVAL: {"selector": {"boolean": {}}},
                    CONF_NOTES: {"selector": {"text": {"multiline": True}}},
                },
            }
        }
    )


def _build_pet_schema_fields(defaults: dict[str, Any]) -> dict[Any, Any]:
    camera_defaults = defaults.get(CAMERA_SECTION, {})
    medical_defaults = defaults.get(MEDICAL_SECTION, {})
    routine_defaults = defaults.get(ROUTINE_SECTION, {})
    calendar_defaults = defaults.get(CALENDAR_SECTION, {})
    nutrition_defaults = defaults.get(NUTRITION_SECTION, {})
    operations_defaults = defaults.get(OPERATIONS_SECTION, {})
    passport_defaults = defaults.get(PASSPORT_SECTION, {})
    tracking_defaults = defaults.get(TRACKING_SECTION, {})
    behavior_defaults = defaults.get(BEHAVIOR_SECTION, {})

    return {
        vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): TextSelector(),
        vol.Required(CONF_SPECIES, default=defaults.get(CONF_SPECIES, "dog")): TextSelector(),
        vol.Required(CONF_BREED, default=defaults.get(CONF_BREED, "")): TextSelector(),
        vol.Required(CONF_BIRTHDATE, default=defaults.get(CONF_BIRTHDATE)): DateSelector(),
        vol.Required(
            CONF_WEIGHT,
            default=defaults.get(CONF_WEIGHT, 5.0),
        ): NumberSelector(
            NumberSelectorConfig(
                min=0.1,
                max=200.0,
                step=0.1,
                unit_of_measurement="kg",
                mode=NumberSelectorMode.BOX,
            )
        ),
        vol.Required(
            CONF_DIET_MODE,
            default=defaults.get(CONF_DIET_MODE, DIET_MODES[1]),
        ): SelectSelector(
            SelectSelectorConfig(
                options=[SelectOptionDict(value=mode, label=mode) for mode in DIET_MODES],
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(
            CONF_AVATAR,
            default=defaults.get(CONF_AVATAR, ""),
        ): TextSelector(),
        vol.Optional(ROUTINE_SECTION): section(
            vol.Schema(
                {
                    vol.Optional(
                        CONF_FEEDING_ROUTINES,
                        default=routine_defaults.get(CONF_FEEDING_ROUTINES, []),
                    ): _routine_object_selector(category=CONF_FEEDING_ROUTINES),
                    vol.Optional(
                        CONF_WALK_ROUTINES,
                        default=routine_defaults.get(CONF_WALK_ROUTINES, []),
                    ): _routine_object_selector(category=CONF_WALK_ROUTINES),
                    vol.Optional(
                        CONF_CARE_ROUTINES,
                        default=routine_defaults.get(CONF_CARE_ROUTINES, []),
                    ): _routine_object_selector(category=CONF_CARE_ROUTINES),
                    vol.Optional(
                        CONF_ROUTINE_EXCEPTIONS,
                        default=routine_defaults.get(CONF_ROUTINE_EXCEPTIONS, []),
                    ): _exceptions_object_selector(),
                    vol.Optional(
                        CONF_DEFAULT_MANUAL_MODE,
                        default=routine_defaults.get(CONF_DEFAULT_MANUAL_MODE, OPERATION_MODES[0]),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[SelectOptionDict(value=mode, label=mode) for mode in OPERATION_MODES],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_WEATHER_ADAPTATION,
                        default=routine_defaults.get(CONF_WEATHER_ADAPTATION, True),
                    ): selector({"boolean": {}}),
                    vol.Optional(
                        CONF_HEAT_THRESHOLD_C,
                        default=routine_defaults.get(CONF_HEAT_THRESHOLD_C, DEFAULT_HEAT_THRESHOLD_C),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=10.0,
                            max=50.0,
                            step=0.5,
                            unit_of_measurement="°C",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_COLD_THRESHOLD_C,
                        default=routine_defaults.get(CONF_COLD_THRESHOLD_C, DEFAULT_COLD_THRESHOLD_C),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=-20.0,
                            max=15.0,
                            step=0.5,
                            unit_of_measurement="°C",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            {"collapsed": True},
        ),
        vol.Optional(CALENDAR_SECTION): section(
            vol.Schema(
                {
                    vol.Optional(
                        CONF_VET_APPOINTMENTS,
                        default=calendar_defaults.get(CONF_VET_APPOINTMENTS, ""),
                    ): TextSelector(TextSelectorConfig(multiline=True)),
                    vol.Optional(
                        CONF_CALENDAR_LINKS,
                        default=calendar_defaults.get(CONF_CALENDAR_LINKS, []),
                    ): _calendar_links_selector(),
                }
            ),
            {"collapsed": True},
        ),
        vol.Optional(NUTRITION_SECTION): section(
            vol.Schema(
                {
                    vol.Optional(
                        CONF_FOOD_CATALOG,
                        default=nutrition_defaults.get(CONF_FOOD_CATALOG, []),
                    ): _food_catalog_selector(),
                    vol.Optional(
                        CONF_FOOD_TRANSITION_PLAN,
                        default=nutrition_defaults.get(CONF_FOOD_TRANSITION_PLAN, []),
                    ): _food_transition_selector(),
                }
            ),
            {"collapsed": True},
        ),
        vol.Optional(MEDICAL_SECTION): section(
            vol.Schema(
                {
                    vol.Optional(
                        CONF_MEDICAL_COUNTRY,
                        default=medical_defaults.get(CONF_MEDICAL_COUNTRY, DEFAULT_MEDICAL_COUNTRY),
                    ): TextSelector(),
                    vol.Optional(
                        CONF_MEDICAL_REGION,
                        default=medical_defaults.get(CONF_MEDICAL_REGION, DEFAULT_MEDICAL_REGION),
                    ): TextSelector(),
                    vol.Optional(
                        CONF_REGIONAL_POLICY,
                        default=medical_defaults.get(CONF_REGIONAL_POLICY, medical_defaults.get(CONF_MEDICAL_REGION, DEFAULT_MEDICAL_REGION)),
                    ): TextSelector(),
                    vol.Optional(
                        CONF_VACCINE_PROFILE,
                        default=medical_defaults.get(CONF_VACCINE_PROFILE, VACCINE_PROFILE_OPTIONS[0]),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[SelectOptionDict(value=value, label=value) for value in VACCINE_PROFILE_OPTIONS],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_VET_OVERRIDE,
                        default=medical_defaults.get(CONF_VET_OVERRIDE, True),
                    ): selector({"boolean": {}}),
                    vol.Optional(
                        CONF_BODY_CONDITION_SCORE,
                        default=medical_defaults.get(CONF_BODY_CONDITION_SCORE, DEFAULT_BODY_CONDITION_SCORE),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=1.0,
                            max=9.0,
                            step=0.5,
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                    _optional_number_field(
                        CONF_WEIGHT_GOAL_MIN_KG,
                        medical_defaults.get(CONF_WEIGHT_GOAL_MIN_KG),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=0.1,
                            max=200.0,
                            step=0.1,
                            unit_of_measurement="kg",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                    _optional_number_field(
                        CONF_WEIGHT_GOAL_MAX_KG,
                        medical_defaults.get(CONF_WEIGHT_GOAL_MAX_KG),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=0.1,
                            max=200.0,
                            step=0.1,
                            unit_of_measurement="kg",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_MEDICATION_COURSES,
                        default=medical_defaults.get(CONF_MEDICATION_COURSES, []),
                    ): _medication_courses_selector(),
                    vol.Optional(
                        CONF_CHRONIC_CONDITIONS,
                        default=medical_defaults.get(CONF_CHRONIC_CONDITIONS, []),
                    ): _chronic_conditions_selector(),
                    vol.Optional(
                        CONF_DIAGNOSES,
                        default=medical_defaults.get(CONF_DIAGNOSES, []),
                    ): _diagnoses_selector(),
                    vol.Optional(
                        CONF_ALLERGIES,
                        default=medical_defaults.get(CONF_ALLERGIES, []),
                    ): _allergies_selector(),
                    vol.Optional(
                        CONF_CONTRAINDICATIONS,
                        default=medical_defaults.get(CONF_CONTRAINDICATIONS, []),
                    ): _contraindications_selector(),
                    vol.Optional(
                        CONF_MEDICAL_HISTORY,
                        default=medical_defaults.get(CONF_MEDICAL_HISTORY, []),
                    ): _medical_history_selector(),
                    vol.Optional(
                        CONF_VACCINE_OVERRIDES,
                        default=medical_defaults.get(CONF_VACCINE_OVERRIDES, []),
                    ): _vaccine_overrides_selector(),
                }
            ),
            {"collapsed": True},
        ),
        vol.Optional(PASSPORT_SECTION): section(
            vol.Schema(
                {
                    vol.Optional(
                        CONF_PASSPORT_NUMBER,
                        default=passport_defaults.get(CONF_PASSPORT_NUMBER, ""),
                    ): TextSelector(),
                    vol.Optional(
                        CONF_MICROCHIP_ID,
                        default=passport_defaults.get(CONF_MICROCHIP_ID, ""),
                    ): TextSelector(),
                    vol.Optional(
                        CONF_INSURANCE_POLICY,
                        default=passport_defaults.get(CONF_INSURANCE_POLICY, ""),
                    ): TextSelector(),
                    vol.Optional(
                        CONF_PRIMARY_VET,
                        default=passport_defaults.get(CONF_PRIMARY_VET, ""),
                    ): TextSelector(),
                    vol.Optional(
                        CONF_VET_PHONE,
                        default=passport_defaults.get(CONF_VET_PHONE, ""),
                    ): TextSelector(),
                }
            ),
            {"collapsed": True},
        ),
        vol.Optional(TRACKING_SECTION): section(
            vol.Schema(
                {
                    _optional_entity_field(CONF_GPS_TRACKER_ENTITY_ID, tracking_defaults.get(CONF_GPS_TRACKER_ENTITY_ID)): EntitySelector(
                        EntitySelectorConfig(domain="device_tracker")
                    ),
                    _optional_entity_field(CONF_BLE_TRACKER_ENTITY_ID, tracking_defaults.get(CONF_BLE_TRACKER_ENTITY_ID)): EntitySelector(
                        EntitySelectorConfig(domain=["sensor", "binary_sensor", "device_tracker"])
                    ),
                    vol.Optional(
                        CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS,
                        default=tracking_defaults.get(CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS, []),
                    ): EntitySelector(
                        EntitySelectorConfig(domain=["person", "device_tracker"], multiple=True)
                    ),
                    vol.Optional(
                        CONF_SAFE_ZONES,
                        default=tracking_defaults.get(CONF_SAFE_ZONES, []),
                    ): _safe_zones_selector(),
                    vol.Optional(
                        CONF_ROOM_PRESENCE_SOURCES,
                        default=tracking_defaults.get(CONF_ROOM_PRESENCE_SOURCES, []),
                    ): _room_presence_sources_selector(),
                    vol.Optional(
                        CONF_CAMERA_ROOM_NAME,
                        default=tracking_defaults.get(CONF_CAMERA_ROOM_NAME, ""),
                    ): TextSelector(),
                    _optional_entity_field(CONF_WEATHER_ENTITY_ID, tracking_defaults.get(CONF_WEATHER_ENTITY_ID)): EntitySelector(
                        EntitySelectorConfig(domain=["weather", "sensor"])
                    ),
                }
            ),
            {"collapsed": True},
        ),
        vol.Optional(BEHAVIOR_SECTION): section(
            vol.Schema(
                {
                    vol.Optional(
                        CONF_BEHAVIOR_SIGNAL_ENTITY_IDS,
                        default=behavior_defaults.get(CONF_BEHAVIOR_SIGNAL_ENTITY_IDS, []),
                    ): EntitySelector(
                        EntitySelectorConfig(domain=["binary_sensor", "sensor"], multiple=True)
                    ),
                    vol.Optional(
                        CONF_CAREGIVERS,
                        default=behavior_defaults.get(CONF_CAREGIVERS, ""),
                    ): TextSelector(TextSelectorConfig(multiline=True)),
                }
            ),
            {"collapsed": True},
        ),
        vol.Optional(OPERATIONS_SECTION): section(
            vol.Schema(
                {
                    vol.Optional(
                        CONF_CARE_ROLES,
                        default=operations_defaults.get(CONF_CARE_ROLES, []),
                    ): _care_roles_selector(),
                    vol.Optional(
                        CONF_CARE_SHIFTS,
                        default=operations_defaults.get(CONF_CARE_SHIFTS, []),
                    ): _care_shifts_selector(),
                    vol.Optional(
                        CONF_CHECKLIST_ITEMS,
                        default=operations_defaults.get(CONF_CHECKLIST_ITEMS, []),
                    ): _checklist_items_selector(),
                    vol.Optional(
                        CONF_APPROVAL_REQUIRED_ACTIONS,
                        default=operations_defaults.get(CONF_APPROVAL_REQUIRED_ACTIONS, []),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[SelectOptionDict(value=item, label=item) for item in APPROVAL_ACTION_OPTIONS],
                            multiple=True,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            {"collapsed": True},
        ),
        vol.Optional(CAMERA_SECTION): section(
            vol.Schema(
                {
                    _optional_entity_field(CONF_CAMERA_ENTITY_ID, camera_defaults.get(CONF_CAMERA_ENTITY_ID)): EntitySelector(
                        EntitySelectorConfig(domain="camera")
                    ),
                    vol.Optional(
                        CONF_FOOD_BOWL_AREA,
                        default=camera_defaults.get(CONF_FOOD_BOWL_AREA, ""),
                    ): TextSelector(),
                    vol.Optional(
                        CONF_WATER_BOWL_AREA,
                        default=camera_defaults.get(CONF_WATER_BOWL_AREA, ""),
                    ): TextSelector(),
                }
            ),
            {"collapsed": True},
        ),
    }


def _optional_entity_field(name: str, default: Any) -> vol.Optional:
    if default:
        return vol.Optional(name, default=default)
    return vol.Optional(name)


def _optional_number_field(name: str, default: Any) -> vol.Optional:
    if default not in (None, ""):
        return vol.Optional(name, default=default)
    return vol.Optional(name)


def _validate_pet_input(
    user_input: dict[str, Any],
    *,
    existing_pet_ids: set[str] | None = None,
    editing_pet_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Validate and normalize a pet profile form submission."""
    cleaned = dict(user_input)
    camera_settings = cleaned.pop(CAMERA_SECTION, {}) or {}
    medical_settings = cleaned.pop(MEDICAL_SECTION, {}) or {}
    routine_settings = cleaned.pop(ROUTINE_SECTION, {}) or {}
    calendar_settings = cleaned.pop(CALENDAR_SECTION, {}) or {}
    nutrition_settings = cleaned.pop(NUTRITION_SECTION, {}) or {}
    operations_settings = cleaned.pop(OPERATIONS_SECTION, {}) or {}
    passport_settings = cleaned.pop(PASSPORT_SECTION, {}) or {}
    tracking_settings = cleaned.pop(TRACKING_SECTION, {}) or {}
    behavior_settings = cleaned.pop(BEHAVIOR_SECTION, {}) or {}

    cleaned[CONF_AVATAR] = normalize_avatar_reference(cleaned.get(CONF_AVATAR))
    cleaned[CONF_CAMERA_ENTITY_ID] = camera_settings.get(CONF_CAMERA_ENTITY_ID) or None
    cleaned[CONF_FOOD_BOWL_AREA] = camera_settings.get(CONF_FOOD_BOWL_AREA) or None
    cleaned[CONF_WATER_BOWL_AREA] = camera_settings.get(CONF_WATER_BOWL_AREA) or None
    cleaned[CONF_FEEDING_ROUTINES] = list(routine_settings.get(CONF_FEEDING_ROUTINES, []) or [])
    cleaned[CONF_WALK_ROUTINES] = list(routine_settings.get(CONF_WALK_ROUTINES, []) or [])
    cleaned[CONF_CARE_ROUTINES] = list(routine_settings.get(CONF_CARE_ROUTINES, []) or [])
    cleaned[CONF_ROUTINE_EXCEPTIONS] = list(routine_settings.get(CONF_ROUTINE_EXCEPTIONS, []) or [])
    cleaned[CONF_DEFAULT_MANUAL_MODE] = str(
        routine_settings.get(CONF_DEFAULT_MANUAL_MODE, OPERATION_MODES[0]) or OPERATION_MODES[0]
    )
    cleaned[CONF_WEATHER_ADAPTATION] = bool(routine_settings.get(CONF_WEATHER_ADAPTATION, True))
    cleaned[CONF_HEAT_THRESHOLD_C] = float(routine_settings.get(CONF_HEAT_THRESHOLD_C, DEFAULT_HEAT_THRESHOLD_C))
    cleaned[CONF_COLD_THRESHOLD_C] = float(routine_settings.get(CONF_COLD_THRESHOLD_C, DEFAULT_COLD_THRESHOLD_C))
    cleaned[CONF_FEEDING_SCHEDULE] = ""
    cleaned[CONF_WALK_SCHEDULE] = ""
    cleaned[CONF_CARE_SCHEDULE] = ""
    cleaned[CONF_VET_APPOINTMENTS] = _normalize_text(calendar_settings.get(CONF_VET_APPOINTMENTS))
    cleaned[CONF_CALENDAR_LINKS] = list(calendar_settings.get(CONF_CALENDAR_LINKS, []) or [])
    cleaned[CONF_EXTERNAL_CALENDAR_ENTITY_IDS] = [
        str(item.get(CONF_CALENDAR_ENTITY_ID, "")).strip()
        for item in cleaned[CONF_CALENDAR_LINKS]
        if isinstance(item, dict) and str(item.get(CONF_CALENDAR_ENTITY_ID, "")).strip()
    ]
    cleaned[CONF_FOOD_CATALOG] = list(nutrition_settings.get(CONF_FOOD_CATALOG, []) or [])
    cleaned[CONF_FOOD_TRANSITION_PLAN] = list(nutrition_settings.get(CONF_FOOD_TRANSITION_PLAN, []) or [])
    cleaned[CONF_MEDICAL_COUNTRY] = _normalize_text(medical_settings.get(CONF_MEDICAL_COUNTRY)) or DEFAULT_MEDICAL_COUNTRY
    cleaned[CONF_MEDICAL_REGION] = _normalize_text(medical_settings.get(CONF_MEDICAL_REGION)) or DEFAULT_MEDICAL_REGION
    cleaned[CONF_REGIONAL_POLICY] = (
        _normalize_text(medical_settings.get(CONF_REGIONAL_POLICY))
        or cleaned[CONF_MEDICAL_REGION]
    )
    cleaned[CONF_VACCINE_PROFILE] = str(medical_settings.get(CONF_VACCINE_PROFILE, VACCINE_PROFILE_OPTIONS[0]) or VACCINE_PROFILE_OPTIONS[0])
    cleaned[CONF_VET_OVERRIDE] = bool(medical_settings.get(CONF_VET_OVERRIDE, True))
    cleaned[CONF_BODY_CONDITION_SCORE] = float(
        medical_settings.get(CONF_BODY_CONDITION_SCORE, DEFAULT_BODY_CONDITION_SCORE)
    )
    cleaned[CONF_WEIGHT_GOAL_MIN_KG] = medical_settings.get(CONF_WEIGHT_GOAL_MIN_KG) or None
    cleaned[CONF_WEIGHT_GOAL_MAX_KG] = medical_settings.get(CONF_WEIGHT_GOAL_MAX_KG) or None
    cleaned[CONF_MEDICATION_COURSES] = list(medical_settings.get(CONF_MEDICATION_COURSES, []) or [])
    cleaned[CONF_CHRONIC_CONDITIONS] = list(medical_settings.get(CONF_CHRONIC_CONDITIONS, []) or [])
    cleaned[CONF_DIAGNOSES] = list(medical_settings.get(CONF_DIAGNOSES, []) or [])
    cleaned[CONF_ALLERGIES] = list(medical_settings.get(CONF_ALLERGIES, []) or [])
    cleaned[CONF_CONTRAINDICATIONS] = list(medical_settings.get(CONF_CONTRAINDICATIONS, []) or [])
    cleaned[CONF_MEDICAL_HISTORY] = list(medical_settings.get(CONF_MEDICAL_HISTORY, []) or [])
    cleaned[CONF_VACCINE_OVERRIDES] = list(medical_settings.get(CONF_VACCINE_OVERRIDES, []) or [])
    cleaned[CONF_CARE_ROLES] = list(operations_settings.get(CONF_CARE_ROLES, []) or [])
    cleaned[CONF_CARE_SHIFTS] = list(operations_settings.get(CONF_CARE_SHIFTS, []) or [])
    cleaned[CONF_CHECKLIST_ITEMS] = list(operations_settings.get(CONF_CHECKLIST_ITEMS, []) or [])
    cleaned[CONF_APPROVAL_REQUIRED_ACTIONS] = list(operations_settings.get(CONF_APPROVAL_REQUIRED_ACTIONS, []) or [])
    cleaned[CONF_PASSPORT_NUMBER] = _normalize_text(passport_settings.get(CONF_PASSPORT_NUMBER)) or None
    cleaned[CONF_MICROCHIP_ID] = _normalize_text(passport_settings.get(CONF_MICROCHIP_ID)) or None
    cleaned[CONF_INSURANCE_POLICY] = _normalize_text(passport_settings.get(CONF_INSURANCE_POLICY)) or None
    cleaned[CONF_PRIMARY_VET] = _normalize_text(passport_settings.get(CONF_PRIMARY_VET)) or None
    cleaned[CONF_VET_PHONE] = _normalize_text(passport_settings.get(CONF_VET_PHONE)) or None
    cleaned[CONF_GPS_TRACKER_ENTITY_ID] = tracking_settings.get(CONF_GPS_TRACKER_ENTITY_ID) or None
    cleaned[CONF_BLE_TRACKER_ENTITY_ID] = tracking_settings.get(CONF_BLE_TRACKER_ENTITY_ID) or None
    cleaned[CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS] = list(tracking_settings.get(CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS, []) or [])
    cleaned[CONF_SAFE_ZONES] = list(tracking_settings.get(CONF_SAFE_ZONES, []) or [])
    cleaned[CONF_ROOM_PRESENCE_SOURCES] = list(tracking_settings.get(CONF_ROOM_PRESENCE_SOURCES, []) or [])
    cleaned[CONF_CAMERA_ROOM_NAME] = _normalize_text(tracking_settings.get(CONF_CAMERA_ROOM_NAME)) or None
    cleaned[CONF_WEATHER_ENTITY_ID] = tracking_settings.get(CONF_WEATHER_ENTITY_ID) or None
    cleaned[CONF_BEHAVIOR_SIGNAL_ENTITY_IDS] = list(behavior_settings.get(CONF_BEHAVIOR_SIGNAL_ENTITY_IDS, []) or [])
    cleaned[CONF_CAREGIVERS] = _normalize_text(behavior_settings.get(CONF_CAREGIVERS))
    errors: dict[str, str] = {}

    if float(cleaned[CONF_WEIGHT]) <= 0:
        errors[CONF_WEIGHT] = "invalid_weight"
    if not 1.0 <= cleaned[CONF_BODY_CONDITION_SCORE] <= 9.0:
        errors[CONF_BODY_CONDITION_SCORE] = "invalid_body_condition_score"
    if (
        cleaned[CONF_WEIGHT_GOAL_MIN_KG] is not None
        and cleaned[CONF_WEIGHT_GOAL_MAX_KG] is not None
        and float(cleaned[CONF_WEIGHT_GOAL_MIN_KG]) > float(cleaned[CONF_WEIGHT_GOAL_MAX_KG])
    ):
        errors[CONF_WEIGHT_GOAL_MIN_KG] = "invalid_weight_goal"
    if cleaned[CONF_DEFAULT_MANUAL_MODE] not in OPERATION_MODES:
        errors[CONF_DEFAULT_MANUAL_MODE] = "invalid_mode"
    if cleaned[CONF_COLD_THRESHOLD_C] >= cleaned[CONF_HEAT_THRESHOLD_C]:
        errors[CONF_COLD_THRESHOLD_C] = "invalid_temperature_window"

    for key in (CONF_FOOD_BOWL_AREA, CONF_WATER_BOWL_AREA):
        try:
            BowlArea.from_value(cleaned.get(key))
        except ValueError:
            errors[key] = "invalid_bowl_area"

    if any(cleaned.get(key) for key in (CONF_FOOD_BOWL_AREA, CONF_WATER_BOWL_AREA)) and not cleaned.get(CONF_CAMERA_ENTITY_ID):
        errors[CONF_CAMERA_ENTITY_ID] = "camera_required"

    schedule_validators = {
        CONF_FEEDING_ROUTINES: lambda value: parse_feeding_schedule(value, pet_id="preview") if value else (),
        CONF_WALK_ROUTINES: lambda value: parse_walk_schedule(value, pet_id="preview") if value else (),
        CONF_CARE_ROUTINES: lambda value: parse_care_schedule(value, pet_id="preview") if value else (),
        CONF_ROUTINE_EXCEPTIONS: lambda value: parse_schedule_exceptions(value, pet_id="preview") if value else (),
        CONF_VET_APPOINTMENTS: lambda value: parse_vet_appointments(value, pet_id="preview") if value else (),
        CONF_CALENDAR_LINKS: lambda value: parse_calendar_links(value) if value else (),
        CONF_FOOD_CATALOG: lambda value: parse_food_catalog(value) if value else (),
        CONF_FOOD_TRANSITION_PLAN: lambda value: parse_food_transition_plan(value) if value else (),
        CONF_MEDICATION_COURSES: lambda value: parse_medication_courses(value) if value else (),
        CONF_CHRONIC_CONDITIONS: lambda value: parse_chronic_conditions(value) if value else (),
        CONF_VACCINE_OVERRIDES: lambda value: parse_vaccine_overrides(value) if value else (),
        CONF_CARE_ROLES: lambda value: parse_care_roles(value) if value else (),
        CONF_CARE_SHIFTS: lambda value: parse_care_shifts(value, pet_id="preview") if value else (),
        CONF_CHECKLIST_ITEMS: lambda value: parse_checklist_items(value, pet_id="preview") if value else (),
        CONF_APPROVAL_REQUIRED_ACTIONS: lambda value: parse_approval_required_actions(value) if value else (),
        CONF_SAFE_ZONES: lambda value: parse_safe_zones(value) if value else (),
        CONF_ROOM_PRESENCE_SOURCES: lambda value: parse_room_presence_sources(value) if value else (),
    }
    for field, validator in schedule_validators.items():
        try:
            validator(cleaned.get(field))
        except ValueError:
            errors[field] = "invalid_schedule"

    if not errors.get(CONF_FOOD_TRANSITION_PLAN):
        catalog_names = {str(item.get(CONF_FOOD_NAME, "")).strip() for item in cleaned.get(CONF_FOOD_CATALOG, []) if item}
        for step in cleaned.get(CONF_FOOD_TRANSITION_PLAN, []):
            if not step:
                continue
            from_food = str(step.get(CONF_FROM_FOOD_NAME, "")).strip()
            to_food = str(step.get(CONF_TO_FOOD_NAME, "")).strip()
            if catalog_names and (from_food not in catalog_names or to_food not in catalog_names):
                errors[CONF_FOOD_TRANSITION_PLAN] = "invalid_schedule"
                break

    generated_pet_id = editing_pet_id or generate_pet_id(
        f"{cleaned[CONF_NAME]}_{cleaned[CONF_BIRTHDATE]}_{cleaned[CONF_SPECIES]}"
    )
    existing_pet_ids = existing_pet_ids or set()
    if generated_pet_id in existing_pet_ids and generated_pet_id != editing_pet_id:
        errors[CONF_NAME] = "duplicate_pet"

    cleaned[CONF_WEIGHT] = float(cleaned[CONF_WEIGHT])
    if cleaned[CONF_WEIGHT_GOAL_MIN_KG] is not None:
        cleaned[CONF_WEIGHT_GOAL_MIN_KG] = float(cleaned[CONF_WEIGHT_GOAL_MIN_KG])
    if cleaned[CONF_WEIGHT_GOAL_MAX_KG] is not None:
        cleaned[CONF_WEIGHT_GOAL_MAX_KG] = float(cleaned[CONF_WEIGHT_GOAL_MAX_KG])
    cleaned[CONF_PET_ID] = generated_pet_id
    return cleaned, errors


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _entry_settings(entry: ConfigEntry) -> dict[str, Any]:
    """Return merged hub settings from a config entry."""
    if entry.options.get(CONF_PETS):
        return {
            CONF_HUB_NAME: entry.options.get(CONF_HUB_NAME, entry.title or DEFAULT_HUB_NAME),
            CONF_PET_SCHEMA: int(entry.options.get(CONF_PET_SCHEMA, entry.data.get(CONF_PET_SCHEMA, 0)) or 0),
            CONF_SHOW_EDITOR_IN_SIDEBAR: entry.options.get(
                CONF_SHOW_EDITOR_IN_SIDEBAR,
                entry.data.get(CONF_SHOW_EDITOR_IN_SIDEBAR, DEFAULT_SHOW_EDITOR_IN_SIDEBAR),
            ),
            CONF_PETS: [normalize_pet_config_record(dict(pet)) for pet in entry.options.get(CONF_PETS, [])],
        }
    if CONF_PETS in entry.data:
        return {
            CONF_HUB_NAME: entry.data.get(CONF_HUB_NAME, entry.title or DEFAULT_HUB_NAME),
            CONF_PET_SCHEMA: int(entry.data.get(CONF_PET_SCHEMA, 0) or 0),
            CONF_SHOW_EDITOR_IN_SIDEBAR: entry.data.get(
                CONF_SHOW_EDITOR_IN_SIDEBAR,
                DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
            ),
            CONF_PETS: [normalize_pet_config_record(dict(pet)) for pet in entry.data.get(CONF_PETS, [])],
        }

    legacy_pet = dict(entry.data)
    legacy_pet.setdefault(
        CONF_PET_ID,
        generate_pet_id(
            f"{legacy_pet.get(CONF_NAME, 'pet')}_{legacy_pet.get(CONF_BIRTHDATE, '')}_{legacy_pet.get(CONF_SPECIES, '')}"
        ),
    )
    return {
        CONF_HUB_NAME: entry.title or DEFAULT_HUB_NAME,
        CONF_PET_SCHEMA: 0,
        CONF_SHOW_EDITOR_IN_SIDEBAR: entry.data.get(
            CONF_SHOW_EDITOR_IN_SIDEBAR,
            DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
        ),
        CONF_PETS: [legacy_pet],
    }


def _pet_defaults_for_form(pet: dict[str, Any]) -> dict[str, Any]:
    """Build form defaults for editing an existing pet."""
    pet = normalize_pet_config_record(pet)
    pet_id = str(pet.get(CONF_PET_ID, "preview"))
    profile = {
        **pet,
        CONF_FEEDING_ROUTINES: pet.get(CONF_FEEDING_ROUTINES)
        or [routine.as_dict() for routine in parse_feeding_schedule(pet.get(CONF_FEEDING_SCHEDULE), pet_id=pet_id)],
        CONF_WALK_ROUTINES: pet.get(CONF_WALK_ROUTINES)
        or [routine.as_dict() for routine in parse_walk_schedule(pet.get(CONF_WALK_SCHEDULE), pet_id=pet_id)],
        CONF_CARE_ROUTINES: pet.get(CONF_CARE_ROUTINES)
        or [routine.as_dict() for routine in parse_care_schedule(pet.get(CONF_CARE_SCHEDULE), pet_id=pet_id)],
        CONF_ROUTINE_EXCEPTIONS: pet.get(CONF_ROUTINE_EXCEPTIONS, []),
    }
    return {
        **profile,
        ROUTINE_SECTION: {
            CONF_FEEDING_ROUTINES: profile.get(CONF_FEEDING_ROUTINES, []),
            CONF_WALK_ROUTINES: profile.get(CONF_WALK_ROUTINES, []),
            CONF_CARE_ROUTINES: profile.get(CONF_CARE_ROUTINES, []),
            CONF_ROUTINE_EXCEPTIONS: profile.get(CONF_ROUTINE_EXCEPTIONS, []),
            CONF_DEFAULT_MANUAL_MODE: pet.get(CONF_DEFAULT_MANUAL_MODE, OPERATION_MODES[0]),
            CONF_WEATHER_ADAPTATION: pet.get(CONF_WEATHER_ADAPTATION, True),
            CONF_HEAT_THRESHOLD_C: pet.get(CONF_HEAT_THRESHOLD_C, DEFAULT_HEAT_THRESHOLD_C),
            CONF_COLD_THRESHOLD_C: pet.get(CONF_COLD_THRESHOLD_C, DEFAULT_COLD_THRESHOLD_C),
        },
        CALENDAR_SECTION: {
            CONF_VET_APPOINTMENTS: pet.get(CONF_VET_APPOINTMENTS, ""),
            CONF_CALENDAR_LINKS: pet.get(CONF_CALENDAR_LINKS)
            or [
                {
                    CONF_CALENDAR_ENTITY_ID: entity_id,
                    CONF_SOURCE_OF_TRUTH: "diva",
                }
                for entity_id in pet.get(CONF_EXTERNAL_CALENDAR_ENTITY_IDS, [])
            ],
        },
        NUTRITION_SECTION: {
            CONF_FOOD_CATALOG: pet.get(CONF_FOOD_CATALOG, []),
            CONF_FOOD_TRANSITION_PLAN: pet.get(CONF_FOOD_TRANSITION_PLAN, []),
        },
        MEDICAL_SECTION: {
            CONF_MEDICAL_COUNTRY: pet.get(CONF_MEDICAL_COUNTRY, DEFAULT_MEDICAL_COUNTRY),
            CONF_MEDICAL_REGION: pet.get(CONF_MEDICAL_REGION, DEFAULT_MEDICAL_REGION),
            CONF_BODY_CONDITION_SCORE: pet.get(CONF_BODY_CONDITION_SCORE, DEFAULT_BODY_CONDITION_SCORE),
            CONF_WEIGHT_GOAL_MIN_KG: pet.get(CONF_WEIGHT_GOAL_MIN_KG, ""),
            CONF_WEIGHT_GOAL_MAX_KG: pet.get(CONF_WEIGHT_GOAL_MAX_KG, ""),
            CONF_MEDICATION_COURSES: pet.get(CONF_MEDICATION_COURSES, []),
            CONF_CHRONIC_CONDITIONS: pet.get(CONF_CHRONIC_CONDITIONS, []),
            CONF_VACCINE_OVERRIDES: pet.get(CONF_VACCINE_OVERRIDES, []),
        },
        PASSPORT_SECTION: {
            CONF_PASSPORT_NUMBER: pet.get(CONF_PASSPORT_NUMBER, ""),
            CONF_MICROCHIP_ID: pet.get(CONF_MICROCHIP_ID, ""),
            CONF_INSURANCE_POLICY: pet.get(CONF_INSURANCE_POLICY, ""),
            CONF_PRIMARY_VET: pet.get(CONF_PRIMARY_VET, ""),
            CONF_VET_PHONE: pet.get(CONF_VET_PHONE, ""),
        },
        TRACKING_SECTION: {
            CONF_GPS_TRACKER_ENTITY_ID: pet.get(CONF_GPS_TRACKER_ENTITY_ID, ""),
            CONF_BLE_TRACKER_ENTITY_ID: pet.get(CONF_BLE_TRACKER_ENTITY_ID, ""),
            CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS: pet.get(CONF_HOUSEHOLD_PRESENCE_ENTITY_IDS, []),
            CONF_SAFE_ZONES: pet.get(CONF_SAFE_ZONES, []),
            CONF_ROOM_PRESENCE_SOURCES: pet.get(CONF_ROOM_PRESENCE_SOURCES, []),
            CONF_CAMERA_ROOM_NAME: pet.get(CONF_CAMERA_ROOM_NAME, ""),
            CONF_WEATHER_ENTITY_ID: pet.get(CONF_WEATHER_ENTITY_ID, ""),
        },
        BEHAVIOR_SECTION: {
            CONF_BEHAVIOR_SIGNAL_ENTITY_IDS: pet.get(CONF_BEHAVIOR_SIGNAL_ENTITY_IDS, []),
            CONF_CAREGIVERS: pet.get(CONF_CAREGIVERS, ""),
        },
        OPERATIONS_SECTION: {
            CONF_CARE_ROLES: pet.get(CONF_CARE_ROLES, []),
            CONF_CARE_SHIFTS: pet.get(CONF_CARE_SHIFTS, []),
            CONF_CHECKLIST_ITEMS: pet.get(CONF_CHECKLIST_ITEMS, []),
            CONF_APPROVAL_REQUIRED_ACTIONS: pet.get(CONF_APPROVAL_REQUIRED_ACTIONS, []),
        },
        CAMERA_SECTION: {
            CONF_CAMERA_ENTITY_ID: pet.get(CONF_CAMERA_ENTITY_ID, ""),
            CONF_FOOD_BOWL_AREA: pet.get(CONF_FOOD_BOWL_AREA, ""),
            CONF_WATER_BOWL_AREA: pet.get(CONF_WATER_BOWL_AREA, ""),
        },
    }


def _find_pet(pets: list[dict[str, Any]], pet_id: str | None) -> dict[str, Any] | None:
    """Return a pet dict by pet_id."""
    if pet_id is None:
        return None
    for pet in pets:
        if pet.get(CONF_PET_ID) == pet_id:
            return pet
    return None


def _pet_options(pets: list[dict[str, Any]]) -> list[SelectOptionDict]:
    """Build pet selector options."""
    return [
        SelectOptionDict(
            value=pet[CONF_PET_ID],
            label=f"{pet[CONF_NAME]} ({pet[CONF_SPECIES]})",
        )
        for pet in pets
    ]

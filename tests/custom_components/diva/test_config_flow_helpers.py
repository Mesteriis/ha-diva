from __future__ import annotations

from custom_components.diva.config_flow import (
    MEDICAL_SECTION,
    _build_pet_schema_fields,
    _pet_defaults_for_form,
    _validate_pet_input,
)
from custom_components.diva.const import (
    CONF_ALLERGEN,
    CONF_ALLERGIES,
    CONF_BIRTHDATE,
    CONF_BODY_CONDITION_SCORE,
    CONF_BREED,
    CONF_CHRONIC_CONDITIONS,
    CONF_CONDITION_NAME,
    CONF_CONDITION_STATUS,
    CONF_CONTRAINDICATION,
    CONF_CONTRAINDICATIONS,
    CONF_DIAGNOSED_ON,
    CONF_DIAGNOSES,
    CONF_DIAGNOSIS_NAME,
    CONF_DIAGNOSIS_STATUS,
    CONF_DIET_MODE,
    CONF_DUE_DATE,
    CONF_END_DATE,
    CONF_HISTORY_CATEGORY,
    CONF_HISTORY_DATE,
    CONF_HISTORY_TITLE,
    CONF_MEDICAL_COUNTRY,
    CONF_MEDICAL_HISTORY,
    CONF_MEDICAL_REGION,
    CONF_MEDICATION_COURSES,
    CONF_MEDICATION_NAME,
    CONF_MEDICATION_TIMES,
    CONF_MONITOR_INTERVAL_DAYS,
    CONF_NAME,
    CONF_NOTES,
    CONF_REASON,
    CONF_REACTION,
    CONF_RECURRENCE_MONTHS,
    CONF_REGIONAL_POLICY,
    CONF_ROUTINE_CATEGORY,
    CONF_SOURCE_OF_TRUTH,
    CONF_SPECIES,
    CONF_START_DATE,
    CONF_VACCINE_DOSE_ID,
    CONF_VACCINE_NAME,
    CONF_VACCINE_OVERRIDES,
    CONF_VACCINE_PROFILE,
    CONF_VET_OVERRIDE,
    CONF_WEIGHT,
    CONF_WEIGHT_GOAL_MAX_KG,
    CONF_WEIGHT_GOAL_MIN_KG,
    VACCINE_PROFILE_OPTIONS,
)


def _medical_settings() -> dict[str, object]:
    return {
        CONF_MEDICAL_COUNTRY: "es",
        CONF_MEDICAL_REGION: "madrid",
        CONF_REGIONAL_POLICY: "es_madrid",
        CONF_VACCINE_PROFILE: VACCINE_PROFILE_OPTIONS[0],
        CONF_VET_OVERRIDE: False,
        CONF_BODY_CONDITION_SCORE: 5.5,
        CONF_WEIGHT_GOAL_MIN_KG: 22.0,
        CONF_WEIGHT_GOAL_MAX_KG: 24.5,
        CONF_MEDICATION_COURSES: [
            {
                CONF_MEDICATION_NAME: "Carprofen",
                CONF_MEDICATION_TIMES: ["08:00"],
                CONF_START_DATE: "2026-03-01",
                CONF_END_DATE: "2026-03-10",
                CONF_NOTES: "After breakfast",
            }
        ],
        CONF_CHRONIC_CONDITIONS: [
            {
                CONF_CONDITION_NAME: "Arthritis",
                CONF_CONDITION_STATUS: "monitoring",
                CONF_MONITOR_INTERVAL_DAYS: 21,
                CONF_NOTES: "Rear leg stiffness",
            }
        ],
        CONF_DIAGNOSES: [
            {
                CONF_DIAGNOSIS_NAME: "Hip dysplasia",
                CONF_DIAGNOSIS_STATUS: "active",
                CONF_DIAGNOSED_ON: "2025-06-15",
                CONF_NOTES: "Confirmed by x-ray",
            }
        ],
        CONF_ALLERGIES: [
            {
                CONF_ALLERGEN: "Chicken",
                CONF_REACTION: "itching",
                CONF_NOTES: "Avoid treats",
            }
        ],
        CONF_CONTRAINDICATIONS: [
            {
                CONF_CONTRAINDICATION: "NSAIDs",
                CONF_REASON: "GI sensitivity",
                CONF_NOTES: "Use alternatives",
            }
        ],
        CONF_MEDICAL_HISTORY: [
            {
                CONF_HISTORY_DATE: "2024-09-01",
                CONF_HISTORY_TITLE: "ACL surgery",
                CONF_HISTORY_CATEGORY: "surgery",
                CONF_NOTES: "Recovered well",
            }
        ],
        CONF_VACCINE_OVERRIDES: [
            {
                CONF_VACCINE_DOSE_ID: "rabies_booster",
                CONF_VACCINE_NAME: "Rabies",
                CONF_DUE_DATE: "2026-09-01",
                CONF_ROUTINE_CATEGORY: "core",
                CONF_SOURCE_OF_TRUTH: "manual_override",
                CONF_RECURRENCE_MONTHS: 12,
                CONF_NOTES: "Annual booster",
            }
        ],
    }


def _pet_form_input() -> dict[str, object]:
    return {
        CONF_NAME: "Rex",
        CONF_SPECIES: "dog",
        CONF_BREED: "Labrador Retriever",
        CONF_BIRTHDATE: "2020-02-14",
        CONF_WEIGHT: 23.4,
        CONF_DIET_MODE: "adult",
        MEDICAL_SECTION: _medical_settings(),
    }


def _section_default(schema_fields: dict[object, object], section_name: str, field_name: str):
    for marker, field in schema_fields.items():
        if getattr(marker, "schema", None) != section_name:
            continue
        nested_schema = field["schema"].schema
        for nested_marker in nested_schema:
            if getattr(nested_marker, "schema", None) == field_name:
                return nested_marker.default()
    raise AssertionError(f"missing {section_name}.{field_name}")


def test_validate_pet_input_flattens_medical_section_fields() -> None:
    cleaned, errors = _validate_pet_input(_pet_form_input())

    assert errors == {}
    assert cleaned[CONF_REGIONAL_POLICY] == "es_madrid"
    assert cleaned[CONF_VACCINE_PROFILE] == VACCINE_PROFILE_OPTIONS[0]
    assert cleaned[CONF_VET_OVERRIDE] is False
    assert cleaned[CONF_DIAGNOSES] == _medical_settings()[CONF_DIAGNOSES]
    assert cleaned[CONF_ALLERGIES] == _medical_settings()[CONF_ALLERGIES]
    assert cleaned[CONF_CONTRAINDICATIONS] == _medical_settings()[CONF_CONTRAINDICATIONS]
    assert cleaned[CONF_MEDICAL_HISTORY] == _medical_settings()[CONF_MEDICAL_HISTORY]


def test_pet_defaults_for_form_preserves_medical_edit_values() -> None:
    cleaned, errors = _validate_pet_input(_pet_form_input())
    assert errors == {}

    defaults = _pet_defaults_for_form(cleaned)
    medical_defaults = defaults[MEDICAL_SECTION]

    assert medical_defaults[CONF_MEDICAL_COUNTRY] == "ES"
    assert medical_defaults[CONF_MEDICAL_REGION] == "madrid"
    assert medical_defaults[CONF_REGIONAL_POLICY] == "es_madrid"
    assert medical_defaults[CONF_VACCINE_PROFILE] == VACCINE_PROFILE_OPTIONS[0]
    assert medical_defaults[CONF_VET_OVERRIDE] is False
    assert medical_defaults[CONF_DIAGNOSES] == _medical_settings()[CONF_DIAGNOSES]
    assert medical_defaults[CONF_ALLERGIES] == _medical_settings()[CONF_ALLERGIES]
    assert medical_defaults[CONF_CONTRAINDICATIONS] == _medical_settings()[CONF_CONTRAINDICATIONS]
    assert medical_defaults[CONF_MEDICAL_HISTORY] == _medical_settings()[CONF_MEDICAL_HISTORY]


def test_build_pet_schema_fields_uses_medical_defaults_for_edit_flow() -> None:
    cleaned, errors = _validate_pet_input(_pet_form_input())
    assert errors == {}

    defaults = _pet_defaults_for_form(cleaned)
    schema_fields = _build_pet_schema_fields(defaults)

    assert _section_default(schema_fields, MEDICAL_SECTION, CONF_REGIONAL_POLICY) == "es_madrid"
    assert _section_default(schema_fields, MEDICAL_SECTION, CONF_VACCINE_PROFILE) == VACCINE_PROFILE_OPTIONS[0]
    assert _section_default(schema_fields, MEDICAL_SECTION, CONF_VET_OVERRIDE) is False
    assert _section_default(schema_fields, MEDICAL_SECTION, CONF_DIAGNOSES) == _medical_settings()[CONF_DIAGNOSES]
    assert _section_default(schema_fields, MEDICAL_SECTION, CONF_ALLERGIES) == _medical_settings()[CONF_ALLERGIES]
    assert _section_default(schema_fields, MEDICAL_SECTION, CONF_CONTRAINDICATIONS) == _medical_settings()[CONF_CONTRAINDICATIONS]
    assert _section_default(schema_fields, MEDICAL_SECTION, CONF_MEDICAL_HISTORY) == _medical_settings()[CONF_MEDICAL_HISTORY]

from datetime import date, datetime, timezone

from custom_components.diva.pet import (
    PetContext,
    PetEngine,
    PetProfile,
    normalize_pet_config_record,
    serialize_diva_entry_settings_v3,
    serialize_pet_config_record_v3,
)


UTC = timezone.utc


def _profile() -> PetProfile:
    return PetProfile(
        pet_id="schema_pet",
        name="Schema Pet",
        species="dog",
        breed="English Cocker Spaniel",
        birthdate=date(2021, 5, 1),
        weight_kg=11.2,
        diet_mode="adult",
        weather_adaptation=True,
        medical_country="ES",
        medical_region="es_general",
        regional_policy="madrid",
        vaccine_profile="spain_dog_default",
        vet_override=True,
    )


def test_v3_pet_record_roundtrip() -> None:
    profile = _profile()

    payload = serialize_pet_config_record_v3(profile.as_dict())
    normalized = normalize_pet_config_record(payload)

    assert payload["pet_schema"] == 3
    assert set(payload) == {"pet_schema", "profile", "plan", "medical", "analytics", "external_links"}
    assert normalized["pet_id"] == profile.pet_id
    assert normalized["name"] == profile.name
    assert normalized["regional_policy"] == "madrid"
    assert normalized["vaccine_profile"] == "spain_dog_default"


def test_v3_entry_settings_serializer() -> None:
    profile = _profile()

    payload = serialize_diva_entry_settings_v3(
        hub_name="DIVA Pet Guardian",
        show_editor_in_sidebar=False,
        pets=[profile.as_dict()],
    )

    assert payload["hub_name"] == "DIVA Pet Guardian"
    assert payload["show_editor_in_sidebar"] is False
    assert payload["pet_schema"] == 3
    assert payload["pets"][0]["profile"]["pet_id"] == profile.pet_id


def test_sub_engines_expose_runtime_boundaries() -> None:
    engine = PetEngine(_profile())
    now = datetime(2026, 3, 9, 10, 0, tzinfo=UTC)

    snapshot, _ = engine.refresh(now, PetContext())

    assert engine.nutrition.recommended_portion_grams() == snapshot.recommended_food_portion_grams
    assert engine.medical.vaccine_status(now) == snapshot.vaccine_status
    assert engine.mobility.walk_distance_today_km(now) == snapshot.walk_distance_today_km
    assert engine.behavior.sleep_quality_score(now) == snapshot.sleep_quality_score

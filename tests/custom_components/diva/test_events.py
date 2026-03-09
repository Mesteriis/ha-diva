from custom_components.diva.events import build_notice_payload, notice_event_type
from custom_components.diva.pet import PetNotice, PetProfile


def test_event_payload_builder() -> None:
    profile = PetProfile.from_dict(
        {
            "pet_id": "don_abrikos_a1b2c3",
            "name": "Don Abrikos",
            "species": "dog",
            "breed": "Poodle",
            "birthdate": "2020-01-01",
            "weight": 8.2,
            "diet_mode": "adult",
        }
    )
    notice = PetNotice(category="event", name="food_eaten", timestamp="2026-03-08T10:00:00+00:00")
    payload = build_notice_payload(profile, notice)

    assert notice_event_type(notice) == "diva_event"
    assert payload["pet"] == profile.pet_id
    assert payload["event"] == "food_eaten"

import asyncio
import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from custom_components.diva.const import CONF_PETS, RUNTIME_JSON_FILENAME
from custom_components.diva.coordinator import DivaCoordinator, ManagedPet
from custom_components.diva.pet import PetEngine, PetProfile
from custom_components.diva.storage import DivaJSONStorage


class FakeConfig:
    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path

    def path(self, *parts: str) -> str:
        return str(self._base_path.joinpath(*parts))


class FakeHass:
    def __init__(self, base_path: Path) -> None:
        self.config = FakeConfig(base_path)
        self.states = SimpleNamespace(get=lambda entity_id: None)

    async def async_add_executor_job(self, func, *args):
        return func(*args)


class FakeLegacyStore:
    def __init__(self, payload) -> None:
        self._payload = payload

    async def async_load(self):
        return self._payload


def _profile() -> PetProfile:
    return PetProfile(
        pet_id="don_abrikos_a1b2c3",
        name="Don Abrikos",
        species="dog",
        breed="English Cocker Spaniel",
        birthdate=date(2020, 1, 1),
        weight_kg=12.4,
        diet_mode="adult",
    )


def _build_coordinator(tmp_path: Path, store_payload=None) -> tuple[DivaCoordinator, PetProfile]:
    profile = _profile()
    coordinator = object.__new__(DivaCoordinator)
    coordinator.hass = FakeHass(tmp_path)
    coordinator.entry = SimpleNamespace(entry_id="entry-1")
    coordinator.hub_name = "Legacy Hub"
    coordinator._runtime_store = DivaJSONStorage(coordinator.hass, RUNTIME_JSON_FILENAME)
    coordinator._store = FakeLegacyStore(store_payload)
    coordinator._pets = {
        profile.pet_id: ManagedPet(
            profile=profile,
            engine=PetEngine(profile),
        )
    }
    coordinator.data = {}
    return coordinator, profile


def test_runtime_json_storage_loads_legacy_single_entry_root(tmp_path) -> None:
    legacy_entry = {
        "hub_name": "Legacy Hub",
        "pets": {
            "don_abrikos_a1b2c3": {
                "food_today_grams": 17.5,
            }
        },
    }
    runtime_path = tmp_path / RUNTIME_JSON_FILENAME
    runtime_path.write_text(json.dumps(legacy_entry), encoding="utf-8")

    storage = DivaJSONStorage(FakeHass(tmp_path), RUNTIME_JSON_FILENAME)
    loaded = asyncio.run(storage.async_load_entry("entry-1"))

    assert loaded == legacy_entry

    payload = json.loads(runtime_path.read_text(encoding="utf-8"))
    assert payload["entries"]["entry-1"] == legacy_entry


def test_coordinator_setup_migrates_legacy_runtime_entry_to_canonical_v3(tmp_path) -> None:
    coordinator, profile = _build_coordinator(tmp_path)
    runtime_path = tmp_path / RUNTIME_JSON_FILENAME
    runtime_path.write_text(
        json.dumps(
            {
                "version": 1,
                "entries": {
                    coordinator.entry.entry_id: {
                        "hub_name": "Legacy Hub",
                        "pet_schema": 3,
                        "storage_backend": "json_root",
                        "pets": {
                            profile.pet_id: {
                                "food_today_grams": 42.0,
                                "current_room": "Kitchen",
                            }
                        },
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    asyncio.run(DivaCoordinator._async_setup(coordinator))

    assert coordinator._pets[profile.pet_id].engine.state.food_today_grams == 42.0
    assert coordinator._pets[profile.pet_id].engine.state.current_room == "Kitchen"

    payload = json.loads(runtime_path.read_text(encoding="utf-8"))
    stored_pet = payload["entries"][coordinator.entry.entry_id]["pets"][profile.pet_id]
    assert stored_pet["runtime"]["food_today_grams"] == 42.0
    assert stored_pet["runtime"]["current_room"] == "Kitchen"
    assert stored_pet["profile"]["pet_schema"] == 3
    assert isinstance(stored_pet["runtime_sections"], dict)
    assert "snapshot" in stored_pet
    assert isinstance(stored_pet["timeline"], list)
    assert stored_pet["camera"]["enabled"] is False


def test_coordinator_setup_imports_legacy_store_into_runtime_json(tmp_path) -> None:
    legacy_profile = _profile()
    coordinator, profile = _build_coordinator(
        tmp_path,
        store_payload={
            CONF_PETS: {
                legacy_profile.pet_id: {
                    "food_today_grams": 9.5,
                    "current_room": "Hall",
                }
            }
        },
    )

    asyncio.run(DivaCoordinator._async_setup(coordinator))

    assert coordinator._pets[profile.pet_id].engine.state.food_today_grams == 9.5
    assert coordinator._pets[profile.pet_id].engine.state.current_room == "Hall"

    payload = json.loads((tmp_path / RUNTIME_JSON_FILENAME).read_text(encoding="utf-8"))
    stored_pet = payload["entries"][coordinator.entry.entry_id]["pets"][profile.pet_id]
    assert stored_pet["runtime"]["food_today_grams"] == 9.5
    assert stored_pet["runtime"]["current_room"] == "Hall"
    assert stored_pet["profile"]["pet_schema"] == 3

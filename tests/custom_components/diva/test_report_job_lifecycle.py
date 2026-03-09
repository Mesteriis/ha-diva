import asyncio
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

import custom_components.diva.coordinator as coordinator_module
from custom_components.diva.coordinator import DivaCoordinator, ManagedPet, _runtime_sections
from custom_components.diva.pet import PetContext, PetEngine, PetProfile


UTC = timezone.utc


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


def _build_coordinator(tmp_path: Path, now: datetime) -> tuple[DivaCoordinator, ManagedPet]:
    profile = _profile()
    engine = PetEngine(profile)
    snapshot, notices = engine.refresh(now, PetContext())
    engine.append_records(notices)

    coordinator = object.__new__(DivaCoordinator)
    coordinator.hass = FakeHass(tmp_path)
    managed = ManagedPet(profile=profile, engine=engine)
    coordinator._pets = {profile.pet_id: managed}
    coordinator.data = {profile.pet_id: snapshot}

    async def _noop_save() -> None:
        return None

    async def _noop_fire(items) -> None:
        return None

    async def _noop_refresh() -> None:
        return None

    coordinator._async_save_runtime_state = _noop_save
    coordinator._async_fire_notices = _noop_fire
    coordinator.async_request_refresh = _noop_refresh
    return coordinator, managed


def test_generate_vet_report_pdf_tracks_completed_job_without_extra_txt(tmp_path, monkeypatch) -> None:
    now = datetime(2026, 3, 9, 10, 0, tzinfo=UTC)
    monkeypatch.setattr(coordinator_module.dt_util, "now", lambda: now)
    coordinator, managed = _build_coordinator(tmp_path, now)

    report_path = asyncio.run(
        DivaCoordinator.async_generate_vet_report(
            coordinator,
            managed.profile.pet_id,
            report_format="pdf",
            history_days=14,
        )
    )

    path = Path(report_path)
    assert path.suffix == ".pdf"
    assert path.exists()
    assert not path.with_suffix(".txt").exists()

    report_job = managed.engine.state.report_jobs[-1]
    generated_report = managed.engine.state.generated_reports[-1]

    assert report_job["status"] == "completed"
    assert report_job["report_kind"] == "vet"
    assert report_job["report_format"] == "pdf"
    assert report_job["history_days"] == 14
    assert report_job["report_path"] == report_path
    assert generated_report["job_id"] == report_job["job_id"]
    assert generated_report["status"] == "completed"
    assert generated_report["report_kind"] == "vet"

    runtime_reports = _runtime_sections(managed.engine.state)["reports"]
    assert runtime_reports["report_jobs"][-1]["job_id"] == report_job["job_id"]


def test_generate_operations_report_records_failed_job(tmp_path, monkeypatch) -> None:
    now = datetime(2026, 3, 9, 10, 30, tzinfo=UTC)
    monkeypatch.setattr(coordinator_module.dt_util, "now", lambda: now)
    coordinator, managed = _build_coordinator(tmp_path, now)

    async def _failing_executor_job(func, *args):
        if func.__name__ == "_write_pdf_report_file":
            raise OSError("disk full")
        return func(*args)

    coordinator.hass.async_add_executor_job = _failing_executor_job

    with pytest.raises(OSError, match="disk full"):
        asyncio.run(
            DivaCoordinator.async_generate_operations_report(
                coordinator,
                managed.profile.pet_id,
                report_format="pdf",
                history_days=7,
            )
        )

    assert managed.engine.state.generated_reports == []
    assert managed.engine.state.report_jobs[-1]["status"] == "failed"
    assert managed.engine.state.report_jobs[-1]["report_kind"] == "operations"
    assert managed.engine.state.report_jobs[-1]["error"] == "disk full"
    assert managed.engine.state.recent_records[-1]["name"] == "operations_report_failed"

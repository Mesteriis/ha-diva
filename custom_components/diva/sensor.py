"""Sensor platform for DIVA."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription

from . import DivaConfigEntry
from .coordinator import DivaCoordinator
from .entity import DivaPetEntity
from .pet import PetRuntimeState, daily_water_target_ml


@dataclass(frozen=True, kw_only=True)
class DivaSensorDescription(SensorEntityDescription):
    """Describe a DIVA sensor entity."""

    value_fn: Callable[[Any], Any]
    attributes_fn: Callable[[DivaCoordinator, str], dict[str, Any]] | None = None


SENSORS: tuple[DivaSensorDescription, ...] = (
    DivaSensorDescription(
        key="food_today",
        translation_key="food_today",
        native_unit_of_measurement="g",
        icon="mdi:food-drumstick",
        value_fn=lambda snapshot: snapshot.food_today_grams,
        attributes_fn=lambda coordinator, pet_id: {
            "food_served_today": coordinator.pets[pet_id].engine.state.food_served_today_grams,
            "food_ignored_today": coordinator.pets[pet_id].engine.state.food_ignored_today_grams,
            "food_served_by_type": dict(coordinator.pets[pet_id].engine.state.food_served_today_by_type),
            "food_eaten_by_type": dict(coordinator.pets[pet_id].engine.state.food_eaten_today_by_type),
            "food_ignored_by_type": dict(coordinator.pets[pet_id].engine.state.food_ignored_today_by_type),
            "food_eaten_by_food": dict(coordinator.pets[pet_id].engine.state.food_today_grams_by_food),
            "active_food_transition": coordinator.get_snapshot(pet_id).active_food_transition,
        },
    ),
    DivaSensorDescription(
        key="calories_consumed_today",
        translation_key="calories_consumed_today",
        native_unit_of_measurement="kcal",
        icon="mdi:fire-circle",
        value_fn=lambda snapshot: snapshot.calories_consumed_today,
        attributes_fn=lambda coordinator, pet_id: {
            "daily_calorie_target": coordinator.get_snapshot(pet_id).daily_calories,
            "treat_calories_today": coordinator.get_snapshot(pet_id).treat_calories_today,
        },
    ),
    DivaSensorDescription(
        key="water_today",
        translation_key="water_today",
        native_unit_of_measurement="mL",
        icon="mdi:cup-water",
        value_fn=lambda snapshot: snapshot.water_today_ml,
        attributes_fn=lambda coordinator, pet_id: {
            "target_water_today": daily_water_target_ml(coordinator.pets[pet_id].engine.state.weight_kg),
        },
    ),
    DivaSensorDescription(
        key="weight",
        translation_key="weight",
        native_unit_of_measurement="kg",
        icon="mdi:scale-bathroom",
        value_fn=lambda snapshot: snapshot.weight_kg,
        attributes_fn=lambda coordinator, pet_id: {
            "goal_min_kg": coordinator.get_snapshot(pet_id).weight_goal_min_kg,
            "goal_max_kg": coordinator.get_snapshot(pet_id).weight_goal_max_kg,
            "weight_history": coordinator.pets[pet_id].engine.state.weight_history[-10:],
        },
    ),
    DivaSensorDescription(
        key="weight_trend",
        translation_key="weight_trend",
        native_unit_of_measurement="kg",
        icon="mdi:chart-line",
        value_fn=lambda snapshot: snapshot.weight_trend_kg,
        attributes_fn=lambda coordinator, pet_id: {
            "period_days": 14,
            "goal_min_kg": coordinator.get_snapshot(pet_id).weight_goal_min_kg,
            "goal_max_kg": coordinator.get_snapshot(pet_id).weight_goal_max_kg,
            "current_weight_kg": coordinator.get_snapshot(pet_id).weight_kg,
            "weight_history": coordinator.pets[pet_id].engine.state.weight_history[-10:],
        },
    ),
    DivaSensorDescription(
        key="last_feeding",
        translation_key="last_feeding",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-outline",
        value_fn=lambda snapshot: _as_datetime(snapshot.last_feeding_at),
    ),
    DivaSensorDescription(
        key="next_feeding",
        translation_key="next_feeding",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-alert-outline",
        value_fn=lambda snapshot: _as_datetime(snapshot.next_feeding_at),
    ),
    DivaSensorDescription(
        key="next_walk",
        translation_key="next_walk",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:dog-side",
        value_fn=lambda snapshot: _as_datetime(snapshot.next_walk_at),
    ),
    DivaSensorDescription(
        key="walk_distance",
        translation_key="walk_distance",
        native_unit_of_measurement="km",
        icon="mdi:map-marker-distance",
        value_fn=lambda snapshot: snapshot.walk_distance_km,
        attributes_fn=lambda coordinator, pet_id: {
            "active_walk": coordinator.pets[pet_id].engine.state.walk_active,
            "current_route_points": coordinator.pets[pet_id].engine.state.current_walk_route,
            "current_route_line": _route_line(coordinator.pets[pet_id].engine.state.current_walk_route),
            "current_route_geojson": _route_geojson(coordinator.pets[pet_id].engine.state.current_walk_route),
            "current_route_bounds": _route_bounds(coordinator.pets[pet_id].engine.state.current_walk_route),
            "last_walk_distance_km": coordinator.get_snapshot(pet_id).last_walk_distance_km,
            "last_walk_duration_minutes": coordinator.get_snapshot(pet_id).last_walk_duration_minutes,
            "last_walk_route_summary": coordinator.get_snapshot(pet_id).last_walk_route_summary,
            "last_route_points": coordinator.pets[pet_id].engine.state.last_walk_route,
            "last_route_line": _route_line(coordinator.pets[pet_id].engine.state.last_walk_route),
            "last_route_geojson": _route_geojson(coordinator.pets[pet_id].engine.state.last_walk_route),
            "last_route_bounds": _route_bounds(coordinator.pets[pet_id].engine.state.last_walk_route),
            "map_center": _route_center(
                coordinator.pets[pet_id].engine.state.current_walk_route
                or coordinator.pets[pet_id].engine.state.last_walk_route
                or coordinator.pets[pet_id].engine.state.gps_history
            ),
            "last_walk_summary": coordinator.pets[pet_id].engine.state.last_walk_summary,
        },
    ),
    DivaSensorDescription(
        key="walk_distance_today",
        translation_key="walk_distance_today",
        native_unit_of_measurement="km",
        icon="mdi:walk",
        value_fn=lambda snapshot: snapshot.walk_distance_today_km,
        attributes_fn=lambda coordinator, pet_id: _walk_distance_today_attributes(coordinator, pet_id),
    ),
    DivaSensorDescription(
        key="next_medication",
        translation_key="next_medication",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:pill",
        value_fn=lambda snapshot: _as_datetime(snapshot.next_medication_at),
    ),
    DivaSensorDescription(
        key="next_vet_visit",
        translation_key="next_vet_visit",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:stethoscope",
        value_fn=lambda snapshot: _as_datetime(snapshot.next_vet_visit_at),
    ),
    DivaSensorDescription(
        key="next_vaccine",
        translation_key="next_vaccine",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:needle",
        value_fn=lambda snapshot: _as_datetime(snapshot.next_vaccine_at),
    ),
    DivaSensorDescription(
        key="vaccine_status",
        translation_key="vaccine_status",
        icon="mdi:needle-off",
        value_fn=lambda snapshot: snapshot.vaccine_status,
        attributes_fn=lambda coordinator, pet_id: {
            "pet_id": pet_id,
            "pet_name": coordinator.get_profile(pet_id).name,
            "next_vaccine_at": coordinator.get_snapshot(pet_id).next_vaccine_at,
            "vaccine_profile": coordinator.get_profile(pet_id).vaccine_profile,
            "regional_policy": coordinator.get_profile(pet_id).regional_policy,
            "vet_override": coordinator.get_profile(pet_id).vet_override,
            "completed_vaccine_doses": dict(coordinator.pets[pet_id].engine.state.completed_vaccine_doses),
            "vaccine_overrides": dict(coordinator.pets[pet_id].engine.state.vaccine_runtime_overrides),
            "configured_overrides": [item.as_dict() for item in coordinator.get_profile(pet_id).vaccine_overrides],
            "effective_plan": [
                item.as_dict()
                for item in coordinator.get_profile(pet_id).effective_vaccine_plan(coordinator.coordinator_now.date())
            ]
            if hasattr(coordinator, "coordinator_now")
            else [item.as_dict() for item in coordinator.get_profile(pet_id).effective_vaccine_plan(date.today())],
        },
    ),
    DivaSensorDescription(
        key="last_seen_eating",
        translation_key="last_seen_eating",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:camera-timer",
        value_fn=lambda snapshot: _as_datetime(snapshot.last_seen_eating_at),
    ),
    DivaSensorDescription(
        key="activity_level",
        translation_key="activity_level",
        native_unit_of_measurement="%",
        icon="mdi:run-fast",
        value_fn=lambda snapshot: snapshot.activity_level,
        attributes_fn=lambda coordinator, pet_id: {
            "baseline_activity_level": _baseline_metrics(coordinator.pets[pet_id].engine.state)["activity_level"],
            "home_alone": coordinator.get_snapshot(pet_id).home_alone,
            "active_modes": list(coordinator.get_snapshot(pet_id).active_modes),
        },
    ),
    DivaSensorDescription(
        key="sleep_duration",
        translation_key="sleep_duration",
        native_unit_of_measurement="h",
        icon="mdi:sleep",
        value_fn=lambda snapshot: snapshot.sleep_duration_hours,
        attributes_fn=lambda coordinator, pet_id: {
            "baseline_sleep_hours": _baseline_metrics(coordinator.pets[pet_id].engine.state)["sleep_hours"],
            "sleep_quality_score": coordinator.get_snapshot(pet_id).sleep_quality_score,
            "sleep_interruptions_today": coordinator.pets[pet_id].engine.state.sleep_interruptions_today,
            "sleep_minutes_by_hour": dict(coordinator.pets[pet_id].engine.state.sleep_minutes_by_hour),
        },
    ),
    DivaSensorDescription(
        key="sleep_quality",
        translation_key="sleep_quality",
        native_unit_of_measurement="%",
        icon="mdi:sleep-off",
        value_fn=lambda snapshot: snapshot.sleep_quality_score,
        attributes_fn=lambda coordinator, pet_id: {
            "sleep_duration_hours": coordinator.get_snapshot(pet_id).sleep_duration_hours,
            "sleep_interruptions_today": coordinator.pets[pet_id].engine.state.sleep_interruptions_today,
            "baseline_sleep_hours": _baseline_metrics(coordinator.pets[pet_id].engine.state)["sleep_hours"],
        },
    ),
    DivaSensorDescription(
        key="stress_score",
        translation_key="stress_score",
        native_unit_of_measurement="%",
        icon="mdi:heart-flash",
        value_fn=lambda snapshot: snapshot.stress_score,
        attributes_fn=lambda coordinator, pet_id: {
            "behavior_signals": list(coordinator.get_snapshot(pet_id).active_behavior_signals),
            "caregiver_home_count": coordinator.get_snapshot(pet_id).caregiver_home_count,
            "operation_mode": coordinator.get_snapshot(pet_id).operation_mode,
            "stress_factors": list(coordinator.get_snapshot(pet_id).stress_factors),
            "behavior_profile": coordinator.get_snapshot(pet_id).behavior_profile,
        },
    ),
    DivaSensorDescription(
        key="inactivity_duration",
        translation_key="inactivity_duration",
        native_unit_of_measurement="min",
        icon="mdi:timer-sand",
        value_fn=lambda snapshot: snapshot.inactivity_duration_minutes,
        attributes_fn=lambda coordinator, pet_id: {
            "last_activity_at": coordinator.pets[pet_id].engine.state.last_activity_at,
            "active_minutes_by_hour": dict(coordinator.pets[pet_id].engine.state.active_minutes_by_hour),
        },
    ),
    DivaSensorDescription(
        key="separation_score",
        translation_key="separation_score",
        native_unit_of_measurement="%",
        icon="mdi:account-arrow-left",
        value_fn=lambda snapshot: snapshot.separation_score,
        attributes_fn=lambda coordinator, pet_id: {
            "separation_minutes_today": coordinator.pets[pet_id].engine.state.separation_minutes_today,
            "home_alone": coordinator.get_snapshot(pet_id).home_alone,
            "caregiver_home_count": coordinator.get_snapshot(pet_id).caregiver_home_count,
            "current_room": coordinator.get_snapshot(pet_id).current_room,
            "current_zone": coordinator.get_snapshot(pet_id).current_zone,
        },
    ),
    DivaSensorDescription(
        key="separation_risk",
        translation_key="separation_risk",
        native_unit_of_measurement="%",
        icon="mdi:account-alert-outline",
        value_fn=lambda snapshot: snapshot.separation_score,
        attributes_fn=lambda coordinator, pet_id: {
            "separation_minutes_today": coordinator.pets[pet_id].engine.state.separation_minutes_today,
            "home_alone": coordinator.get_snapshot(pet_id).home_alone,
            "caregiver_home_count": coordinator.get_snapshot(pet_id).caregiver_home_count,
            "current_room": coordinator.get_snapshot(pet_id).current_room,
            "current_zone": coordinator.get_snapshot(pet_id).current_zone,
            "risk_band": _risk_band(coordinator.get_snapshot(pet_id).separation_score),
        },
    ),
    DivaSensorDescription(
        key="feeding_quality_score",
        translation_key="feeding_quality_score",
        native_unit_of_measurement="%",
        icon="mdi:clipboard-check-outline",
        value_fn=lambda snapshot: snapshot.feeding_quality_score,
        attributes_fn=lambda coordinator, pet_id: {
            "calories_consumed_today": coordinator.get_snapshot(pet_id).calories_consumed_today,
            "daily_calories": coordinator.get_snapshot(pet_id).daily_calories,
            "treat_calories_today": coordinator.get_snapshot(pet_id).treat_calories_today,
            "active_food_transition": coordinator.get_snapshot(pet_id).active_food_transition,
        },
    ),
    DivaSensorDescription(
        key="baseline_drift",
        translation_key="baseline_drift",
        native_unit_of_measurement="%",
        icon="mdi:chart-bell-curve-cumulative",
        value_fn=lambda snapshot: snapshot.baseline_drift_score,
        attributes_fn=lambda coordinator, pet_id: {
            "baseline": _baseline_metrics(coordinator.pets[pet_id].engine.state),
            "subtle_anomalies": list(coordinator.get_snapshot(pet_id).subtle_anomalies),
            "latest_behavior_summary": coordinator.get_snapshot(pet_id).behavior_summary,
        },
    ),
    DivaSensorDescription(
        key="behavior_profile",
        translation_key="behavior_profile",
        icon="mdi:brain",
        value_fn=lambda snapshot: snapshot.behavior_profile or "unknown",
        attributes_fn=lambda coordinator, pet_id: {
            "behavior_summary": coordinator.get_snapshot(pet_id).behavior_summary,
            "stress_factors": list(coordinator.get_snapshot(pet_id).stress_factors),
            "latest_behavior_observation_at": coordinator.get_snapshot(pet_id).latest_behavior_observation_at,
            "behavior_observations": coordinator.pets[pet_id].engine.state.behavior_observations[-10:],
        },
    ),
    DivaSensorDescription(
        key="health_score",
        translation_key="health_score",
        native_unit_of_measurement="%",
        icon="mdi:heart-pulse",
        value_fn=lambda snapshot: snapshot.health_score,
        attributes_fn=lambda coordinator, pet_id: {
            "active_anomalies": sorted(coordinator.pets[pet_id].engine.state.active_anomalies),
            "stress_score": coordinator.get_snapshot(pet_id).stress_score,
            "baseline": _baseline_metrics(coordinator.pets[pet_id].engine.state),
            "gps_tracker_state": coordinator.get_snapshot(pet_id).gps_tracker_state,
            "ble_tracker_state": coordinator.get_snapshot(pet_id).ble_tracker_state,
            "current_zone": coordinator.get_snapshot(pet_id).current_zone,
            "current_room": coordinator.get_snapshot(pet_id).current_room,
            "distance_from_safe_zone_m": coordinator.get_snapshot(pet_id).distance_from_safe_zone_m,
            "passport_number": coordinator.pets[pet_id].profile.passport_number,
            "microchip_id": coordinator.pets[pet_id].profile.microchip_id,
            "insurance_policy": coordinator.pets[pet_id].profile.insurance_policy,
            "primary_vet": coordinator.pets[pet_id].profile.primary_vet,
            "body_condition_score": coordinator.get_snapshot(pet_id).body_condition_score,
            "symptom_severity_score": coordinator.get_snapshot(pet_id).symptom_severity_score,
            "recovery_status": coordinator.get_snapshot(pet_id).recovery_status,
            "diagnoses": [item.as_dict() for item in coordinator.pets[pet_id].profile.diagnoses],
            "allergies": [item.as_dict() for item in coordinator.pets[pet_id].profile.allergies],
            "contraindications": [item.as_dict() for item in coordinator.pets[pet_id].profile.contraindications],
            "medical_history": [item.as_dict() for item in coordinator.pets[pet_id].profile.medical_history[-10:]],
            "baseline_drift_score": coordinator.get_snapshot(pet_id).baseline_drift_score,
            "behavior_profile": coordinator.get_snapshot(pet_id).behavior_profile,
            "behavior_summary": coordinator.get_snapshot(pet_id).behavior_summary,
        },
    ),
    DivaSensorDescription(
        key="active_medications",
        translation_key="active_medications",
        icon="mdi:clipboard-pulse",
        value_fn=lambda snapshot: len(snapshot.active_medications),
        attributes_fn=lambda coordinator, pet_id: {
            "pet_id": pet_id,
            "pet_name": coordinator.get_profile(pet_id).name,
            "medications": list(coordinator.get_snapshot(pet_id).active_medications),
            "overdue_medications": list(coordinator.get_snapshot(pet_id).overdue_medications),
            "configured_courses": [item.as_dict() for item in coordinator.get_profile(pet_id).medication_courses],
        },
    ),
    DivaSensorDescription(
        key="recovery_status",
        translation_key="recovery_status",
        icon="mdi:medical-bag",
        value_fn=lambda snapshot: snapshot.recovery_status,
    ),
    DivaSensorDescription(
        key="recovery_progress",
        translation_key="recovery_progress",
        native_unit_of_measurement="%",
        icon="mdi:progress-check",
        value_fn=lambda snapshot: snapshot.recovery_progress_pct,
        attributes_fn=lambda coordinator, pet_id: _recovery_progress_attributes(coordinator, pet_id),
    ),
    DivaSensorDescription(
        key="body_condition_score",
        translation_key="body_condition_score",
        icon="mdi:scale-balance",
        value_fn=lambda snapshot: snapshot.body_condition_score,
        attributes_fn=lambda coordinator, pet_id: {
            "recommended_range": "4-6",
            "chronic_conditions": list(coordinator.get_snapshot(pet_id).chronic_conditions),
        },
    ),
    DivaSensorDescription(
        key="symptom_severity",
        translation_key="symptom_severity",
        native_unit_of_measurement="%",
        icon="mdi:alert-circle-outline",
        value_fn=lambda snapshot: snapshot.symptom_severity_score,
        attributes_fn=lambda coordinator, pet_id: {
            "recent_symptoms": coordinator.pets[pet_id].engine.state.symptom_log[-5:],
        },
    ),
    DivaSensorDescription(
        key="symptom_burden",
        translation_key="symptom_burden",
        native_unit_of_measurement="%",
        icon="mdi:clipboard-pulse-outline",
        value_fn=lambda snapshot: snapshot.symptom_severity_score,
        attributes_fn=lambda coordinator, pet_id: _symptom_burden_attributes(coordinator, pet_id),
    ),
    DivaSensorDescription(
        key="recommended_food_portion",
        translation_key="recommended_food_portion",
        native_unit_of_measurement="g",
        icon="mdi:food-steak",
        value_fn=lambda snapshot: snapshot.recommended_food_portion_grams,
        attributes_fn=lambda coordinator, pet_id: {
            "daily_calories": coordinator.pets[pet_id].engine.state.daily_calories,
            "feeding_routines": [routine.as_dict() for routine in coordinator.pets[pet_id].profile.effective_feeding_routines()],
            "food_catalog": [item.as_dict() for item in coordinator.pets[pet_id].profile.food_catalog],
            "food_transition_plan": [step.as_dict() for step in coordinator.pets[pet_id].profile.food_transition_plan],
        },
    ),
    DivaSensorDescription(
        key="daily_timeline",
        translation_key="daily_timeline",
        icon="mdi:calendar-clock",
        value_fn=lambda snapshot: snapshot.routine_status or "No upcoming routines",
        attributes_fn=lambda coordinator, pet_id: {
            "upcoming_events": coordinator.get_timeline(pet_id),
            "recent_journal": coordinator.pets[pet_id].engine.state.journal_entries[-10:],
            "external_calendars": list(coordinator.pets[pet_id].profile.external_calendar_entity_ids),
            "operation_mode": coordinator.get_snapshot(pet_id).operation_mode,
            "active_modes": list(coordinator.get_snapshot(pet_id).active_modes),
            "routine_exceptions": [exception.as_dict() for exception in coordinator.pets[pet_id].profile.routine_exceptions],
            "current_zone": coordinator.get_snapshot(pet_id).current_zone,
            "current_room": coordinator.get_snapshot(pet_id).current_room,
            "room_dwell_today_minutes": dict(coordinator.pets[pet_id].engine.state.room_dwell_today_minutes),
            "zone_visits_today": dict(coordinator.pets[pet_id].engine.state.zone_visits_today),
            "behavior_profile": coordinator.get_snapshot(pet_id).behavior_profile,
            "behavior_summary": coordinator.get_snapshot(pet_id).behavior_summary,
        },
    ),
    DivaSensorDescription(
        key="current_shift",
        translation_key="current_shift",
        icon="mdi:badge-account-horizontal",
        value_fn=lambda snapshot: snapshot.current_shift or "unassigned",
        attributes_fn=lambda coordinator, pet_id: {
            "next_shift_at": coordinator.get_snapshot(pet_id).next_shift_at,
            "care_shifts": [shift.as_dict() for shift in coordinator.pets[pet_id].profile.care_shifts],
            "care_roles": [role.as_dict() for role in coordinator.pets[pet_id].profile.care_roles],
        },
    ),
    DivaSensorDescription(
        key="checklist_progress",
        translation_key="checklist_progress",
        native_unit_of_measurement="%",
        icon="mdi:check-decagram-outline",
        value_fn=lambda snapshot: snapshot.checklist_progress_pct,
        attributes_fn=lambda coordinator, pet_id: {
            "pending_items": list(coordinator.get_snapshot(pet_id).pending_checklist_items),
            "checklist_templates": [item.as_dict() for item in coordinator.pets[pet_id].profile.checklist_items],
            "recent_completions": coordinator.pets[pet_id].engine.state.checklist_completions[-10:],
        },
    ),
    DivaSensorDescription(
        key="checklist_completion",
        translation_key="checklist_completion",
        native_unit_of_measurement="%",
        icon="mdi:checkbox-marked-circle-outline",
        value_fn=lambda snapshot: snapshot.checklist_progress_pct,
        attributes_fn=lambda coordinator, pet_id: {
            "pending_items": list(coordinator.get_snapshot(pet_id).pending_checklist_items),
            "completed_items_today": _completed_checklist_count(coordinator, pet_id, days=1),
            "completed_items_week": _completed_checklist_count(coordinator, pet_id, days=7),
        },
    ),
    DivaSensorDescription(
        key="pending_approvals",
        translation_key="pending_approvals",
        icon="mdi:account-clock-outline",
        value_fn=lambda snapshot: snapshot.pending_approvals_count,
        attributes_fn=lambda coordinator, pet_id: {
            "approvals": coordinator.pets[pet_id].engine.state.pending_approvals[-20:],
        },
    ),
    DivaSensorDescription(
        key="today_vs_baseline",
        translation_key="today_vs_baseline",
        icon="mdi:compare-horizontal",
        value_fn=lambda snapshot: snapshot.today_vs_baseline or "No baseline yet",
    ),
    DivaSensorDescription(
        key="weekly_summary",
        translation_key="weekly_summary",
        icon="mdi:chart-box-outline",
        value_fn=lambda snapshot: snapshot.weekly_summary or "No weekly summary yet",
    ),
    DivaSensorDescription(
        key="operations_center",
        translation_key="operations_center",
        icon="mdi:view-dashboard-outline",
        value_fn=lambda snapshot: snapshot.operations_summary or "No operations data",
        attributes_fn=lambda coordinator, pet_id: {
            "pet_id": pet_id,
            "pet_name": coordinator.get_profile(pet_id).name,
            "current_shift": coordinator.get_snapshot(pet_id).current_shift,
            "next_shift_at": coordinator.get_snapshot(pet_id).next_shift_at,
            "checklist_progress_pct": coordinator.get_snapshot(pet_id).checklist_progress_pct,
            "pending_checklist_items": list(coordinator.get_snapshot(pet_id).pending_checklist_items),
            "pending_approvals_count": coordinator.get_snapshot(pet_id).pending_approvals_count,
            "today_vs_baseline": coordinator.get_snapshot(pet_id).today_vs_baseline,
            "weekly_summary": coordinator.get_snapshot(pet_id).weekly_summary,
            "recent_journal": coordinator.pets[pet_id].engine.state.journal_entries[-20:],
            "generated_reports": coordinator.pets[pet_id].engine.state.generated_reports[-10:],
        },
    ),
    DivaSensorDescription(
        key="calendar_sync",
        translation_key="calendar_sync",
        icon="mdi:calendar-sync-outline",
        value_fn=lambda snapshot: snapshot.calendar_sync_status,
        attributes_fn=lambda coordinator, pet_id: {
            "pet_id": pet_id,
            "pet_name": coordinator.get_profile(pet_id).name,
            "linked_calendars": [link.as_dict() for link in coordinator.pets[pet_id].profile.calendar_links],
            "sync_state": dict(coordinator.pets[pet_id].engine.state.calendar_sync_state),
            "import_overrides": coordinator.pets[pet_id].engine.state.calendar_import_overrides[-20:],
            "conflicts_count": coordinator.get_snapshot(pet_id).calendar_conflicts_count,
        },
    ),
    DivaSensorDescription(
        key="calendar_conflicts",
        translation_key="calendar_conflicts",
        icon="mdi:calendar-alert-outline",
        value_fn=lambda snapshot: snapshot.calendar_conflicts_count,
        attributes_fn=lambda coordinator, pet_id: {
            "pet_id": pet_id,
            "pet_name": coordinator.get_profile(pet_id).name,
            "conflicts": coordinator.pets[pet_id].engine.state.calendar_conflicts[-20:],
            "resolved_conflicts": coordinator.pets[pet_id].engine.state.calendar_conflict_resolutions[-20:],
            "calendar_sync_status": coordinator.get_snapshot(pet_id).calendar_sync_status,
        },
    ),
    DivaSensorDescription(
        key="generated_reports",
        translation_key="generated_reports",
        icon="mdi:file-document-multiple-outline",
        value_fn=lambda snapshot: snapshot.generated_reports_count,
        attributes_fn=lambda coordinator, pet_id: {
            "pet_id": pet_id,
            "pet_name": coordinator.get_profile(pet_id).name,
            "reports": coordinator.pets[pet_id].engine.state.generated_reports[-20:],
        },
    ),
    DivaSensorDescription(
        key="current_zone",
        translation_key="current_zone",
        icon="mdi:map-marker-radius",
        value_fn=lambda snapshot: snapshot.current_zone or "unknown",
        attributes_fn=lambda coordinator, pet_id: {
            "geofence_breached": coordinator.get_snapshot(pet_id).geofence_breached,
            "distance_from_safe_zone_m": coordinator.get_snapshot(pet_id).distance_from_safe_zone_m,
            "gps_tracker_state": coordinator.get_snapshot(pet_id).gps_tracker_state,
            "safe_zones": [zone.as_dict() for zone in coordinator.pets[pet_id].profile.safe_zones],
            "gps_history": coordinator.pets[pet_id].engine.state.gps_history[-10:],
        },
    ),
    DivaSensorDescription(
        key="current_room",
        translation_key="current_room",
        icon="mdi:home-map-marker",
        value_fn=lambda snapshot: snapshot.current_room or "unknown",
        attributes_fn=lambda coordinator, pet_id: {
            "room_presence_sources": list(coordinator.get_snapshot(pet_id).room_presence_sources),
            "preferred_rooms": list(coordinator.get_snapshot(pet_id).preferred_rooms),
            "avoided_rooms": list(coordinator.get_snapshot(pet_id).avoided_rooms),
            "room_dwell_today_minutes": dict(coordinator.pets[pet_id].engine.state.room_dwell_today_minutes),
            "room_history": coordinator.pets[pet_id].engine.state.room_history[-10:],
        },
    ),
    DivaSensorDescription(
        key="room_preference",
        translation_key="room_preference",
        icon="mdi:sofa-outline",
        value_fn=lambda snapshot: snapshot.preferred_rooms[0] if snapshot.preferred_rooms else (snapshot.current_room or "unknown"),
        attributes_fn=lambda coordinator, pet_id: {
            "preferred_rooms": list(coordinator.get_snapshot(pet_id).preferred_rooms),
            "avoided_rooms": list(coordinator.get_snapshot(pet_id).avoided_rooms),
            "room_dwell_today_minutes": dict(coordinator.pets[pet_id].engine.state.room_dwell_today_minutes),
        },
    ),
    DivaSensorDescription(
        key="room_heatmap",
        translation_key="room_heatmap",
        icon="mdi:floor-plan",
        value_fn=lambda snapshot: snapshot.current_room or "No room data",
        attributes_fn=lambda coordinator, pet_id: _room_heatmap_attributes(coordinator, pet_id),
    ),
)


async def async_setup_entry(hass, entry: DivaConfigEntry, async_add_entities) -> None:
    """Set up DIVA sensor entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        DivaSensorEntity(coordinator, pet_id, description)
        for pet_id in coordinator.pet_ids
        for description in SENSORS
    )


class DivaSensorEntity(DivaPetEntity, SensorEntity):
    """Representation of a DIVA sensor."""

    entity_description: DivaSensorDescription

    def __init__(self, coordinator: DivaCoordinator, pet_id: str, description: DivaSensorDescription) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator, pet_id, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the sensor state."""
        return self.entity_description.value_fn(self.pet_snapshot)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra sensor attributes."""
        if self.entity_description.attributes_fn is None:
            return None
        return self.entity_description.attributes_fn(self.coordinator, self.pet_id)


def _as_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _baseline_metrics(runtime: PetRuntimeState) -> dict[str, float]:
    history = runtime.daily_history[-7:]
    if not history:
        return {"food_grams": 0.0, "sleep_hours": 0.0, "activity_level": 0.0}
    return {
        "food_grams": round(sum(float(item.get("food_today_grams", 0.0)) for item in history) / len(history), 1),
        "sleep_hours": round(
            sum(float(item.get("sleep_minutes_today", 0.0)) for item in history) / len(history) / 60.0,
            2,
        ),
        "activity_level": round(
            min(100.0, sum(float(item.get("activity_points_today", 0.0)) for item in history) / len(history) * 4.0),
            1,
        ),
    }


def _route_line(points: list[dict[str, Any]]) -> list[list[float]]:
    """Return a route as [lat, lon] pairs."""
    line: list[list[float]] = []
    for point in points:
        latitude = point.get("latitude")
        longitude = point.get("longitude")
        if isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
            line.append([round(float(latitude), 6), round(float(longitude), 6)])
    return line


def _route_bounds(points: list[dict[str, Any]]) -> dict[str, float] | None:
    """Return route bounds for simple frontend map fitting."""
    line = _route_line(points)
    if not line:
        return None
    lats = [item[0] for item in line]
    lons = [item[1] for item in line]
    return {
        "min_latitude": min(lats),
        "max_latitude": max(lats),
        "min_longitude": min(lons),
        "max_longitude": max(lons),
    }


def _route_center(points: list[dict[str, Any]]) -> dict[str, float] | None:
    """Return a center point for the provided route."""
    bounds = _route_bounds(points)
    if bounds is None:
        return None
    return {
        "latitude": round((bounds["min_latitude"] + bounds["max_latitude"]) / 2, 6),
        "longitude": round((bounds["min_longitude"] + bounds["max_longitude"]) / 2, 6),
    }


def _route_geojson(points: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return a minimal GeoJSON LineString for custom map cards."""
    line = _route_line(points)
    if len(line) < 2:
        return None
    return {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[lon, lat] for lat, lon in line],
        },
        "properties": {"point_count": len(line)},
    }


def _walk_distance_today_attributes(coordinator: DivaCoordinator, pet_id: str) -> dict[str, Any]:
    """Build attributes for today's walk distance sensor."""
    runtime = coordinator.pets[pet_id].engine.state
    snapshot = coordinator.get_snapshot(pet_id)
    reference_now = coordinator.coordinator_now if hasattr(coordinator, "coordinator_now") else datetime.now()
    completed_today = [
        entry
        for entry in runtime.journal_entries[-120:]
        if entry.get("action") == "finish_walk"
        and (completed_at := _as_datetime(entry.get("timestamp"))) is not None
        and completed_at.date() == reference_now.date()
    ]
    return {
        "active_walk": runtime.walk_active,
        "completed_walks_today": len(completed_today),
        "active_walk_distance_km": snapshot.walk_distance_km,
        "last_walk_distance_km": snapshot.last_walk_distance_km,
        "last_walk_duration_minutes": snapshot.last_walk_duration_minutes,
    }


def _recovery_progress_attributes(coordinator: DivaCoordinator, pet_id: str) -> dict[str, Any]:
    """Build attributes for recovery progress."""
    plan = coordinator.pets[pet_id].engine.state.active_recovery_plan or {}
    started_at = _as_datetime(plan.get("started_at"))
    expected_end = _as_datetime(plan.get("expected_end"))
    return {
        "status": coordinator.get_snapshot(pet_id).recovery_status,
        "title": plan.get("title"),
        "started_at": started_at,
        "expected_end": expected_end,
        "expected_days": plan.get("expected_days"),
        "note": plan.get("note"),
    }


def _symptom_burden_attributes(coordinator: DivaCoordinator, pet_id: str) -> dict[str, Any]:
    """Build aggregated symptom burden attributes."""
    recent = coordinator.pets[pet_id].engine.state.symptom_log[-10:]
    total_duration = round(
        sum(float(item.get("duration_hours", 0.0) or 0.0) for item in recent),
        1,
    )
    return {
        "recent_symptoms": recent,
        "recent_count": len(recent),
        "duration_hours_total": total_duration,
        "max_severity_score": max((float(item.get("severity_score", 0.0)) for item in recent), default=0.0),
    }


def _completed_checklist_count(coordinator: DivaCoordinator, pet_id: str, *, days: int) -> int:
    """Return completed checklist count within the time window."""
    now = coordinator.coordinator_now if hasattr(coordinator, "coordinator_now") else datetime.now()
    count = 0
    for entry in coordinator.pets[pet_id].engine.state.checklist_completions:
        completed_at = _as_datetime(entry.get("completed_at"))
        if completed_at is None:
            continue
        if now - completed_at <= timedelta(days=days):
            count += 1
    return count


def _risk_band(score: float) -> str:
    """Return a simple qualitative risk band."""
    if score >= 75:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def _room_heatmap_attributes(coordinator: DivaCoordinator, pet_id: str) -> dict[str, Any]:
    """Build a room heatmap payload for dashboard rendering."""
    runtime = coordinator.pets[pet_id].engine.state
    snapshot = coordinator.get_snapshot(pet_id)
    today_map = {
        str(room_name): round(float(minutes), 1)
        for room_name, minutes in runtime.room_dwell_today_minutes.items()
        if float(minutes) > 0
    }
    week_map: dict[str, float] = {}
    for item in runtime.daily_history[-7:]:
        for room_name, minutes in dict(item.get("room_dwell_today_minutes", {})).items():
            minutes_value = round(float(minutes), 1)
            if minutes_value <= 0:
                continue
            week_map[str(room_name)] = round(week_map.get(str(room_name), 0.0) + minutes_value, 1)
    for room_name, minutes in today_map.items():
        week_map[room_name] = round(week_map.get(room_name, 0.0) + minutes, 1)
    return {
        "pet_id": pet_id,
        "pet_name": coordinator.get_profile(pet_id).name,
        "current_room": snapshot.current_room,
        "today_rows": _room_heatmap_rows(today_map),
        "week_rows": _room_heatmap_rows(week_map),
        "today_total_minutes": round(sum(today_map.values()), 1),
        "week_total_minutes": round(sum(week_map.values()), 1),
        "preferred_rooms": list(snapshot.preferred_rooms),
        "avoided_rooms": list(snapshot.avoided_rooms),
        "room_history": runtime.room_history[-20:],
    }


def _room_heatmap_rows(dwell_map: dict[str, float]) -> list[dict[str, Any]]:
    """Return normalized room dwell rows suitable for a heatmap table."""
    if not dwell_map:
        return []
    max_minutes = max(dwell_map.values(), default=0.0)
    total_minutes = sum(dwell_map.values())
    rows: list[dict[str, Any]] = []
    for room_name, minutes in sorted(dwell_map.items(), key=lambda item: item[1], reverse=True):
        intensity = 0.0 if max_minutes <= 0 else round(minutes / max_minutes, 3)
        share = 0.0 if total_minutes <= 0 else round(minutes / total_minutes, 3)
        rows.append(
            {
                "room_name": room_name,
                "minutes": round(minutes, 1),
                "hours": round(minutes / 60.0, 2),
                "share_pct": round(share * 100.0, 1),
                "intensity": intensity,
                "blocks": _heat_blocks(intensity),
            }
        )
    return rows


def _heat_blocks(intensity: float) -> str:
    """Return a fixed-width block bar for markdown heatmap rendering."""
    active = max(0, min(5, round(float(intensity) * 5)))
    return ("█" * active) + ("░" * (5 - active))

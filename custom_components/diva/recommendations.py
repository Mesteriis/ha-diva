"""Recommendation and anomaly evaluation for DIVA."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any

from .const import (
    ANOMALY_GAIT,
    ANOMALY_COUGH,
    ANOMALY_GEOFENCE_BREACH,
    ANOMALY_INACTIVITY,
    ANOMALY_LIMPING,
    ANOMALY_LONG_INACTIVITY,
    ANOMALY_LOW_FOOD,
    ANOMALY_LOW_WATER,
    ANOMALY_MEDICATION_OVERDUE,
    ANOMALY_RECOVERY_DELAY,
    ANOMALY_SEPARATION_STRESS,
    ANOMALY_BASELINE_DRIFT,
    ANOMALY_SLEEP,
    ANOMALY_SLEEP_QUALITY,
    ANOMALY_STRESS,
    ANOMALY_SYMPTOM_ESCALATION,
    ANOMALY_SUBTLE_BEHAVIOR_SHIFT,
    ANOMALY_VACCINE_OVERDUE,
    ANOMALY_VOMITING,
    ANOMALY_RESTLESSNESS,
    OPERATION_MODE_ILLNESS,
)
from .pet import PetContext, PetNotice, PetRuntimeState, PetSnapshot, daily_water_target_ml


def evaluate_pet(
    snapshot: PetSnapshot,
    runtime: PetRuntimeState,
    now: datetime,
    context: PetContext | None = None,
) -> tuple[PetSnapshot, list[PetNotice], dict[str, str], set[str]]:
    """Evaluate anomalies and recommendations for the current pet snapshot."""
    context = context or PetContext()
    notices: list[PetNotice] = []
    active_anomalies: dict[str, str] = {}

    history_baseline = _history_baseline(runtime.daily_history)
    water_target = daily_water_target_ml(snapshot.weight_kg)
    timestamp = now.isoformat()
    sleep_baseline_hours = history_baseline["sleep_hours"] or 8.0
    food_baseline = history_baseline["food_grams"] or snapshot.recommended_food_portion_grams
    calorie_ratio = snapshot.calories_consumed_today / max(snapshot.daily_calories, 1.0)
    activity_baseline = history_baseline["activity_level"] or 35.0
    behavior_signals = _merged_behavior_signals(runtime, context, now)
    baseline_drift_score = _baseline_drift_score(snapshot, history_baseline)
    subtle_anomalies = _subtle_anomalies(
        snapshot=snapshot,
        baseline_drift_score=baseline_drift_score,
        behavior_signals=behavior_signals,
    )
    illness_mode = OPERATION_MODE_ILLNESS in snapshot.active_modes
    next_vaccine = _as_datetime(snapshot.next_vaccine_at)

    if now.hour >= 12 and calorie_ratio < 0.5:
        active_anomalies[ANOMALY_LOW_FOOD] = "warning"
    if now.hour >= 19 and calorie_ratio < 0.3:
        active_anomalies[ANOMALY_LOW_FOOD] = "critical"
    if now.hour >= 18 and food_baseline > 0 and snapshot.food_today_grams < food_baseline * 0.55:
        active_anomalies[ANOMALY_LOW_FOOD] = active_anomalies.get(ANOMALY_LOW_FOOD, "warning")

    if now.hour >= 13 and snapshot.water_today_ml < water_target * 0.35:
        active_anomalies[ANOMALY_LOW_WATER] = "warning"
    if now.hour >= 20 and snapshot.water_today_ml < water_target * 0.2:
        active_anomalies[ANOMALY_LOW_WATER] = "critical"

    inactivity_warning_threshold = 12 if illness_mode else 20
    inactivity_critical_threshold = 6 if illness_mode else 10
    if now.hour >= 17 and snapshot.activity_level < inactivity_warning_threshold and not snapshot.sleeping:
        active_anomalies[ANOMALY_INACTIVITY] = "warning"
    if now.hour >= 21 and snapshot.activity_level < inactivity_critical_threshold and not snapshot.sleeping:
        active_anomalies[ANOMALY_INACTIVITY] = "critical"
    if (
        not illness_mode
        and now.hour >= 18
        and activity_baseline > 0
        and snapshot.activity_level < activity_baseline * 0.4
        and not snapshot.sleeping
    ):
        active_anomalies[ANOMALY_INACTIVITY] = active_anomalies.get(ANOMALY_INACTIVITY, "warning")

    if now.hour >= 10 and sleep_baseline_hours > 1.0 and snapshot.sleep_duration_hours < sleep_baseline_hours * 0.55:
        active_anomalies[ANOMALY_SLEEP] = "warning"
    if snapshot.sleep_quality_score < 65:
        active_anomalies[ANOMALY_SLEEP_QUALITY] = "warning"
    if snapshot.sleep_quality_score < 45:
        active_anomalies[ANOMALY_SLEEP_QUALITY] = "critical"
    if snapshot.inactivity_duration_minutes >= (300 if illness_mode else 240):
        active_anomalies[ANOMALY_LONG_INACTIVITY] = "warning"
    if snapshot.inactivity_duration_minutes >= (480 if illness_mode else 360):
        active_anomalies[ANOMALY_LONG_INACTIVITY] = "critical"

    for signal in behavior_signals:
        if signal in {ANOMALY_VOMITING, ANOMALY_LIMPING, ANOMALY_GAIT, ANOMALY_COUGH, ANOMALY_RESTLESSNESS}:
            active_anomalies[signal] = "critical" if signal == ANOMALY_VOMITING else "warning"

    if snapshot.overdue_medications:
        active_anomalies[ANOMALY_MEDICATION_OVERDUE] = "warning"
    if snapshot.recovery_status == "overdue":
        active_anomalies[ANOMALY_RECOVERY_DELAY] = "warning"
    if snapshot.symptom_severity_score >= 60:
        active_anomalies[ANOMALY_SYMPTOM_ESCALATION] = "critical" if snapshot.symptom_severity_score >= 80 else "warning"
    if next_vaccine is not None and next_vaccine <= now:
        active_anomalies[ANOMALY_VACCINE_OVERDUE] = "warning"
    if snapshot.geofence_breached:
        active_anomalies[ANOMALY_GEOFENCE_BREACH] = "critical" if snapshot.distance_from_safe_zone_m and snapshot.distance_from_safe_zone_m >= 500 else "warning"
    if snapshot.separation_score >= 65:
        active_anomalies[ANOMALY_SEPARATION_STRESS] = "warning"
    if snapshot.separation_score >= 85:
        active_anomalies[ANOMALY_SEPARATION_STRESS] = "critical"
    if baseline_drift_score >= 45:
        active_anomalies[ANOMALY_BASELINE_DRIFT] = "warning"
    if baseline_drift_score >= 65:
        active_anomalies[ANOMALY_BASELINE_DRIFT] = "critical"
    if subtle_anomalies:
        active_anomalies[ANOMALY_SUBTLE_BEHAVIOR_SHIFT] = "warning"

    stress_score, stress_factors = _calculate_stress_score(
        snapshot=snapshot,
        context=context,
        behavior_signals=behavior_signals,
        sleep_baseline_hours=sleep_baseline_hours,
        active_anomalies=active_anomalies,
        baseline_drift_score=baseline_drift_score,
    )
    if stress_score >= 65:
        active_anomalies[ANOMALY_STRESS] = "warning"
    if stress_score >= 85:
        active_anomalies[ANOMALY_STRESS] = "critical"

    for anomaly_type, severity in active_anomalies.items():
        if runtime.active_anomalies.get(anomaly_type) != severity:
            notices.append(
                PetNotice(
                    category="anomaly",
                    name=anomaly_type,
                    timestamp=timestamp,
                    severity=severity,
                    message=_anomaly_message(anomaly_type, severity),
                )
            )

    sent_recommendations = set(runtime.sent_recommendations_today)
    next_vet = _as_datetime(snapshot.next_vet_visit_at)
    candidates = {
        "activity_low": (
            snapshot.activity_level < 25 and now.hour >= 16 and not illness_mode,
            "Pet activity is low. Consider a walk.",
        ),
        "food_skipped": (
            calorie_ratio < 0.5 and now.hour >= 14,
            "Pet skipped feeding. Check the bowl and appetite.",
        ),
        "feeding_quality_low": (
            snapshot.feeding_quality_score < 65.0 and now.hour >= 14,
            "Feeding quality is low today. Check served vs eaten meals and transition tolerance.",
        ),
        "treats_high": (
            snapshot.treat_calories_today > snapshot.daily_calories * 0.2 and now.hour >= 14,
            "Treat intake is high today. Review treat calories versus the daily target.",
        ),
        "transition_active": (
            snapshot.active_food_transition is not None and now.hour >= 9,
            f"Food transition active: {snapshot.active_food_transition}. Monitor appetite and stool quality.",
        ),
        "water_low": (
            snapshot.water_today_ml < water_target * 0.5 and now.hour >= 14,
            "Pet drank little water today. Refresh water and monitor intake.",
        ),
        "home_alone": (
            context.home_alone and now.hour >= 12,
            "Pet is home alone. Consider enrichment or a camera check.",
        ),
        "heat_precaution": (
            context.outside_temperature_c is not None and context.outside_temperature_c >= 28.0,
            "Outdoor temperature is high. Refresh water and keep walks to cooler hours.",
        ),
        "cold_precaution": (
            context.outside_temperature_c is not None and context.outside_temperature_c <= 0.0,
            "Outdoor temperature is low. Shorten walks and protect paws.",
        ),
        "stress_high": (
            stress_score >= 60,
            f"Stress indicators are elevated. Factors: {', '.join(stress_factors[:4])}.",
        ),
        "geofence_alert": (
            snapshot.geofence_breached,
            "Pet is outside configured safe zones. Verify location and review tracker data immediately.",
        ),
        "separation_support": (
            snapshot.separation_score >= 60,
            "Separation indicators are elevated. Add enrichment, camera checks, or a caregiver visit.",
        ),
        "sleep_quality_drop": (
            snapshot.sleep_quality_score < 70,
            "Sleep quality dropped below the rolling baseline. Review interruptions, activity timing, and environment.",
        ),
        "baseline_drift": (
            baseline_drift_score >= 40,
            "Behavior baseline drift is building. Review combined changes in food, water, sleep, and activity.",
        ),
        "subtle_shift": (
            bool(subtle_anomalies),
            f"Subtle behavior shift detected: {', '.join(subtle_anomalies[:3])}. Watch for progression.",
        ),
        "vet_due": (
            next_vet is not None and timedelta(0) <= next_vet - now <= timedelta(days=1),
            "A vet appointment is coming up. Prepare documents and transport.",
        ),
        "medication_due": (
            bool(snapshot.overdue_medications),
            f"Medication is overdue: {', '.join(snapshot.overdue_medications)}. Record the dose or review the course.",
        ),
        "vaccine_due": (
            next_vaccine is not None and timedelta(days=-1) <= next_vaccine - now <= timedelta(days=14),
            "Vaccination review is due soon. Plan the vet visit and update the vaccine record after completion.",
        ),
        "recovery_active": (
            snapshot.recovery_status in {"active", "overdue"},
            "Recovery monitoring is active. Track appetite, mobility, and symptoms closely.",
        ),
        "symptom_monitoring": (
            snapshot.symptom_severity_score >= 40,
            "Symptoms were logged recently. Monitor progression and prepare a vet summary if they persist.",
        ),
        "body_condition_review": (
            snapshot.body_condition_score < 4.0 or snapshot.body_condition_score > 6.0,
            "Body condition score is outside the typical 4-6 range. Review weight, diet, and exercise.",
        ),
    }

    for key, (enabled, message) in candidates.items():
        if not enabled or key in sent_recommendations:
            continue
        sent_recommendations.add(key)
        notices.append(
            PetNotice(
                category="recommendation",
                name=key,
                timestamp=timestamp,
                message=message,
            )
        )

    anomaly_penalty = len(active_anomalies) * 7.5
    stress_penalty = stress_score * 0.08
    behavior_profile, behavior_summary = _behavior_profile(
        snapshot=snapshot,
        behavior_signals=behavior_signals,
        stress_score=stress_score,
        baseline_drift_score=baseline_drift_score,
    )
    runtime.latest_behavior_profile = behavior_profile
    runtime.latest_behavior_summary = behavior_summary
    runtime.latest_behavior_factors = list(stress_factors)
    runtime.latest_baseline_drift_score = round(baseline_drift_score, 1)
    updated_snapshot = replace(
        snapshot,
        health_score=max(0.0, round(snapshot.health_score - anomaly_penalty - stress_penalty, 1)),
        stress_score=round(stress_score, 1),
        anomaly_detected=bool(active_anomalies),
        active_anomalies=tuple(sorted(active_anomalies)),
        baseline_drift_score=round(baseline_drift_score, 1),
        behavior_profile=behavior_profile,
        behavior_summary=behavior_summary,
        stress_factors=tuple(stress_factors),
        subtle_anomalies=tuple(subtle_anomalies),
        gps_tracker_state=context.gps_tracker_state,
        ble_tracker_state=context.ble_tracker_state,
        caregiver_home_count=context.caregiver_home_count,
        home_alone=context.home_alone,
        outside_temperature_c=context.outside_temperature_c,
        current_zone=context.current_zone,
        geofence_breached=context.geofence_breached,
        distance_from_safe_zone_m=context.distance_from_safe_zone_m,
        current_room=context.current_room,
        room_presence_sources=context.room_presence_sources,
        active_behavior_signals=tuple(sorted(behavior_signals)),
    )
    return updated_snapshot, notices, active_anomalies, sent_recommendations


def _history_baseline(history: list[dict[str, Any]]) -> dict[str, float]:
    """Return baseline metrics from rolling day history."""
    if not history:
        return {"food_grams": 0.0, "sleep_hours": 0.0, "activity_level": 0.0}
    sample = history[-7:]
    food = sum(float(item.get("food_today_grams", 0.0)) for item in sample) / len(sample)
    sleep_hours = sum(float(item.get("sleep_minutes_today", 0.0)) for item in sample) / len(sample) / 60.0
    activity_level = (
        sum(float(item.get("activity_points_today", 0.0)) for item in sample) / len(sample) * 4.0
    )
    return {
        "food_grams": round(food, 1),
        "sleep_hours": round(sleep_hours, 2),
        "activity_level": round(min(100.0, activity_level), 1),
    }


def _merged_behavior_signals(
    runtime: PetRuntimeState,
    context: PetContext,
    now: datetime,
) -> tuple[str, ...]:
    signals = set(context.active_behavior_signals)
    for report in runtime.behavior_reports[-40:]:
        report_time = _as_datetime(report.get("timestamp"))
        if report_time is None or now - report_time > timedelta(hours=48):
            continue
        behavior_type = report.get("type")
        if behavior_type:
            signals.add(str(behavior_type))
    for observation in runtime.behavior_observations[-80:]:
        observed_at = _as_datetime(observation.get("timestamp"))
        if observed_at is None or now - observed_at > timedelta(hours=48):
            continue
        confidence = float(observation.get("confidence", 0.0))
        if confidence < 0.45:
            continue
        behavior_type = observation.get("type")
        if behavior_type:
            signals.add(str(behavior_type))
    return tuple(sorted(signals))


def _calculate_stress_score(
    *,
    snapshot: PetSnapshot,
    context: PetContext,
    behavior_signals: tuple[str, ...],
    sleep_baseline_hours: float,
    active_anomalies: dict[str, str],
    baseline_drift_score: float,
) -> tuple[float, list[str]]:
    """Estimate stress from behavior, anomalies, and context."""
    score = 0.0
    factors: list[str] = []
    if snapshot.activity_level < 20 and not snapshot.sleeping:
        score += 18.0
        factors.append("low_activity")
    if sleep_baseline_hours > 1.0 and snapshot.sleep_duration_hours < sleep_baseline_hours * 0.6:
        score += 20.0
        factors.append("sleep_below_baseline")
    if snapshot.sleep_quality_score < 65:
        score += 15.0
        factors.append("sleep_quality_drop")
    if context.home_alone:
        score += 10.0
        factors.append("home_alone")
    score += snapshot.separation_score * 0.35
    if snapshot.separation_score >= 50:
        factors.append("separation_pressure")
    if snapshot.geofence_breached:
        score += 20.0
        factors.append("outside_safe_zone")
    if context.outside_temperature_c is not None and (context.outside_temperature_c >= 30.0 or context.outside_temperature_c <= -2.0):
        score += 12.0
        factors.append("temperature_stress")
    score += len(behavior_signals) * 18.0
    if behavior_signals:
        factors.append(f"behavior_signals:{len(behavior_signals)}")
    score += baseline_drift_score * 0.22
    if baseline_drift_score >= 40:
        factors.append("baseline_drift")
    if snapshot.inactivity_duration_minutes >= 240:
        score += 10.0
        factors.append("long_inactivity")
    score += len(active_anomalies) * 6.0
    if active_anomalies:
        factors.append(f"active_anomalies:{len(active_anomalies)}")
    return max(0.0, min(100.0, score)), factors


def _anomaly_message(anomaly_type: str, severity: str) -> str:
    """Return a human-readable anomaly message."""
    messages = {
        ANOMALY_LOW_FOOD: "Food intake is below the expected range.",
        ANOMALY_LOW_WATER: "Water intake is below the expected range.",
        ANOMALY_INACTIVITY: "Activity is low for the current day.",
        ANOMALY_SLEEP: "Sleep duration is below the rolling baseline.",
        ANOMALY_STRESS: "Stress indicators are elevated.",
        ANOMALY_VOMITING: "Vomiting signal detected.",
        ANOMALY_COUGH: "Cough signal detected.",
        ANOMALY_LIMPING: "Limping signal detected.",
        ANOMALY_GAIT: "Gait change signal detected.",
        ANOMALY_RESTLESSNESS: "Restlessness signal detected.",
        ANOMALY_LONG_INACTIVITY: "The pet has been inactive for an unusually long period.",
        ANOMALY_MEDICATION_OVERDUE: "A medication dose was missed or delayed.",
        ANOMALY_VACCINE_OVERDUE: "A vaccination review is overdue.",
        ANOMALY_SYMPTOM_ESCALATION: "Recent symptoms indicate escalation.",
        ANOMALY_RECOVERY_DELAY: "The recovery plan exceeded the expected end date.",
        ANOMALY_GEOFENCE_BREACH: "The pet is outside configured safe zones.",
        ANOMALY_SEPARATION_STRESS: "Separation indicators are elevated.",
        ANOMALY_SLEEP_QUALITY: "Sleep quality dropped below the rolling baseline.",
        ANOMALY_BASELINE_DRIFT: "Combined behavior metrics are drifting away from the rolling baseline.",
        ANOMALY_SUBTLE_BEHAVIOR_SHIFT: "Small changes across multiple signals indicate a subtle behavior shift.",
    }
    prefix = "Critical" if severity == "critical" else "Warning"
    return f"{prefix}: {messages.get(anomaly_type, anomaly_type)}"


def _baseline_drift_score(snapshot: PetSnapshot, baseline: dict[str, float]) -> float:
    """Return a combined drift score against rolling baselines."""
    score = 0.0
    if baseline["food_grams"] > 0:
        score += min(25.0, abs(snapshot.food_today_grams - baseline["food_grams"]) / baseline["food_grams"] * 25.0)
    if baseline["sleep_hours"] > 0:
        score += min(25.0, abs(snapshot.sleep_duration_hours - baseline["sleep_hours"]) / baseline["sleep_hours"] * 25.0)
    if baseline["activity_level"] > 0:
        score += min(25.0, abs(snapshot.activity_level - baseline["activity_level"]) / baseline["activity_level"] * 25.0)
    if snapshot.sleep_quality_score < 80:
        score += min(15.0, (80.0 - snapshot.sleep_quality_score) * 0.5)
    if snapshot.inactivity_duration_minutes >= 180:
        score += min(20.0, (snapshot.inactivity_duration_minutes - 180.0) / 12.0)
    return max(0.0, min(100.0, score))


def _subtle_anomalies(
    *,
    snapshot: PetSnapshot,
    baseline_drift_score: float,
    behavior_signals: tuple[str, ...],
) -> list[str]:
    """Return subtle anomaly reasons before they become explicit incidents."""
    reasons: list[str] = []
    if 35 <= baseline_drift_score < 65:
        reasons.append("baseline_drift_building")
    if 55 <= snapshot.sleep_quality_score < 75:
        reasons.append("sleep_quality_soft_drop")
    if 120 <= snapshot.inactivity_duration_minutes < 240:
        reasons.append("inactivity_creeping_up")
    if snapshot.separation_score >= 45:
        reasons.append("separation_pressure_rising")
    if behavior_signals and all(
        signal not in {ANOMALY_VOMITING, ANOMALY_LIMPING, ANOMALY_GAIT, ANOMALY_COUGH}
        for signal in behavior_signals
    ):
        reasons.append("behavior_signal_cluster")
    return reasons[:4]


def _behavior_profile(
    *,
    snapshot: PetSnapshot,
    behavior_signals: tuple[str, ...],
    stress_score: float,
    baseline_drift_score: float,
) -> tuple[str, str]:
    """Return an AI-style profile label and summary."""
    if stress_score >= 75 or snapshot.separation_score >= 70:
        return "separation_sensitive", "Elevated stress or separation pressure with close monitoring recommended."
    if ANOMALY_RESTLESSNESS in behavior_signals or baseline_drift_score >= 60:
        return "restless_watch", "Restlessness or baseline drift is elevated versus the usual pattern."
    if snapshot.activity_level >= 55 and stress_score < 45:
        return "playful_explorer", "High activity with stable stress indicators."
    if snapshot.sleep_quality_score >= 80 and baseline_drift_score < 30:
        return "balanced_companion", "Balanced sleep, activity, and behavior versus baseline."
    return "low_energy_monitor", "Lower energy or softer deviations suggest closer observation."


def _as_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed

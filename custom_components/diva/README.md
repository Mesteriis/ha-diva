# DIVA - Pet Guardian

Documentation languages:

- English: [README.md](./README.md)
- Russian: [README.ru.md](./README.ru.md)
- Spanish: [README.es.md](./README.es.md)

DIVA is a Home Assistant custom integration for pet care tracking. It models the installation as a single DIVA hub and each pet as its own Home Assistant device. DIVA publishes entities, timeline calendars, runtime events, anomalies, and recommendations for Herald or native Home Assistant automations.

The hub name is fixed to `DIVA Pet Guardian` in the normal UI flow. It is used only as the config entry title and hub device label.

## Architecture

- Async-first implementation
- `DataUpdateCoordinator` runtime model
- One DIVA hub config entry with multiple pets inside it
- Event-driven outputs, never direct notifications
- Optional camera-based bowl monitoring
- Optional calendar sync to external `calendar.*` entities
- JSON runtime storage in `/config/diva_runtime.json`

## Features

- Feeding, water, walk, and sleep tracking
- Structured weekly planner in the config/options form
- Multiple feeding types: dry, wet, treat, medication, supplement
- Food catalog with brand, category, and calorie density
- Food transition plan with dated mix steps
- Treat accounting, calories consumed, and feeding quality scoring
- Medical core with medication courses, symptom logging, recovery plans, and chronic condition tracking
- Default dog vaccination plan based on WSAVA core guidance with Spain overlays for rabies, leptospirosis, and leishmaniosis review
- Editable vaccine workflow with complete, reschedule, and cancel actions
- Weight goals, rolling weight history, and 14-day weight trend analytics
- Combined per-pet timeline calendar
- Vet appointment planning and external calendar sync
- Pet passport fields: passport number, microchip, insurance, vet details
- GPS/BLE tracking, safe zones, room presence mapping, and household presence links
- Behavior-signal ingest from external AI/vision entities or manual reporting
- Structured behavior observations with source, confidence, and detector/model provenance
- Rolling baseline analytics for food, sleep, activity, and hourly sleep/activity buckets
- Explainable stress scoring, sleep quality analytics, long inactivity detection, subtle anomaly detection, and AI behavior profiles
- Seasonal recommendations using a linked `weather.*` or numeric `sensor.*` temperature entity
- Care journal with actor/action/note entries
- Family operations model with care roles, caregiver shifts, recurring checklists, approval queues, and operations reports
- Optional bowl camera analysis with simple pixel differencing and optional OpenCV contour support

## Installation

1. Copy `custom_components/diva` into your Home Assistant config directory.
2. Restart Home Assistant.
3. Add the `DIVA` integration from `Settings -> Devices & services`.
4. Create the first pet profile.
5. Add more pets from the integration `Options` flow.

## Optional OpenCV Support

DIVA works with `numpy` only.
For stronger contour-based bowl interaction detection, install an OpenCV package in the Home Assistant Python environment, for example `opencv-python-headless`.

## JSON Storage

DIVA persists hub runtime data into `/config/diva_runtime.json`.
The file stores the hub name, pet profiles, routines, timeline snapshots, journal entries, calendar sync state, recent notices, and camera metadata.
Legacy `.storage` runtime data is imported automatically on the first start after the update.

## Architecture

DIVA now uses a versioned `pet_schema = 3` config shape.

Each pet record is stored in explicit sections:

- `profile`
- `plan`
- `medical`
- `analytics`
- `external_links`

The runtime JSON payload also stores typed `runtime_sections` for:

- `medical`
- `mobility`
- `behavior`
- `operations`
- `reports`

Inside the domain layer, `PetEngine` now exposes explicit sub-engine boundaries:

- `routines`
- `nutrition`
- `medical`
- `mobility`
- `behavior`
- `reporting`

## Configuration Model

The DIVA hub stores a list of pets.
Each pet profile includes:

- `name`
- `species`
- `breed`
- `birthdate`
- `weight`
- `diet_mode`
- Optional `avatar`
- Optional `feeding_routines`
- Optional `walk_routines`
- Optional `care_routines`
- Optional `routine_exceptions`
- Optional `default_manual_mode`
- Optional `weather_adaptation`
- Optional `heat_threshold_c`
- Optional `cold_threshold_c`
- Optional `vet_appointments`
- Optional `food_catalog`
- Optional `food_transition_plan`
- Optional `medical_country`
- Optional `medical_region`
- Optional `regional_policy`
- Optional `vaccine_profile`
- Optional `vet_override`
- Optional `body_condition_score`
- Optional `weight_goal_min_kg`
- Optional `weight_goal_max_kg`
- Optional `medication_courses`
- Optional `chronic_conditions`
- Optional `diagnoses`
- Optional `allergies`
- Optional `contraindications`
- Optional `medical_history`
- Optional `vaccine_overrides`
- Optional `care_roles`
- Optional `care_shifts`
- Optional `checklist_items`
- Optional `approval_required_actions`
- Optional `external_calendar_entity_ids`
- Optional passport and veterinary fields
- Optional GPS/BLE/presence/weather/behavior entities
- Optional `safe_zones`
- Optional `room_presence_sources`
- Optional `camera_room_name`
- Optional `camera_entity_id`
- Optional `food_bowl_area`
- Optional `water_bowl_area`

Bowl areas use `x,y,width,height` pixel coordinates.
Avatar values can use `/local/...`, `/media/local/...`, or a full `https://...` URL.

## Routine Planner

Routine configuration is now structured in the UI. No text DSL is required.

Each routine row includes:

- time
- weekdays
- label
- duration
- meal type and portion for feedings
- location for walks/care
- category and notes for care routines

Supported manual modes:

- `normal`
- `vacation`
- `illness`

Automatic adaptive modes:

- `heat`
- `winter`
- `home_alone`

Routine exceptions are one-off date-bound overrides with three actions:

- `skip`
- `add`
- `move`

Examples:

- Move a walk from `13:00` to `20:30` for a hot day
- Skip a feeding for a fasting day
- Add an extra care event for a specific date

## Nutrition

Nutrition configuration is now structured in the UI.

Food catalog entries support:

- `food_name`
- `food_brand`
- `food_kind`: `main_food`, `treats`, `medical_food`, `supplements`
- `meal_type`
- `kcal_per_gram`
- `notes`

Food transition steps support:

- `transition_date`
- `from_food_name`
- `to_food_name`
- `from_percent`
- `to_percent`
- `notes`

The transition mix must always sum to `100%`.

`diva.feed_pet` can now optionally take:

- `meal_type`
- `food_name`

## Medical Core

Medical settings are configured in a structured section of the pet form.

Medication courses support:

- `medication_name`
- `dose`
- `medication_times`
- `start_date`
- `end_date`
- `medication_route`
- `notes`

Chronic conditions support:

- `condition_name`
- `condition_status`
- `monitor_interval_days`
- `notes`

Structured medical profile also supports:

- `diagnoses`: diagnosis name, status, diagnosed date, notes
- `allergies`: allergen, reaction, notes
- `contraindications`: contraindication, reason, notes
- `medical_history`: dated medical event, category, notes
- `regional_policy`: pragmatic regional overlay label such as `es_general`, `madrid`, `andalucia`, `galicia`, `custom`
- `vaccine_profile`: `auto`, `dog_default`, `spain_dog_default`
- `vet_override`: whether configured vaccine overrides can replace generated default doses

Vaccination defaults:

- Dogs use a default protocol derived from WSAVA 2024 core guidance
- Spain overlays keep rabies on an annual review cadence
- Spain overlays add leptospirosis and leishmaniosis annual review entries
- English/Cocker Spaniel does not get a special core timing rule, but the notes flag Spanish exposure review
- `vaccine_overrides` can add custom reminders or replace default due dates
- `regional_policy` adds regional review notes without hardcoding legal advice into the core template
- `vet_override = false` keeps default generated vaccine doses authoritative even if a matching override exists
- runtime services can complete, reschedule, or cancel vaccine reminders per pet

Medical runtime services:

- `diva.log_medication_dose`
- `diva.log_symptom`
- `diva.start_recovery_plan`
- `diva.complete_vaccine_dose`
- `diva.reschedule_vaccine`
- `diva.cancel_vaccine`
- `diva.log_weight`
- `diva.generate_vet_report`

`diva.log_symptom` can now optionally take:

- `duration_hours`

`diva.generate_vet_report` writes a `txt` or `pdf` report into `/config/diva_reports/` and fires a DIVA event with:

- `report_path`
- `telegram_caption`
- summary fields for automations

Vet appointments:

```text
2026-03-12 14:00|Annual checkup|60|City Vet|vet|Bring passport
2026-06-01 10:00|Vaccination|30|City Vet|vet|Booster shot
```

Format:

```text
YYYY-MM-DD HH:MM|label|duration_minutes|location|category|notes
```

Days can be `daily`, `weekdays`, `weekends`, or comma-separated short names such as `mon,wed,fri`.

## Family Operations

Operations settings are configured in a structured section of the pet form.

Operations profile objects support:

- `care_roles`
- `care_shifts`
- `checklist_items`
- `approval_required_actions`

Checklist items can be daily or weekly and may be marked as approval-required per item.

Approval-aware runtime services:

- `diva.complete_checklist_item`
- `diva.approve_action`
- `diva.generate_operations_report`

If an action is configured as approval-required, DIVA does not execute it immediately.
Instead it creates a queued approval record, fires an `approval_requested` event, and waits for `diva.approve_action`.

`diva.generate_operations_report` writes a `txt` or `pdf` report into `/config/diva_reports/` and fires a DIVA event with:

- `report_path`
- `telegram_caption`
- checklist and approval summary fields

## Google and Apple Calendar

DIVA creates its own per-pet `calendar` entity for the full routine timeline.

For external calendars:

- Google: use the built-in Home Assistant `Google Calendar` integration
- Apple/iCloud: use the built-in `CalDAV` integration
- Then link the resulting `calendar.*` entities in the DIVA pet profile
- Run `diva.sync_calendar` to push upcoming DIVA events into those linked calendars

DIVA itself does not own OAuth or CalDAV credentials. It reuses Home Assistant calendar entities as the sync target.

Each linked calendar now has a `source_of_truth` policy:

- `diva`
- `calendar`
- `manual_review`

The sync is now reconcile-based and bidirectional:

- create missing DIVA events
- update changed DIVA events when the target calendar supports `UPDATE_EVENT`
- delete stale DIVA events when the target calendar supports `DELETE_EVENT`
- import external edits back into DIVA as stable timeline overrides when the calendar is the source of truth
- record conflicts instead of auto-merging when the policy is `manual_review`
- fall back safely when a calendar backend is create-only

Imported calendar overrides are applied on top of the DIVA timeline as one-off replacements, skips, or custom imported events. This keeps recurring routines stable while still allowing external calendar edits to round-trip back into DIVA.

## Deferred UX

The current avatar field accepts a path or URL and exposes it as `entity_picture`.

Planned for a future iteration:

- A post-setup pet avatar editor in the DIVA options flow
- Media-browser based image selection
- Preview before saving
- Optional crop support in a dedicated frontend editor

## Entities

Each pet appears as a Home Assistant device.
The DIVA hub is registered as a service device and each pet device is attached through it.

Sensors:

- `sensor.<pet>_food_today`
- `sensor.<pet>_calories_consumed_today`
- `sensor.<pet>_water_today`
- `sensor.<pet>_weight`
- `sensor.<pet>_weight_trend`
- `sensor.<pet>_last_feeding`
- `sensor.<pet>_next_feeding`
- `sensor.<pet>_next_walk`
- `sensor.<pet>_walk_distance`
- `sensor.<pet>_next_medication`
- `sensor.<pet>_next_vet_visit`
- `sensor.<pet>_next_vaccine`
- `sensor.<pet>_vaccine_status`
- `sensor.<pet>_last_seen_eating`
- `sensor.<pet>_activity_level`
- `sensor.<pet>_sleep_duration`
- `sensor.<pet>_sleep_quality`
- `sensor.<pet>_stress_score`
- `sensor.<pet>_inactivity_duration`
- `sensor.<pet>_separation_score`
- `sensor.<pet>_feeding_quality_score`
- `sensor.<pet>_baseline_drift`
- `sensor.<pet>_behavior_profile`
- `sensor.<pet>_health_score`
- `sensor.<pet>_active_medications`
- `sensor.<pet>_recovery_status`
- `sensor.<pet>_body_condition_score`
- `sensor.<pet>_symptom_severity`
- `sensor.<pet>_recommended_food_portion`
- `sensor.<pet>_daily_timeline`
- `sensor.<pet>_current_shift`
- `sensor.<pet>_checklist_progress`
- `sensor.<pet>_pending_approvals`
- `sensor.<pet>_today_vs_baseline`
- `sensor.<pet>_weekly_summary`
- `sensor.<pet>_operations_center`
- `sensor.<pet>_current_zone`
- `sensor.<pet>_current_room`
- `sensor.<pet>_room_heatmap`

Device trackers:

- `device_tracker.<pet>_location`

Binary sensors:

- `binary_sensor.<pet>_hungry`
- `binary_sensor.<pet>_needs_walk`
- `binary_sensor.<pet>_food_bowl_empty`
- `binary_sensor.<pet>_water_bowl_empty`
- `binary_sensor.<pet>_sleeping`
- `binary_sensor.<pet>_home_alone`
- `binary_sensor.<pet>_geofence_breached`
- `binary_sensor.<pet>_anomaly_detected`

Buttons:

- `button.<pet>_feed_now`
- `button.<pet>_refill_food`
- `button.<pet>_refill_water`
- `button.<pet>_start_walk`
- `button.<pet>_finish_walk`
- `button.<pet>_generate_operations_report`

Numbers:

- `number.<pet>_food_portion`
- `number.<pet>_daily_calories`
- `number.<pet>_weight_goal_min`
- `number.<pet>_weight_goal_max`

Select:

- `select.<pet>_diet_mode`
- `select.<pet>_operation_mode`

Camera:

- `camera.<pet>_bowl_monitor`

Calendar:

- `calendar.<pet>_timeline`

## Events

DIVA publishes these Home Assistant events:

- `diva_event`
- `diva_anomaly`
- `diva_recommendation`

Event payloads always include at least:

```yaml
pet: don_abrikos_a1b2c3
pet_name: Don Abrikos
timestamp: "2026-03-09T08:30:00+00:00"
```

Additional runtime events now include schedule and journal flows such as:

- `food_served`
- `food_eaten`
- `routine_due`
- `vet_appointment_due`
- `care_action_logged`
- `behavior_reported`
- `calendar_synced`
- `approval_requested`
- `action_approved`
- `checklist_completed`
- `operations_report_generated`

## Services

- `diva.feed_pet`
- `diva.skip_feeding`
- `diva.delay_feeding`
- `diva.start_walk`
- `diva.finish_walk`
- `diva.sync_calendar`
- `diva.log_care_action`
- `diva.log_medication_dose`
- `diva.log_symptom`
- `diva.report_behavior`
- `diva.observe_behavior`
- `diva.complete_checklist_item`
- `diva.approve_action`
- `diva.apply_mode`
- `diva.start_recovery_plan`
- `diva.complete_vaccine_dose`
- `diva.upsert_vaccine_override`
- `diva.remove_vaccine_override`
- `diva.reschedule_vaccine`
- `diva.cancel_vaccine`
- `diva.upsert_medication_course`
- `diva.remove_medication_course`
- `diva.log_weight`
- `diva.generate_vet_report`
- `diva.generate_operations_report`
- `diva.add_schedule_exception`

`diva.feed_pet` accepts optional nutrition overrides:

- `portion`
- `meal_type`
- `food_name`

Target by `device_id` or `pet_id`.
If there is only one pet in the hub, target is optional.

## Telegram Handoff Example

```yaml
automation:
  - alias: Send DIVA vet report to Telegram
    trigger:
      - platform: event
        event_type: diva_event
        event_data:
          event: vet_report_generated
    action:
      - action: telegram_bot.send_document
        data:
          file: "{{ trigger.event.data.report_path }}"
          caption: "{{ trigger.event.data.telegram_caption }}"
```

## Herald Example

```yaml
automation:
  - alias: Herald DIVA recommendation
    trigger:
      - platform: event
        event_type: diva_recommendation
    action:
      - action: herald.notify
        data:
          title: "Pet recommendation"
          message: "{{ trigger.event.data.pet_name }}: {{ trigger.event.data.recommendation }}"
          level: warning
```

## Calendar Sync Example

```yaml
action:
  - action: diva.sync_calendar
    target:
      entity_id: calendar.don_abrikos_timeline
    data:
      pet_id: don_abrikos_a1b2c3
      days: 14
```

## Lovelace Example

A ready example card is available in [`examples/lovelace_pet_card.yaml`](./examples/lovelace_pet_card.yaml).
The per-pet DIVA timeline calendar can also be shown directly on a Calendar card for a full day agenda.

A fuller built-in dashboard example is available in [`examples/lovelace_dashboard.yaml`](./examples/lovelace_dashboard.yaml).
A dedicated walk map stack is available in [`examples/lovelace_walk_map.yaml`](./examples/lovelace_walk_map.yaml).
A dedicated room heatmap stack is available in [`examples/lovelace_room_heatmap.yaml`](./examples/lovelace_room_heatmap.yaml).
It covers:

- daily control
- timeline calendar
- medical status
- mobility and behavior
- operations center
- calendar sync health
- walk map via `device_tracker.<pet>_location`

Use it as a YAML dashboard or copy individual cards into an existing dashboard.

## Editor Panel

DIVA auto-registers a dedicated sidebar panel at `/diva-editor`.

The panel is served directly from the integration and does not require:

- `panel_custom`
- a separate frontend build pipeline
- copying assets into `/www`

Current panel coverage:

- medication course create, edit, remove
- medication dose logging
- vaccine complete, reschedule, cancel
- vaccine override create, edit, remove
- manual calendar sync
- vet and operations report export

Sidebar visibility is configurable from `Settings -> Devices & Services -> DIVA -> Configure -> Hub settings`.
When hidden, the editor route still exists at `/diva-editor`.

For editable UI workflows, a helper + script workbench is available:

- package: [`examples/ui_workbench_package.yaml`](./examples/ui_workbench_package.yaml)
- Lovelace view: [`examples/lovelace_editor_workbench.yaml`](./examples/lovelace_editor_workbench.yaml)

This workbench remains the Home Assistant-native fallback UI for:

- completing, rescheduling, and cancelling vaccines
- logging medication doses
- exporting vet and operations reports
- triggering calendar sync

It is useful if you prefer native helpers and scripts over the custom DIVA editor panel.

## Limitations

- External calendar reconcile depends on feature support of the selected calendar backend. Some calendars are create-only.
- DIVA-managed external events are identified by a sync marker added to the event description.

## Diagnostics

Diagnostics include:

- Hub settings
- JSON storage backend and file path
- Per-pet configuration
- Entity state snapshots
- Timeline and journal data
- Camera settings and recent analysis
- Recent DIVA notices per pet
- Runtime metrics per pet

## Testing

Pure logic tests are provided under `tests/custom_components/diva` for:

- Feeding logic
- Event payload generation
- Recommendation generation
- Camera detection heuristics
- Schedule parsing and behavior reporting

Home Assistant integration test scaffolding is provided under `tests_integration/custom_components/diva`.

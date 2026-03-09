# DIVA - Guardián de Mascotas

Documentación original en inglés: [README.md](./README.md)

DIVA es una integración personalizada de Home Assistant para gestionar el cuidado de mascotas.
Modela el sistema como un único hub DIVA con varias mascotas y publica:

- entidades de Home Assistant
- eventos
- anomalías
- recomendaciones
- un calendario de rutina por mascota

DIVA no envía notificaciones directamente.
Las notificaciones deben implementarse mediante automatizaciones de Home Assistant, Herald, Telegram u otras integraciones.

## Arquitectura

- implementación async-first
- `DataUpdateCoordinator`
- un único hub `diva` con varias mascotas
- modelo event-driven
- almacenamiento JSON en `/config/diva_runtime.json`
- análisis opcional de cuencos por cámara
- sincronización opcional con entidades externas `calendar.*`

## Funciones principales

- seguimiento de comida, agua, paseos, sueño y actividad
- weekly planner estructurado en `config_flow` y `options_flow`
- varios tipos de comida: `dry`, `wet`, `treat`, `medication`, `supplement`
- catálogo de alimentos y plan de transición entre alimentos
- medical core: medicación, síntomas, recovery plan y chronic conditions
- workflow de vacunas: completar, reprogramar, cancelar y overrides
- objetivos de peso y análisis de tendencia
- `calendar` de línea temporal por mascota
- vet appointments y sincronización bidireccional con calendarios
- pasaporte de la mascota: número, microchip, seguro y datos del veterinario
- GPS/BLE tracking, safe zones y room presence
- ingestión de behavior signals desde fuentes externas de AI/vision
- family operations: roles, turnos, checklist, approvals e informes
- custom editor panel en `/diva-editor`

## Instalación

1. Copia `custom_components/diva` en la configuración de Home Assistant.
2. Reinicia Home Assistant.
3. Añade la integración `DIVA` desde `Settings -> Devices & Services`.
4. Crea el primer perfil de mascota.
5. Añade más mascotas desde `Configure` / `Options`.

## Almacenamiento

DIVA guarda sus datos de runtime en `/config/diva_runtime.json`.
Se almacenan:

- configuración del hub
- perfiles de mascotas
- snapshots
- journal entries
- estado de calendar sync
- recent notices
- camera metadata

## Arquitectura

DIVA ahora usa una configuración versionada con `pet_schema = 3`.

Cada registro de mascota se guarda en secciones explícitas:

- `profile`
- `plan`
- `medical`
- `analytics`
- `external_links`

El runtime JSON también guarda `runtime_sections` tipadas para:

- `medical`
- `mobility`
- `behavior`
- `operations`
- `reports`

En la capa de dominio, `PetEngine` ahora expone límites claros de sub-engine:

- `routines`
- `nutrition`
- `medical`
- `mobility`
- `behavior`
- `reporting`

## Modelo de configuración de la mascota

Campos obligatorios:

- `name`
- `species`
- `breed`
- `birthdate`
- `weight`
- `diet_mode`

Grupos opcionales:

- avatar
- routines
- nutrition
- medical
- passport
- tracking
- behavior
- operations
- camera

El avatar puede usar:

- `/local/...`
- `/media/local/...`
- `https://...`

## Calendarios

DIVA crea su propia entidad `calendar.<pet>_timeline`.

Para calendarios externos:

- Google: usa la integración nativa `Google Calendar`
- Apple/iCloud: usa `CalDAV`
- vincula las entidades `calendar.*` en el perfil de la mascota
- ejecuta `diva.sync_calendar`

Políticas `source_of_truth` disponibles:

- `diva`
- `calendar`
- `manual_review`

DIVA no gestiona credenciales OAuth o CalDAV por sí sola.
Reutiliza las entidades de calendario ya configuradas en Home Assistant.

## Panel del editor

DIVA registra automáticamente un custom panel en `/diva-editor`.

La cobertura actual del panel incluye:

- create/edit/remove de medication courses
- registro de medication dose
- complete/reschedule/cancel de vacunas
- create/edit/remove de vaccine overrides
- calendar sync manual
- export de vet report y operations report

La visibilidad del enlace en la barra lateral se configura en:

`Settings -> Devices & Services -> DIVA -> Configure -> Hub settings`

Si el enlace del sidebar está oculto, la ruta `/diva-editor` sigue disponible.

## Eventos

Eventos principales:

- `diva_event`
- `diva_anomaly`
- `diva_recommendation`

Nombres de evento habituales:

- `food_served`
- `food_eaten`
- `routine_due`
- `vet_appointment_due`
- `calendar_synced`
- `approval_requested`
- `operations_report_generated`

## Servicios

Servicios runtime básicos:

- `diva.feed_pet`
- `diva.skip_feeding`
- `diva.delay_feeding`
- `diva.start_walk`
- `diva.finish_walk`
- `diva.sync_calendar`
- `diva.apply_mode`
- `diva.add_schedule_exception`

Servicios medical / operations:

- `diva.log_medication_dose`
- `diva.upsert_medication_course`
- `diva.remove_medication_course`
- `diva.log_symptom`
- `diva.start_recovery_plan`
- `diva.complete_vaccine_dose`
- `diva.upsert_vaccine_override`
- `diva.remove_vaccine_override`
- `diva.reschedule_vaccine`
- `diva.cancel_vaccine`
- `diva.log_weight`
- `diva.generate_vet_report`
- `diva.generate_operations_report`
- `diva.complete_checklist_item`
- `diva.approve_action`

El perfil médico ampliado ahora soporta:

- `diagnoses`
- `allergies`
- `contraindications`
- `medical_history`
- `regional_policy`
- `vaccine_profile`
- `vet_override`

`diva.log_symptom` también acepta el parámetro opcional `duration_hours`.

## Ejemplos

Automatizaciones:

- [automations.yaml](./examples/automations.yaml)
- [automations.ru.yaml](./examples/automations.ru.yaml)
- [automations.es.yaml](./examples/automations.es.yaml)

Documentación de calendar workflows:

- [calendar_sync_workflows.en.md](./examples/calendar_sync_workflows.en.md)
- [calendar_sync_workflows.ru.md](./examples/calendar_sync_workflows.ru.md)
- [calendar_sync_workflows.es.md](./examples/calendar_sync_workflows.es.md)

Ejemplos de Lovelace:

- [lovelace_pet_card.yaml](./examples/lovelace_pet_card.yaml)
- [lovelace_dashboard.yaml](./examples/lovelace_dashboard.yaml)
- [lovelace_walk_map.yaml](./examples/lovelace_walk_map.yaml)
- [lovelace_room_heatmap.yaml](./examples/lovelace_room_heatmap.yaml)
- [lovelace_editor_workbench.yaml](./examples/lovelace_editor_workbench.yaml)
- [ui_workbench_package.yaml](./examples/ui_workbench_package.yaml)

## Diagnóstico

Diagnostics incluye:

- configuración de mascotas
- snapshots
- ajustes de cámara
- eventos recientes
- ruta del storage backend

## Limitaciones

- calendar reconcile depende del backend de calendario seleccionado
- algunos backends solo soportan create-only
- el análisis de cuencos por cámara es heurístico y depende de una calibración correcta
- los medical defaults no sustituyen el criterio del veterinario

## Pruebas

Se mantiene:

- unit tests en `tests/custom_components/diva`
- integration scaffolding en `tests_integration/custom_components/diva`

Smoke test recomendado en runtime:

1. crear una mascota
2. comprobar entidades y device registry
3. ejecutar `feed_now`, `start_walk`, `sync_calendar`
4. abrir `/diva-editor`
5. verificar eventos `diva_event`, `diva_anomaly`, `diva_recommendation`

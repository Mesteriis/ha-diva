# DIVA Implementation Plan

## Цель

Подготовить поэтапное внедрение следующего функционала в DIVA:

- адаптивный распорядок и weekly planner
- исключения из расписания, отпуск, болезнь, жара, зима, режим "дома один"
- расширенная логика кормления и учета рациона
- лекарства, прививки, веткарта, симптомы, восстановление, хронические состояния
- весовой тренд, BCS, PDF vet-pack
- прогулки, геозоны, побег, BLE-локализация, карта привычек
- поведенческая аналитика, vision/AI, stress/anomaly/baseline
- family roles, журналы, подтверждение действий, чек-листы, отчеты
- двусторонняя календарная интеграция

## Базовые принципы

- DIVA не отправляет уведомления напрямую.
- Telegram, e-mail, mobile push и другие каналы идут через штатные интеграции Home Assistant и automations.
- Погода берется из Home Assistant по привязанной сущности. Поддержать нужно оба пути:
  - `weather.*`
  - числовой `sensor.*` с температурой и погодными атрибутами
- Внешние календари идут через Home Assistant calendar entities:
  - Google Calendar
  - CalDAV / Apple Calendar
- Любой медико-ветеринарный шаблон должен быть editable и override-able пользователем или ветеринаром.

## Важное допущение по прививкам

### Что подтверждают источники

1. По WSAVA 2024 базовые core-вакцины для собак глобально: CDV, CAV, CPV.
2. Rabies считается core там, где заболевание эндемично или этого требует региональный контекст/закон.
3. Leptospirosis для собак должна считаться core в регионах, где она эндемична, известны значимые серогруппы и доступны подходящие вакцины.
4. В Испании веторганизации подчеркивают важность antirabies vaccination, а также профилактики leptospirosis и leishmaniosis.
5. Leishmaniosis в Испании эндемична, поэтому в DIVA нужен не только календарь вакцинации, но и круглогодичный preventive plan.

### Что является выводом, а не прямой нормой из источника

- Я не нашел авторитетного источника, который задавал бы отдельный породный календарь прививок именно для кокер-спаниеля.
- Вывод: для `Cocker Spaniel + Spain` в DIVA должен использоваться `dog-in-Spain default template`, а не отдельный breed-specific mandatory schedule.
- Породная специфика для кокера должна проявляться прежде всего в health overlays:
  - уши
  - кожа
  - глаза
  - контроль веса
  - активность и стресс

## Рекомендуемый Spain dog vaccine template для DIVA

### Базовый шаблон по умолчанию

#### Puppy core series

- старт core-вакцин: не раньше `6 weeks`
- ревакцинация каждые `3-4 weeks`
- базовый финиш серии: `16 weeks`
- high-risk option: продолжать до `20 weeks`
- дополнительная core-точка: `26+ weeks`
- далее: повтор по продукту и плану врача, обычно с long-term core scheduling

#### Rabies

- включать в Spain template по умолчанию
- при этом хранить отдельный региональный policy layer, потому что правоприменение в Испании меняется по автономным сообществам
- DIVA не должна хардкодить единый юридический срок без регионального override

#### Leptospirosis

- включить в Spain default как `recommended/high-priority non-core or regional-core template`
- повторять по product/vet policy, обычно annual cycle

#### Leishmaniosis

- добавить как Spain endemic prevention program
- не только вакцина, но и:
  - repellents
  - seasonality tracking
  - travel risk
  - reminders на тесты/контроль

#### Kennel cough / social exposure package

- опциональный пакет для:
  - daycare
  - kennel
  - grooming
  - exhibitions
  - active social dogs

### Как это должно выглядеть в DIVA

- `vaccine_profile: spain_dog_default`
- `regional_policy: andalucia | cataluna | madrid | custom`
- `breed_overlay: english_cocker_spaniel`
- `vet_override: enabled`

## Источники для vaccine policy

- WSAVA 2024 Vaccination Guidelines:
  - https://wsava.org/wp-content/uploads/2024/04/WSAVA-Vaccination-guidelines-2024.pdf
- WSAVA Vaccination Guidelines portal:
  - https://wsava.org/Global-Guidelines/Vaccination-Guidelines/
- OCV Spain on rabies vaccination:
  - https://www.colvet.es/es/23-Prensa/43-Comunicados/49-El-Consejo-General-de-Colegios-Veterinarios-recomienda-la-vacunacion-anual-y-obligatoria-contra-la-rabia.htm
- OCV note on Spain regional rabies inconsistency:
  - https://www.colvet.es/index.php?buscarfecha1=01-01-2024&buscarfecha2=29-01-2024&buscaridseccion=&buscaridsubseccion=&buscartexto=&id=0&idioma=es&menu=1&opcion=2
- OCV on canine leishmaniosis endemicity in Spain:
  - https://www.colvet.es/es/1-Noticias-actualidad/18987-La-OCV-advierte-de-las-consecuencias-graves-de-la-leishmaniosis-una-zoonosis-desatendida-a-pesar-de-ser-endemica-en-Espana-.htm
- OCV / European approval note for canine leishmaniosis vaccine:
  - https://www.colvet.es/es/1-Noticias-actualidad/16408-La-CE-autoriza-una-vacuna-espanola-contra-la-leishmaniosis-canina.htm

## Архитектурные требования перед стартом

### Data model

- [x] ввести versioned pet schema `v3`
- [x] разделить `profile`, `plan`, `runtime`, `medical`, `analytics`, `external_links`
- [ ] вынести routine exceptions в отдельную структуру
- [x] добавить typed storage для vaccines, meds, symptoms, GPS/BLE, reports, approvals
- [x] добавить compatibility migration `v2 -> v3`

### Coordinator/runtime

- [x] ввести отдельные sub-engines:
  - `RoutineEngine`
  - `NutritionEngine`
  - `MedicalEngine`
  - `MobilityEngine`
  - `BehaviorEngine`
  - `ReportingEngine`
- [ ] тяжелую аналитику выносить из event loop
- [x] для external vision/AI ingest использовать capability adapters, а не hardcoded pipelines
  - `observe_behavior` принимает adapter-ready payloads и Frigate metadata

### Storage

- [x] оставить JSON root storage как основной backend
- [ ] подготовить optional SQLite backend для history-heavy функций
- [ ] в SQLite унести:
  - timeline history
  - symptoms
  - walks
  - GPS points
  - BLE room presence
  - vision detections
  - reports/PDF exports metadata

## Этапы внедрения

## Phase 1: Routine 2.0

Фичи:
- `1, 2, 3, 4, 5, 6, 7, 8`

### Deliverables

- adaptive routine engine
- weekly planner UI
- exceptions engine
- режимы `vacation`, `illness`, `heat`, `winter`, `home_alone`
- weather ingestion from HA entity/sensor

### Checklist

- [ ] заменить multiline routine editor на structured weekly planner
- [ ] добавить schedule exceptions table
- [ ] добавить special modes per pet
- [ ] сделать rule engine для automatic schedule shift
- [ ] добавить weather resolver для `weather.*` и `sensor.*`
- [ ] ввести risk policies для жары и холода
- [ ] добавить occupancy logic для режима `home_alone`
- [ ] обновить calendar timeline под modes/exceptions

### Acceptance

- [ ] пользователь может задать прогулку `09:00`, кормление `09:30` через UI без текстового DSL
- [ ] исключение на конкретную дату корректно меняет timeline
- [ ] при высокой температуре DIVA сдвигает или маркирует дневную прогулку как heat-risk
- [ ] при отсутствии людей дома включается `home_alone` режим и меняются рекомендации

## Phase 2: Nutrition Intelligence

Фичи:
- `10, 11, 12, 13`

### Deliverables

- brand/food transition tracking
- treats accounting
- served vs eaten reconciliation
- feeding quality scoring

### Checklist

- [ ] добавить `food_catalog` и `food_transition_plan`
- [ ] разделить `main_food`, `treats`, `medical_food`, `supplements`
- [ ] добавить ingest рейтинга приема пищи
- [ ] добавить `feeding_quality_score`
- [ ] связать smart feeder и bowl/camera confirmations
- [ ] пересчитать calories с учетом treats

### Acceptance

- [ ] DIVA отличает dry/wet/treat/medical intake
- [ ] видно сколько выдано, сколько реально съедено, сколько проигнорировано
- [ ] transition между кормами отображается в timeline и recommendations

## Phase 3: Medical Core

Фичи:
- `17, 18, 19, 20, 21, 22, 23, 24, 25`

### Deliverables

- meds and courses
- default Spain vaccine template
- vet card / chronic conditions
- symptoms timeline
- recovery plans
- body condition and weight trend
- PDF vet-pack export
- Telegram delivery through HA

### Checklist

- [x] добавить `medications`, `courses`, `dose_schedule`
- [x] добавить `vaccination_profiles` с `spain_dog_default`
- [x] добавить `regional_policy` и `vet_override`
- [x] сделать vaccine generator по возрасту, виду, локации
- [x] добавить medical history / allergies / contraindications / diagnoses
- [x] добавить symptom logging with severity and duration
- [x] добавить recovery programs после болезни/операции
- [x] добавить chronic monitoring templates
- [ ] добавить weight trend chart + goal range
- [x] добавить BCS manual scoring
- [x] реализовать PDF export job
- [x] сделать HA action path для Telegram:
  - generate report package in DIVA
  - fire event / expose file path
  - HA automation -> `notify.telegram` / Telegram bot integration

### Acceptance

- [ ] для puppy в Spain создается editable vaccine plan
- [x] пользователь может подтвердить/перенести/отменить прививку
- [x] PDF vet-pack содержит историю веса, симптомы, medications, vaccines, key anomalies
- [x] Telegram отправка делается через HA automation, а не напрямую из DIVA

## Phase 4: Mobility, GPS, BLE, Geofencing

Фичи:
- `26, 27, 28, 29, 30, 31, 32`

### Deliverables

- walk distance/time/route
- geofences
- escape detection
- BLE + camera assisted indoor localization
- heatmap and preferred/avoided zones
- separation analytics

### Checklist

- [x] ввести GPS point storage
- [x] добавить geofence model and events
- [x] реализовать escape policy engine
- [x] привязать BLE room presence entities
- [x] объединить BLE + camera detections в room resolver
- [x] строить habit map по комнатам/зонам
- [x] считать time-spent by room
- [x] добавить separation analytics when humans away

### Acceptance

- [x] прогулка имеет duration, distance и route summary
- [x] уход за границы safe zone вызывает anomaly/event
- [x] DIVA умеет показать комнаты, где питомец бывает чаще всего

## Phase 5: Vision, Behavior, AI

Фичи:
- `33, 34, 35, 36, 37, 38, 39, 40`

### Deliverables

- gait/vomit/cough/restlessness detectors
- long inactivity detector
- sleep quality analytics
- stress model v2
- hourly/weekly/seasonal baseline
- AI behavior profile
- subtle anomaly engine

### Checklist

- [x] определить external detector contract for vision pipelines
- [x] добавить `behavior_observation` schema
- [x] реализовать temporal anomaly scoring
- [x] сделать sleep quality model
- [x] расширить baseline до hour-of-day и weekday profiles
- [x] сделать AI profile labels from features
- [x] ввести explainable anomaly reasons
- [x] подготовить plug points для future YOLO / CV / ML backends

### Acceptance

- [x] DIVA не просто пишет `stress_score`, а объясняет факторы
- [x] subtle anomaly может подняться до явной клинической проблемы
- [x] каждое AI-наблюдение имеет provenance: manual / BLE / camera / external model

## Phase 6: Family Ops and Daily Control

Фичи:
- `41, 42, 43, 44, 45, 46, 47, 48, 49`

### Deliverables

- day timeline center
- family roles
- action approval workflow
- care shifts
- daily/weekly checklists
- reports and dashboards
- comparison with baseline day
- operations center view

### Checklist

- [x] сделать dedicated Lovelace dashboard package
- [x] добавить `care_roles` and `care_shifts`
- [x] добавить required confirmation for critical actions
- [x] добавить checklist engine
- [x] weekly summary entity + PDF report
- [x] comparator `today vs normal day`
- [x] action audit log with actor and source
- [x] add dashboard cards for timeline / medical / mobility / behavior

### Acceptance

- [x] понятно кто что сделал и когда
- [x] критические действия нельзя считать завершенными без подтверждения
- [x] dashboard закрывает operational use-case без ухода в diagnostics

## Phase 7: Calendar Bi-Directional Sync

Фичи:
- `50`

### Deliverables

- import external edits back into DIVA
- conflict resolution rules
- round-trip stable IDs

### Checklist

- [x] добавить `source_of_truth` policy per calendar
- [x] добавить inbound polling/webhook sync
- [x] map external event IDs to DIVA objects
- [x] реализовать conflict states:
  - DIVA wins
  - calendar wins
  - manual review
- [x] логировать origin and last_sync_state
- [x] добавить safe merge for recurring schedules and single exceptions

### Acceptance

- [x] изменение события в linked calendar может корректно попасть обратно в DIVA
- [x] нет дублей и loop-updates

## UI backlog

Статус:
- built-in helper + script workbench добавлен для vaccine, medication, report и sync workflows
- custom sidebar panel `/diva-editor` добавлен для medical, report и calendar workflows

- [x] Routine planner card
- [x] vaccine calendar editor
- [x] medication course editor
- [x] symptom timeline card
- [x] walk map card
- [x] room heatmap card
- [x] family operations center
- [x] report export dialog
- [x] conflict resolution dialog for calendar sync

## Entities / services backlog

### New entities

- [x] `sensor.<pet>_weight_trend`
- [x] `sensor.<pet>_body_condition_score`
- [x] `sensor.<pet>_separation_risk`
- [x] `sensor.<pet>_room_preference`
- [x] `sensor.<pet>_walk_distance_today`
- [x] `sensor.<pet>_symptom_burden`
- [x] `sensor.<pet>_recovery_progress`
- [x] `sensor.<pet>_vaccine_status`
- [x] `sensor.<pet>_checklist_completion`

### New services

- [x] `diva.apply_mode`
- [x] `diva.add_schedule_exception`
- [x] `diva.log_symptom`
- [x] `diva.approve_action`
- [x] `diva.start_recovery_plan`
- [x] `diva.generate_vet_report`
- [x] PDF export через `generate_vet_report` / `generate_operations_report` с `report_format: pdf`
- [x] `diva.sync_calendar` как bidirectional sync entry point
- [x] service hardening: validation for date/time payloads, deduplicated device targets, approvals stay pending on execution failure

## Testing strategy

### Unit tests

- [x] routine exception resolution
- [x] adaptive schedule shifts
- [x] vaccine template generation for Spain
- [x] weather policy engine
- [x] medication course logic
- [x] weight trend and BCS scoring
- [x] geofence breach logic
- [x] BLE+camera fusion logic
- [x] subtle anomaly scoring
- [x] calendar conflict resolution

### Integration tests

- [x] config flow with all new sections
- [x] entity creation for medical/mobility/reporting
- [x] HA calendar sync create/update/delete/import
- [x] unit coverage for calendar sync lifecycle create/update/delete/import
- [x] scenario runtime validation harness for one adult dog with GPS + BLE + camera
- [x] Telegram handoff via HA automation path
- [x] PDF generation job lifecycle
- [x] storage migration `v2 -> v3`

### Live validation

- [ ] one puppy dog profile in Spain
- [ ] one adult dog with GPS + BLE + camera
- [ ] one Frigate MQTT / tracked object pipeline
- [ ] one household with multiple caregivers
- [ ] one linked Google calendar
- [ ] one linked CalDAV calendar

## Риски

- [ ] medical defaults могут конфликтовать с product-specific vaccine labels
- [ ] legal rabies policy differs across autonomous communities
- [ ] BLE room detection quality сильно зависит от home setup
- [ ] camera-based gait/vomit detection без размеченных данных даст много false positives
- [ ] bidirectional calendar sync без strict IDs приводит к event loops
- [ ] PDF export + media delivery потребуют надежного file lifecycle management

## Порядок внедрения

### Sprint order

1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 6
6. Phase 5
7. Phase 7

### Почему именно так

- сначала нужен удобный operational backbone
- потом nutrition and medical core
- затем mobility and family operations
- только потом heavy AI/vision and bidirectional calendar import

## Definition of Done для всего roadmap

- [ ] все новые функции имеют typed storage и diagnostics coverage
- [ ] все critical flows покрыты unit + integration tests
- [ ] no blocking operations in runtime path
- [ ] все внешние эффекты идут через HA entities/events/services
- [x] пользователь может реально управлять питомцем из Lovelace без ручного редактирования JSON
- [ ] medical/vaccine templates editable и не выдают себя за прямую замену назначения ветеринара

## Локализация

### Целевые языки

- [x] `ru` как основной язык проекта
- [x] `en` как обязательный международный fallback
- [x] `es` как обязательный язык для Spain-centric сценариев

### Что должно быть переведено

- [x] `translations/ru.json`
- [x] `translations/en.json`
- [x] `translations/es.json`
- [x] названия шагов `config_flow` и `options_flow`
- [x] labels, descriptions, placeholders и error messages
- [x] названия режимов, schedule actions, care actions и medical actions
- [x] service descriptions для UI сервисов
- [x] onboarding/help тексты в `README.md`
- [x] примеры automations и calendar workflows

### Правила локализации

- [ ] `ru` считается source-of-truth для product wording
- [ ] `en` должен быть технически точным и нейтральным
- [ ] `es` должен использовать понятные формулировки для пользователей в Испании
- [ ] medical/vaccine terminology должна проверяться отдельно, без буквального машинного перевода
- [ ] все новые фичи не считаются завершенными без обновления трех языков

### Acceptance

- [x] пользователь может пройти setup flow целиком на `ru`, `en` и `es`
- [x] ошибки, сервисы и режимы отображаются корректно на всех трех языках
- [x] документация по ключевым сценариям доступна минимум на `ru`, `en`, `es`

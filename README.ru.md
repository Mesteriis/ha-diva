# DIVA - Защитник питомцев

Оригинальная английская документация: [README.md](./README.md)

DIVA — это кастомная интеграция Home Assistant для управления уходом за питомцами.
Она моделирует систему как один DIVA hub с несколькими питомцами внутри и публикует:

- сущности Home Assistant
- события
- аномалии
- рекомендации
- календарь распорядка по каждому питомцу

DIVA не отправляет уведомления напрямую.
Все внешние уведомления должны строиться через Home Assistant automations, Herald, Telegram и другие интеграции.

## Архитектура

- async-first реализация
- `DataUpdateCoordinator`
- один hub `diva` с несколькими питомцами
- event-driven модель
- runtime JSON-хранилище в `/config/diva_runtime.json`
- опциональная camera-аналитика мисок
- опциональная синхронизация с внешними `calendar.*`

## Основные возможности

- учет кормления, воды, прогулок, сна и активности
- структурированный weekly planner в `config_flow` и `options_flow`
- несколько типов кормления: `dry`, `wet`, `treat`, `medication`, `supplement`
- каталог кормов и план перехода между кормами
- medical core: лекарства, симптомы, recovery plan, chronic conditions
- vaccine workflow: complete, reschedule, cancel, overrides
- weight goals и trend analytics
- per-pet timeline calendar
- vet appointments и bidirectional calendar sync
- паспорт питомца: паспорт, чип, страховка, ветеринар
- GPS/BLE tracking, safe zones, room presence
- импорт behavior signals из внешних AI/vision источников
- family operations: роли, смены, checklist, approvals, reports
- custom editor panel `/diva-editor`

## Установка

1. Скопируйте `custom_components/diva` в конфигурацию Home Assistant.
2. Перезапустите Home Assistant.
3. Добавьте интеграцию `DIVA` через `Settings -> Devices & Services`.
4. Создайте первый профиль питомца.
5. Дополнительных питомцев добавляйте через `Configure` / `Options`.

## Хранилище

DIVA сохраняет runtime-данные в `/config/diva_runtime.json`.
Там хранятся:

- профиль hub
- профили питомцев
- snapshots
- журнал действий
- состояние календарной синхронизации
- recent notices
- camera metadata

## Архитектура

DIVA теперь использует versioned config shape с `pet_schema = 3`.

Каждая запись питомца хранится в секциях:

- `profile`
- `plan`
- `medical`
- `analytics`
- `external_links`

Runtime JSON также хранит typed `runtime_sections` для:

- `medical`
- `mobility`
- `behavior`
- `operations`
- `reports`

В доменном слое `PetEngine` теперь отдает явные sub-engine границы:

- `routines`
- `nutrition`
- `medical`
- `mobility`
- `behavior`
- `reporting`

## Модель конфигурации питомца

Обязательные поля:

- `name`
- `species`
- `breed`
- `birthdate`
- `weight`
- `diet_mode`

Опциональные группы:

- avatar
- routines
- nutrition
- medical
- passport
- tracking
- behavior
- operations
- camera

Avatar можно задавать через:

- `/local/...`
- `/media/local/...`
- `https://...`

## Календари

DIVA создает собственную сущность `calendar.<pet>_timeline`.

Для внешних календарей:

- Google: используйте штатную интеграцию `Google Calendar`
- Apple/iCloud: используйте `CalDAV`
- затем свяжите нужные `calendar.*` сущности в профиле питомца
- запустите `diva.sync_calendar`

Поддерживаются политики `source_of_truth`:

- `diva`
- `calendar`
- `manual_review`

DIVA не хранит OAuth или CalDAV credentials самостоятельно.
Она использует уже подключенные в Home Assistant calendar entities.

## Editor Panel

DIVA автоматически регистрирует custom panel по пути `/diva-editor`.

Панель покрывает:

- medication course create/edit/remove
- medication dose logging
- vaccine complete/reschedule/cancel
- vaccine override create/edit/remove
- manual calendar sync
- review и resolution для calendar conflicts
- vet и operations report export
- walk map summary
- room heatmap summary

Видимость ссылки в sidebar настраивается отдельно:

`Settings -> Devices & Services -> DIVA -> Configure -> Hub settings`

Если sidebar entry скрыт, сам маршрут `/diva-editor` продолжает работать.

## События

Основные события:

- `diva_event`
- `diva_anomaly`
- `diva_recommendation`

Типовые event names:

- `food_served`
- `food_eaten`
- `routine_due`
- `vet_appointment_due`
- `calendar_synced`
- `approval_requested`
- `operations_report_generated`

## Сервисы

Базовые runtime services:

- `diva.feed_pet`
- `diva.skip_feeding`
- `diva.delay_feeding`
- `diva.start_walk`
- `diva.finish_walk`
- `diva.sync_calendar`
- `diva.apply_mode`
- `diva.add_schedule_exception`

Medical / operations services:

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

Расширенный медицинский профиль поддерживает:

- `diagnoses`
- `allergies`
- `contraindications`
- `medical_history`
- `regional_policy`
- `vaccine_profile`
- `vet_override`

`diva.log_symptom` также принимает необязательный параметр `duration_hours`.

## Примеры

Automation examples:

- [automations.yaml](./examples/automations.yaml)
- [automations.ru.yaml](./examples/automations.ru.yaml)
- [automations.es.yaml](./examples/automations.es.yaml)

Calendar workflow docs:

- [calendar_sync_workflows.en.md](./examples/calendar_sync_workflows.en.md)
- [calendar_sync_workflows.ru.md](./examples/calendar_sync_workflows.ru.md)
- [calendar_sync_workflows.es.md](./examples/calendar_sync_workflows.es.md)

Lovelace examples:

- [lovelace_pet_card.yaml](./examples/lovelace_pet_card.yaml)
- [lovelace_dashboard.yaml](./examples/lovelace_dashboard.yaml)
- [lovelace_walk_map.yaml](./examples/lovelace_walk_map.yaml)
- [lovelace_room_heatmap.yaml](./examples/lovelace_room_heatmap.yaml)
- [lovelace_editor_workbench.yaml](./examples/lovelace_editor_workbench.yaml)
- [ui_workbench_package.yaml](./examples/ui_workbench_package.yaml)

## Диагностика

Diagnostics включают:

- конфигурацию питомцев
- snapshots
- camera settings
- recent events
- storage backend path

## Ограничения

- calendar reconcile зависит от возможностей выбранного calendar backend
- часть calendar backends поддерживает только create-only сценарий
- camera-анализ мисок эвристический и зависит от корректной калибровки областей
- medical defaults не заменяют рекомендации ветеринара

## Тестирование

Локально поддерживаются:

- unit tests в `tests/custom_components/diva`
- integration scaffolding в `tests_integration/custom_components/diva`

Рекомендуемый live smoke test:

1. создать питомца
2. проверить сущности и device registry
3. выполнить `feed_now`, `start_walk`, `sync_calendar`
4. открыть `/diva-editor`
5. проверить события `diva_event`, `diva_anomaly`, `diva_recommendation`

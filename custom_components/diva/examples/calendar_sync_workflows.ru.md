# Сценарии синхронизации календаря DIVA

## Обзор

DIVA поддерживает собственную сущность `calendar.<pet>_timeline` и умеет синхронизироваться со связанными `calendar.*` сущностями Home Assistant.

Поддерживаемые политики `source_of_truth`:

- `diva`: расписанием владеет DIVA и публикует его наружу
- `calendar`: изменения во внешнем календаре могут попадать обратно в DIVA
- `manual_review`: DIVA фиксирует конфликт и ждет ручного решения

## Базовый сценарий

1. Подключите Google Calendar или CalDAV в Home Assistant.
2. Выберите связанные `calendar.*` сущности в профиле питомца DIVA.
3. Установите `source_of_truth` для каждого календаря.
4. Выполните `diva.sync_calendar`.

## Рекомендуемые автоматизации

### Ночная синхронизация

```yaml
- alias: DIVA Daily Calendar Sync
  trigger:
    - platform: time
      at: "04:00:00"
  action:
    - action: diva.sync_calendar
      data:
        pet_id: don_abrikos_a1b2c3
        days: 14
```

### Контроль конфликтов

Следите за сущностями:

- `sensor.<pet>_calendar_sync`
- `sensor.<pet>_calendar_conflicts`

## Примечания

- Некоторые calendar backends умеют только create-only операции.
- Поддержка update/delete зависит от конкретного backend.
- Импортированные overrides накладываются поверх базового recurring planner и не ломают основной распорядок напрямую.

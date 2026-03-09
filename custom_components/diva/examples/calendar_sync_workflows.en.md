# DIVA Calendar Sync Workflows

## Overview

DIVA maintains its own `calendar.<pet>_timeline` entity and can synchronize with linked Home Assistant `calendar.*` entities.

Supported `source_of_truth` policies:

- `diva`: DIVA owns the schedule and pushes it outward
- `calendar`: external calendar changes can flow back into DIVA
- `manual_review`: DIVA records conflicts and waits for human review

## Basic workflow

1. Add Google Calendar or CalDAV to Home Assistant.
2. Select the linked `calendar.*` entities in the DIVA pet profile.
3. Choose a `source_of_truth` policy per linked calendar.
4. Run `diva.sync_calendar`.

## Recommended automations

### Nightly sync

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

### Review conflicts

Monitor these entities:

- `sensor.<pet>_calendar_sync`
- `sensor.<pet>_calendar_conflicts`

## Notes

- Some calendar backends are create-only.
- Update/delete support depends on the linked backend.
- DIVA keeps imported overrides on top of the recurring routine instead of mutating the base planner directly.

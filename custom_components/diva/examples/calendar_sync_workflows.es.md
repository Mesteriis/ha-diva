# Flujos de sincronización de calendario en DIVA

## Resumen

DIVA mantiene su propia entidad `calendar.<pet>_timeline` y puede sincronizarse con entidades `calendar.*` enlazadas en Home Assistant.

Políticas `source_of_truth` soportadas:

- `diva`: DIVA es dueña del horario y lo publica hacia fuera
- `calendar`: los cambios en el calendario externo pueden volver a DIVA
- `manual_review`: DIVA registra el conflicto y espera revisión manual

## Flujo básico

1. Añade Google Calendar o CalDAV a Home Assistant.
2. Selecciona las entidades `calendar.*` enlazadas en el perfil de la mascota.
3. Elige la política `source_of_truth` para cada calendario enlazado.
4. Ejecuta `diva.sync_calendar`.

## Automatizaciones recomendadas

### Sincronización nocturna

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

### Revisión de conflictos

Supervisa estas entidades:

- `sensor.<pet>_calendar_sync`
- `sensor.<pet>_calendar_conflicts`

## Notas

- Algunos backends de calendario son create-only.
- El soporte de update/delete depende del backend enlazado.
- DIVA aplica los overrides importados sobre la rutina recurrente en lugar de mutar directamente el plan base.

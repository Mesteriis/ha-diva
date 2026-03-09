# Architecture

DIVA uses a versioned `pet_schema = 3` data model.

Each pet record is normalized into explicit sections:

- `profile`
- `plan`
- `medical`
- `analytics`
- `external_links`

Runtime state is persisted to JSON and grouped into typed sections:

- `medical`
- `mobility`
- `behavior`
- `operations`
- `reports`

The domain layer exposes explicit sub-engine boundaries inside `PetEngine`:

- `routines`
- `nutrition`
- `medical`
- `mobility`
- `behavior`
- `reporting`

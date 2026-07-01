# Phase 01: Players Foundation

## Purpose

Create the shared `players` app and canonical player identity foundation used by Analytics and future VCB systems.

`players.Player` is the canonical future player identity model. It should not depend on legacy `pdp.PlayerProfile`. Existing PDP player data is relevant only for coexistence, migration planning, or temporary bridge logic if explicitly required.

## Architecture References

- [02 Players](../architecture/02_players.md)
- [04 Imports](../architecture/04_imports.md)
- [09 Services](../architecture/09_services.md)
- [10 Permissions](../architecture/10_permissions.md)

## Existing Project Integration

Before implementing this phase, inspect relevant existing project conventions, including:

- existing app structure
- installed apps and settings conventions
- existing auth/user model usage
- admin configuration patterns
- model timestamp patterns
- service-layer patterns
- test organization and fixtures

## Scope

- Create the `players` Django app.
- Add canonical player identity models.
- Add source identifiers, aliases, source rows, and tags.
- Add basic player identity, matching, import, and tag service modules as scaffolding.
- Add admin configuration for player identity management.
- Add tests for player model behavior and matching service basics.
- Ensure the Phase 1 design does not make `players.Player` dependent on `pdp.PlayerProfile`.

## Out of Scope

- Analytics observations.
- Coach assessment workflow.
- CSV upload UI.
- Import preview and merge UI.
- Player Profile page.
- Timeline.
- Draft context display.
- Reporting.
- Migrating PDP workflows from `pdp.PlayerProfile` to `players.Player` unless explicitly instructed.
- Designing `players.Player` as an extension of `pdp.PlayerProfile`.
- Measurements, Watch Lists, attachments, AI, parent/player portals.

## Deliverables

- [ ] `players` app added to `INSTALLED_APPS`.
- [ ] `players.Player` model.
- [ ] `players.PlayerAlias` model.
- [ ] `players.PlayerSourceIdentifier` model.
- [ ] `players.PlayerSourceRow` model.
- [ ] `players.PlayerTag` model.
- [ ] `players/services/identity_service.py`.
- [ ] `players/services/matching_service.py`.
- [ ] `players/services/import_service.py` scaffolding.
- [ ] `players/services/tag_service.py`.
- [ ] Admin registrations.
- [ ] Focused model and service tests.

## Models

- `Player`
  - first name
  - last name
  - preferred/nickname field
  - birthdate and/or birth year
  - gender
  - team/division context fields
  - safe reporting fields
  - source metadata
  - created/updated timestamps
- `PlayerAlias`
  - player foreign key
  - alias/name value
  - source/context fields
- `PlayerSourceIdentifier`
  - player foreign key
  - source name/type
  - identifier key/value
- `PlayerSourceRow`
  - player foreign key
  - source filename/import context
  - row number
  - raw row data
  - unmapped fields
- `PlayerTag`
  - name
  - slug/key
  - optional description
  - many-to-many with `Player`

## Services

- `identity_service.py`
  - create/update player helpers
  - normalize player identity fields
  - retrieve player summaries for search/profile use
- `matching_service.py`
  - exact identifier match
  - high-confidence identity match
  - ambiguous match detection
  - no-match result
- `import_service.py`
  - placeholder/scaffold for later CSV workflow
  - shared import result types if useful
- `tag_service.py`
  - create/list tags
  - assign/remove tags
  - filter players by tag

## Views

- None required beyond Django admin in this phase.

## Templates

- None required beyond Django admin in this phase.

## URLs

- No public/player URLs required in this phase.

## Admin

- Register `Player`.
- Register `PlayerAlias`.
- Register `PlayerSourceIdentifier`.
- Register `PlayerSourceRow`.
- Register `PlayerTag`.
- Add useful list display/search fields for staff/admin management.

## Migrations

- Initial `players` migration creating player identity, alias, source identifier, source row, and tag models.

## Tests

- Player full/display name behavior.
- Alias creation and lookup.
- Source identifier uniqueness or matching behavior.
- Source row provenance preservation.
- Tag assignment/removal.
- Matching service exact match.
- Matching service high-confidence match.
- Matching service ambiguous match.
- Matching service no-match result.

## Acceptance Criteria

- `players` app exists and is installed.
- Canonical `players.Player` records can be created.
- Aliases, source identifiers, source rows, and tags link to players.
- Staff/admin can manage player records and tags in admin.
- Matching service returns structured results for exact, high-confidence, ambiguous, and no-match cases.
- Tests for this phase pass.

## Definition of Done

This phase is complete when:

- [ ] All deliverables are complete.
- [ ] Acceptance criteria are satisfied.
- [ ] Tests for the phase pass.
- [ ] Documentation is updated if implementation details changed.
- [ ] Phase Review is completed.
- [ ] `docs/analytics/implementation/STATUS.md` is updated.

## Risks / Open Questions

- Existing `pdp.PlayerProfile` is legacy/transitionary and overlaps with `players.Player`; Phase 1 must avoid dependency on PDP while preserving coexistence.
- Exact field names for team/division context may need to align with imported CSVs.
- Identifier uniqueness rules must avoid blocking legitimate multi-source imports.
- Sensitive imported fields must not leak into coach-facing future screens.

## Implementation Notes


## Phase Review

### What went well

### Challenges

### Technical debt

### Architecture changes

### Recommendations for the next phase

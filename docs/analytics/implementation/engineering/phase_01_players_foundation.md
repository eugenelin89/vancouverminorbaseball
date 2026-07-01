# Phase 1 Engineering Plan: Players Foundation

## Overview

Phase 1 creates the independent `players` app as the canonical future player identity foundation for Analytics and future VCB systems.

`players.Player` is the canonical future player identity model. It must not depend on legacy `pdp.PlayerProfile`. Analytics should reference `players.Player` directly. Existing `pdp.PlayerProfile` data is relevant only for coexistence, migration planning, or temporary bridge logic if explicitly required.

Phase 1 should not migrate PDP workflows, create Analytics observations, build player-facing pages, or implement the full import workflow UI. It should establish the player identity models, admin support, service scaffolding, and tests needed by later phases.

## Files To Create

- `players/__init__.py`
- `players/apps.py`
- `players/models.py`
- `players/admin.py`
- `players/tests.py`
- `players/migrations/__init__.py`
- `players/services/__init__.py`
- `players/services/identity_service.py`
- `players/services/matching_service.py`
- `players/services/import_service.py`
- `players/services/tag_service.py`

## Files To Modify

- `vancouverminor/settings.py`
  - Add `players` to `INSTALLED_APPS`.
- `docs/analytics/implementation/phase_01_players_foundation.md`
  - Update checkboxes and Phase Review only after implementation is verified.
- `docs/analytics/implementation/STATUS.md`
  - Update phase status only after implementation progress actually changes.

No URL, view, template, or CSS files should be created in Phase 1.

## Proposed Models

Use an app-local abstract `TimeStampedModel`, matching existing `pdp`, `leaguehub`, and `scholarships` conventions.

### Player

Fields:

- `first_name`: `CharField(max_length=80)`
- `last_name`: `CharField(max_length=80)`
- `preferred_name`: `CharField(max_length=80, blank=True)`
- `birthdate`: `DateField(null=True, blank=True)`
- `birth_year`: `PositiveSmallIntegerField(null=True, blank=True)`
- `gender`: `CharField(max_length=40, blank=True)`
- `division`: `CharField(max_length=80, blank=True)`
- `team_name`: `CharField(max_length=120, blank=True)`
- `school`: `CharField(max_length=160, blank=True)`
- `graduation_year`: `PositiveSmallIntegerField(null=True, blank=True)`
- `bats`: `CharField(max_length=20, blank=True)`
- `throws`: `CharField(max_length=20, blank=True)`
- `primary_positions`: `CharField(max_length=160, blank=True)`
- `is_active`: `BooleanField(default=True)`
- `metadata`: `JSONField(default=dict, blank=True)`
- `created_at`: `DateTimeField(auto_now_add=True)`
- `updated_at`: `DateTimeField(auto_now=True)`

Methods/properties:

- `full_name`
- `display_name`, using preferred name when present
- `__str__`

Avoid email, phone, address, guardian/contact, and medical fields in Phase 1 unless explicitly required later. If imported CSVs contain sensitive fields, preserve them through provenance rather than adding them to coach-facing identity fields.

### PlayerAlias

Fields:

- `player`: `ForeignKey("players.Player", on_delete=models.CASCADE, related_name="aliases")`
- `alias`: `CharField(max_length=160)`
- `normalized_alias`: `CharField(max_length=160, editable=False)`
- `source`: `CharField(max_length=120, blank=True)`
- `context`: `CharField(max_length=160, blank=True)`
- `created_at`: `DateTimeField(auto_now_add=True)`
- `updated_at`: `DateTimeField(auto_now=True)`

Behavior:

- Save a normalized alias for consistent lookup.
- Do not use aliases as authoritative legal names.

### PlayerSourceIdentifier

Fields:

- `player`: `ForeignKey("players.Player", on_delete=models.CASCADE, related_name="source_identifiers")`
- `source`: `CharField(max_length=80)`
- `identifier_type`: `CharField(max_length=80)`
- `identifier_value`: `CharField(max_length=160)`
- `metadata`: `JSONField(default=dict, blank=True)`
- `created_at`: `DateTimeField(auto_now_add=True)`
- `updated_at`: `DateTimeField(auto_now=True)`

Purpose:

- Store stable identifiers from registration systems, roster files, draft data, and future source systems.
- Support exact player matching without relying only on names.

### PlayerSourceRow

Fields:

- `player`: `ForeignKey("players.Player", on_delete=models.CASCADE, related_name="source_rows")`
- `source`: `CharField(max_length=80)`
- `source_filename`: `CharField(max_length=255, blank=True)`
- `row_number`: `PositiveIntegerField(null=True, blank=True)`
- `original_row`: `JSONField(default=dict, blank=True)`
- `unmapped_fields`: `JSONField(default=dict, blank=True)`
- `imported_by`: `ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)`
- `imported_at`: `DateTimeField(default=timezone.now)`
- `created_at`: `DateTimeField(auto_now_add=True)`
- `updated_at`: `DateTimeField(auto_now=True)`

Purpose:

- Preserve import provenance.
- Keep original source context available for audit/review without making every imported field part of canonical player identity.

### PlayerTag

Fields:

- `name`: `CharField(max_length=80, unique=True)`
- `slug`: `SlugField(max_length=100, unique=True)`
- `description`: `TextField(blank=True)`
- `players`: `ManyToManyField("players.Player", related_name="tags", blank=True)`
- `is_active`: `BooleanField(default=True)`
- `created_at`: `DateTimeField(auto_now_add=True)`
- `updated_at`: `DateTimeField(auto_now=True)`

Purpose:

- Support lightweight staff/admin organization of players.
- Keep tags distinct from future Watch Lists.

## Constraints And Indexes

### Player

- Ordering: `["last_name", "first_name", "id"]`
- Indexes:
  - `["last_name", "first_name"]`
  - `["division", "team_name"]`
  - `["is_active", "last_name"]`
  - `["birthdate"]`
  - `["birth_year"]`

Do not add a unique constraint on player name. Real rosters can contain duplicate names.

### PlayerAlias

- Unique constraint: `["player", "normalized_alias"]`
- Index: `["normalized_alias"]`
- Ordering: `["normalized_alias", "id"]`

The same alias may exist for different players because aliases are matching hints, not global identities.

### PlayerSourceIdentifier

- Unique constraint: `["source", "identifier_type", "identifier_value"]`
- Indexes:
  - `["source", "identifier_type"]`
  - `["identifier_value"]`
- Ordering: `["source", "identifier_type", "identifier_value"]`

Use `source + identifier_type + identifier_value` rather than `identifier_value` alone because different systems may reuse similar IDs.

### PlayerSourceRow

- Indexes:
  - `["source", "source_filename"]`
  - `["player", "source"]`
  - `["imported_at"]`
- Ordering: `["-imported_at", "-id"]`

Do not add a uniqueness constraint in Phase 1. Repeated imports may legitimately preserve multiple provenance rows.

### PlayerTag

- Unique `name`
- Unique `slug`
- Index: `["slug"]`
- Ordering: `["name"]`

## Service Plan

### identity_service.py

Functions:

- `normalize_name(value: str) -> str`
- `normalize_identifier(value: str) -> str`
- `build_display_name(player) -> str`
- `create_player(...) -> Player`
- `update_player_identity(player, **fields) -> Player`
- `create_alias(player, alias, source="", context="") -> PlayerAlias`
- `add_source_identifier(player, source, identifier_type, identifier_value, metadata=None) -> PlayerSourceIdentifier`
- `record_source_row(player, source, source_filename="", row_number=None, original_row=None, unmapped_fields=None, imported_by=None) -> PlayerSourceRow`

Implementation notes:

- Keep functions small and explicit.
- Use transactions where a helper creates or updates multiple records.
- Keep all logic independent of `pdp.PlayerProfile`.

### matching_service.py

Dataclass:

- `PlayerMatchResult`
  - `status`: exact / high_confidence / ambiguous / no_match
  - `player`: optional `Player`
  - `candidates`: list/queryset of possible players
  - `reason`: string
  - `score`: optional numeric score

Functions:

- `match_by_identifier(source, identifier_type, identifier_value)`
- `match_by_name_and_birthdate(first_name, last_name, birthdate)`
- `match_by_name_birth_year_division(first_name, last_name, birth_year=None, division="")`
- `find_player_match(identity_data: dict) -> PlayerMatchResult`

Matching rules:

- Exact source identifier match should return `exact`.
- Exact name plus exact birthdate may return `high_confidence`.
- Name plus birth year/division may return `high_confidence` only when there is a single clear candidate.
- Multiple plausible candidates should return `ambiguous`.
- No plausible candidate should return `no_match`.
- Do not automatically merge ambiguous records.

### import_service.py

Phase 1 scope is scaffolding only. Do not implement CSV upload UI or full preview/confirm workflow.

Dataclasses:

- `ImportIdentityRow`
- `ImportRowResult`

Helpers:

- `clean_cell(value)`
- `normalize_header(value)`
- `build_identity_payload(row, mapping=None)`

Purpose:

- Prepare shared import primitives for Phase 2.
- Keep player import business logic in `players`, not Analytics.

### tag_service.py

Functions:

- `create_tag(name, description="")`
- `assign_tag(player, tag_or_name)`
- `remove_tag(player, tag_or_name)`
- `players_with_tag(tag_or_slug)`
- `active_tags()`

Implementation notes:

- Generate slugs consistently.
- Keep tag assignment idempotent.
- Keep inactive tags available historically but excluded from normal active tag lists.

## Admin Configuration

### PlayerAdmin

- `list_display`: `display_name`, `last_name`, `first_name`, `division`, `team_name`, `is_active`, `updated_at`
- `list_filter`: `is_active`, `division`, `team_name`, `gender`
- `search_fields`: `first_name`, `last_name`, `preferred_name`, `aliases__alias`, `source_identifiers__identifier_value`
- `readonly_fields`: `created_at`, `updated_at`
- Consider inlines for aliases and source identifiers.

### PlayerAliasAdmin

- `list_display`: `alias`, `player`, `source`, `context`, `created_at`
- `search_fields`: `alias`, `normalized_alias`, `player__first_name`, `player__last_name`
- `list_filter`: `source`
- `readonly_fields`: `created_at`, `updated_at`

### PlayerSourceIdentifierAdmin

- `list_display`: `player`, `source`, `identifier_type`, `identifier_value`, `created_at`
- `search_fields`: `identifier_value`, `player__first_name`, `player__last_name`
- `list_filter`: `source`, `identifier_type`
- `readonly_fields`: `created_at`, `updated_at`

### PlayerSourceRowAdmin

- `list_display`: `player`, `source`, `source_filename`, `row_number`, `imported_by`, `imported_at`
- `search_fields`: `player__first_name`, `player__last_name`, `source_filename`
- `list_filter`: `source`, `imported_at`
- `readonly_fields`: `created_at`, `updated_at`

JSON fields can stay editable for debugging and staff correction, but they should not dominate list display.

### PlayerTagAdmin

- `list_display`: `name`, `slug`, `is_active`, `updated_at`
- `list_filter`: `is_active`
- `search_fields`: `name`, `slug`
- `prepopulated_fields`: `{"slug": ("name",)}`
- `readonly_fields`: `created_at`, `updated_at`

## Tests To Write

Create tests in `players/tests.py`, following the repository's app-level `tests.py` convention.

Model tests:

- Player `full_name` and `display_name`.
- Player can be created without a dependency on `pdp.PlayerProfile`.
- Alias saves normalized value.
- Duplicate alias for the same player is rejected.
- Same alias can exist for different players.
- Source identifier uniqueness prevents duplicate source/type/value.
- Source row preserves original row and unmapped fields.
- Tag assignment/removal works.

Service tests:

- `identity_service.create_player` creates canonical player.
- `identity_service.add_source_identifier` normalizes and persists identifiers.
- `matching_service.match_by_identifier` returns exact match.
- Name plus birthdate returns high-confidence match.
- Duplicate name candidates return ambiguous.
- Unknown identity returns no-match.
- `tag_service.assign_tag` creates or links tag consistently.

Integration/sanity tests:

- `players` app is installed.
- Admin classes are registered enough to instantiate or inspect where practical.
- `python manage.py test players` passes.
- Full `python manage.py test` passes after Phase 1.

## Migration Strategy

1. Create `players` app files.
2. Add `players` to `INSTALLED_APPS`.
3. Define models with no foreign key to `pdp.PlayerProfile`.
4. Run `python manage.py makemigrations players`.
5. Review generated `players/migrations/0001_initial.py`.
6. Run `python manage.py migrate`.
7. Run `python manage.py test players`.
8. Run full `python manage.py test`.

The initial migration should only create `players` tables and the many-to-many table for tags. It should not alter PDP, drafts, analytics, or other app tables.

## Risks / Ambiguities

- `pdp.PlayerProfile` has overlapping identity fields. Phase 1 should not bridge automatically; doing so could accidentally create a dependency or migration path before it is designed.
- Existing `pdp.Season` is still the only season model. Avoid adding season foreign keys to `players.Player` in Phase 1.
- Field choices for `gender`, `bats`, `throws`, and positions could be formal choices later, but free text is safer for import compatibility in Phase 1.
- Unique source identifiers are useful, but some real data may reuse weak identifiers across seasons.
- Tags and Watch Lists are distinct in the architecture. Phase 1 should implement only tags.
- Import service should remain scaffolding; a full upload/preview/merge workflow belongs to Phase 2.
- Admin search across aliases/source identifiers can create duplicate result rows unless handled by Django admin behavior.

## Open Questions

- Should `birthdate` or `birth_year` be considered the preferred matching field when both are present?
- Should `division` and `team_name` live directly on `Player` long term, or should they eventually move to season/team membership models?
- Which source names should be standardized first for imported files, draft context, and manual staff entry?
- Should `PlayerTag.name` uniqueness be case-sensitive or enforced through a normalized slug only?
- Should Phase 1 include any read-only bridge metadata back to legacy PDP records, or should that wait for an explicit migration/bridge phase?

## Implementation Decisions

- Used an app-local `TimeStampedModel` in `players.models` to match existing `pdp`, `leaguehub`, and `scholarships` conventions without introducing a shared base app.
- Kept `players.Player` fully independent from legacy `pdp.PlayerProfile`; no foreign keys, bridge models, or migration hooks were added.
- Stored source identifiers in normalized lowercase/casefolded form for deterministic matching and uniqueness checks across imports.
- Stored player aliases with a separate `normalized_alias` field so display aliases can remain human-readable while matching stays consistent.
- Used free-text fields for `gender`, `bats`, `throws`, `division`, `team_name`, and positions to preserve import flexibility in Phase 1.
- Implemented `import_service.py` as scaffolding only: dataclasses and cleaning/mapping helpers, with no upload UI or preview/confirm workflow.
- Added admin inlines for aliases and source identifiers on `PlayerAdmin` because those are part of day-to-day identity management.
- Added `from __future__ import annotations` in service modules because the current runtime is Python 3.9.

## Recommended Implementation Sequence

1. Scaffold the `players` app and add it to settings.
2. Implement models and admin.
3. Create the initial migration.
4. Implement identity, matching, import scaffolding, and tag services.
5. Add focused tests.
6. Run `python manage.py test players`.
7. Run full `python manage.py test`.
8. Update Phase 1 checklist and status only after implementation is verified.

## Implementation Notes

Implemented on 2026-07-01.

The implementation followed the engineering plan without requiring architecture changes. The generated migration creates only `players` tables and related indexes/constraints, plus the `PlayerTag.players` many-to-many table.

Verification completed:

- `python manage.py makemigrations players`
- `python manage.py migrate`
- `python manage.py test players`
- `python manage.py test`

Keep this document as the detailed technical plan and implementation record for Phase 1. The higher-level phase tracking document remains `docs/analytics/implementation/phase_01_players_foundation.md`.

# Phase 2 Engineering Plan: Player Import Workflow

## Overview

Phase 2 builds the staff/admin player import workflow that turns roster/member CSV files into canonical `players.Player` records with conservative matching, preview, conflict review, and provenance.

Phase 1 is complete. This phase should reuse the existing `players` app, Phase 1 player models, and Phase 1 services.

Mandatory boundaries:

- Player import business logic belongs in `players/services/import_service.py`.
- Matching belongs in `players/services/matching_service.py`.
- Analytics may expose the import UI, but Analytics must not own player import behavior.
- Do not implement coach assessments, observations, reporting, timelines, draft context, or future phases.
- Do not migrate PDP workflows.
- Do not make imports depend on legacy `pdp.PlayerProfile`.

Existing project patterns to reuse:

- Drafts import uses a simple CSV upload, preview, hidden preview payload, confirm action, row-level errors, and messages.
- PDP import uses a richer upload, preview, column mapping, import metadata, recent import list, and service-owned execution.
- Phase 2 should combine those patterns: simple enough for CSV player identity imports, but with enough metadata and persisted preview state to support conflict review.

## Expected CSV Sources

Version 1 should support CSV files that describe the same player population with different detail levels. The first expected source families are:

### Member List CSV

Expected source name:

- `vcb_member_list_csv`

Example filename patterns:

- `member list for 13u house.csv`
- `member_list_13u_house.csv`
- `members_13u_house.csv`

Likely columns:

- first name
- last name
- role
- age
- gender
- team
- division

Likely mapping:

- first name -> `Player.first_name`
- last name -> `Player.last_name`
- gender -> `Player.gender`
- team -> `Player.team_name`
- division or team context -> `Player.division`
- age -> preview-only context unless birth year can be reliably inferred from an import cycle date
- role -> source-row metadata unless it clearly identifies player/non-player rows

### Roster Detail CSV

Expected source name:

- `vcb_roster_detail_csv`

Example filename patterns:

- `roster detail for 13u house.csv`
- `roster_detail_13u_house.csv`
- `team_roster_detail.csv`

Likely columns:

- first name
- last name
- player/non-player status
- address
- city
- birthdate
- jersey number
- position
- email
- phone number
- gender
- contacts/guardians
- team ID
- team
- division
- registration ID
- registrant ID
- baseball history
- throwing
- batting
- medical notes
- availability
- volunteering
- sponsorship
- comments

Likely mapping:

- first name -> `Player.first_name`
- last name -> `Player.last_name`
- birthdate -> `Player.birthdate`
- derived birth year -> `Player.birth_year`
- gender -> `Player.gender`
- team -> `Player.team_name`
- division -> `Player.division`
- position / positions -> `Player.primary_positions`
- throwing -> `Player.throws`
- batting -> `Player.bats`
- school or graduation year if present -> `Player.school` / `Player.graduation_year`
- registration ID, registrant ID, team ID -> `PlayerSourceIdentifier`
- jersey number, role, email, phone, address, contacts, guardian data, medical notes, availability, volunteering, sponsorship, comments -> `PlayerSourceRow.original_row` and/or `unmapped_fields`

Sensitive data should not become ordinary `Player` fields in Phase 2. Preserve it as provenance only, and do not display it broadly in Analytics screens.

### Manual Staff CSV

Expected source name:

- `manual_staff_csv`

Purpose:

- A lightweight staff/admin CSV for corrections, small rosters, or data cleanup.

Recommended columns:

- first name
- last name
- preferred name
- birthdate
- birth year
- gender
- division
- team
- bats
- throws
- positions
- source identifier

### Source Naming Conventions

Use stable normalized source names in import metadata, source identifiers, and source rows:

- `vcb_member_list_csv`
- `vcb_roster_detail_csv`
- `manual_staff_csv`
- `draft_context_csv` only when draft-specific import context is explicitly introduced later

Store the original uploaded filename separately from the normalized source name.

Identifier type conventions:

- `registration_id`
- `registrant_id`
- `team_id`
- `source_player_id`
- `draft_player_id` only when draft integration begins

Do not use free-form source names as the only durable integration key.

## Files To Create

Player import ownership:

- `players/forms.py`
  - CSV upload and mapping forms if the UI imports directly from `players`.
  - If the UI lives under Analytics, keep forms there only when they are purely presentation concerns. Prefer service-owned validation in `players`.

Likely Analytics UI entry point:

- `analytics/__init__.py`
- `analytics/apps.py`
- `analytics/urls.py`
- `analytics/views.py`
- `analytics/forms.py`
- `analytics/templates/analytics/base.html`
- `analytics/templates/analytics/import_list.html`
- `analytics/templates/analytics/import_upload.html`
- `analytics/templates/analytics/import_preview.html`
- `analytics/templates/analytics/import_conflicts.html`
- `analytics/templates/analytics/import_detail.html`
- `analytics/tests.py`

Static assets:

- Avoid adding CSS unless existing PDP classes are insufficient.
- If needed later, create `static/css/analytics.css`, but keep styling minimal and consistent with the PDP app shell.

## Files To Modify

Project settings and URLs:

- `vancouverminor/settings.py`
  - Add `analytics` to `INSTALLED_APPS` if the import UI is exposed through an Analytics app in Phase 2.
- `vancouverminor/urls.py`
  - Add `path("analytics/", include("analytics.urls"))` if Analytics UI is created in Phase 2.

Players app:

- `players/models.py`
  - Add import metadata model if approved by this plan.
  - Consider adding a nullable FK from `PlayerSourceRow` to the import metadata model.
- `players/admin.py`
  - Register import metadata model.
  - Add import metadata display/filtering to source row admin if linked.
- `players/services/import_service.py`
  - Expand Phase 1 scaffolding into full CSV parse, preview, mapping, conflict, and commit services.
- `players/services/matching_service.py`
  - Extend only if Phase 2 import matching needs small reusable helpers; avoid changing Phase 1 semantics unnecessarily.
- `players/tests.py`
  - Add player import service tests, unless test volume justifies `players/tests.py` splitting in a later cleanup.

Documentation after implementation:

- `docs/analytics/implementation/STATUS.md`
- `docs/analytics/implementation/phase_02_player_import_workflow.md`
- `docs/analytics/implementation/engineering/phase_02_player_import_workflow.md`

## Import Metadata Model Decision

Add an import metadata model in the `players` app.

Recommended model name:

- `PlayerImportBatch`

Reasoning:

- Import ownership belongs to the `players` bounded context.
- The import workflow needs persisted upload metadata, preview snapshots, mapping config, row errors, conflict summaries, status, and completion summary.
- Hidden preview payloads are acceptable for small draft imports, but Phase 2 needs conflict review and multi-step mapping; persisted state is more reliable and easier to audit.
- PDP already uses an import metadata model for richer imports; Phase 2 should follow that pattern without coupling to PDP.

Do not put this metadata model in Analytics. Analytics can display and route the workflow, but it should consume `players.PlayerImportBatch`.

## Proposed Model Changes

### PlayerImportBatch

Fields:

- `source`: `CharField(max_length=80)`
- `original_filename`: `CharField(max_length=255)`
- `uploaded_by`: `ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="player_import_batches")`
- `status`: `CharField(max_length=40, choices=...)`
- `mapping_config`: `JSONField(default=dict, blank=True)`
- `preview_snapshot`: `JSONField(default=dict, blank=True)`
- `row_errors`: `JSONField(default=list, blank=True)`
- `conflict_summary`: `JSONField(default=dict, blank=True)`
- `import_summary`: `JSONField(default=dict, blank=True)`
- `rows_processed`: `PositiveIntegerField(default=0)`
- `rows_created`: `PositiveIntegerField(default=0)`
- `rows_updated`: `PositiveIntegerField(default=0)`
- `rows_skipped`: `PositiveIntegerField(default=0)`
- `rows_conflicted`: `PositiveIntegerField(default=0)`
- `committed_at`: `DateTimeField(null=True, blank=True)`
- `created_at`: `DateTimeField(auto_now_add=True)`
- `updated_at`: `DateTimeField(auto_now=True)`

Status choices:

- `uploaded`
- `previewed`
- `needs_review`
- `committed`
- `failed`
- `cancelled`

Indexes:

- `["status", "-created_at"]`
- `["source", "-created_at"]`
- `["uploaded_by", "-created_at"]`

Ordering:

- `["-created_at", "-id"]`

### PlayerSourceRow

Recommended change:

- Add nullable FK:
  - `import_batch = ForeignKey("players.PlayerImportBatch", null=True, blank=True, on_delete=models.SET_NULL, related_name="source_rows")`

Reasoning:

- Phase 1 source rows already preserve row-level provenance.
- Linking source rows to a batch makes it possible to inspect all rows from one upload and report import outcomes.
- Use `SET_NULL` so row provenance survives if a batch record is removed by staff/admin.

Additional index:

- `["import_batch", "row_number"]`

## Service Design

All business logic below belongs in `players/services/import_service.py`.

### Dataclasses

Extend or replace Phase 1 dataclasses with:

- `ParsedCsvFile`
  - `file_name`
  - `headers`
  - `normalized_headers`
  - `rows`
  - `duplicate_headers`
- `ImportPreviewRow`
  - `row_number`
  - `identity`
  - `original_row`
  - `unmapped_fields`
  - `source_identifiers`
  - `match_status`
  - `matched_player_id`
  - `candidate_ids`
  - `field_conflicts`
  - `errors`
  - `action`
- `FieldConflict`
  - `field_name`
  - `existing_value`
  - `imported_value`
  - `resolution`
- `ImportCommitResult`
  - `rows_processed`
  - `created`
  - `updated`
  - `skipped`
  - `conflicts`
  - `errors`

Keep dataclasses serializable to JSON-friendly dictionaries for `preview_snapshot`, `row_errors`, and `conflict_summary`.

### CSV Parsing

Functions:

- `parse_player_csv(file_obj) -> ParsedCsvFile`
- `serialize_preview(preview: dict) -> str`
- `deserialize_preview(payload: str) -> dict`
- `detect_source_from_filename(filename: str) -> str`
- `build_column_choices(parsed: ParsedCsvFile) -> list[tuple[str, str]]`

Parsing rules:

- Accept `.csv` only in Phase 2.
- Decode bytes with `utf-8-sig`.
- Use `csv.DictReader`.
- Reject missing header row.
- Reject blank or duplicate normalized headers.
- Preserve original headers for display.
- Preserve original row values in `original_row`.
- Strip cell values for mapped fields.
- Do not drop unmapped fields.

### Header Normalization And Mapping

Functions:

- `normalize_header(value) -> str`
- `suggest_mapping(headers: list[str], source: str = "") -> dict`
- `build_identity_payload(row, mapping) -> dict`
- `build_source_identifiers(row, mapping, source) -> list[dict]`
- `split_full_name(full_name: str) -> tuple[str, str]`
- `parse_birthdate(value: str)`
- `parse_birth_year(value: str)`

Suggested canonical field mapping keys:

- `first_name`
- `last_name`
- `full_name`
- `preferred_name`
- `birthdate`
- `birth_year`
- `gender`
- `division`
- `team_name`
- `primary_positions`
- `bats`
- `throws`
- `school`
- `graduation_year`
- `registration_id`
- `registrant_id`
- `team_id`
- `source_player_id`

Header aliases:

- first name: `first`, `first name`, `firstname`, `given name`, `player first name`
- last name: `last`, `last name`, `lastname`, `surname`, `family name`, `player last name`
- full name: `name`, `full name`, `player`, `player name`
- birthdate: `birthdate`, `birth date`, `date of birth`, `dob`
- birth year: `birth year`, `year of birth`, `yob`
- gender: `gender`, `sex`
- division: `division`, `level`, `program`
- team: `team`, `team name`, `current team`
- positions: `position`, `positions`, `primary position`, `primary positions`
- bats: `bats`, `batting`, `hits`
- throws: `throws`, `throwing`
- registration ID: `registration id`, `registration`, `reg id`
- registrant ID: `registrant id`, `member id`, `participant id`
- team ID: `team id`, `teamid`

### Preview Generation

Functions:

- `create_import_batch(*, file_obj, source, uploaded_by) -> PlayerImportBatch`
- `build_import_preview(*, import_batch, mapping_config=None) -> dict`
- `preview_row(*, row, mapping_config, source) -> ImportPreviewRow`

Preview responsibilities:

- Show parsed rows before committing.
- Suggest default mapping based on source/header aliases.
- Validate required identity fields.
- Call `players.services.matching_service.find_player_match`.
- Classify each row:
  - `create`
  - `update`
  - `needs_review`
  - `skip`
  - `error`
- Detect field-level conflicts when an imported value differs from an existing non-empty player value.
- Store preview snapshot on `PlayerImportBatch`.
- Store row errors and conflict summary on `PlayerImportBatch`.

Required identity rule:

- A row must have either:
  - first name and last name, or
  - full name that can be split into first and last name.

Recommended source identifier rule:

- If registration ID, registrant ID, team ID, or source player ID is present, store it as `PlayerSourceIdentifier`.

### Conflict Detection And Resolution

Conflict cases:

- Existing player has non-empty value and imported row has a different non-empty value for:
  - `preferred_name`
  - `birthdate`
  - `birth_year`
  - `gender`
  - `division`
  - `team_name`
  - `primary_positions`
  - `bats`
  - `throws`
  - `school`
  - `graduation_year`

Default behavior:

- If existing player field is blank and imported value exists, fill it.
- If existing player field is non-empty and imported value differs, do not overwrite automatically.
- Store conflicting imported value in source row provenance.
- Mark row as `needs_review` unless staff chooses an explicit field resolution.

Resolution options:

- `keep_existing`
- `use_imported`
- `metadata_only`

Conflict review should be practical in Phase 2:

- Allow row-level review of conflicts.
- Do not build a complex spreadsheet editor.
- Support posting selected resolutions for conflicted rows.

### Commit Import

Functions:

- `commit_import_batch(*, import_batch, actor, resolutions=None) -> ImportCommitResult`
- `create_player_from_import(identity) -> Player`
- `apply_player_updates(player, identity, field_resolutions=None) -> Player`
- `attach_source_identifiers(player, identifiers, metadata=None)`
- `record_import_source_row(player, import_batch, preview_row, actor)`

Commit behavior:

- Use `transaction.atomic`.
- Lock the import batch row before committing.
- Prevent committing an already committed batch.
- Create new players for `create` rows.
- Update existing players for high-confidence `update` rows by filling blanks.
- Apply explicit conflict resolutions only when provided by staff/admin.
- Skip unresolved ambiguous/conflict rows.
- Always preserve source rows for created/updated rows.
- Record row-level errors for rows that cannot be committed.
- Update import summary counts and status.

Status transitions:

- `uploaded` after file upload metadata is created.
- `previewed` after preview without conflicts.
- `needs_review` after preview with ambiguous matches or conflicts.
- `committed` after successful commit.
- `failed` after unexpected service-level failure.
- `cancelled` if staff cancels the batch.

## Preview / Mapping / Conflict Workflow

Recommended UI workflow:

1. Staff opens `/analytics/imports/`.
2. Staff clicks new import and uploads CSV.
3. Upload view creates `PlayerImportBatch`, parses CSV, detects source, suggests mapping, and redirects to preview.
4. Preview page shows:
   - source
   - original filename
   - row counts
   - headers
   - suggested column mapping
   - sample rows
   - row status summary
5. Staff adjusts mapping and reruns preview if needed.
6. If preview has no conflicts or ambiguous rows, staff can confirm import.
7. If preview has conflicts/ambiguous rows, staff goes to conflict review.
8. Staff resolves conflicts or chooses to skip ambiguous rows.
9. Confirm action commits import through `players.services.import_service`.
10. Result page shows created, updated, skipped, conflict, and error counts.

Do not use hidden preview payloads as the only source of truth for Phase 2. Persist preview state in `PlayerImportBatch` because conflict review is multi-step.

## Permission Rules

Version 1 permission rule:

- Only authenticated `is_staff` or `is_superuser` users can access import workflow.

Implementation options:

- Create `AnalyticsStaffRequiredMixin` in `analytics/views.py`, similar to `drafts.views.StaffRequiredMixin`.
- Or create a small permission helper in `players/services/permissions.py` only if multiple players workflows need it.

Recommended for Phase 2:

- Use an `AnalyticsStaffRequiredMixin` for UI access.
- Use service-level actor validation where commit mutates records, so future non-Analytics entry points cannot bypass permission checks accidentally.

Do not expose import views to public users, coaches, players, or parents in Phase 2.

## Analytics UI Plan

Phase 2 may create a minimal `analytics` app only to expose the player import workflow.

Keep Analytics UI thin:

- Forms validate upload/mapping inputs.
- Views enforce staff/admin access.
- Views call `players.services.import_service`.
- Views display service results.
- Views do not contain matching, merge, or player identity business logic.

URL patterns:

- `/analytics/imports/`
- `/analytics/imports/new/`
- `/analytics/imports/<int:pk>/preview/`
- `/analytics/imports/<int:pk>/conflicts/`
- `/analytics/imports/<int:pk>/confirm/`
- `/analytics/imports/<int:pk>/`

URL names:

- `analytics:import-list`
- `analytics:import-new`
- `analytics:import-preview`
- `analytics:import-conflicts`
- `analytics:import-confirm`
- `analytics:import-detail`

Templates should extend the PDP shell or a minimal Analytics base that itself extends `pdp/base.html`, consistent with the repository assessment.

## Forms

Recommended forms:

### PlayerImportUploadForm

Location:

- `analytics/forms.py` if purely UI.

Fields:

- `csv_file`: `FileField`
- `source`: `ChoiceField`

Validation:

- Require `.csv` extension.
- Source must be one of the known source names.

### PlayerImportMappingForm

Fields:

- `first_name_column`
- `last_name_column`
- `full_name_column`
- `preferred_name_column`
- `birthdate_column`
- `birth_year_column`
- `gender_column`
- `division_column`
- `team_name_column`
- `primary_positions_column`
- `bats_column`
- `throws_column`
- `school_column`
- `graduation_year_column`
- `registration_id_column`
- `registrant_id_column`
- `team_id_column`
- `source_player_id_column`

Validation:

- Require either full name or both first and last name.

### PlayerImportConflictResolutionForm

Keep simple:

- per-row action:
  - `commit`
  - `skip`
- per-field resolution:
  - `keep_existing`
  - `use_imported`
  - `metadata_only`

If this becomes too complex in one form, use POSTed structured JSON-like field names and parse them in a UI orchestration helper while keeping commit logic in `players.services.import_service`.

## Admin Configuration

Register `PlayerImportBatch` in `players/admin.py`.

Recommended `PlayerImportBatchAdmin`:

- `list_display`: `original_filename`, `source`, `status`, `uploaded_by`, `rows_processed`, `rows_created`, `rows_updated`, `rows_conflicted`, `created_at`
- `list_filter`: `status`, `source`, `created_at`
- `search_fields`: `original_filename`, `uploaded_by__username`, `uploaded_by__email`
- `readonly_fields`: `created_at`, `updated_at`, `committed_at`
- Avoid making preview JSON the primary management surface.

Update `PlayerSourceRowAdmin`:

- include `import_batch` in `list_display`
- add `import_batch` to `list_filter`
- add `import_batch__original_filename` to `search_fields`

Do not add admin bulk merge actions in Phase 2.

## Tests To Write

Follow current app-level `tests.py` convention unless test size becomes unmanageable.

### players service/model tests

Add to `players/tests.py` or split into a future tests package only if needed.

CSV parsing:

- Parses UTF-8 BOM CSV.
- Rejects missing header row.
- Rejects duplicate normalized headers.
- Rejects blank headers.
- Preserves original row data.
- Preserves unmapped fields.

Mapping:

- Suggests mapping for member list headers.
- Suggests mapping for roster detail headers.
- Requires full name or first/last.
- Builds source identifiers for registration ID, registrant ID, team ID.

Preview:

- New player row classified as `create`.
- Exact source identifier classified as `update`.
- High-confidence name/birthdate match classified as `update`.
- Multiple candidate match classified as `needs_review`.
- Missing name row classified as `error`.
- Field conflict detected when existing value differs from imported non-empty value.

Commit:

- Creates new players.
- Fills missing fields on matched players.
- Does not silently overwrite conflicting existing fields.
- Applies explicit `use_imported` conflict resolution.
- Records `PlayerSourceRow` linked to import batch.
- Creates `PlayerSourceIdentifier` records.
- Handles duplicate source identifier gracefully.
- Updates `PlayerImportBatch` summary/status.
- Prevents double commit.

Permissions:

- Non-authenticated users cannot access import pages.
- Non-staff authenticated users cannot access import pages.
- Staff users can access import pages.
- Service commit rejects unauthorized actor if service-level permission check is added.

### analytics UI tests

If Phase 2 creates an Analytics app:

- Import list renders for staff.
- Upload view accepts CSV and redirects to preview.
- Preview shows mapping and row summary.
- Confirm commits import and redirects to detail.
- Conflict page displays ambiguous/conflict rows.
- Messages show success/warning/error counts.

### Regression tests

- Existing `python manage.py test players` passes.
- Full `python manage.py test` passes.
- No tests should require PDP workflow migration.

## Migration Strategy

Expected migrations:

1. `players` migration adding `PlayerImportBatch`.
2. `players` migration adding nullable `PlayerSourceRow.import_batch` FK, or same migration if implemented together.
3. If creating `analytics` app:
   - no models required in Phase 2, so no Analytics migration should be needed.

Migration constraints:

- Do not alter `pdp` models.
- Do not alter `drafts` models.
- Do not introduce Analytics observation tables.
- Preserve existing `PlayerSourceRow` rows by making `import_batch` nullable.

Required commands during implementation:

- `python manage.py makemigrations players`
- `python manage.py migrate`
- `python manage.py test players`
- `python manage.py test`

If an `analytics` app is created without models, `makemigrations analytics` should not create a migration.

## Risks / Ambiguities

- Real CSV headers may differ from the expected member-list and roster-detail examples.
- Sensitive roster-detail fields may be present. The UI must avoid casually displaying medical, contact, guardian, address, phone, and email data.
- A single import workflow may become too complex if conflict review is implemented as a spreadsheet-like editor. Keep conflict review row-focused and limited.
- Existing `matching_service` may need small extensions for source identifiers and richer candidate reasons; avoid making it import-specific.
- Duplicate source identifiers could happen if a prior bad import linked an ID to the wrong player. The service should report this clearly instead of crashing.
- Existing `PlayerSourceRow` has no FK to import batch yet. Adding it is straightforward but requires a migration.
- Analytics app creation in Phase 2 is UI-only. There is a risk future work starts placing player business logic there; keep strict boundaries.
- The phrase "evaluation cycle" appears in the architecture, but no shared cycle model exists yet. Do not add one in Phase 2 unless the architecture is updated.

## Open Questions

- Resolved: Phase 2 created the minimal `analytics` app for the import UI.
- Should imported email and phone fields ever be visible to staff in import review, or should they be stored only in provenance until explicit privacy rules are written?
- What exact source names should be used for the first real files if filenames are inconsistent?
- Should unresolved conflict rows be allowed to leave an import batch in `needs_review` after some rows are committed, or should Phase 2 require all unresolved rows to be skipped before commit?
- Should staff be able to cancel/delete import batches, or only leave them as failed/cancelled records?

## Implementation Decisions

- Created the minimal `analytics` app now for import UI routing, forms, templates, and staff-only views.
- Kept import business logic in `players.services.import_service`; Analytics views only validate UI forms, call services, display results, and redirect.
- Added `players.PlayerImportBatch` to persist upload metadata, mapping config, preview snapshots, row errors, conflict summaries, and import summaries.
- Added nullable `PlayerSourceRow.import_batch` so existing and future source rows can be grouped by upload while preserving provenance if a batch is removed.
- Persisted preview state in `PlayerImportBatch.preview_snapshot` rather than relying on hidden preview payloads because Phase 2 includes mapping refresh and conflict review.
- Kept CSV support only; XLSX and other formats remain out of scope.
- Implemented conflict review as row-focused form controls rather than a spreadsheet-like editor.
- Staff/admin access is enforced in Analytics views and in import service mutation entry points.
- Imported sensitive fields remain in `original_row` / `unmapped_fields` provenance and are not promoted to canonical player fields.
- Corrected the generated migration operation order so `PlayerSourceRow.import_batch` is added before its index.
- Added a commit preflight that blocks the entire commit when any conflict, ambiguous, or error row is unresolved. This avoids partial imports without row-level committed state in Phase 2 and lets staff return to resolve or explicitly skip rows.
- Added real ambiguous-row resolution with three staff choices: use a selected existing candidate, create a new player, or skip the row.
- Updated import matching to check all mapped source identifiers before falling back to name/birthdate matching. If multiple identifiers match different players, the row is marked ambiguous.
- Added `first_name` and `last_name` to import conflict detection so source-identifier matches do not silently hide name discrepancies.
- Added CSV guardrails: 5 MB maximum upload size and 5,000 data rows per upload.
- Made sensitive import JSON fields read-only in Django admin and routed preview pages with review rows through the conflict review page before commit.

## Recommended Implementation Sequence

1. Re-read `docs/analytics/architecture/04_imports.md`, Phase 2 tracker, this engineering plan, and current `players` services.
2. Add `PlayerImportBatch` and nullable `PlayerSourceRow.import_batch`.
3. Update `players/admin.py` for import batch and source row filtering.
4. Expand `players/services/import_service.py` with CSV parsing, source detection, mapping suggestions, preview generation, conflict detection, and commit behavior.
5. Add players service tests for parsing, mapping, preview, conflict, and commit behavior.
6. Create a minimal `analytics` app only for import UI if proceeding with the Phase 2 "Analytics Import Players page" deliverable.
7. Add Analytics URL include and staff-only import views/forms/templates.
8. Add Analytics UI permission and workflow tests.
9. Run migrations and required tests.
10. Update `STATUS.md`, `phase_02_player_import_workflow.md`, and this engineering plan with implementation decisions and Phase Review.

## Implementation Notes

Implemented on 2026-07-02.

The implementation followed the architecture without requiring Architecture Handbook changes. Analytics owns only UI orchestration for this phase; `players` owns import state, matching, merge behavior, and provenance.

Verification completed:

- `python manage.py makemigrations players`
- `python manage.py migrate`
- `python manage.py test players`
- `python manage.py test analytics`
- `python manage.py test`

Review-fix verification completed:

- `python manage.py test players`
- `python manage.py test analytics`
- `python manage.py test`

Test results:

- Initial implementation: `players` 30 tests passing, `analytics` 5 tests passing, full suite 69 tests passing.
- Review fixes: `players` 39 tests passing, `analytics` 7 tests passing, full suite 80 tests passing.

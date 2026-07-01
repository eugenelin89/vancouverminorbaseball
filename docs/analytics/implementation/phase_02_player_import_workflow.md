# Phase 02: Player Import Workflow

## Purpose

Build the staff/admin player import workflow that turns roster/member CSV files into shared `players.Player` records with conservative matching, merge review, and provenance.

## Architecture References

- [02 Players](../architecture/02_players.md)
- [04 Imports](../architecture/04_imports.md)
- [09 Services](../architecture/09_services.md)
- [10 Permissions](../architecture/10_permissions.md)

## Existing Project Integration

Before implementing this phase, inspect relevant existing project conventions, including:

- upload handling patterns
- form patterns
- messages and redirect conventions
- authentication and permission patterns
- admin configuration patterns for import/provenance records
- service-layer patterns
- test organization and fixtures for file uploads

## Scope

- Add staff/admin import workflow exposed through Analytics.
- Implement CSV upload and parsing.
- Add import preview.
- Add column mapping.
- Use `players.services.matching_service` for matching.
- Use `players.services.import_service` for import/merge behavior.
- Preserve source rows and unmapped fields.
- Add conflict review and row-level errors.

## Out of Scope

- Coach assessments.
- Observation models.
- Player timeline UI beyond linking imported players later.
- Draft matching.
- Advanced import formats beyond CSV.
- Automated risky merges.
- Public/coach access to import data.

## Deliverables

- [ ] Analytics Import Players page.
- [ ] CSV upload form.
- [ ] Import preview page.
- [ ] Column mapping support.
- [ ] Import confirmation action.
- [ ] Conflict/ambiguous match review path.
- [ ] Row-level import error reporting.
- [ ] Provenance persistence via `players.PlayerSourceRow`.
- [ ] Tests for CSV parsing, matching, merging, conflicts, and permissions.

## Models

- Use Phase 1 `players` models.
- Add or finalize import metadata model if needed for uploaded file status, preview snapshot, row errors, conflict summary, and import summary.
- Prefer keeping import/provenance models in `players` unless a strong reason requires analytics-owned upload metadata.

## Services

- `players/services/import_service.py`
  - parse CSV data
  - normalize headers
  - build preview rows
  - apply column mappings
  - call matching service
  - create/update players
  - create source rows
  - record conflicts/errors
- `players/services/matching_service.py`
  - reusable matching from Phase 1
- `analytics/services` may contain thin orchestration for the UI only if needed.

## Views

- Staff/admin upload view.
- Staff/admin preview/mapping view.
- Staff/admin conflict review view.
- Staff/admin import confirmation view.
- Import result/detail view.

## Templates

- Upload form template.
- Preview/mapping template.
- Conflict review template.
- Import result template.

## URLs

- `/analytics/imports/`
- `/analytics/imports/new/`
- `/analytics/imports/<id>/preview/`
- `/analytics/imports/<id>/confirm/`
- `/analytics/imports/<id>/`

Exact names can follow project URL conventions.

## Admin

- Admin access to import metadata if an import model is created.
- Read-only or safe display of source rows/provenance.

## Migrations

- Migration for any import metadata model not created in Phase 1.
- Migration changes for additional source row/import fields discovered during implementation.

## Tests

- Staff/admin-only access to import workflow.
- CSV header normalization.
- CSV row parsing.
- Preview generation.
- Column mapping.
- Exact/high-confidence match merge.
- Ambiguous match handling.
- Conflict detection.
- New player creation.
- Source row preservation.
- Row-level error reporting.

## Acceptance Criteria

- Staff/admin can upload member-list and roster-detail CSV files.
- Staff/admin can preview rows before committing.
- Matching uses `players.services.matching_service`.
- High-confidence matches enrich existing players.
- Ambiguous matches require review.
- Original source rows and unmapped fields are preserved.
- Import errors are visible to staff/admin users.
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

- CSV source formats may contain inconsistent headers or sensitive fields.
- Conflict UI should be useful without becoming too complex for Version 1.
- Import metadata ownership should remain consistent with the players bounded context.

## Implementation Notes


## Phase Review

### What went well

### Challenges

### Technical debt

### Architecture changes

### Recommendations for the next phase

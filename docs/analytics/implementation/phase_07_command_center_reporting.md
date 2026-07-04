# Phase 07: Command Center and Reporting

## Purpose

Provide staff/admin users with the Version 1 Analytics Command Center and simple reporting summaries.

## Architecture References

- [07 Player Experience](../architecture/07_player_experience.md)
- [08 Reporting](../architecture/08_reporting.md)
- [09 Services](../architecture/09_services.md)
- [10 Permissions](../architecture/10_permissions.md)

## Existing Project Integration

Before implementing this phase, inspect relevant existing project conventions, including:

- dashboard/page layout conventions
- template partial patterns
- permission patterns for staff-only pages
- ORM aggregation patterns
- service-layer patterns for metrics/reporting
- test organization for summary services and views

## Scope

- Analytics Command Center.
- Completion tracking.
- Observation summaries.
- Import summaries.
- Draft matching summaries.
- Recent observations.
- Links to import, player search, Player Profile, timeline, and comparison pages.
- Simple server-rendered reports/cards/tables.

## Out of Scope

- Reporting engine.
- Saved filters.
- Report definitions.
- Report runs.
- Advanced charts.
- JavaScript-heavy visualizations.
- AI report generation.
- Non-`coach_assessment` workflow reporting.

## Deliverables

- [x] Analytics Command Center page.
- [x] Metrics service summaries.
- [x] Reporting service summaries.
- [x] Completion status cards/tables.
- [x] Import status summaries.
- [x] Draft matching summaries.
- [x] Recent observations list.
- [x] Tests for metrics and permissions.

## Models

- No new models expected.
- Use existing `players`, `analytics`, and `drafts` data.

## Services

- `analytics/services/metrics_service.py`
  - observation counts
  - completion counts
  - average scores
  - category averages
  - evaluator role summaries
  - unmatched draft counts
- `analytics/services/reporting_service.py`
  - command center summary payloads
  - simple report/table data

## Views

- Analytics Command Center view.
- Simple report/detail views only if needed for Version 1 summaries.

## Templates

- Command Center template.
- Summary card partials.
- Simple table partials.
- Empty/error state partials where useful.

## URLs

- `/analytics/`
- Optional simple report URLs if needed.

## Admin

- No new admin required.

## Migrations

- None expected.

## Tests

- Staff/admin access to Command Center.
- Non-staff restriction where applicable.
- Coach completion metrics.
- Observation count metrics.
- Average score metrics.
- Category score metrics.
- Evaluator role metrics.
- Import summary metrics.
- Draft matching summary metrics.
- Recent observations query.

## Acceptance Criteria

- Staff can access the Analytics Command Center.
- Command Center shows Version 1 summary cards/tables.
- Metrics use reusable services.
- Command Center links to import, player search, profiles/timelines, comparison, and review workflows.
- Reports remain simple server-rendered summaries and tables.
- Tests for this phase pass.

## Definition of Done

This phase is complete when:

- [x] All deliverables are complete.
- [x] Acceptance criteria are satisfied.
- [x] Tests for the phase pass.
- [x] Documentation is updated if implementation details changed.
- [x] Phase Review is completed.
- [x] `docs/analytics/implementation/STATUS.md` is updated.

## Risks / Open Questions

- Metrics should avoid excessive database queries.
- Empty-state handling is important before real data exists.
- Reporting should not grow into a full reporting engine in Version 1.

## Implementation Notes

Phase 7 added the staff-only command center at `/analytics/` using read-only service dataclasses and server-rendered tables.

Implementation followed the approved service boundaries:

- `analytics.services.player_service` owns reusable player search/filter/queryset helpers.
- `analytics.services.comparison_service` remains focused on comparison and score summaries.
- `analytics.services.metrics_service` owns counts, averages, completion metrics, import metrics, draft matching summaries, variance rows, and recent-observation queries.
- `analytics.services.reporting_service` assembles the grouped command center read model and navigation metadata from metrics service results.
- `analytics.services.draft_service` remains the owner of draft matching and `DraftContext` read models.

No models or migrations were added.

## Phase Review

### What went well

The existing Phase 5 and Phase 6 service boundaries made the command center straightforward to assemble without duplicating timeline, comparison, or draft matching logic.

### Challenges

The Phase 6 player search helpers originally lived in `comparison_service`, so Phase 7 moved that reusable search/filter logic into a dedicated `player_service` before adding reporting.

### Technical debt

Draft matching summaries currently call read-time draft context matching across drafts. This is acceptable for Version 1 but may need caching or denormalized reporting infrastructure if draft/player volume grows.

### Architecture changes

No architecture handbook changes were required. The implementation applied the approved Phase 7 engineering-plan clarification that Analytics-facing player search/filter logic belongs in `analytics.services.player_service`.

### Recommendations for the next phase

Before starting any future reporting expansion, decide whether the simple command center summaries are sufficient or whether a separate architecture phase is needed for saved reports, exports, charts, or cached metrics.

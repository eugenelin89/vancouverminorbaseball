# Phase 07: Command Center and Reporting

## Purpose

Provide staff/admin users with the Version 1 Analytics Command Center and simple reporting summaries.

## Architecture References

- [07 Player Experience](../architecture/07_player_experience.md)
- [08 Reporting](../architecture/08_reporting.md)
- [09 Services](../architecture/09_services.md)
- [10 Permissions](../architecture/10_permissions.md)

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

- Analytics Command Center page.
- Metrics service summaries.
- Reporting service summaries.
- Completion status cards/tables.
- Import status summaries.
- Draft matching summaries.
- Recent observations list.
- Tests for metrics and permissions.

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

## Risks / Open Questions

- Metrics should avoid excessive database queries.
- Empty-state handling is important before real data exists.
- Reporting should not grow into a full reporting engine in Version 1.

## Implementation Notes


## Phase Review


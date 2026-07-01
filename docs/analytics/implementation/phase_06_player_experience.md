# Phase 06: Player Experience

## Purpose

Create the practical staff-facing player experience for Version 1: search, Player Profile with timeline, and simple Player Comparison.

## Architecture References

- [07 Player Experience](../architecture/07_player_experience.md)
- [08 Reporting](../architecture/08_reporting.md)
- [09 Services](../architecture/09_services.md)

## Scope

- Player search/filtering.
- Player Profile page.
- Timeline section on Player Profile.
- Simple Player Comparison view.
- Timeline assembly service.
- Comparison service.

## Out of Scope

- Advanced dashboard visualizations.
- Future `TimelineEvent` abstraction.
- Measurements.
- AI/video timeline entries.
- Third-party imports in timeline.
- Advanced comparison dashboard.
- Parent/player portal views.

## Deliverables

- Player search page.
- Player Profile page with timeline.
- Player Comparison page.
- `analytics/services/timeline_service.py`.
- `analytics/services/comparison_service.py`.
- Search/filter helpers using `players` services/models.
- Tests for search, timeline, and comparison behavior.

## Models

- No new models expected.
- Use `players.Player`, `players.PlayerTag`, analytics observations/responses, and draft context services.

## Services

- `analytics/services/timeline_service.py`
  - assemble coach assessments
  - include imported player context
  - include draft context
  - sort timeline entries
- `analytics/services/comparison_service.py`
  - compare average scores
  - compare category scores
  - include coach notes
  - include evaluator count
  - include draft expectation vs actual draft
  - include team/division and tags

## Views

- Player search view.
- Player Profile/detail view.
- Player Comparison selection/result view.

## Templates

- Player search template.
- Player Profile template.
- Timeline partial/template.
- Player Comparison template.

## URLs

- `/analytics/players/`
- `/analytics/players/<player_id>/`
- `/analytics/players/compare/`

Exact route names can follow project conventions.

## Admin

- No new admin expected beyond player/admin configuration from earlier phases.

## Migrations

- None expected.

## Tests

- Search by name.
- Filter by team.
- Filter by division.
- Filter by birth year.
- Filter by draft status.
- Filter by tags.
- Filter by imported source.
- Filter by evaluation completion.
- Player Profile shows player details, tags, imported context, coach assessments, and draft context.
- Timeline includes coach assessments, imported player context, and draft context.
- Comparison includes average scores, category scores, notes, evaluator count, draft expectation vs actual draft, team/division, and tags.

## Acceptance Criteria

- Staff can search/filter players using simple server-rendered controls.
- Staff can open a Player Profile page.
- Timeline is visible on the Player Profile page.
- Player Comparison works for Version 1 comparison fields.
- No future timeline/event abstractions are implemented prematurely.
- Tests for this phase pass.

## Risks / Open Questions

- Search/filter performance may need basic indexes depending on data size.
- Comparison UI should stay simple and avoid becoming a full analytics dashboard.
- Timeline ordering rules should be simple and deterministic.

## Implementation Notes


## Phase Review


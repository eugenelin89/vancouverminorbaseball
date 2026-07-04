# Phase 06: Player Experience

## Purpose

Create the practical staff-facing player experience for Version 1: search, Player Profile with timeline, and simple Player Comparison.

## Architecture References

- [07 Player Experience](../architecture/07_player_experience.md)
- [08 Reporting](../architecture/08_reporting.md)
- [09 Services](../architecture/09_services.md)

## Existing Project Integration

Before implementing this phase, inspect relevant existing project conventions, including:

- template/layout conventions
- URL routing conventions
- search/filter form patterns
- permission patterns for staff and coaches
- service-layer patterns for read models
- test organization for page rendering and filters

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

- [x] Player search page.
- [x] Player Profile page with timeline.
- [x] Player Comparison page.
- [x] `analytics/services/timeline_service.py`.
- [x] `analytics/services/comparison_service.py`.
- [x] Search/filter helpers using `players` services/models.
- [x] Tests for search, timeline, and comparison behavior.

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

## Definition of Done

This phase is complete when:

- [x] All deliverables are complete.
- [x] Acceptance criteria are satisfied.
- [x] Tests for the phase pass.
- [x] Documentation is updated if implementation details changed.
- [x] Phase Review is completed.
- [x] `docs/analytics/implementation/STATUS.md` is updated.

## Risks / Open Questions

- Search/filter performance may need basic indexes depending on data size.
- Comparison UI should stay simple and avoid becoming a full analytics dashboard.
- Timeline ordering rules should be simple and deterministic.

## Implementation Notes

Implemented Phase 6 as staff-only, read-only player experience pages under `/analytics/players/`.

Timeline and comparison behavior use dataclasses/read models only. No timeline database model, reporting engine, charts, exports, AI summaries, player-facing views, parent portal views, new models, or migrations were added.

Draft context lookup from canonical `players.Player` was added to the existing Phase 5 draft context service so profile, timeline, comparison, and search filters can reuse the same read-only draft context behavior.

## Phase Review

### What went well

The existing service boundaries made it straightforward to assemble profile, timeline, comparison, import, tag, observation, and draft context data without changing underlying workflows.

### Challenges

Draft status filtering is limited by the absence of a persistent relationship between `drafts.DraftPlayer` and `players.Player`, so the implementation uses conservative read-only matching through the draft context service.

### Technical debt

Player-oriented draft context lookup scans draft rooms and should be revisited if draft data grows large. A persistent bridge should not be introduced without an architecture update.

### Architecture changes

None.

### Recommendations for the next phase

Keep Phase 7 focused on command center and reporting summaries. Reuse the Phase 6 timeline/comparison services and avoid duplicating player search or draft-context matching logic.

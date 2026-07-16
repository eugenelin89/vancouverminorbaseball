# Phase 6 Engineering Plan: Player Experience

> Historical implementation record.
> This document preserves the plan and decisions used during implementation. For current behavior, use [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the relevant subsystem summaries.

## Phase Goal

Create the practical staff-facing player experience for Version 1 of Analytics:

- player search and filtering
- Player Profile page
- Player Timeline section on the Player Profile page
- simple server-rendered Player Comparison page

Phase 6 should make existing player, import, coach assessment, and draft-context data easier for staff to inspect. It should not create new business workflows or mutate player, draft, import, or observation data.

## Strict Scope

Implement only these Phase 6 capabilities:

- Staff-only player search page.
- Staff-only Player Profile page.
- Staff-only Player Comparison page.
- `analytics/services/timeline_service.py`.
- `analytics/services/comparison_service.py`.
- Search/filter helper logic using `players.Player`, `players.PlayerTag`, `players.PlayerSourceRow`, Analytics observations, and existing draft context services.
- Server-rendered templates using the existing Analytics/PDP shell.
- Tests for service behavior, view permissions, filters, timeline assembly, and comparison output.

## Out Of Scope

Do not implement:

- Phase 7 Analytics Command Center.
- Dashboards.
- Charts.
- Exports.
- AI summaries.
- Reporting engine.
- Saved filters.
- Timeline database models.
- Future `TimelineEvent` abstraction.
- Measurements.
- Video, AI, attendance, awards, tryouts, or development milestone timeline entries.
- Player-facing or parent-facing portal pages.
- Coach assessment workflow changes.
- Draft workflow changes.
- Import workflow changes.
- New models or migrations unless an implementation blocker is found and approved separately.

## Files To Create

- `analytics/services/timeline_service.py`
- `analytics/services/comparison_service.py`
- `analytics/templates/analytics/player_search.html`
- `analytics/templates/analytics/player_profile.html`
- `analytics/templates/analytics/_player_timeline.html`
- `analytics/templates/analytics/player_compare.html`

## Files To Modify

- `analytics/views.py`
  - Add Phase 6 view classes.
  - Keep views thin and delegate query/read-model logic to services.
- `analytics/urls.py`
  - Add Phase 6 route names and paths.
- `analytics/tests.py`
  - Add Phase 6 service and view tests.
- `docs/analytics/implementation/STATUS.md`
  - Update only after implementation starts/completes in a later task.
- `docs/analytics/implementation/phase_06_player_experience.md`
  - Update only after implementation in a later task.

No changes are expected in `players`, `drafts`, or model files.

## URL Names And Paths

Use these URL patterns:

- Path: `/analytics/players/`
  - Name: `analytics:player-search`
  - View: `PlayerSearchView`
- Path: `/analytics/players/<int:player_id>/`
  - Name: `analytics:player-profile`
  - View: `PlayerProfileView`
- Path: `/analytics/players/compare/`
  - Name: `analytics:player-compare`
  - View: `PlayerComparisonView`

Place the `compare/` route before `<int:player_id>/` to avoid route ambiguity.

## View Classes

### PlayerSearchView

- Inherits from `AnalyticsStaffRequiredMixin` and `TemplateView`.
- Template: `analytics/player_search.html`.
- Reads GET filters.
- Calls a search helper/service function.
- Provides filter values, active tags, source choices, players, and result count to the template.
- Does not mutate data.

### PlayerProfileView

- Inherits from `AnalyticsStaffRequiredMixin` and `TemplateView`.
- Template: `analytics/player_profile.html`.
- Loads `players.Player` by `player_id`.
- Calls timeline service.
- Calls comparison/profile summary helpers as needed.
- Provides player, tags, source rows, submitted observations summary, draft context, and timeline entries.
- Does not allow editing.

### PlayerComparisonView

- Inherits from `AnalyticsStaffRequiredMixin` and `TemplateView`.
- Template: `analytics/player_compare.html`.
- Reads selected player IDs from `?players=<id>&players=<id>` and optionally `?player_ids=1,2`.
- Limits comparison to a small practical maximum, recommended 6 players.
- Calls `analytics.services.comparison_service`.
- Provides selected players, comparison rows, and available search result candidates if needed.
- Does not mutate data.

## Service Functions And Dataclasses

## `analytics/services/timeline_service.py`

### Dataclasses

`PlayerTimelineItem`

- `occurred_at`
- `sort_key`
- `kind`
- `title`
- `subtitle`
- `description`
- `metadata`
- `url`

`PlayerTimeline`

- `player`
- `items`
- `coach_assessment_count`
- `import_count`
- `draft_context_count`

### Functions

`get_player_timeline(player: Player) -> PlayerTimeline`

- Returns all Version 1 timeline items for one canonical player.
- Includes submitted coach-assessment observations.
- Includes imported player source rows.
- Includes draft context records that can be matched back to this player.
- Excludes draft/reopened observations.
- Excludes future timeline types.

`coach_assessment_timeline_items(player: Player) -> list[PlayerTimelineItem]`

- Uses `analytics.Observation`.
- Filters:
  - `observation_type_key="coach_assessment"`
  - `status="submitted"`
  - `player=player`
- Includes evaluator, evaluator role, cycle, submitted date, and optional assessment detail URL.

`import_timeline_items(player: Player) -> list[PlayerTimelineItem]`

- Uses `players.PlayerSourceRow`.
- Includes source, filename, row number, and imported timestamp.
- Does not expose raw source JSON in the main timeline.

`draft_context_timeline_items(player: Player) -> list[PlayerTimelineItem]`

- Reuses Phase 5 draft context lookup helpers where possible.
- Includes matched draft room, pick number, selected round, selected team, and unmatched state where appropriate.
- Does not duplicate draft selection logic.

`get_draft_contexts_for_player(player: Player) -> list[DraftContext]`

- Add this function to `analytics.services.draft_service` during implementation if needed.
- It should derive player-oriented draft contexts from existing Phase 5 logic instead of duplicating matching, pick, and round calculations.
- It must remain read-only.

## `analytics/services/comparison_service.py`

### Dataclasses

`PlayerScoreSummary`

- `player`
- `average_rating`
- `rating_count`
- `submitted_observation_count`
- `evaluator_count`
- `category_scores`
- `notes`
- `tags`
- `draft_contexts`

`CategoryScoreSummary`

- `category`
- `average_rating`
- `rating_count`

`PlayerComparison`

- `players`
- `summaries`
- `category_names`
- `empty`

### Functions

`get_player_score_summary(player: Player) -> PlayerScoreSummary`

- Uses submitted coach assessments only.
- Computes overall average from `rating_1_5` responses.
- Computes category averages by `ObservationQuestion.category`.
- Includes submitted observation count.
- Includes distinct evaluator count.
- Includes text notes from submitted coach assessments.
- Includes active tags.
- Includes draft context from `draft_service`.

`get_player_comparison(players: Iterable[Player]) -> PlayerComparison`

- Preserves selected player order.
- Calls `get_player_score_summary()` for each player.
- Builds a union of category names for table rendering.
- Handles empty selections.

## Player Search / Filter Semantics

The player search page should query `players.Player` and return active players by default.

### Query Parameter Names

- `q`
- `team`
- `division`
- `birth_year`
- `tag`
- `source`
- `evaluation`
- `draft_status`
- `include_inactive`

### Name Search

Parameter: `q`

Search fields:

- `first_name`
- `last_name`
- `preferred_name`

Use case-insensitive containment. Keep this simple; do not add fuzzy search.

### Team Filter

Parameter: `team`

Filter:

- `team_name__iexact=team`

Ignore blank values.

### Division Filter

Parameter: `division`

Filter:

- `division__iexact=division`

Ignore blank values.

### Birth Year Filter

Parameter: `birth_year`

Filter:

- exact integer match on `birth_year`

Invalid values should be ignored rather than crashing.

### Tag Filter

Parameter: `tag`

Filter:

- active `players.PlayerTag.slug`

Use `players.services.tag_service.active_tags()` for filter choices.

### Imported Source Filter

Parameter: `source`

Filter:

- players with at least one `PlayerSourceRow.source` equal to the selected source

Source choices should come from distinct `PlayerSourceRow.source` values ordered alphabetically.

### Include Inactive

Parameter: `include_inactive`

Default behavior:

- only `Player.is_active=True`

If `include_inactive=1`, include inactive players.

This should be staff-only and simple.

## Draft Status Filter Semantics

Parameter: `draft_status`

Supported values:

- blank: all players
- `drafted`: player has at least one matched draft context with a pick number or selected/current team
- `available`: player has at least one matched draft context but no pick/current team
- `unmatched`: at least one draft player appears to correspond by name search inputs but cannot be confidently matched is not reliable from canonical player search; for Phase 6, define this as players with no matched draft context when draft data exists for their division/name
- `no_draft_context`: player has no draft context

Implementation guidance:

- Prefer service-backed filtering over complex view queries.
- If efficient filtering is difficult without a model-level link, compute draft-status filters in the search helper after applying basic database filters.
- Keep the first implementation conservative and deterministic.
- Do not create a bridge model in Phase 6.
- Do not mutate draft data.

If the `unmatched` semantics are too expensive or ambiguous during implementation, implement `drafted`, `available`, and `no_draft_context` first and document `unmatched` as an open question before coding.

## Evaluation Completion Filter Semantics

Parameter: `evaluation`

Supported values:

- blank: all players
- `has_submitted`: at least one submitted coach assessment
- `no_submitted`: no submitted coach assessments
- `has_any`: at least one coach assessment in any status
- `not_started`: no coach assessment observations

Rules:

- Submitted means `Observation.status == "submitted"` and `observation_type_key == "coach_assessment"`.
- Any means any status for `coach_assessment`.
- Use annotations or service-backed ID sets to avoid N+1 queries.

## Player Profile Layout

Template: `analytics/player_profile.html`

Use the existing Analytics shell and PDP card/table classes.

Sections:

1. Header
   - Player display name.
   - Division, team, birth year, active status.
   - Back link to player search.
   - Link to comparison with this player selected.

2. Player Details
   - First name, last name, preferred name.
   - Birthdate/birth year.
   - Team/division.
   - Bats/throws/positions/school/graduation year when available.

3. Tags
   - Active tags assigned to the player.
   - Empty state: “No tags assigned.”

4. Imported Context
   - Source rows summarized by source, filename, row number, imported date.
   - Do not display raw `original_row` JSON by default.
   - Empty state: “No imported source rows.”

5. Draft Context
   - Reuse Phase 5 draft context information.
   - Show draft room, selected team, pick, round, and match status.
   - Empty state: “No draft context found.”

6. Coach Assessments
   - Submitted coach assessment count.
   - Evaluator count.
   - Latest submitted assessment.
   - Link to existing observation review/detail where appropriate.

7. Timeline
   - Include `_player_timeline.html`.

## Timeline Item Shape

Timeline entries are read-model dataclasses only. Do not create a timeline database table.

Fields:

- `occurred_at`: datetime/date used for display and ordering.
- `sort_key`: tuple or datetime fallback used for deterministic ordering.
- `kind`: one of:
  - `coach_assessment`
  - `import`
  - `draft_context`
- `title`: short display label.
- `subtitle`: secondary display text.
- `description`: optional longer text.
- `metadata`: dict for small display-safe values.
- `url`: optional internal URL for details.

Do not include raw import JSON in timeline metadata.

## Timeline Ordering Rules

Default ordering:

1. Newest `occurred_at` first.
2. If timestamps tie, order by kind priority:
   - `coach_assessment`
   - `draft_context`
   - `import`
3. If still tied, order by stable source id descending when available.

Timestamp selection:

- coach assessment: `submitted_at`
- import: `imported_at`
- draft context: draft action `created_at` when selected, otherwise draft player `updated_at`/`created_at`

Entries with no timestamp should sort last.

## Comparison Page Behavior

Template: `analytics/player_compare.html`

Behavior:

- Staff can select players by query string.
- Accept repeated `players` parameters and/or comma-separated `player_ids`.
- Maximum selected players: 6.
- If no players are selected, show a simple selection/search form and empty state.
- If players are selected, show a table with one column per player or one row per player, whichever is simpler in the existing CSS.

Version 1 comparison fields:

- Display name.
- Team.
- Division.
- Tags.
- Submitted assessment count.
- Evaluator count.
- Overall average rating.
- Category average ratings.
- Coach notes.
- Draft status.
- Expected draft round, when available.
- Actual selected round/pick/team, when available.

Do not add charts or dashboard widgets.

## Draft Context Lookup From Canonical `players.Player`

Current Phase 5 draft context starts from `drafts.DraftPlayer`.

Phase 6 needs player-oriented lookup:

- Add read-only helper in `analytics.services.draft_service`, if needed:
  - `get_draft_contexts_for_player(player: Player) -> list[DraftContext]`
  - `get_draft_contexts_for_players(players: Iterable[Player]) -> dict[int, list[DraftContext]]`

These helpers should:

- Reuse existing `get_draft_contexts_for_draft()` and `match_draft_player_to_player()`.
- Avoid duplicating pick/round logic.
- Return only contexts confidently matched to the canonical player.
- Treat ambiguous matches as unmatched.
- Never create or update draft/player records.

If performance becomes an issue, document it as technical debt. Do not add a bridge model in Phase 6.

## Permission Model

Phase 6 is staff-only.

All Phase 6 views should use `AnalyticsStaffRequiredMixin`.

Access rules:

- Anonymous users redirect to login.
- Authenticated non-staff users receive 403.
- Staff and superusers can access player search, profile, and comparison.

Do not introduce player/parent-facing permissions in Phase 6.

## Empty States

Player search:

- No matching players: “No players match this search.”

Player profile:

- No tags: “No tags assigned.”
- No source rows: “No imported source rows.”
- No draft context: “No draft context found.”
- No submitted coach assessments: “No submitted coach assessments yet.”
- Empty timeline: “No timeline entries yet.”

Comparison:

- No selected players: “Select players to compare.”
- Selected player has no submitted assessments: show blanks or “No submitted assessments.”
- Selected player has no category score: show “-”.
- Selected player has no draft context: show “No draft context.”

## Tests To Write

### Timeline Service Tests

- Timeline includes submitted coach assessments.
- Timeline excludes draft observations.
- Timeline excludes reopened observations.
- Timeline includes imported source rows.
- Timeline includes draft context for matched players.
- Timeline handles no entries.
- Timeline ordering is newest-first and deterministic.

### Comparison Service Tests

- Computes overall average score from submitted rating responses.
- Computes category averages from submitted rating responses.
- Counts distinct evaluators.
- Includes coach notes from submitted text responses.
- Excludes draft/reopened observations.
- Includes tags.
- Includes draft context.
- Handles players with no observations.
- Preserves selected player order.

### Player Search View Tests

- Requires login.
- Requires staff.
- Search by name.
- Filter by team.
- Filter by division.
- Filter by birth year.
- Filter by tag.
- Filter by imported source.
- Filter by evaluation completion:
  - `has_submitted`
  - `no_submitted`
  - `has_any`
  - `not_started`
- Filter by draft status:
  - `drafted`
  - `available`
  - `no_draft_context`
- Invalid filter values do not crash.

### Player Profile View Tests

- Requires staff.
- Renders player details.
- Renders tags.
- Renders imported context summary.
- Renders submitted coach assessment summary.
- Renders draft context.
- Renders timeline entries.
- Does not display raw import JSON by default.

### Player Comparison View Tests

- Requires staff.
- Handles no selected players.
- Handles selected players.
- Enforces maximum selected players.
- Displays average score, category scores, evaluator count, notes, tags, and draft context.

### Regression Tests

- Existing coach assessment workflow still renders.
- Existing staff review workflow still renders.
- Existing draft command center still renders.
- Existing import list still renders.

## Implementation Sequence

1. Add service read models and timeline service.
2. Add player-oriented draft context helper in `analytics.services.draft_service` only if needed.
3. Add comparison service.
4. Add Phase 6 view classes in `analytics/views.py`.
5. Add Phase 6 URL patterns in `analytics/urls.py`.
6. Add player search template.
7. Add player profile template and timeline partial.
8. Add comparison template.
9. Add service tests.
10. Add view tests.
11. Run:
    - `python manage.py makemigrations analytics --check`
    - `python manage.py test analytics`
    - `python manage.py test players`
    - `python manage.py test drafts`
    - `python manage.py test`
12. Update Phase 6 tracking document and `STATUS.md` only after implementation is complete.

## Risks / Open Questions

- Draft status filtering is limited by the lack of a persistent canonical link between `drafts.DraftPlayer` and `players.Player`.
- Player-oriented draft context may be less efficient because Phase 5 draft context starts from draft rooms.
- The architecture mentions basic reports on the profile, but Phase 6 should avoid becoming a reporting engine or Phase 7 dashboard.
- Expected draft round exists only when a question has a recognized key or metadata. The default question set does not currently guarantee such a question.
- Search/filter result counts may be inefficient if draft-status filtering is applied in Python after database filters.
- The comparison page should remain small; adding charts or trend analysis would violate scope.

## Definition Of Done

Phase 6 is done when:

- Staff can search and filter players at `/analytics/players/`.
- Staff can open a Player Profile page at `/analytics/players/<player_id>/`.
- Player Profile displays player details, tags, imported context, submitted coach assessment context, draft context, and timeline.
- Staff can compare selected players at `/analytics/players/compare/`.
- Timeline service uses dataclasses/read models only.
- Comparison service uses dataclasses/read models only.
- No new models or migrations are introduced.
- No Phase 7 command center/reporting dashboard work is implemented.
- No charts, exports, AI summaries, player-facing views, or timeline database models are implemented.
- Required Phase 6 tests pass.
- Existing Phase 1-5 tests continue to pass.
- `docs/analytics/implementation/phase_06_player_experience.md` is updated after implementation.
- `docs/analytics/implementation/STATUS.md` is updated after implementation.

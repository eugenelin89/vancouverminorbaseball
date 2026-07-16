# Phase 7 Engineering Plan: Command Center And Reporting

> Historical implementation record.
> This document preserves the plan and decisions used during implementation. For current behavior, use [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the relevant subsystem summaries.

## Phase Goal

Provide staff/admin users with the Version 1 Analytics Command Center and simple reporting summaries.

Phase 7 should make the completed Phase 1-6 workflows easier to monitor and navigate:

- player search and profile links
- coach assessment completion
- observation summaries
- import summaries
- draft matching summaries
- recent submitted observations
- simple server-rendered reporting tables

This phase should not create a reporting platform. It should expose practical, read-only summaries using services and templates.

## Scope

Implement only:

- Staff-only Analytics Command Center at `/analytics/`.
- `analytics/services/player_service.py`.
- `analytics/services/metrics_service.py`.
- `analytics/services/reporting_service.py`.
- Read-model/dataclass summaries for command center cards and tables.
- Server-rendered command center template.
- Small reusable card/table partials if helpful.
- Staff-only navigation links to existing Analytics pages:
  - imports
  - player search
  - player profiles/timelines
  - player comparison
  - coach assessments
  - staff observation review
- Tests for metrics, reporting payloads, permissions, rendering, links, and empty states.

## Out Of Scope

Do not implement:

- Reporting engine.
- Saved filters.
- Report definitions.
- Report runs.
- Advanced charts.
- JavaScript-heavy visualizations.
- Exports.
- AI report generation.
- Non-`coach_assessment` workflow reporting.
- New database models.
- New migrations.
- Player-facing or parent-facing reporting pages.
- Changes to coach assessment submission behavior.
- Changes to player import behavior.
- Changes to draft workflow behavior.
- Changes to Phase 6 player search/profile/comparison behavior.

## Files To Create

- `analytics/services/player_service.py`
- `analytics/services/metrics_service.py`
- `analytics/services/reporting_service.py`
- `analytics/templates/analytics/command_center.html`
- `analytics/templates/analytics/_summary_card.html` if useful
- `analytics/templates/analytics/_simple_table_empty.html` if useful

## Files To Modify

- `analytics/views.py`
  - Add the command center view.
  - Keep the view thin.
  - Update existing Phase 6 player search/profile/comparison views to consume `analytics.services.player_service` for player lookup/search helpers where applicable.
- `analytics/urls.py`
  - Add `/analytics/` route before more specific paths if needed.
- `analytics/tests.py`
  - Add Phase 7 service and view tests.
  - Add or adjust tests proving player search/filter behavior is preserved after moving search logic to `player_service`.
- `docs/analytics/implementation/STATUS.md`
  - Mark Phase 7 active/in progress during implementation.
  - Mark complete only after implementation and tests pass.
- `docs/analytics/implementation/phase_07_command_center_reporting.md`
  - Update checklist and Phase Review after implementation.

The Phase 7 tracking document exists at `docs/analytics/implementation/phase_07_command_center_reporting.md`.

No changes are expected in:

- `players/models.py`
- `analytics/models.py`
- `drafts/models.py`
- migrations

## URLs

Use this route:

- Path: `/analytics/`
- Name: `analytics:command-center`
- View: `AnalyticsCommandCenterView`

Keep existing routes unchanged:

- `/analytics/players/`
- `/analytics/players/<int:player_id>/`
- `/analytics/players/compare/`
- `/analytics/imports/`
- `/analytics/assessments/`
- `/analytics/observations/review/`

The command center should link to these existing routes instead of rebuilding their behavior.

## View Classes

### AnalyticsCommandCenterView

- Inherits from `AnalyticsStaffRequiredMixin`.
- Template: `analytics/command_center.html`.
- Calls `analytics.services.reporting_service.get_command_center_context()`.
- Adds only minimal request-derived filter context if needed.
- Does not perform metrics calculations directly.
- Does not mutate data.

Example context keys:

- `command_center`
- `summary_cards`
- `completion_summary`
- `observation_summary`
- `import_summary`
- `draft_summary`
- `recent_observations`
- `navigation_links`

## Service Responsibilities

## `analytics/services/player_service.py`

Owns reusable Analytics-facing player search/filter logic and player lists used by staff pages and reports.

Responsibilities:

- parse/normalize player filter inputs when a plain dictionary or request-like query object is supplied
- search/filter canonical `players.Player` records
- expose active player querysets/lists for metrics and reporting
- expose reusable source/tag filter choices for staff pages
- provide helper functions for player ID sets used by metrics

Phase 7 should move player search/filtering out of `analytics.services.comparison_service` into this dedicated service boundary. During implementation, update Phase 6 player search/profile/comparison views to consume `player_service` rather than keeping search logic in `comparison_service`.

Consumers:

- Player Search should use `player_service`.
- Player Profile should use `player_service` for reusable player/profile lookup helpers if needed.
- Player Comparison should use `player_service` for selected-player lookup and search candidate lists.
- Command Center and Reporting should use `player_service` for player filters and active player populations.

Boundaries:

- `player_service` may call `players` models/services because `players` owns canonical identity.
- `player_service` should not compute score summaries, draft metrics, timeline entries, or command center cards.
- Reporting must not duplicate player search/filtering logic.
- `comparison_service` should focus only on comparison and score summaries.

## `analytics/services/metrics_service.py`

Owns reusable metric calculations. It should not know about template layout.

Responsibilities:

- observation counts
- submitted/draft/reopened counts
- player counts
- coach assessment completion counts
- assessment count by player
- assessment count by evaluator role
- average score by category
- average score by evaluator role
- coach-to-coach score variance by player/category
- recent submitted observations
- import status counts
- import error and ambiguous/review counts
- draft matching summary counts
- players whose expected draft round differs from actual draft selection
- players with no draft context

Reuse existing services:

- Use `analytics.services.player_service` for player populations and filters.
- Use `analytics.services.comparison_service.get_player_score_summary()` where per-player scoring summaries are needed.
- Use `analytics.services.draft_service.get_draft_contexts_for_players()` and existing `DraftContext` read models for draft matching summaries.
- Use `analytics.services.coach_assessment_service.get_active_coach_assessment_cycle()` for active-cycle defaults.
- Use `players.Player`, `players.PlayerImportBatch`, `players.PlayerSourceRow`, and `players.PlayerTag` for player/import counts.
- Use `analytics.Observation` and `analytics.ObservationResponse` for observation metrics.

Do not duplicate:

- player search/filtering logic from `analytics.services.player_service`
- draft matching logic from `analytics.services.draft_service`
- timeline assembly from `analytics.services.timeline_service`
- comparison score summary logic from `analytics.services.comparison_service`

Draft matching remains owned by `analytics.services.draft_service`. `metrics_service.py` may call `draft_service` for `DraftContext` read models, but it must not duplicate draft matching rules, pick/round calculation rules, or canonical-player matching rules.

## `analytics/services/reporting_service.py`

Owns command center payload assembly and simple table/report read models.

Responsibilities:

- call metrics service functions
- assemble command center read model
- build summary card read models
- build table row read models
- centralize command center navigation metadata
- return template-ready dataclasses/read models

It should not run raw aggregation logic that belongs in `metrics_service.py`.

Separation rule:

- `metrics_service.py` computes counts, averages, summaries, and metric rows.
- `reporting_service.py` assembles command center read models, cards, navigation links, and grouped sections from metrics service results.
- `reporting_service.py` should not contain ORM aggregation logic or duplicate player/draft/timeline/comparison logic.

## Read Models / Dataclasses

Use dataclasses/read models only.

Recommended dataclasses:

### `MetricCard`

- `label`
- `value`
- `help_text`
- `url`
- `status`

### `CompletionSummary`

- `active_cycle`
- `total_active_players`
- `players_with_submitted_assessment`
- `players_without_submitted_assessment`
- `submitted_observation_count`
- `draft_observation_count`
- `reopened_observation_count`
- `completion_rate`

### `ObservationSummary`

- `total_observations`
- `submitted_count`
- `draft_count`
- `reopened_count`
- `by_evaluator_role`
- `by_category_average`
- `by_role_average`

### `ImportSummary`

- `total_batches`
- `uploaded_count`
- `previewed_count`
- `needs_review_count`
- `committed_count`
- `failed_count`
- `recent_batches`
- `rows_created`
- `rows_updated`
- `rows_skipped`
- `rows_conflicted`

### `DraftMatchingSummary`

- `matched_player_count`
- `drafted_player_count`
- `available_player_count`
- `no_context_player_count`
- `unmatched_draft_player_count`
- `expected_round_mismatch_count`
- `mismatches`
- `players_without_draft_context`

### `RecentObservationRow`

- `observation`
- `player`
- `evaluator_name`
- `evaluator_role`
- `cycle_name`
- `submitted_at`
- `detail_url`
- `player_profile_url`

### `CommandCenterContext`

- `summary_cards`
- `completion_summary`
- `observation_summary`
- `import_summary`
- `draft_summary`
- `recent_observations`
- `navigation_links`
- `generated_at`

Keep `CommandCenterContext` as a small top-level object containing grouped dataclasses. Do not add many flat metric fields directly to `CommandCenterContext`; put detailed data inside the grouped summary dataclasses above.

## Dashboard Layout

Template: `analytics/command_center.html`

Use the existing Analytics base template and PDP card/table styles.

Recommended layout:

1. Header
   - Title: `Analytics Command Center`
   - Subtitle: staff/admin read-only overview.

2. Quick Actions
   - Player Search
   - Compare Players
   - Import Players
   - Coach Assessments
   - Observation Review

3. Summary Cards
   - Active players
   - Submitted assessments
   - Completion rate
   - Imports needing review
   - Drafted/matched players
   - Recent observations

4. Coach Completion
   - Active cycle name.
   - total active players.
   - players with submitted assessment.
   - players without submitted assessment.
   - completion percentage.

5. Observation Summary
   - counts by status.
   - assessment count by evaluator role.
   - average score by category.
   - average score by evaluator role.

6. Import Summary
   - batch status counts.
   - rows created/updated/skipped/conflicted.
   - recent import batches.
   - link to import list and review pages.

7. Draft Matching Summary
   - matched/drafted/available/no-context counts.
   - players with expected-vs-actual round mismatch.
   - players without draft context.
   - links to affected player profiles where possible.

8. Recent Observations
   - latest submitted coach assessments.
   - player, evaluator, role, cycle, submitted date.
   - links to observation detail/review and Player Profile.

Do not add charts. Tables and summary cards only.

## Reporting Components

Version 1 reporting components are simple server-rendered summaries:

- summary cards
- short tables
- links to existing detailed workflows
- empty states

Do not add:

- report builder UI
- saved reports
- export buttons
- charts
- async jobs
- background report runs

If additional report/detail URLs seem useful, defer them unless the Phase 7 tracking document explicitly requires them.

## Aggregation Rules

### Observation Counts

Include only `observation_type_key == "coach_assessment"` for Phase 7 metrics.

Status counts:

- draft
- submitted
- reopened
- archived only if present

### Completion Counts

Default cycle:

- Use `get_active_coach_assessment_cycle()`.

Active players:

- `players.Player.is_active=True`.

Player is complete if:

- at least one submitted `coach_assessment` observation exists for that player in the active cycle.

Player is incomplete if:

- active player has no submitted `coach_assessment` observation in the active cycle.

Completion rate:

- `players_with_submitted_assessment / total_active_players`.
- If total active players is zero, completion rate is `0`.

### Average Scores

Use only:

- submitted `coach_assessment` observations
- `ObservationResponse.response_type == "rating_1_5"`
- non-null `numeric_value`

Category average:

- group by `ObservationQuestion.category`, falling back to `"Questions"`.

Evaluator role average:

- group by `Observation.evaluator_role_key` and display `evaluator_role_name`, falling back to `"Unknown role"`.

### Coach-To-Coach Variance

Version 1 should keep this simple:

- group by player and question category.
- compute min average and max average across evaluators when at least two evaluators submitted assessments for that player/category.
- variance value is `max_average - min_average`.
- surface only top rows, recommended 10.

Do not implement statistical variance formulas unless explicitly requested later.

### Import Summary

Use `players.PlayerImportBatch`.

Counts:

- total batches
- uploaded
- previewed
- needs review
- committed
- failed
- cancelled

Rows:

- sum `rows_created`
- sum `rows_updated`
- sum `rows_skipped`
- sum `rows_conflicted`

Recent batches:

- order by newest created date.
- recommended limit: 5.

### Draft Matching Summary

Use existing `analytics.services.draft_service` read models.

Draft matching responsibility stays in `analytics.services.draft_service`.

`metrics_service.py` may call draft service helpers such as `get_draft_contexts_for_players()` to receive `DraftContext` read models. It must not reimplement:

- draft player to canonical player matching
- ambiguous match handling
- pick number lookup
- selected round calculation
- expected-round extraction from observation responses

Canonical players:

- active players only by default.

Matched:

- player has at least one confident draft context.

Drafted:

- context has `pick_number`, `selected_team`, or `current_team`.

Available:

- context exists but has no pick/current team.

No context:

- active player has no confident draft context.

Unmatched draft player:

- draft player context has no matched canonical `players.Player`.

Expected-vs-actual mismatch:

- expected round is present in draft observation summary.
- actual selected round is present.
- compare as normalized strings or integers when possible.
- mismatch when values differ.

### Recent Observations

Use submitted `coach_assessment` observations only.

Order:

- `submitted_at` descending.
- `id` descending as tie breaker.

Recommended limit:

- 10.

## Filtering Semantics

Phase 7 command center should start with minimal filters:

- `cycle`
- `division`
- `team`

### Cycle Filter

Parameter: `cycle`

- blank: active coach assessment cycle from `get_active_coach_assessment_cycle()`.
- integer: specific `EvaluationCycle.id`.
- invalid value: ignore and use active cycle.

### Division Filter

Parameter: `division`

- filters active players and completion metrics by `Player.division__iexact`.
- filters observations through `Observation.player`.
- blank means all divisions.

### Team Filter

Parameter: `team`

- filters active players and completion metrics by `Player.team_name__iexact`.
- filters observations through `Observation.player`.
- blank means all teams.

Do not add advanced saved filters in Phase 7.

## Sorting Semantics

Recent observations:

- newest submitted first.

Recent imports:

- newest created first.

Players without draft context:

- last name, first name, id.

Expected-vs-actual mismatches:

- selected round, pick number, player last name, player first name.

Category averages:

- category name ascending.

Evaluator role summaries:

- role display name ascending.

Variance rows:

- largest spread first.

## Empty States

Command center:

- No active cycle: show “No active coach assessment cycle is available.”
- No active players: show “No active players found.”
- No observations: show “No coach assessment observations yet.”
- No recent observations: show “No submitted observations yet.”
- No import batches: show “No player imports yet.”
- No imports needing review: show “No imports currently need review.”
- No draft contexts: show “No draft context found.”
- No expected-vs-actual mismatches: show “No expected-vs-actual draft round mismatches found.”

Empty states should be plain text inside the relevant card/table. Do not hide whole sections unless the section cannot be interpreted without data.

## Permissions

Phase 7 is staff-only.

Use `AnalyticsStaffRequiredMixin`.

Rules:

- anonymous users redirect to login.
- authenticated non-staff users receive 403.
- staff and superusers can access the command center.

Do not implement player/parent access.

Do not expose sensitive raw import JSON, addresses, guardian/contact info, medical notes, or private source-row payloads.

## Performance Considerations

Phase 7 is read-heavy and should avoid N+1 query patterns.

Use:

- `select_related()` for observation player, evaluator, evaluator role, cycle.
- `prefetch_related()` for responses/questions when computing score metrics.
- database aggregation for simple counts and averages where practical.
- existing services for higher-level read models.
- small limits for recent rows and variance/mismatch lists.

Do not introduce:

- caching layer
- background jobs
- materialized report tables
- denormalized metrics models

If metrics become slow, document the issue as technical debt after implementation.

## Tests To Write

### Metrics Service Tests

- player population/filter helpers come from `player_service`, not reporting or comparison code.
- observation status counts include only coach assessments.
- completion metrics use active cycle by default.
- completion metrics respect cycle filter.
- completion metrics respect division/team filters.
- average score by category uses submitted rating responses only.
- average score by evaluator role uses submitted rating responses only.
- draft/reopened observations are excluded from submitted metrics.
- coach-to-coach spread rows require at least two evaluators.
- import summary counts statuses and row totals.
- draft matching summary counts matched, drafted, available, no context, unmatched draft players.
- expected-vs-actual mismatch detects mismatch when both values exist.
- recent observations ordered newest first and limited.

### Reporting Service Tests

- command center context is a small grouped object and does not expose many flat metric fields.
- command center context includes summary cards.
- command center context includes completion summary.
- command center context includes observation summary.
- command center context includes import summary.
- command center context includes draft summary.
- navigation links point to existing route names.
- empty datasets return usable empty read models.

### View Tests

- command center requires login.
- command center requires staff.
- staff user can render command center.
- command center includes links to imports, player search, comparison, assessments, and observation review.
- command center renders empty states.
- command center renders populated summary cards/tables.
- invalid cycle filter does not crash.
- division/team filters are passed through to reporting service results.

### Regression Tests

- player search page still renders.
- player profile page still renders.
- player comparison page still renders.
- import list still renders.
- coach assessment list still renders.
- staff observation review list still renders.
- draft command center still renders.

## Implementation Sequence

1. Add `analytics/services/player_service.py` and move reusable player search/filter helpers out of `comparison_service.py`.
2. Update Phase 6 player search/profile/comparison views to consume `player_service` for player search, selected-player lookup, source choices, active tags, and player populations.
3. Keep `comparison_service.py` focused on comparison and score summaries.
4. Add `analytics/services/metrics_service.py` with dataclasses and metric functions.
5. Add `analytics/services/reporting_service.py` with command center read models.
6. Add `AnalyticsCommandCenterView` to `analytics/views.py`.
7. Add `/analytics/` route to `analytics/urls.py`.
8. Add `analytics/templates/analytics/command_center.html`.
9. Add small partials only if they reduce duplication.
10. Add player service regression tests.
11. Add metrics service tests.
12. Add reporting service tests.
13. Add command center view tests.
14. Add regression tests for existing Phase 1-6 pages.
15. Run:
    - `python manage.py makemigrations analytics --check`
    - `python manage.py test analytics`
    - `python manage.py test players`
    - `python manage.py test drafts`
    - `python manage.py test`
16. Update `docs/analytics/implementation/phase_07_command_center_reporting.md`.
17. Update `docs/analytics/implementation/STATUS.md`.

## Risks / Open Questions

- Expected draft round is not guaranteed by the default question set. Mismatch metrics should handle absent expected round values gracefully.
- Draft matching still relies on conservative read-time matching between `drafts.DraftPlayer` and `players.Player`; this may become expensive with large draft datasets.
- Coach-to-coach spread can be interpreted several ways. Phase 7 should use simple max-minus-min spread, not statistical variance.
- Completion metrics need a clear default cycle. Use `get_active_coach_assessment_cycle()`.
- Reporting can easily expand beyond Version 1. Keep Phase 7 limited to summary cards and tables.

## Definition Of Done

Phase 7 is done when:

- Staff can access `/analytics/`.
- Non-staff users cannot access `/analytics/`.
- Command center shows summary cards and simple tables for:
  - completion tracking
  - observation summaries
  - import summaries
  - draft matching summaries
  - recent observations
- Command center links to existing import, player search, profile/timeline, comparison, assessment, and review workflows.
- Metrics and reporting logic live in services.
- Views remain thin.
- Templates remain presentation-only.
- No new models or migrations are introduced.
- No dashboards, charts, exports, saved reports, report definitions, AI summaries, or reporting engine are introduced.
- Player search/filter logic lives in `analytics.services.player_service`.
- `comparison_service.py` contains comparison/score summary logic only.
- Draft matching remains in `analytics.services.draft_service`.
- `reporting_service.py` assembles grouped read models and does not contain raw aggregation logic.
- Required Phase 7 tests pass.
- Existing Phase 1-6 tests continue to pass.
- `docs/analytics/implementation/phase_07_command_center_reporting.md` is updated.
- `docs/analytics/implementation/STATUS.md` is updated.

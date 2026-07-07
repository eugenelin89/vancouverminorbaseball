**Repository Discovery**
Current incomplete phase: **Phase 6 - Player Experience**

Docs found and read:
- [docs/analytics/implementation/STATUS.md](/Users/eugenelin/dev/vmba0/docs/analytics/implementation/STATUS.md)
- [docs/analytics/architecture/README.md](/Users/eugenelin/dev/vmba0/docs/analytics/architecture/README.md)
- [docs/analytics/implementation/phase_06_player_experience.md](/Users/eugenelin/dev/vmba0/docs/analytics/implementation/phase_06_player_experience.md)
- [docs/analytics/architecture/07_player_experience.md](/Users/eugenelin/dev/vmba0/docs/analytics/architecture/07_player_experience.md)
- [docs/analytics/architecture/08_reporting.md](/Users/eugenelin/dev/vmba0/docs/analytics/architecture/08_reporting.md)
- [docs/analytics/architecture/09_services.md](/Users/eugenelin/dev/vmba0/docs/analytics/architecture/09_services.md)
- [docs/analytics/architecture/90_implementation_roadmap.md](/Users/eugenelin/dev/vmba0/docs/analytics/architecture/90_implementation_roadmap.md)
- [docs/analytics/implementation/repository_assessment.md](/Users/eugenelin/dev/vmba0/docs/analytics/implementation/repository_assessment.md)

Missing:
- No `docs/analytics/implementation/engineering/phase_06_player_experience.md` exists.
- The `implementation/README.md` “Current engineering plans” section only lists Phase 1, even though engineering plans exist for Phases 1-4.
- No detailed Phase 6 engineering design exists for exact URL names, filter semantics, comparison layout, timeline item shape, or draft-status filter behavior.

**Existing Implementation Review**
Reusable code already present:
- Models:
  - `players.Player`, `PlayerTag`, `PlayerSourceRow`, `PlayerImportBatch`
  - `analytics.Observation`, `ObservationResponse`, `ObservationQuestion`, `EvaluationCycle`
  - `drafts.Draft`, `DraftPlayer`, `DraftAction`, `DraftTeam`
- Services:
  - `analytics.services.observation_service`
  - `analytics.services.coach_assessment_service`
  - `analytics.services.draft_service`
  - `analytics.services.permissions`
  - `players.services.tag_service`
  - `players.services.matching_service`
  - `players.services.import_service`
- Views/templates:
  - Analytics uses `analytics/base.html`, extending the PDP shell.
  - Views are class-based and thin.
  - Tables/forms are server-rendered.
  - Staff-only workflows use `AnalyticsStaffRequiredMixin`.
- Existing URL namespace:
  - `/analytics/assessments/`
  - `/analytics/observations/review/`
  - `/analytics/imports/`
- Existing tests:
  - App-level `tests.py`
  - `django.test.TestCase`
  - inline fixtures in `setUp`
  - `reverse(...)`
  - `force_login(...)`

**Phase 6 Goals**
Implement staff-facing Player Experience only:
- Player search/filter page
- Player Profile page
- Timeline section on Player Profile
- Simple Player Comparison page
- `analytics/services/timeline_service.py`
- `analytics/services/comparison_service.py`

Do not implement:
- Phase 7 Command Center
- dashboards
- charts
- exports
- AI summaries
- future `TimelineEvent` model
- measurements
- parent/player portal views
- advanced reporting engine

**Architecture Overview**
Phase 6 should remain read-only from an analytics perspective:
- `players` owns canonical player identity, tags, source rows, and imports.
- `analytics` owns timelines, comparison, observations, and draft analytics.
- `drafts` owns draft actions and draft selections.
- Views should orchestrate requests and call services.
- Templates should render service output only.

**Existing Code To Reuse**
- `players.Player` queryset fields for name/team/division/birth year.
- `players.services.tag_service.active_tags()`.
- `PlayerSourceRow` for imported context.
- `analytics.services.draft_service` for draft context.
- `Observation` and `ObservationResponse` for submitted coach assessment history.
- `analytics.services.coach_assessment_service.group_questions_for_display()` for response grouping if needed.
- `AnalyticsStaffRequiredMixin` for staff-only player profile/search/comparison views.

**Likely Files To Create**
- `analytics/services/timeline_service.py`
- `analytics/services/comparison_service.py`
- `analytics/templates/analytics/player_search.html`
- `analytics/templates/analytics/player_profile.html`
- `analytics/templates/analytics/_player_timeline.html`
- `analytics/templates/analytics/player_compare.html`

**Likely Files To Modify**
- `analytics/views.py`
- `analytics/urls.py`
- `analytics/tests.py`
- `docs/analytics/implementation/STATUS.md`
- `docs/analytics/implementation/phase_06_player_experience.md`

No migrations expected.

**New Services**
`timeline_service.py` should provide:
- `get_player_timeline(player)`
- timeline items for:
  - submitted coach assessments
  - imported source rows
  - draft context
- deterministic ordering, likely newest-first
- dataclasses for timeline display objects
- no `TimelineEvent` model

`comparison_service.py` should provide:
- `get_player_comparison(players)`
- average score by player
- category score summaries
- evaluator count
- coach notes
- tags
- team/division
- draft context summary

A small player search helper may be needed. Architecture does not explicitly name a `player_search_service.py`, so this could either live in `comparison_service.py`/`timeline_service.py` only if scoped, or as a private helper in views. A separate service would be cleaner but may exceed documented deliverables unless approved.

**View Changes**
Add staff-only views:
- `PlayerSearchView`
  - route: likely `/analytics/players/`
  - filters: name, team, division, birth year, tag, imported source, evaluation completion, draft status
- `PlayerProfileView`
  - route: likely `/analytics/players/<int:player_id>/`
  - displays canonical player fields, tags, import context, submitted coach assessments, timeline, draft context
- `PlayerComparisonView`
  - route: likely `/analytics/players/compare/`
  - GET-based selection of player IDs
  - simple table output

**Template Changes**
Use existing `analytics/base.html`.

Player search:
- compact filter form
- table of players
- links to profile
- simple status columns

Player profile:
- profile summary
- tags
- import/source context
- submitted coach assessment summary
- draft context
- timeline partial

Comparison:
- player selection form
- comparison table
- average score, categories, notes, evaluator count, draft context, tags

**Tests To Add**
Service tests:
- timeline includes submitted assessments
- timeline excludes draft/reopened observations
- timeline includes import/source rows
- timeline includes draft context when matched
- timeline ordering deterministic
- comparison average scores
- comparison category scores
- comparison notes
- comparison evaluator count
- comparison handles players with no observations

View tests:
- player search requires staff
- search by name
- filter by team
- filter by division
- filter by birth year
- filter by tag
- filter by imported source
- filter by evaluation completion
- filter by draft status
- profile page renders player details, tags, imports, assessments, timeline
- comparison page renders selected players
- non-staff access denied

Regression tests:
- existing coach assessment views still work
- existing draft context service behavior still works
- existing import UI unaffected

**Risks**
- Draft status filter is not defined precisely. It could mean drafted/undrafted/unmatched/no draft record, but the docs do not define exact values.
- “Player Profile shows draft context” is underspecified because current `draft_service` starts from `DraftPlayer`, not `players.Player`.
- “Expected draft round vs actual draft” depends on question metadata/key conventions, but the default question set does not currently include an expected draft round question.
- Comparison scope could easily drift into Phase 7 reporting if not kept table-based and narrow.
- Player search could become duplicated logic unless a clear service/helper boundary is chosen.

**Assumptions Required If Implemented**
- Phase 6 pages are staff-only because the phase says “staff-facing player experience.”
- Draft status filters would need a small agreed vocabulary before implementation.
- Player profile draft context would require adding a service helper that finds draft contexts for a canonical `players.Player`.
- Comparison should be limited to selected players via querystring, not a dashboard.
- Timeline entries are dataclasses/read models, not database models.

**Potential Architecture Concerns**
- Missing Phase 6 engineering plan means exact behavior would require interpretation.
- The architecture says use `analytics/services/timeline_service.py` and `comparison_service.py`, while repository assessment mentions plural alternatives like `timelines.py`; the architecture should win.
- Phase 6 references “basic reports” indirectly through Player Profile and Reporting docs, but the phase must not become Phase 7 reporting.
- Current Phase 5 implementation exposes draft context in the draft command center, but not yet on player profile pages; Phase 6 needs a player-oriented lookup path.

**Inconsistencies Found**
- `STATUS.md` says Phase 5 is complete but “Current Phase” still says Phase 5, not Phase 6.
- `implementation/README.md` lists only Phase 1 under “Current engineering plans,” although Phase 2-4 engineering docs exist.
- No Phase 5 or Phase 6 engineering plan file exists.
- Phase 6 requires several filter behaviors but does not define exact option semantics for draft status or evaluation completion.

Because the Phase 6 engineering plan is missing and several required behaviors are underspecified, implementing Phase 6 now would require guessing on user-facing behavior and service contracts.

CANNOT IMPLEMENT UNTIL DOCUMENTATION IS PROVIDED
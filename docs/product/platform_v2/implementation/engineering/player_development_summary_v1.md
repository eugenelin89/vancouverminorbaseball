# Player Development Summary V1 Engineering Plan

Status:

```text
Engineering plan complete.
Implementation not started.
```

Date: 2026-07-16

## 1. Purpose

Player Development Summary V1 is the first implementation phase for Platform V2: Player Development Intelligence.

The goal is to give players, coaches, and staff a deterministic, privacy-aware summary of a player's submitted evaluation evidence for a selected season or evaluation cycle.

The summary must help users understand development patterns without creating rankings, predictions, AI-generated claims, or persisted development records.

## 2. Non-Implementation Boundary

This document is an engineering plan only.

Do not implement during Phase 1A:

- the `development` Django app;
- `INSTALLED_APPS` changes;
- URL registration;
- models;
- migrations;
- services;
- read models;
- views;
- forms;
- templates;
- tests;
- permissions;
- Analytics, Accounts, Players, Seasons, Drafts, PDP, or settings changes.

Future implementation must use this document as the coding contract.

## 3. Bounded Context Ownership

Future app:

```text
development
```

The `development` app should own:

- Player Development Summary read models;
- summary assembly services;
- summary-specific permission composition;
- summary views;
- summary templates;
- the `development` URL namespace;
- future development-plan workflows only when separately approved.

The `development` app must not own:

- canonical player identity;
- Django user identity;
- account roles;
- user-player links;
- seasons;
- season teams;
- player roster memberships;
- coach assignments;
- raw evaluations;
- observation responses;
- evaluation submission workflows;
- account permissions;
- PDP models or PDP migration behavior.

Allowed dependency direction:

```text
development -> players
development -> accounts
development -> seasons
development -> analytics
```

Forbidden dependency direction:

```text
analytics -> development
seasons -> development
accounts -> development
players -> development
development -> pdp
```

No exception is approved for Player Development Summary V1.

## 4. Product Boundary

Player Development Summary V1 must remain:

- deterministic;
- computed on request;
- read-only;
- evidence-grounded;
- server-rendered;
- season/cycle scoped;
- privacy-aware;
- non-ranking;
- non-predictive;
- non-AI.

Out of scope:

- persisted summaries;
- development plans;
- goal tracking;
- coach-authored priorities;
- player action plans;
- longitudinal cross-season analysis;
- charts;
- exports;
- PDFs;
- parent access;
- notifications;
- AI;
- rankings;
- percentiles;
- player comparisons;
- overall player score;
- team-scoped permission redesign;
- PDP integration.

## 5. Source Data Contract

Use only authorized Analytics evidence.

Included records must satisfy all of these conditions:

- `Observation.status = submitted`;
- `Observation.observation_type_key = coach_assessment`;
- `Observation.player` is the selected `players.Player`;
- `Observation.season` is not null for normal summaries;
- the observation belongs to the selected season or selected evaluation cycle;
- the selected cycle, when supplied, belongs to the selected/derived season;
- the observation has a supported perspective: self, coach, staff, peer, or guest;
- responses are `rating_1_5` or `text`;
- the viewer is authorized for the selected projection.

Excluded records:

- draft observations;
- reopened observations until resubmitted;
- archived observations;
- legacy/no-season observations from normal seasonal summaries;
- observations with mismatched season/cycle context;
- observations for inactive seasons unless explicitly selected by staff/coach;
- observations in inactive cycles unless explicitly selected by staff/coach;
- PDP evaluations;
- import source rows;
- draft context records;
- unsupported measurements;
- generated AI text.

Legacy/no-season records:

- exclude from normal summaries;
- do not infer season from live player/team fields;
- show a staff/coach warning when such evidence exists for the selected player;
- do not show that warning to player-safe views.

Duplicate submissions:

- rely on existing Analytics uniqueness constraints;
- do not add "latest wins" semantics;
- when season scope is used, include valid submitted observations across all cycles in that season;
- when cycle scope is used, include only valid submitted observations in that cycle.

Superseded or corrected observations:

- reopened records are excluded;
- resubmitted records are included once their status returns to submitted;
- no extra correction model exists in V1, so do not invent one.

## 6. Season And Cycle Selection

Supported query parameters:

```text
season=<season_id>
cycle=<evaluation_cycle_id>
```

The server must validate season/cycle consistency. The client must not be allowed to combine mismatched season and cycle values.

### Explicit Cycle

If `cycle` is supplied:

- the cycle must exist;
- the cycle must have a season;
- the season is derived from the cycle;
- if `season` is also supplied, it must match the cycle season;
- the summary uses submitted observations in that cycle only;
- invalid or mismatched cycle/season values should return a clear no-context or 404/permission-safe response according to view conventions.

### Explicit Season Without Cycle

If `season` is supplied and `cycle` is not supplied:

- the season must exist;
- staff/coach projections may select inactive seasons;
- player-safe projection should show only seasons with submitted evidence for that player;
- the summary uses submitted observations in that season across all cycles;
- cycles are labeled in coverage and evidence rows.

### Neither Supplied

Use this deterministic priority:

1. current active coach-assessment evaluation cycle with a season;
2. most recently started active coach-assessment cycle with a season;
3. current season if it contains submitted observations for the selected player;
4. otherwise return a no-context empty state.

This rule extends current `analytics.services.coach_assessment_service.get_active_coach_assessment_cycle()` behavior by requiring a season for development summaries.

## 7. Supported Perspectives

Include all submitted perspectives in staff/coach summaries:

- Self Evaluation;
- Coach Evaluation;
- Staff Evaluation;
- Peer Evaluation;
- Guest Evaluation.

Player-safe summaries may include all rating aggregates by perspective, but must apply visibility rules.

Never blend perspectives into one unlabeled score.

Every metric, warning, text item, comparison, and evidence link must retain perspective labeling.

Perspective ordering:

1. self;
2. coach;
3. staff;
4. peer;
5. guest.

## 8. Rating Aggregation

For each `ObservationResponse` where:

```text
response_type = rating_1_5
numeric_value is not null
```

Group by:

- normalized category;
- perspective.

Category rule:

- use `ObservationQuestion.category`;
- when blank, use `Questions`;
- trim surrounding whitespace;
- compare category names case-insensitively for grouping;
- display the first non-empty source spelling by earliest question order, falling back to title-cased normalized text.

Calculate:

- rating response count;
- arithmetic mean;
- contributing submitted observation count;
- contributing evaluator count when visible;
- contributing question count;
- minimum and maximum only for internal read-model completeness, not required for V1 display.

Display precision:

- one decimal place.

Persistence:

- do not persist calculated values.

Question-set compatibility:

- category aggregation may combine responses across question-set versions only when the normalized category name matches;
- do not combine individual questions merely because prompts look similar;
- evidence links must preserve original question prompt and question-set version;
- show a warning when more than one question-set version contributes to the summary;
- if a future pilot shows category names changed meaning between versions, the future implementation must split those categories before launch.

## 9. Minimum-Data Policy

Category averages:

- display an average when at least one valid rating exists;
- always show count beside the average.

Strength/opportunity labels:

- require at least two valid ratings;
- require at least one submitted observation;
- apply within the same perspective and category;
- never issue a label from a single rating.

Thresholds:

```text
Possible strength: average >= 4.0
Possible development opportunity: average <= 2.5
Insufficient evidence: fewer than 2 ratings
```

These thresholds are approved for pilot use because they are simple, explainable, and conservative. They are not a permanent player-scoring model and should be reviewed after pilot feedback.

## 10. Strength And Opportunity Labels

Allowed labels:

- `Possible strength`
- `Possible development opportunity`
- `Insufficient evidence`

Disallowed labels:

- weakness;
- deficiency;
- below average;
- elite;
- top;
- poor;
- ranking language.

Each label must show:

- perspective;
- category;
- average;
- rating count;
- submitted observation count;
- evidence link(s);
- explanatory text that the label summarizes submitted evaluation responses only.

Labels must never imply objective truth or selection decisions.

## 11. Self-Versus-Coach Comparison

For each category where self and coach ratings both exist:

```text
difference = self_average - coach_average
```

Labels:

```text
Aligned: absolute difference < 0.5
Self rates higher: difference >= 0.5
Coach rates higher: difference <= -0.5
```

Display:

- self average;
- self rating count;
- coach average;
- coach rating count;
- difference rounded to one decimal place;
- neutral discussion-oriented wording.

Do not:

- compare when either side lacks data;
- compare self against staff, peer, guest, or combined external averages in V1;
- imply that self or coach perspective is correct;
- convert the comparison into a score.

## 12. Qualitative Text Visibility

Qualitative text means `ObservationResponse.response_type = text` and non-empty `text_value`.

Staff/coach projection:

- show submitted text feedback;
- group by perspective and submitted observation;
- preserve exact source wording;
- show question label;
- show submitted date;
- show season/cycle context;
- show evaluator display name according to existing coach review behavior;
- do not show evaluator email, internal account metadata, import metadata, or password/provisioning data.

Player-safe projection:

- hide evaluator names, usernames, and emails;
- show perspective label and evaluator role/category only;
- show self text;
- show coach text;
- show staff text;
- show guest text only if it is already visible through existing My Evaluations behavior;
- hide peer free-text comments in Player Development Summary V1;
- show peer rating aggregates with perspective label;
- link only to player-safe source routes.

Rationale for hiding peer text from players:

- youth peer feedback is sensitive;
- existing My Evaluations can show raw submitted evaluation detail, but V2 summaries are broader and more prominent;
- hiding peer text in Phase 1 reduces retaliation and peer-pressure risk while preserving useful aggregate signals.

No projection may algorithmically classify comments as strengths or opportunities.

## 13. Evaluation Coverage Read Model

`EvaluationCoverage` should include:

- total submitted observations;
- count by perspective;
- count by cycle;
- rating response count;
- text response count;
- contributing categories;
- contributing question-set versions;
- first submitted date;
- latest submitted date;
- warnings.

Coverage is context, not a quality score.

Warnings:

- no submitted evaluations;
- only one perspective available;
- no coach evaluation;
- no self evaluation;
- multiple question-set versions;
- legacy/no-season evidence excluded;
- insufficient ratings for labels;
- no text feedback.

Warning ordering:

1. no context;
2. no submitted evaluations;
3. legacy/no-season evidence excluded;
4. multiple question-set versions;
5. only one perspective available;
6. no coach evaluation;
7. no self evaluation;
8. insufficient ratings for labels;
9. no text feedback.

Player-safe projection must suppress staff-only warnings such as legacy evidence counts if those warnings reveal hidden records.

## 14. Evidence Links

Every displayed metric, comparison, label, or text item must be traceable.

`EvidenceLink` fields:

- `title: str`
- `perspective_label: str`
- `evaluation_date: date | datetime | None`
- `season_name: str`
- `cycle_name: str`
- `category: str`
- `question_label: str`
- `url: str`
- `source_observation_id: int`
- `is_player_safe: bool`

Display labels must not expose raw internal IDs.

URL rules:

- player-safe links use `analytics:my-evaluation-detail`;
- staff/coach links use `analytics:evaluation-review-detail`;
- staff-only review links may use `analytics:observation-review-detail` only for staff-only surfaces;
- if no authorized URL exists, omit the URL and show non-sensitive source metadata.

Evidence links are generated by services, not templates.

## 15. Permission Matrix

| Viewer | Access Decision |
| --- | --- |
| Unauthenticated | denied |
| Player with active self link to target player | allowed, player-safe projection only |
| Player without active self link | denied |
| Coach role | allowed, staff/coach projection, using current coach-review access |
| Django staff/superuser | allowed, staff/coach projection |
| `AccountProfile.role = staff` without Django staff/superuser | allowed only if current coach-review access allows it; does not become Django staff |
| Guest evaluator | denied by default |
| Parent/guardian | denied in Phase 1 |

Coach access decision:

```text
Reuse current coach-review access exactly.
Do not introduce stricter team scoping in Player Development Summary V1.
Clearly document that this is the same broad submitted-evaluation review scope coaches already have.
```

This is acceptable for Phase 1 because strict team-scoped coach permissions are explicitly deferred in Seasonal Participation V1. If the pilot requires team-scoped access before summaries launch, that must become a separate prerequisite phase.

## 16. Permission Service Design

Future module:

```text
development/services/permission_service.py
```

Public functions:

```python
can_view_player_development_summary(user, player) -> bool
can_view_player_safe_summary(user, player) -> bool
can_view_staff_summary(user, player) -> bool
summary_visibility_for_user(user, player) -> SummaryVisibility
```

`SummaryVisibility` fields:

- `can_view: bool`
- `projection: Literal["player_safe", "staff_coach"] | None`
- `can_view_evaluator_identity: bool`
- `can_view_peer_text: bool`
- `can_view_staff_warnings: bool`
- `denial_reason: str`

Composition rules:

- `can_view_player_safe_summary()` delegates to `analytics.services.permissions.can_view_my_evaluations(user, player=player)`;
- `can_view_staff_summary()` delegates to `analytics.services.permissions.can_review_submitted_evaluations(user)`;
- guest and parent denial should be explicit even if they can submit evaluations;
- templates must receive a projection that already reflects visibility.

Do not use `AccountProfile.role` as a substitute for Django staff privileges.

## 17. Summary Service Design

Future module:

```text
development/services/summary_service.py
```

Public entry point:

```python
build_player_development_summary(
    *,
    viewer,
    player,
    season=None,
    evaluation_cycle=None,
) -> PlayerDevelopmentSummary
```

Responsibilities:

- validate viewer permission;
- resolve season/cycle context;
- query authorized submitted evidence;
- build neutral aggregation;
- project to player-safe or staff/coach output;
- calculate deterministic metrics;
- create warnings;
- create evidence links;
- return immutable/read-only dataclasses.

Must not:

- save models;
- update evaluations;
- modify snapshots;
- create summaries;
- send messages;
- call AI;
- make HTTP requests;
- implement account-role rules directly;
- render HTML.

Recommended private helpers:

- `resolve_summary_context()`
- `submitted_summary_observations()`
- `build_neutral_aggregation()`
- `build_staff_coach_projection()`
- `build_player_safe_projection()`
- `category_sort_key()`
- `perspective_sort_key()`
- `build_evidence_link()`

Keep projection logic in `summary_service.py` for Phase 1. Do not add a separate projection service until the module becomes difficult to maintain.

## 18. Read Model Design

Use frozen dataclasses in:

```text
development/read_models.py
```

### SummaryVisibility

- `can_view: bool`
- `projection: str`
- `can_view_evaluator_identity: bool`
- `can_view_peer_text: bool`
- `can_view_staff_warnings: bool`
- `denial_reason: str`

### DevelopmentContext

- `player: players.Player`
- `season: seasons.Season | None`
- `evaluation_cycle: analytics.EvaluationCycle | None`
- `scope: str` (`cycle`, `season`, or `none`)
- `title: str`
- `subtitle: str`
- `available_seasons: list[SeasonOption]`
- `available_cycles: list[CycleOption]`

### SeasonOption / CycleOption

- `id: int`
- `label: str`
- `is_selected: bool`
- `is_active: bool`

### EvaluationCoverage

- `total_submitted_observations: int`
- `by_perspective: list[PerspectiveCoverage]`
- `by_cycle: list[CycleCoverage]`
- `rating_response_count: int`
- `text_response_count: int`
- `categories: list[str]`
- `question_set_versions: list[str]`
- `first_submitted_at: object | None`
- `latest_submitted_at: object | None`
- `warnings: list[SummaryWarning]`

### PerspectiveCoverage

- `perspective: str`
- `label: str`
- `submitted_observation_count: int`
- `rating_response_count: int`
- `text_response_count: int`

### CycleCoverage

- `cycle_id: int`
- `cycle_name: str`
- `submitted_observation_count: int`

### CategorySummary

- `category: str`
- `perspective_summaries: list[PerspectiveCategorySummary]`
- `warnings: list[SummaryWarning]`
- `evidence_links: list[EvidenceLink]`

### PerspectiveCategorySummary

- `perspective: str`
- `perspective_label: str`
- `average: Decimal | None`
- `display_average: str`
- `rating_count: int`
- `submitted_observation_count: int`
- `question_count: int`
- `label: str` (`Possible strength`, `Possible development opportunity`, or `Insufficient evidence`)
- `evidence_links: list[EvidenceLink]`

### PerspectiveComparison

- `category: str`
- `self_average: Decimal`
- `coach_average: Decimal`
- `self_rating_count: int`
- `coach_rating_count: int`
- `difference: Decimal`
- `label: str`
- `help_text: str`
- `evidence_links: list[EvidenceLink]`

### TextFeedbackItem

- `perspective: str`
- `perspective_label: str`
- `question_label: str`
- `text: str`
- `submitted_at: object | None`
- `season_name: str`
- `cycle_name: str`
- `evaluator_display: str`
- `evidence_link: EvidenceLink | None`

For player-safe projection, `evaluator_display` must be blank or a role/category label only.

### EvidenceLink

Use fields from the Evidence Links section.

### SummaryWarning

- `code: str`
- `message: str`
- `severity: str` (`info`, `warning`, `critical`)
- `staff_only: bool`

### PlayerDevelopmentSummary

- `context: DevelopmentContext`
- `visibility: SummaryVisibility`
- `coverage: EvaluationCoverage`
- `category_summaries: list[CategorySummary]`
- `self_vs_coach: list[PerspectiveComparison]`
- `text_feedback: list[TextFeedbackItem]`
- `evidence_links: list[EvidenceLink]`
- `is_empty: bool`

Design choice:

```text
Use one neutral aggregation result and separate staff/coach and player-safe projections.
```

Sensitive evaluator metadata must not exist in player-safe read models.

## 19. Source Query Strategy

The summary service should:

- load the player once using `players.Player`;
- load selected season/cycle once;
- resolve available seasons/cycles with bounded queries;
- query submitted observations in one queryset;
- use `select_related("player", "evaluation_cycle", "season", "evaluator", "evaluator_role", "question_set")`;
- use `prefetch_related("responses__question")`;
- filter by player, observation type, submitted status, and season/cycle;
- exclude legacy/no-season records from the main queryset;
- run a separate lightweight `exists()` check for legacy/no-season evidence for staff/coach warnings;
- avoid one query per category, perspective, response, or evidence link.

The future implementation may reuse `analytics.services.evaluation_review_service.submitted_evaluation_queryset()` for base submitted-review behavior, but it must add season/cycle scoping and player-safe projection. It must not reuse `analytics.services.comparison_service.get_player_score_summary()` because that service blends perspectives and is staff comparison-oriented.

## 20. Ordering Rules

Deterministic ordering is required.

- seasons: current season first, then most recent `starts_on`, then name, then id;
- cycles: most recent `starts_on`, then created date, then name, then id;
- perspectives: self, coach, staff, peer, guest;
- categories: lowest source question display order for the normalized category, then display name;
- category perspective summaries: perspective order;
- evaluations: newest submitted first, then created date, then id;
- text feedback: newest submitted first, then question display order, then response id;
- warnings: warning order from the Evaluation Coverage section;
- evidence links: newest submitted first, then observation id, then question display order.

## 21. URLs And Routes

Future namespace:

```text
development
```

Required routes:

```text
/development/players/<int:player_id>/summary/
/development/my/summary/
```

Required names:

```text
development:player-summary
development:my-summary
```

Optional query parameters:

```text
season=<season_id>
cycle=<evaluation_cycle_id>
```

Server-side validation:

- reject or normalize mismatched season/cycle;
- derive season from cycle when cycle is supplied;
- do not let player-safe route accept arbitrary player IDs;
- do not create separate coach and staff routes unless future presentation differences require them.

## 22. View Plan

Future module:

```text
development/views.py
```

### PlayerDevelopmentSummaryView

Route:

```text
development:player-summary
```

Responsibilities:

- require authentication;
- resolve `players.Player` by `player_id`;
- parse optional `season` and `cycle`;
- call `build_player_development_summary()`;
- render staff/coach projection;
- raise `PermissionDenied` for unauthorized users;
- use existing 404 behavior for missing player/context records.

### MyDevelopmentSummaryView

Route:

```text
development:my-summary
```

Responsibilities:

- require authentication;
- resolve active self-linked players through `accounts.services.link_service.get_self_linked_players()`;
- if no self link, render no-self-link empty state;
- if one self-linked player, summarize that player;
- if multiple self-linked players, render a selector and summarize the selected player only if supplied through a validated safe parameter or choose the primary player when available;
- parse optional `season` and `cycle`;
- call `build_player_development_summary()`;
- render player-safe projection.

Views must not calculate averages, filter comments, or build evidence links.

## 23. Template Plan

Future templates:

```text
development/templates/development/base.html
development/templates/development/player_summary.html
development/templates/development/my_summary.html
development/templates/development/_coverage.html
development/templates/development/_warnings.html
development/templates/development/_category_summary.html
development/templates/development/_comparison.html
development/templates/development/_text_feedback.html
development/templates/development/_evidence_links.html
```

Templates should display:

- player/context header;
- season/cycle controls;
- coverage;
- warnings;
- category summaries;
- self-versus-coach comparisons;
- qualitative feedback;
- source evidence;
- constructive empty states.

Templates must not:

- compute metrics;
- filter sensitive fields;
- enforce permissions;
- hide peer text by conditionally checking raw model fields;
- display empty sections.

## 24. Navigation And Entry Points

Future implementation should add links only after the `development` app exists.

Recommended links:

- staff Analytics player profile: `Development Summary`;
- coach evaluation-review rows/details: `Development Summary`;
- player account/profile area or My Evaluations page: `My Development Summary`;
- Analytics Command Center quick links only after pilot staff confirms the page is useful.

Do not add a new broad dashboard in Player Development Summary V1.

## 25. Empty States

Use constructive text.

### No Self Link

```text
Your account is not linked to a player profile.
```

### Multiple Self Links

```text
Choose which linked player summary you want to view.
```

### No Current Context

```text
No current evaluation period is available.
```

### No Submitted Evaluations

```text
No submitted evaluations are available for this player in the selected period.
```

### Insufficient Data

```text
There is not yet enough evaluation evidence to identify possible strengths or development opportunities.
```

### Legacy Evidence Excluded

Staff/coach only:

```text
Some legacy evaluations are not included because they do not have verified seasonal context.
```

## 26. Performance Plan

Expected behavior:

- bounded query count independent of response count;
- no N+1 query over responses, questions, categories, or evidence links;
- no per-category database queries;
- no per-evidence-link database queries;
- player-safe projection should avoid exposing sensitive fields even if fetched for staff/coach projection.

Representative test target:

- building a summary for one player with multiple submitted observations and responses should stay under a small fixed query count determined during implementation.

Do not introduce caching in V1.

## 27. Migration Decision

Decision:

```text
No migrations expected.
```

Future implementation should add:

- `development` Django app;
- `apps.py`;
- `urls.py`;
- `views.py`;
- `read_models.py`;
- service modules;
- templates;
- tests;
- documentation updates.

It should not add:

- database models;
- admin registration;
- migrations;
- persisted summary tables.

If implementation discovers a concrete need for persistence, stop and return BLOCKED instead of creating a migration.

## 28. Future App Structure

Recommended structure:

```text
development/
    __init__.py
    apps.py
    urls.py
    views.py
    read_models.py
    services/
        __init__.py
        permission_service.py
        summary_service.py
    templates/
        development/
            base.html
            player_summary.html
            my_summary.html
            _coverage.html
            _warnings.html
            _category_summary.html
            _comparison.html
            _text_feedback.html
            _evidence_links.html
    tests/
        __init__.py
        helpers.py
        test_permission_service.py
        test_summary_service.py
        test_player_safe_projection.py
        test_views.py
```

Use one small `views.py` initially. Split only if implementation complexity justifies it.

Do not create `models.py` unless Django app conventions require an empty file. If an empty `models.py` is created, it must define no models.

## 29. Testing Plan

### Summary Service Tests

Cover:

- explicit cycle scope;
- explicit season scope;
- default context resolution priority;
- invalid cycle/season mismatch;
- submitted-only inclusion;
- exclusion of draft, reopened, archived, and legacy/no-season records;
- inclusion of inactive season/cycle only when explicitly selected by staff/coach;
- perspective separation;
- category averages;
- counts;
- threshold labels;
- self-versus-coach comparison;
- warning generation;
- stable ordering;
- multiple question-set versions;
- no model persistence.

### Permission Service Tests

Cover:

- player self-link access;
- player other-player denial;
- inactive self-link denial;
- multiple self-link behavior;
- coach access matching current coach review;
- Django staff/superuser access;
- `AccountProfile.role = staff` without Django staff behavior;
- guest evaluator denial;
- parent/guardian denial;
- unauthenticated denial.

### Player-Safe Projection Tests

Assert player-safe output excludes:

- evaluator names;
- usernames;
- emails;
- hidden peer text;
- internal staff warnings;
- account metadata;
- raw internal IDs in display labels.

Assert player-safe output includes:

- allowed rating aggregates;
- allowed coach/staff/self text;
- perspective labels;
- player-safe evidence URLs only.

### View Tests

Cover:

- authentication;
- route resolution;
- season/cycle query parameters;
- mismatched season/cycle handling;
- 403 behavior;
- 404 behavior;
- no-self-link state;
- multiple-self-link state;
- staff/coach projection context;
- player-safe projection context;
- template names;
- evidence links in rendered context.

### Regression Tests

Future implementation must preserve:

- `accounts` tests;
- `players` tests;
- `seasons` tests;
- `analytics` tests;
- `drafts` tests;
- `pdp` tests;
- full suite.

## 30. Pilot Rollout Boundary

Player Development Summary V1 should launch as a pilot.

Pilot boundary:

- staff/coach access first;
- player-safe access enabled only after staff reviews sample summaries;
- one season;
- one evaluation cycle;
- one or two teams;
- small player cohort;
- no parent access;
- no exports;
- no AI;
- no ranking language.

Feature flag decision:

```text
No generalized feature-flag system is required for Phase 1.
```

Rollout should be controlled by:

- route permissions;
- limited navigation links;
- pilot user communication;
- staff review before exposing player-safe links.

If production operations require a runtime switch before launch, that should be planned as a small deployment-control task, not added implicitly to the summary implementation.

## 31. Documentation Deliverables For Implementation

Future coding phase must update:

- `README.md` if the `development` app is added to the current platform list;
- `docs/ARCHITECTURE.md` when the app is actually implemented;
- `docs/USER_MANUAL.md` when user-visible summary pages exist;
- `docs/product/platform_v2/README.md` to mark Phase 1 implementation status;
- this engineering plan with implementation decisions and review notes.

Do not document AI, parent access, exports, reports, or development plans as implemented.

## 32. Implementation Acceptance Criteria

### A. App Boundary

- `development` app exists.
- No database models are added.
- No migrations are created.
- No PDP dependency exists.
- Dependencies flow only from `development` to `players`, `accounts`, `seasons`, and `analytics`.

### B. Summary Service

- Deterministic summary is generated for selected player/context.
- Submitted records only are included.
- Season/cycle period is enforced.
- Perspectives remain separate.
- Category averages use the approved formula.
- Strength/opportunity labels use approved thresholds.
- Every displayed conclusion is evidence-traceable.

### C. Privacy

- Player-safe output strips evaluator identity.
- Peer free text is hidden from player-safe summaries.
- Guest and parent users are denied summary access.
- Account metadata is not exposed.
- Staff-only warnings are suppressed for players.

### D. Permissions

- Current player self-link rules are reused.
- Current coach review access is reused.
- Django staff/superuser access is reused.
- No new team-scoped policy is introduced accidentally.
- `AccountProfile.role = staff` does not grant Django staff access.

### E. UX

- Staff/coach summary page works.
- Player-safe summary page works.
- Empty states are clear.
- Insufficient-data states are clear.
- Evidence links route to authorized source pages.
- No ranking, percentile, or overall score is displayed.

### F. Performance

- Query count is bounded.
- No N+1 queries are introduced.
- Ordering is deterministic.

### G. Migration

- No models.
- No migrations.
- `makemigrations --check` passes.

### H. Tests

- Focused `development` tests exist.
- Privacy and permission cases are covered.
- Deterministic metric tests are covered.
- Full regression suite passes.

### I. Documentation

- User manual updated after visible routes exist.
- Architecture updated after `development` app exists.
- Product status updated.
- No deferred features are described as implemented.

## 33. Resolved Phase 0 Open Questions

Minimum response count:

- one valid rating may display an average;
- two valid ratings are required for strength/opportunity labels.

Peer text visibility:

- hide peer free-text comments from player-safe summaries in Phase 1;
- show peer rating aggregates with perspective labels;
- staff/coach projection may show peer text under current review access.

Coach access:

- reuse current broad coach-review access;
- strict team scoping remains deferred and must not be silently added.

Route placement:

- use `/development/players/<int:player_id>/summary/` and `/development/my/summary/`;
- link from Analytics and player-facing pages only after implementation.

Summary wording approval:

- staff/coordinators own pilot wording approval before player-safe rollout.

## 34. Final Review

Reviewed from these perspectives:

- player: player-safe projection hides evaluator identity and peer text;
- coach: staff/coach projection gives source-grounded, perspective-aware summaries;
- staff reviewer: every conclusion links to evidence and exposes warnings;
- privacy reviewer: sensitive identity is stripped before player templates;
- security reviewer: existing permission services are composed, not duplicated in templates;
- senior Django engineer: views stay thin, services own logic, no migrations expected;
- data architect: source data remains authoritative and derived values are computed;
- test engineer: deterministic ordering, thresholds, privacy, and permissions are testable;
- pilot operator: pilot scope is narrow and rollback is simple because no persistence is added.

Terminal state:

```text
PASS
```

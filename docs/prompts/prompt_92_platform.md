# Prompt 92: Platform

## User Prompt

````text
Complete Platform V2 Phase 1A only: Player Development Summary V1 Engineering Planning.

Use continuous loop engineering.

Continue until Player Development Summary V1 has a complete, repository-grounded engineering plan with all material product, data, permission, privacy, aggregation, route, read-model, testing, and rollout decisions resolved.

Do not implement application code.

Do not create the `development` Django app.

Do not modify models, migrations, services, views, forms, templates, URLs, permissions, tests, settings, dependencies, or deployment configuration.

Do not start Player Development Summary V1 implementation.

==================================================
Current State
=============

Platform V1 is complete and frozen.

Repository Cleanup Phases 1 through 8 are complete.

Platform V2 Phase 0 is complete.

The approved Platform V2 direction is:

```text
Player Development Intelligence
```

The approved first implementation phase is:

```text
Player Development Summary V1
```

Phase 0 established:

* a future `development` Django app should own Platform V2;
* Phase 1 should use deterministic computed read models;
* no persisted summary models are expected;
* AI is deferred;
* parent access is deferred;
* reports and exports are deferred;
* rankings and overall player scores are prohibited;
* PDP remains legacy/transitionary and is not a dependency target;
* Platform V1 remains frozen.

The Phase 0 plan identified several open questions that must be resolved before implementation.

==================================================
Objective
=========

Produce the detailed engineering plan for Player Development Summary V1.

The plan must resolve:

1. exact bounded-context ownership;
2. exact URL names and paths;
3. exact views and entry points;
4. exact read models and service responsibilities;
5. exact source query strategy;
6. season and evaluation-cycle selection behavior;
7. evaluation inclusion/exclusion rules;
8. aggregation formulas;
9. minimum-data thresholds;
10. strength/opportunity labeling rules;
11. self-versus-coach comparison rules;
12. qualitative-comment visibility;
13. evidence-link behavior;
14. player-safe versus coach/staff visibility;
15. coach access scope;
16. permission composition;
17. empty and insufficient-data states;
18. performance expectations;
19. test structure;
20. migration expectations;
21. pilot rollout boundary;
22. Phase 1 implementation acceptance criteria.

The completed plan must be detailed enough that the next coding prompt can implement the phase without reopening foundational decisions.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Material engineering decisions, repository review, documentation, or acceptance criteria remain unresolved.

PASS

The Phase 1 engineering plan is complete, internally consistent, committed, pushed, and the working tree is clean.

BLOCKED

A required decision cannot be responsibly resolved from repository evidence and established product direction and needs explicit stakeholder direction.

NO_PROGRESS

Two consecutive loops fail to resolve a material planning criterion.

Do not hide unresolved product decisions behind implementation discretion.

==================================================
Established Loop Workflow
=========================

Every loop must:

1. reconcile the committed repository state;
2. read `AGENTS.md`;
3. confirm the working tree is clean;
4. read Platform V2 Phase 0 documentation and relevant current system documentation;
5. inspect current models, services, permissions, views, routes, templates, and tests;
6. identify unresolved Phase 1 decisions;
7. create the next prompt archive before documentation changes;
8. update planning documentation only;
9. review decisions from product, engineering, privacy, security, data, UX, and operations perspectives;
10. resolve contradictions;
11. run documentation verification;
12. commit planning documentation;
13. finalize and separately commit the prompt archive;
14. push both commits;
15. re-read the committed diff;
16. confirm the working tree is clean;
17. reassess every acceptance criterion;
18. choose CONTINUE, PASS, BLOCKED, or NO_PROGRESS;
19. if CONTINUE, immediately begin the next loop.

Each loop must produce:

1. one engineering-planning documentation commit;
2. one prompt archive commit.

==================================================
Required Repository Review
==========================

Read:

* `AGENTS.md`
* `README.md`
* `docs/ARCHITECTURE.md`
* `docs/USER_MANUAL.md`
* `docs/product/README.md`
* `docs/product/PLATFORM_V2_ROADMAP.md`
* `docs/product/platform_v2/README.md`
* `docs/product/platform_v2/implementation/engineering/platform_v2_phase_0_plan.md`
* `docs/engineering/REPOSITORY_CLEANUP_FINAL_AUDIT.md`
* `docs/analytics/implementation/STATUS.md`
* current evaluation access and self-evaluation documentation;
* current coach-review documentation;
* current player-facing evaluation documentation;
* current seasonal-participation documentation.

Inspect:

* `players/models.py`
* `accounts/models.py`
* `accounts/services/permissions.py`
* `accounts/services/link_service.py`
* `seasons/models.py`
* `seasons/services/`
* `analytics/models.py`
* `analytics/services/`
* current Analytics comparison services;
* current player timeline services;
* current metrics services;
* current player-facing My Evaluations views;
* current coach-review views;
* current staff-review and Analytics views;
* current URLs and route names;
* relevant templates;
* current test packages for accounts, seasons, players, and analytics.

Do not modify application code.

==================================================
Bounded Context Decision
========================

Confirm the future bounded context:

```text
development
```

Define its exact responsibilities.

The future `development` app should own:

* Player Development Summary read models;
* summary assembly services;
* summary-specific permission composition;
* summary views;
* summary templates;
* development-specific URL namespace;
* future development-plan workflows only when separately approved.

It must not own:

* player identity;
* user identity;
* user-player links;
* seasons;
* team membership;
* coach assignments;
* raw evaluations;
* observation responses;
* evaluation submissions;
* account permissions;
* PDP models.

Define allowed dependencies:

```text
development -> players
development -> accounts
development -> seasons
development -> analytics
```

Define forbidden dependencies:

```text
analytics -> development
seasons -> development
accounts -> development
players -> development
development -> pdp
```

Exceptions must be explicitly justified.

==================================================
Phase 1 Product Boundary
========================

Player Development Summary V1 must remain:

* deterministic;
* computed;
* read-only;
* evidence-grounded;
* server-rendered;
* season/cycle scoped;
* privacy-aware;
* non-ranking;
* non-predictive;
* non-AI.

Do not include:

* persisted summaries;
* development plans;
* goal tracking;
* coach-authored priorities;
* player action plans;
* longitudinal cross-season analysis;
* charts;
* exports;
* PDFs;
* parent access;
* notifications;
* AI;
* rankings;
* percentiles;
* player comparisons;
* overall player score;
* team-scoped permission redesign;
* PDP integration.

==================================================
Source Data Contract
====================

Define the exact source dataset.

Use only authorized, submitted Analytics records.

Determine whether source observations must satisfy all of:

* `status = submitted`;
* selected player;
* selected season and/or cycle;
* supported observation type;
* supported perspective;
* current question/response types;
* non-legacy seasonal context where required.

Recommended initial source:

* submitted observations;
* `coach_assessment` observation type only;
* selected player;
* one selected season;
* optional selected evaluation cycle within that season;
* valid snapshot context;
* rating and text responses;
* question categories;
* perspective labels.

Explicitly decide treatment of:

* reopened observations;
* archived observations;
* legacy/no-season observations;
* observations lacking player membership;
* inactive evaluation cycles;
* inactive seasons;
* duplicate submissions;
* superseded or corrected observations.

Do not silently include ambiguous records.

==================================================
Season And Cycle Selection
==========================

Resolve exact selection behavior.

Recommended contract:

## Explicit Cycle

If `cycle` is supplied:

* cycle must exist;
* cycle must belong to selected player-access context;
* cycle must have a season;
* summary uses only submitted observations in that cycle;
* season derives from cycle.

## Explicit Season Without Cycle

If `season` is supplied:

* summary uses submitted observations in that season;
* cycles are grouped or labeled;
* no cross-season observations are included.

## Neither Supplied

Use this deterministic priority:

1. current active evaluation cycle with a season;
2. most recently started active cycle with a season;
3. current season, if it contains submitted observations;
4. otherwise show a clear no-context empty state.

Confirm or replace this rule based on repository behavior.

Do not let the client independently control mismatched season and cycle values.

==================================================
Supported Perspectives
======================

Define whether Phase 1 includes:

* self;
* peer;
* coach;
* staff;
* guest.

Recommended contract:

* include every authorized submitted perspective in staff/coach summaries;
* player-safe summaries may include all perspectives but must apply visibility rules;
* never blend perspectives into one unlabeled score;
* every metric and comment must retain perspective labeling.

Explicitly decide whether peer-evaluation text is shown to players.

Recommended conservative rule:

* player may see peer rating aggregates;
* peer free-text comments are hidden from player-facing summaries in Phase 1;
* staff/coach may see them according to current authorized review access.

If repository evidence supports a different existing rule, document it.

==================================================
Observation Inclusion Rules
===========================

Define exact observation inclusion.

Recommended:

* submitted only;
* exclude drafts;
* exclude reopened observations until resubmitted;
* exclude legacy/no-season observations from normal seasonal summaries;
* display a staff-only warning if legacy evidence exists but is excluded;
* do not attempt to infer season;
* no automatic deduplication beyond existing observation uniqueness rules.

If the same evaluator submits more than one valid observation in different cycles:

* include both when season scope is used;
* include only selected cycle when cycle scope is used.

Do not invent “latest wins” semantics without evidence.

==================================================
Rating Aggregation
==================

Define exact aggregation.

For each response where:

```text
response_type = rating_1_5
```

Group by:

* question category;
* perspective.

If category is blank:

```text
Questions
```

Calculate:

* response count;
* arithmetic mean;
* optional minimum and maximum only if useful;
* source evaluation count;
* source question count.

Avoid misleading precision.

Recommended display precision:

* one decimal place.

Do not persist calculated values.

Do not combine categories across incompatible question sets without explicit category equivalence.

==================================================
Question-Set Compatibility
==========================

Resolve how multiple question sets or versions are handled.

Review current question-set and category behavior.

Recommended initial rule:

* category aggregation may combine responses across question-set versions only when category names match after existing normalization;
* evidence links must preserve original question text and question-set context;
* do not combine individual questions merely because labels appear similar;
* show a warning when multiple question-set versions contributed.

If category semantics differ materially between versions, document that aggregation must remain separated.

==================================================
Minimum-Data Policy
===================

Resolve the open minimum-data question.

Recommended policy:

## Category Average

Display an average when:

* at least one valid rating exists.

Always show its count.

## Strength / Opportunity Labels

Require:

* at least two valid ratings;
* from at least one submitted observation;
* for the same perspective and category.

Recommended thresholds:

```text
Possible strength: average >= 4.0
Possible development opportunity: average <= 2.5
```

Do not issue either label with only one rating.

If self and coach data are being compared, each side must have at least one valid rating in the category.

Document why these thresholds are appropriate for a pilot and subject to later review.

If repository evidence makes these thresholds unsafe, choose and justify an alternative.

==================================================
Strength And Opportunity Rules
==============================

Define exact display language.

Use:

* `Possible strength`
* `Possible development opportunity`
* `Insufficient evidence`

Do not use:

* weakness;
* deficiency;
* below average;
* elite;
* top;
* poor;
* ranking language.

Labels must:

* identify perspective;
* show average;
* show count;
* link to evidence;
* explain that they summarize submitted evaluation responses.

Never imply objective truth.

==================================================
Self-Versus-Coach Comparison
============================

Define exact comparison rules.

For a category where both self and coach ratings exist:

Calculate:

```text
difference = self_average - coach_average
```

Recommended deterministic labels:

```text
Aligned: absolute difference < 0.5
Self rates higher: difference >= 0.5
Coach rates higher: difference <= -0.5
```

Display:

* self average and count;
* coach average and count;
* difference;
* neutral discussion-oriented wording.

Do not imply which perspective is correct.

Do not compare self against a combined coach/staff/guest average unless separately defined.

Do not compare when either side lacks data.

==================================================
Qualitative Text
================

Define exact treatment of text responses.

Recommended Phase 1 behavior:

* list text feedback;
* group by perspective and submitted observation;
* preserve exact source wording;
* display question label;
* display submitted date;
* display season/cycle context;
* do not algorithmically classify comments;
* do not combine comments into a generated narrative;
* do not label text as strength or opportunity automatically.

For player-facing views:

* hide evaluator identity;
* show perspective label;
* hide peer text unless explicitly approved;
* use only player-safe source links.

For coach/staff views:

* follow existing authorized identity visibility;
* do not expose account email or internal metadata.

==================================================
Evaluation Coverage
===================

Define a deterministic coverage read model.

Include:

* total submitted observations;
* count by perspective;
* count by cycle;
* rating response count;
* text response count;
* contributing categories;
* contributing question-set versions;
* date range;
* warnings.

Possible warnings:

* no submitted evaluations;
* only one perspective available;
* no coach evaluation;
* no self evaluation;
* multiple question-set versions;
* legacy/no-season evidence excluded;
* insufficient ratings for labels;
* no text feedback.

Do not present coverage as a quality score.

==================================================
Evidence Links
==============

Every displayed metric, comparison, label, or text response must be traceable.

Define evidence-link read model fields:

* title;
* perspective label;
* evaluation date;
* season;
* cycle;
* category;
* question label where applicable;
* authorized URL;
* source observation identifier internally.

Player-safe links must use current player-safe evaluation detail routes.

Coach/staff links must use authorized review routes.

Do not expose raw internal IDs in display labels.

If no authorized source route exists:

* omit the link;
* still show source metadata;
* do not create an unsafe shortcut.

==================================================
Permission Matrix
=================

Define exact access.

## Player

Access allowed only when:

* authenticated;
* account has active self link to target player;
* summary is player-safe.

Player must not view:

* other players;
* evaluator usernames;
* evaluator email;
* hidden evaluator identity;
* internal staff metadata;
* peer free text if deferred;
* guest/staff notes prohibited by current player visibility.

## Coach

Recommended Phase 1 decision:

* reuse current coach-review access exactly;
* do not introduce stricter team scoping in this phase;
* clearly document that access is as broad as current coach review;
* strict team scoping remains deferred.

Confirm this is acceptable from repository rules.

## Staff / Superuser

Use current staff Analytics-review access.

`AccountProfile.role` alone must not grant staff access.

## Guest Evaluator

No summary access by default.

## Parent/Guardian

No summary access in Phase 1.

==================================================
Permission Service Design
=========================

Plan a future:

```text
development/services/permission_service.py
```

It should compose existing permission rules rather than redefine account roles.

Likely functions:

* `can_view_player_development_summary(user, player)`;
* `can_view_player_safe_summary(user, player)`;
* `can_view_staff_summary(user, player)`;
* `summary_visibility_for_user(user, player)`.

Define expected outputs and ownership.

Do not let templates decide visibility.

Do not use `AccountProfile.role` as a substitute for Django staff privileges.

==================================================
Summary Service Design
======================

Plan a future:

```text
development/services/summary_service.py
```

Define its public API.

Recommended entry point:

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

* validate context;
* call permission service;
* query authorized evidence;
* group responses;
* calculate deterministic metrics;
* create warnings;
* create evidence links;
* return immutable/read-only dataclasses.

It must not:

* save models;
* update evaluations;
* modify snapshots;
* create summaries;
* send messages;
* call AI;
* make HTTP requests;
* implement account-role rules;
* render HTML.

==================================================
Read Model Design
=================

Define exact dataclasses.

At minimum consider:

```text
PlayerDevelopmentSummary
DevelopmentContext
EvaluationCoverage
PerspectiveCoverage
CategorySummary
PerspectiveCategorySummary
PerspectiveComparison
TextFeedbackItem
EvidenceLink
SummaryWarning
```

For each, define:

* fields;
* types;
* optionality;
* ordering;
* sensitive fields;
* player-safe versus staff fields.

Prefer frozen dataclasses.

Sensitive evaluator metadata should not exist in player-safe read models.

Determine whether to use:

* one common summary with filtered visibility;
* separate staff and player-safe summary read models.

Recommended safer design:

* shared neutral aggregation result;
* separate projection step for staff/coach versus player-safe output.

Document exact choice.

==================================================
Recommended Read-Model Projection
=================================

Recommended architecture:

```text
authorized evidence
    ->
neutral aggregation result
    ->
staff/coach projection
    ->
player-safe projection
```

Benefits:

* aggregation logic remains shared;
* sensitive fields are removed before reaching player templates;
* player safety is testable;
* templates stay simple.

Define whether projections live in:

* `summary_service.py`;
* separate `projection_service.py`.

Do not over-split unless it improves privacy ownership.

==================================================
URL And Route Plan
==================

Resolve exact future routes.

Recommended namespace:

```text
development
```

Recommended routes:

```text
/development/players/<int:player_id>/summary/
/development/my/summary/
```

Recommended names:

```text
development:player-summary
development:my-summary
```

Optional query parameters:

```text
season=<season_id>
cycle=<evaluation_cycle_id>
```

Server must validate season/cycle consistency.

Do not create separate coach and staff URLs unless presentation or permission differences require them.

Player route must never accept another player ID.

==================================================
View Plan
=========

Plan future server-rendered views.

## Staff / Coach Player Summary

Responsibilities:

* authenticate;
* resolve player;
* resolve optional season/cycle;
* call summary service;
* render staff/coach projection;
* return 403 or 404 according to current patterns.

## My Summary

Responsibilities:

* authenticate;
* resolve active self-linked player;
* handle zero, one, or multiple active self links using current account-link conventions;
* resolve optional season/cycle;
* call player-safe summary service;
* render player-safe projection.

Views must not calculate averages or filter comments.

==================================================
Template Plan
=============

Plan templates such as:

```text
development/templates/development/player_summary.html
development/templates/development/my_summary.html
development/templates/development/_coverage.html
development/templates/development/_category_summary.html
development/templates/development/_comparison.html
development/templates/development/_text_feedback.html
development/templates/development/_warnings.html
```

Use only as many partials as improve clarity.

Templates should display:

* player/context header;
* coverage;
* warnings;
* category summaries;
* self-versus-coach comparisons;
* qualitative feedback;
* source evidence.

Do not compute metrics in templates.

Do not display empty sections.

==================================================
Navigation And Entry Points
===========================

Define future entry points.

Recommended:

* player area: `My Development Summary`;
* coach review player row/detail: `Development Summary`;
* staff Analytics player detail: `Development Summary`;
* no new broad dashboard.

Determine exactly which existing templates/pages should link to the new routes.

Do not change navigation in Phase 1A.

==================================================
Empty States
============

Define exact empty states.

At minimum:

## No Self Link

Player:

```text
Your account is not linked to a player profile.
```

## No Season/Cycle Context

```text
No current evaluation period is available.
```

## No Submitted Evaluations

```text
No submitted evaluations are available for this player in the selected period.
```

## Insufficient Data

```text
There is not yet enough evaluation evidence to identify possible strengths or development opportunities.
```

## Legacy Evidence Excluded

Staff/coach only:

```text
Some legacy evaluations are not included because they do not have verified seasonal context.
```

Use constructive language.

==================================================
Ordering Rules
==============

Define stable ordering.

Recommended:

* seasons: most recent first;
* cycles: most recent start date first;
* perspectives: self, coach, staff, peer, guest;
* categories: existing question display/category order where available, then alphabetical;
* evaluations: newest submitted first;
* text feedback: newest submitted first;
* warnings: severity/order defined explicitly;
* evidence links: newest first.

Deterministic ordering is required for tests.

==================================================
Performance Plan
================

Define expected query strategy.

The summary service should ideally:

* load player once;
* load selected season/cycle once;
* query submitted observations in one bounded queryset;
* `select_related` evaluator/cycle/player/membership where required;
* `prefetch_related` responses/questions;
* avoid one query per category;
* avoid one query per evidence link;
* avoid querying hidden evaluator data for player-safe output where practical.

Set a reasonable query-count expectation for representative tests, but do not overfit prematurely.

Recommended target:

* bounded number of queries independent of response count;
* exact threshold determined during implementation after inspecting current Analytics services.

==================================================
Migration Decision
==================

Confirm:

```text
No migrations expected.
```

Phase 1 should add:

* new Django app;
* services;
* read models;
* views;
* routes;
* templates;
* tests;
* documentation.

It should not add database models.

If implementation reveals a need for persistence:

* stop;
* do not create a migration automatically;
* return BLOCKED;
* document the concrete need.

==================================================
App Creation Plan
=================

Define expected future app structure:

```text
development/
    __init__.py
    apps.py
    urls.py
    views.py or views/
    services/
        permission_service.py
        summary_service.py
    read_models.py
    templates/development/
    tests/
```

Decide whether:

* views should start as one small module;
* tests should begin as a package;
* no `models.py` beyond an empty default file is needed;
* admin registration is unnecessary.

Recommended:

* create test package from the start;
* one small views module initially;
* no models;
* no admin.

==================================================
Testing Plan
============

Define exact test groups.

## Summary Service

Test:

* season scope;
* cycle scope;
* default-context resolution;
* submitted-only behavior;
* exclusion of drafts/reopened/legacy records;
* perspective separation;
* category averages;
* counts;
* thresholds;
* comparisons;
* warnings;
* stable ordering;
* question-set versions;
* no persistence.

## Permission Service

Test:

* player self-link access;
* other-player denial;
* coach current access behavior;
* staff access;
* metadata-only staff denial;
* guest denial;
* parent/guardian denial;
* inactive links;
* multiple self links.

## Player-Safe Projection

Test that it excludes:

* evaluator names;
* usernames;
* emails;
* hidden peer text;
* internal IDs;
* account metadata;
* staff-only warnings where inappropriate.

## Views

Test:

* authentication;
* route resolution;
* season/cycle validation;
* 403/404 behavior;
* templates;
* context;
* query parameters;
* player route cannot target another player;
* empty states.

## Regression

Run and preserve:

* accounts;
* players;
* seasons;
* analytics;
* drafts;
* PDP;
* full suite.

==================================================
Acceptance Criteria For Implementation
======================================

Write detailed acceptance criteria for the future coding phase.

At minimum:

A. App Boundary

* `development` app exists;
* no models;
* no PDP dependency;
* dependencies flow only toward current source apps.

B. Summary Service

* deterministic summary generated;
* submitted records only;
* selected period enforced;
* perspectives remain separate;
* metrics are evidence-traceable.

C. Privacy

* player-safe output strips sensitive identity;
* peer text follows approved rule;
* guest/parent denied;
* account metadata not exposed.

D. Permissions

* current player/coach/staff rules reused correctly;
* no new team-scoped policy accidentally introduced.

E. UX

* staff/coach and player-safe pages work;
* empty and insufficient states are clear;
* evidence links are authorized.

F. Performance

* bounded queries;
* no N+1;
* stable ordering.

G. Migration

* no models;
* no migrations.

H. Tests

* focused development tests;
* full regression suite;
* privacy and permission cases;
* deterministic metric tests.

I. Documentation

* user manual;
* architecture;
* product phase status;
* no AI or future features described as implemented.

==================================================
Pilot Boundary
==============

Define implementation rollout as pilot-only initially.

Recommended:

* staff/coach access first;
* player-safe access may be feature-linked but enabled only after staff review;
* one season;
* one evaluation cycle;
* one or two teams;
* small player cohort;
* no parent access;
* no exports;
* no AI.

Determine whether a code-level feature flag is necessary.

Recommended Phase 1 default:

* no generalized feature-flag system;
* permission-controlled routes;
* operational rollout controlled by navigation links and pilot usage.

If a feature flag is necessary, justify it explicitly.

==================================================
Documentation Deliverables
==========================

Create:

```text
docs/product/platform_v2/implementation/engineering/player_development_summary_v1.md
```

or the next repository-consistent equivalent.

Update as needed:

* `docs/product/platform_v2/README.md`
* `docs/product/PLATFORM_V2_ROADMAP.md`
* `docs/ARCHITECTURE.md`

Do not mark Phase 1 implemented.

Clearly state:

```text
Engineering plan complete.
Implementation not started.
```

==================================================
Scope Restrictions
==================

Do not:

* create `development/`;
* modify `INSTALLED_APPS`;
* add URLs;
* add models;
* create migrations;
* add services;
* add read models;
* add views;
* add templates;
* add tests;
* change permissions;
* alter Analytics;
* alter Seasons;
* alter Accounts;
* alter Players;
* alter PDP;
* modify dependencies;
* add AI;
* add exports;
* add feature flags;
* add application code.

Documentation and engineering planning only.

==================================================
Verification
============

Run:

```text
git diff --check
```

Run the existing local Markdown link sanity check.

Run pre-commit on touched documentation files.

No Django tests are required unless application files were unexpectedly changed.

If application files change, treat it as a scope violation.

==================================================
Acceptance Criteria
===================

Do not declare PASS until:

* all Phase 0 open questions are resolved or explicitly BLOCKED;
* exact source data rules are defined;
* exact season/cycle behavior is defined;
* exact minimum-data thresholds are defined;
* exact comparison rules are defined;
* peer text visibility is defined;
* exact coach access decision is defined;
* read models are defined;
* services and dependency direction are defined;
* URLs and views are defined;
* player-safe projection is defined;
* empty states are defined;
* ordering is defined;
* performance plan is defined;
* migration decision is final;
* test plan is detailed;
* pilot boundary is defined;
* implementation acceptance criteria are complete;
* no application code changed;
* links pass;
* pre-commit passes;
* `git diff --check` passes;
* planning commit pushed;
* prompt archive committed separately;
* working tree clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should:

1. review the Phase 0 plan and current repository;
2. resolve all listed open questions;
3. define exact aggregation and visibility contracts;
4. define services and read models;
5. define routes and views;
6. define permission composition;
7. define test and performance strategy;
8. create the engineering plan;
9. reconcile product and architecture docs;
10. verify documentation;
11. commit, archive, push, and reassess.

Continue only if a material engineering decision remains unresolved.

==================================================
No-Progress Rule
================

A loop counts as progress only if it resolves:

* a data-inclusion rule;
* an aggregation rule;
* a privacy rule;
* a permission rule;
* a route/read-model/service contract;
* a test or performance contract;
* an implementation acceptance criterion.

Adding general product prose does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* player;
* coach;
* staff reviewer;
* privacy reviewer;
* security reviewer;
* senior Django engineer;
* data architect;
* test engineer;
* pilot operator.

Confirm:

* output is deterministic and explainable;
* no perspective is silently blended;
* player-safe data is genuinely safe;
* every conclusion links to evidence;
* sparse data is handled honestly;
* exact implementation boundaries are settled;
* no migrations are expected;
* the next coding prompt can be written without reopening product decisions.

==================================================
Git Workflow
============

For every loop:

1. create the next prompt archive before documentation changes;
2. commit Phase 1 engineering documentation;
3. update the prompt archive with:

   * planning commit hash;
   * source-data decisions;
   * aggregation rules;
   * threshold rules;
   * privacy decisions;
   * permission decisions;
   * service/read-model design;
   * routes/views;
   * test strategy;
   * performance strategy;
   * migration decision;
   * pilot boundary;
   * remaining questions;
   * terminal state;
4. commit the prompt archive separately;
5. push both commits;
6. confirm the working tree is clean.

Suggested planning commit:

```text
Plan Player Development Summary V1
```

==================================================
Final Report
============

Report:

* terminal state;
* loops completed;
* reviewed commit;
* files created;
* files modified;
* source-data contract;
* season/cycle behavior;
* supported perspectives;
* rating aggregation;
* thresholds;
* strength/opportunity rules;
* self-versus-coach comparison;
* qualitative text rules;
* peer text decision;
* permission matrix;
* coach access decision;
* read-model design;
* service design;
* route/view plan;
* player-safe projection;
* evidence-link rules;
* empty states;
* ordering;
* performance plan;
* migration decision;
* testing plan;
* pilot boundary;
* implementation acceptance criteria;
* unresolved questions;
* verification;
* commits;
* push result;
* confirmation that no application code changed;
* confirmation that Platform V1 remains frozen;
* confirmation that the working tree is clean.
````

## Planning Commit

`787851a Plan player development summary phase`

## Decisions Recorded

- Source data: submitted, season-scoped `coach_assessment` observations only.
- Aggregation: category + perspective groups, arithmetic mean, one decimal display.
- Thresholds: averages display from one rating; strength/opportunity labels require two ratings.
- Privacy: player-safe summaries hide evaluator identity and peer free-text comments.
- Permissions: player self-link, current broad coach-review access, and Django staff/superuser access are reused.
- Services/read models: future `development` app owns summary and permission services plus frozen dataclass read models.
- Routes/views: future `development:player-summary` and `development:my-summary`.
- Tests: service, permission, player-safe projection, view, and full regression coverage required.
- Performance: bounded query count, no N+1, no caching in V1.
- Migration: no models and no migrations expected.
- Pilot: staff/coach first, player-safe after staff review, no parent/AI/export/ranking.
- Remaining questions: none blocking Phase 1 implementation planning; implementation not started.
- Terminal state: PASS.

## Commit Diff

````diff
commit 787851a588a63ebb8aa25a996385a917eb85352b
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 16 14:50:09 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 16 14:50:09 2026 -0700

    Plan player development summary phase
---
 docs/ARCHITECTURE.md                               |    1 +
 docs/product/PLATFORM_V2_ROADMAP.md                |    2 +-
 docs/product/platform_v2/README.md                 |   11 +
 .../engineering/player_development_summary_v1.md   | 1276 ++++++++++++++++++++
 4 files changed, 1289 insertions(+), 1 deletion(-)

diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 3f4f9e2..943bb75 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -349,6 +349,7 @@ Documentation:

 - [Platform V2 Roadmap](product/PLATFORM_V2_ROADMAP.md)
 - [Platform V2 Product Planning](product/platform_v2/README.md)
+- [Player Development Summary V1 Engineering Plan](product/platform_v2/implementation/engineering/player_development_summary_v1.md)

 ## Current Platform State

diff --git a/docs/product/PLATFORM_V2_ROADMAP.md b/docs/product/PLATFORM_V2_ROADMAP.md
index 6e9f521..8b9737a 100644
--- a/docs/product/PLATFORM_V2_ROADMAP.md
+++ b/docs/product/PLATFORM_V2_ROADMAP.md
@@ -10,7 +10,7 @@ The recommended next product milestone is:
 Platform V2: Player Development Intelligence
 ```

-Phase 0 product and implementation planning is recorded in [Platform V2 Product Planning](platform_v2/README.md). That plan recommends Player Development Summary V1 as the first implementation phase, using deterministic computed read models before AI, reports, parent access, or persisted development-plan workflows.
+Phase 0 product and implementation planning is recorded in [Platform V2 Product Planning](platform_v2/README.md). That plan recommends Player Development Summary V1 as the first implementation phase, using deterministic computed read models before AI, reports, parent access, or persisted development-plan workflows. Phase 1A engineering planning is complete in the [Player Development Summary V1 Engineering Plan](platform_v2/implementation/engineering/player_development_summary_v1.md); implementation has not started.

 Seasonal Participation V1 is complete and frozen. It allows permanent players and coach accounts to be reused across seasons while evaluations retain historical team/division context. See [Seasonal Participation V1](../seasons/README.md).

diff --git a/docs/product/platform_v2/README.md b/docs/product/platform_v2/README.md
index 0823fae..4491e57 100644
--- a/docs/product/platform_v2/README.md
+++ b/docs/product/platform_v2/README.md
@@ -33,10 +33,21 @@ Platform V2 should build on the completed Platform V1 foundations:
 - PDP should remain legacy/transitionary. Platform V2 should not depend on `pdp.PlayerProfile` or PDP development models.
 - Parent access, AI-generated summaries, report exports, rankings, and development-plan persistence are deferred.

+## Phase 1A Decision Summary
+
+- Player Development Summary V1 engineering planning is complete.
+- Implementation has not started.
+- Future implementation should create a `development` app with no models and no migrations.
+- Summary output should use submitted, season-scoped `coach_assessment` observations only.
+- Category averages may display from one valid rating, but strength/opportunity labels require at least two valid ratings.
+- Player-safe summaries hide evaluator identity and peer free-text comments.
+- Coach access reuses current broad coach-review access; strict team scoping remains deferred.
+
 ## Planning Documents

 - [Platform V2 Roadmap](../PLATFORM_V2_ROADMAP.md)
 - [Phase 0 Engineering Plan](implementation/engineering/platform_v2_phase_0_plan.md)
+- [Player Development Summary V1 Engineering Plan](implementation/engineering/player_development_summary_v1.md)

 ## Implementation Rule

diff --git a/docs/product/platform_v2/implementation/engineering/player_development_summary_v1.md b/docs/product/platform_v2/implementation/engineering/player_development_summary_v1.md
new file mode 100644
index 0000000..61ca9fe
--- /dev/null
+++ b/docs/product/platform_v2/implementation/engineering/player_development_summary_v1.md
@@ -0,0 +1,1276 @@
+# Player Development Summary V1 Engineering Plan
+
+Status:
+
+```text
+Engineering plan complete.
+Implementation not started.
+```
+
+Date: 2026-07-16
+
+## 1. Purpose
+
+Player Development Summary V1 is the first implementation phase for Platform V2: Player Development Intelligence.
+
+The goal is to give players, coaches, and staff a deterministic, privacy-aware summary of a player's submitted evaluation evidence for a selected season or evaluation cycle.
+
+The summary must help users understand development patterns without creating rankings, predictions, AI-generated claims, or persisted development records.
+
+## 2. Non-Implementation Boundary
+
+This document is an engineering plan only.
+
+Do not implement during Phase 1A:
+
+- the `development` Django app;
+- `INSTALLED_APPS` changes;
+- URL registration;
+- models;
+- migrations;
+- services;
+- read models;
+- views;
+- forms;
+- templates;
+- tests;
+- permissions;
+- Analytics, Accounts, Players, Seasons, Drafts, PDP, or settings changes.
+
+Future implementation must use this document as the coding contract.
+
+## 3. Bounded Context Ownership
+
+Future app:
+
+```text
+development
+```
+
+The `development` app should own:
+
+- Player Development Summary read models;
+- summary assembly services;
+- summary-specific permission composition;
+- summary views;
+- summary templates;
+- the `development` URL namespace;
+- future development-plan workflows only when separately approved.
+
+The `development` app must not own:
+
+- canonical player identity;
+- Django user identity;
+- account roles;
+- user-player links;
+- seasons;
+- season teams;
+- player roster memberships;
+- coach assignments;
+- raw evaluations;
+- observation responses;
+- evaluation submission workflows;
+- account permissions;
+- PDP models or PDP migration behavior.
+
+Allowed dependency direction:
+
+```text
+development -> players
+development -> accounts
+development -> seasons
+development -> analytics
+```
+
+Forbidden dependency direction:
+
+```text
+analytics -> development
+seasons -> development
+accounts -> development
+players -> development
+development -> pdp
+```
+
+No exception is approved for Player Development Summary V1.
+
+## 4. Product Boundary
+
+Player Development Summary V1 must remain:
+
+- deterministic;
+- computed on request;
+- read-only;
+- evidence-grounded;
+- server-rendered;
+- season/cycle scoped;
+- privacy-aware;
+- non-ranking;
+- non-predictive;
+- non-AI.
+
+Out of scope:
+
+- persisted summaries;
+- development plans;
+- goal tracking;
+- coach-authored priorities;
+- player action plans;
+- longitudinal cross-season analysis;
+- charts;
+- exports;
+- PDFs;
+- parent access;
+- notifications;
+- AI;
+- rankings;
+- percentiles;
+- player comparisons;
+- overall player score;
+- team-scoped permission redesign;
+- PDP integration.
+
+## 5. Source Data Contract
+
+Use only authorized Analytics evidence.
+
+Included records must satisfy all of these conditions:
+
+- `Observation.status = submitted`;
+- `Observation.observation_type_key = coach_assessment`;
+- `Observation.player` is the selected `players.Player`;
+- `Observation.season` is not null for normal summaries;
+- the observation belongs to the selected season or selected evaluation cycle;
+- the selected cycle, when supplied, belongs to the selected/derived season;
+- the observation has a supported perspective: self, coach, staff, peer, or guest;
+- responses are `rating_1_5` or `text`;
+- the viewer is authorized for the selected projection.
+
+Excluded records:
+
+- draft observations;
+- reopened observations until resubmitted;
+- archived observations;
+- legacy/no-season observations from normal seasonal summaries;
+- observations with mismatched season/cycle context;
+- observations for inactive seasons unless explicitly selected by staff/coach;
+- observations in inactive cycles unless explicitly selected by staff/coach;
+- PDP evaluations;
+- import source rows;
+- draft context records;
+- unsupported measurements;
+- generated AI text.
+
+Legacy/no-season records:
+
+- exclude from normal summaries;
+- do not infer season from live player/team fields;
+- show a staff/coach warning when such evidence exists for the selected player;
+- do not show that warning to player-safe views.
+
+Duplicate submissions:
+
+- rely on existing Analytics uniqueness constraints;
+- do not add "latest wins" semantics;
+- when season scope is used, include valid submitted observations across all cycles in that season;
+- when cycle scope is used, include only valid submitted observations in that cycle.
+
+Superseded or corrected observations:
+
+- reopened records are excluded;
+- resubmitted records are included once their status returns to submitted;
+- no extra correction model exists in V1, so do not invent one.
+
+## 6. Season And Cycle Selection
+
+Supported query parameters:
+
+```text
+season=<season_id>
+cycle=<evaluation_cycle_id>
+```
+
+The server must validate season/cycle consistency. The client must not be allowed to combine mismatched season and cycle values.
+
+### Explicit Cycle
+
+If `cycle` is supplied:
+
+- the cycle must exist;
+- the cycle must have a season;
+- the season is derived from the cycle;
+- if `season` is also supplied, it must match the cycle season;
+- the summary uses submitted observations in that cycle only;
+- invalid or mismatched cycle/season values should return a clear no-context or 404/permission-safe response according to view conventions.
+
+### Explicit Season Without Cycle
+
+If `season` is supplied and `cycle` is not supplied:
+
+- the season must exist;
+- staff/coach projections may select inactive seasons;
+- player-safe projection should show only seasons with submitted evidence for that player;
+- the summary uses submitted observations in that season across all cycles;
+- cycles are labeled in coverage and evidence rows.
+
+### Neither Supplied
+
+Use this deterministic priority:
+
+1. current active coach-assessment evaluation cycle with a season;
+2. most recently started active coach-assessment cycle with a season;
+3. current season if it contains submitted observations for the selected player;
+4. otherwise return a no-context empty state.
+
+This rule extends current `analytics.services.coach_assessment_service.get_active_coach_assessment_cycle()` behavior by requiring a season for development summaries.
+
+## 7. Supported Perspectives
+
+Include all submitted perspectives in staff/coach summaries:
+
+- Self Evaluation;
+- Coach Evaluation;
+- Staff Evaluation;
+- Peer Evaluation;
+- Guest Evaluation.
+
+Player-safe summaries may include all rating aggregates by perspective, but must apply visibility rules.
+
+Never blend perspectives into one unlabeled score.
+
+Every metric, warning, text item, comparison, and evidence link must retain perspective labeling.
+
+Perspective ordering:
+
+1. self;
+2. coach;
+3. staff;
+4. peer;
+5. guest.
+
+## 8. Rating Aggregation
+
+For each `ObservationResponse` where:
+
+```text
+response_type = rating_1_5
+numeric_value is not null
+```
+
+Group by:
+
+- normalized category;
+- perspective.
+
+Category rule:
+
+- use `ObservationQuestion.category`;
+- when blank, use `Questions`;
+- trim surrounding whitespace;
+- compare category names case-insensitively for grouping;
+- display the first non-empty source spelling by earliest question order, falling back to title-cased normalized text.
+
+Calculate:
+
+- rating response count;
+- arithmetic mean;
+- contributing submitted observation count;
+- contributing evaluator count when visible;
+- contributing question count;
+- minimum and maximum only for internal read-model completeness, not required for V1 display.
+
+Display precision:
+
+- one decimal place.
+
+Persistence:
+
+- do not persist calculated values.
+
+Question-set compatibility:
+
+- category aggregation may combine responses across question-set versions only when the normalized category name matches;
+- do not combine individual questions merely because prompts look similar;
+- evidence links must preserve original question prompt and question-set version;
+- show a warning when more than one question-set version contributes to the summary;
+- if a future pilot shows category names changed meaning between versions, the future implementation must split those categories before launch.
+
+## 9. Minimum-Data Policy
+
+Category averages:
+
+- display an average when at least one valid rating exists;
+- always show count beside the average.
+
+Strength/opportunity labels:
+
+- require at least two valid ratings;
+- require at least one submitted observation;
+- apply within the same perspective and category;
+- never issue a label from a single rating.
+
+Thresholds:
+
+```text
+Possible strength: average >= 4.0
+Possible development opportunity: average <= 2.5
+Insufficient evidence: fewer than 2 ratings
+```
+
+These thresholds are approved for pilot use because they are simple, explainable, and conservative. They are not a permanent player-scoring model and should be reviewed after pilot feedback.
+
+## 10. Strength And Opportunity Labels
+
+Allowed labels:
+
+- `Possible strength`
+- `Possible development opportunity`
+- `Insufficient evidence`
+
+Disallowed labels:
+
+- weakness;
+- deficiency;
+- below average;
+- elite;
+- top;
+- poor;
+- ranking language.
+
+Each label must show:
+
+- perspective;
+- category;
+- average;
+- rating count;
+- submitted observation count;
+- evidence link(s);
+- explanatory text that the label summarizes submitted evaluation responses only.
+
+Labels must never imply objective truth or selection decisions.
+
+## 11. Self-Versus-Coach Comparison
+
+For each category where self and coach ratings both exist:
+
+```text
+difference = self_average - coach_average
+```
+
+Labels:
+
+```text
+Aligned: absolute difference < 0.5
+Self rates higher: difference >= 0.5
+Coach rates higher: difference <= -0.5
+```
+
+Display:
+
+- self average;
+- self rating count;
+- coach average;
+- coach rating count;
+- difference rounded to one decimal place;
+- neutral discussion-oriented wording.
+
+Do not:
+
+- compare when either side lacks data;
+- compare self against staff, peer, guest, or combined external averages in V1;
+- imply that self or coach perspective is correct;
+- convert the comparison into a score.
+
+## 12. Qualitative Text Visibility
+
+Qualitative text means `ObservationResponse.response_type = text` and non-empty `text_value`.
+
+Staff/coach projection:
+
+- show submitted text feedback;
+- group by perspective and submitted observation;
+- preserve exact source wording;
+- show question label;
+- show submitted date;
+- show season/cycle context;
+- show evaluator display name according to existing coach review behavior;
+- do not show evaluator email, internal account metadata, import metadata, or password/provisioning data.
+
+Player-safe projection:
+
+- hide evaluator names, usernames, and emails;
+- show perspective label and evaluator role/category only;
+- show self text;
+- show coach text;
+- show staff text;
+- show guest text only if it is already visible through existing My Evaluations behavior;
+- hide peer free-text comments in Player Development Summary V1;
+- show peer rating aggregates with perspective label;
+- link only to player-safe source routes.
+
+Rationale for hiding peer text from players:
+
+- youth peer feedback is sensitive;
+- existing My Evaluations can show raw submitted evaluation detail, but V2 summaries are broader and more prominent;
+- hiding peer text in Phase 1 reduces retaliation and peer-pressure risk while preserving useful aggregate signals.
+
+No projection may algorithmically classify comments as strengths or opportunities.
+
+## 13. Evaluation Coverage Read Model
+
+`EvaluationCoverage` should include:
+
+- total submitted observations;
+- count by perspective;
+- count by cycle;
+- rating response count;
+- text response count;
+- contributing categories;
+- contributing question-set versions;
+- first submitted date;
+- latest submitted date;
+- warnings.
+
+Coverage is context, not a quality score.
+
+Warnings:
+
+- no submitted evaluations;
+- only one perspective available;
+- no coach evaluation;
+- no self evaluation;
+- multiple question-set versions;
+- legacy/no-season evidence excluded;
+- insufficient ratings for labels;
+- no text feedback.
+
+Warning ordering:
+
+1. no context;
+2. no submitted evaluations;
+3. legacy/no-season evidence excluded;
+4. multiple question-set versions;
+5. only one perspective available;
+6. no coach evaluation;
+7. no self evaluation;
+8. insufficient ratings for labels;
+9. no text feedback.
+
+Player-safe projection must suppress staff-only warnings such as legacy evidence counts if those warnings reveal hidden records.
+
+## 14. Evidence Links
+
+Every displayed metric, comparison, label, or text item must be traceable.
+
+`EvidenceLink` fields:
+
+- `title: str`
+- `perspective_label: str`
+- `evaluation_date: date | datetime | None`
+- `season_name: str`
+- `cycle_name: str`
+- `category: str`
+- `question_label: str`
+- `url: str`
+- `source_observation_id: int`
+- `is_player_safe: bool`
+
+Display labels must not expose raw internal IDs.
+
+URL rules:
+
+- player-safe links use `analytics:my-evaluation-detail`;
+- staff/coach links use `analytics:evaluation-review-detail`;
+- staff-only review links may use `analytics:observation-review-detail` only for staff-only surfaces;
+- if no authorized URL exists, omit the URL and show non-sensitive source metadata.
+
+Evidence links are generated by services, not templates.
+
+## 15. Permission Matrix
+
+| Viewer | Access Decision |
+| --- | --- |
+| Unauthenticated | denied |
+| Player with active self link to target player | allowed, player-safe projection only |
+| Player without active self link | denied |
+| Coach role | allowed, staff/coach projection, using current coach-review access |
+| Django staff/superuser | allowed, staff/coach projection |
+| `AccountProfile.role = staff` without Django staff/superuser | allowed only if current coach-review access allows it; does not become Django staff |
+| Guest evaluator | denied by default |
+| Parent/guardian | denied in Phase 1 |
+
+Coach access decision:
+
+```text
+Reuse current coach-review access exactly.
+Do not introduce stricter team scoping in Player Development Summary V1.
+Clearly document that this is the same broad submitted-evaluation review scope coaches already have.
+```
+
+This is acceptable for Phase 1 because strict team-scoped coach permissions are explicitly deferred in Seasonal Participation V1. If the pilot requires team-scoped access before summaries launch, that must become a separate prerequisite phase.
+
+## 16. Permission Service Design
+
+Future module:
+
+```text
+development/services/permission_service.py
+```
+
+Public functions:
+
+```python
+can_view_player_development_summary(user, player) -> bool
+can_view_player_safe_summary(user, player) -> bool
+can_view_staff_summary(user, player) -> bool
+summary_visibility_for_user(user, player) -> SummaryVisibility
+```
+
+`SummaryVisibility` fields:
+
+- `can_view: bool`
+- `projection: Literal["player_safe", "staff_coach"] | None`
+- `can_view_evaluator_identity: bool`
+- `can_view_peer_text: bool`
+- `can_view_staff_warnings: bool`
+- `denial_reason: str`
+
+Composition rules:
+
+- `can_view_player_safe_summary()` delegates to `analytics.services.permissions.can_view_my_evaluations(user, player=player)`;
+- `can_view_staff_summary()` delegates to `analytics.services.permissions.can_review_submitted_evaluations(user)`;
+- guest and parent denial should be explicit even if they can submit evaluations;
+- templates must receive a projection that already reflects visibility.
+
+Do not use `AccountProfile.role` as a substitute for Django staff privileges.
+
+## 17. Summary Service Design
+
+Future module:
+
+```text
+development/services/summary_service.py
+```
+
+Public entry point:
+
+```python
+build_player_development_summary(
+    *,
+    viewer,
+    player,
+    season=None,
+    evaluation_cycle=None,
+) -> PlayerDevelopmentSummary
+```
+
+Responsibilities:
+
+- validate viewer permission;
+- resolve season/cycle context;
+- query authorized submitted evidence;
+- build neutral aggregation;
+- project to player-safe or staff/coach output;
+- calculate deterministic metrics;
+- create warnings;
+- create evidence links;
+- return immutable/read-only dataclasses.
+
+Must not:
+
+- save models;
+- update evaluations;
+- modify snapshots;
+- create summaries;
+- send messages;
+- call AI;
+- make HTTP requests;
+- implement account-role rules directly;
+- render HTML.
+
+Recommended private helpers:
+
+- `resolve_summary_context()`
+- `submitted_summary_observations()`
+- `build_neutral_aggregation()`
+- `build_staff_coach_projection()`
+- `build_player_safe_projection()`
+- `category_sort_key()`
+- `perspective_sort_key()`
+- `build_evidence_link()`
+
+Keep projection logic in `summary_service.py` for Phase 1. Do not add a separate projection service until the module becomes difficult to maintain.
+
+## 18. Read Model Design
+
+Use frozen dataclasses in:
+
+```text
+development/read_models.py
+```
+
+### SummaryVisibility
+
+- `can_view: bool`
+- `projection: str`
+- `can_view_evaluator_identity: bool`
+- `can_view_peer_text: bool`
+- `can_view_staff_warnings: bool`
+- `denial_reason: str`
+
+### DevelopmentContext
+
+- `player: players.Player`
+- `season: seasons.Season | None`
+- `evaluation_cycle: analytics.EvaluationCycle | None`
+- `scope: str` (`cycle`, `season`, or `none`)
+- `title: str`
+- `subtitle: str`
+- `available_seasons: list[SeasonOption]`
+- `available_cycles: list[CycleOption]`
+
+### SeasonOption / CycleOption
+
+- `id: int`
+- `label: str`
+- `is_selected: bool`
+- `is_active: bool`
+
+### EvaluationCoverage
+
+- `total_submitted_observations: int`
+- `by_perspective: list[PerspectiveCoverage]`
+- `by_cycle: list[CycleCoverage]`
+- `rating_response_count: int`
+- `text_response_count: int`
+- `categories: list[str]`
+- `question_set_versions: list[str]`
+- `first_submitted_at: object | None`
+- `latest_submitted_at: object | None`
+- `warnings: list[SummaryWarning]`
+
+### PerspectiveCoverage
+
+- `perspective: str`
+- `label: str`
+- `submitted_observation_count: int`
+- `rating_response_count: int`
+- `text_response_count: int`
+
+### CycleCoverage
+
+- `cycle_id: int`
+- `cycle_name: str`
+- `submitted_observation_count: int`
+
+### CategorySummary
+
+- `category: str`
+- `perspective_summaries: list[PerspectiveCategorySummary]`
+- `warnings: list[SummaryWarning]`
+- `evidence_links: list[EvidenceLink]`
+
+### PerspectiveCategorySummary
+
+- `perspective: str`
+- `perspective_label: str`
+- `average: Decimal | None`
+- `display_average: str`
+- `rating_count: int`
+- `submitted_observation_count: int`
+- `question_count: int`
+- `label: str` (`Possible strength`, `Possible development opportunity`, or `Insufficient evidence`)
+- `evidence_links: list[EvidenceLink]`
+
+### PerspectiveComparison
+
+- `category: str`
+- `self_average: Decimal`
+- `coach_average: Decimal`
+- `self_rating_count: int`
+- `coach_rating_count: int`
+- `difference: Decimal`
+- `label: str`
+- `help_text: str`
+- `evidence_links: list[EvidenceLink]`
+
+### TextFeedbackItem
+
+- `perspective: str`
+- `perspective_label: str`
+- `question_label: str`
+- `text: str`
+- `submitted_at: object | None`
+- `season_name: str`
+- `cycle_name: str`
+- `evaluator_display: str`
+- `evidence_link: EvidenceLink | None`
+
+For player-safe projection, `evaluator_display` must be blank or a role/category label only.
+
+### EvidenceLink
+
+Use fields from the Evidence Links section.
+
+### SummaryWarning
+
+- `code: str`
+- `message: str`
+- `severity: str` (`info`, `warning`, `critical`)
+- `staff_only: bool`
+
+### PlayerDevelopmentSummary
+
+- `context: DevelopmentContext`
+- `visibility: SummaryVisibility`
+- `coverage: EvaluationCoverage`
+- `category_summaries: list[CategorySummary]`
+- `self_vs_coach: list[PerspectiveComparison]`
+- `text_feedback: list[TextFeedbackItem]`
+- `evidence_links: list[EvidenceLink]`
+- `is_empty: bool`
+
+Design choice:
+
+```text
+Use one neutral aggregation result and separate staff/coach and player-safe projections.
+```
+
+Sensitive evaluator metadata must not exist in player-safe read models.
+
+## 19. Source Query Strategy
+
+The summary service should:
+
+- load the player once using `players.Player`;
+- load selected season/cycle once;
+- resolve available seasons/cycles with bounded queries;
+- query submitted observations in one queryset;
+- use `select_related("player", "evaluation_cycle", "season", "evaluator", "evaluator_role", "question_set")`;
+- use `prefetch_related("responses__question")`;
+- filter by player, observation type, submitted status, and season/cycle;
+- exclude legacy/no-season records from the main queryset;
+- run a separate lightweight `exists()` check for legacy/no-season evidence for staff/coach warnings;
+- avoid one query per category, perspective, response, or evidence link.
+
+The future implementation may reuse `analytics.services.evaluation_review_service.submitted_evaluation_queryset()` for base submitted-review behavior, but it must add season/cycle scoping and player-safe projection. It must not reuse `analytics.services.comparison_service.get_player_score_summary()` because that service blends perspectives and is staff comparison-oriented.
+
+## 20. Ordering Rules
+
+Deterministic ordering is required.
+
+- seasons: current season first, then most recent `starts_on`, then name, then id;
+- cycles: most recent `starts_on`, then created date, then name, then id;
+- perspectives: self, coach, staff, peer, guest;
+- categories: lowest source question display order for the normalized category, then display name;
+- category perspective summaries: perspective order;
+- evaluations: newest submitted first, then created date, then id;
+- text feedback: newest submitted first, then question display order, then response id;
+- warnings: warning order from the Evaluation Coverage section;
+- evidence links: newest submitted first, then observation id, then question display order.
+
+## 21. URLs And Routes
+
+Future namespace:
+
+```text
+development
+```
+
+Required routes:
+
+```text
+/development/players/<int:player_id>/summary/
+/development/my/summary/
+```
+
+Required names:
+
+```text
+development:player-summary
+development:my-summary
+```
+
+Optional query parameters:
+
+```text
+season=<season_id>
+cycle=<evaluation_cycle_id>
+```
+
+Server-side validation:
+
+- reject or normalize mismatched season/cycle;
+- derive season from cycle when cycle is supplied;
+- do not let player-safe route accept arbitrary player IDs;
+- do not create separate coach and staff routes unless future presentation differences require them.
+
+## 22. View Plan
+
+Future module:
+
+```text
+development/views.py
+```
+
+### PlayerDevelopmentSummaryView
+
+Route:
+
+```text
+development:player-summary
+```
+
+Responsibilities:
+
+- require authentication;
+- resolve `players.Player` by `player_id`;
+- parse optional `season` and `cycle`;
+- call `build_player_development_summary()`;
+- render staff/coach projection;
+- raise `PermissionDenied` for unauthorized users;
+- use existing 404 behavior for missing player/context records.
+
+### MyDevelopmentSummaryView
+
+Route:
+
+```text
+development:my-summary
+```
+
+Responsibilities:
+
+- require authentication;
+- resolve active self-linked players through `accounts.services.link_service.get_self_linked_players()`;
+- if no self link, render no-self-link empty state;
+- if one self-linked player, summarize that player;
+- if multiple self-linked players, render a selector and summarize the selected player only if supplied through a validated safe parameter or choose the primary player when available;
+- parse optional `season` and `cycle`;
+- call `build_player_development_summary()`;
+- render player-safe projection.
+
+Views must not calculate averages, filter comments, or build evidence links.
+
+## 23. Template Plan
+
+Future templates:
+
+```text
+development/templates/development/base.html
+development/templates/development/player_summary.html
+development/templates/development/my_summary.html
+development/templates/development/_coverage.html
+development/templates/development/_warnings.html
+development/templates/development/_category_summary.html
+development/templates/development/_comparison.html
+development/templates/development/_text_feedback.html
+development/templates/development/_evidence_links.html
+```
+
+Templates should display:
+
+- player/context header;
+- season/cycle controls;
+- coverage;
+- warnings;
+- category summaries;
+- self-versus-coach comparisons;
+- qualitative feedback;
+- source evidence;
+- constructive empty states.
+
+Templates must not:
+
+- compute metrics;
+- filter sensitive fields;
+- enforce permissions;
+- hide peer text by conditionally checking raw model fields;
+- display empty sections.
+
+## 24. Navigation And Entry Points
+
+Future implementation should add links only after the `development` app exists.
+
+Recommended links:
+
+- staff Analytics player profile: `Development Summary`;
+- coach evaluation-review rows/details: `Development Summary`;
+- player account/profile area or My Evaluations page: `My Development Summary`;
+- Analytics Command Center quick links only after pilot staff confirms the page is useful.
+
+Do not add a new broad dashboard in Player Development Summary V1.
+
+## 25. Empty States
+
+Use constructive text.
+
+### No Self Link
+
+```text
+Your account is not linked to a player profile.
+```
+
+### Multiple Self Links
+
+```text
+Choose which linked player summary you want to view.
+```
+
+### No Current Context
+
+```text
+No current evaluation period is available.
+```
+
+### No Submitted Evaluations
+
+```text
+No submitted evaluations are available for this player in the selected period.
+```
+
+### Insufficient Data
+
+```text
+There is not yet enough evaluation evidence to identify possible strengths or development opportunities.
+```
+
+### Legacy Evidence Excluded
+
+Staff/coach only:
+
+```text
+Some legacy evaluations are not included because they do not have verified seasonal context.
+```
+
+## 26. Performance Plan
+
+Expected behavior:
+
+- bounded query count independent of response count;
+- no N+1 query over responses, questions, categories, or evidence links;
+- no per-category database queries;
+- no per-evidence-link database queries;
+- player-safe projection should avoid exposing sensitive fields even if fetched for staff/coach projection.
+
+Representative test target:
+
+- building a summary for one player with multiple submitted observations and responses should stay under a small fixed query count determined during implementation.
+
+Do not introduce caching in V1.
+
+## 27. Migration Decision
+
+Decision:
+
+```text
+No migrations expected.
+```
+
+Future implementation should add:
+
+- `development` Django app;
+- `apps.py`;
+- `urls.py`;
+- `views.py`;
+- `read_models.py`;
+- service modules;
+- templates;
+- tests;
+- documentation updates.
+
+It should not add:
+
+- database models;
+- admin registration;
+- migrations;
+- persisted summary tables.
+
+If implementation discovers a concrete need for persistence, stop and return BLOCKED instead of creating a migration.
+
+## 28. Future App Structure
+
+Recommended structure:
+
+```text
+development/
+    __init__.py
+    apps.py
+    urls.py
+    views.py
+    read_models.py
+    services/
+        __init__.py
+        permission_service.py
+        summary_service.py
+    templates/
+        development/
+            base.html
+            player_summary.html
+            my_summary.html
+            _coverage.html
+            _warnings.html
+            _category_summary.html
+            _comparison.html
+            _text_feedback.html
+            _evidence_links.html
+    tests/
+        __init__.py
+        helpers.py
+        test_permission_service.py
+        test_summary_service.py
+        test_player_safe_projection.py
+        test_views.py
+```
+
+Use one small `views.py` initially. Split only if implementation complexity justifies it.
+
+Do not create `models.py` unless Django app conventions require an empty file. If an empty `models.py` is created, it must define no models.
+
+## 29. Testing Plan
+
+### Summary Service Tests
+
+Cover:
+
+- explicit cycle scope;
+- explicit season scope;
+- default context resolution priority;
+- invalid cycle/season mismatch;
+- submitted-only inclusion;
+- exclusion of draft, reopened, archived, and legacy/no-season records;
+- inclusion of inactive season/cycle only when explicitly selected by staff/coach;
+- perspective separation;
+- category averages;
+- counts;
+- threshold labels;
+- self-versus-coach comparison;
+- warning generation;
+- stable ordering;
+- multiple question-set versions;
+- no model persistence.
+
+### Permission Service Tests
+
+Cover:
+
+- player self-link access;
+- player other-player denial;
+- inactive self-link denial;
+- multiple self-link behavior;
+- coach access matching current coach review;
+- Django staff/superuser access;
+- `AccountProfile.role = staff` without Django staff behavior;
+- guest evaluator denial;
+- parent/guardian denial;
+- unauthenticated denial.
+
+### Player-Safe Projection Tests
+
+Assert player-safe output excludes:
+
+- evaluator names;
+- usernames;
+- emails;
+- hidden peer text;
+- internal staff warnings;
+- account metadata;
+- raw internal IDs in display labels.
+
+Assert player-safe output includes:
+
+- allowed rating aggregates;
+- allowed coach/staff/self text;
+- perspective labels;
+- player-safe evidence URLs only.
+
+### View Tests
+
+Cover:
+
+- authentication;
+- route resolution;
+- season/cycle query parameters;
+- mismatched season/cycle handling;
+- 403 behavior;
+- 404 behavior;
+- no-self-link state;
+- multiple-self-link state;
+- staff/coach projection context;
+- player-safe projection context;
+- template names;
+- evidence links in rendered context.
+
+### Regression Tests
+
+Future implementation must preserve:
+
+- `accounts` tests;
+- `players` tests;
+- `seasons` tests;
+- `analytics` tests;
+- `drafts` tests;
+- `pdp` tests;
+- full suite.
+
+## 30. Pilot Rollout Boundary
+
+Player Development Summary V1 should launch as a pilot.
+
+Pilot boundary:
+
+- staff/coach access first;
+- player-safe access enabled only after staff reviews sample summaries;
+- one season;
+- one evaluation cycle;
+- one or two teams;
+- small player cohort;
+- no parent access;
+- no exports;
+- no AI;
+- no ranking language.
+
+Feature flag decision:
+
+```text
+No generalized feature-flag system is required for Phase 1.
+```
+
+Rollout should be controlled by:
+
+- route permissions;
+- limited navigation links;
+- pilot user communication;
+- staff review before exposing player-safe links.
+
+If production operations require a runtime switch before launch, that should be planned as a small deployment-control task, not added implicitly to the summary implementation.
+
+## 31. Documentation Deliverables For Implementation
+
+Future coding phase must update:
+
+- `README.md` if the `development` app is added to the current platform list;
+- `docs/ARCHITECTURE.md` when the app is actually implemented;
+- `docs/USER_MANUAL.md` when user-visible summary pages exist;
+- `docs/product/platform_v2/README.md` to mark Phase 1 implementation status;
+- this engineering plan with implementation decisions and review notes.
+
+Do not document AI, parent access, exports, reports, or development plans as implemented.
+
+## 32. Implementation Acceptance Criteria
+
+### A. App Boundary
+
+- `development` app exists.
+- No database models are added.
+- No migrations are created.
+- No PDP dependency exists.
+- Dependencies flow only from `development` to `players`, `accounts`, `seasons`, and `analytics`.
+
+### B. Summary Service
+
+- Deterministic summary is generated for selected player/context.
+- Submitted records only are included.
+- Season/cycle period is enforced.
+- Perspectives remain separate.
+- Category averages use the approved formula.
+- Strength/opportunity labels use approved thresholds.
+- Every displayed conclusion is evidence-traceable.
+
+### C. Privacy
+
+- Player-safe output strips evaluator identity.
+- Peer free text is hidden from player-safe summaries.
+- Guest and parent users are denied summary access.
+- Account metadata is not exposed.
+- Staff-only warnings are suppressed for players.
+
+### D. Permissions
+
+- Current player self-link rules are reused.
+- Current coach review access is reused.
+- Django staff/superuser access is reused.
+- No new team-scoped policy is introduced accidentally.
+- `AccountProfile.role = staff` does not grant Django staff access.
+
+### E. UX
+
+- Staff/coach summary page works.
+- Player-safe summary page works.
+- Empty states are clear.
+- Insufficient-data states are clear.
+- Evidence links route to authorized source pages.
+- No ranking, percentile, or overall score is displayed.
+
+### F. Performance
+
+- Query count is bounded.
+- No N+1 queries are introduced.
+- Ordering is deterministic.
+
+### G. Migration
+
+- No models.
+- No migrations.
+- `makemigrations --check` passes.
+
+### H. Tests
+
+- Focused `development` tests exist.
+- Privacy and permission cases are covered.
+- Deterministic metric tests are covered.
+- Full regression suite passes.
+
+### I. Documentation
+
+- User manual updated after visible routes exist.
+- Architecture updated after `development` app exists.
+- Product status updated.
+- No deferred features are described as implemented.
+
+## 33. Resolved Phase 0 Open Questions
+
+Minimum response count:
+
+- one valid rating may display an average;
+- two valid ratings are required for strength/opportunity labels.
+
+Peer text visibility:
+
+- hide peer free-text comments from player-safe summaries in Phase 1;
+- show peer rating aggregates with perspective labels;
+- staff/coach projection may show peer text under current review access.
+
+Coach access:
+
+- reuse current broad coach-review access;
+- strict team scoping remains deferred and must not be silently added.
+
+Route placement:
+
+- use `/development/players/<int:player_id>/summary/` and `/development/my/summary/`;
+- link from Analytics and player-facing pages only after implementation.
+
+Summary wording approval:
+
+- staff/coordinators own pilot wording approval before player-safe rollout.
+
+## 34. Final Review
+
+Reviewed from these perspectives:
+
+- player: player-safe projection hides evaluator identity and peer text;
+- coach: staff/coach projection gives source-grounded, perspective-aware summaries;
+- staff reviewer: every conclusion links to evidence and exposes warnings;
+- privacy reviewer: sensitive identity is stripped before player templates;
+- security reviewer: existing permission services are composed, not duplicated in templates;
+- senior Django engineer: views stay thin, services own logic, no migrations expected;
+- data architect: source data remains authoritative and derived values are computed;
+- test engineer: deterministic ordering, thresholds, privacy, and permissions are testable;
+- pilot operator: pilot scope is narrow and rollback is simple because no persistence is added.
+
+Terminal state:
+
+```text
+PASS
+```
````

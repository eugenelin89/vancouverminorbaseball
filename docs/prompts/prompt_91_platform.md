# Prompt 91: Platform

## User Prompt

````text
Complete Platform V2 Phase 0 only: Player Development Intelligence Product and Implementation Planning.

Use continuous loop engineering.

Continue until Platform V2 has a concrete, repository-grounded implementation plan with clearly defined product scope, architecture boundaries, phases, acceptance criteria, risks, and pilot strategy.

Do not implement Platform V2 application code.

Do not modify models, migrations, services, views, forms, templates, URLs, permissions, tests, settings, or dependencies.

Do not start Player Development Summary implementation.

==================================================
Current State
=============

Platform V1 is complete.

Seasonal Participation V1 is:

```text
Feature Complete
Production Ready
Frozen
```

Repository Cleanup Phases 1 through 8 are complete.

The final repository audit concluded:

```text
READY FOR PLATFORM V2 PLANNING
```

Current foundations include:

* permanent player identity;
* permanent account identity;
* user-player relationships;
* seasons;
* season-specific teams;
* player roster memberships;
* coach seasonal assignments;
* season-aware player import;
* season-aware coach import;
* season-aware evaluation context;
* durable historical evaluation snapshots;
* staff Season Operations;
* player self-evaluation;
* coach evaluation;
* staff evaluation review;
* account operations;
* analytics command-center and review surfaces;
* stable service façades;
* coherent test packages;
* 458 passing tests.

Platform V2 product direction already exists in:

```text
docs/product/PLATFORM_V2_ROADMAP.md
```

This phase must turn that roadmap into a concrete implementation plan based on the repository as it exists now.

==================================================
Objective
=========

Plan Platform V2 as a new product phase centered on:

```text
Player Development Intelligence
```

The core goal is to transform existing evaluation, roster, and player-history data into useful development guidance without compromising:

* historical accuracy;
* privacy;
* role boundaries;
* human judgment;
* explainability;
* data ownership;
* V1 stability.

The plan should define:

1. Platform V2 product vision;
2. primary users;
3. real user problems;
4. product principles;
5. data foundations;
6. first implementation phase;
7. later phases;
8. AI boundaries;
9. privacy and permission boundaries;
10. rollout and pilot strategy;
11. success metrics;
12. stop/go criteria;
13. implementation acceptance criteria.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete planning, repository review, decision resolution, or documentation work remains.

PASS

The Platform V2 plan is complete, repository-grounded, internally consistent, committed, pushed, and the working tree is clean.

BLOCKED

A required product decision cannot be resolved from repository evidence or established strategy and requires explicit stakeholder direction.

NO_PROGRESS

Two consecutive loops fail to make meaningful progress toward an unresolved planning criterion.

Do not create artificial architecture merely to avoid BLOCKED.

==================================================
Established Loop Workflow
=========================

Every loop must:

1. reconcile the committed repository state;
2. read `AGENTS.md`;
3. confirm the working tree is clean;
4. read current product, architecture, user, seasonal, analytics, and audit documentation;
5. inspect relevant current models, services, permissions, views, and tests;
6. identify concrete product and architecture decisions;
7. create the next prompt archive before documentation changes;
8. update planning documents only;
9. review decisions from product, engineering, privacy, security, and operations perspectives;
10. resolve contradictions;
11. run documentation verification;
12. commit planning documentation;
13. finalize and separately commit the prompt archive;
14. push both commits;
15. re-read the committed diff;
16. confirm the working tree is clean;
17. reassess all acceptance criteria;
18. choose CONTINUE, PASS, BLOCKED, or NO_PROGRESS;
19. if CONTINUE, immediately begin the next loop.

Each loop must produce:

1. one planning/documentation commit;
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
* `docs/engineering/REPOSITORY_CLEANUP_FINAL_AUDIT.md`
* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`
* `docs/account_management/V1_SUMMARY.md`
* `docs/analytics/implementation/STATUS.md`
* relevant evaluation documentation;
* relevant PDP documentation;
* relevant current prompt archives.

Inspect sufficiently to ground the plan:

* `players/models.py`
* `accounts/models.py`
* `seasons/models.py`
* `analytics/models.py`
* `pdp/models.py`
* current evaluation services;
* current reporting and comparison services;
* current permissions;
* current player-facing evaluation views;
* current coach-review views;
* current staff Analytics views;
* current seasonal-history views;
* current tests for player, coach, and staff workflows.

Do not modify application code.

==================================================
Product Vision
==============

Define Platform V2 around a concise product vision.

Recommended direction:

> Help players, coaches, and staff understand development over time and turn evaluations into clear, evidence-based next steps.

The plan must distinguish Platform V2 from:

* registration software;
* team scheduling;
* stat tracking;
* recruiting software;
* automated coaching;
* generic AI chat;
* medical or injury diagnosis;
* player ranking systems.

Platform V2 should focus on development intelligence derived from existing trusted data.

==================================================
Primary Users
=============

Define the needs of:

## Player

Needs:

* understand strengths;
* understand development priorities;
* compare self-perception with coach feedback;
* see progress over time;
* receive clear next actions;
* retain access to historical evaluations.

## Coach

Needs:

* quickly understand a player’s development history;
* identify agreement and disagreement across evaluations;
* plan development priorities;
* track whether recommendations were followed;
* avoid reading every raw evaluation independently.

## Staff / Administrator

Needs:

* monitor evaluation completion;
* identify program-wide patterns;
* maintain privacy and role boundaries;
* review data quality;
* support coaches without replacing their judgment.

## Parent

Treat parent access as deferred unless repository and roadmap evidence clearly authorize it.

Do not assume parent access in the first implementation phase.

==================================================
Product Principles
==================

Define principles including:

* development over ranking;
* evidence over unsupported inference;
* historical context over mutable current fields;
* explainability over opaque scoring;
* human review over autonomous decisions;
* minimal data exposure;
* role-appropriate access;
* gradual pilot rollout;
* deterministic summaries before generative AI;
* reversible product decisions;
* no fabricated facts;
* no medical diagnosis;
* no automated roster or selection decisions.

==================================================
Recommended First Implementation Phase
======================================

The first implementation phase should normally be:

```text
Player Development Summary V1
```

This should be a deterministic, non-generative summary built from existing evaluation data.

The Phase 0 plan must determine whether this remains the correct first implementation after reviewing the repository.

If confirmed, define it precisely.

Potential summary sections:

* player identity and current-season context;
* evaluation coverage;
* latest submitted evaluations;
* self-evaluation versus coach-evaluation comparison;
* consistent strengths;
* recurring development opportunities;
* areas of agreement;
* areas of disagreement;
* recent changes;
* coach-authored comments;
* suggested discussion prompts;
* evidence links back to source evaluations.

Do not implement these sections in Phase 0.

==================================================
Deterministic Before AI
=======================

The first Platform V2 implementation should not require a language model.

Plan a deterministic summary layer using:

* existing submitted observations;
* response values;
* question categories;
* evaluation perspective;
* season;
* submitted snapshots;
* evaluation-cycle dates;
* existing comparison services;
* existing score-summary services;
* explicit rules.

Reasons to document:

* easier validation;
* stable output;
* lower privacy risk;
* lower operating cost;
* easier testing;
* clear provenance;
* safer pilot;
* baseline for later AI comparison.

Do not describe AI as required for Platform V2 Phase 1.

==================================================
AI Strategy
===========

Plan AI as a later optional layer.

Define allowed future uses such as:

* summarizing already-authorized evaluation evidence;
* drafting development-plan language;
* identifying themes for human review;
* generating coach discussion prompts;
* translating summaries into simpler language.

Define prohibited or high-risk uses:

* diagnosing injuries;
* psychological diagnosis;
* predicting professional potential;
* autonomous player ranking;
* autonomous team selection;
* inventing observations;
* inferring protected characteristics;
* exposing another player’s data;
* generating recommendations without evidence citations;
* replacing coach judgment.

Require future AI outputs to:

* cite source evaluations;
* distinguish evidence from interpretation;
* allow human editing;
* record generation time and model/version where appropriate;
* avoid becoming the authoritative data record;
* be regenerable;
* support removal;
* remain permission-scoped.

Do not implement AI integration.

==================================================
Data Foundation Review
======================

Map existing data to Platform V2 needs.

Review:

* permanent Player;
* Season;
* SeasonTeam;
* PlayerRosterMembership;
* CoachSeasonAssignment;
* EvaluationCycle;
* Observation;
* ObservationResponse;
* evaluation perspective;
* submitted snapshots;
* player links;
* current comparison and timeline services;
* PDP models.

Determine:

* what data is already sufficient;
* what is missing;
* what should remain computed;
* what might eventually be persisted;
* what should not be duplicated.

Prefer computed read models initially.

Do not recommend creating a new table unless persistence solves a concrete problem.

==================================================
PDP Relationship
================

The repository contains an older `pdp` bounded context.

The plan must explicitly decide Platform V2’s relationship with PDP.

Possible outcomes:

1. Platform V2 replaces PDP gradually;
2. Platform V2 reuses selected PDP models;
3. PDP remains legacy while new work belongs elsewhere;
4. a future migration phase consolidates them.

Base the decision on current code and documentation.

Do not automatically reuse PDP merely because its names sound relevant.

Do not delete or migrate PDP in Phase 0.

Recommended default unless evidence says otherwise:

* treat PDP as legacy/experimental;
* build Platform V2 summaries from current Analytics and Seasons data;
* plan PDP migration or retirement separately.

==================================================
Bounded Context Ownership
=========================

Determine ownership for Platform V2.

Possible approaches:

## Extend Analytics

Advantages:

* evaluations and comparisons already live there;
* summaries are evaluation-derived;
* existing permissions and review pages are nearby.

Risks:

* Analytics may become overly broad.

## Create A New Development App

Possible names:

* `development`
* `player_development`
* `insights`

Advantages:

* clear new bounded context;
* avoids overloading Analytics;
* can own summary read models and development plans.

Risks:

* additional cross-app coordination;
* may duplicate current Analytics services.

The Phase 0 plan must recommend one approach based on repository evidence.

Do not create the app in this phase.

The recommendation must define:

* model ownership;
* service ownership;
* view ownership;
* URL namespace;
* permission ownership;
* dependencies;
* forbidden dependencies.

==================================================
Read Models And Persistence
===========================

Determine whether Player Development Summary V1 should be:

* computed on request;
* cached;
* persisted as a snapshot;
* manually published;
* versioned.

Recommended initial approach:

* deterministic computed read model;
* no persisted summary;
* source observations remain authoritative;
* optional later publication/snapshot phase if product need is proven.

Consider:

* performance;
* reproducibility;
* historical interpretation;
* corrected evaluations;
* permissions;
* auditability;
* future AI outputs.

Document the decision.

==================================================
Summary Scope
=============

Define exactly which evaluations feed a summary.

Decide:

* selected season only;
* selected evaluation cycle;
* multiple cycles within one season;
* all historical seasons;
* submitted only;
* whether reopened observations count;
* whether self, peer, coach, staff, and guest perspectives are included;
* how duplicate or superseded evaluations are handled.

Recommended V1 direction:

* one selected player;
* one selected season;
* submitted observations only;
* include all authorized perspectives;
* clearly label perspective;
* preserve links to source observations;
* no cross-season aggregation in the first implementation.

Document alternatives and rationale.

==================================================
Scoring And Interpretation
==========================

Define safe deterministic rules.

Potential concepts:

* latest rating;
* average rating by category;
* response count;
* self-versus-coach difference;
* trend within season;
* frequently mentioned themes from structured question categories;
* evidence coverage.

Avoid:

* single opaque overall player score;
* rankings;
* percentile comparisons;
* unsupported weighting;
* hidden formulas;
* false precision.

Every metric should have:

* definition;
* source fields;
* minimum data requirements;
* missing-data behavior;
* display guidance;
* test expectations.

Do not finalize formulas without repository evidence about current question structures.

If necessary, document formula decisions as an explicit Phase 1 implementation task.

==================================================
Qualitative Comments
====================

Plan how free-text responses appear.

Recommended V1:

* display relevant coach/player comments;
* label source and perspective;
* do not algorithmically classify free text in deterministic Phase 1;
* do not expose evaluator identity beyond current authorization rules;
* do not merge comments into invented consensus.

Later AI may summarize comments only with explicit source attribution and permission controls.

==================================================
Permissions
===========

Define access for Player Development Summary V1.

Recommended baseline:

## Player

May view their own summary through an active self link.

## Coach

May view summaries according to current approved coach-review access.

Do not silently introduce strict team-scoped permissions unless separately approved.

## Staff / Admin

May view summaries according to existing Analytics review permissions.

## Guest Evaluator

No broad summary access by default.

## Parent

Deferred.

The plan must distinguish:

* current permissions reused in Phase 1;
* future stricter permissions;
* team-scoped permission work;
* parent access.

Do not mix permission redesign into summary implementation unless absolutely required.

==================================================
Privacy
=======

Document:

* minimum necessary data;
* perspective labeling;
* evaluator anonymity or identity rules;
* free-text sensitivity;
* staff access;
* player access;
* retention;
* exports;
* AI-provider boundaries;
* audit expectations;
* deletion/correction implications.

Require future implementation to avoid exposing:

* other players’ evaluations;
* coach-only staff notes where current rules prohibit it;
* temporary passwords;
* internal import metadata;
* account privilege information;
* hidden evaluator details.

==================================================
User Experience
===============

Plan a simple Phase 1 experience.

Potential entry points:

* player: My Development Summary;
* coach: player review detail;
* staff: Analytics player detail.

Avoid building a new dashboard ecosystem initially.

Define likely pages:

* summary landing/detail;
* evidence/source-evaluation links;
* empty state;
* insufficient-data state;
* legacy/no-season state;
* multiple-season selector only if necessary.

The first implementation should use server-rendered Django.

No JavaScript framework.

==================================================
Pilot Strategy
==============

Define a controlled pilot.

Recommended pilot:

* one active season;
* one or two teams;
* small player group;
* limited coaches;
* existing evaluation cycles;
* deterministic summary only;
* staff review before broad release.

Pilot workflow:

1. create/confirm season and teams;
2. import players and coaches;
3. create evaluation cycle;
4. collect self and coach evaluations;
5. review raw data quality;
6. generate summaries;
7. compare summaries with source evidence;
8. collect player/coach feedback;
9. identify confusing or misleading output;
10. make stop/go decision.

Do not require a full organization rollout.

==================================================
Success Metrics
===============

Define metrics such as:

* percentage of summaries with sufficient data;
* evaluation completion rate;
* time coaches spend reviewing a player;
* percentage of summary claims traceable to evidence;
* player understanding of strengths and priorities;
* coach agreement that summary is accurate;
* correction/error rate;
* privacy incidents;
* support requests;
* repeat use.

Avoid vanity metrics.

==================================================
Stop / Go Criteria
==================

Define explicit criteria.

Potential GO criteria:

* summaries accurately reflect source evaluations;
* no unauthorized data exposure;
* coaches find them useful;
* players understand them;
* insufficient-data states are clear;
* deterministic rules are explainable;
* performance is acceptable.

Potential STOP criteria:

* summaries imply unsupported conclusions;
* player or coach trust decreases;
* permissions are unclear;
* source evidence is difficult to verify;
* free-text creates privacy concerns;
* data coverage is too sparse;
* output encourages ranking rather than development.

==================================================
Recommended Implementation Phases
=================================

Create a concrete phased sequence.

A recommended outline:

## Platform V2 Phase 1 — Player Development Summary Foundation

* deterministic summary read model;
* player/season context;
* evaluation coverage;
* structured category summaries;
* self-versus-coach comparison;
* source evidence links;
* player/coach/staff views;
* permissions;
* empty/insufficient states;
* tests and docs.

## Platform V2 Phase 2 — Development Priorities And Plans

* explicit development priorities;
* coach-reviewed action plan;
* player goals;
* status and follow-up;
* no AI required.

## Platform V2 Phase 3 — Longitudinal Progress

* multi-cycle timeline;
* cross-season history;
* trend interpretation;
* preserved context;
* no ranking.

## Platform V2 Phase 4 — Reports And Sharing

* printable views;
* controlled exports;
* publication rules;
* privacy controls.

## Platform V2 Phase 5 — Optional AI Assistance

* evidence-grounded summaries;
* coach-editable drafts;
* generation provenance;
* privacy review;
* model evaluation;
* opt-in pilot.

## Platform V2 Phase 6 — Expanded Access And Permissions

* team-scoped coach permissions;
* parent access if approved;
* notification policy;
* audit enhancements.

Modify this sequence where repository evidence supports a better order.

==================================================
Phase 1 Implementation Boundary
===============================

Produce a detailed proposed scope for the next coding prompt.

It must specify:

* app/bounded-context ownership;
* services;
* read models;
* views;
* routes;
* templates;
* permissions;
* tests;
* documentation;
* migration expectations;
* explicit non-goals.

The Phase 0 plan should be detailed enough that the next prompt can implement Phase 1 without reopening foundational product decisions.

Do not write the Phase 1 coding prompt yet unless repository workflow explicitly stores a draft next-phase prompt.

==================================================
Migration Expectations
======================

Determine whether Phase 1 should require migrations.

Preferred outcome:

* no migration;
* computed summary from existing data.

If a migration is recommended, justify:

* why computation is insufficient;
* why persistence is required now;
* data ownership;
* lifecycle;
* versioning;
* rollback.

Do not create migrations in Phase 0.

==================================================
Risks
=====

Document risks including:

* sparse evaluation data;
* inconsistent question sets;
* misleading averages;
* self-versus-coach disagreement;
* free-text privacy;
* unauthorized access;
* legacy/no-season evaluations;
* overloading Analytics;
* duplicating PDP;
* premature AI;
* summary becoming treated as objective truth;
* player ranking pressure;
* performance;
* stale computed results;
* product complexity.

For each risk, document:

* likelihood;
* impact;
* mitigation;
* stop/go implication.

==================================================
Documentation Deliverables
==========================

Create or update documentation such as:

```text
docs/product/platform_v2/
    README.md
    implementation/
        engineering/
            platform_v2_phase_0_plan.md
```

Use existing repository conventions if a different structure is more appropriate.

Update:

* `docs/product/README.md`
* `docs/product/PLATFORM_V2_ROADMAP.md`
* `docs/ARCHITECTURE.md`

only as needed.

Do not rewrite historical Platform V1 or Seasonal Participation records.

==================================================
Scope Restrictions
==================

Do not:

* create a new Django app;
* modify models;
* create migrations;
* write services;
* create views;
* create forms;
* create templates;
* add URLs;
* modify permissions;
* modify tests;
* modify dependencies;
* modify deployment code;
* add AI integration;
* add external APIs;
* change Platform V1;
* unfreeze Seasonal Participation V1;
* remove PDP;
* add product functionality.

Documentation and planning only.

==================================================
Verification
============

Run:

```bash
git diff --check
```

Run the repository’s existing Markdown link sanity check if available.

Do not add new documentation tooling.

No Django tests are required unless non-documentation files are unexpectedly changed.

If any application file changes, treat that as a scope violation unless required solely for a documentation link and explicitly justified.

==================================================
Acceptance Criteria
===================

Do not declare PASS until all criteria are satisfied.

A. Product Vision

* Platform V2 vision is concrete;
* primary users and problems are defined;
* product principles are explicit;
* non-goals are clear.

B. Repository Grounding

* plan reflects current models, services, permissions, and docs;
* V1 foundations are reused appropriately;
* PDP relationship is decided;
* no duplicate bounded context is proposed without justification.

C. Phase 1

* first implementation phase is clearly defined;
* deterministic versus AI boundary is settled;
* data scope is settled;
* permissions are settled;
* migration expectations are settled;
* acceptance criteria are detailed.

D. AI

* AI is optional and deferred;
* allowed and prohibited uses are documented;
* evidence and human-review requirements are explicit.

E. Privacy

* role-based access and data exposure are defined;
* free-text risks are addressed;
* parent access remains explicitly decided;
* future exports and AI boundaries are acknowledged.

F. Pilot

* pilot population is defined;
* workflow is defined;
* success metrics are meaningful;
* stop/go criteria are explicit.

G. Roadmap

* implementation phases are ordered;
* dependencies are clear;
* deferred features are separated;
* no future phase is described as implemented.

H. Risks

* major product, data, privacy, architecture, and adoption risks are documented;
* mitigations are actionable.

I. Documentation

* Platform V2 planning docs exist;
* product roadmap and architecture remain consistent;
* no application code changed;
* links pass;
* `git diff --check` passes.

J. Git

* planning/documentation commit exists;
* prompt archive commit exists;
* both pushed;
* working tree is clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should:

1. review the repository and current roadmap;
2. decide bounded-context ownership;
3. decide PDP relationship;
4. confirm Player Development Summary V1 as first phase or justify an alternative;
5. define deterministic summary scope;
6. define permissions and privacy;
7. define implementation phases;
8. define pilot and success criteria;
9. create Platform V2 planning documents;
10. reconcile roadmap and architecture;
11. verify documentation;
12. commit, archive, push, and reassess.

Continue only if material product or architecture decisions remain unresolved.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* resolves a material product decision;
* resolves bounded-context ownership;
* resolves a data or permission boundary;
* defines an implementable Phase 1;
* clarifies privacy or AI rules;
* improves pilot or stop/go criteria;
* reconciles material documentation drift.

Adding more prose without resolving decisions does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* player;
* coach;
* staff administrator;
* privacy reviewer;
* security reviewer;
* product manager;
* senior Django engineer;
* data architect;
* future AI reviewer;
* pilot operator.

Confirm:

* Phase 1 solves a real user problem;
* outputs remain evidence-based;
* privacy boundaries are clear;
* deterministic logic comes before AI;
* current architecture supports the plan;
* PDP relationship is explicit;
* V1 remains untouched;
* the next implementation prompt can be written without reopening foundational decisions.

==================================================
Git Workflow
============

For every loop:

1. create the next prompt archive before documentation changes;
2. commit Platform V2 planning documentation;
3. update the prompt archive with:

   * implementation/planning commit hash;
   * product decisions;
   * bounded-context decision;
   * PDP decision;
   * Phase 1 scope;
   * AI boundaries;
   * privacy decisions;
   * pilot strategy;
   * risks;
   * verification;
   * remaining questions;
   * terminal state;
4. commit the prompt archive separately;
5. push both commits;
6. confirm the working tree is clean.

Suggested planning commit:

```text
Plan Platform V2 player development intelligence
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
* product vision;
* primary users;
* bounded-context ownership;
* PDP relationship;
* Phase 1 scope;
* deterministic summary rules;
* permissions;
* privacy;
* AI boundaries;
* pilot strategy;
* success metrics;
* stop/go criteria;
* implementation phases;
* migration expectations;
* risks;
* unresolved questions;
* verification;
* commits;
* push result;
* confirmation that no application code changed;
* confirmation that Platform V1 remains frozen;
* confirmation that the working tree is clean.
````

## Implementation Commit

`1e94d02 Plan Platform V2 product phase`

## Commit Diff

````diff
commit 1e94d02ac784479724fd1931a6fef82794f1e53e
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 16 14:28:04 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 16 14:28:04 2026 -0700

    Plan Platform V2 product phase
---
 docs/ARCHITECTURE.md                               |  17 +
 docs/product/PLATFORM_V2_ROADMAP.md                |   2 +
 docs/product/README.md                             |   1 +
 docs/product/platform_v2/README.md                 |  43 ++
 .../engineering/platform_v2_phase_0_plan.md        | 747 +++++++++++++++++++++
 5 files changed, 810 insertions(+)

diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 02dcb14..3f4f9e2 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -333,6 +333,23 @@ Dependency guidance:
 | LeagueHub | Planned | Planned |
 | Video | Planned | Planned |

+## Platform V2 Planning
+
+Platform V2 planning is underway as Player Development Intelligence. The Phase 0 product plan recommends a future `development` bounded context for player-development summaries and later development-plan workflows.
+
+No `development` app has been implemented yet. Until a reviewed implementation phase creates it, current ownership remains unchanged:
+
+- `analytics` owns submitted evaluations, responses, evaluator snapshots, timelines, comparisons, metrics, and review surfaces.
+- `players` owns canonical player identity.
+- `accounts` owns login identity, roles, and user-player links.
+- `seasons` owns season, team, roster, and coach assignment context.
+- `pdp` remains legacy/transitionary and should not become the dependency target for new Platform V2 work.
+
+Documentation:
+
+- [Platform V2 Roadmap](product/PLATFORM_V2_ROADMAP.md)
+- [Platform V2 Product Planning](product/platform_v2/README.md)
+
 ## Current Platform State

 The platform currently has:
diff --git a/docs/product/PLATFORM_V2_ROADMAP.md b/docs/product/PLATFORM_V2_ROADMAP.md
index f6d15eb..6e9f521 100644
--- a/docs/product/PLATFORM_V2_ROADMAP.md
+++ b/docs/product/PLATFORM_V2_ROADMAP.md
@@ -10,6 +10,8 @@ The recommended next product milestone is:
 Platform V2: Player Development Intelligence
 ```

+Phase 0 product and implementation planning is recorded in [Platform V2 Product Planning](platform_v2/README.md). That plan recommends Player Development Summary V1 as the first implementation phase, using deterministic computed read models before AI, reports, parent access, or persisted development-plan workflows.
+
 Seasonal Participation V1 is complete and frozen. It allows permanent players and coach accounts to be reused across seasons while evaluations retain historical team/division context. See [Seasonal Participation V1](../seasons/README.md).

 Platform V2 should turn collected evaluation data into useful player-development decision support. It should not begin with large dashboards, AI, rankings, or parent-facing raw data. The next immediate activity should be a real-world pilot using the completed Platform V1 workflows. Product decisions for Platform V2 should be driven by pilot evidence, data quality, privacy requirements, and user value.
diff --git a/docs/product/README.md b/docs/product/README.md
index 25733d2..e69d3e2 100644
--- a/docs/product/README.md
+++ b/docs/product/README.md
@@ -7,6 +7,7 @@ Product documents describe what the platform should become, why the work matters
 ## Documents

 - [Platform V2 Roadmap](PLATFORM_V2_ROADMAP.md)
+- [Platform V2 Product Planning](platform_v2/README.md)

 ## How To Use These Documents

diff --git a/docs/product/platform_v2/README.md b/docs/product/platform_v2/README.md
new file mode 100644
index 0000000..0823fae
--- /dev/null
+++ b/docs/product/platform_v2/README.md
@@ -0,0 +1,43 @@
+# Platform V2 Product Planning
+
+Platform V2 is the next product phase for the VCB Platform.
+
+Status:
+
+```text
+Phase 0 planning complete.
+No Platform V2 application code has been implemented.
+```
+
+## Product Direction
+
+Platform V2 is centered on Player Development Intelligence:
+
+> Help players, coaches, and staff understand development over time and turn evaluations into clear, evidence-based next steps.
+
+Platform V2 should build on the completed Platform V1 foundations:
+
+- canonical player identity in `players`;
+- account identity and user-player links in `accounts`;
+- season-aware rosters and coach assignments in `seasons`;
+- submitted evaluations, perspectives, snapshots, timelines, comparisons, and review surfaces in `analytics`;
+- legacy PDP coexistence without making PDP the dependency target for new work.
+
+## Phase 0 Decision Summary
+
+- The first implementation phase should be Player Development Summary V1.
+- The first implementation should be deterministic and non-AI.
+- Summaries should be computed read models at first, not persisted summary records.
+- A future `development` Django app is recommended as the Platform V2 bounded context.
+- The `development` app should consume `analytics`, `players`, `accounts`, and `seasons` services rather than duplicating their rules.
+- PDP should remain legacy/transitionary. Platform V2 should not depend on `pdp.PlayerProfile` or PDP development models.
+- Parent access, AI-generated summaries, report exports, rankings, and development-plan persistence are deferred.
+
+## Planning Documents
+
+- [Platform V2 Roadmap](../PLATFORM_V2_ROADMAP.md)
+- [Phase 0 Engineering Plan](implementation/engineering/platform_v2_phase_0_plan.md)
+
+## Implementation Rule
+
+Do not implement Platform V2 from the roadmap alone. Create or update an approved phase-specific engineering plan before writing application code.
diff --git a/docs/product/platform_v2/implementation/engineering/platform_v2_phase_0_plan.md b/docs/product/platform_v2/implementation/engineering/platform_v2_phase_0_plan.md
new file mode 100644
index 0000000..20ded84
--- /dev/null
+++ b/docs/product/platform_v2/implementation/engineering/platform_v2_phase_0_plan.md
@@ -0,0 +1,747 @@
+# Platform V2 Phase 0 Plan: Player Development Intelligence
+
+Status:
+
+```text
+Phase 0 complete.
+Ready for Player Development Summary V1 engineering planning.
+No Platform V2 application code has been implemented.
+```
+
+Date: 2026-07-16
+
+## 1. Executive Summary
+
+Platform V1 is complete enough to begin planning Platform V2. The repository now has permanent player identity, account identity, user-player links, seasons, roster memberships, coach assignments, season-aware imports, submitted evaluation snapshots, player self-evaluation, peer evaluation, coach evaluation, staff and coach review, player My Evaluations, command-center summaries, player timelines, player comparison, and stable service boundaries.
+
+Platform V2 should be built around Player Development Intelligence:
+
+> Help players, coaches, and staff understand development over time and turn evaluations into clear, evidence-based next steps.
+
+The recommended first implementation phase is:
+
+```text
+Player Development Summary V1
+```
+
+This should be a deterministic, privacy-aware, source-grounded summary of existing submitted evaluation data. It should not require AI, new evaluation workflows, parent access, rankings, charts, exports, or persisted summary tables.
+
+## 2. Repository-Grounded Baseline
+
+The current codebase provides these foundations for Platform V2:
+
+| Area | Current Owner | Relevant Current Data / Service |
+| --- | --- | --- |
+| Player identity | `players` | `players.Player`, aliases, source identifiers, source rows, tags |
+| Account identity | `accounts` | Django `User`, `AccountProfile`, `UserPlayerLink`, account roles |
+| Season context | `seasons` | `Season`, `SeasonTeam`, `PlayerRosterMembership`, `CoachSeasonAssignment` |
+| Evaluations | `analytics` | `EvaluationCycle`, `Observation`, `ObservationResponse`, `ObservationQuestion`, question categories |
+| Historical snapshots | `analytics` | submitted season/team/division/evaluator snapshots on `Observation` |
+| Perspective labels | `analytics` | self, peer, coach, staff, guest evaluation perspectives |
+| Player-facing access | `analytics` + `accounts` | My Evaluations access via active self player links |
+| Coach/staff review | `analytics` | submitted evaluation review and filtering |
+| Existing read models | `analytics` | player search, timeline, comparison, metrics, reporting, draft context services |
+| Legacy development app | `pdp` | legacy `PlayerProfile`, PDP-specific evaluations, logs, goals, AI scaffolding |
+
+The final cleanup audit concluded:
+
+```text
+READY FOR PLATFORM V2 PLANNING
+```
+
+No critical or high architecture, security, transaction, or performance blocker was identified before starting this planning phase.
+
+## 3. Product Vision
+
+Platform V2 should turn evaluation and roster history into development decision support.
+
+It should help answer:
+
+- What are this player's current strengths?
+- What should this player work on next?
+- How do self, peer, coach, staff, and guest perspectives compare?
+- Is there enough evaluation coverage to trust the summary?
+- What changed across cycles or seasons?
+- Which evidence supports each summary statement?
+- What is safe and appropriate to show to players?
+
+Platform V2 is not:
+
+- registration software;
+- team scheduling software;
+- general stat tracking;
+- recruiting software;
+- automated coaching;
+- generic AI chat;
+- injury, medical, or psychological diagnosis;
+- an automated player ranking or selection system.
+
+Final baseball decisions remain with coaches, coordinators, staff, administrators, players, and families. Software should organize evidence and context, not replace human judgment.
+
+## 4. Primary Users
+
+### Players
+
+Players need feedback that is understandable, constructive, privacy-safe, and tied to their own development.
+
+Important needs:
+
+- understand strengths;
+- understand development priorities;
+- distinguish self-evaluation from external evaluation;
+- compare self-perception with coach feedback without exposing private evaluator identities;
+- see progress over time;
+- know what to discuss with coaches next.
+
+### Coaches
+
+Coaches need a concise way to understand a player before planning feedback or development work.
+
+Important needs:
+
+- see recent submitted evaluations without reading every raw response first;
+- identify recurring strengths and opportunities;
+- distinguish perspective differences;
+- understand season/team context;
+- link back to source evaluations when details matter.
+
+### Staff And Administrators
+
+Staff need oversight, consistency, and privacy control.
+
+Important needs:
+
+- monitor data completeness;
+- verify summaries against source data;
+- preserve historical context;
+- review pilot quality before expanding access;
+- avoid accidental exposure of private youth data.
+
+### Parents
+
+Parent access is deferred.
+
+Parents may eventually receive approved player-development summaries, but Platform V2 Phase 1 should not expose raw evaluations or evaluator identities to parents. Parent access needs a separate visibility and approval plan.
+
+## 5. Product Principles
+
+- Development over ranking.
+- Evidence over unsupported inference.
+- Historical context over mutable current fields.
+- Explainability over opaque scoring.
+- Human review over autonomous decisions.
+- Minimal data exposure.
+- Role-appropriate access.
+- Deterministic summaries before generative AI.
+- Reversible product decisions.
+- No fabricated facts.
+- No medical, injury, or psychological diagnosis.
+- No automated roster, draft, placement, scholarship, or selection decisions.
+- No single overall player score unless explicitly approved in a future phase.
+
+## 6. Data Foundation Assessment
+
+### Already Sufficient
+
+The repository already has enough structure for a first deterministic summary:
+
+- canonical player records;
+- active/inactive player state;
+- active account/player self links;
+- seasons and current-season state;
+- season teams and roster memberships;
+- coach season assignments;
+- evaluation cycles;
+- submitted observations;
+- question categories;
+- rating responses;
+- text responses;
+- evaluator role snapshots;
+- evaluation perspective snapshots;
+- submitted-at timestamps;
+- submitted season/team/division snapshots.
+
+### Missing Or Not Yet Mature
+
+These are not blockers for Phase 1, but should be visible risks:
+
+- real production evaluation volume may be low;
+- question categories may need validation after pilot usage;
+- stricter team-scoped coach permissions are deferred;
+- parent visibility rules are not defined;
+- report approval/publishing rules are not defined;
+- no audit system exists yet for generated summaries or report sharing;
+- PDP migration or retirement is not planned in detail.
+
+### Should Remain Computed Initially
+
+These should be computed from source data in Player Development Summary V1:
+
+- category averages;
+- perspective-specific averages;
+- evaluation counts;
+- data-completeness warnings;
+- self-versus-coach differences;
+- latest evaluation lists;
+- source evidence links;
+- summary section visibility.
+
+Computed read models preserve source authority and avoid storing derived conclusions before the product has been validated.
+
+### Should Not Be Duplicated
+
+Platform V2 should not duplicate:
+
+- canonical player identity;
+- account roles or links;
+- season/team/roster membership state;
+- submitted evaluation responses;
+- evaluator identity snapshots;
+- PDP `PlayerProfile` identity.
+
+## 7. PDP Relationship
+
+Decision:
+
+```text
+PDP remains legacy/transitionary. Platform V2 should not depend on PDP models.
+```
+
+Rationale:
+
+- `players.Player` is now the canonical future player identity model.
+- `accounts` owns platform login identity and user-player links.
+- `seasons` owns roster participation.
+- `analytics` owns submitted evaluations and evaluator snapshots.
+- PDP has overlapping historical models and AI/development scaffolding, but those are not the current platform-forward data sources.
+
+Phase 1 should build from `players`, `accounts`, `seasons`, and `analytics`.
+
+PDP migration, consolidation, or retirement requires a separate plan. Phase 0 does not delete, migrate, or bypass current PDP behavior.
+
+## 8. Bounded Context Recommendation
+
+Recommendation:
+
+```text
+Create a future Django app named development for Platform V2 implementation.
+```
+
+Do not create the app in Phase 0.
+
+### Why Not Put Everything In Analytics?
+
+Analytics already owns observations, metrics, comparisons, timelines, command-center summaries, and review surfaces. Player Development Intelligence will likely grow toward development summaries, goals, plans, progress narratives, report approval, and eventually parent-visible outputs. Keeping that product area inside Analytics would make Analytics too broad.
+
+### Why A New Development App?
+
+A `development` app gives Platform V2 a clear bounded context:
+
+- owns player-development summary read models;
+- owns future development-plan workflows if approved;
+- owns future development-summary pages and reports;
+- consumes Analytics evidence instead of owning raw evaluations;
+- avoids depending on PDP legacy models;
+- keeps new V2 product language separate from V1 operational analytics.
+
+### Ownership Boundaries
+
+Future `development` app should own:
+
+- player-development summary services;
+- summary read models/dataclasses;
+- development-summary views/templates;
+- future development-plan and progress workflows only when explicitly approved;
+- development-specific permission composition that delegates to owning services.
+
+Future `development` app must not own:
+
+- canonical player identity;
+- account identity or account roles;
+- user-player links;
+- player imports;
+- coach imports;
+- season teams or roster memberships;
+- raw evaluation submission;
+- observation responses;
+- draft workflows;
+- PDP migration behavior.
+
+### Dependency Direction
+
+Allowed dependencies:
+
+```text
+development -> players
+development -> accounts
+development -> seasons
+development -> analytics
+```
+
+Expected service usage:
+
+- consume player lookup through `players` or existing Analytics player services;
+- consume self-link and role information through `accounts` services;
+- consume roster context through `seasons` services/models;
+- consume submitted evaluation evidence through `analytics` services/read models.
+
+Forbidden dependencies:
+
+- `development` must not import from `pdp`;
+- `analytics` should not import from `development` for core V1 evaluation behavior;
+- templates must not implement summary calculations;
+- views must not duplicate Analytics query logic.
+
+## 9. First Implementation Phase
+
+Recommended first implementation:
+
+```text
+Player Development Summary V1
+```
+
+### Goal
+
+Provide a concise, privacy-aware player-development summary using existing submitted evaluations and season context.
+
+### Target Users
+
+Initial target users:
+
+- staff;
+- coaches;
+- players for their own linked player record, using player-safe visibility.
+
+Deferred users:
+
+- parents;
+- unauthenticated users;
+- guest evaluators for broad summary access.
+
+### Strict Scope
+
+Player Development Summary V1 should include:
+
+- player identity header;
+- selected season/evaluation-cycle context;
+- evaluation coverage;
+- latest submitted evaluations;
+- perspective-specific category summaries;
+- self-versus-coach comparison when both exist;
+- role-labeled perspective summaries;
+- recent text feedback where visible;
+- data-completeness warnings;
+- evidence links back to authorized source evaluations;
+- empty states when data is insufficient.
+
+### Out Of Scope
+
+Do not include:
+
+- AI-generated summaries;
+- charts or dashboards;
+- exports or PDFs;
+- parent access;
+- published reports;
+- persistent development-plan models;
+- timeline database models;
+- rankings;
+- overall player score;
+- predictive claims;
+- medical/injury guidance;
+- new evaluation submission workflow;
+- new account or roster management workflow;
+- PDP migration.
+
+## 10. Proposed Phase 1 Technical Shape
+
+Phase 1 should be planned separately before implementation. The expected shape is:
+
+### App
+
+Create `development` only when Phase 1 implementation is approved.
+
+### Services
+
+Likely services:
+
+- `development/services/summary_service.py`
+- `development/services/permission_service.py`
+
+The summary service should assemble read models only. It should call existing Analytics services where practical and add perspective-aware logic where current V1 services are too broad.
+
+### Read Models
+
+Likely dataclasses:
+
+- `PlayerDevelopmentSummary`
+- `DevelopmentSummaryContext`
+- `EvaluationCoverage`
+- `PerspectiveSummary`
+- `CategoryDevelopmentSummary`
+- `PerspectiveComparison`
+- `EvidenceLink`
+- `DevelopmentSummaryWarning`
+
+These should be plain dataclasses/read models, not database models.
+
+### Views
+
+Likely server-rendered views:
+
+- staff/coach player summary detail;
+- player-safe own summary detail.
+
+Views should be thin:
+
+- resolve request parameters;
+- call permission service;
+- call summary service;
+- render template.
+
+### URLs
+
+Candidate routes:
+
+```text
+/development/players/<player_id>/summary/
+/development/my/summary/
+```
+
+Potential integration links:
+
+- staff player profile can link to development summary;
+- coach review rows can link to development summary;
+- player account/profile area can link to own summary.
+
+Do not add these routes until Phase 1 implementation is approved.
+
+### Templates
+
+Templates should render supplied read models only. They should not compute averages, compare perspectives, enforce permissions, or filter source data.
+
+### Migrations
+
+No migrations are expected for Player Development Summary V1.
+
+If implementation appears to require persistence, stop and document why. Persisted summaries, publication state, report approvals, and caching should be separate future phases.
+
+## 11. Deterministic Summary Rules
+
+### Source Data
+
+Use only:
+
+- submitted `analytics.Observation` records;
+- `coach_assessment` observation type;
+- active/relevant evaluation cycles;
+- rating responses;
+- text responses;
+- question categories;
+- submitted season/team/division snapshots;
+- evaluator role and perspective snapshots.
+
+Exclude:
+
+- draft observations;
+- reopened observations;
+- archived observations;
+- raw import rows;
+- PDP evaluations;
+- unsupported objective measurements;
+- generated AI text.
+
+### Season And Cycle Scope
+
+Default summary scope should be one selected season and/or one selected evaluation cycle.
+
+Recommended initial behavior:
+
+- if a cycle is selected, summarize that cycle;
+- if a season is selected without a cycle, summarize submitted observations for that season;
+- if neither is selected, use the current active evaluation cycle when available;
+- show a clear empty state when no active/current context exists.
+
+Historical cross-season summary should be deferred until Phase 2 or later.
+
+### Perspective Separation
+
+Never blend evaluation perspectives into a single unlabeled average.
+
+Required perspective groups:
+
+- Self Evaluation;
+- Peer Evaluation;
+- Coach Evaluation;
+- Staff Evaluation;
+- Guest Evaluation.
+
+Each category summary should show count and average by perspective where values exist.
+
+### Category Summary
+
+For `rating_1_5` responses:
+
+- group by `ObservationQuestion.category`;
+- use `Questions` when category is blank;
+- calculate average rating per category and perspective;
+- show count beside every average;
+- do not calculate a category average when there are zero ratings.
+
+For text responses:
+
+- group by evaluation perspective and submitted evaluation;
+- preserve source wording;
+- do not auto-classify text into strengths or weaknesses in Phase 1.
+
+### Self-Versus-Coach Comparison
+
+Only show self-versus-coach comparisons when both perspectives have data in the same category.
+
+Use deterministic labels such as:
+
+- aligned;
+- self higher than coach;
+- coach higher than self;
+- insufficient data.
+
+Do not imply that either perspective is objectively correct.
+
+### Strengths And Opportunities
+
+Phase 1 may show deterministic "possible strengths" and "possible development opportunities" only if the rule is explicit and displayed or documented.
+
+Recommended initial rule:
+
+- possible strength: category average is at least 4.0 with at least the minimum approved response count;
+- possible development opportunity: category average is at most 2.5 with at least the minimum approved response count.
+
+If the approved minimum count is not available, show "insufficient data" instead of a conclusion.
+
+The exact threshold and minimum-count policy should be confirmed during Phase 1 engineering planning.
+
+### Evidence Links
+
+Every summary section should be traceable to source evaluations available to the viewer.
+
+Staff and coach links may point to coach/staff review details.
+
+Player links must use player-safe My Evaluations detail or another player-safe route that hides evaluator names.
+
+## 12. Privacy And Permission Boundaries
+
+### Player Access
+
+Players may view only summaries about player records actively self-linked to their account.
+
+Player-safe summaries must:
+
+- hide evaluator names;
+- hide usernames;
+- hide email addresses;
+- hide account metadata;
+- show evaluator role/category and evaluation perspective only;
+- link only to player-safe source evaluation pages.
+
+### Coach Access
+
+Coaches may view development summaries only under the same broad access assumptions currently used by coach review.
+
+Because strict team-scoped coach permissions are deferred, Phase 1 must explicitly avoid claiming team-only authorization unless that work is implemented first.
+
+### Staff/Admin Access
+
+Django staff and superusers may view staff-oriented development summaries.
+
+`AccountProfile.role = staff` remains metadata and must not grant Django staff access by itself.
+
+### Guest Evaluators
+
+Guest evaluators may submit evaluations under current V1 rules, but should not receive broad development-summary access in Phase 1.
+
+### Parent Access
+
+Parent access is deferred.
+
+Do not expose player-development summaries to parent/guardian accounts until a separate parent visibility plan is approved.
+
+## 13. AI Boundaries
+
+AI is not part of Player Development Summary V1.
+
+Future AI may be considered only after deterministic summaries are proven. Approved future AI use cases may include:
+
+- summarizing already-authorized evidence;
+- drafting coach discussion prompts;
+- simplifying language for players;
+- identifying themes for human review.
+
+Future AI must not:
+
+- invent observations;
+- rank players;
+- make team placement decisions;
+- diagnose injuries or psychology;
+- infer protected characteristics;
+- expose another player's data;
+- replace source evaluations;
+- become the authoritative record.
+
+Any future AI phase should require:
+
+- source citations;
+- human review;
+- model/version recording where appropriate;
+- permission-scoped input and output;
+- deletion/regeneration strategy;
+- privacy review before production.
+
+## 14. Pilot Strategy
+
+Before implementing or launching Player Development Summary V1 broadly, run a small pilot using completed V1 workflows.
+
+Recommended pilot scope:
+
+- one active season;
+- one or two teams;
+- one evaluation cycle;
+- a small group of coaches;
+- a small player group;
+- submitted coach evaluations;
+- submitted self evaluations;
+- optional submitted peer evaluations;
+- staff review before player access.
+
+Pilot steps:
+
+1. Confirm roster and coach assignments.
+2. Confirm evaluation questions and categories.
+3. Collect submitted evaluations.
+4. Review data completeness.
+5. Manually inspect how a development summary would read for sample players.
+6. Confirm privacy expectations with staff.
+7. Approve or revise Phase 1 aggregation rules.
+8. Begin Phase 1 engineering only after pilot concerns are resolved.
+
+## 15. Success Metrics
+
+Pilot and Phase 1 success should be measured by:
+
+- percentage of rostered players with enough submitted evaluations for a useful summary;
+- coach completion rate by cycle;
+- self-evaluation completion rate where applicable;
+- number of summaries with "insufficient data" warnings;
+- coach-reported usefulness;
+- player-reported clarity;
+- staff ability to verify each summary against source evaluations;
+- number of privacy/access defects;
+- number of support requests caused by confusing summary language;
+- repeat use by coaches after first review.
+
+## 16. Stop / Go Criteria
+
+### Go Criteria
+
+Proceed to Player Development Summary V1 implementation when:
+
+- current V1 workflows work in pilot usage;
+- submitted evaluation volume is sufficient for sample summaries;
+- question categories are usable;
+- summary permissions are approved;
+- player-safe visibility is approved;
+- staff can verify summary evidence;
+- the first implementation can be built without new persisted summary models.
+
+### Stop Criteria
+
+Stop or revise the plan if:
+
+- pilot users cannot complete V1 evaluation workflows;
+- data coverage is too low for useful summaries;
+- users expect rankings or selection recommendations;
+- privacy rules are unresolved;
+- parent access is required before internal/player-safe summaries are proven;
+- deterministic summaries would mislead users;
+- implementation requires depending on PDP models;
+- implementation requires a new persisted summary schema before product value is proven.
+
+## 17. Future Implementation Phases
+
+### Phase 1: Player Development Summary V1
+
+Build deterministic, source-grounded player-development summary read models and server-rendered views.
+
+### Phase 2: Development Priorities And Plans
+
+Add coach/staff-authored development priorities or action plans only after summary content is validated.
+
+### Phase 3: Longitudinal Progress
+
+Show cycle-to-cycle or season-to-season progress once multiple real cycles exist and question-category stability is understood.
+
+### Phase 4: Reports And Sharing
+
+Add printable or shareable reports after approval, visibility, and source-traceability rules are defined.
+
+### Phase 5: Optional AI Assistance
+
+Add AI only as a source-grounded assistant after deterministic summaries and privacy rules are proven.
+
+### Phase 6: Expanded Access
+
+Consider parent access, additional coach scoping, or broader portal integration only after staff/player use is stable.
+
+## 18. Risk Register
+
+| Risk | Likelihood | Impact | Mitigation |
+| --- | --- | --- | --- |
+| Low evaluation volume makes summaries weak | Medium | High | Show insufficient-data states; pilot before launch |
+| Question categories are inconsistent | Medium | Medium | Review category taxonomy before Phase 1 |
+| Averages are interpreted as rankings | Medium | High | Avoid ranking language; show counts and perspective labels |
+| Self and coach perspectives conflict | High | Medium | Frame as discussion context, not correctness judgment |
+| Player sees private evaluator identity | Low | High | Reuse player-safe access rules and routes; test visibility |
+| Coach sees too much before team scoping exists | Medium | High | Document current broad review scope; defer strict scoping or implement it first |
+| PDP model overlap creates confusion | Medium | Medium | Do not depend on PDP; document migration as separate |
+| AI pressure causes premature implementation | Medium | High | Keep Phase 1 deterministic; require separate AI plan |
+| Summary text sounds more certain than data supports | Medium | High | Use explicit thresholds and insufficient-data warnings |
+| Performance issues on large rosters | Low | Medium | Use bounded queries, select/prefetch, and service-level tests |
+| Parent access is requested early | Medium | High | Treat as separate visibility and approval phase |
+
+## 19. Implementation Acceptance Criteria For Phase 1 Planning
+
+Before writing Player Development Summary V1 code, the Phase 1 engineering plan should define:
+
+- exact URL names and paths;
+- exact permission matrix;
+- exact read models/dataclasses;
+- exact source query strategy;
+- season/cycle selection behavior;
+- category and perspective aggregation rules;
+- minimum-data thresholds;
+- player-safe text/evidence visibility;
+- staff/coach evidence-link behavior;
+- empty states;
+- tests for service, view, permission, privacy, and regression coverage;
+- confirmation that no migrations are needed.
+
+## 20. Open Questions
+
+These do not block Phase 0 completion, but should be resolved during Phase 1 engineering planning or pilot review:
+
+- What minimum response count should be required before showing a strength or opportunity label?
+- Should Phase 1 expose peer-evaluation text to players, or only ratings and role labels?
+- Should coach access remain as broad as current coach review for Phase 1, or should strict team scoping be implemented first?
+- Should Player Development Summary V1 live only under `/development/`, or should Analytics player profile pages link prominently to it?
+- Which staff role owns final approval of player-facing summary wording?
+
+## 21. Phase 0 Decision
+
+Phase 0 is complete.
+
+The repository is ready for a separate Player Development Summary V1 engineering plan.
+
+Terminal state:
+
+```text
+PASS
+```
````

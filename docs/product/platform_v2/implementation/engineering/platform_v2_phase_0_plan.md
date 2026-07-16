# Platform V2 Phase 0 Plan: Player Development Intelligence

Status:

```text
Phase 0 complete.
Ready for Player Development Summary V1 engineering planning.
No Platform V2 application code has been implemented.
```

Date: 2026-07-16

## 1. Executive Summary

Platform V1 is complete enough to begin planning Platform V2. The repository now has permanent player identity, account identity, user-player links, seasons, roster memberships, coach assignments, season-aware imports, submitted evaluation snapshots, player self-evaluation, peer evaluation, coach evaluation, staff and coach review, player My Evaluations, command-center summaries, player timelines, player comparison, and stable service boundaries.

Platform V2 should be built around Player Development Intelligence:

> Help players, coaches, and staff understand development over time and turn evaluations into clear, evidence-based next steps.

The recommended first implementation phase is:

```text
Player Development Summary V1
```

This should be a deterministic, privacy-aware, source-grounded summary of existing submitted evaluation data. It should not require AI, new evaluation workflows, parent access, rankings, charts, exports, or persisted summary tables.

## 2. Repository-Grounded Baseline

The current codebase provides these foundations for Platform V2:

| Area | Current Owner | Relevant Current Data / Service |
| --- | --- | --- |
| Player identity | `players` | `players.Player`, aliases, source identifiers, source rows, tags |
| Account identity | `accounts` | Django `User`, `AccountProfile`, `UserPlayerLink`, account roles |
| Season context | `seasons` | `Season`, `SeasonTeam`, `PlayerRosterMembership`, `CoachSeasonAssignment` |
| Evaluations | `analytics` | `EvaluationCycle`, `Observation`, `ObservationResponse`, `ObservationQuestion`, question categories |
| Historical snapshots | `analytics` | submitted season/team/division/evaluator snapshots on `Observation` |
| Perspective labels | `analytics` | self, peer, coach, staff, guest evaluation perspectives |
| Player-facing access | `analytics` + `accounts` | My Evaluations access via active self player links |
| Coach/staff review | `analytics` | submitted evaluation review and filtering |
| Existing read models | `analytics` | player search, timeline, comparison, metrics, reporting, draft context services |
| Legacy development app | `pdp` | legacy `PlayerProfile`, PDP-specific evaluations, logs, goals, AI scaffolding |

The final cleanup audit concluded:

```text
READY FOR PLATFORM V2 PLANNING
```

No critical or high architecture, security, transaction, or performance blocker was identified before starting this planning phase.

## 3. Product Vision

Platform V2 should turn evaluation and roster history into development decision support.

It should help answer:

- What are this player's current strengths?
- What should this player work on next?
- How do self, peer, coach, staff, and guest perspectives compare?
- Is there enough evaluation coverage to trust the summary?
- What changed across cycles or seasons?
- Which evidence supports each summary statement?
- What is safe and appropriate to show to players?

Platform V2 is not:

- registration software;
- team scheduling software;
- general stat tracking;
- recruiting software;
- automated coaching;
- generic AI chat;
- injury, medical, or psychological diagnosis;
- an automated player ranking or selection system.

Final baseball decisions remain with coaches, coordinators, staff, administrators, players, and families. Software should organize evidence and context, not replace human judgment.

## 4. Primary Users

### Players

Players need feedback that is understandable, constructive, privacy-safe, and tied to their own development.

Important needs:

- understand strengths;
- understand development priorities;
- distinguish self-evaluation from external evaluation;
- compare self-perception with coach feedback without exposing private evaluator identities;
- see progress over time;
- know what to discuss with coaches next.

### Coaches

Coaches need a concise way to understand a player before planning feedback or development work.

Important needs:

- see recent submitted evaluations without reading every raw response first;
- identify recurring strengths and opportunities;
- distinguish perspective differences;
- understand season/team context;
- link back to source evaluations when details matter.

### Staff And Administrators

Staff need oversight, consistency, and privacy control.

Important needs:

- monitor data completeness;
- verify summaries against source data;
- preserve historical context;
- review pilot quality before expanding access;
- avoid accidental exposure of private youth data.

### Parents

Parent access is deferred.

Parents may eventually receive approved player-development summaries, but Platform V2 Phase 1 should not expose raw evaluations or evaluator identities to parents. Parent access needs a separate visibility and approval plan.

## 5. Product Principles

- Development over ranking.
- Evidence over unsupported inference.
- Historical context over mutable current fields.
- Explainability over opaque scoring.
- Human review over autonomous decisions.
- Minimal data exposure.
- Role-appropriate access.
- Deterministic summaries before generative AI.
- Reversible product decisions.
- No fabricated facts.
- No medical, injury, or psychological diagnosis.
- No automated roster, draft, placement, scholarship, or selection decisions.
- No single overall player score unless explicitly approved in a future phase.

## 6. Data Foundation Assessment

### Already Sufficient

The repository already has enough structure for a first deterministic summary:

- canonical player records;
- active/inactive player state;
- active account/player self links;
- seasons and current-season state;
- season teams and roster memberships;
- coach season assignments;
- evaluation cycles;
- submitted observations;
- question categories;
- rating responses;
- text responses;
- evaluator role snapshots;
- evaluation perspective snapshots;
- submitted-at timestamps;
- submitted season/team/division snapshots.

### Missing Or Not Yet Mature

These are not blockers for Phase 1, but should be visible risks:

- real production evaluation volume may be low;
- question categories may need validation after pilot usage;
- stricter team-scoped coach permissions are deferred;
- parent visibility rules are not defined;
- report approval/publishing rules are not defined;
- no audit system exists yet for generated summaries or report sharing;
- PDP migration or retirement is not planned in detail.

### Should Remain Computed Initially

These should be computed from source data in Player Development Summary V1:

- category averages;
- perspective-specific averages;
- evaluation counts;
- data-completeness warnings;
- self-versus-coach differences;
- latest evaluation lists;
- source evidence links;
- summary section visibility.

Computed read models preserve source authority and avoid storing derived conclusions before the product has been validated.

### Should Not Be Duplicated

Platform V2 should not duplicate:

- canonical player identity;
- account roles or links;
- season/team/roster membership state;
- submitted evaluation responses;
- evaluator identity snapshots;
- PDP `PlayerProfile` identity.

## 7. PDP Relationship

Decision:

```text
PDP remains legacy/transitionary. Platform V2 should not depend on PDP models.
```

Rationale:

- `players.Player` is now the canonical future player identity model.
- `accounts` owns platform login identity and user-player links.
- `seasons` owns roster participation.
- `analytics` owns submitted evaluations and evaluator snapshots.
- PDP has overlapping historical models and AI/development scaffolding, but those are not the current platform-forward data sources.

Phase 1 should build from `players`, `accounts`, `seasons`, and `analytics`.

PDP migration, consolidation, or retirement requires a separate plan. Phase 0 does not delete, migrate, or bypass current PDP behavior.

## 8. Bounded Context Recommendation

Recommendation:

```text
Create a future Django app named development for Platform V2 implementation.
```

Do not create the app in Phase 0.

### Why Not Put Everything In Analytics?

Analytics already owns observations, metrics, comparisons, timelines, command-center summaries, and review surfaces. Player Development Intelligence will likely grow toward development summaries, goals, plans, progress narratives, report approval, and eventually parent-visible outputs. Keeping that product area inside Analytics would make Analytics too broad.

### Why A New Development App?

A `development` app gives Platform V2 a clear bounded context:

- owns player-development summary read models;
- owns future development-plan workflows if approved;
- owns future development-summary pages and reports;
- consumes Analytics evidence instead of owning raw evaluations;
- avoids depending on PDP legacy models;
- keeps new V2 product language separate from V1 operational analytics.

### Ownership Boundaries

Future `development` app should own:

- player-development summary services;
- summary read models/dataclasses;
- development-summary views/templates;
- future development-plan and progress workflows only when explicitly approved;
- development-specific permission composition that delegates to owning services.

Future `development` app must not own:

- canonical player identity;
- account identity or account roles;
- user-player links;
- player imports;
- coach imports;
- season teams or roster memberships;
- raw evaluation submission;
- observation responses;
- draft workflows;
- PDP migration behavior.

### Dependency Direction

Allowed dependencies:

```text
development -> players
development -> accounts
development -> seasons
development -> analytics
```

Expected service usage:

- consume player lookup through `players` or existing Analytics player services;
- consume self-link and role information through `accounts` services;
- consume roster context through `seasons` services/models;
- consume submitted evaluation evidence through `analytics` services/read models.

Forbidden dependencies:

- `development` must not import from `pdp`;
- `analytics` should not import from `development` for core V1 evaluation behavior;
- templates must not implement summary calculations;
- views must not duplicate Analytics query logic.

## 9. First Implementation Phase

Recommended first implementation:

```text
Player Development Summary V1
```

### Goal

Provide a concise, privacy-aware player-development summary using existing submitted evaluations and season context.

### Target Users

Initial target users:

- staff;
- coaches;
- players for their own linked player record, using player-safe visibility.

Deferred users:

- parents;
- unauthenticated users;
- guest evaluators for broad summary access.

### Strict Scope

Player Development Summary V1 should include:

- player identity header;
- selected season/evaluation-cycle context;
- evaluation coverage;
- latest submitted evaluations;
- perspective-specific category summaries;
- self-versus-coach comparison when both exist;
- role-labeled perspective summaries;
- recent text feedback where visible;
- data-completeness warnings;
- evidence links back to authorized source evaluations;
- empty states when data is insufficient.

### Out Of Scope

Do not include:

- AI-generated summaries;
- charts or dashboards;
- exports or PDFs;
- parent access;
- published reports;
- persistent development-plan models;
- timeline database models;
- rankings;
- overall player score;
- predictive claims;
- medical/injury guidance;
- new evaluation submission workflow;
- new account or roster management workflow;
- PDP migration.

## 10. Proposed Phase 1 Technical Shape

Phase 1 should be planned separately before implementation. The expected shape is:

### App

Create `development` only when Phase 1 implementation is approved.

### Services

Likely services:

- `development/services/summary_service.py`
- `development/services/permission_service.py`

The summary service should assemble read models only. It should call existing Analytics services where practical and add perspective-aware logic where current V1 services are too broad.

### Read Models

Likely dataclasses:

- `PlayerDevelopmentSummary`
- `DevelopmentSummaryContext`
- `EvaluationCoverage`
- `PerspectiveSummary`
- `CategoryDevelopmentSummary`
- `PerspectiveComparison`
- `EvidenceLink`
- `DevelopmentSummaryWarning`

These should be plain dataclasses/read models, not database models.

### Views

Likely server-rendered views:

- staff/coach player summary detail;
- player-safe own summary detail.

Views should be thin:

- resolve request parameters;
- call permission service;
- call summary service;
- render template.

### URLs

Candidate routes:

```text
/development/players/<player_id>/summary/
/development/my/summary/
```

Potential integration links:

- staff player profile can link to development summary;
- coach review rows can link to development summary;
- player account/profile area can link to own summary.

Do not add these routes until Phase 1 implementation is approved.

### Templates

Templates should render supplied read models only. They should not compute averages, compare perspectives, enforce permissions, or filter source data.

### Migrations

No migrations are expected for Player Development Summary V1.

If implementation appears to require persistence, stop and document why. Persisted summaries, publication state, report approvals, and caching should be separate future phases.

## 11. Deterministic Summary Rules

### Source Data

Use only:

- submitted `analytics.Observation` records;
- `coach_assessment` observation type;
- active/relevant evaluation cycles;
- rating responses;
- text responses;
- question categories;
- submitted season/team/division snapshots;
- evaluator role and perspective snapshots.

Exclude:

- draft observations;
- reopened observations;
- archived observations;
- raw import rows;
- PDP evaluations;
- unsupported objective measurements;
- generated AI text.

### Season And Cycle Scope

Default summary scope should be one selected season and/or one selected evaluation cycle.

Recommended initial behavior:

- if a cycle is selected, summarize that cycle;
- if a season is selected without a cycle, summarize submitted observations for that season;
- if neither is selected, use the current active evaluation cycle when available;
- show a clear empty state when no active/current context exists.

Historical cross-season summary should be deferred until Phase 2 or later.

### Perspective Separation

Never blend evaluation perspectives into a single unlabeled average.

Required perspective groups:

- Self Evaluation;
- Peer Evaluation;
- Coach Evaluation;
- Staff Evaluation;
- Guest Evaluation.

Each category summary should show count and average by perspective where values exist.

### Category Summary

For `rating_1_5` responses:

- group by `ObservationQuestion.category`;
- use `Questions` when category is blank;
- calculate average rating per category and perspective;
- show count beside every average;
- do not calculate a category average when there are zero ratings.

For text responses:

- group by evaluation perspective and submitted evaluation;
- preserve source wording;
- do not auto-classify text into strengths or weaknesses in Phase 1.

### Self-Versus-Coach Comparison

Only show self-versus-coach comparisons when both perspectives have data in the same category.

Use deterministic labels such as:

- aligned;
- self higher than coach;
- coach higher than self;
- insufficient data.

Do not imply that either perspective is objectively correct.

### Strengths And Opportunities

Phase 1 may show deterministic "possible strengths" and "possible development opportunities" only if the rule is explicit and displayed or documented.

Recommended initial rule:

- possible strength: category average is at least 4.0 with at least the minimum approved response count;
- possible development opportunity: category average is at most 2.5 with at least the minimum approved response count.

If the approved minimum count is not available, show "insufficient data" instead of a conclusion.

The exact threshold and minimum-count policy should be confirmed during Phase 1 engineering planning.

### Evidence Links

Every summary section should be traceable to source evaluations available to the viewer.

Staff and coach links may point to coach/staff review details.

Player links must use player-safe My Evaluations detail or another player-safe route that hides evaluator names.

## 12. Privacy And Permission Boundaries

### Player Access

Players may view only summaries about player records actively self-linked to their account.

Player-safe summaries must:

- hide evaluator names;
- hide usernames;
- hide email addresses;
- hide account metadata;
- show evaluator role/category and evaluation perspective only;
- link only to player-safe source evaluation pages.

### Coach Access

Coaches may view development summaries only under the same broad access assumptions currently used by coach review.

Because strict team-scoped coach permissions are deferred, Phase 1 must explicitly avoid claiming team-only authorization unless that work is implemented first.

### Staff/Admin Access

Django staff and superusers may view staff-oriented development summaries.

`AccountProfile.role = staff` remains metadata and must not grant Django staff access by itself.

### Guest Evaluators

Guest evaluators may submit evaluations under current V1 rules, but should not receive broad development-summary access in Phase 1.

### Parent Access

Parent access is deferred.

Do not expose player-development summaries to parent/guardian accounts until a separate parent visibility plan is approved.

## 13. AI Boundaries

AI is not part of Player Development Summary V1.

Future AI may be considered only after deterministic summaries are proven. Approved future AI use cases may include:

- summarizing already-authorized evidence;
- drafting coach discussion prompts;
- simplifying language for players;
- identifying themes for human review.

Future AI must not:

- invent observations;
- rank players;
- make team placement decisions;
- diagnose injuries or psychology;
- infer protected characteristics;
- expose another player's data;
- replace source evaluations;
- become the authoritative record.

Any future AI phase should require:

- source citations;
- human review;
- model/version recording where appropriate;
- permission-scoped input and output;
- deletion/regeneration strategy;
- privacy review before production.

## 14. Pilot Strategy

Before implementing or launching Player Development Summary V1 broadly, run a small pilot using completed V1 workflows.

Recommended pilot scope:

- one active season;
- one or two teams;
- one evaluation cycle;
- a small group of coaches;
- a small player group;
- submitted coach evaluations;
- submitted self evaluations;
- optional submitted peer evaluations;
- staff review before player access.

Pilot steps:

1. Confirm roster and coach assignments.
2. Confirm evaluation questions and categories.
3. Collect submitted evaluations.
4. Review data completeness.
5. Manually inspect how a development summary would read for sample players.
6. Confirm privacy expectations with staff.
7. Approve or revise Phase 1 aggregation rules.
8. Begin Phase 1 engineering only after pilot concerns are resolved.

## 15. Success Metrics

Pilot and Phase 1 success should be measured by:

- percentage of rostered players with enough submitted evaluations for a useful summary;
- coach completion rate by cycle;
- self-evaluation completion rate where applicable;
- number of summaries with "insufficient data" warnings;
- coach-reported usefulness;
- player-reported clarity;
- staff ability to verify each summary against source evaluations;
- number of privacy/access defects;
- number of support requests caused by confusing summary language;
- repeat use by coaches after first review.

## 16. Stop / Go Criteria

### Go Criteria

Proceed to Player Development Summary V1 implementation when:

- current V1 workflows work in pilot usage;
- submitted evaluation volume is sufficient for sample summaries;
- question categories are usable;
- summary permissions are approved;
- player-safe visibility is approved;
- staff can verify summary evidence;
- the first implementation can be built without new persisted summary models.

### Stop Criteria

Stop or revise the plan if:

- pilot users cannot complete V1 evaluation workflows;
- data coverage is too low for useful summaries;
- users expect rankings or selection recommendations;
- privacy rules are unresolved;
- parent access is required before internal/player-safe summaries are proven;
- deterministic summaries would mislead users;
- implementation requires depending on PDP models;
- implementation requires a new persisted summary schema before product value is proven.

## 17. Future Implementation Phases

### Phase 1: Player Development Summary V1

Build deterministic, source-grounded player-development summary read models and server-rendered views.

### Phase 2: Development Priorities And Plans

Add coach/staff-authored development priorities or action plans only after summary content is validated.

### Phase 3: Longitudinal Progress

Show cycle-to-cycle or season-to-season progress once multiple real cycles exist and question-category stability is understood.

### Phase 4: Reports And Sharing

Add printable or shareable reports after approval, visibility, and source-traceability rules are defined.

### Phase 5: Optional AI Assistance

Add AI only as a source-grounded assistant after deterministic summaries and privacy rules are proven.

### Phase 6: Expanded Access

Consider parent access, additional coach scoping, or broader portal integration only after staff/player use is stable.

## 18. Risk Register

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Low evaluation volume makes summaries weak | Medium | High | Show insufficient-data states; pilot before launch |
| Question categories are inconsistent | Medium | Medium | Review category taxonomy before Phase 1 |
| Averages are interpreted as rankings | Medium | High | Avoid ranking language; show counts and perspective labels |
| Self and coach perspectives conflict | High | Medium | Frame as discussion context, not correctness judgment |
| Player sees private evaluator identity | Low | High | Reuse player-safe access rules and routes; test visibility |
| Coach sees too much before team scoping exists | Medium | High | Document current broad review scope; defer strict scoping or implement it first |
| PDP model overlap creates confusion | Medium | Medium | Do not depend on PDP; document migration as separate |
| AI pressure causes premature implementation | Medium | High | Keep Phase 1 deterministic; require separate AI plan |
| Summary text sounds more certain than data supports | Medium | High | Use explicit thresholds and insufficient-data warnings |
| Performance issues on large rosters | Low | Medium | Use bounded queries, select/prefetch, and service-level tests |
| Parent access is requested early | Medium | High | Treat as separate visibility and approval phase |

## 19. Implementation Acceptance Criteria For Phase 1 Planning

Before writing Player Development Summary V1 code, the Phase 1 engineering plan should define:

- exact URL names and paths;
- exact permission matrix;
- exact read models/dataclasses;
- exact source query strategy;
- season/cycle selection behavior;
- category and perspective aggregation rules;
- minimum-data thresholds;
- player-safe text/evidence visibility;
- staff/coach evidence-link behavior;
- empty states;
- tests for service, view, permission, privacy, and regression coverage;
- confirmation that no migrations are needed.

## 20. Open Questions

These do not block Phase 0 completion, but should be resolved during Phase 1 engineering planning or pilot review:

- What minimum response count should be required before showing a strength or opportunity label?
- Should Phase 1 expose peer-evaluation text to players, or only ratings and role labels?
- Should coach access remain as broad as current coach review for Phase 1, or should strict team scoping be implemented first?
- Should Player Development Summary V1 live only under `/development/`, or should Analytics player profile pages link prominently to it?
- Which staff role owns final approval of player-facing summary wording?

## 21. Phase 0 Decision

Phase 0 is complete.

The repository is ready for a separate Player Development Summary V1 engineering plan.

Terminal state:

```text
PASS
```

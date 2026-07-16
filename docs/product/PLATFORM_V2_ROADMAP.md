# Platform V2 Roadmap: Player Development Intelligence

## 1. Executive Summary

Platform V1 is the stable operational foundation for the VCB Platform. It supports player identity, imports, account management, authentication, user-player links, coach import, season-aware roster participation, evaluations, player My Evaluations, coach review, staff review, Analytics Command Center, player search/profile/timeline/comparison, draft context, draft workflows, deployment documentation, and role-based user documentation.

The recommended next product milestone is:

```text
Platform V2: Player Development Intelligence
```

Phase 0 product and implementation planning is recorded in [Platform V2 Product Planning](platform_v2/README.md). That plan recommends Player Development Summary V1 as the first implementation phase, using deterministic computed read models before AI, reports, parent access, or persisted development-plan workflows.

Seasonal Participation V1 is complete and frozen. It allows permanent players and coach accounts to be reused across seasons while evaluations retain historical team/division context. See [Seasonal Participation V1](../seasons/README.md).

Platform V2 should turn collected evaluation data into useful player-development decision support. It should not begin with large dashboards, AI, rankings, or parent-facing raw data. The next immediate activity should be a real-world pilot using the completed Platform V1 workflows. Product decisions for Platform V2 should be driven by pilot evidence, data quality, privacy requirements, and user value.

Recommended first implementation phase after pilot validation:

```text
Player Development Summary V1
```

This first phase should use existing Platform V1 evaluation data to show a simple, privacy-aware summary of a player's latest development information, separated by evaluation perspective.

## 2. Platform V1 Foundation

Platform V1 currently includes:

- canonical player identity and player records;
- player CSV import and player account provisioning;
- coach account import;
- season-aware teams, player roster memberships, coach assignments, and evaluation context;
- account management and Account Operations;
- user-player relationships;
- authentication and forced password change;
- coach, peer, self, staff, and guest evaluations;
- evaluation cycles;
- player My Evaluations;
- coach review and filtering;
- staff review and reopen;
- Analytics Command Center;
- player search, profiles, timelines, and comparison;
- draft context and draft workflows;
- production deployment documentation;
- role-based user documentation.

Platform V1 should be treated as stable. Platform V2 should build on V1 data and service boundaries rather than replacing them.

Current subsystem ownership remains:

- `accounts` owns authentication, account metadata, roles, links, provisioning, and account operations.
- `players` owns canonical player identity, player imports, matching, and player provenance.
- `seasons` owns season-aware teams, player roster memberships, coach assignments, and roster context.
- `analytics` owns observations, evaluation cycles, responses, evaluator snapshots, perspective snapshots, metrics, timelines, comparisons, command center summaries, and reporting surfaces.
- `drafts` owns draft workflows and draft actions.
- `pdp` remains legacy/transitionary.

## 3. Product Vision

Platform V2 should help VCB make better player-development decisions by organizing evaluation history, perspective differences, notes, and progress over time.

The platform should support people, not replace them. Coaches, coordinators, evaluators, staff, and administrators remain responsible for final baseball decisions.

Platform V2 should help answer questions such as:

- What are this player's current strengths?
- What should this player work on next?
- How has this player changed across cycles?
- Do self evaluations align with external evaluations?
- Are coaches seeing the same development needs?
- Is there enough evaluation coverage to trust the summary?
- What information is appropriate to share with players or parents?

## 4. User Problems To Solve

### Administrators And Coordinators

- Need reliable visibility into evaluation coverage and data completeness.
- Need confidence that privacy rules are enforced.
- Need operational workflows before adding more reporting complexity.

### Staff

- Need a concise view of player development history.
- Need to distinguish coach, peer, self, staff, and guest perspectives.
- Need to avoid misleading conclusions from incomplete data.

### Coaches

- Need a practical way to review players without reading every raw evaluation first.
- Need to identify players who need follow-up or additional feedback.
- Need to see incomplete evaluation work by team, division, cycle, and perspective.

### Players

- Need feedback that is understandable, constructive, and privacy-safe.
- Need to distinguish their own self evaluation from external feedback.
- Need development areas without exposing sensitive evaluator identities.

### Parents

- May eventually need approved development summaries.
- Should not automatically receive raw evaluations, evaluator identities, or private peer comments.

## 5. Recommended Product Areas

### 5.1 Player Development Dashboard

Future purpose:

- Summarize a player's current strengths, development areas, recent evaluations, notes, and progress.

Potential users:

- staff, coaches, players, and eventually parents with approved visibility.

Possible future visualizations:

- trend charts;
- rating summaries;
- radar charts;
- heat maps;
- progress indicators.

Smallest useful first version:

- latest submitted evaluations;
- perspective labels;
- category-level rating summaries;
- cycle selector;
- self versus external separation;
- recent notes;
- clear data completeness warning when evaluation volume is low.

Do not include in the first version:

- AI summaries;
- automated rankings;
- parent access;
- complex charts;
- predictive conclusions.

### 5.2 Historical Progress

Future purpose:

- Show how evaluation results change across cycles such as Spring 2026, Summer 2026, Fall 2026, and Winter 2027.

Possible capabilities:

- rating changes over time;
- skill-category trends;
- improvement and decline indicators;
- cycle-to-cycle comparison;
- historical notes;
- development milestones.

Important principle:

- Historical snapshots must be preserved. Later account-role changes, player-team changes, evaluator changes, or question changes should not rewrite the meaning of submitted evaluations.

Smallest useful version:

- cycle-by-cycle category summary table;
- submitted evaluation counts by cycle and perspective;
- notes grouped by cycle.

### 5.3 Multi-Evaluator Consensus

Future purpose:

- Compare perspectives without mixing them invisibly.

Perspectives currently available:

- Self Evaluation;
- Peer Evaluation;
- Coach Evaluation;
- Staff Evaluation;
- Guest Evaluation.

Potential insights:

- agreement between perspectives;
- disagreement between perspectives;
- self-perception gaps;
- consistency among coaches;
- areas with high uncertainty;
- areas where more evaluation data is needed.

Aggregation guardrails:

- Do not mix perspectives into a single average without clear labels.
- Do not present small-sample averages as objective truth.
- Show counts and data completeness beside summaries.
- Keep raw source evaluations available to authorized reviewers.
- Treat self-evaluation bias and coach bias as expected context, not errors.

No scoring formula should be implemented until aggregation rules are explicitly defined and validated with real pilot data.

### 5.4 AI-Assisted Insights

Possible future capabilities:

- summarize multiple evaluations;
- identify recurring strengths;
- identify repeated development concerns;
- detect trends across cycles;
- draft player-development summaries;
- highlight differences between self and external evaluations;
- produce coach-review preparation notes.

AI guardrails:

- AI output is advisory only.
- AI must not make selection, roster, discipline, scholarship, eligibility, or placement decisions.
- Source evaluations must remain visible to authorized users.
- Users must be able to verify summaries against source data.
- Youth player data requires explicit privacy and consent review.
- AI output must not invent facts.
- Prompts and outputs may require auditability before production use.
- AI summaries should distinguish observed facts from generated interpretation.

AI should not be the first Platform V2 implementation phase. The platform first needs pilot data, aggregation rules, visibility rules, and a simple non-AI development summary.

### 5.5 Parent Portal

Possible future purpose:

- Provide parents with approved player-development information.

Potential future content:

- approved player-development summaries;
- selected evaluations;
- strengths;
- development areas;
- coach comments;
- progress over time;
- account and linked-player information.

Parent portal guardrails:

- Parents should not automatically receive all raw evaluations.
- Peer comments, evaluator identities, and sensitive notes require explicit visibility decisions.
- Staff or coach approval may be required before sharing summaries.
- Parent access should be built only after player-facing and staff-facing summary rules are proven.

### 5.6 Coach Dashboard

Future purpose:

- Help coaches manage evaluation work and review team development patterns.

Possible content:

- players needing evaluation;
- incomplete evaluations;
- recently submitted evaluations;
- team-level strengths and development areas;
- players improving fastest;
- evaluation coverage;
- self-versus-coach perception gaps;
- filters by team, division, cycle, and perspective.

Practical first version:

- evaluation coverage by team/cycle;
- incomplete evaluation list;
- recent submitted evaluations;
- links to player development summaries.

Avoid in the first version:

- automated player rankings;
- complex charts without validated data;
- conclusions based on incomplete evaluation coverage.

### 5.7 Reports And PDF Export

Possible report types:

- player development report;
- end-of-cycle review;
- parent communication;
- coach meeting packet;
- recruiting support;
- internal staff review.

Report rules:

- clearly identify evaluation perspectives;
- preserve privacy and visibility rules;
- avoid exposing hidden evaluator identity;
- state evaluation cycle and date;
- distinguish factual data from generated summaries;
- avoid presenting rankings as objective truth;
- show data completeness and sample size where appropriate.

First reporting candidate:

- printable player-development summary for staff/coach use, without parent visibility by default.

### 5.8 Notifications And Workflow Reminders

Possible notifications:

- account invitation;
- password reset;
- evaluation cycle opening;
- evaluation due date;
- incomplete evaluation;
- reopened evaluation;
- new approved player feedback;
- cycle closing reminder.

Priority order:

1. Essential account email workflows such as invitations and password recovery.
2. Operational reminders for staff/coaches.
3. User-facing notifications for players/parents.

Broad notification automation should wait until email deliverability, consent, unsubscribe/communication preferences, and operational ownership are defined.

### 5.9 Audit And Operational History

Future auditable events:

- account changes;
- password resets;
- imports;
- evaluation submission;
- evaluation reopen;
- bulk account actions;
- permission changes;
- report generation;
- AI summary generation.

Why audit matters:

- protects youth data;
- supports operational accountability;
- helps investigate accidental access or incorrect changes;
- gives staff confidence before expanding parent and AI features;
- records how sensitive summaries or reports were produced.

Audit logging is not required before the first Player Development Summary V1 if the view only reads existing data. It becomes more important before parent sharing, report export, AI summaries, bulk updates, and sensitive workflow automation.

## 6. Product-Area Boundaries

Product areas describe user-facing responsibility. They do not automatically imply Django app boundaries.

```text
Platform
├── Identity
├── Players
├── Evaluations
├── Analytics
├── Development
├── Reporting
├── Recruiting
├── Communications
└── Administration
```

| Product Area | Responsibility | Platform V1 Coverage | Likely Platform V2 Scope | Dependencies | Non-Goals |
| --- | --- | --- | --- | --- | --- |
| Identity | Login, account metadata, roles, user-player links | Account Management V1 and Account Operations complete | Email invitations, password recovery, communication preferences | `accounts`, deployment email config | Custom auth model, SSO by default |
| Players | Canonical player identity and provenance | Player records, imports, matching, tags | Better roster context, development summary entry points | `players`, account links | Player identity inside Analytics |
| Evaluations | Evaluation submission and review workflows | Coach, peer, self, staff, guest submissions; cycles; My Evaluations; coach/staff review | Question quality review, completion workflows, perspective-aware summaries | `analytics`, `accounts`, `players` | Automated selection decisions |
| Analytics | Decision-support read models and summaries | Command Center, metrics, timelines, comparisons, draft context | Player Development Summary, trends, consensus summaries | evaluation data volume, privacy rules | Ranking players as objective truth |
| Development | Player growth tracking and feedback | Limited to evaluation results and timeline context | strengths, development areas, cycle progress, milestones | Analytics summaries, approved visibility | Medical, injury, or discipline conclusions |
| Reporting | Printable/shareable outputs | Command Center tables and read-only review pages | PDF reports, end-of-cycle summaries, parent-approved reports | privacy rules, report templates | Unrestricted raw data export |
| Recruiting | Recruiting history and support | Not implemented as a V1 workflow | Future recruiting reports and history | player identity, reports, visibility decisions | Verified recruiting claims without evidence |
| Communications | Account and workflow communication | Manual account/password workflows | invitations, password recovery, reminders | email infrastructure, consent rules | Broad notification automation first |
| Administration | Operational oversight and safety | Account Operations, staff review, imports | audit history, operational quality checks | logging strategy, staff permissions | Hidden administrative side effects |

Technical implementation should continue to follow the existing architecture. For example, a future Development product area may still be implemented inside `analytics` services and templates if it is primarily a read model over observations.

## 7. Pilot-First Strategy

The next immediate activity should be real-world pilot usage, not a large new feature build.

Recommended pilot:

1. Import a representative player roster.
2. Import real coach accounts.
3. Run one evaluation cycle.
4. Collect coach evaluations.
5. Collect player peer evaluations.
6. Collect player self evaluations.
7. Test player My Evaluations.
8. Test coach review.
9. Record workflow friction.
10. Track defects separately from feature requests.
11. Review findings before approving large Platform V2 work.

### Pilot Feedback Framework

Use a simple spreadsheet or document first. Do not implement a feedback system yet.

Recommended fields:

- task;
- role;
- expected result;
- actual result;
- confusion;
- number of clicks;
- missing information;
- severity;
- suggested improvement;
- defect or feature request;
- follow-up owner.

### Pilot Review Questions

- Did users understand where to start?
- Did coaches complete evaluations without staff assistance?
- Did players understand self versus peer evaluations?
- Did My Evaluations show enough useful information?
- Did coach review filters support real review work?
- Were evaluation questions clear and useful?
- Was evaluation coverage high enough to support summaries?
- Were privacy expectations clear?
- Which requests were defects, and which were new features?

## 8. Recommended Phases

### Phase 0: Product And Data Readiness

Purpose:

- Confirm the platform has enough real usage and clean data for development intelligence.

Scope:

- confirm real pilot workflows;
- collect user feedback;
- confirm evaluation question quality;
- validate cycle usage;
- confirm sufficient evaluation volume;
- define privacy and visibility rules;
- define aggregation rules;
- define terminology;
- establish success metrics.

Deliverables:

- pilot findings;
- approved terminology;
- aggregation rules;
- visibility matrix;
- first-phase implementation plan.

Stop/go criteria:

- Go if pilot users complete workflows and evaluation data is sufficient for a simple summary.
- Stop if users cannot complete V1 workflows, data coverage is too low, or privacy rules are unresolved.

### Phase 1: Player Development Summary

Purpose:

- Implement the smallest useful player-development view using existing evaluation data.

Minimal scope:

- latest submitted evaluations;
- perspective labels;
- category summaries;
- cycle selector;
- self versus external evaluation separation;
- recent notes;
- data completeness indicators;
- no AI;
- no advanced charts unless necessary.

Target users:

- staff and coaches first;
- players only if the existing My Evaluations privacy model supports the selected fields.

Acceptance criteria:

- summaries clearly separate self, peer, coach, staff, and guest perspectives;
- every summary shows cycle and data completeness;
- no hidden evaluator identity is exposed to players;
- raw source evaluations remain reachable to authorized reviewers;
- no automated ranking is presented;
- staff and coaches can understand the summary without reading every raw evaluation first.

### Phase 2: Historical Progress

Purpose:

- Show player development across cycles.

Scope:

- cycle-to-cycle history;
- category trends;
- longitudinal player view;
- data completeness indicators;
- historical notes grouped by cycle.

Dependencies:

- multiple real evaluation cycles;
- stable question categories;
- clear handling for changed question sets.

### Phase 3: Coach Dashboard

Purpose:

- Help coaches monitor evaluation coverage and player-development work.

Scope:

- evaluation coverage;
- incomplete work;
- team/cycle filters;
- links to player development summaries;
- no automated player ranking by default.

Dependencies:

- Player Development Summary V1;
- validated coach workflow needs from pilot.

### Phase 4: Reporting

Purpose:

- Provide printable or shareable player-development outputs.

Scope:

- printable player-development report;
- approved PDF export;
- privacy-aware visibility rules.

Dependencies:

- approved report content;
- visibility rules;
- source-data verification approach.

### Phase 5: Account Communications

Purpose:

- Reduce staff effort for account setup and operational reminders.

Scope:

- email invitations;
- verified password recovery;
- account activation communication;
- operational reminders.

Dependencies:

- production email configuration;
- consent and communication preferences;
- support process for failed delivery.

### Phase 6: Parent Experience

Purpose:

- Share approved player-development information with parents.

Scope:

- approved parent-facing summaries;
- explicit visibility rules;
- linked-player access.

Dependencies:

- stable player development summaries;
- parent visibility decisions;
- account communication workflows;
- privacy review.

### Phase 7: AI-Assisted Insights

Purpose:

- Add source-grounded AI assistance after data quality, visibility, and auditability are proven.

Scope:

- source-grounded summaries;
- human review;
- auditability;
- privacy controls;
- no autonomous decisions.

Dependencies:

- mature source data;
- approved prompt/output logging policy;
- consent/privacy review;
- user verification workflow.

## 9. Dependencies

Platform V2 depends on:

- successful Platform V1 pilot usage;
- enough submitted evaluations per cycle;
- reliable self, peer, coach, staff, and guest perspective snapshots;
- clear evaluation question categories;
- active player/account links;
- privacy and visibility rules;
- deployment stability;
- operational support for account access;
- staff agreement on terminology and aggregation rules.

Features should not advance when their dependencies are unresolved. For example, parent reports should not start before visibility rules are approved, and AI summaries should not start before source-grounding and auditability are designed.

## 10. Data Requirements

Minimum data needed for Player Development Summary V1:

- active players;
- evaluation cycles;
- submitted evaluations;
- perspective snapshots;
- evaluator role snapshots;
- rating responses;
- notes/text responses;
- question categories;
- submitted timestamps.

Data quality checks:

- enough evaluations per player;
- enough coach evaluations to support external summaries;
- self evaluations present for meaningful self/external comparison;
- consistent question categories across cycles;
- no unresolved player identity duplicates;
- no unclear inactive player/account state;
- no missing perspective snapshots.

Data completeness should be visible in user-facing summaries. If a player has one evaluation, the platform should say so rather than imply broad consensus.

## 11. Privacy And Safety Principles

Platform V2 should follow these principles:

- Youth player data is sensitive.
- Player-facing pages must not reveal hidden evaluator identities.
- Parent-facing pages require explicit approval and visibility rules.
- Peer comments may need stronger filtering or approval before sharing.
- Coach/staff review may show more detail than player/parent views.
- Reports must clearly identify audience and visibility.
- AI output must be verifiable and advisory.
- Rankings should not be presented as objective truth.
- Users should understand whether they are viewing raw evaluations, summaries, or generated interpretation.

## 12. AI Guardrails

AI work should be deferred until after non-AI player development summaries are useful.

Before production AI use, decide:

- which data AI may read;
- who may generate AI summaries;
- whether prompts and outputs are stored;
- who can view generated summaries;
- whether summaries need staff approval;
- how users verify summaries against source evaluations;
- how incorrect summaries are corrected;
- how youth privacy and consent are handled.

AI must not:

- make roster, placement, scholarship, discipline, eligibility, medical, or injury decisions;
- invent facts not present in source data;
- hide source evaluations from authorized reviewers;
- replace coach or staff judgment;
- produce public claims about players without review.

## 13. Success Metrics

Recommended Platform V2 metrics:

- evaluation completion rate;
- percentage of active players with evaluation coverage;
- percentage of players with self evaluations;
- average time to complete an evaluation;
- number of unresolved import conflicts;
- coach review usage;
- player My Evaluations usage;
- user-reported workflow friction;
- data completeness by cycle;
- report generation usage;
- support requests;
- privacy incidents;
- system errors.

Avoid vanity metrics such as raw page views without task context.

Do not define player performance rankings as platform success metrics.

## 14. Risks And Mitigations

| Risk | Why It Matters | Mitigation |
| --- | --- | --- |
| Insufficient evaluation volume | Summaries may be misleading. | Show data completeness and wait for enough pilot data. |
| Inconsistent evaluator scoring | One evaluator may rate differently than another. | Separate perspectives and show counts before averages. |
| Misleading averages | Averages can hide disagreement or small sample size. | Label perspectives, show sample size, and keep source data visible. |
| Self-evaluation bias | Self ratings may differ from external feedback. | Treat self as its own perspective, not as interchangeable data. |
| Coach bias | Coach feedback may reflect limited exposure or role context. | Preserve evaluator role and perspective; compare across evaluators carefully. |
| Youth privacy | Sensitive data can affect players and families. | Apply strict visibility rules and avoid raw parent access by default. |
| Evaluator identity leakage | Player-facing pages should not reveal hidden identities. | Reuse My Evaluations privacy rules and test visibility paths. |
| Overreliance on AI | Generated summaries can be wrong or overtrusted. | Defer AI, require source grounding, and keep humans responsible. |
| Overengineered visualizations | Complex charts may distract from useful tasks. | Start with tables and simple summaries. |
| Dashboards before data quality | Poor input data creates poor decision support. | Complete pilot and data readiness first. |
| Parent access to sensitive raw comments | Raw peer/coach notes may not be appropriate for parents. | Require approval and content selection before parent portal work. |
| Ranking youth players without context | Rankings may be harmful or misleading. | Avoid automated ranking as a product goal. |
| Feature expansion before validation | Work may solve the wrong problem. | Use pilot feedback and stop/go criteria. |

## 15. Deferred Ideas

Do not implement these unless separately approved:

- automated roster selection;
- automated player ranking;
- eligibility decisions;
- scholarship decisions;
- disciplinary decisions;
- medical conclusions;
- injury diagnosis;
- public player profiles;
- anonymous public evaluations;
- unrestricted parent access;
- AI-generated decisions;
- recruiting claims presented as verified facts;
- complex predictive modeling before sufficient data exists.

## 16. Recommended First Implementation Phase

Recommended first phase after pilot:

```text
Player Development Summary V1
```

Why this phase has the highest value:

- It uses data already collected by Platform V1.
- It helps coaches and staff turn raw evaluations into actionable review context.
- It validates summary and aggregation rules before reports, parent access, or AI.
- It avoids high-risk features such as automated rankings or generated conclusions.

Required data:

- submitted evaluations;
- evaluation cycle;
- question category;
- numeric rating responses;
- text notes;
- perspective snapshot;
- evaluator role snapshot;
- player identity.

Target users:

- staff;
- coaches;
- possibly players if the data shown matches existing My Evaluations privacy rules.

Minimal scope:

- player-level summary page or section;
- cycle selector;
- submitted evaluation count;
- category summary by perspective;
- latest notes grouped by perspective;
- clear data completeness message;
- links back to source evaluations for authorized users.

Non-scope:

- AI;
- complex charts;
- automated rankings;
- parent access;
- new evaluation question sets;
- major account changes;
- exports;
- prediction.

Acceptance criteria:

- user can see a player's latest development summary;
- self, peer, coach, staff, and guest perspectives are clearly separated;
- summary shows cycle and data completeness;
- source evaluations remain available to authorized reviewers;
- player-facing visibility does not expose hidden evaluator identities;
- no automated ranking or placement recommendation is shown.

Privacy constraints:

- player-facing summaries must follow My Evaluations privacy rules;
- coach/staff summaries may show more context than player-facing summaries;
- parent visibility is out of scope;
- notes may require filtering before broader sharing.

Production risks:

- summary may be misleading if data is sparse;
- changed question sets may complicate category summaries;
- users may overinterpret averages;
- notes may contain sensitive freeform content.

## 17. Stop/Go Decision Points

### Before Platform V2 Implementation

Go only if:

- pilot workflows are usable;
- evaluation data exists for a representative roster;
- users understand self, peer, coach, staff, and guest perspectives;
- privacy rules for the first summary audience are defined;
- first-phase scope is limited and testable.

Stop if:

- Platform V1 workflows are still unreliable;
- users cannot complete evaluations;
- evaluation questions are unclear;
- data volume is too low;
- privacy/visibility rules are unresolved.

### Before Historical Progress

Go only if:

- multiple cycles exist;
- cycle definitions are used consistently;
- question categories are stable enough for comparison.

### Before Parent Experience

Go only if:

- parent visibility rules are approved;
- player-facing summaries are stable;
- sensitive comments are handled intentionally;
- account communication workflows are reliable.

### Before AI

Go only if:

- summaries are useful without AI;
- source-grounding rules are defined;
- audit and privacy policies are approved;
- users can verify AI output against source evaluations.

## 18. Open Product Questions

- Who is the first approved audience for Player Development Summary V1: staff only, coaches, or players too?
- Which evaluation categories matter most for development summaries?
- What minimum number of evaluations is needed before showing averages?
- Should self evaluations be shown beside coach evaluations or in a separate section?
- Which freeform notes are safe for players to see?
- Should staff approve player-facing summaries before publication?
- What parent-facing information is appropriate, and who approves it?
- Are coach/team assignments needed before coach dashboards become useful?
- What report format is most useful for meetings: browser print, PDF, or both?
- What account email workflows are required before parent or player expansion?
- Which events require audit logging before broader production use?
- What language should the platform use to prevent summaries from being treated as rankings?

## Final Recommendation

Do not start Platform V2 by building AI, parent access, or complex visual analytics.

Run a real Platform V1 evaluation pilot first. Use the findings to approve a narrow Player Development Summary V1 that separates evaluation perspectives, shows data completeness, and helps coaches and staff make better development decisions without turning youth player feedback into automated rankings.

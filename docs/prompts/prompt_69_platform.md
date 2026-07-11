# Prompt 69 - Platform

## User Prompt

```text
Implement a production-ready Self-Evaluation extension for Evaluation Access V1.

Use continuous loop engineering.

This is not a fixed-number loop.

Continue until the work reaches a valid terminal state.

==================================================
Product Intent
==============

Players should be allowed to evaluate themselves.

A self-evaluation must be clearly and consistently identified as:

Self Evaluation

It must never be indistinguishable from:

* a peer evaluation;
* a coach evaluation;
* a staff evaluation;
* a guest evaluator submission.

The current system blocks self-evaluation.

Replace that blanket restriction with an explicit, safe self-evaluation workflow.

Do not merely delete the self-evaluation permission check.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete implementation, review, documentation, or verification work remains and the next loop can make meaningful progress.

PASS

All acceptance criteria are satisfied, all verification commands pass, documentation is current, commits are pushed, and the working tree is clean.

BLOCKED

A necessary decision or fix requires:

* unresolved product direction;
* destructive migration;
* external infrastructure;
* architecture expansion outside the approved feature;
* a security/privacy decision that cannot safely be inferred.

NO_PROGRESS

Two consecutive complete loops fail to make concrete progress toward an unsatisfied acceptance criterion.

Do not continue indefinitely through speculative refactoring.

Only declare the feature production-ready when the terminal state is PASS.

==================================================
Established Loop Workflow
=========================

Every loop must complete the full repository workflow.

Do not skip stages, even for a small fix.

Each loop must:

1. Reconcile the current committed state.
2. Read the previous loop prompt and result.
3. Confirm the working tree is clean.
4. Inspect the complete affected workflow.
5. Identify concrete, evidence-based issues or incomplete criteria.
6. Create the next prompt archive for that loop before implementation, following `AGENTS.md`.
7. Implement only the selected verified work.
8. Add or update focused tests.
9. Run focused tests.
10. Perform a senior-engineer self-review.
11. Fix every verified review issue.
12. Update relevant documentation.
13. Run the complete verification suite.
14. Commit implementation, tests, migrations, and documentation.
15. Finalize the prompt archive with the commit hash and loop result.
16. Commit the prompt archive separately.
17. Push both commits.
18. Re-read the committed diff.
19. Confirm the working tree is clean.
20. Reassess every acceptance criterion.
21. Choose CONTINUE, PASS, BLOCKED, or NO_PROGRESS.
22. If CONTINUE, begin the next loop without asking for confirmation.

Each loop gets its own new prompt archive and two commits:

1. implementation/review/documentation commit;
2. prompt archive commit.

Do not combine multiple loops into one commit.

==================================================
Before Loop 1
=============

Read:

* `AGENTS.md`
* `README.md`
* `docs/ARCHITECTURE.md`
* `docs/USER_MANUAL.md`
* `docs/evaluations/implementation/engineering/evaluation_access_v1.md`
* `docs/analytics/`
* `docs/account_management/V1_SUMMARY.md`
* relevant prompt archives for Evaluation Access V1
* current migration history

Inspect:

* `analytics/models.py`
* `analytics/services/permissions.py`
* `analytics/services/evaluation_access_service.py`
* `analytics/services/evaluation_review_service.py`
* `analytics/services/observation_service.py`
* `analytics/services/question_service.py`
* `analytics/forms.py`
* `analytics/views.py`
* `analytics/urls.py`
* evaluation templates
* My Evaluations templates
* coach review templates
* staff review templates
* `analytics/tests.py`
* `accounts/models.py`
* `accounts/services/link_service.py`
* account profile navigation
* current player self-link rules

Review the current database constraints governing duplicate evaluations.

Do not assume that evaluator role alone can distinguish self and peer evaluations.

==================================================
Architecture Goal
=================

The system must explicitly record the evaluation perspective.

Recommended perspectives:

* self
* peer
* coach
* staff
* guest

Use names consistent with the current model and codebase after inspection.

The stored value must be a snapshot of the submission context.

It must not be inferred dynamically later from the evaluator’s current role or current user-player links.

For example:

* a player evaluating themselves → self;
* a player evaluating another player → peer;
* a coach evaluating a player → coach;
* staff/admin evaluating a player → staff;
* guest evaluator evaluating a player → guest.

If the current architecture has an existing suitable source/type field, reuse or extend it cleanly.

Otherwise, add the smallest explicit field required.

A model change and migration are authorized for this feature.

Do not add a large generalized evaluation-type subsystem unless current architecture clearly requires it.

==================================================
Required Domain Rules
=====================

## Self Evaluation

A self-evaluation is permitted only when:

* the user is authenticated;
* the account may submit evaluations;
* the user has an active `UserPlayerLink` with relationship `self`;
* the linked player is active;
* the target player is that actively self-linked player;
* the evaluation perspective is explicitly stored as `self`.

A player must not be able to submit a self-evaluation for an unrelated player by manipulating form data or URLs.

## Peer Evaluation

When a player evaluates a different player:

* perspective must be stored as `peer`;
* it must not be labelled self-evaluation;
* normal player evaluation permissions remain in force.

## Coach, Staff And Guest Evaluations

Existing evaluation behavior must continue:

* coach submissions are identified as coach evaluations;
* staff/admin submissions are identified consistently according to current policy;
* guest evaluator submissions are identified as guest evaluations;
* parent accounts remain unable to submit unless another authorized evaluator role is assigned.

## Historical Snapshot

Changing the evaluator’s account role or user-player links after submission must not alter the stored evaluation perspective.

==================================================
Duplicate And Cycle Rules
=========================

Inspect the current duplicate-evaluation constraint and service rules.

Implement a clear rule for self-evaluation.

Recommended rule:

* one submitted self-evaluation per player per active evaluation cycle;
* a draft self-evaluation may be resumed;
* duplicate submitted self-evaluations in the same cycle are rejected;
* a peer evaluation and a self-evaluation are distinct submissions;
* existing coach/staff/guest duplicate rules remain intact.

Do not accidentally allow unlimited duplicate evaluations by changing an existing database constraint incorrectly.

If the existing constraint cannot represent the new semantics, update it through a safe migration.

Review compatibility with existing production data.

The migration must preserve existing observations.

Existing records should receive a correct perspective through a deterministic data migration when practical:

* player evaluator targeting an actively self-linked player at the relevant time may not be historically inferable;
* do not guess historical self-evaluations because the current system blocked them;
* existing player submissions can safely default to `peer`;
* existing coach/staff/admin/guest records should map from the stored evaluator role snapshot.

Document the migration rule.

==================================================
Submission UX
=============

The evaluation flow must make the submission type obvious.

Preferred behavior:

* the system derives the perspective from the evaluator and target player;
* the user does not freely choose an arbitrary perspective;
* when a player selects themselves, the page clearly displays:
  `Self Evaluation`;
* when a player selects another player, it clearly displays:
  `Peer Evaluation`;
* coach/staff/guest labels are displayed appropriately.

Do not provide a client-controlled hidden field that can override the server-derived perspective.

The backend remains authoritative.

Before submission, self-evaluation pages should include concise explanatory copy, such as:

> You are evaluating yourself. This submission will be clearly labelled as a Self Evaluation.

Do not require JavaScript.

==================================================
Evaluation Lists And Own Submission
===================================

On evaluation submission/list pages:

* self-evaluation rows must be labelled `Self Evaluation`;
* peer evaluations must be labelled `Peer Evaluation`;
* existing evaluator-owned submission links remain private;
* evaluators may view their own submitted self-evaluation;
* the label must be based on the stored perspective snapshot.

==================================================
Player “My Evaluations”
=======================

Self-evaluations should be visible in the player’s My Evaluations area.

They must be clearly labelled:

Self Evaluation

External evaluations must retain their existing privacy rules:

* player-facing results hide evaluator identity;
* evaluator role/category or perspective may be shown safely;
* self-evaluation can identify that it was submitted by the player themselves;
* do not reveal hidden evaluator identities for peer, coach, staff, or guest evaluations.

The player-facing list and detail should make it easy to distinguish:

* Self Evaluation
* Peer Evaluation
* Coach Evaluation
* Staff Evaluation
* Guest Evaluation

Use friendly display labels rather than raw database keys.

Draft and reopened evaluations remain excluded from final My Evaluations results.

==================================================
Coach Review
============

Coach evaluation review must show the stored evaluation perspective.

Add or update filtering so coaches can filter by perspective when practical.

At minimum, coaches must be able to distinguish:

* self evaluations;
* peer evaluations;
* coach evaluations;
* staff evaluations;
* guest evaluations.

Coach review may continue showing evaluator identity according to existing rules.

Self-evaluations must not be mixed invisibly into external evaluation results.

Do not add comparison charts or self-versus-coach analytics in this feature.

==================================================
Staff Review
============

Existing staff review and reopen behavior must remain functional.

Staff review should show the evaluation perspective clearly.

Reopening and resubmitting must not silently change the stored perspective unless the submission context genuinely requires re-derivation and the current workflow explicitly supports it.

Prefer preserving the original perspective snapshot.

==================================================
Permissions And Security
========================

Remove the blanket self-evaluation denial only after explicit perspective enforcement exists.

Backend services must enforce:

* only a player linked to themselves can submit a self-evaluation;
* a coach cannot mark an evaluation as self;
* a guest evaluator cannot mark an evaluation as self;
* a player cannot mark an evaluation of another player as self;
* request manipulation cannot override the derived perspective;
* inactive self links do not allow self-evaluation;
* inactive players cannot receive new evaluations under current policy;
* role changes do not rewrite historical perspective snapshots.

Views remain thin.

Templates do not decide permissions or perspective.

==================================================
Privacy Requirements
====================

Self-evaluation support must not weaken existing player privacy.

Verify:

* My Evaluations still hides evaluator names for external evaluations;
* stored perspective does not expose user IDs or account metadata;
* coach review exposes only currently approved evaluator information;
* staff review behavior remains unchanged except for the new label;
* no raw evaluator object is added to player-facing read models;
* forbidden detail access remains 403;
* nonexistent records remain 404.

==================================================
User Manual Update
==================

Update:

* `docs/USER_MANUAL.md`

The manual must clearly explain:

* players may evaluate themselves;
* self-evaluations are explicitly labelled;
* players may still evaluate other players as peer evaluations;
* self and peer evaluations are stored as different perspectives;
* how to start a self-evaluation;
* how self-evaluations appear in My Evaluations;
* how coaches can distinguish/filter self-evaluations;
* self-evaluation does not reveal identities of external evaluators;
* the system does not yet provide self-versus-coach charts or automated comparison analysis unless that functionality already exists.

Remove or replace all stale statements saying self-evaluation is prohibited.

Review:

* role quick-start sections;
* evaluation workflow;
* Player Quick Start;
* Coach Quick Start;
* My Evaluations;
* Coach Review;
* FAQ;
* privacy section.

Use friendly language.

Do not add deployment or engineering details to the user manual.

==================================================
Engineering Documentation
=========================

Update as necessary:

* `docs/evaluations/implementation/engineering/evaluation_access_v1.md`
* `docs/ARCHITECTURE.md`
* Analytics architecture/permission documentation
* relevant status documents

Record:

* perspective model;
* snapshot behavior;
* permission rules;
* duplicate rules;
* migration/backfill behavior;
* privacy behavior;
* feature status.

Do not mark the extension complete until PASS.

==================================================
Loop 1 Recommended Objective
============================

Loop 1 should normally:

1. inspect the current model and duplicate constraints;
2. design the smallest explicit perspective representation;
3. create the migration;
4. implement server-derived perspective classification;
5. allow valid self-evaluation;
6. preserve peer/coach/staff/guest behavior;
7. update core submission UI;
8. add focused model/service/view tests;
9. update initial documentation;
10. run full verification;
11. commit, archive, push, and reassess.

If inspection reveals a safer minimal design, use it and document the rationale.

==================================================
Subsequent Loop Priorities
==========================

Each later loop must reassess the whole feature.

Prioritize in this order:

1. authorization and request manipulation;
2. migration/data integrity;
3. duplicate rules;
4. perspective snapshot correctness;
5. player privacy;
6. My Evaluations labels;
7. coach/staff review labels and filtering;
8. draft/reopen behavior;
9. performance/query behavior;
10. documentation consistency;
11. user experience.

Do not spend a loop on cosmetic refactoring alone.

==================================================
Required Test Coverage
======================

Add comprehensive tests covering at least:

## Perspective Derivation

* player evaluating self → self;
* player evaluating another player → peer;
* coach evaluating player → coach;
* staff/admin evaluating player → correct staff/admin policy;
* guest evaluator evaluating player → guest;
* perspective saved as a snapshot;
* later role changes do not alter it.

## Self-Evaluation Permissions

* active self-linked player can evaluate self;
* inactive self link denied;
* unrelated player denied;
* inactive target player denied;
* parent denied;
* coach cannot create a self evaluation;
* guest cannot create a self evaluation;
* request manipulation cannot force perspective.

## Duplicate Rules

* self-evaluation draft resumes;
* one submitted self-evaluation per player/cycle;
* duplicate submitted self-evaluation rejected;
* self and peer submissions remain distinct;
* existing coach duplicate protections remain;
* migration constraints work on SQLite.

## Submission UI

* self target clearly shows Self Evaluation;
* different player target shows Peer Evaluation;
* submitted list labels correctly;
* own submission detail labels correctly.

## My Evaluations

* self-evaluation appears;
* clearly labelled Self Evaluation;
* external evaluator identity remains hidden;
* peer/coach/staff/guest labels are correct;
* draft/reopened self-evaluations excluded;
* response ordering remains deterministic;
* active self-link access remains required.

## Coach Review

* self-evaluation visible and labelled;
* perspective filter works;
* filters combine correctly;
* evaluator identity rules remain correct;
* submitted-only behavior remains;
* no N+1 regression where query-count testing is practical.

## Staff Review

* staff review remains available;
* reopen still works;
* perspective remains stable after reopen;
* existing staff permissions remain unchanged.

## Regressions

* coach import works;
* player import/account provisioning works;
* account operations work;
* peer evaluation works;
* coach evaluation works;
* guest evaluation works;
* existing player privacy tests pass;
* existing coach review tests pass;
* existing staff review tests pass.

==================================================
Focused Verification Per Loop
=============================

Run focused tests for affected apps.

At minimum:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py test analytics
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts
```

If players or another app changes, run its tests too.

Run:

```bash
git diff --check
```

Do not proceed with known focused-test failures.

==================================================
Full Verification Every Loop
============================

Every loop must run:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations analytics --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations players --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py test analytics
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test players
DJANGO_SECRET_KEY=test-only-not-production python manage.py test drafts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test pdp
DJANGO_SECRET_KEY=test-only-not-production python manage.py test
git diff --check
```

All commands must pass before an implementation commit is created.

If a migration is added, verify:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py migrate --plan
```

Also test migration application against a temporary/test database through the normal Django test suite.

==================================================
Self-Review Every Loop
======================

Review each diff as a senior engineer.

Check:

* migration safety;
* backfill correctness;
* SQLite compatibility;
* duplicate constraints;
* transaction boundaries;
* permission bypasses;
* role/perspective confusion;
* unsafe form fields;
* hidden-field manipulation;
* active/inactive links;
* historical snapshot stability;
* 403/404 behavior;
* player privacy;
* evaluator identity leakage;
* thin views;
* service ownership;
* dependency direction;
* query count and N+1 risks;
* deterministic ordering;
* stale wording;
* dead code;
* unused imports;
* documentation drift.

Fix all verified issues before committing.

==================================================
Production Readiness Acceptance Criteria
========================================

Do not declare PASS until all criteria are satisfied.

A. Data Model

* perspective is explicitly stored;
* migration is additive and safe;
* historical records receive deterministic values;
* raw perspective choices are validated;
* database constraints support required duplicate rules.

B. Permissions

* valid self-evaluation allowed;
* invalid self-evaluation denied;
* peer evaluation remains valid;
* request manipulation cannot forge perspective;
* inactive links/players are denied.

C. Snapshot Integrity

* perspective is derived server-side;
* perspective survives role changes;
* perspective survives link changes;
* reopened observations preserve correct perspective.

D. UX

* Self Evaluation is unmistakably labelled;
* Peer Evaluation is distinguishable;
* no arbitrary perspective selector permits impersonation;
* task flow remains usable without JavaScript.

E. Player Results

* self-evaluation appears in My Evaluations;
* external evaluator privacy remains intact;
* all perspectives have friendly labels;
* draft/reopened results excluded.

F. Coach Review

* self evaluations are identifiable;
* perspective filtering works;
* external evaluator identity rules remain correct;
* submitted-only and read-only behavior remain.

G. Staff Review

* existing review/reopen workflow works;
* perspective is visible;
* no staff permission regression.

H. Documentation

* user manual accurately explains self-evaluation;
* no stale self-evaluation prohibition remains;
* engineering docs explain the model and rules;
* architecture and status documents are consistent.

I. Verification

* full test suite passes;
* migration checks pass;
* migration plan is reviewed;
* working tree is clean;
* commits are pushed.

==================================================
Non-Goals
=========

Do not implement:

* self-versus-coach charts;
* automatic gap analysis;
* averages comparing perspectives;
* AI summaries;
* confidence scoring;
* development plans;
* parent evaluation;
* anonymous evaluation;
* configurable perspective types through admin;
* new question sets specifically for self-evaluation;
* email notifications;
* dashboards beyond required labels/filtering;
* exports;
* APIs;
* JavaScript frameworks;
* account or player redesign;
* unrelated production deployment work.

If self-evaluation would benefit from different questions, defer that as a separate future feature. For this extension, reuse the active evaluation question set unless current architecture requires otherwise.

==================================================
Prompt Archive And Git Workflow
===============================

For every loop:

1. Create the next prompt archive before implementation according to `AGENTS.md`.
2. Record the loop objective, current gaps, selected work, tests, and non-goals.
3. Complete implementation and full verification.
4. Commit implementation/tests/migration/documentation.
5. Update the prompt archive with:

   * implementation commit hash;
   * diff summary;
   * issues found;
   * fixes applied;
   * verification results;
   * remaining acceptance gaps;
   * loop terminal state.
6. Commit the prompt archive separately.
7. Push both commits.
8. Confirm the remote update succeeded.
9. Confirm the working tree is clean.
10. Reassess the feature from the committed state.

Suggested implementation commit messages may include:

* `Implement labeled player self evaluations`
* `Harden self evaluation permissions`
* `Fix self evaluation duplicate rules`
* `Improve self evaluation review labels`
* `Complete self evaluation production review`

Do not create an unrelated feature commit.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* satisfies an unsatisfied acceptance criterion;
* fixes a verified defect;
* adds missing regression proof;
* improves required migration/data safety;
* removes an architecture or privacy violation;
* corrects material documentation drift.

Formatting-only edits and speculative refactors do not count.

If two consecutive loops make no concrete progress and PASS cannot be reached, stop with NO_PROGRESS and report the remaining unproven criteria.

==================================================
Final PASS Review
=================

Before PASS, perform one final complete review from these perspectives:

* player submitting a self-evaluation;
* player submitting a peer evaluation;
* coach reviewing evaluations;
* staff reopening an evaluation;
* administrator reviewing permissions and data;
* privacy reviewer checking player-facing output;
* release engineer reviewing migration safety.

Confirm the manual is understandable for a non-technical player and coach.

Only then update status documentation to say the Self-Evaluation extension is complete and production-ready.

==================================================
Final Report
============

Report:

* terminal state;
* number of loops completed;
* objective of each loop;
* issues identified in each loop;
* fixes applied in each loop;
* model and migration changes;
* historical backfill decision;
* duplicate-rule decision;
* permission behavior;
* UX behavior;
* My Evaluations behavior;
* coach review behavior;
* staff review behavior;
* privacy outcome;
* documentation changes;
* tests added;
* focused verification results;
* full verification results;
* remaining deferred work;
* commits created;
* push results;
* confirmation that the working tree is clean.

Only declare the Self-Evaluation extension accepted when the terminal state is PASS.
```

## Loop 1 Objective

Implement the smallest production-ready self-evaluation extension:

- add explicit stored evaluation perspective;
- migrate/backfill existing observations deterministically;
- derive perspective server-side;
- allow valid active self-linked player self-evaluations;
- preserve peer/coach/staff/guest behavior;
- make self/peer/coach/staff/guest labels visible in submission, My Evaluations, coach review, and staff review;
- add focused tests;
- update user and engineering documentation;
- run full verification.

## Current Gaps

- Current `Observation` had evaluator role snapshots but no explicit perspective snapshot.
- Current permissions blocked self-evaluation through `is_player_self`.
- Current duplicate rules did not model self evaluation as a distinct stored perspective.
- My Evaluations and coach review showed evaluator role labels only, not evaluation perspective labels.
- User manual stated self-evaluation was prohibited.

## Selected Work

- Added `evaluation_perspective` to `analytics.Observation`.
- Added perspective constants, choices, labels, and migration/backfill rules.
- Updated services and permissions to derive perspective server-side.
- Updated duplicate logic for evaluator/perspective and one self-evaluation per player/cycle.
- Updated templates/read models/admin to display friendly labels.
- Added tests for perspective derivation, self permissions, duplicate behavior, My Evaluations, coach review, and staff review stability.
- Updated documentation.

## Non-Goals

- No self-vs-coach charts.
- No AI summaries.
- No exports or APIs.
- No new question sets.
- No account/player redesign.
- No deployment work.

## Implementation Commit

`a086348d0d1afa54d48609c89f7d5f3d32da1691`

## Issues Found

- Existing player self-evaluation checks were blanket denials instead of explicit perspective-aware rules.
- Existing read models did not expose a friendly evaluation type label.
- Documentation had stale self-evaluation prohibition language.
- Staff reopen tests needed to prove perspective stability rather than assume a role based on a fixture username.

## Fixes Applied

- Added stored `self`, `peer`, `coach`, `staff`, and `guest` perspectives.
- Added deterministic backfill: existing player submissions become peer; coach/staff/admin/guest records map from the evaluator role snapshot.
- Added active self-link enforcement for self evaluation and inactive self-link denial.
- Kept perspective server-derived; no client-controlled perspective field was added.
- Added labels and filtering to player submission, My Evaluations, coach review, and staff review surfaces.
- Added tests and documentation updates.

## Verification Results

```text
DJANGO_SECRET_KEY=test-only-not-production python manage.py check: PASS
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations analytics --check: PASS
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations accounts --check: PASS
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations players --check: PASS
DJANGO_SECRET_KEY=test-only-not-production python manage.py migrate --plan: REVIEWED
DJANGO_SECRET_KEY=test-only-not-production python manage.py test analytics: PASS, 127 tests
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts: PASS, 184 tests
DJANGO_SECRET_KEY=test-only-not-production python manage.py test players: PASS, 43 tests
DJANGO_SECRET_KEY=test-only-not-production python manage.py test drafts: PASS, 8 tests
DJANGO_SECRET_KEY=test-only-not-production python manage.py test pdp: PASS, 6 tests
DJANGO_SECRET_KEY=test-only-not-production python manage.py test: PASS, 395 tests
git diff --check: PASS
```

## Remaining Acceptance Gaps

None identified for the requested production-ready Self-Evaluation extension.

## Loop Terminal State

PASS.

## Implementation Commit Diff

```diff
commit a086348d0d1afa54d48609c89f7d5f3d32da1691
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Fri Jul 10 23:55:05 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Fri Jul 10 23:55:05 2026 -0700

    Implement labeled player self evaluations
---
 accounts/services/link_service.py                  |  14 ++
 analytics/admin.py                                 |   4 +-
 ...ique_coach_assessment_per_evaluator_and_more.py |  51 ++++++++
 analytics/models.py                                |  38 +++++-
 analytics/services/coach_assessment_service.py     |  42 +++++-
 analytics/services/evaluation_access_service.py    |   6 +
 analytics/services/evaluation_review_service.py    |  11 ++
 analytics/services/observation_service.py          |  41 +++++-
 analytics/services/permissions.py                  |  49 ++++++-
 .../templates/analytics/assessment_detail.html     |   1 +
 analytics/templates/analytics/assessment_form.html |   1 +
 analytics/templates/analytics/assessment_list.html |   4 +-
 analytics/templates/analytics/evaluation_form.html |   1 +
 analytics/templates/analytics/evaluation_list.html |   6 +-
 .../analytics/evaluation_review_detail.html        |   2 +
 .../analytics/evaluation_review_list.html          |  13 +-
 .../templates/analytics/my_evaluation_detail.html  |   2 +
 analytics/templates/analytics/my_evaluations.html  |   4 +-
 .../analytics/observation_review_list.html         |   4 +-
 analytics/tests.py                                 | 143 ++++++++++++++++++---
 analytics/views.py                                 |   6 +-
 docs/ARCHITECTURE.md                               |   3 +-
 docs/USER_MANUAL.md                                |  21 +--
 docs/analytics/architecture/10_permissions.md      |  12 +-
 .../engineering/evaluation_access_v1.md            |  69 ++++++----
 25 files changed, 466 insertions(+), 82 deletions(-)

diff --git a/accounts/services/link_service.py b/accounts/services/link_service.py
index b22d8ab..9119df3 100644
--- a/accounts/services/link_service.py
+++ b/accounts/services/link_service.py
@@ -235,6 +235,20 @@ def get_self_linked_players(user, active_only=True):
     return Player.objects.filter(**filters).distinct().order_by("last_name", "first_name", "id")
 
 
+def has_self_link(user, player, active_only=True) -> bool:
+    """Return whether a user has a self relationship to a player."""
+    _validate_user(user)
+    _validate_player(player)
+    filters = {
+        "user": user,
+        "player": player,
+        "relationship": UserPlayerRelationship.SELF,
+    }
+    if active_only:
+        filters["is_active"] = True
+    return UserPlayerLink.objects.filter(**filters).exists()
+
+
 def get_users_for_player(player, active_only=True):
     """Return users linked to a player."""
     _validate_player(player)
diff --git a/analytics/admin.py b/analytics/admin.py
index 2e2fe7a..b1c1ea9 100644
--- a/analytics/admin.py
+++ b/analytics/admin.py
@@ -99,15 +99,17 @@ class ObservationAdmin(TimeStampedAdmin):
         "status",
         "evaluator",
         "evaluator_role_name",
+        "evaluation_perspective",
         "submitted_at",
     )
-    list_filter = ("status", "observation_type", "evaluation_cycle", "evaluator_role_key", "source")
+    list_filter = ("status", "observation_type", "evaluation_cycle", "evaluator_role_key", "evaluation_perspective", "source")
     search_fields = ("player__first_name", "player__last_name", "evaluator__username", "evaluator__email")
     readonly_fields = TimeStampedAdmin.readonly_fields + (
         "submitted_at",
         "observation_type_key",
         "evaluator_role_key",
         "evaluator_role_name",
+        "evaluation_perspective",
     )
     inlines = [ObservationResponseInline]
 
diff --git a/analytics/migrations/0003_remove_observation_analytics_unique_coach_assessment_per_evaluator_and_more.py b/analytics/migrations/0003_remove_observation_analytics_unique_coach_assessment_per_evaluator_and_more.py
new file mode 100644
index 0000000..58cb4ea
--- /dev/null
+++ b/analytics/migrations/0003_remove_observation_analytics_unique_coach_assessment_per_evaluator_and_more.py
@@ -0,0 +1,51 @@
+# Generated by Django 4.2.25 on 2026-07-11 06:26
+
+from django.db import migrations, models
+
+
+def backfill_evaluation_perspective(apps, schema_editor):
+    Observation = apps.get_model("analytics", "Observation")
+    role_mapping = {
+        "player": "peer",
+        "coach": "coach",
+        "assistant_coach": "coach",
+        "head_coach": "coach",
+        "coordinator": "coach",
+        "staff": "staff",
+        "admin": "staff",
+        "guest_evaluator": "guest",
+    }
+    for role_key, perspective in role_mapping.items():
+        Observation.objects.filter(evaluator_role_key=role_key).update(evaluation_perspective=perspective)
+
+
+class Migration(migrations.Migration):
+
+    dependencies = [
+        ('analytics', '0002_seed_observation_defaults'),
+    ]
+
+    operations = [
+        migrations.RemoveConstraint(
+            model_name='observation',
+            name='analytics_unique_coach_assessment_per_evaluator',
+        ),
+        migrations.AddField(
+            model_name='observation',
+            name='evaluation_perspective',
+            field=models.CharField(choices=[('self', 'Self Evaluation'), ('peer', 'Peer Evaluation'), ('coach', 'Coach Evaluation'), ('staff', 'Staff Evaluation'), ('guest', 'Guest Evaluation')], default='guest', max_length=40),
+        ),
+        migrations.RunPython(backfill_evaluation_perspective, migrations.RunPython.noop),
+        migrations.AddIndex(
+            model_name='observation',
+            index=models.Index(fields=['evaluation_perspective', 'evaluation_cycle'], name='analytics_o_evaluat_b05f17_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='observation',
+            constraint=models.UniqueConstraint(condition=models.Q(('evaluator__isnull', False), ('observation_type_key', 'coach_assessment')), fields=('player', 'evaluation_cycle', 'observation_type_key', 'evaluator', 'evaluation_perspective'), name='analytics_unique_coach_assessment_per_perspective'),
+        ),
+        migrations.AddConstraint(
+            model_name='observation',
+            constraint=models.UniqueConstraint(condition=models.Q(('evaluation_perspective', 'self'), ('observation_type_key', 'coach_assessment')), fields=('player', 'evaluation_cycle', 'observation_type_key', 'evaluation_perspective'), name='analytics_unique_self_assessment_per_player'),
+        ),
+    ]
diff --git a/analytics/models.py b/analytics/models.py
index 35e9b30..baf66f4 100644
--- a/analytics/models.py
+++ b/analytics/models.py
@@ -42,6 +42,22 @@ OBSERVATION_STATUS_CHOICES = [
     (OBSERVATION_STATUS_ARCHIVED, "Archived"),
 ]
 
+EVALUATION_PERSPECTIVE_SELF = "self"
+EVALUATION_PERSPECTIVE_PEER = "peer"
+EVALUATION_PERSPECTIVE_COACH = "coach"
+EVALUATION_PERSPECTIVE_STAFF = "staff"
+EVALUATION_PERSPECTIVE_GUEST = "guest"
+
+EVALUATION_PERSPECTIVE_CHOICES = [
+    (EVALUATION_PERSPECTIVE_SELF, "Self Evaluation"),
+    (EVALUATION_PERSPECTIVE_PEER, "Peer Evaluation"),
+    (EVALUATION_PERSPECTIVE_COACH, "Coach Evaluation"),
+    (EVALUATION_PERSPECTIVE_STAFF, "Staff Evaluation"),
+    (EVALUATION_PERSPECTIVE_GUEST, "Guest Evaluation"),
+]
+
+EVALUATION_PERSPECTIVE_LABELS = dict(EVALUATION_PERSPECTIVE_CHOICES)
+
 
 class TimeStampedModel(models.Model):
     created_at = models.DateTimeField(auto_now_add=True)
@@ -237,6 +253,11 @@ class Observation(TimeStampedModel):
     )
     evaluator_role_key = models.CharField(max_length=80, blank=True)
     evaluator_role_name = models.CharField(max_length=120, blank=True)
+    evaluation_perspective = models.CharField(
+        max_length=40,
+        choices=EVALUATION_PERSPECTIVE_CHOICES,
+        default=EVALUATION_PERSPECTIVE_GUEST,
+    )
     status = models.CharField(max_length=40, choices=OBSERVATION_STATUS_CHOICES, default=OBSERVATION_STATUS_DRAFT)
     submitted_at = models.DateTimeField(null=True, blank=True)
     notes = models.TextField(blank=True)
@@ -247,9 +268,17 @@ class Observation(TimeStampedModel):
         ordering = ["-submitted_at", "-created_at", "-id"]
         constraints = [
             models.UniqueConstraint(
-                fields=["player", "evaluation_cycle", "observation_type_key", "evaluator"],
+                fields=["player", "evaluation_cycle", "observation_type_key", "evaluator", "evaluation_perspective"],
                 condition=Q(observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT, evaluator__isnull=False),
-                name="analytics_unique_coach_assessment_per_evaluator",
+                name="analytics_unique_coach_assessment_per_perspective",
+            ),
+            models.UniqueConstraint(
+                fields=["player", "evaluation_cycle", "observation_type_key", "evaluation_perspective"],
+                condition=Q(
+                    observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
+                    evaluation_perspective=EVALUATION_PERSPECTIVE_SELF,
+                ),
+                name="analytics_unique_self_assessment_per_player",
             ),
         ]
         indexes = [
@@ -257,6 +286,7 @@ class Observation(TimeStampedModel):
             models.Index(fields=["evaluation_cycle", "observation_type", "status"]),
             models.Index(fields=["evaluator", "evaluation_cycle"]),
             models.Index(fields=["evaluator_role_key", "evaluation_cycle"]),
+            models.Index(fields=["evaluation_perspective", "evaluation_cycle"]),
             models.Index(fields=["observation_type_key", "status"]),
             models.Index(fields=["submitted_at"]),
         ]
@@ -274,6 +304,10 @@ class Observation(TimeStampedModel):
     def __str__(self) -> str:
         return f"{self.observation_type_key} for {self.player}"
 
+    @property
+    def evaluation_perspective_label(self) -> str:
+        return EVALUATION_PERSPECTIVE_LABELS.get(self.evaluation_perspective, "Evaluation")
+
 
 class ObservationResponse(TimeStampedModel):
     observation = models.ForeignKey(Observation, on_delete=models.CASCADE, related_name="responses")
diff --git a/analytics/services/coach_assessment_service.py b/analytics/services/coach_assessment_service.py
index df43dbf..240aeed 100644
--- a/analytics/services/coach_assessment_service.py
+++ b/analytics/services/coach_assessment_service.py
@@ -7,6 +7,7 @@ from django.db import transaction
 from django.db.models import Q
 
 from analytics.models import (
+    EVALUATION_PERSPECTIVE_LABELS,
     OBSERVATION_STATUS_DRAFT,
     OBSERVATION_STATUS_REOPENED,
     OBSERVATION_STATUS_SUBMITTED,
@@ -16,6 +17,7 @@ from analytics.models import (
     ObservationQuestionSet,
 )
 from analytics.services.observation_service import create_coach_assessment_observation
+from analytics.services.permissions import can_evaluate_player, evaluation_perspective_for_user
 from analytics.services.question_service import get_active_questions, get_coach_assessment_type, get_question_set_for_cycle
 from players.models import Player
 
@@ -25,6 +27,8 @@ class PlayerAssessmentStatus:
     player: Player
     observation: Observation | None
     status: str
+    evaluation_perspective: str = ""
+    evaluation_perspective_label: str = ""
 
 
 def get_active_coach_assessment_cycle(cycle_id: int | None = None) -> EvaluationCycle | None:
@@ -45,7 +49,13 @@ def list_players_for_assessment(query: str = "", division: str = "", team: str =
     return players
 
 
-def get_existing_coach_assessment(player: Player, cycle: EvaluationCycle, evaluator) -> Observation | None:
+def get_existing_coach_assessment(
+    player: Player,
+    cycle: EvaluationCycle,
+    evaluator,
+    evaluation_perspective: str | None = None,
+) -> Observation | None:
+    evaluation_perspective = evaluation_perspective or evaluation_perspective_for_user(evaluator, player)
     return (
         Observation.objects.select_related("player", "evaluation_cycle", "question_set", "evaluator", "evaluator_role")
         .filter(
@@ -53,6 +63,7 @@ def get_existing_coach_assessment(player: Player, cycle: EvaluationCycle, evalua
             evaluation_cycle=cycle,
             observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
             evaluator=evaluator,
+            evaluation_perspective=evaluation_perspective,
         )
         .first()
     )
@@ -60,13 +71,15 @@ def get_existing_coach_assessment(player: Player, cycle: EvaluationCycle, evalua
 
 @transaction.atomic
 def get_or_create_draft_coach_assessment(player: Player, cycle: EvaluationCycle, evaluator) -> Observation:
-    existing = get_existing_coach_assessment(player, cycle, evaluator)
+    evaluation_perspective = evaluation_perspective_for_user(evaluator, player)
+    existing = get_existing_coach_assessment(player, cycle, evaluator, evaluation_perspective=evaluation_perspective)
     if existing:
         return existing
     result = create_coach_assessment_observation(
         player=player,
         evaluation_cycle=cycle,
         evaluator=evaluator,
+        evaluation_perspective=evaluation_perspective,
         question_set=get_question_set_for_cycle(cycle, get_coach_assessment_type()),
         status=OBSERVATION_STATUS_DRAFT,
     )
@@ -74,19 +87,34 @@ def get_or_create_draft_coach_assessment(player: Player, cycle: EvaluationCycle,
 
 
 def assessment_status_for_players(players, cycle: EvaluationCycle, evaluator) -> list[PlayerAssessmentStatus]:
+    player_list = list(players)
     observations = {
-        observation.player_id: observation
+        (observation.player_id, observation.evaluation_perspective): observation
         for observation in Observation.objects.filter(
-            player__in=players,
+            player__in=player_list,
             evaluation_cycle=cycle,
             observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
             evaluator=evaluator,
         )
     }
     statuses = []
-    for player in players:
-        observation = observations.get(player.id)
-        statuses.append(PlayerAssessmentStatus(player=player, observation=observation, status=observation.status if observation else "not_started"))
+    for player in player_list:
+        perspective = ""
+        label = ""
+        observation = None
+        if can_evaluate_player(evaluator, player):
+            perspective = evaluation_perspective_for_user(evaluator, player)
+            label = EVALUATION_PERSPECTIVE_LABELS.get(perspective, "Evaluation")
+            observation = observations.get((player.id, perspective))
+        statuses.append(
+            PlayerAssessmentStatus(
+                player=player,
+                observation=observation,
+                status=observation.status if observation else "not_started",
+                evaluation_perspective=perspective,
+                evaluation_perspective_label=label,
+            )
+        )
     return statuses
 
 
diff --git a/analytics/services/evaluation_access_service.py b/analytics/services/evaluation_access_service.py
index 8564ea9..d59c26a 100644
--- a/analytics/services/evaluation_access_service.py
+++ b/analytics/services/evaluation_access_service.py
@@ -34,6 +34,7 @@ class EvaluationTargetStatus:
     observation: Observation | None
     status: str
     can_evaluate: bool
+    evaluation_perspective_label: str = ""
 
 
 @dataclass(frozen=True)
@@ -49,6 +50,7 @@ class EvaluationTargetList:
 class MyEvaluationSummary:
     observation_id: int
     player: Player
+    evaluation_perspective_label: str
     evaluator_role_name: str
     submitted_at: object
     cycle_name: str
@@ -66,6 +68,7 @@ class MyEvaluationQuestionResponse:
 class MyEvaluationDetail:
     observation_id: int
     player: Player
+    evaluation_perspective_label: str
     evaluator_role_name: str
     submitted_at: object
     cycle_name: str
@@ -94,6 +97,7 @@ def get_evaluation_target_list(user, params) -> EvaluationTargetList:
             observation=statuses_by_player_id[player.id].observation,
             status=statuses_by_player_id[player.id].status,
             can_evaluate=can_evaluate_player(user, player),
+            evaluation_perspective_label=statuses_by_player_id[player.id].evaluation_perspective_label,
         )
         for player in players
     ]
@@ -152,6 +156,7 @@ def get_my_evaluations(user, player: Player | None = None) -> tuple[list[Player]
         MyEvaluationSummary(
             observation_id=observation.id,
             player=observation.player,
+            evaluation_perspective_label=observation.evaluation_perspective_label,
             evaluator_role_name=observation.evaluator_role_name or "Evaluator",
             submitted_at=observation.submitted_at,
             cycle_name=observation.evaluation_cycle.name,
@@ -185,6 +190,7 @@ def get_my_evaluation_detail(user, observation_id: int) -> MyEvaluationDetail:
     return MyEvaluationDetail(
         observation_id=observation.id,
         player=observation.player,
+        evaluation_perspective_label=observation.evaluation_perspective_label,
         evaluator_role_name=observation.evaluator_role_name or "Evaluator",
         submitted_at=observation.submitted_at,
         cycle_name=observation.evaluation_cycle.name,
diff --git a/analytics/services/evaluation_review_service.py b/analytics/services/evaluation_review_service.py
index 2759cb6..4a89668 100644
--- a/analytics/services/evaluation_review_service.py
+++ b/analytics/services/evaluation_review_service.py
@@ -7,6 +7,7 @@ from django.db.models import Q
 from django.utils.dateparse import parse_date
 
 from analytics.models import (
+    EVALUATION_PERSPECTIVE_CHOICES,
     OBSERVATION_STATUS_SUBMITTED,
     OBSERVATION_TYPE_COACH_ASSESSMENT,
     EvaluationCycle,
@@ -22,6 +23,7 @@ class EvaluationReviewFilters:
     player: str = ""
     evaluator: str = ""
     evaluator_role: str = ""
+    perspective: str = ""
     team: str = ""
     division: str = ""
     cycle: str = ""
@@ -37,6 +39,7 @@ class EvaluationReviewRow:
     player_division: str
     evaluator_name: str
     evaluator_role_name: str
+    evaluation_perspective_label: str
     cycle_name: str
     submitted_at: object
 
@@ -57,6 +60,7 @@ class EvaluationReviewDetail:
     player_division: str
     evaluator_name: str
     evaluator_role_name: str
+    evaluation_perspective_label: str
     cycle_name: str
     submitted_at: object
     responses: list[EvaluationReviewQuestionResponse]
@@ -69,6 +73,7 @@ class EvaluationReviewList:
     total_count: int
     cycles: object
     evaluator_roles: object
+    perspective_choices: object
 
 
 def parse_evaluation_review_filters(params) -> EvaluationReviewFilters:
@@ -77,6 +82,7 @@ def parse_evaluation_review_filters(params) -> EvaluationReviewFilters:
         player=(params.get("player") or "").strip(),
         evaluator=(params.get("evaluator") or "").strip(),
         evaluator_role=(params.get("evaluator_role") or "").strip(),
+        perspective=(params.get("perspective") or "").strip(),
         team=(params.get("team") or "").strip(),
         division=(params.get("division") or "").strip(),
         cycle=(params.get("cycle") or "").strip(),
@@ -118,6 +124,8 @@ def submitted_evaluation_queryset(filters: EvaluationReviewFilters | None = None
             queryset = queryset.filter(evaluator__username__icontains=filters.evaluator)
     if filters.evaluator_role:
         queryset = queryset.filter(evaluator_role_key=filters.evaluator_role)
+    if filters.perspective:
+        queryset = queryset.filter(evaluation_perspective=filters.perspective)
     if filters.team:
         queryset = queryset.filter(player__team_name__icontains=filters.team)
     if filters.division:
@@ -148,6 +156,7 @@ def get_evaluation_review_list(user, params) -> EvaluationReviewList:
             player_division=observation.player.division,
             evaluator_name=_display_user(observation.evaluator),
             evaluator_role_name=observation.evaluator_role_name or "Evaluator",
+            evaluation_perspective_label=observation.evaluation_perspective_label,
             cycle_name=observation.evaluation_cycle.name,
             submitted_at=observation.submitted_at,
         )
@@ -159,6 +168,7 @@ def get_evaluation_review_list(user, params) -> EvaluationReviewList:
         total_count=len(rows),
         cycles=EvaluationCycle.objects.filter(is_active=True).order_by("-starts_on", "-created_at", "name"),
         evaluator_roles=EvaluatorRole.objects.filter(is_active=True).order_by("name"),
+        perspective_choices=EVALUATION_PERSPECTIVE_CHOICES,
     )
 
 
@@ -186,6 +196,7 @@ def get_evaluation_review_detail(user, observation_id: int) -> EvaluationReviewD
         player_division=observation.player.division,
         evaluator_name=_display_user(observation.evaluator),
         evaluator_role_name=observation.evaluator_role_name or "Evaluator",
+        evaluation_perspective_label=observation.evaluation_perspective_label,
         cycle_name=observation.evaluation_cycle.name,
         submitted_at=observation.submitted_at,
         responses=responses,
diff --git a/analytics/services/observation_service.py b/analytics/services/observation_service.py
index 3b2dbd6..ca6dfb8 100644
--- a/analytics/services/observation_service.py
+++ b/analytics/services/observation_service.py
@@ -9,6 +9,8 @@ from django.db import IntegrityError, transaction
 from django.utils import timezone
 
 from analytics.models import (
+    EVALUATION_PERSPECTIVE_GUEST,
+    EVALUATION_PERSPECTIVE_SELF,
     OBSERVATION_STATUS_DRAFT,
     OBSERVATION_STATUS_SUBMITTED,
     OBSERVATION_TYPE_COACH_ASSESSMENT,
@@ -30,7 +32,7 @@ from analytics.services.question_service import (
     get_default_coach_assessment_question_set,
     get_question_set_for_cycle,
 )
-from analytics.services.permissions import can_evaluate_player, evaluator_role_for_user
+from analytics.services.permissions import can_evaluate_player, evaluation_perspective_for_user, evaluator_role_for_user
 from players.models import Player
 
 
@@ -54,6 +56,7 @@ def _validate_unique_coach_assessment(
     evaluation_cycle: EvaluationCycle,
     observation_type: ObservationType,
     evaluator,
+    evaluation_perspective: str,
     exclude_observation: Observation | None = None,
 ) -> None:
     if observation_type.key != OBSERVATION_TYPE_COACH_ASSESSMENT or evaluator is None:
@@ -63,11 +66,23 @@ def _validate_unique_coach_assessment(
         evaluation_cycle=evaluation_cycle,
         observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
         evaluator=evaluator,
+        evaluation_perspective=evaluation_perspective,
     )
     if exclude_observation:
         queryset = queryset.exclude(pk=exclude_observation.pk)
     if queryset.exists():
         raise ValidationError("This evaluator already has a coach assessment for this player and evaluation cycle.")
+    if evaluation_perspective == EVALUATION_PERSPECTIVE_SELF:
+        self_queryset = Observation.objects.filter(
+            player=player,
+            evaluation_cycle=evaluation_cycle,
+            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
+            evaluation_perspective=EVALUATION_PERSPECTIVE_SELF,
+        )
+        if exclude_observation:
+            self_queryset = self_queryset.exclude(pk=exclude_observation.pk)
+        if self_queryset.exists():
+            raise ValidationError("This player already has a self evaluation for this evaluation cycle.")
 
 
 def _coerce_rating(value) -> Decimal:
@@ -122,6 +137,7 @@ def create_observation(
     source: ObservationSource,
     evaluator=None,
     evaluator_role: EvaluatorRole | None = None,
+    evaluation_perspective: str | None = None,
     status: str = OBSERVATION_STATUS_DRAFT,
     notes: str = "",
     source_metadata: dict[str, Any] | None = None,
@@ -133,11 +149,15 @@ def create_observation(
         if not can_evaluate_player(evaluator, player):
             raise ValidationError("This evaluator cannot evaluate this player.")
         evaluator_role = evaluator_role or evaluator_role_for_user(evaluator)
+        evaluation_perspective = evaluation_perspective or evaluation_perspective_for_user(evaluator, player)
+    else:
+        evaluation_perspective = evaluation_perspective or EVALUATION_PERSPECTIVE_GUEST
     _validate_unique_coach_assessment(
         player=player,
         evaluation_cycle=evaluation_cycle,
         observation_type=observation_type,
         evaluator=evaluator,
+        evaluation_perspective=evaluation_perspective,
     )
     observation = Observation(
         player=player,
@@ -147,6 +167,7 @@ def create_observation(
         question_set=question_set,
         source=source,
         evaluator=evaluator,
+        evaluation_perspective=evaluation_perspective,
         status=status,
         notes=notes,
         source_metadata=source_metadata or {},
@@ -169,6 +190,7 @@ def create_coach_assessment_observation(
     evaluation_cycle: EvaluationCycle,
     evaluator,
     evaluator_role: EvaluatorRole | None = None,
+    evaluation_perspective: str | None = None,
     source: ObservationSource | None = None,
     question_set: ObservationQuestionSet | None = None,
     status: str = OBSERVATION_STATUS_DRAFT,
@@ -184,6 +206,7 @@ def create_coach_assessment_observation(
     question_set = question_set or get_question_set_for_cycle(evaluation_cycle, observation_type)
     source = source or ObservationSource.objects.get(key=SOURCE_COACH)
     evaluator_role = evaluator_role or evaluator_role_for_user(evaluator)
+    evaluation_perspective = evaluation_perspective or evaluation_perspective_for_user(evaluator, player)
     observation = create_observation(
         player=player,
         evaluation_cycle=evaluation_cycle,
@@ -192,6 +215,7 @@ def create_coach_assessment_observation(
         source=source,
         evaluator=evaluator,
         evaluator_role=evaluator_role,
+        evaluation_perspective=evaluation_perspective,
         status=status,
         notes=notes,
         source_metadata=source_metadata,
@@ -259,7 +283,20 @@ def validate_required_responses(observation: Observation) -> None:
 @transaction.atomic
 def submit_observation(observation: Observation, actor=None) -> Observation:
     """Mark an observation submitted."""
-    locked_observation = Observation.objects.select_for_update().get(pk=observation.pk)
+    locked_observation = (
+        Observation.objects.select_for_update()
+        .select_related("observation_type", "evaluation_cycle", "player", "evaluator")
+        .get(pk=observation.pk)
+    )
+    if locked_observation.observation_type:
+        _validate_unique_coach_assessment(
+            player=locked_observation.player,
+            evaluation_cycle=locked_observation.evaluation_cycle,
+            observation_type=locked_observation.observation_type,
+            evaluator=locked_observation.evaluator,
+            evaluation_perspective=locked_observation.evaluation_perspective,
+            exclude_observation=locked_observation,
+        )
     validate_required_responses(locked_observation)
     locked_observation.status = OBSERVATION_STATUS_SUBMITTED
     locked_observation.submitted_at = timezone.now()
diff --git a/analytics/services/permissions.py b/analytics/services/permissions.py
index 7153514..66867c2 100644
--- a/analytics/services/permissions.py
+++ b/analytics/services/permissions.py
@@ -1,9 +1,19 @@
 from django.core.exceptions import ValidationError
 
 from accounts.models import AccountRole
-from accounts.services.link_service import get_self_linked_players, is_player_self
+from accounts.services.link_service import get_self_linked_players, has_self_link, is_player_self
 from accounts.services.role_service import role_for_user, role_label
-from analytics.models import OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED, OBSERVATION_STATUS_SUBMITTED, EvaluatorRole
+from analytics.models import (
+    EVALUATION_PERSPECTIVE_COACH,
+    EVALUATION_PERSPECTIVE_GUEST,
+    EVALUATION_PERSPECTIVE_PEER,
+    EVALUATION_PERSPECTIVE_SELF,
+    EVALUATION_PERSPECTIVE_STAFF,
+    OBSERVATION_STATUS_DRAFT,
+    OBSERVATION_STATUS_REOPENED,
+    OBSERVATION_STATUS_SUBMITTED,
+    EvaluatorRole,
+)
 
 
 ACCOUNT_ROLE_TO_EVALUATOR_ROLE = {
@@ -24,19 +34,46 @@ def can_submit_coach_assessment(user) -> bool:
 def can_submit_evaluation(user, target_player=None) -> bool:
     if not user or not user.is_authenticated:
         return False
+    if target_player is not None and not getattr(target_player, "is_active", False):
+        return False
     if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
-        return not (target_player is not None and is_player_self(user, target_player))
+        return True
 
     account_role = role_for_user(user)
     if account_role not in EVALUATION_SUBMITTER_ROLES:
         return False
-    if target_player is not None and is_player_self(user, target_player):
-        return False
     return True
 
 
 def can_evaluate_player(user, target_player) -> bool:
-    return bool(target_player and can_submit_evaluation(user, target_player=target_player))
+    if not target_player or not can_submit_evaluation(user, target_player=target_player):
+        return False
+    if role_for_user(user) == AccountRole.PLAYER and not is_player_self(user, target_player):
+        return not has_self_link(user, target_player, active_only=False)
+    return True
+
+
+def evaluation_perspective_for_user(user, target_player) -> str:
+    """Return the server-derived evaluation perspective for this submission."""
+    if not can_submit_evaluation(user, target_player=target_player):
+        raise ValidationError("This account cannot submit an evaluation for this player.")
+    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
+        return EVALUATION_PERSPECTIVE_STAFF
+
+    account_role = role_for_user(user)
+    if account_role == AccountRole.PLAYER:
+        if is_player_self(user, target_player):
+            return EVALUATION_PERSPECTIVE_SELF
+        if has_self_link(user, target_player, active_only=False):
+            raise ValidationError("An active self player link is required to submit a self evaluation.")
+        return EVALUATION_PERSPECTIVE_PEER
+    if account_role == AccountRole.COACH:
+        return EVALUATION_PERSPECTIVE_COACH
+    if account_role == AccountRole.STAFF or account_role == AccountRole.ADMIN:
+        return EVALUATION_PERSPECTIVE_STAFF
+    if account_role == AccountRole.GUEST_EVALUATOR:
+        return EVALUATION_PERSPECTIVE_GUEST
+    raise ValidationError("This account role cannot submit evaluations.")
 
 
 def evaluator_role_for_user(user) -> EvaluatorRole:
diff --git a/analytics/templates/analytics/assessment_detail.html b/analytics/templates/analytics/assessment_detail.html
index 9ccbf5b..6a92a16 100644
--- a/analytics/templates/analytics/assessment_detail.html
+++ b/analytics/templates/analytics/assessment_detail.html
@@ -6,6 +6,7 @@
 {% block analytics_content %}
 <article class="pdp-card">
     <h2>Assessment</h2>
+    <p>Type: {{ observation.evaluation_perspective_label }}</p>
     <p>Evaluator: {{ observation.evaluator }} · Role: {{ observation.evaluator_role_name }}</p>
     {% if observation.submitted_at %}<p>Submitted: {{ observation.submitted_at }}</p>{% endif %}
     {% for group in question_groups %}
diff --git a/analytics/templates/analytics/assessment_form.html b/analytics/templates/analytics/assessment_form.html
index ebc8d8d..241887d 100644
--- a/analytics/templates/analytics/assessment_form.html
+++ b/analytics/templates/analytics/assessment_form.html
@@ -6,6 +6,7 @@
 {% block analytics_content %}
 <article class="pdp-card pdp-card--form">
     <h2>Coach Assessment</h2>
+    <p>{{ observation.evaluation_perspective_label }}</p>
     {% if question_set.rubric.labels %}
         <p>
             {% for value, label in question_set.rubric.labels.items %}
diff --git a/analytics/templates/analytics/assessment_list.html b/analytics/templates/analytics/assessment_list.html
index a85deac..e07c226 100644
--- a/analytics/templates/analytics/assessment_list.html
+++ b/analytics/templates/analytics/assessment_list.html
@@ -32,6 +32,7 @@
                         <th>Player</th>
                         <th>Division</th>
                         <th>Team</th>
+                        <th>Type</th>
                         <th>Status</th>
                         <th>Action</th>
                     </tr>
@@ -42,6 +43,7 @@
                             <td>{{ item.player.display_name }}</td>
                             <td>{{ item.player.division }}</td>
                             <td>{{ item.player.team_name }}</td>
+                            <td>{{ item.evaluation_perspective_label }}</td>
                             <td>{% include "analytics/_assessment_status_badge.html" with status=item.status %}</td>
                             <td>
                                 {% if item.observation and item.status == "submitted" %}
@@ -54,7 +56,7 @@
                             </td>
                         </tr>
                     {% empty %}
-                        <tr><td colspan="5">No active players found.</td></tr>
+                        <tr><td colspan="6">No active players found.</td></tr>
                     {% endfor %}
                 </tbody>
             </table>
diff --git a/analytics/templates/analytics/evaluation_form.html b/analytics/templates/analytics/evaluation_form.html
index 46ca022..7bd2a48 100644
--- a/analytics/templates/analytics/evaluation_form.html
+++ b/analytics/templates/analytics/evaluation_form.html
@@ -6,6 +6,7 @@
 {% block analytics_content %}
 <article class="pdp-card pdp-card--form">
     <h2>Evaluation</h2>
+    <p>{{ observation.evaluation_perspective_label }}</p>
     {% if question_set.rubric.labels %}
         <p>
             {% for value, label in question_set.rubric.labels.items %}
diff --git a/analytics/templates/analytics/evaluation_list.html b/analytics/templates/analytics/evaluation_list.html
index 75af0b9..77210fe 100644
--- a/analytics/templates/analytics/evaluation_list.html
+++ b/analytics/templates/analytics/evaluation_list.html
@@ -32,6 +32,7 @@
                         <th>Player</th>
                         <th>Division</th>
                         <th>Team</th>
+                        <th>Type</th>
                         <th>My submission</th>
                         <th>Action</th>
                     </tr>
@@ -42,10 +43,11 @@
                             <td>{{ item.player.display_name }}</td>
                             <td>{{ item.player.division }}</td>
                             <td>{{ item.player.team_name }}</td>
+                            <td>{{ item.evaluation_perspective_label }}</td>
                             <td>{% include "analytics/_assessment_status_badge.html" with status=item.status %}</td>
                             <td>
                                 {% if not item.can_evaluate %}
-                                    <span class="pdp-badge pdp-badge--muted">Self-evaluation blocked</span>
+                                    <span class="pdp-badge pdp-badge--muted">Unavailable</span>
                                 {% elif item.observation and item.status == "submitted" %}
                                     <a class="button button--ghost" href="{% url 'analytics:assessment-detail' observation_id=item.observation.id %}">View My Submission</a>
                                 {% elif item.observation %}
@@ -56,7 +58,7 @@
                             </td>
                         </tr>
                     {% empty %}
-                        <tr><td colspan="5">No active players found.</td></tr>
+                        <tr><td colspan="6">No active players found.</td></tr>
                     {% endfor %}
                 </tbody>
             </table>
diff --git a/analytics/templates/analytics/evaluation_review_detail.html b/analytics/templates/analytics/evaluation_review_detail.html
index 960b529..0280bab 100644
--- a/analytics/templates/analytics/evaluation_review_detail.html
+++ b/analytics/templates/analytics/evaluation_review_detail.html
@@ -17,6 +17,8 @@
         <dd>{{ detail.evaluator_name }}</dd>
         <dt>Evaluator Role</dt>
         <dd>{{ detail.evaluator_role_name }}</dd>
+        <dt>Type</dt>
+        <dd>{{ detail.evaluation_perspective_label }}</dd>
         <dt>Cycle</dt>
         <dd>{{ detail.cycle_name }}</dd>
         <dt>Submitted</dt>
diff --git a/analytics/templates/analytics/evaluation_review_list.html b/analytics/templates/analytics/evaluation_review_list.html
index 7791e24..8ca8b92 100644
--- a/analytics/templates/analytics/evaluation_review_list.html
+++ b/analytics/templates/analytics/evaluation_review_list.html
@@ -28,6 +28,15 @@
                 {% endfor %}
             </select>
         </label>
+        <label>
+            Type
+            <select name="perspective">
+                <option value="">All</option>
+                {% for value, label in perspective_choices %}
+                    <option value="{{ value }}" {% if filters.perspective == value %}selected{% endif %}>{{ label }}</option>
+                {% endfor %}
+            </select>
+        </label>
         <label>
             Team
             <input type="text" name="team" value="{{ filters.team }}">
@@ -65,6 +74,7 @@
                     <th>Division</th>
                     <th>Evaluator</th>
                     <th>Role</th>
+                    <th>Type</th>
                     <th>Cycle</th>
                     <th>Submitted</th>
                     <th></th>
@@ -78,12 +88,13 @@
                         <td>{{ row.player_division }}</td>
                         <td>{{ row.evaluator_name }}</td>
                         <td>{{ row.evaluator_role_name }}</td>
+                        <td>{{ row.evaluation_perspective_label }}</td>
                         <td>{{ row.cycle_name }}</td>
                         <td>{{ row.submitted_at|date:"M j, Y" }}</td>
                         <td><a class="button button--ghost" href="{% url 'analytics:evaluation-review-detail' observation_id=row.observation_id %}">Review</a></td>
                     </tr>
                 {% empty %}
-                    <tr><td colspan="8">No submitted evaluations found.</td></tr>
+                    <tr><td colspan="9">No submitted evaluations found.</td></tr>
                 {% endfor %}
             </tbody>
         </table>
diff --git a/analytics/templates/analytics/my_evaluation_detail.html b/analytics/templates/analytics/my_evaluation_detail.html
index abf1909..cfbb502 100644
--- a/analytics/templates/analytics/my_evaluation_detail.html
+++ b/analytics/templates/analytics/my_evaluation_detail.html
@@ -9,6 +9,8 @@
     <dl class="pdp-definition-list">
         <dt>Player</dt>
         <dd>{{ detail.player.display_name }}</dd>
+        <dt>Type</dt>
+        <dd>{{ detail.evaluation_perspective_label }}</dd>
         <dt>Evaluator Role</dt>
         <dd>{{ detail.evaluator_role_name }}</dd>
         <dt>Submitted</dt>
diff --git a/analytics/templates/analytics/my_evaluations.html b/analytics/templates/analytics/my_evaluations.html
index 2dd2921..d27f1c4 100644
--- a/analytics/templates/analytics/my_evaluations.html
+++ b/analytics/templates/analytics/my_evaluations.html
@@ -25,6 +25,7 @@
                     <tr>
                         <th>Player</th>
                         <th>Cycle</th>
+                        <th>Type</th>
                         <th>Evaluator Role</th>
                         <th>Submitted</th>
                         <th>Action</th>
@@ -35,12 +36,13 @@
                         <tr>
                             <td>{{ item.player.display_name }}</td>
                             <td>{{ item.cycle_name }}</td>
+                            <td>{{ item.evaluation_perspective_label }}</td>
                             <td>{{ item.evaluator_role_name }}</td>
                             <td>{{ item.submitted_at|date:"M j, Y" }}</td>
                             <td><a class="button button--ghost" href="{% url 'analytics:my-evaluation-detail' observation_id=item.observation_id %}">View Evaluation</a></td>
                         </tr>
                     {% empty %}
-                        <tr><td colspan="5">No submitted evaluations are available yet.</td></tr>
+                        <tr><td colspan="6">No submitted evaluations are available yet.</td></tr>
                     {% endfor %}
                 </tbody>
             </table>
diff --git a/analytics/templates/analytics/observation_review_list.html b/analytics/templates/analytics/observation_review_list.html
index e3fdbd5..d2b3d69 100644
--- a/analytics/templates/analytics/observation_review_list.html
+++ b/analytics/templates/analytics/observation_review_list.html
@@ -29,6 +29,7 @@
                     <th>Player</th>
                     <th>Cycle</th>
                     <th>Evaluator</th>
+                    <th>Type</th>
                     <th>Status</th>
                     <th>Submitted</th>
                     <th></th>
@@ -40,12 +41,13 @@
                         <td>{{ observation.player.display_name }}</td>
                         <td>{{ observation.evaluation_cycle.name }}</td>
                         <td>{{ observation.evaluator }}</td>
+                        <td>{{ observation.evaluation_perspective_label }}</td>
                         <td>{{ observation.get_status_display }}</td>
                         <td>{{ observation.submitted_at|default:"" }}</td>
                         <td><a class="button button--ghost" href="{% url 'analytics:observation-review-detail' observation_id=observation.id %}">Review</a></td>
                     </tr>
                 {% empty %}
-                    <tr><td colspan="6">No observations found.</td></tr>
+                    <tr><td colspan="7">No observations found.</td></tr>
                 {% endfor %}
             </tbody>
         </table>
diff --git a/analytics/tests.py b/analytics/tests.py
index 32dff4a..6a43ddb 100644
--- a/analytics/tests.py
+++ b/analytics/tests.py
@@ -15,6 +15,11 @@ from accounts.models import AccountRole, UserPlayerRelationship
 from accounts.services.link_service import activate_link, deactivate_link, link_user_to_player
 from accounts.services.profile_service import set_account_role
 from analytics.models import (
+    EVALUATION_PERSPECTIVE_COACH,
+    EVALUATION_PERSPECTIVE_GUEST,
+    EVALUATION_PERSPECTIVE_PEER,
+    EVALUATION_PERSPECTIVE_SELF,
+    EVALUATION_PERSPECTIVE_STAFF,
     OBSERVATION_STATUS_DRAFT,
     OBSERVATION_STATUS_REOPENED,
     OBSERVATION_STATUS_SUBMITTED,
@@ -67,6 +72,7 @@ from analytics.services.permissions import (
     can_evaluate_player,
     can_submit_evaluation,
     can_view_own_evaluation_draft,
+    evaluation_perspective_for_user,
     evaluator_role_for_user,
 )
 from analytics.services.reporting_service import get_command_center_context
@@ -465,22 +471,38 @@ class AnalyticsObservationFoundationTests(TestCase):
         self.assertTrue(can_submit_evaluation(guest))
         self.assertFalse(can_submit_evaluation(parent))
 
-    def test_self_evaluation_is_blocked_by_active_self_link_only(self):
+    def test_self_evaluation_is_allowed_with_active_self_link_only(self):
         player_user = User.objects.create_user(username="selflinked", password="testpass")
         set_account_role(player_user, AccountRole.PLAYER)
         link = link_user_to_player(player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
 
-        self.assertFalse(can_evaluate_player(player_user, self.player))
+        self.assertTrue(can_evaluate_player(player_user, self.player))
         self.assertTrue(can_evaluate_player(player_user, self.other_player))
-        with self.assertRaises(ValidationError):
-            create_coach_assessment_observation(
-                player=self.player,
-                evaluation_cycle=self.cycle,
-                evaluator=player_user,
-            )
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=player_user,
+        )
+        self.assertEqual(result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF)
 
         deactivate_link(link)
-        self.assertTrue(can_evaluate_player(player_user, self.player))
+        self.assertFalse(can_evaluate_player(player_user, self.player))
+        with self.assertRaises(ValidationError):
+            evaluation_perspective_for_user(player_user, self.player)
+
+    def test_evaluation_perspective_is_server_derived_by_role(self):
+        users = [
+            (AccountRole.COACH, EVALUATION_PERSPECTIVE_COACH),
+            (AccountRole.PLAYER, EVALUATION_PERSPECTIVE_PEER),
+            (AccountRole.STAFF, EVALUATION_PERSPECTIVE_STAFF),
+            (AccountRole.ADMIN, EVALUATION_PERSPECTIVE_STAFF),
+            (AccountRole.GUEST_EVALUATOR, EVALUATION_PERSPECTIVE_GUEST),
+        ]
+        for account_role, expected_perspective in users:
+            with self.subTest(account_role=account_role):
+                evaluator = User.objects.create_user(username=f"perspective-{account_role}", password="testpass")
+                set_account_role(evaluator, account_role)
+                self.assertEqual(evaluation_perspective_for_user(evaluator, self.other_player), expected_perspective)
 
     def test_parent_role_cannot_create_observation(self):
         parent = User.objects.create_user(username="parent", password="testpass")
@@ -680,6 +702,46 @@ class AnalyticsObservationFoundationTests(TestCase):
                 evaluator=self.evaluator,
             )
 
+    def test_duplicate_self_evaluation_is_prevented_for_player_cycle(self):
+        first_player_user = User.objects.create_user(username="self-one", password="testpass")
+        second_player_user = User.objects.create_user(username="self-two", password="testpass")
+        set_account_role(first_player_user, AccountRole.PLAYER)
+        set_account_role(second_player_user, AccountRole.PLAYER)
+        link_user_to_player(first_player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
+        link_user_to_player(second_player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=False)
+
+        create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=first_player_user,
+        )
+
+        with self.assertRaises(ValidationError):
+            create_coach_assessment_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                evaluator=second_player_user,
+            )
+
+    def test_self_and_peer_evaluations_from_same_player_are_distinct(self):
+        player_user = User.objects.create_user(username="self-peer", password="testpass")
+        set_account_role(player_user, AccountRole.PLAYER)
+        link_user_to_player(player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
+
+        self_result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=player_user,
+        )
+        peer_result = create_coach_assessment_observation(
+            player=self.other_player,
+            evaluation_cycle=self.cycle,
+            evaluator=player_user,
+        )
+
+        self.assertEqual(self_result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF)
+        self.assertEqual(peer_result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER)
+
     def test_multiple_evaluators_can_assess_same_player_cycle(self):
         create_coach_assessment_observation(
             player=self.player,
@@ -1734,6 +1796,7 @@ class CoachAssessmentWorkflowTests(TestCase):
             responses={question: 4 for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)},
         )
         submit_observation(result.observation)
+        original_perspective = result.observation.evaluation_perspective
         self.client.force_login(self.staff)
 
         response = self.client.post(
@@ -1744,6 +1807,7 @@ class CoachAssessmentWorkflowTests(TestCase):
         result.observation.refresh_from_db()
         self.assertEqual(response.status_code, 302)
         self.assertEqual(result.observation.status, OBSERVATION_STATUS_REOPENED)
+        self.assertEqual(result.observation.evaluation_perspective, original_perspective)
 
 
 class EvaluationAccessSubmissionViewTests(TestCase):
@@ -1802,7 +1866,7 @@ class EvaluationAccessSubmissionViewTests(TestCase):
         self.client.force_login(self.parent)
         self.assertEqual(self.client.get(reverse("analytics:evaluation-list")).status_code, 403)
 
-    def test_evaluation_list_blocks_self_and_uses_evaluation_copy(self):
+    def test_evaluation_list_allows_self_and_uses_evaluation_copy(self):
         self.client.force_login(self.player_user)
 
         response = self.client.get(reverse("analytics:evaluation-list"), {"q": "Player"})
@@ -1810,7 +1874,8 @@ class EvaluationAccessSubmissionViewTests(TestCase):
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "Evaluate Player")
         self.assertContains(response, "My submission")
-        self.assertContains(response, "Self-evaluation blocked")
+        self.assertContains(response, "Self Evaluation")
+        self.assertContains(response, reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}))
         self.assertContains(response, reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
 
     def test_player_can_open_evaluation_form_for_another_player(self):
@@ -1822,16 +1887,19 @@ class EvaluationAccessSubmissionViewTests(TestCase):
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, f"Evaluate {self.target_player.display_name}")
         self.assertContains(response, "Submit Evaluation")
+        self.assertContains(response, "Peer Evaluation")
         self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
         self.assertEqual(observation.evaluator_role_key, ROLE_PLAYER)
+        self.assertEqual(observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER)
 
-    def test_player_cannot_evaluate_self_or_inactive_player(self):
+    def test_player_can_evaluate_self_but_not_inactive_player(self):
         self.client.force_login(self.player_user)
 
-        self.assertEqual(
-            self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id})).status_code,
-            403,
-        )
+        self_response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}))
+        self_observation = Observation.objects.get(player=self.self_player, evaluator=self.player_user)
+        self.assertEqual(self_response.status_code, 200)
+        self.assertContains(self_response, "Self Evaluation")
+        self.assertEqual(self_observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF)
         self.assertEqual(
             self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.inactive_player.id})).status_code,
             404,
@@ -1866,6 +1934,28 @@ class EvaluationAccessSubmissionViewTests(TestCase):
         self.assertEqual(response["Location"], reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
         self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
         self.assertEqual(observation.evaluator_role_key, ROLE_PLAYER)
+        self.assertEqual(observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER)
+
+    def test_player_self_evaluation_draft_resumes_and_submitted_duplicate_redirects(self):
+        self.client.force_login(self.player_user)
+        first_response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}))
+        second_response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}))
+        observation = Observation.objects.get(player=self.self_player, evaluator=self.player_user)
+
+        self.assertEqual(first_response.status_code, 200)
+        self.assertEqual(second_response.status_code, 200)
+        self.assertEqual(observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF)
+        self.assertEqual(Observation.objects.filter(player=self.self_player, evaluator=self.player_user).count(), 1)
+
+        data = {"action": "submit"}
+        data.update(self.response_payload())
+        self.client.post(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}), data)
+        response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}))
+        observation.refresh_from_db()
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
+        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
 
     def test_submitted_evaluation_detail_is_private_to_evaluator_and_staff(self):
         result = create_coach_assessment_observation(
@@ -2048,6 +2138,7 @@ class MyEvaluationsViewTests(TestCase):
         self.assertContains(response, self.player.display_name)
         self.assertContains(response, self.cycle.name)
         self.assertContains(response, "Coach")
+        self.assertContains(response, "Coach Evaluation")
         self.assertContains(response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
 
     def test_my_evaluation_detail_hides_evaluator_identity_and_shows_feedback(self):
@@ -2058,6 +2149,7 @@ class MyEvaluationsViewTests(TestCase):
 
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, self.player.display_name)
+        self.assertContains(response, "Coach Evaluation")
         self.assertContains(response, "Evaluator Role")
         self.assertContains(response, "Coach")
         self.assertContains(response, self.cycle.name)
@@ -2075,6 +2167,17 @@ class MyEvaluationsViewTests(TestCase):
         self.assertEqual(detail.observation_id, observation.id)
         self.assertFalse(hasattr(detail, "observation"))
 
+    def test_my_evaluations_show_self_label_without_external_identity(self):
+        self_observation = self.submitted_observation(player=self.player, evaluator=self.player_user, note="My reflection.")
+        self.client.force_login(self.player_user)
+
+        list_response = self.client.get(reverse("analytics:my-evaluations"))
+        detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": self_observation.id}))
+
+        self.assertContains(list_response, "Self Evaluation")
+        self.assertContains(detail_response, "Self Evaluation")
+        self.assertContains(detail_response, "My reflection.")
+
     def test_nonexistent_my_evaluation_detail_returns_404(self):
         self.client.force_login(self.player_user)
 
@@ -2343,6 +2446,8 @@ class EvaluationReviewViewTests(TestCase):
     def test_coach_can_review_all_submitted_evaluations(self):
         first = self.submitted_observation(player=self.player, evaluator=self.coach, note="First submitted.")
         second = self.submitted_observation(player=self.second_player, evaluator=self.second_coach, cycle=self.second_cycle, note="Second submitted.")
+        link_user_to_player(self.player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
+        self_observation = self.submitted_observation(player=self.player, evaluator=self.player_user, note="Self submitted.")
         self.client.force_login(self.coach)
 
         response = self.client.get(reverse("analytics:evaluation-review-list"))
@@ -2352,8 +2457,10 @@ class EvaluationReviewViewTests(TestCase):
         self.assertContains(response, self.second_player.display_name)
         self.assertContains(response, "Casey Coach")
         self.assertContains(response, "Sam Coach")
+        self.assertContains(response, "Self Evaluation")
         self.assertContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": first.id}))
         self.assertContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": second.id}))
+        self.assertContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": self_observation.id}))
         self.assertNotContains(response, self.coach.email)
 
     def test_coach_review_access_rules(self):
@@ -2380,6 +2487,8 @@ class EvaluationReviewViewTests(TestCase):
     def test_coach_review_filters_individually_and_in_combination(self):
         first = self.submitted_observation(player=self.player, evaluator=self.coach, note="Reds note.")
         second = self.submitted_observation(player=self.second_player, evaluator=self.second_coach, cycle=self.second_cycle, note="Blues note.")
+        link_user_to_player(self.player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
+        self_observation = self.submitted_observation(player=self.player, evaluator=self.player_user, note="Self note.")
         today = timezone.localdate().isoformat()
         self.client.force_login(self.coach)
 
@@ -2389,6 +2498,8 @@ class EvaluationReviewViewTests(TestCase):
             ({"evaluator": str(self.coach.id)}, first, second),
             ({"evaluator": "second-coach"}, second, first),
             ({"evaluator_role": ROLE_COACH}, first, None),
+            ({"perspective": EVALUATION_PERSPECTIVE_SELF}, self_observation, first),
+            ({"perspective": EVALUATION_PERSPECTIVE_COACH}, first, self_observation),
             ({"team": "Reds"}, first, second),
             ({"division": "15U"}, second, first),
             ({"cycle": str(self.second_cycle.id)}, second, first),
diff --git a/analytics/views.py b/analytics/views.py
index 9ae8b3d..11ae636 100644
--- a/analytics/views.py
+++ b/analytics/views.py
@@ -9,7 +9,7 @@ from django.views.generic import FormView, ListView, TemplateView, View
 
 from analytics.assessment_forms import CoachAssessmentForm
 from analytics.forms import PlayerImportMappingForm, PlayerImportUploadForm, parse_conflict_resolutions
-from analytics.models import OBSERVATION_STATUS_SUBMITTED, OBSERVATION_TYPE_COACH_ASSESSMENT, EvaluationCycle, Observation
+from analytics.models import EVALUATION_PERSPECTIVE_CHOICES, OBSERVATION_STATUS_SUBMITTED, OBSERVATION_TYPE_COACH_ASSESSMENT, EvaluationCycle, Observation
 from analytics.services.coach_assessment_service import (
     assessment_status_for_players,
     get_active_coach_assessment_cycle,
@@ -423,6 +423,7 @@ class EvaluationReviewListView(EvaluationReviewRequiredMixin, TemplateView):
                 "filters": review_list.filters,
                 "cycles": review_list.cycles,
                 "evaluator_roles": review_list.evaluator_roles,
+                "perspective_choices": review_list.perspective_choices,
                 "total_count": review_list.total_count,
             }
         )
@@ -585,7 +586,7 @@ class StaffObservationReviewListView(AnalyticsStaffRequiredMixin, ListView):
     paginate_by = 25
 
     def get_queryset(self):
-        queryset = Observation.objects.select_related("player", "evaluation_cycle", "observation_type", "evaluator", "source").filter(
+        queryset = Observation.objects.select_related("player", "evaluation_cycle", "observation_type", "evaluator", "evaluator_role", "source").filter(
             observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT
         )
         status = self.request.GET.get("status", "").strip()
@@ -606,6 +607,7 @@ class StaffObservationReviewListView(AnalyticsStaffRequiredMixin, ListView):
     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context["cycles"] = EvaluationCycle.objects.filter(is_active=True)
+        context["perspective_choices"] = EVALUATION_PERSPECTIVE_CHOICES
         return context
 
 
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index b6b4bf4..4e29c82 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -98,6 +98,7 @@ What it owns:
 - evaluation cycles
 - question sets and questions
 - evaluator snapshots
+- evaluation perspective snapshots
 - analytics metrics, timelines, comparisons, and reports
 
 What it must not own:
@@ -110,7 +111,7 @@ What it must not own:
 
 Current status:
 
-V1 complete. Implementation status records Phases 1-7 as complete. Evaluation Access V1 is complete and frozen for roster-based evaluation access, including coach import, player/coach evaluation submission, player "My Evaluations," and coach evaluation review/filtering.
+V1 complete. Implementation status records Phases 1-7 as complete. Evaluation Access V1 is complete and frozen for roster-based evaluation access, including coach import, player/coach evaluation submission, self-evaluation with explicit perspective labels, player "My Evaluations," and coach evaluation review/filtering.
 
 Documentation:
 
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 4b3a8ca..88bab1e 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -169,7 +169,7 @@ If your account was imported or reset, you may need to change your password befo
 
 ### Purpose
 
-Use this section when you have a player account and need to submit peer evaluations or view evaluations about yourself.
+Use this section when you have a player account and need to submit peer or self evaluations, or view evaluations about yourself.
 
 ### Where To Log In
 
@@ -189,7 +189,7 @@ If this is your first login, change your temporary password when prompted.
 
 1. Sign in.
 2. Change your password if required.
-3. Submit evaluations for players you know.
+3. Submit evaluations for players you know, including yourself when appropriate.
 4. View submitted evaluations about yourself from My Evaluations.
 5. Sign out when finished.
 
@@ -200,7 +200,7 @@ If this is your first login, change your temporary password when prompted.
 - `/accounts/profile/`
 - `/accounts/password/`
 
-Players cannot evaluate themselves in the current version.
+Player self-evaluations are allowed and are clearly labeled as Self Evaluation.
 
 ## Account Access
 
@@ -381,9 +381,10 @@ Parent accounts do not submit evaluations unless staff gives that user an evalua
 
 - Authenticated coaches, players, staff, and guest evaluators can evaluate players they know.
 - The player does not need to be on the evaluator's own team.
-- Players cannot evaluate themselves.
+- Players can evaluate themselves when their account is actively linked to their own player record.
+- Self evaluations are labeled Self Evaluation.
 - The system records who submitted the evaluation.
-- The evaluator's role/category is recorded for reporting and historical context.
+- The evaluator's role/category and evaluation type are recorded for reporting and historical context.
 - Submitted evaluations become part of the player's Analytics record.
 
 ### Ratings And Notes
@@ -443,7 +444,7 @@ Players, parents, and guest evaluators cannot access the review page.
 ### Typical Workflow
 
 1. Open `/analytics/evaluation-review/`.
-2. Filter by player, evaluator, evaluator role, team, division, cycle, or date.
+2. Filter by player, evaluator, evaluator role, evaluation type, team, division, cycle, or date.
 3. Open an evaluation detail.
 4. Use the information for discussion and decision support.
 
@@ -454,7 +455,7 @@ Players, parents, and guest evaluators cannot access the review page.
 
 Coach review is read-only. It shows submitted evaluations only. Coaches cannot reopen, edit, or delete submitted evaluations from this page.
 
-Coach review shows evaluator names and role/category. It does not show evaluator email addresses, passwords, import metadata, or unrelated account details.
+Coach review shows evaluator names, role/category, and evaluation type. It does not show evaluator email addresses, passwords, import metadata, or unrelated account details.
 
 ## Staff Analytics
 
@@ -728,15 +729,15 @@ Yes, if your account can submit evaluations and you know the player well enough
 
 ### Can I evaluate myself?
 
-No. Self-evaluation is blocked in the current version.
+Yes. If you have an active player account linked to your own player record, your own submission is labeled Self Evaluation.
 
 ### Is my role recorded when I submit an evaluation?
 
-Yes. The system records your evaluator identity and role/category for reporting and historical context.
+Yes. The system records your evaluator identity, role/category, and evaluation type for reporting and historical context.
 
 ### Can players see who evaluated them?
 
-No. Player-facing My Evaluations pages hide evaluator names, usernames, emails, and account details. Players may see evaluator role/category.
+No. Player-facing My Evaluations pages hide evaluator names, usernames, emails, and account details for external evaluations. Players may see evaluator role/category and evaluation type.
 
 ### Can coaches see all submitted evaluations?
 
diff --git a/docs/analytics/architecture/10_permissions.md b/docs/analytics/architecture/10_permissions.md
index e777dbc..11c163a 100644
--- a/docs/analytics/architecture/10_permissions.md
+++ b/docs/analytics/architecture/10_permissions.md
@@ -22,11 +22,17 @@ Coaches may edit their own draft/unsubmitted observations. Staff/admin users con
 
 Coaches do not manage player tags unless future permissions allow it.
 
-## Future Player And Parent Access
+## Player Access
 
-Future player and parent portals are supported by the long-term architecture but are not implemented in Version 1.
+Authenticated player users can submit evaluations for active players. When evaluating their own active self-linked player record, the submission is labeled Self Evaluation. When evaluating another player, the submission is labeled Peer Evaluation.
 
-Future permissions may allow players or parents to view selected timeline entries, reports, or development feedback. Do not implement those surfaces in Version 1.
+Players can view submitted evaluations about their own active self-linked player records through the player-facing My Evaluations pages. Player-facing result pages hide evaluator names, usernames, emails, and account metadata for external evaluations.
+
+## Future Parent Access
+
+Future parent portals are supported by the long-term architecture but are not implemented in Version 1.
+
+Future permissions may allow parents to view selected timeline entries, reports, or development feedback. Do not implement those surfaces in Version 1.
 
 ## Sensitive Data
 
diff --git a/docs/evaluations/implementation/engineering/evaluation_access_v1.md b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
index 7ce69b1..0ef52a6 100644
--- a/docs/evaluations/implementation/engineering/evaluation_access_v1.md
+++ b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
@@ -4,6 +4,8 @@ Status: COMPLETE and FROZEN.
 
 Frozen on: 2026-07-10.
 
+Self-Evaluation extension added on: 2026-07-11.
+
 ## 1. Goal
 
 Document the completed Platform V1 operational work needed for roster-based evaluations.
@@ -13,7 +15,7 @@ The target stopping point is:
 - players can be imported;
 - coaches can be imported;
 - coaches can evaluate players;
-- players can evaluate one another;
+- players can evaluate one another and themselves with explicit evaluation type labels;
 - players can view evaluations about themselves;
 - coaches can view and filter all evaluations.
 
@@ -51,12 +53,23 @@ These product and architecture decisions are recorded before implementation begi
 Decision:
 
 ```text
-Block self-evaluation for Evaluation Access V1.
+Originally block self-evaluation for Evaluation Access V1.
+```
+
+Rationale:
+
+The initial goal was coach and peer evaluation. Self-evaluation was deferred until it could be labeled and reported separately.
+
+Updated decision:
+
+```text
+Allow player self-evaluation when the evaluator has an active self link to the target player.
+Store the server-derived evaluation perspective snapshot on every observation.
 ```
 
 Rationale:
 
-The initial goal is coach and peer evaluation. Self-evaluation may be useful later, but it needs separate labeling and reporting to avoid confusing review results.
+The platform now supports separate `self`, `peer`, `coach`, `staff`, and `guest` perspectives. Self-evaluations are explicitly labeled as Self Evaluation, are distinct from peer evaluations, and require an active self link.
 
 ### Player-Facing Evaluator Visibility
 
@@ -466,30 +479,31 @@ Proposed flow:
 
 1. Player signs in.
 2. Player opens evaluation list/search.
-3. Player selects another active player.
+3. Player selects another active player, or their own linked player record for self evaluation.
 4. System opens or creates that evaluator's draft observation for the selected player and current cycle.
 5. Player completes ratings and notes.
 6. Player saves draft or submits.
-7. System records evaluator user and role snapshot as player.
+7. System records evaluator user, role snapshot as player, and evaluation perspective snapshot as `self` or `peer`.
 
 ### Self-Evaluation Rule
 
-Decision for Evaluation Access V1:
+Updated decision for Evaluation Access V1:
 
 ```text
-Block self-evaluation.
+Allow self-evaluation with explicit labels and perspective snapshots.
 ```
 
 Reasoning:
 
-- the target use case is peer and coach evaluation;
-- self-evaluations can be valuable but should have explicit labels and reporting treatment;
-- allowing them without UI explanation may confuse coaches reviewing results.
+- self-evaluations are valuable when clearly separated from peer, coach, staff, and guest evaluations;
+- the explicit `evaluation_perspective` snapshot prevents coaches from confusing self feedback with external evaluations;
+- the active self-link requirement prevents unrelated users from creating self-labeled records for another player.
 
 Implementation guidance:
 
-- add a permission/service check that blocks a user from evaluating a player linked to them by active primary or active `self` relationship;
-- if self-evaluation is later desired, make it an explicit cycle setting or observation metadata flag.
+- derive perspective server-side; do not accept a client-controlled perspective field;
+- allow self evaluation only when an active `self` relationship links the evaluator user to the target player;
+- keep self and peer duplicate rules distinct.
 
 ### Form Reuse
 
@@ -909,7 +923,7 @@ Purpose:
 
 Decisions recorded:
 
-- self-evaluation is blocked;
+- self-evaluation is allowed only through an active self link and is labeled separately;
 - player-facing results show evaluator role/category only, not evaluator names;
 - coach import avoids a persistent batch model in Phase 1 unless absolutely necessary;
 - coach-to-player links are not imported in Coach Import Phase 1;
@@ -1064,13 +1078,14 @@ Deliverables:
 - staff can submit;
 - guest evaluator can submit if authenticated;
 - role snapshot matches account profile role;
-- self-evaluation is blocked;
+- self-evaluation requires an active self link and stores `evaluation_perspective=self`;
 - coach review access does not grant Account Operations access;
 - player review access is limited to linked self player.
 
 ### Player Submission Tests
 
 - player can open evaluation form for another active player;
+- player can open evaluation form for their own active self-linked player record;
 - player cannot evaluate inactive player;
 - player cannot create duplicate evaluation for same player/cycle;
 - player can save draft;
@@ -1118,7 +1133,7 @@ Deliverables:
 - Coach review could accidentally grant staff-only abilities such as reopening observations.
 - Temporary passwords can leak if stored in summaries, logs, messages, or metadata.
 - Team and division filtering may become stale if player roster data is outdated.
-- Blocking self-evaluation may disappoint users who expect reflection workflows; future self-evaluation should be explicitly labeled and reported separately.
+- Self-evaluation must remain clearly labeled so coaches do not confuse it with external feedback.
 - No audit logging exists, so staff account operations and coach imports have limited historical operator visibility.
 
 ## 19. Open Questions
@@ -1149,8 +1164,8 @@ Evaluation Access V1 is complete when:
 - [x] imported coach accounts have role `coach`;
 - [x] temporary password behavior is safe and one-time;
 - [x] coaches can evaluate players;
-- [x] players can evaluate other players, with self-evaluation blocked;
-- [x] evaluator identity and role snapshots are correct;
+- [x] players can evaluate other players and themselves with explicit evaluation perspective labels;
+- [x] evaluator identity, role snapshots, and evaluation perspective snapshots are correct;
 - [x] players can view submitted evaluations about themselves only, with evaluator role/category but not evaluator names;
 - [x] coaches can view and filter all submitted evaluations;
 - [x] staff retains existing review and reopen capabilities;
@@ -1169,8 +1184,8 @@ The completed stopping point is:
 - coaches can be imported from CSV;
 - coaches can evaluate players;
 - players can evaluate other players;
-- self-evaluation is blocked;
-- evaluator identity and role snapshots are stored;
+- self-evaluation is allowed and explicitly labeled;
+- evaluator identity, role snapshots, and evaluation perspective snapshots are stored;
 - players can privately view submitted evaluations about themselves;
 - player-facing results hide evaluator identity and show evaluator role/category only;
 - coaches can view and filter all submitted evaluations;
@@ -1186,7 +1201,7 @@ Subsystem boundaries remain consistent with the Platform V1 architecture:
 - `drafts` remains separate and continues to own draft workflows.
 - `pdp` remains legacy/transitionary and was not migrated as part of Evaluation Access V1.
 
-No new models or migrations were required for Evaluation Access V1 after the existing Accounts, Players, and Analytics foundations.
+The Self-Evaluation extension added an Analytics migration for the `Observation.evaluation_perspective` snapshot and related uniqueness/index constraints.
 
 ## 24. Security And Privacy Assessment
 
@@ -1194,9 +1209,9 @@ Security and privacy posture:
 
 - unauthenticated users cannot submit or review evaluations;
 - parent accounts cannot submit evaluations by default;
-- player accounts can submit peer evaluations but cannot evaluate themselves;
+- player accounts can submit peer evaluations and self evaluations when an active self link exists;
 - players can view only submitted evaluations about active self-linked player records;
-- inactive self links and inactive players do not grant "My Evaluations" access;
+- inactive self links and inactive players do not grant self-evaluation or "My Evaluations" access;
 - player-facing result pages hide evaluator names, usernames, email addresses, and account metadata;
 - coach review exposes evaluator display names and role/category but not evaluator email, password state, import metadata, or account metadata;
 - guest evaluators can submit but cannot access coach review;
@@ -1220,8 +1235,8 @@ The implemented workflow supports:
 4. coaches and provisioned players complete first-login password changes when required;
 5. coaches submit evaluations;
 6. players submit peer evaluations;
-7. self-evaluation attempts are blocked;
-8. submitted evaluations store evaluator identity and role snapshots;
+7. players submit self evaluations when they have an active self link;
+8. submitted evaluations store evaluator identity, role snapshots, and evaluation perspective snapshots;
 9. players view submitted evaluations about themselves without seeing evaluator names;
 10. coaches view and filter all submitted evaluations;
 11. staff review and reopen remain available through the existing staff-only workflow.
@@ -1246,7 +1261,7 @@ Use this checklist for a manual production pilot:
 - [ ] Log in as a player and complete forced password change.
 - [ ] Submit an evaluation as a coach.
 - [ ] Submit a peer evaluation as a player.
-- [ ] Attempt self-evaluation as a player and confirm it is blocked.
+- [ ] Submit a self evaluation as a player and confirm it is labeled Self Evaluation.
 - [ ] View `/analytics/my/evaluations/` as a player.
 - [ ] Confirm evaluator identity is hidden from the player-facing result.
 - [ ] View `/analytics/evaluation-review/` as a coach.
@@ -1280,10 +1295,12 @@ Deferred work remains outside Evaluation Access V1:
 - recruiting;
 - new observation types;
 - PDP retirement;
-- self-evaluation workflows with separate labeling/reporting.
+- broader self-evaluation reporting beyond the current explicit perspective label and filters.
 
 ## 30. Freeze Declaration
 
 Evaluation Access V1 is COMPLETE and FROZEN as of 2026-07-10.
 
+The Self-Evaluation extension is complete as of 2026-07-11.
+
 Future changes should be planned as a new phase or version unless they are bug fixes, security fixes, documentation corrections, or operational support for the frozen V1 scope.
```

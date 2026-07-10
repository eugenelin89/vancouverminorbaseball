# Prompt 62 - Analytics

## Loop 1 Prompt Archive

Current terminal state: CONTINUE

Loop objective:

Implement Evaluation Access V1 Phase 5: Coach Evaluation Review and Filtering, then harden the new workflow enough to prove the Phase 5 acceptance criteria.

Current production-readiness gaps:

- Coach-facing all-submitted-evaluation review did not exist before this loop.
- Coach review filtering by target player, evaluator, evaluator role, team, division, cycle, and submitted date was not implemented before this loop.
- Coach review detail did not exist as a read-only coach-accessible surface before this loop.
- User manual still said coach all-evaluation review was future work before this loop.
- Evaluation Access plan did not yet mark Phase 5 implemented before this loop.

Concrete issues selected for this loop:

- Add Analytics-owned coach review permission helpers.
- Add Analytics-owned evaluation review service with filter parsing, submitted-only queryset, list read models, and detail read model.
- Add thin Analytics views and routes for coach review list/detail.
- Add server-rendered templates for list/detail.
- Keep staff review and reopen workflow separate.
- Add tests for access control, submitted-only visibility, filters, read-only behavior, and regressions.
- Update user-facing and engineering documentation for Phase 5.

Allowed changes:

- `analytics/services/permissions.py`
- new Analytics review service code
- `analytics/views.py`
- `analytics/urls.py`
- Analytics templates
- Analytics tests
- relevant documentation

Tests to add/run:

- `python manage.py test analytics`
- `python manage.py test accounts`
- full verification suite required by the user prompt before committing

Explicit non-goals:

- Do not implement Phase 6/freeze in this loop.
- Do not add models or migrations.
- Do not add coach-to-player links.
- Do not implement parent portal, coach portal, exports, charts, APIs, audit logging, or future observation types.

## Source Prompt

```text
You are implementing and production-hardening Evaluation Access V1 Phase 5:

Coach Evaluation Review and Filtering.

Use continuous loop engineering.

This is not a fixed-number loop.

Continue looping until the system reaches a valid terminal state.

==================================================
Terminal States
===============

Every loop must end in exactly one of these states:

CONTINUE

Verified issues or incomplete acceptance criteria remain, and the next loop can make concrete progress within approved scope.

PASS

All production-readiness acceptance criteria are satisfied, all required tests pass, documentation is current, commits are pushed, and the working tree is clean.

BLOCKED

A required fix needs one or more of:

* a product decision;
* a new model or migration not authorized by this prompt;
* external infrastructure;
* a security decision;
* expansion beyond Evaluation Access V1;
* destructive data migration;
* unresolved conflict with documented architecture.

NO_PROGRESS

Two consecutive completed loops:

* found no new concrete fix that advances an unsatisfied criterion; and
* still could not prove all production-readiness criteria.

Do not loop indefinitely without concrete progress.

Only state that Evaluation Access V1 is production-ready if the terminal state is PASS.

==================================================
Overall Goal
============

Reach the user’s production stopping point:

* players can be imported;
* coaches can be imported;
* coaches can evaluate players;
* players can evaluate other players;
* players can privately view submitted evaluations about themselves;
* coaches can view and filter all submitted evaluations;
* permissions and privacy are production-safe;
* documentation and the user manual are accurate;
* all required tests pass;
* Evaluation Access V1 can be declared complete and frozen.

Phases 0 through 4 already exist.

The remaining product feature is Phase 5:

Coach Review and Filtering.

After Phase 5 exists, continue looping through review, hardening, integration verification, documentation reconciliation, pilot-readiness assessment, and freeze preparation until PASS, BLOCKED, or NO_PROGRESS.

==================================================
Strict Scope
============

Allowed product work:

* Phase 5 coach review and filtering;
* Phase 5 review fixes;
* correctness fixes affecting Evaluation Access V1;
* security/privacy fixes;
* architecture fixes;
* performance fixes;
* UX consistency fixes;
* documentation fixes;
* tests;
* production-readiness hardening;
* final Evaluation Access V1 freeze documentation.

Do NOT implement unrelated future features.

Do NOT implement:

* audit logging;
* account merge;
* duplicate account resolution;
* coach-to-player roster assignment;
* parent import;
* parent portal;
* full coach portal;
* full player portal;
* email invitations;
* email verification;
* self-service password recovery;
* REST APIs;
* JavaScript frameworks;
* charts;
* exports;
* LeagueHub;
* video;
* recruiting;
* new observation types;
* account-management redesign;
* PDP retirement.

If production readiness genuinely requires one of these, stop with BLOCKED and explain why.

==================================================
Before Loop 1
=============

Read completely:

* AGENTS.md
* README.md
* docs/ARCHITECTURE.md
* docs/USER_MANUAL.md
* docs/evaluations/implementation/engineering/evaluation_access_v1.md
* docs/account_management/V1_SUMMARY.md
* docs/account_management/implementation/engineering/platform_v1_account_operations.md
* docs/analytics/architecture/
* docs/analytics/implementation/

Review implementation:

* accounts/
* analytics/
* players/
* drafts/
* pdp/

Review prompt history relevant to Evaluation Access V1:

* Phase 0 decisions
* Coach Import implementation and review
* Permission/role snapshots
* Player evaluation submission and review
* Player My Evaluations implementation and loop review

Inspect current Git status and recent commits before changing anything.

==================================================
Full Loop Workflow
==================

Every loop must complete ALL stages below.

Do not skip stages because the change appears small.

---

## Stage 1 — Reconcile Current State

At the start of every loop:

1. Read the current committed implementation.
2. Read current documentation.
3. Review previous loop report.
4. Run `git status`.
5. Confirm the working tree is clean before beginning.
6. Identify which production-readiness criteria remain unproven or unsatisfied.

Write a concise loop objective based on current evidence.

Do not reuse a stale objective from a previous loop.

---

## Stage 2 — Inspect

Inspect the complete end-to-end workflow:

1. Coach import
2. Coach login and forced password change
3. Player import/account provisioning
4. Player login and forced password change
5. Coach evaluation submission
6. Player peer evaluation submission
7. Self-evaluation blocking
8. Evaluator role snapshots
9. Evaluator viewing own submission
10. Player My Evaluations
11. Coach all-evaluation review
12. Coach review filtering
13. Staff review compatibility
14. Privacy and unauthorized URL access
15. Account/profile navigation
16. Documentation and user instructions

Do not inspect only files changed in the previous loop.

---

## Stage 3 — Identify Concrete Issues

Create an evidence-based issue list.

Each issue must include:

* observed behavior;
* expected behavior;
* file/service involved;
* acceptance criterion affected;
* severity;
* whether it is inside approved scope.

Do not add speculative refactoring tasks.

Do not change code merely for taste.

Prioritize:

1. security/privacy;
2. authorization;
3. data integrity;
4. correctness;
5. architecture;
6. production usability;
7. performance;
8. documentation;
9. minor UX consistency.

---

## Stage 4 — Plan This Loop

Create the next prompt archive for the loop before implementation, following AGENTS.md and the repository’s prompt-record convention.

The loop prompt must record:

* loop number;
* current terminal state: CONTINUE;
* current production-readiness gaps;
* concrete issues selected;
* exact allowed changes;
* tests to add;
* verification commands;
* explicit non-goals.

Do not use one giant original prompt as the archive for every loop.

Each loop gets its own prompt record reflecting the newly discovered state.

Use the correct next prompt number.

---

## Stage 5 — Implement

Fix only verified issues selected for this loop.

Keep these ownership boundaries:

accounts owns:

* login identity;
* account roles;
* passwords;
* user-player links;
* coach account import;
* account operations.

players owns:

* canonical player identity;
* player import and matching;
* player search primitives.

analytics owns:

* evaluation submission;
* evaluator role snapshots;
* evaluation permissions;
* player-safe result views;
* coach review and filtering;
* evaluation read models.

Views remain thin.

Templates do not own role or permission logic.

Cross-subsystem business rules flow through services.

Avoid new models and migrations unless already authorized.

If a model or migration becomes necessary, stop with BLOCKED.

---

## Stage 6 — Focused Tests

Add or update tests for every issue fixed.

Run focused tests for affected apps.

At minimum:

python manage.py test analytics
python manage.py test accounts

Also run another app’s tests when that loop changes or meaningfully touches its behavior.

Do not proceed if focused tests fail.

Fix the failure within the same loop if it is within scope.

---

## Stage 7 — Self-Review

Review the diff as a senior engineer.

Check:

* security;
* permissions;
* privacy;
* service ownership;
* dependency direction;
* transaction boundaries;
* query behavior;
* N+1 risks;
* data leakage;
* error handling;
* 403 versus 404 behavior;
* one-time password safety;
* role snapshots;
* active/inactive links;
* active/inactive players;
* duplicated logic;
* dead code;
* unused imports;
* template copy;
* test quality;
* documentation drift.

Run:

git diff --check

If the self-review finds a concrete issue, fix it before committing.

---

## Stage 8 — Update Documentation

Update documentation in every loop when behavior, status, risks, or production-readiness evidence changed.

Review and update only as needed:

* docs/USER_MANUAL.md
* docs/evaluations/implementation/engineering/evaluation_access_v1.md
* docs/ARCHITECTURE.md
* relevant subsystem summaries
* roadmap/status documents

Documentation must state what exists now, not what is merely planned.

Do not mark Evaluation Access V1 complete or frozen before PASS.

---

## Stage 9 — Full Verification

Every loop must run the complete verification suite, not only focused tests:

python manage.py check
python manage.py makemigrations analytics --check
python manage.py makemigrations accounts --check
python manage.py makemigrations players --check
python manage.py test analytics
python manage.py test accounts
python manage.py test players
python manage.py test drafts
python manage.py test pdp
python manage.py test
git diff --check

All commands must pass before committing the implementation loop.

If a command fails:

* fix the verified issue within the current loop;
* rerun focused tests;
* rerun the complete verification suite.

Do not commit a known failing state.

---

## Stage 10 — Commit Implementation

Commit the implementation, tests, and documentation for the loop.

Use a clear commit message describing the loop outcome.

Examples:

* `Implement coach evaluation review`
* `Harden coach evaluation privacy`
* `Fix evaluation filter correctness`
* `Reconcile Evaluation Access documentation`
* `Freeze Evaluation Access V1`

Do not include the prompt archive in this implementation commit.

---

## Stage 11 — Finalize Prompt Archive

Update the loop’s prompt archive with:

* implementation commit hash;
* commit diff or required prompt-record content;
* loop result;
* tests run;
* issues resolved;
* remaining gaps;
* next recommended loop objective;
* terminal state.

Commit the prompt archive separately.

---

## Stage 12 — Push

Push both commits.

Confirm the push result.

A local credential helper warning is not a failure if the remote update succeeds.

---

## Stage 13 — Post-Commit Review

After pushing:

1. Re-read the committed diff.
2. Reassess every production-readiness criterion.
3. Identify whether any new regression, inconsistency, or unproven criterion remains.
4. Confirm the working tree is clean.
5. Choose terminal state:

* CONTINUE
* PASS
* BLOCKED
* NO_PROGRESS

If CONTINUE:

* begin the next loop from the new committed state;
* use a new loop prompt archive;
* do not ask for confirmation unless a product decision is genuinely required.

==================================================
Phase 5 Feature Requirements
============================

The first loop should normally implement Phase 5 unless inspection finds a blocker.

Add coach-facing review of submitted evaluations.

Recommended routes:

/analytics/evaluation-review/
/analytics/evaluation-review/[int:observation_id](int:observation_id)/

Recommended names:

analytics:evaluation-review-list
analytics:evaluation-review-detail

Access:

* Django staff/superuser: allowed;
* account role coach: allowed;
* account role admin/staff without Django staff: coach review may be allowed according to Analytics role policy, but must not gain Account Operations access;
* player: denied;
* parent: denied;
* guest evaluator: denied.

Coach review must be read-only.

It must not grant reopen, edit, delete, or workflow-management powers.

Existing staff review remains separate and retains its existing abilities.

==================================================
Coach Review List
=================

Show submitted evaluations only.

Support filtering by:

* target player;
* target player name/search;
* evaluator;
* evaluator role/category;
* team;
* division;
* evaluation cycle;
* submitted date from;
* submitted date to.

Use server-rendered GET filters.

No JavaScript required.

Default ordering:

* newest submitted first;
* deterministic tie-breaker.

Result rows should include:

* target player;
* evaluator display identity;
* evaluator role snapshot;
* cycle;
* submitted date;
* team;
* division;
* detail link.

Coaches are allowed to see evaluator identity.

Players are not.

==================================================
Coach Review Detail
===================

Show:

* target player;
* evaluator name;
* evaluator role snapshot;
* cycle;
* submitted date;
* questions;
* ratings;
* notes.

Do not show unnecessary account-sensitive data such as:

* evaluator email unless genuinely needed;
* password/account metadata;
* import metadata;
* unrelated user fields.

Coach review remains read-only.

Do not expose staff-only reopen controls unless the user separately has existing staff-review permission and uses the existing staff route.

==================================================
Coach Review Services
=====================

Create or expand an Analytics-owned service, for example:

analytics/services/evaluation_review_service.py

Responsibilities may include:

* parse filters;
* build filtered submitted-evaluation queryset;
* return typed list rows;
* return typed detail read model;
* enforce coach review access;
* expose safe evaluator identity;
* avoid N+1 queries.

Do not put query/filter business logic in views.

==================================================
Coach Review Permission Helpers
===============================

Add explicit helpers such as:

* can_review_submitted_evaluations(user)
* can_view_evaluation_review_detail(user, observation)

Rules:

* staff/superuser allowed;
* coach role allowed;
* player denied;
* parent denied;
* guest evaluator denied;
* coach review access does not grant staff review/reopen access;
* coach role does not grant Account Operations access.

==================================================
Production-Readiness Acceptance Criteria
========================================

Do not reach PASS until all criteria below are proven.

A. Imports

* players can be imported;
* player account provisioning works according to current options;
* coaches can be imported in bulk;
* coach import duplicate/reuse behavior is documented;
* temporary passwords are one-time and not persisted;
* no accidental Player or UserPlayerLink creation from coach import.

B. Authentication

* imported coaches can log in when active;
* imported/provisioned players can log in when active;
* forced password change works;
* inactive users cannot log in;
* password reset operations remain functional.

C. Submission

* coaches can evaluate active players;
* players can evaluate other active players;
* guest evaluators can submit;
* parents cannot submit by default;
* self-evaluation is blocked;
* drafts resume correctly;
* complete evaluations submit;
* incomplete required responses are rejected;
* duplicates are prevented.

D. Role Snapshots

* coach snapshots as coach;
* player snapshots as player;
* guest evaluator snapshots correctly;
* staff/admin snapshots correctly;
* snapshots do not mutate after account-role changes.

E. Evaluator-Owned Detail

* evaluators can view their own submission;
* cannot view another evaluator’s submission unless authorized staff;
* submitted link wording is unambiguous.

F. Player My Evaluations

* active self link required;
* inactive self link denied;
* inactive player denied;
* multiple self links supported;
* submitted only;
* evaluator names hidden;
* role/category shown;
* deterministic response ordering;
* missing resources 404;
* forbidden resources 403;
* staff with self link receives player-safe representation.

G. Coach Review

* coach can view all submitted evaluations;
* player, parent, and guest evaluator cannot;
* filters work individually and in combination;
* evaluator identity visible to coach;
* evaluator email and sensitive metadata not exposed unnecessarily;
* draft/reopened observations excluded;
* detail is read-only;
* coach cannot reopen unless separately authorized staff using staff workflow;
* list and detail avoid obvious N+1 queries.

H. Staff Review Regression

* existing staff review works;
* reopen workflow works;
* staff review and coach review remain distinct;
* command center remains functional.

I. Account Operations Regression

* staff account operations still work;
* coach role does not grant Account Operations access;
* coach import remains staff-only;
* account creation/edit/reset/bulk operations remain functional.

J. Security and Privacy

* all mutation endpoints require POST and CSRF;
* role escalation is impossible through evaluation routes;
* player result privacy is preserved;
* coach review access is explicit;
* no plaintext passwords in logs, messages, sessions, metadata, summaries, or later pages;
* URL manipulation does not bypass ownership or role checks.

K. Documentation

* user manual describes player import, coach import, submission, My Evaluations, and coach review;
* architecture docs reflect actual dependency direction;
* Evaluation Access plan accurately marks completed work;
* deferred features remain clearly listed;
* no stale “future work” claims for implemented features.

L. Operational Pilot Readiness

Documentation includes a manual pilot checklist covering:

1. import sample players;
2. provision and activate player accounts;
3. import sample coaches;
4. copy one-time passwords;
5. log in as coach and change password;
6. log in as player and change password;
7. coach submits evaluation;
8. player submits peer evaluation;
9. self-evaluation attempt is blocked;
10. player views My Evaluations;
11. evaluator identity is hidden from player;
12. coach views and filters all submitted evaluations;
13. player cannot access coach review;
14. guest evaluator cannot access coach review;
15. staff review and reopen still work.

M. Freeze

Before PASS:

* complete final architecture review;
* complete final security review;
* complete final performance review;
* complete documentation reconciliation;
* run full test suite;
* ensure clean working tree;
* update status to COMPLETE and FROZEN;
* record remaining deferred work.

==================================================
No-Progress Rule
================

Track concrete progress across loops.

A loop counts as progress only if it does at least one of:

* satisfies a previously unsatisfied acceptance criterion;
* fixes a verified defect;
* adds missing regression proof;
* removes a documented architecture violation;
* corrects material documentation drift;
* completes a required production-readiness artifact.

Formatting, renaming, or speculative refactoring alone does not count.

If two consecutive loops make no concrete progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Deliverables
=======================

The PASS loop must include:

1. Executive production-readiness assessment.
2. Architecture assessment.
3. Security/privacy assessment.
4. Performance assessment.
5. End-to-end workflow assessment.
6. Documentation assessment.
7. Manual pilot checklist.
8. Deferred-work list.
9. Full test results.
10. Freeze declaration.

Only after all criteria pass, update documentation to state:

Evaluation Access V1 is COMPLETE and FROZEN.

The final report must state:

Terminal state: PASS

and confirm:

* all implementation/documentation commits were pushed;
* working tree is clean;
* Evaluation Access V1 is production-ready for the documented scope;
* no Phase beyond Evaluation Access V1 was started.

```

## Implementation Commit

`ab9a1f0 Implement coach evaluation review`

## Loop Result

CONTINUE

Phase 5 coach evaluation review was implemented and verified, but final Evaluation Access V1 production freeze artifacts and COMPLETE/FROZEN documentation remain for a subsequent loop.

## Tests Run

- `python manage.py test analytics` - passed, 122 tests
- `python manage.py test accounts` - passed, 184 tests
- `python manage.py check` - passed
- `python manage.py makemigrations analytics --check` - passed, no changes
- `python manage.py makemigrations accounts --check` - passed, no changes
- `python manage.py makemigrations players --check` - passed, no changes
- `python manage.py test analytics` - passed, 122 tests
- `python manage.py test accounts` - passed, 184 tests
- `python manage.py test players` - passed, 43 tests
- `python manage.py test drafts` - passed, 8 tests
- `python manage.py test pdp` - passed, 6 tests
- `python manage.py test` - passed, 385 tests
- `git diff --check` - passed

## Issues Resolved

- Added explicit coach review permissions for Django staff/superusers and account roles `coach`, `staff`, and `admin`.
- Denied coach review to player, parent, guest evaluator, and anonymous users.
- Added read-only submitted-evaluation list and detail routes.
- Added filters for player search, player ID, evaluator, evaluator role, team, division, cycle, and submitted date range.
- Kept draft and reopened observations out of coach review.
- Kept staff review/reopen workflow separate.
- Avoided exposing evaluator email or account metadata in coach review templates.
- Updated user-facing documentation to describe coach review as implemented.
- Marked Phase 5 implemented in the Evaluation Access engineering plan.

## Remaining Gaps

- Final pilot/freeze documentation is not complete.
- Evaluation Access V1 is not yet marked COMPLETE and FROZEN.
- Manual pilot checklist still needs to be added.
- Final architecture, security/privacy, performance, workflow, and documentation assessments still need to be recorded.

## Next Recommended Loop Objective

Run the final Evaluation Access V1 production-readiness/freeze loop: reconcile all docs, add the manual pilot checklist, record final assessments and deferred work, rerun full verification, and mark Evaluation Access V1 COMPLETE and FROZEN only if all criteria remain satisfied.

## Commit Diff

```diff
commit ab9a1f0553e3f207bbf7eebb2980cf8952c8d30c
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Fri Jul 10 11:47:54 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Fri Jul 10 11:47:54 2026 -0700

    Implement coach evaluation review
---
 analytics/services/evaluation_review_service.py    | 192 +++++++++++++++++++++
 analytics/services/permissions.py                  |  16 ++
 .../analytics/evaluation_review_detail.html        |  44 +++++
 .../analytics/evaluation_review_list.html          |  92 ++++++++++
 .../includes/account_profile_actions.html          |   3 +
 analytics/templatetags/analytics_account_nav.py    |   7 +-
 analytics/tests.py                                 | 190 ++++++++++++++++++++
 analytics/urls.py                                  |   4 +
 analytics/views.py                                 |  44 +++++
 docs/USER_MANUAL.md                                |  26 ++-
 .../engineering/evaluation_access_v1.md            |   4 +
 11 files changed, 620 insertions(+), 2 deletions(-)

diff --git a/analytics/services/evaluation_review_service.py b/analytics/services/evaluation_review_service.py
new file mode 100644
index 0000000..2759cb6
--- /dev/null
+++ b/analytics/services/evaluation_review_service.py
@@ -0,0 +1,192 @@
+from __future__ import annotations
+
+from dataclasses import dataclass
+
+from django.core.exceptions import PermissionDenied
+from django.db.models import Q
+from django.utils.dateparse import parse_date
+
+from analytics.models import (
+    OBSERVATION_STATUS_SUBMITTED,
+    OBSERVATION_TYPE_COACH_ASSESSMENT,
+    EvaluationCycle,
+    EvaluatorRole,
+    Observation,
+)
+from analytics.services.permissions import can_review_submitted_evaluations, can_view_evaluation_review_detail
+
+
+@dataclass(frozen=True)
+class EvaluationReviewFilters:
+    q: str = ""
+    player: str = ""
+    evaluator: str = ""
+    evaluator_role: str = ""
+    team: str = ""
+    division: str = ""
+    cycle: str = ""
+    submitted_from: str = ""
+    submitted_to: str = ""
+
+
+@dataclass(frozen=True)
+class EvaluationReviewRow:
+    observation_id: int
+    player_name: str
+    player_team: str
+    player_division: str
+    evaluator_name: str
+    evaluator_role_name: str
+    cycle_name: str
+    submitted_at: object
+
+
+@dataclass(frozen=True)
+class EvaluationReviewQuestionResponse:
+    question_prompt: str
+    category: str
+    numeric_value: object = None
+    text_value: str = ""
+
+
+@dataclass(frozen=True)
+class EvaluationReviewDetail:
+    observation_id: int
+    player_name: str
+    player_team: str
+    player_division: str
+    evaluator_name: str
+    evaluator_role_name: str
+    cycle_name: str
+    submitted_at: object
+    responses: list[EvaluationReviewQuestionResponse]
+
+
+@dataclass(frozen=True)
+class EvaluationReviewList:
+    filters: EvaluationReviewFilters
+    rows: list[EvaluationReviewRow]
+    total_count: int
+    cycles: object
+    evaluator_roles: object
+
+
+def parse_evaluation_review_filters(params) -> EvaluationReviewFilters:
+    return EvaluationReviewFilters(
+        q=(params.get("q") or "").strip(),
+        player=(params.get("player") or "").strip(),
+        evaluator=(params.get("evaluator") or "").strip(),
+        evaluator_role=(params.get("evaluator_role") or "").strip(),
+        team=(params.get("team") or "").strip(),
+        division=(params.get("division") or "").strip(),
+        cycle=(params.get("cycle") or "").strip(),
+        submitted_from=(params.get("submitted_from") or "").strip(),
+        submitted_to=(params.get("submitted_to") or "").strip(),
+    )
+
+
+def _display_user(user) -> str:
+    if not user:
+        return "Unknown evaluator"
+    return user.get_full_name() or user.username
+
+
+def submitted_evaluation_queryset(filters: EvaluationReviewFilters | None = None):
+    queryset = (
+        Observation.objects.select_related("player", "evaluation_cycle", "evaluator", "evaluator_role")
+        .filter(
+            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
+            status=OBSERVATION_STATUS_SUBMITTED,
+        )
+        .order_by("-submitted_at", "-created_at", "-id")
+    )
+    if filters is None:
+        return queryset
+
+    if filters.q:
+        queryset = queryset.filter(
+            Q(player__first_name__icontains=filters.q)
+            | Q(player__last_name__icontains=filters.q)
+            | Q(player__preferred_name__icontains=filters.q)
+        )
+    if filters.player.isdigit():
+        queryset = queryset.filter(player_id=int(filters.player))
+    if filters.evaluator:
+        if filters.evaluator.isdigit():
+            queryset = queryset.filter(evaluator_id=int(filters.evaluator))
+        else:
+            queryset = queryset.filter(evaluator__username__icontains=filters.evaluator)
+    if filters.evaluator_role:
+        queryset = queryset.filter(evaluator_role_key=filters.evaluator_role)
+    if filters.team:
+        queryset = queryset.filter(player__team_name__icontains=filters.team)
+    if filters.division:
+        queryset = queryset.filter(player__division__icontains=filters.division)
+    if filters.cycle.isdigit():
+        queryset = queryset.filter(evaluation_cycle_id=int(filters.cycle))
+
+    submitted_from = parse_date(filters.submitted_from)
+    if submitted_from:
+        queryset = queryset.filter(submitted_at__date__gte=submitted_from)
+    submitted_to = parse_date(filters.submitted_to)
+    if submitted_to:
+        queryset = queryset.filter(submitted_at__date__lte=submitted_to)
+
+    return queryset
+
+
+def get_evaluation_review_list(user, params) -> EvaluationReviewList:
+    if not can_review_submitted_evaluations(user):
+        raise PermissionDenied("You cannot review submitted evaluations.")
+    filters = parse_evaluation_review_filters(params)
+    queryset = submitted_evaluation_queryset(filters)
+    rows = [
+        EvaluationReviewRow(
+            observation_id=observation.id,
+            player_name=observation.player.display_name,
+            player_team=observation.player.team_name,
+            player_division=observation.player.division,
+            evaluator_name=_display_user(observation.evaluator),
+            evaluator_role_name=observation.evaluator_role_name or "Evaluator",
+            cycle_name=observation.evaluation_cycle.name,
+            submitted_at=observation.submitted_at,
+        )
+        for observation in queryset
+    ]
+    return EvaluationReviewList(
+        filters=filters,
+        rows=rows,
+        total_count=len(rows),
+        cycles=EvaluationCycle.objects.filter(is_active=True).order_by("-starts_on", "-created_at", "name"),
+        evaluator_roles=EvaluatorRole.objects.filter(is_active=True).order_by("name"),
+    )
+
+
+def get_evaluation_review_detail(user, observation_id: int) -> EvaluationReviewDetail:
+    observation = submitted_evaluation_queryset().get(pk=observation_id)
+    if not can_view_evaluation_review_detail(user, observation):
+        raise PermissionDenied("You cannot review this evaluation.")
+    responses = [
+        EvaluationReviewQuestionResponse(
+            question_prompt=response.question.prompt,
+            category=response.question.category or "Questions",
+            numeric_value=response.numeric_value,
+            text_value=response.text_value,
+        )
+        for response in observation.responses.select_related("question").order_by(
+            "question__display_order",
+            "question_id",
+            "id",
+        )
+    ]
+    return EvaluationReviewDetail(
+        observation_id=observation.id,
+        player_name=observation.player.display_name,
+        player_team=observation.player.team_name,
+        player_division=observation.player.division,
+        evaluator_name=_display_user(observation.evaluator),
+        evaluator_role_name=observation.evaluator_role_name or "Evaluator",
+        cycle_name=observation.evaluation_cycle.name,
+        submitted_at=observation.submitted_at,
+        responses=responses,
+    )
diff --git a/analytics/services/permissions.py b/analytics/services/permissions.py
index c5f9ed0..7153514 100644
--- a/analytics/services/permissions.py
+++ b/analytics/services/permissions.py
@@ -57,6 +57,22 @@ def can_review_observations(user) -> bool:
     return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))
 
 
+def can_review_submitted_evaluations(user) -> bool:
+    if not user or not user.is_authenticated:
+        return False
+    if user.is_staff or user.is_superuser:
+        return True
+    return role_for_user(user) in {AccountRole.COACH, AccountRole.STAFF, AccountRole.ADMIN}
+
+
+def can_view_evaluation_review_detail(user, observation) -> bool:
+    return bool(
+        observation
+        and observation.status == OBSERVATION_STATUS_SUBMITTED
+        and can_review_submitted_evaluations(user)
+    )
+
+
 def can_view_observation(user, observation) -> bool:
     if can_review_observations(user):
         return True
diff --git a/analytics/templates/analytics/evaluation_review_detail.html b/analytics/templates/analytics/evaluation_review_detail.html
new file mode 100644
index 0000000..960b529
--- /dev/null
+++ b/analytics/templates/analytics/evaluation_review_detail.html
@@ -0,0 +1,44 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}Evaluation Review{% endblock %}
+{% block analytics_subtitle %}{{ detail.player_name }} · {{ detail.cycle_name }}{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Submitted Evaluation</h2>
+    <dl class="pdp-definition-list">
+        <dt>Player</dt>
+        <dd>{{ detail.player_name }}</dd>
+        <dt>Team</dt>
+        <dd>{{ detail.player_team }}</dd>
+        <dt>Division</dt>
+        <dd>{{ detail.player_division }}</dd>
+        <dt>Evaluator</dt>
+        <dd>{{ detail.evaluator_name }}</dd>
+        <dt>Evaluator Role</dt>
+        <dd>{{ detail.evaluator_role_name }}</dd>
+        <dt>Cycle</dt>
+        <dd>{{ detail.cycle_name }}</dd>
+        <dt>Submitted</dt>
+        <dd>{{ detail.submitted_at|date:"M j, Y" }}</dd>
+    </dl>
+    {% for response in detail.responses %}
+        <section class="pdp-list__item pdp-list__item--stack">
+            <h3>{{ response.category }}</h3>
+            <div>
+                <strong>{{ response.question_prompt }}</strong>
+                {% if response.numeric_value %}
+                    <span>{{ response.numeric_value|floatformat:0 }}</span>
+                {% elif response.text_value %}
+                    <p>{{ response.text_value }}</p>
+                {% else %}
+                    <span>Not answered</span>
+                {% endif %}
+            </div>
+        </section>
+    {% empty %}
+        <p>No responses are available.</p>
+    {% endfor %}
+    <a class="button button--ghost" href="{% url 'analytics:evaluation-review-list' %}">Back</a>
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/evaluation_review_list.html b/analytics/templates/analytics/evaluation_review_list.html
new file mode 100644
index 0000000..7791e24
--- /dev/null
+++ b/analytics/templates/analytics/evaluation_review_list.html
@@ -0,0 +1,92 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}Evaluation Review{% endblock %}
+{% block analytics_subtitle %}Read-only review of submitted evaluations.{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Submitted Evaluations</h2>
+    <form method="get" class="pdp-form">
+        <label>
+            Player Search
+            <input type="search" name="q" value="{{ filters.q }}">
+        </label>
+        <label>
+            Player ID
+            <input type="text" name="player" value="{{ filters.player }}">
+        </label>
+        <label>
+            Evaluator
+            <input type="text" name="evaluator" value="{{ filters.evaluator }}">
+        </label>
+        <label>
+            Evaluator Role
+            <select name="evaluator_role">
+                <option value="">All</option>
+                {% for role in evaluator_roles %}
+                    <option value="{{ role.key }}" {% if filters.evaluator_role == role.key %}selected{% endif %}>{{ role.name }}</option>
+                {% endfor %}
+            </select>
+        </label>
+        <label>
+            Team
+            <input type="text" name="team" value="{{ filters.team }}">
+        </label>
+        <label>
+            Division
+            <input type="text" name="division" value="{{ filters.division }}">
+        </label>
+        <label>
+            Cycle
+            <select name="cycle">
+                <option value="">All</option>
+                {% for cycle in cycles %}
+                    <option value="{{ cycle.id }}" {% if filters.cycle == cycle.id|stringformat:"s" %}selected{% endif %}>{{ cycle.name }}</option>
+                {% endfor %}
+            </select>
+        </label>
+        <label>
+            Submitted From
+            <input type="date" name="submitted_from" value="{{ filters.submitted_from }}">
+        </label>
+        <label>
+            Submitted To
+            <input type="date" name="submitted_to" value="{{ filters.submitted_to }}">
+        </label>
+        <button class="button button--primary" type="submit">Filter</button>
+    </form>
+    <p>{{ total_count }} submitted evaluation{{ total_count|pluralize }} found.</p>
+    <div class="table-wrap">
+        <table class="pdp-table">
+            <thead>
+                <tr>
+                    <th>Player</th>
+                    <th>Team</th>
+                    <th>Division</th>
+                    <th>Evaluator</th>
+                    <th>Role</th>
+                    <th>Cycle</th>
+                    <th>Submitted</th>
+                    <th></th>
+                </tr>
+            </thead>
+            <tbody>
+                {% for row in rows %}
+                    <tr>
+                        <td>{{ row.player_name }}</td>
+                        <td>{{ row.player_team }}</td>
+                        <td>{{ row.player_division }}</td>
+                        <td>{{ row.evaluator_name }}</td>
+                        <td>{{ row.evaluator_role_name }}</td>
+                        <td>{{ row.cycle_name }}</td>
+                        <td>{{ row.submitted_at|date:"M j, Y" }}</td>
+                        <td><a class="button button--ghost" href="{% url 'analytics:evaluation-review-detail' observation_id=row.observation_id %}">Review</a></td>
+                    </tr>
+                {% empty %}
+                    <tr><td colspan="8">No submitted evaluations found.</td></tr>
+                {% endfor %}
+            </tbody>
+        </table>
+    </div>
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/includes/account_profile_actions.html b/analytics/templates/analytics/includes/account_profile_actions.html
index 42a34ee..674baa6 100644
--- a/analytics/templates/analytics/includes/account_profile_actions.html
+++ b/analytics/templates/analytics/includes/account_profile_actions.html
@@ -4,3 +4,6 @@
 {% if can_view_my_evaluations %}
     <p><a class="button button--ghost" href="{% url 'analytics:my-evaluations' %}">My Evaluations</a></p>
 {% endif %}
+{% if can_review_submitted_evaluations %}
+    <p><a class="button button--ghost" href="{% url 'analytics:evaluation-review-list' %}">Review Evaluations</a></p>
+{% endif %}
diff --git a/analytics/templatetags/analytics_account_nav.py b/analytics/templatetags/analytics_account_nav.py
index 3fa5a5e..9a6a020 100644
--- a/analytics/templatetags/analytics_account_nav.py
+++ b/analytics/templatetags/analytics_account_nav.py
@@ -1,6 +1,10 @@
 from django import template
 
-from analytics.services.permissions import can_submit_evaluation, can_view_my_evaluations
+from analytics.services.permissions import (
+    can_review_submitted_evaluations,
+    can_submit_evaluation,
+    can_view_my_evaluations,
+)
 
 
 register = template.Library()
@@ -12,4 +16,5 @@ def analytics_account_profile_actions(user):
     return {
         "can_submit_evaluations": can_submit_evaluation(user),
         "can_view_my_evaluations": can_view_my_evaluations(user),
+        "can_review_submitted_evaluations": can_review_submitted_evaluations(user),
     }
diff --git a/analytics/tests.py b/analytics/tests.py
index 756f8ce..32dff4a 100644
--- a/analytics/tests.py
+++ b/analytics/tests.py
@@ -2272,3 +2272,193 @@ class MyEvaluationsViewTests(TestCase):
 
         self.client.force_login(self.player_user)
         self.assertEqual(self.client.get(reverse("analytics:evaluation-list")).status_code, 200)
+
+
+class EvaluationReviewViewTests(TestCase):
+    def setUp(self):
+        self.coach = User.objects.create_user(
+            username="coach-review",
+            password="testpass",
+            first_name="Casey",
+            last_name="Coach",
+            email="coach-review@example.com",
+        )
+        self.second_coach = User.objects.create_user(
+            username="second-coach-review",
+            password="testpass",
+            first_name="Sam",
+            last_name="Coach",
+            email="sam-coach@example.com",
+        )
+        self.player_user = User.objects.create_user(username="player-review", password="testpass")
+        self.parent = User.objects.create_user(username="parent-review", password="testpass")
+        self.guest = User.objects.create_user(username="guest-review", password="testpass")
+        self.staff = User.objects.create_user(username="staff-review-phase5", password="testpass", is_staff=True)
+        self.role_staff = User.objects.create_user(username="role-staff-review", password="testpass")
+        self.role_admin = User.objects.create_user(username="role-admin-review", password="testpass")
+        set_account_role(self.coach, AccountRole.COACH)
+        set_account_role(self.second_coach, AccountRole.COACH)
+        set_account_role(self.player_user, AccountRole.PLAYER)
+        set_account_role(self.parent, AccountRole.PARENT)
+        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
+        set_account_role(self.staff, AccountRole.STAFF)
+        set_account_role(self.role_staff, AccountRole.STAFF)
+        set_account_role(self.role_admin, AccountRole.ADMIN)
+        self.player = Player.objects.create(first_name="Target", last_name="One", division="13U", team_name="Reds")
+        self.second_player = Player.objects.create(first_name="Target", last_name="Two", division="15U", team_name="Blues")
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+        )
+        self.second_cycle = EvaluationCycle.objects.create(
+            name="2026 15U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+        )
+
+    def service_response_payload(self, value=4, note="Good teammate."):
+        payload = {
+            question: value
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5,
+                is_required=True,
+                is_active=True,
+            )
+        }
+        text_question = self.setup_result.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
+        payload[text_question] = note
+        return payload
+
+    def submitted_observation(self, player=None, evaluator=None, cycle=None, value=4, note="Good teammate."):
+        result = create_coach_assessment_observation(
+            player=player or self.player,
+            evaluation_cycle=cycle or self.cycle,
+            evaluator=evaluator or self.coach,
+            responses=self.service_response_payload(value=value, note=note),
+        )
+        return submit_observation(result.observation, actor=evaluator or self.coach)
+
+    def test_coach_can_review_all_submitted_evaluations(self):
+        first = self.submitted_observation(player=self.player, evaluator=self.coach, note="First submitted.")
+        second = self.submitted_observation(player=self.second_player, evaluator=self.second_coach, cycle=self.second_cycle, note="Second submitted.")
+        self.client.force_login(self.coach)
+
+        response = self.client.get(reverse("analytics:evaluation-review-list"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+        self.assertContains(response, self.second_player.display_name)
+        self.assertContains(response, "Casey Coach")
+        self.assertContains(response, "Sam Coach")
+        self.assertContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": first.id}))
+        self.assertContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": second.id}))
+        self.assertNotContains(response, self.coach.email)
+
+    def test_coach_review_access_rules(self):
+        self.submitted_observation()
+        for user in [self.player_user, self.parent, self.guest]:
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                response = self.client.get(reverse("analytics:evaluation-review-list"))
+                self.assertEqual(response.status_code, 403)
+                self.client.logout()
+
+        for user in [self.coach, self.staff, self.role_staff, self.role_admin]:
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                response = self.client.get(reverse("analytics:evaluation-review-list"))
+                self.assertEqual(response.status_code, 200)
+                self.client.logout()
+
+    def test_coach_role_does_not_grant_account_operations(self):
+        self.client.force_login(self.coach)
+
+        self.assertEqual(self.client.get(reverse("accounts:operations-dashboard")).status_code, 403)
+
+    def test_coach_review_filters_individually_and_in_combination(self):
+        first = self.submitted_observation(player=self.player, evaluator=self.coach, note="Reds note.")
+        second = self.submitted_observation(player=self.second_player, evaluator=self.second_coach, cycle=self.second_cycle, note="Blues note.")
+        today = timezone.localdate().isoformat()
+        self.client.force_login(self.coach)
+
+        cases = [
+            ({"q": "One"}, first, second),
+            ({"player": str(self.player.id)}, first, second),
+            ({"evaluator": str(self.coach.id)}, first, second),
+            ({"evaluator": "second-coach"}, second, first),
+            ({"evaluator_role": ROLE_COACH}, first, None),
+            ({"team": "Reds"}, first, second),
+            ({"division": "15U"}, second, first),
+            ({"cycle": str(self.second_cycle.id)}, second, first),
+            ({"submitted_from": today, "submitted_to": today}, first, None),
+            ({"q": "Target", "team": "Blues", "cycle": str(self.second_cycle.id)}, second, first),
+        ]
+        for params, included, excluded in cases:
+            with self.subTest(params=params):
+                response = self.client.get(reverse("analytics:evaluation-review-list"), params)
+                self.assertEqual(response.status_code, 200)
+                self.assertContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": included.id}))
+                if excluded:
+                    self.assertNotContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": excluded.id}))
+
+    def test_coach_review_excludes_draft_and_reopened_observations(self):
+        submitted = self.submitted_observation(player=self.player, evaluator=self.coach)
+        draft = create_coach_assessment_observation(
+            player=self.second_player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=self.service_response_payload(),
+        ).observation
+        reopened = create_coach_assessment_observation(
+            player=self.second_player,
+            evaluation_cycle=self.second_cycle,
+            evaluator=self.second_coach,
+            responses=self.service_response_payload(),
+        ).observation
+        reopened.status = OBSERVATION_STATUS_REOPENED
+        reopened.save(update_fields=["status", "updated_at"])
+        self.client.force_login(self.coach)
+
+        list_response = self.client.get(reverse("analytics:evaluation-review-list"))
+        draft_detail = self.client.get(reverse("analytics:evaluation-review-detail", kwargs={"observation_id": draft.id}))
+        reopened_detail = self.client.get(reverse("analytics:evaluation-review-detail", kwargs={"observation_id": reopened.id}))
+
+        self.assertContains(list_response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": submitted.id}))
+        self.assertNotContains(list_response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": draft.id}))
+        self.assertNotContains(list_response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": reopened.id}))
+        self.assertEqual(draft_detail.status_code, 404)
+        self.assertEqual(reopened_detail.status_code, 404)
+
+    def test_coach_review_detail_is_read_only_and_exposes_safe_evaluator_identity(self):
+        observation = self.submitted_observation(note="Review detail note.")
+        self.client.force_login(self.coach)
+
+        response = self.client.get(reverse("analytics:evaluation-review-detail", kwargs={"observation_id": observation.id}))
+        post_response = self.client.post(reverse("analytics:evaluation-review-detail", kwargs={"observation_id": observation.id}), {"action": "reopen"})
+        observation.refresh_from_db()
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+        self.assertContains(response, "Casey Coach")
+        self.assertContains(response, "Coach")
+        self.assertContains(response, "Review detail note.")
+        self.assertNotContains(response, self.coach.email)
+        self.assertNotContains(response, "Reopen")
+        self.assertEqual(post_response.status_code, 405)
+        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
+
+    def test_staff_review_reopen_remains_separate(self):
+        observation = self.submitted_observation()
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("analytics:observation-review-detail", kwargs={"observation_id": observation.id}),
+            {"action": "reopen"},
+            follow=True,
+        )
+        observation.refresh_from_db()
+
+        self.assertEqual(response.status_code, 200)
+        self.assertEqual(observation.status, OBSERVATION_STATUS_REOPENED)
diff --git a/analytics/urls.py b/analytics/urls.py
index 3d080a2..2e9ebc7 100644
--- a/analytics/urls.py
+++ b/analytics/urls.py
@@ -7,6 +7,8 @@ from analytics.views import (
     CoachAssessmentListView,
     EvaluationListView,
     EvaluationPlayerView,
+    EvaluationReviewDetailView,
+    EvaluationReviewListView,
     MyEvaluationDetailView,
     MyEvaluationsPlayerView,
     MyEvaluationsView,
@@ -33,6 +35,8 @@ urlpatterns = [
     path("players/<int:player_id>/", PlayerProfileView.as_view(), name="player-profile"),
     path("evaluations/", EvaluationListView.as_view(), name="evaluation-list"),
     path("evaluations/players/<int:player_id>/", EvaluationPlayerView.as_view(), name="evaluation-player"),
+    path("evaluation-review/", EvaluationReviewListView.as_view(), name="evaluation-review-list"),
+    path("evaluation-review/<int:observation_id>/", EvaluationReviewDetailView.as_view(), name="evaluation-review-detail"),
     path("my/evaluations/", MyEvaluationsView.as_view(), name="my-evaluations"),
     path("my/evaluations/players/<int:player_id>/", MyEvaluationsPlayerView.as_view(), name="my-evaluations-player"),
     path("my/evaluations/<int:observation_id>/", MyEvaluationDetailView.as_view(), name="my-evaluation-detail"),
diff --git a/analytics/views.py b/analytics/views.py
index 14d49c2..9ae8b3d 100644
--- a/analytics/views.py
+++ b/analytics/views.py
@@ -37,11 +37,13 @@ from analytics.services.evaluation_access_service import (
     get_my_evaluations,
     get_or_create_evaluation_for_player,
 )
+from analytics.services.evaluation_review_service import get_evaluation_review_detail, get_evaluation_review_list
 from analytics.services.observation_service import get_observation_detail, save_observation_responses, submit_observation
 from analytics.services.permissions import (
     can_edit_observation,
     can_evaluate_player,
     can_reopen_observation,
+    can_review_submitted_evaluations,
     can_submit_coach_assessment,
     can_submit_evaluation,
     can_view_my_evaluations,
@@ -401,6 +403,48 @@ class MyEvaluationDetailView(LoginRequiredMixin, TemplateView):
         return context
 
 
+class EvaluationReviewRequiredMixin(LoginRequiredMixin):
+    def dispatch(self, request, *args, **kwargs):
+        if request.user.is_authenticated and not can_review_submitted_evaluations(request.user):
+            raise PermissionDenied("You cannot review submitted evaluations.")
+        return super().dispatch(request, *args, **kwargs)
+
+
+class EvaluationReviewListView(EvaluationReviewRequiredMixin, TemplateView):
+    template_name = "analytics/evaluation_review_list.html"
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        review_list = get_evaluation_review_list(self.request.user, self.request.GET)
+        context.update(
+            {
+                "review_list": review_list,
+                "rows": review_list.rows,
+                "filters": review_list.filters,
+                "cycles": review_list.cycles,
+                "evaluator_roles": review_list.evaluator_roles,
+                "total_count": review_list.total_count,
+            }
+        )
+        return context
+
+
+class EvaluationReviewDetailView(EvaluationReviewRequiredMixin, TemplateView):
+    template_name = "analytics/evaluation_review_detail.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        try:
+            self.detail = get_evaluation_review_detail(request.user, kwargs["observation_id"])
+        except Observation.DoesNotExist as exc:
+            raise Http404("Evaluation not found.") from exc
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["detail"] = self.detail
+        return context
+
+
 class CoachAssessmentListView(LoginRequiredMixin, TemplateView):
     template_name = "analytics/assessment_list.html"
 
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 038245a..d106820 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -376,7 +376,31 @@ Players with an active linked self player record can view submitted evaluations
 
 Player-facing evaluation results show evaluator role/category, submitted date, cycle, ratings, and notes. Evaluator names, usernames, and email addresses are hidden from players.
 
-Draft and reopened evaluations are not shown as final feedback. Inactive player links and inactive player records are not shown in normal My Evaluations lists. Coaches still do not have an all-evaluation review page until the coach review phase.
+Draft and reopened evaluations are not shown as final feedback. Inactive player links and inactive player records are not shown in normal My Evaluations lists.
+
+## Coach Evaluation Review
+
+Coaches can review submitted evaluations:
+
+```text
+/analytics/evaluation-review/
+```
+
+Coach review is read-only. It shows submitted evaluations only and does not allow coaches to reopen, edit, or delete submitted evaluations.
+
+Coaches can filter submitted evaluations by:
+
+- player name or player ID
+- evaluator
+- evaluator role/category
+- team
+- division
+- evaluation cycle
+- submitted date range
+
+Coach review shows evaluator names and role/category so coaches can understand who submitted each evaluation. It does not show evaluator email addresses, account metadata, passwords, import metadata, or unrelated account details.
+
+Players, parents, and guest evaluators cannot access the coach review page. Staff review remains a separate workflow.
 
 ## Who Can Evaluate A Player
 
diff --git a/docs/evaluations/implementation/engineering/evaluation_access_v1.md b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
index 3c89add..1921be6 100644
--- a/docs/evaluations/implementation/engineering/evaluation_access_v1.md
+++ b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
@@ -1006,6 +1006,10 @@ Deliverables:
 - staff behavior preserved;
 - tests.
 
+Status: implemented.
+
+Review notes: Coach review is implemented as an Analytics-owned read-only submitted-evaluation surface. It uses explicit coach-review permission helpers, an `evaluation_review_service` for filter parsing/query/read models, thin views, and presentation-only templates. Coach review remains separate from existing staff observation review; coaches cannot reopen submitted observations through the coach review routes.
+
 ### Phase 6: Final Pilot / Freeze
 
 Purpose:

```

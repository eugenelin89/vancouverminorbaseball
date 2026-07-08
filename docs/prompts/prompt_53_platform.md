# Prompt 53 - Platform

## User Prompt

```text
Implement Evaluation Access V1 Phase 0 only.

This is a planning-decision documentation phase.

Do NOT implement application code.

Do NOT modify Python files.

Do NOT modify models, services, forms, views, URLs, templates, middleware, tests, or migrations.

Goal:
Record the product/architecture decisions required before implementing Evaluation Access V1.

Read:

- docs/ARCHITECTURE.md
- docs/USER_MANUAL.md
- docs/evaluations/implementation/engineering/evaluation_access_v1.md
- docs/account_management/V1_SUMMARY.md
- docs/account_management/implementation/engineering/platform_v1_account_operations.md
- accounts/
- players/
- analytics/

Update:

- docs/evaluations/implementation/engineering/evaluation_access_v1.md

Document these Phase 0 decisions:

1. Self-evaluation

Decision:
Block self-evaluation for Evaluation Access V1.

Rationale:
The initial goal is coach and peer evaluation. Self-evaluation may be useful later, but it needs separate labeling/reporting to avoid confusing review results.

2. Player-facing evaluator visibility

Decision:
Players should not see evaluator names in “My Evaluations.”

Players may see evaluator role/category only.

Rationale:
Youth player evaluations are sensitive. Hiding names reduces peer pressure and retaliation risk while still allowing coaches/staff to see full evaluator identity in review pages.

3. Imported coach account activation

Decision:
Imported coach accounts should be active by default.

They must still have `must_change_password=True`.

Rationale:
Coach import is intended to reduce operational setup work. Active-by-default makes imported coaches usable immediately while forced password change preserves safety.

4. Coach-to-player links during coach import

Decision:
Do not create coach-to-player links in Coach Import Phase 1.

Coach import should create/reuse coach user accounts only.

Rationale:
The immediate blocker is onboarding many coaches quickly. Coach/team/player assignment is a separate roster-management problem and should not block evaluation access.

5. Coach import persistence

Decision:
Do not add a new coach import batch model in Phase 1 unless absolutely necessary.

Prefer a simple upload/preview/confirm workflow using service read models and one-time result display.

Rationale:
Avoid adding models/migrations before proving the workflow. Existing account services can create/reuse users without a persistent import model.

6. Guest evaluator submission

Decision:
Allow authenticated guest evaluators to submit evaluations.

Do not give guest evaluators coach review access.

Rationale:
This keeps the existing broad authenticated-evaluator design while preserving review privacy.

7. Coach review scope

Decision:
Coach review should show submitted evaluations only by default.

Draft/reopened observations remain visible only through existing owner/staff workflows.

Rationale:
Coach review is for final evaluation analysis, not workflow management.

Also update the implementation phase list if needed so Phase 0 is marked complete once these decisions are recorded.

Do NOT change the overall roadmap.

Do NOT add new features.

Verification:

Run:

git diff --check

No Django tests are required because this is documentation-only.

Prompt archive:

Create the next prompt record in docs/prompts/ according to AGENTS.md.

Commit documentation changes first.

Then commit the prompt archive separately.

Push both commits.

Final report:

Report:

- files modified
- decisions recorded
- any roadmap text clarified
- confirmation that no application code was changed
- confirmation that Phase 1 Coach Import was NOT implemented
- git diff --check result
- commits created
- push result
```

## App / Subsystem

platform

## Work Commit

```text
00a0c480f772089e016fc24a7287e1f8b96b0839 Record Evaluation Access Phase 0 decisions
```

## Commit Diff

```diff
commit 00a0c480f772089e016fc24a7287e1f8b96b0839
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 8 12:47:50 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 8 12:47:50 2026 -0700

    Record Evaluation Access Phase 0 decisions
---
 .../engineering/evaluation_access_v1.md            | 242 ++++++++++++++-------
 1 file changed, 163 insertions(+), 79 deletions(-)

diff --git a/docs/evaluations/implementation/engineering/evaluation_access_v1.md b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
index 7afe399..e67efd4 100644
--- a/docs/evaluations/implementation/engineering/evaluation_access_v1.md
+++ b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
@@ -35,7 +35,103 @@ Important current gaps:
 - Current coach-assessment creation defaults evaluator role to `coach` unless a caller supplies a different `EvaluatorRole`; player-submitted evaluations need role snapshot behavior based on the user's account role.
 - Current player profile/timeline pages are staff-facing, not private player result pages.
 
-## 3. Strict Scope
+## 3. Phase 0 Decisions
+
+Status: complete.
+
+These product and architecture decisions are recorded before implementation begins.
+
+### Self-Evaluation
+
+Decision:
+
+```text
+Block self-evaluation for Evaluation Access V1.
+```
+
+Rationale:
+
+The initial goal is coach and peer evaluation. Self-evaluation may be useful later, but it needs separate labeling and reporting to avoid confusing review results.
+
+### Player-Facing Evaluator Visibility
+
+Decision:
+
+```text
+Players should not see evaluator names in "My Evaluations."
+Players may see evaluator role/category only.
+```
+
+Rationale:
+
+Youth player evaluations are sensitive. Hiding names reduces peer pressure and retaliation risk while still allowing coaches and staff to see full evaluator identity in review pages.
+
+### Imported Coach Account Activation
+
+Decision:
+
+```text
+Imported coach accounts should be active by default.
+Imported coach accounts must still have must_change_password=True.
+```
+
+Rationale:
+
+Coach import is intended to reduce operational setup work. Active-by-default makes imported coaches usable immediately while forced password change preserves safety.
+
+### Coach-To-Player Links During Coach Import
+
+Decision:
+
+```text
+Do not create coach-to-player links in Coach Import Phase 1.
+Coach import should create or reuse coach user accounts only.
+```
+
+Rationale:
+
+The immediate blocker is onboarding many coaches quickly. Coach/team/player assignment is a separate roster-management problem and should not block evaluation access.
+
+### Coach Import Persistence
+
+Decision:
+
+```text
+Do not add a new coach import batch model in Phase 1 unless absolutely necessary.
+Prefer a simple upload/preview/confirm workflow using service read models and one-time result display.
+```
+
+Rationale:
+
+Avoid adding models and migrations before proving the workflow. Existing account services can create and reuse users without a persistent import model.
+
+### Guest Evaluator Submission
+
+Decision:
+
+```text
+Allow authenticated guest evaluators to submit evaluations.
+Do not give guest evaluators coach review access.
+```
+
+Rationale:
+
+This keeps the existing broad authenticated-evaluator design while preserving review privacy.
+
+### Coach Review Scope
+
+Decision:
+
+```text
+Coach review should show submitted evaluations only by default.
+Draft and reopened observations remain visible only through existing owner/staff workflows.
+```
+
+Rationale:
+
+Coach review is for final evaluation analysis, not workflow management.
+
+## 4. Strict Scope
 
 This plan covers:
 
@@ -49,7 +145,7 @@ This plan covers:
 
 This plan assumes evaluations continue using the existing Analytics observation architecture. The first implementation should reuse the existing `coach_assessment` observation workflow and question-set architecture unless a later approved architecture document renames the workflow.
 
-## 4. Out Of Scope
+## 5. Out Of Scope
 
 Do not implement these as part of Evaluation Access V1:
 
@@ -74,13 +170,15 @@ Do not implement these as part of Evaluation Access V1:
 - new timeline database models;
 - PDP migration.
 
-## 5. Coach Import
+## 6. Coach Import
 
 ### Purpose
 
 Coach import should let staff create or update coach login accounts from a roster-style CSV without manually creating every coach account.
 
-Coach import belongs to `accounts`, not `players` or `analytics`, because it creates Django users and account profiles. It may optionally create coach-to-player links using existing `UserPlayerLink` relationship values, but it must not create or modify canonical player identity.
+Coach import belongs to `accounts`, not `players` or `analytics`, because it creates Django users and account profiles. It must not create or modify canonical player identity.
+
+Coach Import Phase 1 should create or reuse coach user accounts only. It should not create coach-to-player links yet.
 
 ### Recommended CSV Format
 
@@ -166,23 +264,24 @@ Reasoning:
 
 `linked_player_ids` and `linked_player_names`:
 
-- optional;
-- if used, create `UserPlayerLink` records with relationship `coach`;
-- require exact player lookup or explicit conflict review;
-- do not create player records from coach import.
+- deferred from Coach Import Phase 1;
+- may be accepted only as ignored/unmapped context if present in uploaded files;
+- should not create `UserPlayerLink` records in Phase 1;
+- future coach-to-player linking needs a separate roster-management plan;
+- must never create player records from coach import.
 
 ### Account Creation
 
 Coach import should create:
 
 - Django `User`;
-- `AccountProfile` with `role = coach`;
-- optional `UserPlayerLink` rows with `relationship = coach` if explicit links are provided.
+- `AccountProfile` with `role = coach`.
 
 It should not create:
 
 - `players.Player`;
 - a new Coach model;
+- `UserPlayerLink` rows in Coach Import Phase 1;
 - Analytics observations;
 - staff/superuser permissions.
 
@@ -284,7 +383,7 @@ Justification:
 
 Revisit only if future LeagueHub/team-roster architecture needs canonical staff assignments.
 
-## 6. Evaluation Permissions
+## 7. Evaluation Permissions
 
 ### Submission Rules
 
@@ -352,7 +451,7 @@ Guest evaluators:
 - can view/edit their own draft/reopened evaluations;
 - should not get all-evaluation review unless staff/admin.
 
-## 7. Player Evaluation Submission
+## 8. Player Evaluation Submission
 
 ### Workflow
 
@@ -368,12 +467,12 @@ Proposed flow:
 6. Player saves draft or submits.
 7. System records evaluator user and role snapshot as player.
 
-### Self-Evaluation Decision
+### Self-Evaluation Rule
 
-Recommendation for Evaluation Access V1:
+Decision for Evaluation Access V1:
 
 ```text
-Do not allow self-evaluation by default.
+Block self-evaluation.
 ```
 
 Reasoning:
@@ -387,10 +486,6 @@ Implementation guidance:
 - add a permission/service check that blocks a user from evaluating a player linked to them by active primary or active `self` relationship;
 - if self-evaluation is later desired, make it an explicit cycle setting or observation metadata flag.
 
-Open question:
-
-- confirm whether VCB wants self-evaluation included in the pilot.
-
 ### Form Reuse
 
 Reuse the existing dynamic assessment form and question-set rendering:
@@ -401,7 +496,7 @@ Reuse the existing dynamic assessment form and question-set rendering:
 
 The UI copy may say "Evaluation" rather than "Coach Assessment" for player-facing screens, but the underlying observation type can remain `coach_assessment` for this increment unless architecture is updated.
 
-## 8. Player "My Evaluations" View
+## 9. Player "My Evaluations" View
 
 ### Purpose
 
@@ -429,10 +524,10 @@ Only submitted observations should be shown. Draft or reopened observations shou
 
 ### Evaluator Visibility
 
-Recommendation for Evaluation Access V1:
+Decision for Evaluation Access V1:
 
 ```text
-Hide evaluator names from player-facing results by default.
+Hide evaluator names from player-facing results.
 Show evaluator role only.
 ```
 
@@ -442,10 +537,6 @@ Reasoning:
 - anonymity reduces peer pressure and retaliation risk;
 - coaches can still see evaluator identity in review views.
 
-Open question:
-
-- confirm whether staff wants player-facing evaluations to show evaluator names, role-only, or anonymous.
-
 ### Privacy Boundaries
 
 Players must not be able to:
@@ -456,7 +547,7 @@ Players must not be able to:
 - see staff-only notes if future note types are added;
 - see draft/reopened evaluations as final feedback.
 
-## 9. Coach Review View
+## 10. Coach Review View
 
 ### Purpose
 
@@ -500,6 +591,8 @@ Coach review should support filtering by:
 
 Team and division should come from `players.Player.team_name` and `players.Player.division` for the target player.
 
+Coach review should show submitted evaluations only by default. Draft and reopened observations remain visible only through existing owner/staff workflows.
+
 ### Sorting
 
 Default sorting:
@@ -546,7 +639,7 @@ Coach review detail should show:
 
 Coaches should not be able to reopen submitted observations unless they also have staff review permission.
 
-## 10. Service Ownership
+## 11. Service Ownership
 
 ### accounts
 
@@ -557,7 +650,6 @@ Owns:
 - email normalization and duplicate checks;
 - temporary password generation;
 - `AccountProfile.role = coach`;
-- user-player coach links if imported;
 - staff-only coach import permissions.
 
 Recommended new services:
@@ -583,7 +675,7 @@ Owns:
 - player matching;
 - player lookup helpers.
 
-Coach import may look up players for optional coach links, but it must not create or merge players.
+Coach import should not look up or link players in Phase 1. Future coach-to-player linking may use player lookup helpers, but it must not create or merge players.
 
 ### analytics
 
@@ -627,7 +719,7 @@ analytics.services.permissions.can_view_evaluator_identity(user, observation)
 
 Views should call these helpers and raise `PermissionDenied` when checks fail.
 
-## 11. Recommended Routes
+## 12. Recommended Routes
 
 ### Coach Import
 
@@ -636,9 +728,8 @@ Accounts-owned, staff-only:
 ```text
 /accounts/imports/coaches/
 /accounts/imports/coaches/new/
-/accounts/imports/coaches/<int:batch_id>/preview/
-/accounts/imports/coaches/<int:batch_id>/confirm/
-/accounts/imports/coaches/<int:batch_id>/
+/accounts/imports/coaches/preview/
+/accounts/imports/coaches/confirm/
 ```
 
 Route names:
@@ -648,10 +739,9 @@ accounts:coach-import-list
 accounts:coach-import-new
 accounts:coach-import-preview
 accounts:coach-import-confirm
-accounts:coach-import-detail
 ```
 
-If no persistent batch model is added, the route set can be smaller, but a preview/confirm workflow is strongly recommended for duplicate handling and one-time password display.
+Phase 1 should avoid a persistent coach import batch model unless absolutely necessary. If implementation discovers that a persistent model is required, document that before adding migrations and then use detail routes such as `/accounts/imports/coaches/<int:batch_id>/`. Without a persistent model, duplicate handling and password exposure rules must remain explicit in the upload/preview/confirm flow.
 
 ### Evaluation Submission
 
@@ -717,7 +807,7 @@ Avoid colliding with existing staff-only:
 
 The existing staff review can remain staff-only and preserve reopen behavior. Coach review should be read-only unless the user also has staff permission.
 
-## 12. Security And Privacy
+## 13. Security And Privacy
 
 ### Role-Based Access
 
@@ -734,7 +824,7 @@ Do not use name matching, email matching, player import metadata, or URL ownersh
 
 ### Evaluator Visibility
 
-Recommended default:
+Evaluation Access V1 default:
 
 - coaches and staff can see evaluator names;
 - players see evaluator role only;
@@ -751,7 +841,7 @@ Implementation should include tests for:
 - staff can access staff review and coach review;
 - anonymous users are redirected or denied.
 
-## 13. Files Likely To Create
+## 14. Files Likely To Create
 
 Documentation:
 
@@ -778,7 +868,7 @@ Analytics evaluation access:
 
 Tests may remain in existing app test modules or be split if the project later adopts package-style tests.
 
-## 14. Files Likely To Modify
+## 15. Files Likely To Modify
 
 Accounts:
 
@@ -802,28 +892,31 @@ Analytics:
 - `analytics/templates/analytics/base.html` if navigation needs new links
 - `analytics/tests.py`
 
-No migrations are expected unless implementation chooses to persist coach import batches. If a persistent coach import batch is needed, create a dedicated implementation plan before adding models.
+No migrations are expected for Phase 1. Do not add a persistent coach import batch model unless implementation discovers it is absolutely necessary and the need is documented before adding models.
 
-## 15. Implementation Phases
+## 16. Implementation Phases
 
 ### Phase 0: Planning And Decisions
 
 Purpose:
 
-- finalize open product decisions before code.
+- record product and architecture decisions before code.
 
-Decisions required:
+Decisions recorded:
 
-- whether self-evaluation is allowed;
-- whether player-facing results show evaluator names, role only, or anonymous labels;
-- whether coach import needs persistent batches or can be session/file based;
-- whether coach-to-player links are imported in this version;
-- whether coach accounts are active immediately by default.
+- self-evaluation is blocked;
+- player-facing results show evaluator role/category only, not evaluator names;
+- coach import avoids a persistent batch model in Phase 1 unless absolutely necessary;
+- coach-to-player links are not imported in Coach Import Phase 1;
+- imported coach accounts are active by default and require password change;
+- authenticated guest evaluators may submit evaluations but cannot access coach review;
+- coach review shows submitted evaluations only by default.
 
 Deliverables:
 
-- approved implementation prompt for Phase 1;
-- any needed updates to user-facing documentation after decisions.
+- this plan updated with Phase 0 decisions.
+
+Status: complete.
 
 ### Phase 1: Coach Import
 
@@ -924,7 +1017,7 @@ Deliverables:
 - updated user manual;
 - freeze note or summary document.
 
-## 16. Tests Required
+## 17. Tests Required
 
 ### Coach Import Tests
 
@@ -939,6 +1032,7 @@ Deliverables:
 - inactive import creates inactive account;
 - invalid/missing required fields produce row errors;
 - import summary counts created/skipped/conflict/error rows;
+- coach import does not create coach-to-player links in Phase 1;
 - coach import pages require staff/superuser.
 
 ### Permission Tests
@@ -949,7 +1043,7 @@ Deliverables:
 - staff can submit;
 - guest evaluator can submit if authenticated;
 - role snapshot matches account profile role;
-- self-evaluation is blocked or allowed according to final decision;
+- self-evaluation is blocked;
 - coach review access does not grant Account Operations access;
 - player review access is limited to linked self player.
 
@@ -968,7 +1062,7 @@ Deliverables:
 - self-linked player can view submitted evaluations about self;
 - player cannot view another player's evaluation detail;
 - draft/reopened observations are hidden from final results;
-- evaluator name is hidden or shown according to final decision;
+- evaluator name is hidden from player-facing results;
 - evaluator email is never shown to player;
 - multiple self links are handled safely.
 
@@ -981,6 +1075,7 @@ Deliverables:
 - coach can filter by team;
 - coach can filter by date range;
 - coach can filter by cycle;
+- coach review shows submitted evaluations by default;
 - player cannot access coach review;
 - guest evaluator cannot access coach review;
 - coach cannot reopen submitted observation unless staff;
@@ -994,7 +1089,7 @@ Deliverables:
 - existing player import provisioning still works;
 - existing Analytics command center still works.
 
-## 17. Risks
+## 18. Risks
 
 - Coach import can accidentally create duplicate users if email normalization is weak.
 - Player-facing result pages can expose another player's private evaluations if self-link checks are incomplete.
@@ -1002,35 +1097,24 @@ Deliverables:
 - Coach review could accidentally grant staff-only abilities such as reopening observations.
 - Temporary passwords can leak if stored in summaries, logs, messages, or metadata.
 - Team and division filtering may become stale if player roster data is outdated.
-- Allowing or blocking self-evaluation affects reporting interpretation; this needs explicit product agreement.
+- Blocking self-evaluation may disappoint users who expect reflection workflows; future self-evaluation should be explicitly labeled and reported separately.
 - No audit logging exists, so staff account operations and coach imports have limited historical operator visibility.
 
-## 18. Open Questions
-
-1. Should self-evaluation be blocked for the pilot, or allowed with an explicit self-evaluation label?
-2. Should players see evaluator names, evaluator role only, or fully anonymous results?
-3. Should imported coach accounts be active immediately by default?
-4. Should coach import support coach-to-player links in the first implementation, or only create coach accounts?
-5. Should coach import persist a reusable import batch model, or is a simpler preview/confirm workflow sufficient?
-6. Should coach review include draft/reopened observations, or submitted-only by default?
-7. Should guest evaluators be allowed to submit evaluations in the pilot?
-8. Should coach accounts created manually and by import use the same one-time temporary password display UI?
-
-## 19. Recommended First Implementation Phase
+## 19. Open Questions
 
-Start with Phase 0: Planning And Decisions.
+1. Should coach accounts created manually and by import use the same one-time temporary password display UI?
+2. Should coach import allow optional guest evaluator rows, or should it strictly reject non-coach roles?
+3. Should coach import support an inactive-account option in the upload UI, or only via CSV `is_active` column?
+4. Should Phase 1 expose a coach import history page if no persistent import batch model is added?
+5. What later roadmap should own coach/team/player roster assignment?
 
-Before writing application code, resolve:
+## 20. Recommended First Implementation Phase
 
-- self-evaluation rule;
-- player-facing evaluator visibility;
-- coach import active/inactive default;
-- whether coach import creates coach-to-player links;
-- whether coach import requires a persistent batch model.
+Phase 0 is complete.
 
-After those decisions, implement Phase 1: Coach Import. It is the cleanest first build because it is accounts-owned, does not require changing Analytics observation behavior, and provides the coach accounts needed for the later evaluation-access pilot.
+The first implementation phase should be Phase 1: Coach Import. It is the cleanest first build because it is accounts-owned, does not require changing Analytics observation behavior, and provides the coach accounts needed for the later evaluation-access pilot.
 
-## 20. Definition Of Done For This Roadmap
+## 21. Definition Of Done For This Roadmap
 
 Evaluation Access V1 is complete when:
 
@@ -1038,9 +1122,9 @@ Evaluation Access V1 is complete when:
 - imported coach accounts have role `coach`;
 - temporary password behavior is safe and one-time;
 - coaches can evaluate players;
-- players can evaluate other players according to the agreed self-evaluation rule;
+- players can evaluate other players, with self-evaluation blocked;
 - evaluator identity and role snapshots are correct;
-- players can view submitted evaluations about themselves only;
+- players can view submitted evaluations about themselves only, with evaluator role/category but not evaluator names;
 - coaches can view and filter all submitted evaluations;
 - staff retains existing review and reopen capabilities;
 - players cannot access other players' private evaluation results;
```

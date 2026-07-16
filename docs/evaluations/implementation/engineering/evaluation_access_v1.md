# Evaluation Access V1 Engineering Plan

> Historical implementation record.
> This document preserves the plan and decisions used to implement Evaluation Access V1. For current behavior, use [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the relevant subsystem summaries.

Status: COMPLETE and FROZEN.

Frozen on: 2026-07-10.

Self-Evaluation extension added on: 2026-07-11.

## 1. Goal

Document the completed Platform V1 operational work needed for roster-based evaluations.

The target stopping point is:

- players can be imported;
- coaches can be imported;
- coaches can evaluate players;
- players can evaluate one another and themselves with explicit evaluation type labels;
- players can view evaluations about themselves;
- coaches can view and filter all evaluations.

This plan extends the frozen Players V1, Analytics V1, Account Management V1, and Platform V1 Account Operations work. It does not introduce a new architecture version. It completes the practical access and roster workflows needed to pilot evaluations with real teams.

## 2. Current Platform Context

Existing completed capabilities:

- `players` owns canonical `players.Player` identity, imports, matching, source rows, aliases, identifiers, and tags.
- `accounts` owns Django `User`, `AccountProfile`, `AccountRole`, `UserPlayerLink`, account provisioning, username/email/password services, account operations, and forced password change.
- `analytics` owns `Observation`, `ObservationResponse`, `EvaluatorRole`, question sets, coach assessments, staff review, player search/profile/timeline, comparison, draft context, command center, and metrics.
- Any authenticated user can currently submit coach assessments through `analytics.services.permissions.can_submit_coach_assessment()`.
- Existing `Observation` records already store evaluator user, evaluator role FK, and evaluator role snapshot fields.
- Existing account roles include `coach`, `player`, `staff`, `guest_evaluator`, `parent`, and `admin`.
- Existing account links support `self`, `parent`, `guardian`, `coach`, and `staff` relationships.

Important completed additions:

- Coach import is implemented in `accounts` as a staff-only CSV workflow.
- Player-facing evaluation submission is implemented for authenticated evaluator roles.
- Player-facing "My Evaluations" is implemented for active self-linked players with evaluator identity hidden.
- Coach review of all submitted evaluations is implemented as a coach-accessible, read-only Analytics surface.
- Evaluator role snapshots are resolved from Account Management role metadata.
- Staff profile/timeline pages remain staff-facing, while private player result access is handled through "My Evaluations."

## 3. Phase 0 Decisions

Status: complete.

These product and architecture decisions are recorded before implementation begins.

### Self-Evaluation

Decision:

```text
Originally block self-evaluation for Evaluation Access V1.
```

Rationale:

The initial goal was coach and peer evaluation. Self-evaluation was deferred until it could be labeled and reported separately.

Updated decision:

```text
Allow player self-evaluation when the evaluator has an active self link to the target player.
Store the server-derived evaluation perspective snapshot on every observation.
```

Rationale:

The platform now supports separate `self`, `peer`, `coach`, `staff`, and `guest` perspectives. Self-evaluations are explicitly labeled as Self Evaluation, are distinct from peer evaluations, and require an active self link.

### Player-Facing Evaluator Visibility

Decision:

```text
Players should not see evaluator names in "My Evaluations."
Players may see evaluator role/category only.
```

Rationale:

Youth player evaluations are sensitive. Hiding names reduces peer pressure and retaliation risk while still allowing coaches and staff to see full evaluator identity in review pages.

### Imported Coach Account Activation

Decision:

```text
Imported coach accounts should be active by default.
Imported coach accounts must still have must_change_password=True.
```

Rationale:

Coach import is intended to reduce operational setup work. Active-by-default makes imported coaches usable immediately while forced password change preserves safety.

### Coach-To-Player Links During Coach Import

Decision:

```text
Do not create coach-to-player links in Coach Import Phase 1.
Coach import should create or reuse coach user accounts only.
```

Rationale:

The immediate blocker is onboarding many coaches quickly. Coach/team/player assignment is a separate roster-management problem and should not block evaluation access.

### Coach Import Persistence

Decision:

```text
Do not add a new coach import batch model in Phase 1 unless absolutely necessary.
Prefer a simple upload/preview/confirm workflow using service read models and one-time result display.
```

Rationale:

Avoid adding models and migrations before proving the workflow. Existing account services can create and reuse users without a persistent import model.

### Guest Evaluator Submission

Decision:

```text
Allow authenticated guest evaluators to submit evaluations.
Do not give guest evaluators coach review access.
```

Rationale:

This keeps the existing broad authenticated-evaluator design while preserving review privacy.

### Coach Review Scope

Decision:

```text
Coach review should show submitted evaluations only by default.
Draft and reopened observations remain visible only through existing owner/staff workflows.
```

Rationale:

Coach review is for final evaluation analysis, not workflow management.

## 4. Strict Scope

This plan covers:

- staff-only coach CSV import and coach account provisioning;
- evaluation permission updates for coaches, players, and staff;
- player-accessible evaluation submission;
- player-accessible "My Evaluations" result view;
- coach-accessible all-evaluations review and filtering;
- service ownership and route planning;
- tests required before production pilot/freeze.

This plan assumes evaluations continue using the existing Analytics observation architecture. The first implementation should reuse the existing `coach_assessment` observation workflow and question-set architecture unless a later approved architecture document renames the workflow.

## 5. Out Of Scope

Do not implement these as part of Evaluation Access V1:

- new canonical `Coach` model;
- new player identity model;
- player merge or account merge;
- duplicate account resolution;
- parent import;
- parent result portal;
- public self-registration;
- email invitations;
- email verification;
- self-service password recovery emails;
- OAuth or SSO;
- audit logging;
- APIs;
- JavaScript dashboards;
- charts;
- exports;
- AI summaries;
- measurement workflows;
- new timeline database models;
- PDP migration.

## 6. Coach Import

### Purpose

Coach import should let staff create or update coach login accounts from a roster-style CSV without manually creating every coach account.

Coach import belongs to `accounts`, not `players` or `analytics`, because it creates Django users and account profiles. It must not create or modify canonical player identity.

Coach Import Phase 1 should create or reuse coach user accounts only. It should not create coach-to-player links yet.

### Recommended CSV Format

Required columns:

- `first_name`
- `last_name`
- `email`

Optional columns:

- `username`
- `team`
- `division`
- `role`
- `is_active`
- `temporary_password`
- `linked_player_ids`
- `linked_player_names`
- `notes`
- `source_id`

Recommended source name:

```text
coach_roster
```

Recommended file naming:

```text
coach_roster_[season]_[division_or_team].csv
```

Examples:

```text
coach_roster_2026_13u_house.csv
coach_roster_2026_15u_aaa.csv
```

### Required Fields

`first_name`, `last_name`, and `email` should be required for automated coach account creation.

Reasoning:

- first and last name are needed for readable account profiles and username generation;
- email is the safest available duplicate-detection key for coaches;
- coaches do not have canonical player identity records, so birthdate-based player provisioning rules do not apply.

### Optional Fields

`username`:

- if present, validate through `accounts.services.username_service`;
- if blank, generate using `firstname.lastname`;
- collisions must be resolved by the username service, not forms or views.

`team` and `division`:

- store as account metadata for now;
- do not create a Team model in this phase;
- use for later filtering and review context.

`role`:

- default to `coach`;
- reject unsupported roles unless a staff import option explicitly allows guest evaluator accounts;
- never grant Django staff/superuser flags from CSV.

`is_active`:

- default to active;
- allow staff to import inactive accounts when preparing accounts before release;
- activation should only set Django `User.is_active`, not mutate links or provenance.

`temporary_password`:

- optional and not recommended;
- if supported, must never be stored in import summaries, metadata, logs, source rows, or prompt records;
- generated random temporary passwords are preferred.

`linked_player_ids` and `linked_player_names`:

- deferred from Coach Import Phase 1;
- may be accepted only as ignored/unmapped context if present in uploaded files;
- should not create `UserPlayerLink` records in Phase 1;
- future coach-to-player linking needs a separate roster-management plan;
- must never create player records from coach import.

### Account Creation

Coach import should create:

- Django `User`;
- `AccountProfile` with `role = coach`.

It should not create:

- `players.Player`;
- a new Coach model;
- `UserPlayerLink` rows in Coach Import Phase 1;
- Analytics observations;
- staff/superuser permissions.

### Username Generation

Username generation remains owned by `accounts.services.username_service`.

Recommended addition:

```text
username_for_person(first_name, last_name)
```

This should use the same normalization rules as `username_for_player()` and default to:

```text
firstname.lastname
```

Views and import forms must not implement username rules.

### Active / Inactive Behavior

Default:

- imported coach accounts are active immediately;
- imported users must change temporary passwords before normal platform access.

If `is_active` is false:

- create the account inactive;
- still create `AccountProfile`;
- do not allow login until staff activates the user.

### Temporary Password Behavior

Coach accounts should use generated random temporary passwords by default.

Rules:

- temporary passwords are shown only once in the import result;
- temporary passwords are never stored;
- `AccountProfile.must_change_password = True`;
- password is set through Django password hashing;
- staff should export/copy the one-time result immediately if needed.

Birthdate-based temporary passwords should remain player-account-specific and should not be used for coaches.

### Duplicate Email / Username Handling

Email:

- normalize through `accounts.services.email_service`;
- if an existing user has the same email and already has role `coach`, treat as an existing account and update safe metadata only if explicitly allowed;
- if an existing user has the same email with another role, mark row as conflict unless staff explicitly chooses to reuse/update;
- never create a second user with the same email when email matching finds an existing user.

Username:

- explicit username must be validated by username service;
- generated username collisions should resolve by suffix;
- manual username conflicts should be reported as row errors or conflicts.

Recommended row statuses:

- `created`
- `updated_existing`
- `already_exists`
- `skipped`
- `conflict`
- `error`

### Import Summary

Import detail should report:

- rows processed;
- users created;
- existing users reused;
- users updated;
- rows skipped;
- conflicts;
- errors;
- accounts activated;
- accounts imported inactive;
- password-change-required count.

The import summary must not include plaintext temporary passwords except in a one-time display object immediately after confirm. Persisted summaries should contain counts and usernames only.

### No Coach Model For Now

Do not add a `Coach` model in Evaluation Access V1.

Justification:

- coach is currently an account role, not canonical baseball identity;
- coach-to-player/team context can be represented by `AccountProfile.metadata` and optional `UserPlayerLink(relationship="coach")`;
- introducing a coach model would require broader team/season modeling that is outside this stopping point.

Revisit only if future LeagueHub/team-roster architecture needs canonical staff assignments.

## 7. Evaluation Permissions

### Submission Rules

Users who can submit evaluations:

- authenticated coaches;
- authenticated players;
- authenticated staff/admin users;
- authenticated guest evaluators, if staff has created those accounts for evaluation purposes.

Unauthenticated users cannot submit evaluations.

For this stopping point, submission should remain broad: any authenticated evaluator may evaluate any active player they know. This preserves the existing Analytics V1 rule while making role snapshots accurate.

### Role Snapshot Requirement

Every submitted evaluation must store:

- evaluator `User`;
- evaluator role FK;
- evaluator role key;
- evaluator role name;
- timestamp;
- target `players.Player`;
- evaluation cycle;
- question-set version.

Role snapshot should come from Account Management role metadata:

- `AccountProfile.role = coach` maps to `EvaluatorRole.coach`;
- `AccountProfile.role = player` maps to `EvaluatorRole.player`;
- `AccountProfile.role = staff` maps to `EvaluatorRole.staff`;
- `AccountProfile.role = admin` maps to `EvaluatorRole.admin`;
- `AccountProfile.role = guest_evaluator` maps to `EvaluatorRole.guest_evaluator`.

Recommended implementation:

- add or extend an Analytics service helper such as `analytics.services.observation_service.evaluator_role_for_user(user)`;
- avoid hard-coding role defaults in views;
- update `create_coach_assessment_observation()` or add a wrapper to snapshot the user's actual role instead of defaulting all callers to coach.

### Viewing Rules

Staff:

- can view all evaluations.

Coaches:

- can view all submitted evaluations through the coach review view;
- can view their own draft/reopened evaluations;
- can edit only their own draft/reopened evaluations.

Players:

- can submit evaluations;
- can view evaluations about themselves through "My Evaluations";
- can view their own draft/reopened evaluations as evaluator if editing/resuming is supported;
- cannot view all evaluations;
- cannot view private results for other players.

Guest evaluators:

- can submit evaluations if authenticated;
- can view/edit their own draft/reopened evaluations;
- should not get all-evaluation review unless staff/admin.

## 8. Player Evaluation Submission

### Workflow

Authenticated player users should be able to access evaluation forms.

Proposed flow:

1. Player signs in.
2. Player opens evaluation list/search.
3. Player selects another active player, or their own linked player record for self evaluation.
4. System opens or creates that evaluator's draft observation for the selected player and current cycle.
5. Player completes ratings and notes.
6. Player saves draft or submits.
7. System records evaluator user, role snapshot as player, and evaluation perspective snapshot as `self` or `peer`.

### Self-Evaluation Rule

Updated decision for Evaluation Access V1:

```text
Allow self-evaluation with explicit labels and perspective snapshots.
```

Reasoning:

- self-evaluations are valuable when clearly separated from peer, coach, staff, and guest evaluations;
- the explicit `evaluation_perspective` snapshot prevents coaches from confusing self feedback with external evaluations;
- the active self-link requirement prevents unrelated users from creating self-labeled records for another player.

Implementation guidance:

- derive perspective server-side; do not accept a client-controlled perspective field;
- allow self evaluation only when an active `self` relationship links the evaluator user to the target player;
- keep self and peer duplicate rules distinct.

### Form Reuse

Reuse the existing dynamic assessment form and question-set rendering:

- no hard-coded question text in templates;
- keep response validation in services/forms;
- keep duplicate protection per evaluator/player/cycle.

The UI copy may say "Evaluation" rather than "Coach Assessment" for player-facing screens, but the underlying observation type can remain `coach_assessment` for this increment unless architecture is updated.

## 9. Player "My Evaluations" View

### Purpose

Players need a private page to view submitted evaluations about themselves.

### Access Rule

A user may access "My Evaluations" only for players linked to that user by active `UserPlayerLink(relationship="self")`.

If the user has multiple active self links, show a selector or list. In normal operation, constraints should allow only one active primary self link per user, but the view should not assume exactly one link exists.

### Data Shown

Recommended initial content:

- evaluation cycle;
- submitted date;
- evaluator role;
- ratings grouped by category;
- freeform notes;
- question prompts and responses;
- status label.

Only submitted observations should be shown. Draft or reopened observations should not appear as final feedback.

### Evaluator Visibility

Decision for Evaluation Access V1:

```text
Hide evaluator names from player-facing results.
Show evaluator role only.
```

Reasoning:

- youth-player evaluations can be sensitive;
- anonymity reduces peer pressure and retaliation risk;
- coaches can still see evaluator identity in review views.

### Privacy Boundaries

Players must not be able to:

- change URL IDs to see another player's results;
- see all evaluations;
- see evaluator email addresses;
- see staff-only notes if future note types are added;
- see draft/reopened evaluations as final feedback.

## 10. Coach Review View

### Purpose

Coaches need a way to review all submitted evaluations and filter them for practical roster decisions.

### Access Rule

Allowed:

- users with `AccountProfile.role = coach`;
- Django staff users;
- Django superusers.

Denied:

- players;
- parents;
- guest evaluators unless also Django staff/superuser;
- anonymous users.

Important distinction:

- `AccountProfile.role = coach` should grant coach review for evaluation pages only.
- It must not grant Django staff access or Account Operations access.

### Filters

Coach review should support filtering by:

- player name;
- target player ID;
- evaluator name;
- evaluator role;
- team;
- division;
- date range;
- evaluation cycle;
- observation status, defaulting to submitted;
- response completion status if useful;
- question/category if later needed.

Team and division should come from `players.Player.team_name` and `players.Player.division` for the target player.

Coach review should show submitted evaluations only by default. Draft and reopened observations remain visible only through existing owner/staff workflows.

### Sorting

Default sorting:

```text
submitted_at descending, player last_name, player first_name
```

Optional sort choices:

- player name;
- evaluator name;
- evaluator role;
- submitted date;
- team;
- division;
- cycle.

### Result Rows

Each row should include:

- player display name;
- division;
- team;
- evaluation cycle;
- evaluator display name;
- evaluator role snapshot;
- submitted date;
- status;
- detail link.

### Detail View

Coach review detail should show:

- target player;
- evaluator identity;
- evaluator role snapshot;
- cycle;
- submitted timestamp;
- grouped responses;
- notes.

Coaches should not be able to reopen submitted observations unless they also have staff review permission.

## 11. Service Ownership

### accounts

Owns:

- coach import/account provisioning;
- username generation;
- email normalization and duplicate checks;
- temporary password generation;
- `AccountProfile.role = coach`;
- staff-only coach import permissions.

Recommended new services:

```text
accounts/services/coach_import_service.py
```

Optional if the workflow needs CSV preview state:

```text
accounts/services/account_import_service.py
```

Do not put coach import logic in `analytics`.

### players

Owns:

- canonical `players.Player`;
- player identity import;
- player matching;
- player lookup helpers.

Coach import should not look up or link players in Phase 1. Future coach-to-player linking may use player lookup helpers, but it must not create or merge players.

### analytics

Owns:

- evaluation submission workflow;
- observation permissions;
- "My Evaluations" read models;
- coach review read models and filtering;
- evaluation detail rendering.

Recommended new or expanded services:

```text
analytics/services/evaluation_access_service.py
analytics/services/evaluation_review_service.py
```

Possible responsibilities:

- resolve evaluator role for a user;
- check whether a user can evaluate a target player;
- check whether a user can view a player's private evaluation results;
- query submitted evaluations for a self-linked player;
- query all evaluations for coach/staff review;
- apply evaluation review filters.

### permissions

Permission checks should live in services, not views.

Recommended additions:

```text
analytics.services.permissions.can_submit_evaluation(user, target_player)
analytics.services.permissions.can_view_my_evaluations(user, player)
analytics.services.permissions.can_view_coach_evaluation_review(user)
analytics.services.permissions.can_view_evaluation_detail(user, observation)
analytics.services.permissions.can_view_evaluator_identity(user, observation)
```

Views should call these helpers and raise `PermissionDenied` when checks fail.

## 12. Recommended Routes

### Coach Import

Accounts-owned, staff-only:

```text
/accounts/imports/coaches/
/accounts/imports/coaches/new/
/accounts/imports/coaches/preview/
/accounts/imports/coaches/confirm/
```

Route names:

```text
accounts:coach-import-list
accounts:coach-import-new
accounts:coach-import-preview
accounts:coach-import-confirm
```

Phase 1 should avoid a persistent coach import batch model unless absolutely necessary. If implementation discovers that a persistent model is required, document that before adding migrations and then use detail routes such as `/accounts/imports/coaches/<int:batch_id>/`. Without a persistent model, duplicate handling and password exposure rules must remain explicit in the upload/preview/confirm flow.

### Evaluation Submission

Analytics-owned:

```text
/analytics/evaluations/
/analytics/evaluations/players/<int:player_id>/
/analytics/evaluations/<int:observation_id>/
/analytics/evaluations/<int:observation_id>/edit/
```

Route names:

```text
analytics:evaluation-list
analytics:evaluation-player
analytics:evaluation-detail
analytics:evaluation-edit
```

These may reuse existing coach-assessment views internally if the UI can remain coherent. If routes are aliased to existing assessment views, keep permission logic centralized.

### My Evaluations

Analytics-owned, player-private:

```text
/analytics/my/evaluations/
/analytics/my/evaluations/players/<int:player_id>/
/analytics/my/evaluations/<int:observation_id>/
```

Route names:

```text
analytics:my-evaluations
analytics:my-evaluations-player
analytics:my-evaluation-detail
```

### Coach Evaluation Review

Analytics-owned, coach/staff:

```text
/analytics/evaluations/review/
/analytics/evaluations/review/<int:observation_id>/
```

Route names:

```text
analytics:evaluation-review-list
analytics:evaluation-review-detail
```

Avoid colliding with existing staff-only:

```text
/analytics/observations/review/
```

The existing staff review can remain staff-only and preserve reopen behavior. Coach review should be read-only unless the user also has staff permission.

## 13. Security And Privacy

### Role-Based Access

- Staff/superuser access remains controlled by Django `User.is_staff` / `User.is_superuser`.
- `AccountProfile.role = coach` grants coach evaluation review only, not Account Operations.
- `AccountProfile.role = player` grants player evaluation submission and private "My Evaluations" access only for self-linked player records.
- `AccountProfile.role = staff` remains metadata unless backed by Django staff/superuser flags for staff-only pages.

### Linked-Player Access

Private player evaluation results must be based on active `UserPlayerLink(relationship="self")`.

Do not use name matching, email matching, player import metadata, or URL ownership assumptions to grant access.

### Evaluator Visibility

Evaluation Access V1 default:

- coaches and staff can see evaluator names;
- players see evaluator role only;
- player-facing pages hide evaluator username/email.

### Accidental Exposure Controls

Implementation should include tests for:

- player cannot view another player's private evaluation result by URL;
- player cannot access all-evaluation review;
- guest evaluator cannot access all-evaluation review;
- coach can access review but cannot access Account Operations;
- staff can access staff review and coach review;
- anonymous users are redirected or denied.

## 14. Files Likely To Create

Documentation:

- `docs/evaluations/implementation/engineering/evaluation_access_v1.md`

Coach import:

- `accounts/services/coach_import_service.py`
- optional `accounts/templates/accounts/coach_import_list.html`
- optional `accounts/templates/accounts/coach_import_upload.html`
- optional `accounts/templates/accounts/coach_import_preview.html`
- optional `accounts/templates/accounts/coach_import_detail.html`

Analytics evaluation access:

- `analytics/services/evaluation_access_service.py`
- `analytics/services/evaluation_review_service.py`
- `analytics/templates/analytics/evaluation_list.html`
- `analytics/templates/analytics/evaluation_form.html` if existing `assessment_form.html` cannot be reused cleanly
- `analytics/templates/analytics/my_evaluations.html`
- `analytics/templates/analytics/my_evaluation_detail.html`
- `analytics/templates/analytics/evaluation_review_list.html`
- `analytics/templates/analytics/evaluation_review_detail.html`

Tests may remain in existing app test modules or be split if the project later adopts package-style tests.

## 15. Files Likely To Modify

Accounts:

- `accounts/forms.py`
- `accounts/urls.py`
- `accounts/views.py`
- `accounts/services/username_service.py`
- `accounts/services/password_service.py` if coach import needs reusable one-time random password helpers
- `accounts/services/account_operations_service.py` only if dashboard cards should link to coach import
- `accounts/tests.py`

Analytics:

- `analytics/assessment_forms.py`
- `analytics/forms.py`
- `analytics/urls.py`
- `analytics/views.py`
- `analytics/services/permissions.py`
- `analytics/services/observation_service.py`
- `analytics/services/coach_assessment_service.py`
- `analytics/templates/analytics/base.html` if navigation needs new links
- `analytics/tests.py`

No migrations are expected for Phase 1. Do not add a persistent coach import batch model unless implementation discovers it is absolutely necessary and the need is documented before adding models.

## 16. Implementation Phases

### Phase 0: Planning And Decisions

Purpose:

- record product and architecture decisions before code.

Decisions recorded:

- self-evaluation is allowed only through an active self link and is labeled separately;
- player-facing results show evaluator role/category only, not evaluator names;
- coach import avoids a persistent batch model in Phase 1 unless absolutely necessary;
- coach-to-player links are not imported in Coach Import Phase 1;
- imported coach accounts are active by default and require password change;
- authenticated guest evaluators may submit evaluations but cannot access coach review;
- coach review shows submitted evaluations only by default.

Deliverables:

- this plan updated with Phase 0 decisions.

Status: complete.

### Phase 1: Coach Import

Purpose:

- staff can import coach accounts from CSV.

Deliverables:

- `accounts.services.coach_import_service`;
- staff-only coach import upload/preview/confirm/result workflow without a persistent import batch model;
- account creation with `AccountProfile.role = coach`;
- username/email duplicate handling;
- random temporary password generation;
- one-time temporary password result display;
- import summary without plaintext password persistence;
- tests.

Status: implemented.

### Phase 2: Evaluation Permission And Role Snapshot Updates

Purpose:

- make evaluation submission role-aware and prepare player/coach access.

Deliverables:

- Analytics permission helpers;
- evaluator-role resolution from account profile;
- correct snapshot for player, coach, staff, admin, and guest evaluator users;
- self-evaluation rule enforced based on Phase 0 decision;
- regression tests proving existing coach assessment behavior still works.

Status: implemented.

### Phase 3: Player Evaluation Submission

Purpose:

- authenticated player users can evaluate other players.

Deliverables:

- player-accessible evaluation list/search;
- dynamic evaluation form reuse;
- player role snapshot;
- duplicate protection per evaluator/player/cycle;
- self-evaluation handling;
- permission tests.

Status: implemented.

Review fixes: completed. Submitted evaluation detail remains limited to the evaluator and staff; the evaluation list labels submitted links as "View My Submission"; profile navigation uses service-derived evaluation permission context.

### Phase 4: Player "My Evaluations"

Purpose:

- players can privately view submitted evaluations about themselves.

Deliverables:

- self-linked player lookup;
- my evaluations list;
- my evaluation detail;
- evaluator identity hiding according to Phase 0 decision;
- no access to other players' private results;
- tests.

Status: implemented.

Review fixes: completed. Account Profile no longer imports Analytics permission services in `accounts.views`; Analytics owns profile navigation eligibility through an Analytics template tag. Player-facing My Evaluations read models expose observation IDs and player-safe labels instead of full observations, inactive self links and inactive players do not grant access, forbidden existing details return 403 while missing details return 404, and responses render in deterministic question order.

### Phase 5: Coach Review And Filtering

Purpose:

- coaches can view and filter all submitted evaluations.

Deliverables:

- coach/staff evaluation review list;
- review detail;
- filters by player, evaluator, role, team, date, and cycle;
- read-only behavior for coaches;
- staff behavior preserved;
- tests.

Status: implemented.

Review notes: Coach review is implemented as an Analytics-owned read-only submitted-evaluation surface. It uses explicit coach-review permission helpers, an `evaluation_review_service` for filter parsing/query/read models, thin views, and presentation-only templates. Coach review remains separate from existing staff observation review; coaches cannot reopen submitted observations through the coach review routes.

### Phase 6: Final Pilot / Freeze

Purpose:

- verify the roster-based evaluation workflow is production-ready.

Review areas:

- coach import safety;
- account activation and password behavior;
- permission boundaries;
- player privacy;
- coach review accuracy;
- query performance;
- UX clarity;
- documentation updates.

Deliverables:

- final review/fix pass;
- updated user manual;
- freeze note or summary document.

## 17. Tests Required

### Coach Import Tests

- valid coach CSV creates active coach account;
- imported coach has `AccountProfile.role = coach`;
- imported coach must change password;
- temporary password shown once and not persisted;
- explicit username is normalized/validated by username service;
- generated username uses `firstname.lastname` and suffixes collisions;
- duplicate email with existing coach is handled safely;
- duplicate email with non-coach user becomes conflict;
- inactive import creates inactive account;
- invalid/missing required fields produce row errors;
- import summary counts created/skipped/conflict/error rows;
- coach import does not create coach-to-player links in Phase 1;
- coach import pages require staff/superuser.

### Permission Tests

- anonymous user cannot submit;
- coach can submit;
- player can submit;
- staff can submit;
- guest evaluator can submit if authenticated;
- role snapshot matches account profile role;
- self-evaluation requires an active self link and stores `evaluation_perspective=self`;
- coach review access does not grant Account Operations access;
- player review access is limited to linked self player.

### Player Submission Tests

- player can open evaluation form for another active player;
- player can open evaluation form for their own active self-linked player record;
- player cannot evaluate inactive player;
- player cannot create duplicate evaluation for same player/cycle;
- player can save draft;
- player can submit with required responses;
- missing required responses are blocked;
- player role snapshot is stored.

### My Evaluations Tests

- self-linked player can view submitted evaluations about self;
- player cannot view another player's evaluation detail;
- draft/reopened observations are hidden from final results;
- evaluator name is hidden from player-facing results;
- evaluator email is never shown to player;
- multiple self links are handled safely.

### Coach Review Tests

- coach can view submitted evaluations;
- coach can filter by player;
- coach can filter by evaluator;
- coach can filter by evaluator role;
- coach can filter by team;
- coach can filter by date range;
- coach can filter by cycle;
- coach review shows submitted evaluations by default;
- player cannot access coach review;
- guest evaluator cannot access coach review;
- coach cannot reopen submitted observation unless staff;
- staff review behavior remains unchanged.

### Regression Tests

- existing staff observation review still works;
- existing coach assessment list/edit/detail still works;
- existing Account Operations permissions still work;
- existing player import provisioning still works;
- existing Analytics command center still works.

## 18. Risks

- Coach import can accidentally create duplicate users if email normalization is weak.
- Player-facing result pages can expose another player's private evaluations if self-link checks are incomplete.
- Defaulting evaluator role to `coach` can corrupt player-submitted role snapshots unless fixed.
- Coach review could accidentally grant staff-only abilities such as reopening observations.
- Temporary passwords can leak if stored in summaries, logs, messages, or metadata.
- Team and division filtering may become stale if player roster data is outdated.
- Self-evaluation must remain clearly labeled so coaches do not confuse it with external feedback.
- No audit logging exists, so staff account operations and coach imports have limited historical operator visibility.

## 19. Open Questions

1. Should coach accounts created manually and by import use the same one-time temporary password display UI?
2. Should coach import allow optional guest evaluator rows, or should it strictly reject non-coach roles?
3. Should coach import support an inactive-account option in the upload UI, or only via CSV `is_active` column?
4. Should Phase 1 expose a coach import history page if no persistent import batch model is added?
5. What later roadmap should own coach/team/player roster assignment?

## 20. Implementation Sequence

Completed sequence:

1. Phase 0: planning decisions.
2. Phase 1: coach import.
3. Phase 2: evaluation permission and role snapshot updates.
4. Phase 3: player evaluation submission.
5. Phase 4: player "My Evaluations."
6. Phase 5: coach review and filtering.
7. Phase 6: final pilot/freeze documentation.

## 21. Definition Of Done For This Roadmap

Evaluation Access V1 is complete when:

- [x] staff can import coach accounts safely from CSV;
- [x] imported coach accounts have role `coach`;
- [x] temporary password behavior is safe and one-time;
- [x] coaches can evaluate players;
- [x] players can evaluate other players and themselves with explicit evaluation perspective labels;
- [x] evaluator identity, role snapshots, and evaluation perspective snapshots are correct;
- [x] players can view submitted evaluations about themselves only, with evaluator role/category but not evaluator names;
- [x] coaches can view and filter all submitted evaluations;
- [x] staff retains existing review and reopen capabilities;
- [x] players cannot access other players' private evaluation results;
- [x] coaches do not gain Account Operations access from `AccountProfile.role = coach`;
- [x] focused and regression tests pass;
- [x] user-facing documentation is updated.

## 22. Production-Readiness Assessment

Evaluation Access V1 is production-ready for the documented roster-based evaluation pilot scope.

The completed stopping point is:

- players can be imported and optionally provisioned with login accounts;
- coaches can be imported from CSV;
- coaches can evaluate players;
- players can evaluate other players;
- self-evaluation is allowed and explicitly labeled;
- evaluator identity, role snapshots, and evaluation perspective snapshots are stored;
- players can privately view submitted evaluations about themselves;
- player-facing results hide evaluator identity and show evaluator role/category only;
- coaches can view and filter all submitted evaluations;
- staff review and reopen workflows remain separate and functional.

## 23. Architecture Assessment

Subsystem boundaries remain consistent with the Platform V1 architecture:

- `accounts` owns authentication, account roles, password behavior, account provisioning, user-player links, and coach import.
- `players` owns canonical player identity, player import, player matching, and player provenance.
- `analytics` owns evaluation submission, evaluator snapshots, player-safe result views, coach review, filtering, and read models.
- `drafts` remains separate and continues to own draft workflows.
- `pdp` remains legacy/transitionary and was not migrated as part of Evaluation Access V1.

The Self-Evaluation extension added an Analytics migration for the `Observation.evaluation_perspective` snapshot and related uniqueness/index constraints.

## 24. Security And Privacy Assessment

Security and privacy posture:

- unauthenticated users cannot submit or review evaluations;
- parent accounts cannot submit evaluations by default;
- player accounts can submit peer evaluations and self evaluations when an active self link exists;
- players can view only submitted evaluations about active self-linked player records;
- inactive self links and inactive players do not grant self-evaluation or "My Evaluations" access;
- player-facing result pages hide evaluator names, usernames, email addresses, and account metadata;
- coach review exposes evaluator display names and role/category but not evaluator email, password state, import metadata, or account metadata;
- guest evaluators can submit but cannot access coach review;
- coach role grants coach evaluation review only, not Django staff access or Account Operations access;
- staff review and reopen controls remain limited to Django staff/superusers through the existing staff review workflow;
- temporary passwords remain one-time display values and are not persisted in summaries, metadata, or later pages.

## 25. Performance Assessment

The implemented review and result surfaces use service-owned query construction and `select_related()` for common related objects such as player, cycle, evaluator, and evaluator role.

The current dataset size expected for the production pilot is compatible with server-rendered filtering and table views. Future larger deployments may need pagination, indexes tuned to real usage, or export/reporting workflows, but those are outside Evaluation Access V1.

## 26. End-To-End Workflow Assessment

The implemented workflow supports:

1. staff imports players;
2. staff optionally provisions and activates player accounts;
3. staff imports coaches;
4. coaches and provisioned players complete first-login password changes when required;
5. coaches submit evaluations;
6. players submit peer evaluations;
7. players submit self evaluations when they have an active self link;
8. submitted evaluations store evaluator identity, role snapshots, and evaluation perspective snapshots;
9. players view submitted evaluations about themselves without seeing evaluator names;
10. coaches view and filter all submitted evaluations;
11. staff review and reopen remain available through the existing staff-only workflow.

## 27. Documentation Assessment

Documentation has been reconciled for the completed Evaluation Access V1 scope:

- `docs/USER_MANUAL.md` describes coach import, evaluation submission, player "My Evaluations," and coach review.
- this engineering plan records all Evaluation Access V1 phases, decisions, deferred work, and freeze status.
- top-level architecture continues to define subsystem ownership and dependency direction.

## 28. Manual Pilot Checklist

Use this checklist for a manual production pilot:

- [ ] Import sample players through `/analytics/imports/`.
- [ ] Provision and activate sample player accounts during player import, when appropriate.
- [ ] Import sample coaches through `/accounts/imports/coaches/`.
- [ ] Copy one-time temporary passwords from the immediate result pages.
- [ ] Log in as a coach and complete forced password change.
- [ ] Log in as a player and complete forced password change.
- [ ] Submit an evaluation as a coach.
- [ ] Submit a peer evaluation as a player.
- [ ] Submit a self evaluation as a player and confirm it is labeled Self Evaluation.
- [ ] View `/analytics/my/evaluations/` as a player.
- [ ] Confirm evaluator identity is hidden from the player-facing result.
- [ ] View `/analytics/evaluation-review/` as a coach.
- [ ] Filter coach review by player, evaluator, role, team, division, cycle, and date.
- [ ] Confirm a player cannot access coach review.
- [ ] Confirm a guest evaluator cannot access coach review.
- [ ] Confirm staff review at `/analytics/observations/review/` still works.
- [ ] Reopen a submitted observation through staff review only.

## 29. Deferred Work

Deferred work remains outside Evaluation Access V1:

- audit logging;
- account merge;
- duplicate account resolution;
- coach-to-player roster assignment;
- parent import;
- parent portal;
- full coach portal;
- full player portal;
- email invitations;
- email verification;
- self-service password recovery;
- APIs;
- JavaScript dashboards;
- charts;
- exports;
- LeagueHub;
- video;
- recruiting;
- new observation types;
- PDP retirement;
- broader self-evaluation reporting beyond the current explicit perspective label and filters.

## 30. Freeze Declaration

Evaluation Access V1 is COMPLETE and FROZEN as of 2026-07-10.

The Self-Evaluation extension is complete as of 2026-07-11.

Future changes should be planned as a new phase or version unless they are bug fixes, security fixes, documentation corrections, or operational support for the frozen V1 scope.

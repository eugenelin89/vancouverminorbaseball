# Prompt 48 - Account Management

## User Prompt

```text
Reconcile Platform V1 Account Operations documentation only.

Do NOT change application code.

Do NOT modify Python files.

Do NOT modify models, services, forms, views, URLs, templates, middleware, or tests.

Do NOT implement Phase F.

==================================================
Goal
==================================================

Update documentation so it accurately reflects the current implemented state of Platform V1 Account Operations through Phase E.

This is documentation cleanup only before the Phase F production hardening/freeze review.

==================================================
Read
==================================================

Read:

- docs/ARCHITECTURE.md
- docs/account_management/V1_SUMMARY.md
- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/platform_v1_account_operations.md
- docs/prompts/prompt_41_account_management.md
- docs/prompts/prompt_42_account_management.md
- docs/prompts/prompt_43_account_management.md
- docs/prompts/prompt_44_account_management.md
- docs/prompts/prompt_45_account_management.md
- docs/prompts/prompt_46_account_management.md
- docs/prompts/prompt_47_account_management.md

Review implementation only as needed:

- accounts/
- players/
- analytics/
- drafts/
- pdp/

==================================================
Required Documentation Updates
==================================================

1. Fix phase naming/status drift

Clarify that the implemented Platform V1 Account Operations sequence is:

- Phase A — Account Operations Foundation
- Phase B — Manual Account Creation
- Phase C — Account Lifecycle and Link Management
- Phase D — Operational Password Reset
- Phase E — Bulk Operations
- Phase F — Production Hardening / Freeze

If platform_v1_account_operations.md currently labels bulk operations differently, update it to match this sequence.

2. Update V1_SUMMARY.md

Remove or revise stale “current limitations” entries that are now implemented, including:

- staff account operations dashboard/list/detail
- manual account creation
- player account creation
- account activation/deactivation
- username/email/role editing
- user-player link management
- operational password reset
- bulk account operations

Keep true limitations, including:

- no audit logging
- no account merge
- no duplicate account resolution
- no invitation/email verification flow
- no coach import
- no parent import
- no portal dashboards
- no self-service password recovery email flow

3. Add Account Operations section

In V1_SUMMARY.md, add or update a section summarizing Platform V1 Account Operations.

Include:

- implemented routes
- main staff workflows
- service ownership
- security model
- password exposure rules
- role/staff distinction
- provenance rules
- deferred work

4. Clarify staff role semantics

Document clearly:

- `AccountProfile.role = staff` is platform metadata only
- it does not grant Django staff access
- staff-only page access depends on `User.is_staff` or `User.is_superuser`
- creating or editing an account role does not modify Django staff/superuser flags

5. Clarify Phase F

Document that Phase F is not a feature phase.

Phase F should be:

- production hardening
- architecture review
- security review
- performance review
- UX consistency review
- documentation finalization
- freeze declaration

6. Update ARCHITECTURE.md only if necessary

If the top-level architecture document has stale status or obvious account-operations gaps, update it lightly.

Do not rewrite it.

==================================================
Do NOT Change
==================================================

Do NOT implement:

- Phase F
- audit logging
- account merge
- duplicate account resolution
- invitations
- email verification
- coach import
- parent import
- portals
- API endpoints
- JavaScript
- application code

==================================================
Verification
==================================================

Run:

git diff --check

If documentation-only changes are made, no Django test run is required unless documentation references generated checks or code changed accidentally.

==================================================
Final Report
==================================================

Report:

- files modified
- documentation corrections made
- stale limitations removed or updated
- true limitations retained
- confirmation that no application code was changed
- confirmation that Phase F was NOT implemented
```

## App / Subsystem

Account Management

## Work Commit

`08f58c4 Reconcile account operations documentation`

## Work Commit Diff

```diff
commit 08f58c4df0efcad938224210cd8951ee02a9aef8
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 8 11:14:52 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 8 11:14:52 2026 -0700

    Reconcile account operations documentation
---
 docs/ARCHITECTURE.md                               |   8 +-
 docs/account_management/V1_SUMMARY.md              | 118 ++++++++++++++++---
 .../engineering/platform_v1_account_operations.md  | 126 ++++++++++++++-------
 3 files changed, 191 insertions(+), 61 deletions(-)

diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 7487879..ed01946 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -135,6 +135,9 @@ Responsibilities:
 - platform login/logout/password-change routes
 - forced password-change middleware
 - account landing URL behavior
+- staff Account Operations dashboard/list/detail
+- manual account creation and player-account creation
+- account lifecycle, link management, operational password reset, and safe bulk account actions
 
 What it owns:
 
@@ -153,7 +156,7 @@ What it must not own:
 
 Current status:
 
-V1 complete and frozen for Phases 1-4.
+Core V1 is complete. Platform V1 Account Operations is implemented through Phase E and is awaiting Phase F production hardening/freeze review.
 
 Documentation:
 
@@ -268,7 +271,7 @@ Dependency guidance:
 | --- | --- | --- |
 | Players | V1 | Complete |
 | Analytics | V1 | Complete |
-| Account Management | V1 | Complete / Frozen |
+| Account Management | V1 | Core complete; Account Operations Phase F pending |
 | Drafts | Active | Active development |
 | PDP | Legacy | Transitionary |
 | LeagueHub | Planned | Planned |
@@ -282,6 +285,7 @@ The platform currently has:
 - production-ready player import and matching workflow
 - production-ready Analytics V1 workflow
 - production-ready Account Management V1 foundation
+- staff-facing Account Operations implemented through Phase E
 - account provisioning from player imports
 - forced password-change account flow
 - staff-only Analytics command center and reporting tables
diff --git a/docs/account_management/V1_SUMMARY.md b/docs/account_management/V1_SUMMARY.md
index db921ce..12bb58e 100644
--- a/docs/account_management/V1_SUMMARY.md
+++ b/docs/account_management/V1_SUMMARY.md
@@ -209,6 +209,89 @@ Authentication behavior:
 - Non-staff users land at `/accounts/profile/`.
 - PDP routes and middleware remain installed for legacy coexistence.
 
+## Platform V1 Account Operations
+
+Platform V1 Account Operations extends Account Management V1 with staff-facing production operations. These workflows are implemented through Phase E and are ready for Phase F production hardening/freeze review.
+
+Implemented sequence:
+
+- Phase A - Account Operations Foundation.
+- Phase B - Manual Account Creation.
+- Phase C - Account Lifecycle and Link Management.
+- Phase D - Operational Password Reset.
+- Phase E - Bulk Operations.
+- Phase F - Production Hardening / Freeze. This is pending and is not a feature phase.
+
+Implemented routes:
+
+- `/accounts/`: staff Account Operations dashboard.
+- `/accounts/users/`: staff account list with search, filters, and safe bulk actions.
+- `/accounts/users/<id>/`: account detail page.
+- `/accounts/create/`: account-only creation for coach, parent, staff, guest evaluator, and other non-player login accounts.
+- `/accounts/create/player/`: player-account creation for an existing canonical `players.Player`.
+- `/accounts/users/<id>/edit/`: username, email, role, and active-state editing.
+- `/accounts/users/<id>/links/`: user-player link create/deactivate/reactivate/primary management.
+- `/accounts/users/<id>/password/`: operational password reset.
+
+Main staff workflows:
+
+- review account summary cards and issue queues;
+- search and filter accounts by username, name, email, role, active status, staff/superuser status, import status, password-change requirement, and link status;
+- create account-only users without creating players;
+- create player login accounts from existing `players.Player` records;
+- edit username, email, `AccountProfile.role`, and active status;
+- activate and deactivate accounts without deleting profile, link, or provenance history;
+- link and unlink users and players through `UserPlayerLink`;
+- reset a user's password and require password change on next login;
+- bulk activate, deactivate, require password change, and clear password-change requirement.
+
+Service ownership:
+
+- `account_query_service` owns account list query/filter behavior.
+- `account_operations_service` owns staff Account Operations orchestration and read models.
+- `username_service` owns username normalization and collision rules.
+- `password_service` owns temporary-password generation and password-change flags.
+- `link_service` owns all user-player link rules.
+- `profile_service` owns account role updates.
+- `provisioning_service` owns import/player account provisioning.
+
+Security model:
+
+- Account Operations pages are staff-only and require Django `User.is_staff` or `User.is_superuser`.
+- `AccountProfile.role` is platform metadata only.
+- `AccountProfile.role = staff` does not grant Django staff access.
+- `AccountProfile.role = admin` does not grant Django superuser access.
+- Creating or editing an account role never mutates `User.is_staff` or `User.is_superuser`.
+- Assigning the platform `admin` role is restricted to Django superusers even though the role itself does not grant Django admin access.
+- The system blocks self-deactivation and last-active-superuser deactivation.
+
+Password exposure rules:
+
+- Temporary passwords are shown only immediately after account creation or staff password reset.
+- Temporary passwords are not stored in import summaries, metadata, source rows, messages, or account detail pages.
+- Player-account temporary passwords use canonical player birthdate as `YYYYMMDD`.
+- Non-player operational passwords use generated random temporary passwords.
+- All temporary passwords force `must_change_password=True`.
+
+Provenance rules:
+
+- Import-provisioned accounts and links preserve `created_from_import` and `import_batch`.
+- Manual account creation does not create import provenance.
+- Account activation/deactivation preserves account profile, user-player link, and import provenance history.
+- User-player links are deactivated/reactivated rather than deleted in normal operations.
+
+Deferred from Platform V1 Account Operations:
+
+- Phase F production hardening/freeze review;
+- audit logging;
+- account merge;
+- duplicate account resolution;
+- invitation and email verification flows;
+- coach import;
+- parent import;
+- portal dashboards;
+- self-service password recovery email flow.
+
 ## Service Boundaries
 
 `profile_service`
@@ -354,7 +437,7 @@ accounts.services.provisioning_service
 active Django User + AccountProfile + UserPlayerLink
     |
     v
-staff activation (future workflow unless activation was explicitly selected at import)
+staff Account Operations visibility and correction tools
     |
     v
 /accounts/login/
@@ -414,22 +497,25 @@ Role handling:
 
 These are intentional V1 deferrals:
 
-- staff account management UI
-- account activation UI
-- password reset workflow
 - email invitation workflow
+- email verification workflow
+- self-service password recovery email flow
 - self-registration
+- account merge
+- duplicate account resolution
+- coach import
+- parent import
 - player portal
 - parent portal
 - coach portal
+- portal dashboards
 - evaluator role snapshot integration with Account Management roles
 - audit history for account changes
-- bulk account operations
 - custom user model
 - social login or SSO
 - PDP retirement
 
-These should be layered into future versions. They should not be backfilled into V1 without opening a new version or implementation phase.
+These should be layered into future versions or explicit implementation phases. They should not be backfilled into V1 without a separate plan.
 
 ## Technical Decisions
 
@@ -511,7 +597,7 @@ Coverage includes:
 - PDP coexistence
 - ownership-boundary regressions
 
-Every phase concluded with implementation review and regression testing. The final release review accepted Account Management V1 for the Phase 1-4 scope.
+Every core V1 phase concluded with implementation review and regression testing. Platform V1 Account Operations has also been implemented through Phase E and is awaiting Phase F production hardening/freeze review.
 
 ## Lessons Learned
 
@@ -541,11 +627,12 @@ Account Management V1
 Status:
 
 ```text
-COMPLETE
-FROZEN
+CORE V1 COMPLETE
+PLATFORM V1 ACCOUNT OPERATIONS PHASES A-E COMPLETE
+PHASE F PRODUCTION HARDENING / FREEZE PENDING
 ```
 
-Account Management V1 is ready for production for the implemented Phase 1-4 scope.
+Account Management V1 core account infrastructure is complete. Platform V1 Account Operations is implemented through Phase E and should receive a Phase F production hardening/freeze review before being declared frozen.
 
 V1 should remain stable. Future work should be added through a new version or explicit implementation phase.
 
@@ -555,16 +642,17 @@ Likely Account Management V2 work:
 
 - evaluator identity integration
 - mapping account roles into Analytics evaluator role snapshots
-- staff account management UI
-- account activation workflow
-- password reset workflow
 - email invitation workflow
+- email verification workflow
+- self-service password recovery email flow
 - audit history
+- account merge
+- duplicate account resolution
+- coach import
+- parent import
 - player portal
 - parent portal
 - coach portal
-- account deactivation/reactivation operations
-- bulk provisioning review
 - PDP retirement and migration planning
 
 Future versions should continue the V1 principles:
diff --git a/docs/account_management/implementation/engineering/platform_v1_account_operations.md b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
index 3ba10f4..2872dda 100644
--- a/docs/account_management/implementation/engineering/platform_v1_account_operations.md
+++ b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
@@ -506,9 +506,16 @@ Safety rules:
 - Display clear warnings when staff access is controlled by Django `is_staff` or `is_superuser`.
 - Use server-rendered pages consistent with the rest of the platform.
 
-## 9. Future Phases
+## 9. Implementation Phases And Status
 
-Implementation should be split into small, independently testable phases.
+Platform V1 Account Operations is split into small, independently testable phases. The implemented sequence is:
+
+- Phase A - Account Operations Foundation.
+- Phase B - Manual Account Creation.
+- Phase C - Account Lifecycle and Link Management.
+- Phase D - Operational Password Reset.
+- Phase E - Bulk Operations.
+- Phase F - Production Hardening / Freeze.
 
 ### Phase A: Account Operations Foundation
 
@@ -528,86 +535,115 @@ Deliverables:
 - read-only linked player and profile summaries;
 - tests for staff access, non-staff denial, search, filtering, and empty states.
 
+Status: implemented.
+
 ### Phase B: Manual Account Creation
 
 Goals:
 
-- Allow staff to create coach, parent, player, and guest evaluator accounts.
-- Allow superusers to create staff accounts.
+- Allow staff to create coach, parent, player, staff-role metadata, and guest evaluator accounts.
 - Keep account-only creation distinct from player account creation.
+- Keep Django `User.is_staff` and `User.is_superuser` changes outside this workflow.
 
 Deliverables:
 
-- `/accounts/users/create/`;
-- service-backed account-only creation for coach, parent, guest evaluator, and staff users;
+- `/accounts/create/`;
+- `/accounts/create/player/`;
+- service-backed account-only creation for coach, parent, guest evaluator, and staff-role metadata users;
 - service-backed player account creation that starts from an existing `players.Player`;
 - role assignment through `profile_service`;
 - temporary password setup through `password_service`;
-- optional user-player link creation through `link_service`;
+- player-account self-link creation through `link_service`;
 - tests for duplicate username/email, role defaults, staff restrictions, player-account creation from existing players, no player duplication, and password-change requirement.
 
-### Phase C: Link Management
-
-Goals:
-
-- Allow staff to manually link and unlink users and players.
-- Provide player-centered linked-user view.
+Status: implemented.
 
-Deliverables:
-
-- `/accounts/users/<id>/links/`;
-- `/accounts/users/<id>/links/add/`;
-- link activation/deactivation actions;
-- `/accounts/players/<player_id>/users/`;
-- tests for duplicate active links, primary self-link constraints, link history preservation, and permission checks.
-
-### Phase D: Account State And Role Operations
+### Phase C: Account Lifecycle And Link Management
 
 Goals:
 
-- Allow staff to manage active status and account roles safely.
-- Allow superusers to manage privileged staff/admin state.
+- Allow staff to update username, email, platform role metadata, and active status.
+- Prevent self-deactivation and last-active-superuser deactivation.
+- Allow staff to manually link, deactivate, reactivate, and mark primary user-player links.
+- Preserve account, link, and import provenance history.
 
 Deliverables:
 
-- activate/deactivate confirmation pages;
-- role change page;
+- `/accounts/users/<id>/edit/`;
+- `/accounts/users/<id>/links/`;
+- username, email, role, and active-state edit form;
+- account activation/deactivation through service-backed update paths;
+- link create, deactivate, reactivate, and primary-self actions;
 - staff/superuser guardrails;
 - self-lockout prevention;
 - last-superuser protection;
-- tests for all safety rules.
+- tests for duplicate active links, primary self-link constraints, link history preservation, role/staff distinction, lifecycle safety rules, and permission checks.
 
-### Phase E: Password And Username Operations
+Status: implemented.
+
+### Phase D: Operational Password Reset
 
 Goals:
 
-- Allow staff to reset passwords and change usernames through services.
+- Allow staff to reset passwords through account services.
+- Display temporary passwords only once.
+- Force password change after reset.
+- Preserve account active state, profile metadata, links, and provenance.
 
 Deliverables:
 
-- password reset page;
-- username change page;
-- generated temporary password flow or approved birthdate reset flow;
+- `/accounts/users/<id>/password/`;
+- staff password reset confirmation form;
+- birthdate temporary password for player self-linked accounts;
+- random temporary password for non-player accounts;
 - forced password-change after staff reset;
-- username collision handling;
-- tests proving no plaintext password persistence and correct password-change enforcement.
+- tests proving no plaintext password persistence, one-time display behavior, and correct password-change enforcement.
+
+Status: implemented.
 
-### Phase F: Bulk Operations And Polish
+### Phase E: Bulk Operations
 
 Goals:
 
 - Add only low-risk bulk actions after single-user operations are stable.
+- Reuse existing single-account services instead of duplicating business rules.
+- Avoid bulk password reset, bulk username changes, bulk role changes, and bulk user creation.
 
-Possible deliverables:
+Deliverables:
 
 - bulk activate selected users;
 - bulk deactivate selected users;
 - bulk require password change;
-- bulk role update only if safe and restricted;
-- improved filters for imported accounts and linked/unlinked accounts;
-- tests for partial failures and permission restrictions.
+- bulk clear password-change requirement;
+- partial-failure reporting;
+- permission restrictions;
+- tests for successful actions, partial failures, missing users, empty selections, unsupported actions, self-deactivation protection, last-superuser protection, and filtered select-all behavior.
+
+Status: implemented.
+
+### Phase F: Production Hardening / Freeze
+
+Goals:
+
+- Perform the final production-readiness review before freezing Platform V1 Account Operations.
+- Do not add features unless a blocking defect is found and explicitly approved.
+
+Review areas:
+
+- architecture consistency;
+- service boundaries;
+- authentication and authorization correctness;
+- password exposure safety;
+- account/player identity separation;
+- import provenance preservation;
+- permission coverage;
+- edge-case behavior;
+- performance and query sanity;
+- UX consistency;
+- documentation finalization;
+- freeze declaration.
 
-Bulk operations should be deferred if implementation pressure would weaken safety or clarity.
+Status: pending.
 
 ### Explicitly Deferred: Bulk Coach Import
 
@@ -628,6 +664,7 @@ That future plan should define CSV format, matching rules, duplicate detection,
 - Username changes could create collisions or make staff unable to find accounts.
 - Imported player accounts may be active immediately, so staff need clear visibility into which accounts still require password changes.
 - Bulk operations could cause large accidental access changes if not carefully confirmed and permission-guarded.
+- Phase F could expose production-readiness defects that require targeted cleanup before freeze.
 - Without audit logging, staff may have limited historical visibility into who performed account changes. Audit logging is out of scope for this plan unless separately approved.
 
 ## 11. Open Questions
@@ -639,16 +676,17 @@ That future plan should define CSV format, matching rules, duplicate detection,
 - Should `AccountProfile.is_active` be kept synchronized with `User.is_active`, or treated as platform metadata only?
 - Should assigning `AccountProfile.role=admin` require superuser even if it does not grant Django admin access?
 - Should changing `User.is_staff` be included in this operational UI, or remain in Django admin for Platform V1?
-- Should bulk operations be included in the initial implementation or deferred until after single-account workflows are proven in production?
 - Should account merge and duplicate account resolution be planned as a later Platform V1 operations extension or deferred to a future platform version?
 - Should account-operation changes eventually produce audit records? This plan treats audit logging as out of scope, but production operations may require it later.
+- What exact checklist should define the Phase F freeze declaration?
 
 ## Definition Of Done
 
-This roadmap is ready for implementation when:
+This roadmap is ready for Phase F freeze review when:
 
-- each phase has a detailed implementation prompt or engineering plan;
+- Phases A-E are implemented and tested;
 - permission rules are confirmed;
 - password reset behavior is confirmed;
 - role/staff/superuser boundaries are confirmed;
-- the first implementation phase can be built without introducing new architecture decisions.
+- documentation reflects the implemented state;
+- Phase F can proceed without introducing new feature scope.
```

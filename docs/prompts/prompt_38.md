We have completed and frozen the following Platform V1 subsystems:

- Players V1
- Analytics V1
- Account Management V1 (Phases 1–4)
- Architecture documentation

After reviewing the completed platform, we identified a significant operational gap.

Although authentication, provisioning, and user-player linking now exist, the platform still lacks the operational tools required for staff to manage user accounts in production.

This is NOT Platform V2 work.

It is the remaining operational work required to make Platform V1 production-ready.

Your task is to create an engineering plan only.

Do NOT implement any code.

Do NOT create migrations.

Do NOT modify any existing documentation except creating the new engineering plan.

---

Create:

docs/account_management/implementation/engineering/platform_v1_account_operations.md

The document should define the remaining operational account-management work.

The plan should be comprehensive enough that implementation can later be performed phase-by-phase.

Cover at least the following topics.

# 1. Objectives

Explain why operational account management is required before the platform can be considered production ready.

State explicitly that this work extends Platform V1 rather than introducing new architecture.

---

# 2. Scope

Include:

Staff account administration

Coach account management

Parent account management

Guest evaluator accounts

Manual account creation

Manual player linking

Role management

Account activation/deactivation

Password reset

Username management

Account search

Account detail page

Bulk operations where appropriate

---

# 3. What is NOT included

Examples:

OAuth

SSO

Email verification

Invitation emails

Notifications

Portal dashboards

Fine-grained permissions

API endpoints

Background jobs

Caching

Audit logging (unless already planned elsewhere)

---

# 4. Proposed UI

Recommend staff pages.

Example:

/accounts/

/accounts/users/

/accounts/users/<id>/

/accounts/users/create/

/accounts/users/<id>/links/

/accounts/users/<id>/password/

/accounts/users/<id>/activate/

/accounts/users/<id>/deactivate/

Discuss navigation.

Discuss integration with Analytics Command Center if appropriate.

---

# 5. Operations

Describe workflows for:

creating coach accounts

creating parent accounts

creating guest evaluators

creating staff accounts

activating imported players

deactivating users

changing usernames

changing roles

resetting passwords

linking users to players

unlinking users

viewing linked players

viewing linked users

---

# 6. Service ownership

Define which service owns each responsibility.

Continue following existing architecture.

Example:

accounts.services.profile_service

accounts.services.link_service

accounts.services.password_service

accounts.services.username_service

accounts.services.provisioning_service

Identify any new services that should exist.

---

# 7. Permissions

Define which operations require:

staff

superuser

regular authenticated users

State clearly that AccountProfile.role does NOT replace Django staff/superuser permissions.

---

# 8. UX principles

Keep views thin.

Business logic belongs in services.

Avoid duplicate business rules.

Support idempotent operations.

Avoid exposing temporary passwords.

Avoid deleting history unnecessarily.

---

# 9. Future phases

Break implementation into logical engineering phases.

Recommend approximately 4–6 implementation phases.

Each phase should be independently testable.

---

# 10. Risks

Document potential operational risks.

Examples:

incorrect role assignment

duplicate users

incorrect links

orphaned players

password resets

username collisions

---

# 11. Open questions

Identify remaining architectural decisions requiring discussion before implementation.

---

Do not implement anything.

Do not create placeholder code.

Do not modify models.

Do not modify services.

Produce only the engineering planning document.

The resulting plan should become the roadmap for completing the remaining Platform V1 account-management functionality.
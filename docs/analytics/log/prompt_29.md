You are performing a comprehensive architecture and implementation review of Account Management V1.

Do NOT implement new features.

Do NOT implement Phase 5.

Do NOT implement Phase 6.

Do NOT redesign the system.

Your job is to review the completed Account Management V1 implementation exactly as a senior software architect performing a release readiness review.

==================================================
Goal
==================================================

Determine whether Account Management V1 is production-ready.

Review:

- architecture
- service boundaries
- code organization
- performance
- maintainability
- security
- consistency
- technical debt

Only make improvements that improve the quality of the existing implementation.

No new functionality.

==================================================
Current Scope
==================================================

Account Management V1 currently consists of:

Phase 1
- AccountProfile
- roles
- profile services
- permission services

Phase 2
- UserPlayerLink
- relationship model
- link services

Phase 3
- player import account provisioning
- username service
- email service
- password service
- provisioning service
- idempotent provisioning

Phase 4
- platform authentication
- login/logout
- password change
- forced password middleware
- landing service
- account profile page

All four phases have already passed implementation review.

==================================================
Before Reviewing
==================================================

Read:

- docs/account_management/implementation/account_management_v1.md

Read every engineering plan:

- docs/account_management/implementation/engineering/

Review:

accounts/

players/

analytics/

pdp/

drafts/

Review project settings and middleware.

Review existing tests.

==================================================
Review Areas
==================================================

Review the following.

--------------------------------------------------
1. Architecture
--------------------------------------------------

Verify:

- ownership boundaries
- separation of concerns
- layering
- service boundaries
- model responsibilities
- middleware responsibilities
- view responsibilities
- template responsibilities

Look for:

- misplaced logic
- duplicated ownership
- leaking abstractions
- architecture drift

--------------------------------------------------
2. Service Design
--------------------------------------------------

Review every service.

Examples:

profile_service

role_service

permissions

link_service

username_service

email_service

password_service

provisioning_service

auth_redirect_service

Verify:

- single responsibility

- cohesion

- duplicated code

- unnecessary coupling

- naming consistency

- helper organization

--------------------------------------------------
3. Authentication Flow
--------------------------------------------------

Review:

login

logout

password change

forced password middleware

redirect logic

landing logic

Look for:

- duplicated redirects

- redirect loops

- middleware edge cases

- session handling

- authentication correctness

--------------------------------------------------
4. Provisioning
--------------------------------------------------

Review:

username generation

email normalization

password generation

idempotency

existing account reuse

transaction handling

summary generation

Look for:

- duplicate queries

- duplicate work

- race conditions

- maintainability

--------------------------------------------------
5. Performance
--------------------------------------------------

Review:

database queries

select_related()

prefetch_related()

duplicate queries

repeated profile lookups

repeated UserPlayerLink lookups

repeated AccountProfile lookups

username lookup efficiency

middleware efficiency

Do not prematurely optimize.

Only improve obvious inefficiencies.

--------------------------------------------------
6. Security
--------------------------------------------------

Review:

temporary passwords

inactive accounts

forced password flow

permission helpers

role handling

authentication

email normalization

password hashing

Verify:

- no plaintext passwords

- no privilege escalation

- no role escalation

- no accidental account linking

--------------------------------------------------
7. Maintainability
--------------------------------------------------

Review:

module organization

method names

class names

comments

duplication

dead code

unused imports

long methods

private helper extraction

magic constants

--------------------------------------------------
8. Test Quality
--------------------------------------------------

Review:

test organization

coverage

missing edge cases

duplication

helper methods

Verify:

critical paths are covered.

--------------------------------------------------
9. Consistency
--------------------------------------------------

Compare with Analytics V1.

Verify Account Management follows the same architectural style.

Examples:

service-oriented

thin views

read models

minimal middleware

clear ownership

==================================================
Do NOT Implement
==================================================

Do NOT implement:

Phase 5

Phase 6

staff account management

activation UI

player portal

parent portal

coach portal

email invitations

password reset

SSO

social login

custom user model

new database models

new workflows

==================================================
Allowed Changes
==================================================

You MAY:

- refactor

- remove duplication

- improve performance

- improve readability

- improve naming

- improve helper organization

- improve service boundaries

- improve tests

You MUST NOT:

change user-visible behavior

add features

change architecture

==================================================
Verification
==================================================

Run:

python manage.py check

python manage.py makemigrations accounts --check

python manage.py test accounts

python manage.py test analytics

python manage.py test players

python manage.py test drafts

python manage.py test pdp

python manage.py test

git diff --check

==================================================
Final Report
==================================================

Provide a comprehensive release review.

Include:

1. Overall architecture rating

2. Strengths

3. Weaknesses

4. Performance observations

5. Security observations

6. Maintainability observations

7. Technical debt

8. Files modified

9. Tests added

10. Test results

11. Whether Account Management V1 is production-ready

12. Remaining recommendations before freezing V1

13. Confirmation that:

- no new functionality was introduced
- no Phase 5 work was started
- no Phase 6 work was started

If no code changes are necessary, explicitly state that Account Management V1 is accepted without modification and is ready to be frozen as Version 1.
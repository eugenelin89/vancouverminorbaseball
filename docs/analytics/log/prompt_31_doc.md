Account Management V1 has been accepted and is ready to freeze.

Do NOT implement application code.

Do NOT modify any Python files.

Do NOT change models, services, views, URLs, middleware, templates, or tests.

Your task is to improve the engineering documentation only.

==================================================
Before Editing
==================================================

Read:

- docs/account_management/V1_SUMMARY.md

Review:

- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/

Use them only for reference.

V1_SUMMARY.md remains the canonical document.

==================================================
Goals
==================================================

Improve the document so it becomes the definitive engineering onboarding
document for Account Management V1.

Do NOT rewrite the document.

Only improve it.

==================================================
Required Improvements
==================================================

--------------------------------------------------
1. Add Guiding Principles
--------------------------------------------------

Near the beginning of the document (after the introduction and before
Design Principles), add a section:

## Guiding Principles

Summarize the long-lived architectural principles.

Examples include:

- player identity is independent from login identity
- authentication and authorization are separate concerns
- business rules belong in services
- provisioning is explicit and idempotent
- middleware enforces authentication rather than orchestrating workflows
- Django User remains the authentication authority
- future portals consume Account Management rather than own account logic

These should explain WHY the architecture exists.

--------------------------------------------------
2. Clarify subsystem purpose
--------------------------------------------------

Expand the opening description slightly.

Clearly explain that Account Management is the platform identity layer
shared by all current and future subsystems.

Explain that it centralizes:

- authentication
- account metadata
- user-player relationships

while intentionally keeping those concerns out of:

- players
- analytics
- drafts

--------------------------------------------------
3. Add Dependency Direction
--------------------------------------------------

Within the Architecture Overview add a new section:

Dependency Direction

Illustrate which subsystem depends on which.

Use a simple diagram similar to:

accounts
    ↓
players

analytics → players
analytics → accounts

drafts → players

PDP (legacy)

Clarify that cross-subsystem business rules should normally flow through
services rather than directly manipulating another subsystem's models.

--------------------------------------------------
4. Explain why Django User was retained
--------------------------------------------------

Under Technical Decisions add a new subsection:

Why Django User was retained

Discuss:

- mature authentication
- password hashing
- admin integration
- permission system
- ecosystem compatibility
- avoiding unnecessary custom AUTH_USER_MODEL complexity

--------------------------------------------------
5. Add Lessons Learned
--------------------------------------------------

Near the end add:

## Lessons Learned

Examples:

- explicit services scaled better than signals
- idempotent provisioning simplified imports
- separating player identity from authentication reduced coupling
- thin views simplified refactoring
- review/fix passes after every phase improved architecture quality

Keep this concise.

--------------------------------------------------
6. Add Subsystem Status
--------------------------------------------------

Add:

## Platform Status

Summarize the overall platform at a high level.

Example:

Players
    V1 Complete

Analytics
    V1 Complete

Account Management
    V1 Complete

Drafts
    Active

LeagueHub
    Planned

Video
    Planned

This should orient new engineers.

--------------------------------------------------
7. Preserve Existing Structure
--------------------------------------------------

Do NOT remove existing sections.

Do NOT substantially rewrite completed content.

Do NOT change implementation history.

This should remain an incremental documentation improvement.

==================================================
Optional Improvement
==================================================

If appropriate, improve cross references between sections.

Avoid duplication.

==================================================
Final Report
==================================================

Report:

- files modified
- sections added
- documentation improvements made
- confirmation that no application code was changed
- confirmation that Account Management V1 remains frozen
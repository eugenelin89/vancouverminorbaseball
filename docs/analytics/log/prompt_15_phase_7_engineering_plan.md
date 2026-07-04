You are continuing implementation of the VCB Analytics project.

Do NOT implement code.

The current incomplete phase is:

Phase 7 - Command Center & Reporting

Your task is to create the engineering implementation plan only.

==================================================
STEP 1 — Repository Discovery
==================================================

Read:

- docs/analytics/implementation/STATUS.md
- docs/analytics/implementation/phase_07_command_center.md (if it exists)
- docs/analytics/architecture/README.md

List the contents of:

- docs/analytics/implementation/
- docs/analytics/implementation/engineering/
- docs/analytics/architecture/

Locate every document related to Phase 7.

Read every relevant document.

Do not assume filenames.
Use only files that actually exist.

==================================================
STEP 2 — Existing Implementation Review
==================================================

Review the completed implementation of Phases 1–6.

Identify reusable components including:

- observation services
- draft context services
- timeline service
- comparison service
- player search
- player profile
- coach assessment workflow
- import workflow

Determine how Phase 7 should build upon these services without duplicating logic.

==================================================
STEP 3 — Create Engineering Plan
==================================================

If the engineering plan

docs/analytics/implementation/engineering/phase_07_command_center.md

already exists:

- review it
- improve it if necessary
- do not implement code

Otherwise create:

docs/analytics/implementation/engineering/phase_07_command_center.md

The engineering plan should include:

1. Phase goal
2. Scope
3. Out-of-scope
4. Files to create
5. Files to modify
6. URLs
7. View classes
8. Service responsibilities
9. Read models/dataclasses
10. Dashboard layout
11. Reporting components
12. Aggregation rules
13. Filtering semantics
14. Sorting semantics
15. Empty states
16. Permissions
17. Performance considerations
18. Tests to write
19. Implementation sequence
20. Risks/Open questions
21. Definition of Done

==================================================
Engineering Rules
==================================================

The engineering plan must:

- reuse all existing Phase 1–6 services
- not duplicate player search
- not duplicate draft context logic
- not duplicate timeline logic
- not duplicate comparison logic
- keep business logic inside services
- keep views thin
- keep templates presentation-only
- use read models/dataclasses where appropriate
- avoid introducing unnecessary models

If reporting requires additional services, describe them clearly.

==================================================
Documentation Updates
==================================================

Update STATUS.md only if necessary to indicate Phase 7 is now the active planning phase.

Do not mark Phase 7 complete.

==================================================
STOP
==================================================

Do not implement any code.

Only create or update documentation.

Final report:

- files created
- files modified
- summary of architectural decisions
- confirmation that no application code was implemented
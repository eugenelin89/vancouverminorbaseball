Implement Phase 5 only.

Before writing any code:

1. Read and follow:
   - docs/analytics/architecture.md
   - docs/analytics/implementation/STATUS.md
   - docs/analytics/implementation/phase_05_draft_context.md
   - docs/analytics/implementation/engineering/phase_05_draft_context.md

2. Follow the architecture exactly.
3. Do NOT implement any Phase 6 or Phase 7 functionality.
4. Preserve all existing Phase 1–4 behavior and tests.

Implementation requirements:

- Implement only the Draft Context workflow described in Phase 5.
- Keep Draft Context completely read-only.
- Draft Context should consume submitted observations from previous phases and expose them for draft preparation.
- Do not modify coach assessment behavior.
- Do not modify observation workflows.
- Do not modify player import functionality.
- Do not introduce reporting, dashboards, analytics, AI summaries, comparisons, timelines, exports, charts, or player-facing features.
- Do not add placeholder functionality for future phases.

Architecture requirements:

- Reuse existing services wherever possible.
- Keep business logic inside services.
- Keep views thin.
- Keep templates presentation-only.
- Avoid duplicated query logic.
- Do not hard-code question text or workflow rules.
- Follow existing project naming conventions.

Testing:

Add comprehensive tests covering:
- successful Draft Context retrieval
- permission checks
- empty context
- multiple observations
- ordering
- edge cases
- regression coverage so Phases 1–4 continue working

Verification:

Run:

python manage.py makemigrations analytics --check
python manage.py test analytics
python manage.py test players
python manage.py test

When complete, report:

- summary of what was implemented
- files created
- files modified
- migrations added (if any)
- test results
- any implementation decisions
- any assumptions made because of gaps in the engineering document

Do not begin Phase 6 after finishing Phase 5.
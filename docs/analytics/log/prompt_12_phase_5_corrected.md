Implement Phase 5 only.

Important repo note:
- There is no `docs/analytics/architecture.md`.
- Use the architecture handbook under `docs/analytics/architecture/` instead, especially:
  - `docs/analytics/architecture/README.md`
  - `docs/analytics/architecture/06_draft_integration.md`
  - `docs/analytics/architecture/09_services.md`
- There is no `docs/analytics/implementation/engineering/phase_05_draft_context.md`.
- Use the available Phase 5 tracking/planning docs instead:
  - `docs/analytics/implementation/STATUS.md`
  - `docs/analytics/implementation/phase_05_draft_context.md`
  - any existing prompt/planning notes for Phase 5, such as `prompt_11_phase_5.md`, if present.

Before coding:
1. Read the architecture handbook files listed above.
2. Read the Phase 5 tracking doc.
3. Inspect the existing `drafts` app/models/services/views/templates before creating anything new.
4. Reuse existing draft models and workflow wherever possible.

Scope:
- Implement Phase 5 Draft Context only.
- Do not implement Phase 6 or Phase 7.
- Do not add reporting, dashboards, charts, AI summaries, timelines, comparisons, exports, or player-facing features.
- Do not modify coach assessment workflow except where strictly required to consume submitted observations as read-only context.
- Preserve Phase 1–4 behavior.

Phase 5 goal:
- Make submitted coach assessment observations available as read-only draft context for existing draft workflows.
- Draft Context should help staff/users prepare drafts using prior submitted observations.
- It should not create a new assessment workflow.
- It should not change submitted observations.
- It should not duplicate player identity or observation data.

Architecture requirements:
- Keep business logic in services.
- Keep views thin.
- Keep templates presentation-only.
- Reuse existing observation/detail services where appropriate.
- Avoid hard-coded question text.
- Avoid duplicated query logic.

Tests:
Add or update tests for:
- draft context retrieval from submitted observations
- empty context when no submitted observations exist
- excluding draft/reopened observations
- multiple submitted observations
- ordering
- permission/access behavior
- regression coverage for existing draft and analytics workflows

Verification:
Run:
- `python manage.py makemigrations analytics --check`
- `python manage.py test analytics`
- `python manage.py test drafts`
- `python manage.py test players`
- `python manage.py test`

When complete, report:
- files created
- files modified
- migrations added, if any
- test results
- assumptions made because the engineering plan file was missing
- confirmation that Phase 6/7 were not started
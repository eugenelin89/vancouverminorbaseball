# Agent Instructions

These instructions apply to the entire repository.

## General Workflow

- Read the relevant documentation before changing subsystem behavior.
- Keep changes scoped to the user's request.
- Do not implement future phases or placeholder functionality unless explicitly requested.
- Do not rewrite architecture decisions unless the user asks for an architecture update.
- Preserve existing behavior unless the task explicitly requests a behavior change or bug fix.
- Do not revert user changes or unrelated work.

## Project Snapshot Policy

- When any file is created, modified, moved, or deleted, update `project_flat_file.txt` before finishing the task.
- `project_flat_file.txt` should include every project file with:
  - the full absolute file path,
  - a clear separator before each file,
  - text file contents included directly,
  - binary files represented only by metadata and a short description.
- Do not embed binary file contents in the snapshot.
- Exclude `.git`, `.venv`, `__pycache__`, `node_modules`, `dist`, `build`, and the snapshot file itself.

## Architecture Boundaries

- `players` owns canonical player identity, aliases, source identifiers, source rows, tags, imports, matching, and player merge/update behavior.
- `accounts` owns login identity, account metadata, account roles, user-player links, provisioning, auth redirects, and forced password-change behavior.
- `analytics` owns observations, coach assessments, metrics, timelines, comparisons, draft context read models, command center summaries, and reporting surfaces.
- `drafts` owns draft workflows and draft actions.
- `pdp` is legacy/transitionary. Do not migrate PDP workflows unless explicitly requested.
- Cross-subsystem business rules should flow through services instead of directly manipulating another subsystem's models from views or templates.

## Implementation Style

- Keep business logic in services.
- Keep views thin.
- Keep templates presentation-only.
- Prefer explicit service calls over signals for account, import, linking, and workflow behavior.
- Avoid duplicated query logic and duplicated business rules.
- Use transactions where workflow state changes must be atomic.
- Use `select_related()` and `prefetch_related()` where practical to avoid obvious N+1 queries.
- Do not introduce new models, migrations, APIs, JavaScript, charts, exports, background jobs, caching, or AI functionality unless the task explicitly calls for them.

## Documentation

- Keep subsystem documentation consistent with implementation changes.
- `docs/ARCHITECTURE.md` is the top-level platform architecture entry point.
- `docs/analytics/architecture/` is the Analytics architecture reference.
- `docs/analytics/implementation/` tracks Analytics implementation status and phase history.
- `docs/account_management/V1_SUMMARY.md` is the canonical Account Management V1 onboarding document.
- Historical prompts live under `docs/prompts/` and may describe context that was true when the prompt was used.

## Testing

- Run focused tests for the subsystem being changed.
- Run broader regression tests when changes touch shared services, models, auth, imports, or cross-app behavior.
- Run `python manage.py makemigrations <app> --check` when model fields or app models may have changed.
- Run `python manage.py check` for application-level sanity after meaningful code changes.
- Run `git diff --check` before finishing.

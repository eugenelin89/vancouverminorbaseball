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

- Do not regenerate or update a full-project flat file during normal work.
- Treat `project_flat_file.txt` as an on-request artifact only. Update it only when the user explicitly asks for a full project snapshot.
- Prefer token-efficient records:
  - the prompt archive should contain the user's prompt,
  - the implementation commit diff,
  - and, if useful, a short list of changed files.
- Do not paste full repository contents into prompt records.
- If a snapshot is explicitly requested, binary files should still be represented only by metadata and a short description.
- Snapshot-style artifacts should exclude `.git`, `.venv`, `__pycache__`, `node_modules`, `dist`, `build`, generated caches, and unrelated scratch files unless the user explicitly asks to include them.

## Prompt Archive And Commit Policy

When a user prompt causes any file to be created, modified, moved, or deleted:

- Create a prompt record in `docs/prompts/`.
- Use this filename format:

  ```text
  prompt_[ID]_[app_name].md
  ```

- Use the next unused integer ID, zero-padded to two digits.
- Choose the app/subsystem name that the prompt primarily affects. Use `platform` for cross-subsystem or repository-wide prompts.
- Paste the user's prompt into the prompt record.
- Commit the implementation/documentation changes first, using a concise commit message based on the resulting work summary.
- Generate the diff for that commit against its previous commit.
- Paste that diff into the prompt record.
- Commit the prompt record separately.
- Push the resulting commits to the remote repository before finishing the workflow.
- Do not include unrelated user changes in either commit.
- If a task cannot be committed safely because the worktree contains unrelated staged changes or an instruction explicitly forbids committing, explain the blocker.
- Execute routine git commands directly as part of this workflow without asking the user for additional conversational permission, including `git status`, `git diff`, `git add`, `git commit`, `git log`, and `git push`.
- This rule does not override tool-enforced approval prompts or safety restrictions. If the execution environment requires approval for a git command, request that approval through the tool rather than asking separately in chat.

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

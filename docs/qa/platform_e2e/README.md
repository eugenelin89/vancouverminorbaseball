# Platform End-To-End QA Package

This package contains reusable QA material for testing VCB Platform account provisioning, imports, season/team assignments, and evaluation workflows.

Use these files in an isolated QA season only:

```text
TEST - Platform QA 2026
```

Recommended QA teams:

- `TEST - Alpha`
- `TEST - Beta`

## Files

- `platform_e2e_test_script.md`: step-by-step production QA script.
- `test_players_import.csv`: four imported player records.
- `test_coaches_import.csv`: two imported coach records.
- `test_coaches_inactive_import.csv`: optional inactive-coach lifecycle fixture.
- `test_coach_account_collision_cases.csv`: optional negative-test fixture for coach account collision behavior.
- `negative_test_fixtures.md`: purpose, prerequisites, expected outcomes, and cleanup for optional negative fixtures.
- `production_smoke_test.md`: concise post-deployment smoke-test checklist.
- `manual_test_records.md`: records intentionally left for manual creation.
- `cleanup_checklist.md`: safe cleanup checklist after testing.
- `feature_traceability.md`: stable requirement IDs, risk levels, coverage, and automation-readiness matrix.
- `release_pipeline.md`: release QA sequence and change-impact guidance.
- `CHANGELOG.md`: QA package history.

## Traceability And Release Planning

Use `feature_traceability.md` when a release, defect, or code review needs a stable reference to tested behavior.

- Requirement IDs are stable references for platform capabilities.
- The traceability matrix shows where each capability is tested.
- Risk levels help prioritize when release time is limited.
- Automation readiness identifies where future unit, integration, or browser automation can replace manual checks.
- `release_pipeline.md` connects development changes to production QA scope.

## Maintaining Traceability

When a feature is added or materially changed:

1. Create or reuse a stable requirement ID.
2. Update the traceability matrix.
3. Add or update the appropriate smoke, release-blocking, regression, or edge test.
4. Update risk only if the impact changed.
5. Update automation readiness when automated coverage is added.
6. Add a changelog entry.
7. Update release-pipeline impact mapping if a new capability area is introduced.

Do not renumber existing IDs merely to improve ordering. Deprecated requirements should remain listed and be marked deprecated rather than silently removed.

## Current UI Paths

- Sign in: `/accounts/login/`
- Analytics Command Center: `/analytics/`
- Player import: `/analytics/imports/`
- New player import: `/analytics/imports/new/`
- Coach import: `/accounts/imports/coaches/`
- New coach import: `/accounts/imports/coaches/new/`
- Account Operations: `/accounts/`
- Account list/search: `/accounts/users/`
- Manual account creation: `/accounts/create/`
- Manual player-account creation: `/accounts/create/player/`
- Season Operations: `/seasons/`
- Season teams: `/seasons/teams/`
- Player roster memberships: `/seasons/memberships/`
- Coach assignments: `/seasons/coach-assignments/`
- Evaluation submission: `/analytics/evaluations/`
- Player "My Evaluations": `/analytics/my/evaluations/`
- Coach/staff evaluation review: `/analytics/evaluation-review/`

## Short Operating Sequence

1. Confirm a recent database backup exists.
2. Create or verify the QA season `TEST - Platform QA 2026`.
3. Create or verify the QA teams `TEST - Alpha` and `TEST - Beta`.
4. Replace every `REPLACE_WITH_YOUR_EMAIL+...@example.com` placeholder in the CSV files with controlled test inbox aliases before importing.
5. Import `test_players_import.csv` from `/analytics/imports/new/`.
6. Import `test_coaches_import.csv` from `/accounts/imports/coaches/new/`.
7. Manually create the records listed in `manual_test_records.md`.
8. Follow `platform_e2e_test_script.md`.
9. After testing, follow `cleanup_checklist.md`.

## Test Levels

Use the package in this order:

```text
Production smoke test
-> release-blocking E2E tests
-> standard regression
-> extended edge cases
```

- **Release-blocking**: imports, account provisioning, coach evaluation, self-evaluation, peer evaluation, review, direct URL permissions, password change, duplicate-submission protection, and basic dashboard integrity.
- **Standard regression**: imported/manual cross-workflows, cycle isolation, inactive-account lifecycle, archive behavior, reporting filters, and mobile layout.
- **Extended edge cases**: collision handling, multi-tab stale edits, browser back/forward behavior, case and whitespace normalization, and conflicting cross-role emails.

Do not import optional negative fixtures during a normal production smoke test. Use them only when deliberately testing collision or inactive-account behavior.

## Recommended Long-Term QA Strategy

Maintain one permanent QA environment instead of recreating fixtures for every release.

Recommended permanent season:

```text
TEST - Platform QA
```

The current fixture season remains:

```text
TEST - Platform QA 2026
```

Either naming style is acceptable as long as it is clearly isolated from real seasons.

Recommended evaluation-cycle naming:

```text
TEST - Smoke YYYY-MM-DD
```

or:

```text
TEST - Release 1.8.2
```

Long-term practice:

- keep QA players permanent;
- keep QA coaches permanent;
- keep QA teams permanent;
- keep QA accounts permanent but deactivate them when not needed;
- keep historical QA evaluations unless intentionally resetting the QA environment;
- create new evaluation cycles over time when a clean smoke-test run is useful;
- reuse existing evaluation cycles by reopening and resubmitting records when repeatability is more important than a clean cycle.

This keeps repeated production deployments fast and minimizes cleanup.

## Evaluation Cycle Guidance

Full regression:

- create or reuse `TEST - Cycle A`;
- create or reuse `TEST - Cycle B`;
- verify that identical evaluator/player/perspective combinations can be tested independently in each cycle.

Smoke tests support either approach:

- create a new smoke-test cycle such as `TEST - Smoke 2026-07-23`; or
- reuse an existing smoke-test cycle and reopen/resubmit existing evaluations.

The application does not require one approach over the other. Choose based on whether the release needs clean cycle-specific counts or repeatable low-maintenance checks.

Current uniqueness behavior:

```text
Evaluator + Player + Observation Type + Perspective + Evaluation Cycle
```

Self-evaluations also enforce:

```text
Player + Evaluation Cycle
```

This means repeated smoke tests in the same cycle should reuse/reopen existing evaluations rather than trying to create new duplicate evaluations.

## QA Environment Lifecycle

```text
Build once
-> use for many releases
-> archive when obsolete
-> create a new QA environment only when the data model or product workflow changes significantly
```

When future platform features are added, extend this QA package instead of replacing it.

Examples:

- new evaluator roles;
- new observation types;
- new dashboards;
- new reports;
- new permissions;
- new importers.

Each future feature should receive:

- one smoke-test item;
- one release-blocking test if appropriate;
- one full regression section if needed.

## Important Import Notes

- Player import and coach import use different CSV schemas.
- Player import belongs to Analytics UI but uses `players` import services.
- Coach import belongs to Account Operations and creates or reuses coach accounts.
- Player imports can optionally provision player accounts when staff select the account-provisioning option and map the `account_email` column.
- Player account temporary passwords are based on the imported birthdate in `YYYYMMDD` format and are not displayed in the import result.
- Coach account temporary passwords are secure random passwords shown only once on the coach import result page.
- Imported coach accounts are active by default unless the CSV sets `is_active` to a false value.
- Imported coaches do not receive Django staff or superuser access.
- Coach import creates or updates season teams and coach assignments.
- Player import creates or updates season teams and player roster memberships.
- Generated usernames use `firstname.lastname` and suffix with `2`, `3`, and so on when the generated base already exists.
- Explicit usernames are normalized and rejected when already used by a different account.
- Emails are normalized by trimming whitespace and comparing case-insensitively.

## Placeholder Email Rule

The committed CSV files intentionally use `example.com` placeholders. Before using them in a real QA environment, replace them with aliases controlled by the tester, such as:

```text
your.name+qa-player1@your-domain.example
```

Do not import real personal data for this QA package.

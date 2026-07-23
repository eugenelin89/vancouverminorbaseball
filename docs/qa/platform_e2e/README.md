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
- `manual_test_records.md`: records intentionally left for manual creation.
- `cleanup_checklist.md`: safe cleanup checklist after testing.

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
4. Replace every `REPLACE_WITH_YOUR_EMAIL+...@example.com` placeholder in both CSV files with controlled test inbox aliases before importing.
5. Import `test_players_import.csv` from `/analytics/imports/new/`.
6. Import `test_coaches_import.csv` from `/accounts/imports/coaches/new/`.
7. Manually create the records listed in `manual_test_records.md`.
8. Follow `platform_e2e_test_script.md`.
9. After testing, follow `cleanup_checklist.md`.

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

## Placeholder Email Rule

The committed CSV files intentionally use `example.com` placeholders. Before using them in a real QA environment, replace them with aliases controlled by the tester, such as:

```text
your.name+qa-player1@your-domain.example
```

Do not import real personal data for this QA package.

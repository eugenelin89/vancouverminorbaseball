Read:
- docs/analytics/architecture/04_imports.md
- docs/analytics/implementation/phase_02_player_import_workflow.md
- docs/analytics/implementation/engineering/phase_02_player_import_workflow.md

Apply Phase 2 review fixes only.

Do not start Phase 3.

Fix these must-fix issues:

1. Do not mark an import batch fully committed if unresolved conflict/error/ambiguous rows remain.
- Staff must be able to return and resolve or explicitly skip unresolved rows.
- Add tests.

2. Add real ambiguous-match resolution.
- Staff can choose one existing candidate, create a new player, or skip the row.
- Commit service must support that resolution.
- Add tests.

3. Try all source identifiers during matching.
- Do not only use the first source identifier.
- If any identifier matches exactly, use that match.
- If multiple identifiers point to different players, mark ambiguous.
- Add tests.

Also fix these should-fix items if they are straightforward:

4. Make sensitive import JSON fields read-only in admin.
- Especially preview_snapshot, original_row, unmapped_fields, row_errors, conflict_summary, import_summary.
- Avoid exposing raw source data casually.

5. Prevent direct confirm from preview when rows need review.
- Either hide/disable Confirm Import or relabel it clearly.
- Staff should go through conflict review first.

6. Treat first_name and last_name differences as conflicts when an identifier matches an existing player.

7. Add a reasonable CSV row-count or file-size guard.

Do not change architecture documents unless absolutely required.

After fixes:
- run python manage.py test players
- run python manage.py test analytics
- run python manage.py test
- update the Phase 2 engineering plan with implementation decisions
- update phase_02_player_import_workflow.md Phase Review if needed
- summarize files changed and test results
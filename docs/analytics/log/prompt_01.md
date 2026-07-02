Read:
- docs/analytics/architecture/README.md
- docs/analytics/architecture/04_imports.md
- docs/analytics/implementation/README.md
- docs/analytics/implementation/STATUS.md
- docs/analytics/implementation/phase_02_player_import_workflow.md
- docs/analytics/implementation/engineering/phase_02_player_import_workflow.md
- docs/analytics/implementation/repository_assessment.md

Implement Phase 2 only.

Important decisions:
- Create a minimal `analytics` app now for the import UI.
- Keep import business logic in `players/services/import_service.py`.
- Analytics views/forms/templates should be thin UI orchestration only.
- Add `PlayerImportBatch` in the `players` app.
- Add nullable `PlayerSourceRow.import_batch`.
- Do not implement coach assessments, observations, reporting, timelines, draft context, or future phases.
- Do not migrate PDP workflows.
- Do not place player identity/import business logic in Analytics.

Implement:
- PlayerImportBatch model and migration.
- PlayerSourceRow.import_batch migration.
- players admin updates.
- expanded players import service.
- minimal analytics app for staff-only import workflow.
- upload, preview/mapping, conflict review, confirm, and detail pages.
- tests described in the Phase 2 engineering plan.

Run:
- python manage.py makemigrations players
- python manage.py migrate
- python manage.py test players
- python manage.py test analytics
- python manage.py test

After implementation:
- update STATUS.md
- update phase_02_player_import_workflow.md
- update engineering/phase_02_player_import_workflow.md with implementation decisions and review notes

Stop if implementation requires changing architecture.
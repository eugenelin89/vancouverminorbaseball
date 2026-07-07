Read:
- docs/analytics/architecture/README.md
- docs/analytics/architecture/03_analytics.md
- docs/analytics/architecture/05_coach_assessments.md
- docs/analytics/architecture/10_permissions.md
- docs/analytics/implementation/README.md
- docs/analytics/implementation/STATUS.md
- docs/analytics/implementation/repository_assessment.md
- docs/analytics/implementation/phase_04_coach_assessment_workflow.md
- docs/analytics/implementation/engineering/phase_04_coach_assessment_workflow.md
- docs/analytics/implementation/engineering/phase_03_analytics_observation_foundation.md

Implement Phase 4 only.

Important:
- Use `players.Player`.
- Use `analytics.services.question_service`.
- Use `analytics.services.observation_service`.
- Do not hard-code coach assessment questions in templates.
- Do not implement reporting, timelines, draft context, measurements, attachments, AI, or future phases.
- Do not migrate PDP workflows.
- Do not disrupt existing Phase 2 import UI or Phase 3 observation services.

Implement:
- dynamic coach assessment form
- coach assessment list/edit/detail workflow
- staff observation review list/detail workflow
- simple permissions helpers if useful
- templates and URLs
- tests described in the Phase 4 engineering plan

No migrations are expected. Run:
- python manage.py makemigrations analytics --check
- python manage.py test analytics
- python manage.py test players
- python manage.py test

After implementation:
- update STATUS.md
- update phase_04_coach_assessment_workflow.md
- update engineering/phase_04_coach_assessment_workflow.md with implementation decisions and review notes

Stop if implementation requires changing architecture.
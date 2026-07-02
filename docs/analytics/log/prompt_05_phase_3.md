Read:
- docs/analytics/architecture/README.md
- docs/analytics/architecture/03_analytics.md
- docs/analytics/architecture/05_coach_assessments.md
- docs/analytics/implementation/README.md
- docs/analytics/implementation/STATUS.md
- docs/analytics/implementation/repository_assessment.md
- docs/analytics/implementation/phase_03_analytics_observation_foundation.md
- docs/analytics/implementation/engineering/phase_03_analytics_observation_foundation.md

Implement Phase 3 only.

Important:
- Use `players.Player` as the canonical player reference.
- Do not duplicate player identity, matching, or import logic.
- Do not implement coach-facing assessment UI.
- Do not implement staff review UI.
- Do not implement reporting, timelines, draft context, measurements, attachments, AI, or future phases.
- Do not migrate PDP workflows.
- Do not disrupt the existing Phase 2 Analytics import UI.

Implement:
- Analytics observation foundation models.
- Admin registrations.
- Question service.
- Observation service.
- Default coach assessment setup/seed strategy.
- Migrations.
- Tests described in the Phase 3 engineering plan.

Run:
- python manage.py makemigrations analytics
- python manage.py migrate
- python manage.py test analytics
- python manage.py test players
- python manage.py test

After implementation:
- update STATUS.md
- update phase_03_analytics_observation_foundation.md
- update engineering/phase_03_analytics_observation_foundation.md with implementation decisions and review notes

Stop if implementation requires changing architecture.
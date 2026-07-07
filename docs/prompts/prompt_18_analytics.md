Implement Phase 6 only, exactly following:

docs/analytics/implementation/engineering/phase_06_player_experience.md

Do not redesign the plan.

Do not implement Phase 7.

Do not add dashboards, charts, exports, AI summaries, timeline database models, reports, player-facing views, parent portal views, or new models/migrations unless the engineering plan explicitly requires it.

Before coding:
1. Read the Phase 6 engineering plan.
2. Read:
   - docs/analytics/implementation/STATUS.md
   - docs/analytics/implementation/phase_06_player_experience.md
   - docs/analytics/architecture/07_player_experience.md
   - docs/analytics/architecture/08_reporting.md
   - docs/analytics/architecture/09_services.md
3. Inspect existing analytics, players, and drafts services/views/templates/tests.

Implementation requirements:
- Create the Phase 6 services, views, URLs, and templates described in the engineering plan.
- Keep Phase 6 staff-only.
- Use dataclasses/read models only for timeline and comparison.
- Reuse existing observation, player, tag, import, and draft context services where possible.
- Keep business logic in services.
- Keep views thin.
- Keep templates presentation-only.
- Preserve all Phase 1–5 behavior.

Testing:
Add the service, view, permission, filter, timeline, comparison, and regression tests described in the Phase 6 engineering plan.

Run:
python manage.py makemigrations analytics --check
python manage.py test analytics
python manage.py test players
python manage.py test drafts
python manage.py test

When complete, report:
- summary of implementation
- files created
- files modified
- migrations added, if any
- test results
- implementation decisions
- any deviations from the engineering plan
- confirmation that Phase 7 was not started
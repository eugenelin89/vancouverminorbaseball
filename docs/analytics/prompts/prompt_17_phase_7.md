Implement Phase 7 only.

The Phase 7 engineering plan has been reviewed and approved.

Implement exactly what is described in:

- docs/analytics/implementation/engineering/phase_07_command_center.md

Do not redesign the architecture.

==================================================
Before Coding
==================================================

Read:

- docs/analytics/implementation/STATUS.md
- docs/analytics/implementation/phase_07_command_center_reporting.md
- docs/analytics/implementation/engineering/phase_07_command_center.md
- docs/analytics/architecture/README.md
- docs/analytics/architecture/08_reporting.md
- docs/analytics/architecture/09_services.md

Review the existing implementation of:

- analytics/
- players/
- drafts/

especially:

- player_service
- comparison_service
- timeline_service
- draft_service
- coach_assessment_service
- metrics already available from previous phases

==================================================
Scope
==================================================

Implement Phase 7 only.

Create only the components defined by the engineering plan.

Expected additions include:

- analytics/services/player_service.py
- analytics/services/metrics_service.py
- analytics/services/reporting_service.py
- AnalyticsCommandCenterView
- /analytics/ route
- command center templates
- summary cards
- server-rendered reporting tables
- required tests

==================================================
Architecture Rules
==================================================

Follow these boundaries exactly.

player_service.py

Owns:
- reusable player search
- reusable player filtering
- player queryset construction
- player lookup helpers

comparison_service.py

Owns:
- player comparison
- score summaries
- comparison read models

Do not move player search logic into comparison_service.

timeline_service.py

Owns:
- timeline generation only

draft_service.py

Owns:
- draft matching
- DraftContext read models
- draft lookup

metrics_service.py

Owns:
- counts
- averages
- completion metrics
- aggregation
- metric calculations

metrics_service may call draft_service.

metrics_service must not duplicate draft matching logic.

reporting_service.py

Owns:
- assembling command center read models
- MetricCard objects
- CommandCenterContext
- navigation metadata

reporting_service must not calculate metrics.

Views

- thin only
- call services
- no aggregation logic

Templates

- presentation only
- no business logic

==================================================
Do NOT Implement
==================================================

Do not implement:

- Phase 8
- new models
- migrations
- charts
- graphs
- exports
- saved reports
- report builder
- report engine
- AI summaries
- background jobs
- caching
- placeholder functionality
- TODO implementations
- JavaScript dashboards

==================================================
Quality
==================================================

Avoid:

- duplicated query logic
- duplicated player search
- duplicated draft matching
- duplicated score calculations
- N+1 query patterns where practical

Use:

- dataclasses/read models
- select_related()
- prefetch_related()
- existing services

==================================================
Testing
==================================================

Implement every test described in the engineering plan.

Run:

python manage.py check
python manage.py makemigrations analytics --check
python manage.py test analytics
python manage.py test players
python manage.py test drafts
python manage.py test

==================================================
Final Quality Review
==================================================

Before finishing, perform one self-review.

Check for:

- unused imports
- dead code
- duplicated logic
- unnecessary services
- unnecessary queries
- TODO/FIXME comments
- architecture violations
- service responsibility violations

Fix any issues found before producing the final report.

==================================================
Final Report
==================================================

Report:

- implementation summary
- files created
- files modified
- migrations added (if any)
- test results
- implementation decisions
- technical debt identified
- results of the self-review
- confirmation that Phase 8 was not started
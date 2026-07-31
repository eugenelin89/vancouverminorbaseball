# Prompt 107 - Platform

## User Prompt

```text
You are working in the production Django repository:

/Users/eugenelin/dev/vmba0

GitHub repository:

https://github.com/eugenelin89/vancouverminorbaseball

Production site:

https://vancouverminor.com/

The production system is already actively used. Existing functionality must not be broken.

A source workbook should be attached to this task:

2026 VCB House - 13u PeeWee Assessment(1).xlsx

Do not commit the workbook or any real player data to Git.

# Objective

Implement a production-safe, versioned assessment subsystem inside the existing `analytics` app.

The subsystem must support:

- the current 2026 13U assessment workbook
- future assessment formats that may use different metrics
- future rating scales
- different spreadsheet layouts
- renamed columns and worksheets
- changed scoring formulas
- new or removed assessment items
- longitudinal player assessment history

This must be added beside the existing evaluation system without changing the behaviour or calculations of current self, peer, coach, staff, or guest evaluations.

The first release must be staff-only and feature-flagged.

Do not add player- or parent-facing assessment publication in this task.

Do not add trend charts or new ranking algorithms in this task.

Do not mix assessment measurements into existing evaluation averages or player comparison calculations.

# Critical production-safety rule

Treat the current system as live and stable.

The implementation must be additive and isolated.

Do not change the meaning, validation, calculations, workflow, permissions, or storage behaviour of:

- `analytics.Observation`
- `analytics.ObservationResponse`
- `analytics.ObservationQuestion`
- `analytics.ObservationQuestionSet`
- existing `rating_1_5` responses
- evaluation submission
- self evaluations
- peer evaluations
- coach evaluations
- staff evaluations
- guest evaluations
- submitted evaluation review
- My Evaluations
- coach assessment reports
- current player comparison scores
- current player timeline behaviour
- player import
- coach import
- account provisioning
- roster import
- authentication
- existing URLs

Do not reuse `pdp.PlayerProfile`, `pdp.Season`, or the old PDP evaluation models for this feature.

Use the current canonical models:

- `players.Player`
- `seasons.Season`
- `seasons.SeasonTeam`
- `seasons.PlayerRosterMembership`

Do not create a second player identity system.

# First: audit the existing repository

Before writing code, inspect the repository thoroughly.

At minimum, inspect:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/USER_MANUAL.md`
- `docs/deployment/README.md`
- `docs/deployment/RUNBOOK.md`
- `docs/product/PLATFORM_V2_ROADMAP.md`
- `analytics/models.py`
- `analytics/views.py`
- `analytics/urls.py`
- `analytics/admin.py`
- `analytics/forms.py`
- `analytics/assessment_forms.py`
- `analytics/services/`
- `analytics/templates/analytics/`
- `analytics/tests/`
- `players/models.py`
- `players/services/import_service.py`
- `seasons/models.py`
- `accounts/services/`
- `pdp/models.py`
- shared navigation templates
- `static/css/pdp.css`
- `static/css/styles.css`
- `requirements.txt`
- `requirements-dev.txt`
- current migrations
- current feature-setting conventions
- current import preview/commit patterns
- current permission mixins
- current test conventions

Confirm the current production architecture before choosing exact file names or implementation details.

Inspect the Git working tree before making changes.

Preserve the unrelated existing local modification:

/Users/eugenelin/dev/vmba0/docs/qa/platform_e2e/test_coaches_import.csv

Do not stage, commit, modify, or discard that file.

# Inspect the workbook before implementing its mapping

Open and inspect the attached workbook directly.

Verify:

- worksheet names
- header rows
- identity columns
- player-name format
- merged cells
- formulas
- numeric cells
- blank cells
- zero values
- ranking sheets
- assessment sheets
- pitching sheets
- units
- rating scales
- duplicated player names
- players appearing in one sheet but not another
- any annotations such as asterisks or question marks
- whether formulas are stored with cached values
- whether names must be joined across sheets

The expected workbook may contain sheets similar to:

- `Assessment Data`
- `Pitching Data`
- `Ranking`
- `Pitcher Ranking`

Do not assume those names or structures are exact until inspecting the actual workbook.

Do not silently infer that every zero means missing.

Missing-value and zero-value rules must be explicit in a versioned import mapping.

If the workbook is unavailable, do not invent its headers or mappings. Implement the generic framework, leave the workbook-specific bootstrap configuration uncreated, and report the missing-file blocker clearly.

# Conceptual architecture

The platform currently has human evaluations:

Player
└── Evaluations
    ├── Self
    ├── Peer
    ├── Coach
    ├── Staff
    └── Guest

Add a separate assessment domain:

Player
└── Assessments
    ├── Athletic measurements
    ├── Hitting measurements
    ├── Fielding ratings
    ├── Throwing ratings
    ├── Pitching measurements
    └── Pitch repertoire

Evaluations answer:

“What do evaluators think about the player?”

Assessments answer:

“What did the player measure or demonstrate during a testing event?”

They may appear together on a player profile later, but their storage and calculations must remain separate.

# Required versioning concepts

The design must separate these concepts.

## 1. Stable metric definition

A stable metric represents the general meaning of a measurement.

Examples:

- `home_to_first`
- `broad_jump`
- `bat_speed`
- `average_exit_velocity`
- `maximum_exit_velocity`
- `fielding_footwork`
- `fundamental_throwing`
- `pitching_command`
- `pitch_type_1`

Stable metric keys allow compatible results to be recognized across years.

A metric definition should not assume that every assessment uses it.

## 2. Assessment template and template version

An assessment template defines which metrics are used in a particular assessment format.

Examples:

- `13U House Assessment v1` for 2026
- `13U House Assessment v2` for 2027

Template versions must be historical and immutable after use.

A new year or changed assessment process should create a new version rather than modifying the old version.

The template-specific metric configuration must support:

- category
- display name
- display order
- value type
- unit
- required/optional status
- minimum value
- maximum value
- rating scale minimum
- rating scale maximum
- higher-is-better, lower-is-better, or neutral
- help text
- rubric
- metadata

A 2026 rating of `2 / 3` must remain distinguishable from a 2027 rating of `2 / 5`.

## 3. Assessment event

An assessment event represents when testing occurred.

Example:

- Name: `2026 VCB House 13U Assessment`
- Season: 2026
- Division: 13U House
- Date or date range
- Template: `13U House Assessment v1`
- Scoring profile: `2026 13U House v1`

Future events may point to different template versions.

## 4. Player assessment

A player assessment represents one canonical player’s results from one event.

It must reference:

- `players.Player`
- assessment event
- optional `PlayerRosterMembership`
- source import batch
- source row provenance
- status
- metadata

Normally, one player should have one player assessment for one event.

## 5. Assessment values

Assessment values store individual results.

They must support:

- numeric values
- ratings with their original scale
- text values
- choice values
- raw source value
- normalized value
- unit
- source sheet
- source row
- source column/header
- metadata
- provenance
- whether a value was imported
- whether a value was manually corrected or overridden

A manually corrected value must not be overwritten silently by a future import.

## 6. Scoring profile

Scoring and ranking formulas may change from year to year.

Add a versioned scoring-profile concept capable of storing:

- stable key
- name
- version
- description
- JSON configuration
- active/retired state
- metadata

An event may point to a scoring profile.

For this first release:

- store the scoring profile and its version
- preserve the workbook’s ranking and calculated source data in import provenance
- do not yet build a broad new ranking engine unless it is required to validate the import
- do not add these scores to existing evaluation averages

A scoring profile used by committed assessment data must not be edited in place. A new version must be created.

## 7. Spreadsheet import template

Spreadsheet layout is not the permanent assessment definition.

Add a versioned import-template or mapping-profile concept capable of describing:

- expected sheets
- optional sheets
- header-row locations
- identity columns
- column-to-metric mappings
- rating transformations
- unit conversions
- missing-value rules
- zero-value rules
- pitch-name normalization
- sheet joins
- ignored columns
- source-ranking fields
- validation rules

A future workbook can use different worksheet names and headers while mapping to the same stable metric keys.

An import mapping used by a committed import must not be edited in place. Create a new version.

# Recommended model family

After reviewing repository conventions, implement equivalent models inside `analytics`.

Names may be adjusted to fit established conventions, but the responsibilities must remain clear.

Likely model family:

- `AssessmentMetricDefinition`
- `AssessmentTemplate`
- `AssessmentTemplateMetric`
- `AssessmentScoringProfile`
- `AssessmentEvent`
- `PlayerAssessment`
- `AssessmentValue`
- `AssessmentImportTemplate`
- `AssessmentImportBatch`
- `AssessmentImportRow`

Use additive migrations only.

Do not rename or alter existing analytics models.

Do not add foreign keys from existing production models to the new assessment tables unless absolutely necessary.

Prefer new tables referencing existing canonical models.

# Model and constraint requirements

Use database constraints and service validation where practical.

Required behaviours include:

- unique stable metric key
- unique template key/version
- unique template/metric relationship
- unique scoring-profile key/version
- unique import-template key/version
- unique player/event assessment
- unique player-assessment/template-metric value
- assessment event must reference a compatible template
- player roster membership, when supplied, must belong to the same player and season
- imported values must retain source provenance
- committed imports must retain configuration snapshots
- historical templates and import mappings must not be mutable after committed use
- manually overridden values must not be replaced without explicit confirmation
- duplicate imports must not silently create duplicate player assessments

Use database-portable Django features compatible with the project’s current production database.

# Feature flags

Add an environment-backed setting:

ANALYTICS_ASSESSMENTS_ENABLED=false

Default must be `false`.

When disabled:

- no assessment navigation is shown
- new assessment URLs are unavailable or return 404
- no existing pages change visually
- no background assessment behaviour occurs
- existing evaluation and import workflows remain unchanged

The setting must be documented.

Do not enable it automatically in production.

# Permissions

The first release must be staff-only.

Reuse the project’s existing staff permission pattern, such as `AnalyticsStaffRequiredMixin`, after verifying current conventions.

Only staff or superusers may:

- view assessment events
- view player assessments
- upload workbooks
- review import previews
- resolve player matches
- confirm imports
- view import provenance

Do not expose assessment data to ordinary players, parents, coaches, or guest evaluators in this task.

# Import workflow

Create a dedicated assessment import workflow.

Do not reuse or overload the existing player import workflow.

Suggested routes:

- `/analytics/assessments/`
- `/analytics/assessments/<int:pk>/`
- `/analytics/assessment-events/`
- `/analytics/assessment-events/<int:pk>/`
- `/analytics/assessment-imports/`
- `/analytics/assessment-imports/new/`
- `/analytics/assessment-imports/<int:pk>/preview/`
- `/analytics/assessment-imports/<int:pk>/matches/`
- `/analytics/assessment-imports/<int:pk>/confirm/`
- `/analytics/assessment-imports/<int:pk>/`

Adapt route naming to current conventions.

Workflow:

1. Staff creates or selects an assessment event.
2. Staff selects a versioned assessment template.
3. Staff selects a versioned workbook import template.
4. Staff uploads an XLSX workbook.
5. System parses the workbook.
6. System stores a sanitized preview and source provenance.
7. System matches spreadsheet identities to canonical players.
8. Ambiguous or unmatched rows require manual resolution.
9. System validates all values.
10. Staff reviews create/update/skip/conflict actions.
11. Staff explicitly confirms.
12. Commit occurs atomically.
13. System displays a reconciliation summary.

Creating the import batch and preview audit rows before confirmation is acceptable.

However, no `PlayerAssessment` or `AssessmentValue` records may be created or changed until explicit confirmation.

# Workbook parsing

Use `openpyxl` if appropriate.

First inspect `requirements.txt`.

If `openpyxl` is absent:

- add a pinned compatible dependency
- document it
- keep the dependency change minimal

Do not use LibreOffice conversion.

Do not depend on Excel being installed.

Do not use hard-coded column letters as the only mapping mechanism.

Use the import-template configuration to resolve sheets and headers.

Parsing must handle:

- blank rows
- merged cells where relevant
- formulas and cached values
- numeric strings
- text annotations
- unexpected columns
- renamed headers
- missing optional sheets
- missing required sheets
- duplicate names
- duplicate rows
- players appearing on only one sheet
- invalid numeric values
- ratings outside configured scales

Preserve the original raw value for auditability.

# Player matching

Match spreadsheet rows to existing `players.Player` records.

Matching order should be conservative:

1. configured external/source identifier, when available
2. exact normalized canonical full name within the selected season/division
3. exact preferred/display name
4. exact `PlayerAlias`
5. unique exact normalized name outside the selected roster
6. manual resolution

Do not use fuzzy matching for automatic commitment.

Fuzzy or approximate suggestions may be displayed for staff review, but they must never be auto-confirmed.

Do not automatically create a player from an unmatched spreadsheet row.

Do not modify existing player identity fields during an assessment import.

Do not create or modify roster memberships during an assessment import.

# Idempotency and update safety

Store a SHA-256 checksum of the uploaded workbook.

Uploading the same file again must show a warning.

Use an import identity based on appropriate stable fields, likely:

- assessment event
- canonical player
- template
- source mapping version

Repeated imports must not create duplicates.

Preview actions must clearly distinguish:

- create
- update imported values
- skip unchanged
- conflict
- blocked by manual override
- unmatched
- invalid

No existing data may be overwritten silently.

The commit operation must be wrapped in `transaction.atomic()`.

If one confirmed batch fails, no partial player-assessment data should remain.

# Manual override protection

Assessment values need explicit provenance.

At minimum, distinguish:

- imported value
- manually created value
- manually corrected value

A later import may update a prior imported value only when:

- the preview clearly shows the change
- staff explicitly confirms the update
- the value has not been manually overridden

A manually corrected value must produce a conflict or protected state.

# Current 2026 workbook configuration

After inspecting the actual workbook, add an idempotent bootstrap mechanism for the current assessment format.

Do not create production data automatically during migration.

Prefer an explicit management command such as:

python manage.py bootstrap_2026_13u_assessment --dry-run
python manage.py bootstrap_2026_13u_assessment

The exact command name may follow project conventions.

The command should create or verify:

- stable metric definitions
- `13U House Assessment v1`
- template metric configuration
- `2026 13U House v1` scoring-profile metadata
- the workbook import-template/mapping version

The command must:

- be idempotent
- support `--dry-run`
- not create player assessments
- not import the workbook
- not edit an already-used historical version
- report created, existing, conflicting, and skipped configuration

If workbook details differ from our prior assumptions, use the actual workbook as the source of truth.

Do not commit player names or player results into source code.

The configuration may define categories such as:

- Athleticism
- Hitting — Objective
- Hitting — Mechanics
- Fielding and Throwing
- Pitching — Objective
- Pitch Repertoire
- Pitching — Mechanics

Only use categories and metrics actually supported by the workbook.

# Ranking sheets

Treat raw assessment and pitching measurements as the permanent source data.

Do not import ranking sheets as ordinary player metrics.

The ranking sheets may be:

- parsed for reconciliation
- stored in sanitized batch provenance
- compared against future calculated results
- displayed in an import QA summary

Do not make imported rank positions the only stored representation of player performance.

Do not add rank values to existing evaluation averages.

# Staff UI

Build a focused, responsive staff-only interface using current project styles.

Required pages:

- assessment event list
- assessment event detail
- player-assessment detail
- assessment import list
- upload page
- preview page
- player-match resolution page
- import result/detail page

The player-assessment detail should group metrics by category and display:

- metric display name
- normalized value
- original rating scale
- unit
- missing/unavailable state
- source sheet/header
- import provenance
- manual-override status

Do not redesign unrelated pages.

Use existing CSS patterns.

Avoid inline CSS.

Do not introduce a frontend framework.

Mobile pages must not horizontally overflow.

# Existing player profile

A minimal staff-only assessment section may be added to the existing analytics player profile only when:

- the feature flag is enabled
- the viewer is staff
- tests confirm existing profile behaviour remains unchanged

The section may list assessment events and link to the new staff assessment detail.

Do not modify:

- existing evaluation score summaries
- existing comparison calculations
- current timeline ordering
- draft context
- player import history

Do not add assessment values to `get_player_score_summary()`.

Do not modify current coach-assessment averages.

# Historical immutability

Once committed player assessment data references a configuration:

- do not allow the assessment template version to be edited
- do not allow template metric scale/unit/meaning to be edited
- do not allow the scoring profile version to be edited
- do not allow the import mapping version to be edited

Provide a clone/new-version workflow or clear administrative guidance.

Do not silently reinterpret historical results using a newer template.

# Out of scope for this task

Do not implement:

- player or parent publication
- coach access to assessment reports
- email notifications
- assessment trend charts
- cross-year automatic conclusions
- broad ranking redesign
- predictive models
- combining assessment data with evaluation averages
- changing current draft logic
- changing current team-formation logic
- automatic player creation
- automatic roster changes
- deleting old PDP models
- migrating PDP data
- rewriting existing evaluation models
- REST APIs unless already required by current architecture
- background workers
- cloud storage changes

# Tests

Add comprehensive focused tests.

## Model tests

Test:

- uniqueness constraints
- player/event uniqueness
- metric-value uniqueness
- rating-scale preservation
- roster membership validation
- immutable-used-template behaviour
- immutable-used-mapping behaviour
- scoring-profile versioning
- manual-override protection

## Parser tests

Use synthetic workbooks generated in memory with fake player names.

Do not commit the real workbook.

Test:

- multiple sheets
- configurable headers
- renamed columns
- blank cells
- zero-value rules
- numeric strings
- invalid numeric strings
- missing required sheets
- missing optional sheets
- duplicate rows
- formulas/cached values where practical
- pitch annotations
- players appearing in only one component sheet

## Matching tests

Test:

- canonical full-name match
- preferred-name match
- alias match
- selected-season filtering
- ambiguous duplicate names
- unmatched names
- no auto-create
- no fuzzy auto-commit

## Import workflow tests

Test:

- upload creates preview batch only
- preview creates no player-assessment records
- invalid batches cannot commit
- unresolved matches cannot commit
- confirmation creates expected records
- transaction rollback on failure
- repeated import does not duplicate
- identical workbook checksum warning
- explicit update flow
- unchanged rows skip
- manual override blocks overwrite
- provenance is retained

## Permission and feature-flag tests

Test:

- feature disabled hides navigation
- feature disabled blocks new routes
- non-staff cannot access pages
- staff can access pages when enabled
- current evaluation pages still work when flag is off
- current evaluation pages still work when flag is on

## Regression tests

Do not remove or weaken existing tests.

Run and preserve behaviour for:

- evaluation submission
- self evaluation
- peer evaluation
- coach evaluation
- submitted evaluation review
- My Evaluations
- assessment detail
- player profile
- player comparison
- player import
- coach import
- account provisioning
- season and roster workflows
- draft workflows

# Verification commands

Run at minimum:

DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations --check
DJANGO_SECRET_KEY=test ANALYTICS_ASSESSMENTS_ENABLED=false python manage.py test
DJANGO_SECRET_KEY=test ANALYTICS_ASSESSMENTS_ENABLED=true python manage.py test
git diff --check

Also run Ruff, Black, and isort checks on changed Python files using the repository’s configured commands.

Run the full existing test suite.

Do not declare success unless the full suite passes.

# Migration safety

Migrations must be additive.

Allowed:

- new tables
- indexes on new tables
- constraints on new tables

Avoid:

- changing existing analytics columns
- rewriting existing records
- data migrations touching observations
- renaming existing fields
- deleting existing tables
- altering existing uniqueness constraints
- changing existing response validation

No current production record should be updated merely by running `migrate`.

The configuration bootstrap must be an explicit post-deployment command, not an automatic data migration.

# Deployment plan

Provide a production deployment plan in the final response.

It must use a staged rollout:

## Stage 1 — Deploy disabled

1. Back up the production database.
2. Pull the new commits.
3. Install any new pinned dependency.
4. Keep:

   ANALYTICS_ASSESSMENTS_ENABLED=false

5. Run:

   python manage.py check
   python manage.py migrate
   python manage.py collectstatic --noinput

6. Restart Gunicorn.
7. Smoke-test all existing evaluation and import workflows.
8. Confirm no new assessment navigation is visible.

## Stage 2 — Bootstrap configuration

1. Run the bootstrap command with `--dry-run`.
2. Review its output.
3. Run the bootstrap command normally.
4. Do not import player data yet.

## Stage 3 — Enable staff-only feature

1. Set:

   ANALYTICS_ASSESSMENTS_ENABLED=true

2. Restart Gunicorn.
3. Confirm only staff can see the new navigation and pages.
4. Upload the workbook.
5. Review all player matches.
6. Resolve every ambiguous or unmatched row.
7. Review all missing-value and zero-value transformations.
8. Confirm the preview creates no assessment records.

## Stage 4 — Controlled commit

1. Take another database backup.
2. Confirm the batch.
3. Reconcile imported records against the workbook.
4. Review the import audit summary.
5. Keep the feature staff-only.

# Rollback strategy

Document a safe rollback.

The immediate rollback must be:

- set `ANALYTICS_ASSESSMENTS_ENABLED=false`
- restart Gunicorn

Because the migration is additive, disabling the feature should restore the old visible behaviour without removing the new tables.

Do not recommend reversing migrations after production data has been imported unless there is a separately reviewed destructive rollback plan.

# Documentation

Update or add documentation covering:

- assessment architecture
- distinction between evaluations and assessments
- stable metric definitions
- template versioning
- event versioning
- scoring-profile versioning
- import-template versioning
- canonical player matching
- manual override protection
- import preview and commit workflow
- feature flag
- production rollout
- backup requirements
- rollback
- how to add a new 2027 template
- how to add a different workbook mapping without changing old data
- cross-year comparison limitations

Update the user manual for the staff import workflow.

Update deployment documentation for:

- dependency installation
- migration
- feature flag
- bootstrap command
- staged enablement

# Git discipline

- Inspect the working tree first.
- Do not include unrelated changes.
- Preserve:
  `/Users/eugenelin/dev/vmba0/docs/qa/platform_e2e/test_coaches_import.csv`
- Make focused commits.
- Push to the current branch.
- Archive this prompt as:
  `docs/prompts/prompt_107_platform.md`
  unless repository inspection shows that another number is now correct.
- Follow the project’s existing convention of committing the implementation and prompt archive separately.

Suggested implementation commit message:

Add versioned player assessment imports

Suggested prompt archive commit message:

Archive player assessment import prompt

# Final report

When finished, provide:

1. Repository areas reviewed.
2. Current production behaviours explicitly preserved.
3. Final architecture and why it is isolated from evaluations.
4. Models added.
5. Migrations added.
6. Constraints and immutability protections.
7. Feature-flag behaviour.
8. Workbook sheets and headers actually found.
9. Current 2026 template and import mapping created.
10. Missing-value and zero-value rules.
11. Player matching rules.
12. Import preview and commit behaviour.
13. Idempotency behaviour.
14. Manual override protection.
15. Staff routes and templates added.
16. Existing files modified.
17. Tests added.
18. Full verification results.
19. Confirmation that existing evaluation calculations were not changed.
20. Production deployment commands.
21. Backup and rollback instructions.
22. Commit hashes.
23. Remaining limitations and deliberately deferred work.

# Final standard

The completed work must make the platform ready to import and display the 2026 assessment workbook while remaining flexible for different assessment techniques and spreadsheet layouts in 2027 and beyond.

Historical assessment definitions must remain reproducible.

Spreadsheet layout must be treated as an import concern, not as the database schema.

Raw measurements and ratings must retain their original units and scales.

The existing production evaluation system must continue functioning exactly as it does before this change.
```

## Implementation Commit

9d5125e Add feature-flagged assessment workbook imports

## Commit Diff

```diff
diff --git a/README.md b/README.md
index bc39c0b..678c6f2 100644
--- a/README.md
+++ b/README.md
@@ -159,6 +159,7 @@ Key environment variables:
 - `DJANGO_SECRET_KEY` is required.
 - `DJANGO_DEBUG` defaults to false.
 - `COACH_IMPORT_DEFAULT_PASSWORD` is required before creating new coach accounts through coach import.
+- `ANALYTICS_ASSESSMENTS_ENABLED` defaults to false. Set to `true` only after assessment templates/events have been configured and staff are ready to import assessment workbooks.
 - `DJANGO_ALLOWED_HOSTS` defaults to `localhost,127.0.0.1`.
 - `DJANGO_STATIC_ROOT` defaults to `BASE_DIR / "staticfiles"`.
 - `DJANGO_MEDIA_ROOT` defaults to `BASE_DIR / "media"`.
diff --git a/analytics/admin.py b/analytics/admin.py
index bcaade0..2d3abd6 100644
--- a/analytics/admin.py
+++ b/analytics/admin.py
@@ -1,6 +1,15 @@
 from django.contrib import admin
 
 from analytics.models import (
+    AssessmentEvent,
+    AssessmentImportBatch,
+    AssessmentImportRow,
+    AssessmentImportTemplate,
+    AssessmentMetricDefinition,
+    AssessmentScoringProfile,
+    AssessmentTemplate,
+    AssessmentTemplateMetric,
+    AssessmentValue,
     EvaluationCycle,
     EvaluatorRole,
     Observation,
@@ -9,6 +18,7 @@ from analytics.models import (
     ObservationResponse,
     ObservationSource,
     ObservationType,
+    PlayerAssessment,
 )
 
 
@@ -188,3 +198,193 @@ class ObservationResponseAdmin(TimeStampedAdmin):
         "question__prompt",
         "text_value",
     )
+
+
+@admin.register(AssessmentMetricDefinition)
+class AssessmentMetricDefinitionAdmin(TimeStampedAdmin):
+    list_display = ("key", "name", "default_value_type", "default_unit", "is_active")
+    list_filter = ("default_value_type", "is_active")
+    search_fields = ("key", "name")
+
+
+class AssessmentTemplateMetricInline(admin.TabularInline):
+    model = AssessmentTemplateMetric
+    extra = 0
+    autocomplete_fields = ("metric",)
+    fields = (
+        "display_order",
+        "category",
+        "metric",
+        "display_name",
+        "value_type",
+        "unit",
+        "is_required",
+        "direction",
+    )
+
+
+@admin.register(AssessmentTemplate)
+class AssessmentTemplateAdmin(TimeStampedAdmin):
+    list_display = ("name", "key", "version", "is_active", "is_locked")
+    list_filter = ("is_active", "is_locked")
+    search_fields = ("key", "name")
+    inlines = [AssessmentTemplateMetricInline]
+
+
+@admin.register(AssessmentTemplateMetric)
+class AssessmentTemplateMetricAdmin(TimeStampedAdmin):
+    list_display = (
+        "display_name",
+        "template",
+        "category",
+        "display_order",
+        "value_type",
+        "unit",
+        "direction",
+    )
+    list_filter = ("template", "category", "value_type", "direction", "is_required")
+    search_fields = ("display_name", "metric__key", "metric__name", "template__name")
+    autocomplete_fields = ("template", "metric")
+
+
+@admin.register(AssessmentScoringProfile)
+class AssessmentScoringProfileAdmin(TimeStampedAdmin):
+    list_display = ("name", "key", "version", "is_active", "is_locked")
+    list_filter = ("is_active", "is_locked")
+    search_fields = ("key", "name")
+
+
+@admin.register(AssessmentImportTemplate)
+class AssessmentImportTemplateAdmin(TimeStampedAdmin):
+    list_display = ("name", "key", "version", "is_active", "is_locked")
+    list_filter = ("is_active", "is_locked")
+    search_fields = ("key", "name")
+    readonly_fields = TimeStampedAdmin.readonly_fields + ("config", "metadata")
+
+
+@admin.register(AssessmentEvent)
+class AssessmentEventAdmin(TimeStampedAdmin):
+    list_display = ("name", "season", "division", "template", "is_active")
+    list_filter = ("season", "division", "is_active", "template")
+    search_fields = ("name", "slug", "season__name", "division")
+    autocomplete_fields = ("template", "scoring_profile")
+    prepopulated_fields = {"slug": ("name",)}
+
+
+class AssessmentValueInline(admin.TabularInline):
+    model = AssessmentValue
+    extra = 0
+    can_delete = False
+    readonly_fields = (
+        "template_metric",
+        "numeric_value",
+        "rating_value",
+        "text_value",
+        "choice_value",
+        "raw_value",
+        "unit",
+        "source_sheet",
+        "source_row",
+        "source_header",
+        "source_kind",
+        "is_manual_override",
+        "metadata",
+        "created_at",
+        "updated_at",
+    )
+    fields = readonly_fields
+
+    def has_add_permission(self, request, obj=None):
+        return False
+
+
+@admin.register(PlayerAssessment)
+class PlayerAssessmentAdmin(TimeStampedAdmin):
+    list_display = ("player", "event", "status", "roster_membership", "import_batch")
+    list_filter = ("event", "status", "event__season")
+    search_fields = ("player__first_name", "player__last_name", "event__name")
+    autocomplete_fields = ("player", "event", "roster_membership", "import_batch")
+    inlines = [AssessmentValueInline]
+
+
+@admin.register(AssessmentValue)
+class AssessmentValueAdmin(TimeStampedAdmin):
+    list_display = (
+        "player_assessment",
+        "template_metric",
+        "numeric_value",
+        "rating_value",
+        "source_kind",
+        "is_manual_override",
+    )
+    list_filter = ("template_metric__category", "source_kind", "is_manual_override")
+    search_fields = (
+        "player_assessment__player__first_name",
+        "player_assessment__player__last_name",
+        "template_metric__display_name",
+    )
+    autocomplete_fields = ("player_assessment", "template_metric", "import_row")
+
+
+class AssessmentImportRowInline(admin.TabularInline):
+    model = AssessmentImportRow
+    extra = 0
+    can_delete = False
+    readonly_fields = (
+        "row_key",
+        "source_sheet",
+        "source_row",
+        "raw_identity",
+        "player",
+        "roster_membership",
+        "action",
+        "status",
+        "errors",
+        "values_snapshot",
+        "raw_row",
+        "metadata",
+        "created_at",
+        "updated_at",
+    )
+    fields = readonly_fields
+
+    def has_add_permission(self, request, obj=None):
+        return False
+
+
+@admin.register(AssessmentImportBatch)
+class AssessmentImportBatchAdmin(TimeStampedAdmin):
+    list_display = (
+        "original_filename",
+        "event",
+        "status",
+        "uploaded_by",
+        "created_at",
+        "committed_at",
+    )
+    list_filter = ("status", "event", "event__season")
+    search_fields = ("original_filename", "workbook_sha256", "event__name")
+    autocomplete_fields = ("event", "import_template", "uploaded_by")
+    readonly_fields = TimeStampedAdmin.readonly_fields + (
+        "workbook_sha256",
+        "preview_snapshot",
+        "config_snapshot",
+        "import_summary",
+        "committed_at",
+        "metadata",
+    )
+    inlines = [AssessmentImportRowInline]
+
+
+@admin.register(AssessmentImportRow)
+class AssessmentImportRowAdmin(TimeStampedAdmin):
+    list_display = ("batch", "source_sheet", "source_row", "raw_identity", "status")
+    list_filter = ("status", "source_sheet", "batch__event")
+    search_fields = ("raw_identity", "batch__original_filename", "batch__event__name")
+    autocomplete_fields = ("batch", "player", "roster_membership")
+    readonly_fields = TimeStampedAdmin.readonly_fields + (
+        "raw_row",
+        "values_snapshot",
+        "errors",
+        "metadata",
+    )
diff --git a/analytics/forms.py b/analytics/forms.py
index c78e4d2..f68ae3c 100644
--- a/analytics/forms.py
+++ b/analytics/forms.py
@@ -1,5 +1,11 @@
 from django import forms
 
+from analytics.models import (
+    AssessmentEvent,
+    AssessmentImportRow,
+    AssessmentImportTemplate,
+)
+from players.models import Player
 from players.services.import_service import SOURCE_CHOICES, build_column_choices
 from seasons.models import Season
 from seasons.services.season_service import get_current_season
@@ -105,3 +111,59 @@ def parse_conflict_resolutions(post_data):
                 "fields"
             ][field_name] = value
     return resolutions
+
+
+class AssessmentImportUploadForm(forms.Form):
+    event = forms.ModelChoiceField(queryset=AssessmentEvent.objects.none())
+    import_template = forms.ModelChoiceField(
+        queryset=AssessmentImportTemplate.objects.none()
+    )
+    workbook = forms.FileField(
+        help_text="Upload a versioned assessment .xlsx workbook."
+    )
+
+    def __init__(self, *args, **kwargs):
+        super().__init__(*args, **kwargs)
+        self.fields["event"].queryset = (
+            AssessmentEvent.objects.filter(is_active=True)
+            .select_related("season", "template")
+            .order_by("-starts_on", "name")
+        )
+        self.fields["import_template"].queryset = (
+            AssessmentImportTemplate.objects.filter(is_active=True).order_by(
+                "key", "-version"
+            )
+        )
+
+    def clean_workbook(self):
+        workbook = self.cleaned_data["workbook"]
+        if not workbook.name.lower().endswith(".xlsx"):
+            raise forms.ValidationError("Upload an .xlsx workbook.")
+        return workbook
+
+
+class AssessmentImportRowResolutionForm(forms.Form):
+    player = forms.ModelChoiceField(
+        queryset=Player.objects.none(),
+        required=False,
+        help_text="Choose the canonical player that this workbook row represents.",
+    )
+    skip = forms.BooleanField(required=False)
+
+    def __init__(self, *args, row: AssessmentImportRow, **kwargs):
+        super().__init__(*args, **kwargs)
+        self.row = row
+        self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by(
+            "last_name", "first_name", "id"
+        )
+        candidate_ids = row.metadata.get("candidate_ids", [])
+        if candidate_ids:
+            self.fields["player"].queryset = self.fields["player"].queryset.filter(
+                pk__in=candidate_ids
+            )
+
+    def clean(self):
+        cleaned_data = super().clean()
+        if not cleaned_data.get("skip") and not cleaned_data.get("player"):
+            raise forms.ValidationError("Choose a player or skip this row.")
+        return cleaned_data
diff --git a/analytics/management/__init__.py b/analytics/management/__init__.py
new file mode 100644
index 0000000..8b13789
--- /dev/null
+++ b/analytics/management/__init__.py
@@ -0,0 +1 @@
+
diff --git a/analytics/management/commands/__init__.py b/analytics/management/commands/__init__.py
new file mode 100644
index 0000000..8b13789
--- /dev/null
+++ b/analytics/management/commands/__init__.py
@@ -0,0 +1 @@
+
diff --git a/analytics/management/commands/bootstrap_2026_13u_assessment.py b/analytics/management/commands/bootstrap_2026_13u_assessment.py
new file mode 100644
index 0000000..28caeb7
--- /dev/null
+++ b/analytics/management/commands/bootstrap_2026_13u_assessment.py
@@ -0,0 +1,27 @@
+from django.core.management.base import BaseCommand
+
+from analytics.services.assessment_import_service import (
+    ensure_2026_13u_assessment_configuration,
+)
+
+
+class Command(BaseCommand):
+    help = "Create assessment configuration for the 2026 VCB House 13U workbook."
+
+    def add_arguments(self, parser):
+        parser.add_argument(
+            "--dry-run",
+            action="store_true",
+            help="Print the configuration plan without writing database records.",
+        )
+
+    def handle(self, *args, **options):
+        plan = ensure_2026_13u_assessment_configuration(
+            dry_run=options.get("dry_run", False)
+        )
+        mode = "Dry run" if options.get("dry_run", False) else "Configured"
+        self.stdout.write(
+            self.style.SUCCESS(
+                f"{mode} 2026 13U assessment template with {len(plan['metrics'])} metrics."
+            )
+        )
diff --git a/analytics/migrations/0006_assessmentevent_assessmentimportbatch_and_more.py b/analytics/migrations/0006_assessmentevent_assessmentimportbatch_and_more.py
new file mode 100644
index 0000000..692770b
--- /dev/null
+++ b/analytics/migrations/0006_assessmentevent_assessmentimportbatch_and_more.py
@@ -0,0 +1,405 @@
+# Generated by Django 4.2.30 on 2026-07-31 19:23
+
+from django.conf import settings
+from django.db import migrations, models
+import django.db.models.deletion
+
+
+class Migration(migrations.Migration):
+
+    dependencies = [
+        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
+        ('seasons', '0001_initial'),
+        ('players', '0003_playerimportbatch_season_and_more'),
+        ('analytics', '0005_alter_observationquestion_is_required'),
+    ]
+
+    operations = [
+        migrations.CreateModel(
+            name='AssessmentEvent',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('name', models.CharField(max_length=160)),
+                ('slug', models.SlugField(blank=True, max_length=180, unique=True)),
+                ('division', models.CharField(blank=True, max_length=80)),
+                ('starts_on', models.DateField(blank=True, null=True)),
+                ('ends_on', models.DateField(blank=True, null=True)),
+                ('is_active', models.BooleanField(default=True)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+            ],
+            options={
+                'ordering': ['-starts_on', 'name'],
+            },
+        ),
+        migrations.CreateModel(
+            name='AssessmentImportBatch',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('original_filename', models.CharField(max_length=255)),
+                ('workbook_sha256', models.CharField(max_length=64)),
+                ('status', models.CharField(choices=[('uploaded', 'Uploaded'), ('previewed', 'Previewed'), ('committed', 'Committed'), ('failed', 'Failed')], default='uploaded', max_length=40)),
+                ('preview_snapshot', models.JSONField(blank=True, default=dict)),
+                ('config_snapshot', models.JSONField(blank=True, default=dict)),
+                ('import_summary', models.JSONField(blank=True, default=dict)),
+                ('committed_at', models.DateTimeField(blank=True, null=True)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+            ],
+            options={
+                'ordering': ['-created_at', '-id'],
+            },
+        ),
+        migrations.CreateModel(
+            name='AssessmentImportRow',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('row_key', models.CharField(max_length=180)),
+                ('source_sheet', models.CharField(max_length=120)),
+                ('source_row', models.PositiveIntegerField()),
+                ('raw_identity', models.CharField(blank=True, max_length=180)),
+                ('action', models.CharField(blank=True, max_length=40)),
+                ('status', models.CharField(choices=[('matched', 'Matched'), ('unmatched', 'Unmatched'), ('ambiguous', 'Ambiguous'), ('invalid', 'Invalid'), ('skipped', 'Skipped'), ('committed', 'Committed')], default='unmatched', max_length=40)),
+                ('errors', models.JSONField(blank=True, default=list)),
+                ('values_snapshot', models.JSONField(blank=True, default=list)),
+                ('raw_row', models.JSONField(blank=True, default=dict)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+            ],
+            options={
+                'ordering': ['batch', 'source_sheet', 'source_row', 'id'],
+            },
+        ),
+        migrations.CreateModel(
+            name='AssessmentImportTemplate',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('key', models.SlugField(max_length=120)),
+                ('name', models.CharField(max_length=160)),
+                ('version', models.PositiveIntegerField(default=1)),
+                ('description', models.TextField(blank=True)),
+                ('config', models.JSONField(blank=True, default=dict)),
+                ('is_active', models.BooleanField(default=True)),
+                ('is_locked', models.BooleanField(default=False)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+            ],
+            options={
+                'ordering': ['key', '-version'],
+            },
+        ),
+        migrations.CreateModel(
+            name='AssessmentMetricDefinition',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('key', models.SlugField(max_length=120, unique=True)),
+                ('name', models.CharField(max_length=160)),
+                ('description', models.TextField(blank=True)),
+                ('default_value_type', models.CharField(choices=[('number', 'Number'), ('rating', 'Rating'), ('text', 'Text'), ('choice', 'Choice')], default='number', max_length=40)),
+                ('default_unit', models.CharField(blank=True, max_length=40)),
+                ('is_active', models.BooleanField(default=True)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+            ],
+            options={
+                'ordering': ['key'],
+            },
+        ),
+        migrations.CreateModel(
+            name='AssessmentScoringProfile',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('key', models.SlugField(max_length=120)),
+                ('name', models.CharField(max_length=160)),
+                ('version', models.PositiveIntegerField(default=1)),
+                ('description', models.TextField(blank=True)),
+                ('config', models.JSONField(blank=True, default=dict)),
+                ('is_active', models.BooleanField(default=True)),
+                ('is_locked', models.BooleanField(default=False)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+            ],
+            options={
+                'ordering': ['key', '-version'],
+            },
+        ),
+        migrations.CreateModel(
+            name='AssessmentTemplate',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('key', models.SlugField(max_length=120)),
+                ('name', models.CharField(max_length=160)),
+                ('version', models.PositiveIntegerField(default=1)),
+                ('description', models.TextField(blank=True)),
+                ('effective_from', models.DateField(blank=True, null=True)),
+                ('retired_on', models.DateField(blank=True, null=True)),
+                ('is_active', models.BooleanField(default=True)),
+                ('is_locked', models.BooleanField(default=False)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+            ],
+            options={
+                'ordering': ['key', '-version'],
+            },
+        ),
+        migrations.CreateModel(
+            name='AssessmentTemplateMetric',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('category', models.CharField(blank=True, max_length=120)),
+                ('display_name', models.CharField(max_length=160)),
+                ('display_order', models.PositiveIntegerField(default=0)),
+                ('value_type', models.CharField(choices=[('number', 'Number'), ('rating', 'Rating'), ('text', 'Text'), ('choice', 'Choice')], default='number', max_length=40)),
+                ('unit', models.CharField(blank=True, max_length=40)),
+                ('is_required', models.BooleanField(default=False)),
+                ('min_value', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
+                ('max_value', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
+                ('rating_scale_min', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
+                ('rating_scale_max', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
+                ('direction', models.CharField(choices=[('higher', 'Higher is better'), ('lower', 'Lower is better'), ('neutral', 'Neutral')], default='neutral', max_length=20)),
+                ('help_text', models.TextField(blank=True)),
+                ('rubric', models.JSONField(blank=True, default=dict)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+                ('metric', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='template_metrics', to='analytics.assessmentmetricdefinition')),
+                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='template_metrics', to='analytics.assessmenttemplate')),
+            ],
+            options={
+                'ordering': ['template', 'display_order', 'id'],
+            },
+        ),
+        migrations.CreateModel(
+            name='PlayerAssessment',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('source_row_key', models.CharField(blank=True, max_length=180)),
+                ('status', models.CharField(choices=[('draft', 'Draft'), ('committed', 'Committed')], default='draft', max_length=40)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+                ('event', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='player_assessments', to='analytics.assessmentevent')),
+                ('import_batch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player_assessments', to='analytics.assessmentimportbatch')),
+                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_records', to='players.player')),
+                ('roster_membership', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='assessment_records', to='seasons.playerrostermembership')),
+            ],
+            options={
+                'ordering': ['event', 'player__last_name', 'player__first_name', 'id'],
+            },
+        ),
+        migrations.CreateModel(
+            name='AssessmentValue',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('numeric_value', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
+                ('rating_value', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
+                ('rating_scale_min', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
+                ('rating_scale_max', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
+                ('text_value', models.TextField(blank=True)),
+                ('choice_value', models.CharField(blank=True, max_length=160)),
+                ('raw_value', models.TextField(blank=True)),
+                ('normalized_value', models.TextField(blank=True)),
+                ('unit', models.CharField(blank=True, max_length=40)),
+                ('source_sheet', models.CharField(blank=True, max_length=120)),
+                ('source_row', models.PositiveIntegerField(blank=True, null=True)),
+                ('source_column', models.CharField(blank=True, max_length=20)),
+                ('source_header', models.CharField(blank=True, max_length=160)),
+                ('source_kind', models.CharField(choices=[('imported', 'Imported'), ('manual', 'Manual'), ('manual_corrected', 'Manual Correction')], default='imported', max_length=40)),
+                ('is_imported', models.BooleanField(default=True)),
+                ('is_manual_override', models.BooleanField(default=False)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+                ('import_row', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assessment_values', to='analytics.assessmentimportrow')),
+                ('player_assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='analytics.playerassessment')),
+                ('template_metric', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assessment_values', to='analytics.assessmenttemplatemetric')),
+            ],
+            options={
+                'ordering': ['template_metric__display_order', 'id'],
+            },
+        ),
+        migrations.AddIndex(
+            model_name='assessmenttemplate',
+            index=models.Index(fields=['key', 'version'], name='analytics_a_key_eb15b4_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmenttemplate',
+            index=models.Index(fields=['is_active', 'key'], name='analytics_a_is_acti_90eff4_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='assessmenttemplate',
+            constraint=models.UniqueConstraint(fields=('key', 'version'), name='analytics_unique_assessment_template_version'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentscoringprofile',
+            index=models.Index(fields=['key', 'version'], name='analytics_a_key_f400cd_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentscoringprofile',
+            index=models.Index(fields=['is_active', 'key'], name='analytics_a_is_acti_8f1a48_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='assessmentscoringprofile',
+            constraint=models.UniqueConstraint(fields=('key', 'version'), name='analytics_unique_assessment_scoring_profile_version'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentmetricdefinition',
+            index=models.Index(fields=['is_active', 'key'], name='analytics_a_is_acti_af8128_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentimporttemplate',
+            index=models.Index(fields=['key', 'version'], name='analytics_a_key_db23b6_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentimporttemplate',
+            index=models.Index(fields=['is_active', 'key'], name='analytics_a_is_acti_7920fc_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='assessmentimporttemplate',
+            constraint=models.UniqueConstraint(fields=('key', 'version'), name='analytics_unique_assessment_import_template_version'),
+        ),
+        migrations.AddField(
+            model_name='assessmentimportrow',
+            name='batch',
+            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rows', to='analytics.assessmentimportbatch'),
+        ),
+        migrations.AddField(
+            model_name='assessmentimportrow',
+            name='player',
+            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assessment_import_rows', to='players.player'),
+        ),
+        migrations.AddField(
+            model_name='assessmentimportrow',
+            name='roster_membership',
+            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assessment_import_rows', to='seasons.playerrostermembership'),
+        ),
+        migrations.AddField(
+            model_name='assessmentimportbatch',
+            name='event',
+            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='import_batches', to='analytics.assessmentevent'),
+        ),
+        migrations.AddField(
+            model_name='assessmentimportbatch',
+            name='import_template',
+            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='import_batches', to='analytics.assessmentimporttemplate'),
+        ),
+        migrations.AddField(
+            model_name='assessmentimportbatch',
+            name='uploaded_by',
+            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assessment_import_batches', to=settings.AUTH_USER_MODEL),
+        ),
+        migrations.AddField(
+            model_name='assessmentevent',
+            name='scoring_profile',
+            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='events', to='analytics.assessmentscoringprofile'),
+        ),
+        migrations.AddField(
+            model_name='assessmentevent',
+            name='season',
+            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assessment_events', to='seasons.season'),
+        ),
+        migrations.AddField(
+            model_name='assessmentevent',
+            name='template',
+            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='events', to='analytics.assessmenttemplate'),
+        ),
+        migrations.AddIndex(
+            model_name='playerassessment',
+            index=models.Index(fields=['player', 'event'], name='analytics_p_player__dfe03f_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='playerassessment',
+            index=models.Index(fields=['event', 'status'], name='analytics_p_event_i_3f6c0f_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='playerassessment',
+            index=models.Index(fields=['import_batch'], name='analytics_p_import__32b6cf_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='playerassessment',
+            constraint=models.UniqueConstraint(fields=('player', 'event'), name='analytics_unique_player_assessment_per_event'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentvalue',
+            index=models.Index(fields=['player_assessment', 'template_metric'], name='analytics_a_player__06f8d5_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentvalue',
+            index=models.Index(fields=['template_metric', 'numeric_value'], name='analytics_a_templat_f67ba7_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentvalue',
+            index=models.Index(fields=['source_sheet', 'source_row'], name='analytics_a_source__1a2c8d_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentvalue',
+            index=models.Index(fields=['is_manual_override'], name='analytics_a_is_manu_d09571_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='assessmentvalue',
+            constraint=models.UniqueConstraint(fields=('player_assessment', 'template_metric'), name='analytics_unique_assessment_value_per_metric'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmenttemplatemetric',
+            index=models.Index(fields=['template', 'display_order'], name='analytics_a_templat_906453_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmenttemplatemetric',
+            index=models.Index(fields=['category', 'display_order'], name='analytics_a_categor_152f1b_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmenttemplatemetric',
+            index=models.Index(fields=['metric', 'template'], name='analytics_a_metric__78ceed_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='assessmenttemplatemetric',
+            constraint=models.UniqueConstraint(fields=('template', 'metric'), name='analytics_unique_metric_per_assessment_template'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentimportrow',
+            index=models.Index(fields=['batch', 'status'], name='analytics_a_batch_i_74ae38_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentimportrow',
+            index=models.Index(fields=['player', 'batch'], name='analytics_a_player__a7a96e_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentimportrow',
+            index=models.Index(fields=['source_sheet', 'source_row'], name='analytics_a_source__c0e066_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='assessmentimportrow',
+            constraint=models.UniqueConstraint(fields=('batch', 'row_key'), name='analytics_unique_assessment_import_row_key'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentimportbatch',
+            index=models.Index(fields=['event', 'status'], name='analytics_a_event_i_76debe_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentimportbatch',
+            index=models.Index(fields=['workbook_sha256'], name='analytics_a_workboo_1a357e_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentimportbatch',
+            index=models.Index(fields=['uploaded_by', '-created_at'], name='analytics_a_uploade_884708_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentevent',
+            index=models.Index(fields=['season', 'is_active'], name='analytics_a_season__b0de99_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentevent',
+            index=models.Index(fields=['division', 'is_active'], name='analytics_a_divisio_a3dd83_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='assessmentevent',
+            index=models.Index(fields=['slug'], name='analytics_a_slug_38de60_idx'),
+        ),
+    ]
diff --git a/analytics/models.py b/analytics/models.py
index 485dfd8..c538d29 100644
--- a/analytics/models.py
+++ b/analytics/models.py
@@ -57,6 +57,74 @@ EVALUATION_PERSPECTIVE_CHOICES = [
 
 EVALUATION_PERSPECTIVE_LABELS = dict(EVALUATION_PERSPECTIVE_CHOICES)
 
+ASSESSMENT_VALUE_TYPE_NUMBER = "number"
+ASSESSMENT_VALUE_TYPE_RATING = "rating"
+ASSESSMENT_VALUE_TYPE_TEXT = "text"
+ASSESSMENT_VALUE_TYPE_CHOICE = "choice"
+
+ASSESSMENT_VALUE_TYPE_CHOICES = [
+    (ASSESSMENT_VALUE_TYPE_NUMBER, "Number"),
+    (ASSESSMENT_VALUE_TYPE_RATING, "Rating"),
+    (ASSESSMENT_VALUE_TYPE_TEXT, "Text"),
+    (ASSESSMENT_VALUE_TYPE_CHOICE, "Choice"),
+]
+
+ASSESSMENT_DIRECTION_HIGHER = "higher"
+ASSESSMENT_DIRECTION_LOWER = "lower"
+ASSESSMENT_DIRECTION_NEUTRAL = "neutral"
+
+ASSESSMENT_DIRECTION_CHOICES = [
+    (ASSESSMENT_DIRECTION_HIGHER, "Higher is better"),
+    (ASSESSMENT_DIRECTION_LOWER, "Lower is better"),
+    (ASSESSMENT_DIRECTION_NEUTRAL, "Neutral"),
+]
+
+ASSESSMENT_STATUS_DRAFT = "draft"
+ASSESSMENT_STATUS_COMMITTED = "committed"
+
+ASSESSMENT_STATUS_CHOICES = [
+    (ASSESSMENT_STATUS_DRAFT, "Draft"),
+    (ASSESSMENT_STATUS_COMMITTED, "Committed"),
+]
+
+ASSESSMENT_IMPORT_STATUS_UPLOADED = "uploaded"
+ASSESSMENT_IMPORT_STATUS_PREVIEWED = "previewed"
+ASSESSMENT_IMPORT_STATUS_COMMITTED = "committed"
+ASSESSMENT_IMPORT_STATUS_FAILED = "failed"
+
+ASSESSMENT_IMPORT_STATUS_CHOICES = [
+    (ASSESSMENT_IMPORT_STATUS_UPLOADED, "Uploaded"),
+    (ASSESSMENT_IMPORT_STATUS_PREVIEWED, "Previewed"),
+    (ASSESSMENT_IMPORT_STATUS_COMMITTED, "Committed"),
+    (ASSESSMENT_IMPORT_STATUS_FAILED, "Failed"),
+]
+
+ASSESSMENT_IMPORT_ROW_MATCHED = "matched"
+ASSESSMENT_IMPORT_ROW_UNMATCHED = "unmatched"
+ASSESSMENT_IMPORT_ROW_AMBIGUOUS = "ambiguous"
+ASSESSMENT_IMPORT_ROW_INVALID = "invalid"
+ASSESSMENT_IMPORT_ROW_SKIPPED = "skipped"
+ASSESSMENT_IMPORT_ROW_COMMITTED = "committed"
+
+ASSESSMENT_IMPORT_ROW_STATUS_CHOICES = [
+    (ASSESSMENT_IMPORT_ROW_MATCHED, "Matched"),
+    (ASSESSMENT_IMPORT_ROW_UNMATCHED, "Unmatched"),
+    (ASSESSMENT_IMPORT_ROW_AMBIGUOUS, "Ambiguous"),
+    (ASSESSMENT_IMPORT_ROW_INVALID, "Invalid"),
+    (ASSESSMENT_IMPORT_ROW_SKIPPED, "Skipped"),
+    (ASSESSMENT_IMPORT_ROW_COMMITTED, "Committed"),
+]
+
+ASSESSMENT_VALUE_SOURCE_IMPORTED = "imported"
+ASSESSMENT_VALUE_SOURCE_MANUAL = "manual"
+ASSESSMENT_VALUE_SOURCE_MANUAL_CORRECTED = "manual_corrected"
+
+ASSESSMENT_VALUE_SOURCE_CHOICES = [
+    (ASSESSMENT_VALUE_SOURCE_IMPORTED, "Imported"),
+    (ASSESSMENT_VALUE_SOURCE_MANUAL, "Manual"),
+    (ASSESSMENT_VALUE_SOURCE_MANUAL_CORRECTED, "Manual Correction"),
+]
+
 
 class TimeStampedModel(models.Model):
     created_at = models.DateTimeField(auto_now_add=True)
@@ -510,3 +578,557 @@ class ObservationResponse(TimeStampedModel):
 
     def __str__(self) -> str:
         return f"{self.question} response"
+
+
+class AssessmentMetricDefinition(TimeStampedModel):
+    key = models.SlugField(max_length=120, unique=True)
+    name = models.CharField(max_length=160)
+    description = models.TextField(blank=True)
+    default_value_type = models.CharField(
+        max_length=40,
+        choices=ASSESSMENT_VALUE_TYPE_CHOICES,
+        default=ASSESSMENT_VALUE_TYPE_NUMBER,
+    )
+    default_unit = models.CharField(max_length=40, blank=True)
+    is_active = models.BooleanField(default=True)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["key"]
+        indexes = [
+            models.Index(fields=["is_active", "key"]),
+        ]
+
+    def __str__(self) -> str:
+        return self.name
+
+
+class AssessmentTemplate(TimeStampedModel):
+    key = models.SlugField(max_length=120)
+    name = models.CharField(max_length=160)
+    version = models.PositiveIntegerField(default=1)
+    description = models.TextField(blank=True)
+    effective_from = models.DateField(null=True, blank=True)
+    retired_on = models.DateField(null=True, blank=True)
+    is_active = models.BooleanField(default=True)
+    is_locked = models.BooleanField(default=False)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["key", "-version"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["key", "version"],
+                name="analytics_unique_assessment_template_version",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["key", "version"]),
+            models.Index(fields=["is_active", "key"]),
+        ]
+
+    def has_committed_assessments(self) -> bool:
+        if not self.pk:
+            return False
+        return PlayerAssessment.objects.filter(
+            event__template_id=self.pk,
+            status=ASSESSMENT_STATUS_COMMITTED,
+        ).exists()
+
+    def save(self, *args, **kwargs):
+        if self.pk and self.has_committed_assessments():
+            original = AssessmentTemplate.objects.get(pk=self.pk)
+            locked_fields = ["key", "version"]
+            for field_name in locked_fields:
+                if getattr(original, field_name) != getattr(self, field_name):
+                    raise ValidationError(
+                        {field_name: "Template identity cannot change after use."}
+                    )
+            self.is_locked = True
+        super().save(*args, **kwargs)
+
+    def __str__(self) -> str:
+        return f"{self.name} v{self.version}"
+
+
+class AssessmentTemplateMetric(TimeStampedModel):
+    template = models.ForeignKey(
+        AssessmentTemplate, on_delete=models.CASCADE, related_name="template_metrics"
+    )
+    metric = models.ForeignKey(
+        AssessmentMetricDefinition,
+        on_delete=models.PROTECT,
+        related_name="template_metrics",
+    )
+    category = models.CharField(max_length=120, blank=True)
+    display_name = models.CharField(max_length=160)
+    display_order = models.PositiveIntegerField(default=0)
+    value_type = models.CharField(
+        max_length=40,
+        choices=ASSESSMENT_VALUE_TYPE_CHOICES,
+        default=ASSESSMENT_VALUE_TYPE_NUMBER,
+    )
+    unit = models.CharField(max_length=40, blank=True)
+    is_required = models.BooleanField(default=False)
+    min_value = models.DecimalField(
+        max_digits=10, decimal_places=3, null=True, blank=True
+    )
+    max_value = models.DecimalField(
+        max_digits=10, decimal_places=3, null=True, blank=True
+    )
+    rating_scale_min = models.DecimalField(
+        max_digits=6, decimal_places=2, null=True, blank=True
+    )
+    rating_scale_max = models.DecimalField(
+        max_digits=6, decimal_places=2, null=True, blank=True
+    )
+    direction = models.CharField(
+        max_length=20,
+        choices=ASSESSMENT_DIRECTION_CHOICES,
+        default=ASSESSMENT_DIRECTION_NEUTRAL,
+    )
+    help_text = models.TextField(blank=True)
+    rubric = models.JSONField(default=dict, blank=True)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["template", "display_order", "id"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["template", "metric"],
+                name="analytics_unique_metric_per_assessment_template",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["template", "display_order"]),
+            models.Index(fields=["category", "display_order"]),
+            models.Index(fields=["metric", "template"]),
+        ]
+
+    def clean(self):
+        errors = {}
+        if self.min_value is not None and self.max_value is not None:
+            if self.max_value < self.min_value:
+                errors["max_value"] = "Maximum value cannot be less than minimum value."
+        if self.rating_scale_min is not None and self.rating_scale_max is not None:
+            if self.rating_scale_max < self.rating_scale_min:
+                errors["rating_scale_max"] = (
+                    "Rating scale maximum cannot be less than the minimum."
+                )
+        if errors:
+            raise ValidationError(errors)
+
+    def save(self, *args, **kwargs):
+        if self.pk and self.template.has_committed_assessments():
+            original = AssessmentTemplateMetric.objects.get(pk=self.pk)
+            locked_fields = [
+                "metric_id",
+                "category",
+                "display_name",
+                "display_order",
+                "value_type",
+                "unit",
+                "is_required",
+                "min_value",
+                "max_value",
+                "rating_scale_min",
+                "rating_scale_max",
+                "direction",
+                "rubric",
+            ]
+            for field_name in locked_fields:
+                if getattr(original, field_name) != getattr(self, field_name):
+                    raise ValidationError(
+                        {field_name: "Template metrics cannot change after use."}
+                    )
+            self.template.is_locked = True
+            self.template.save(update_fields=["is_locked", "updated_at"])
+        self.full_clean()
+        super().save(*args, **kwargs)
+
+    def __str__(self) -> str:
+        return self.display_name
+
+
+class AssessmentScoringProfile(TimeStampedModel):
+    key = models.SlugField(max_length=120)
+    name = models.CharField(max_length=160)
+    version = models.PositiveIntegerField(default=1)
+    description = models.TextField(blank=True)
+    config = models.JSONField(default=dict, blank=True)
+    is_active = models.BooleanField(default=True)
+    is_locked = models.BooleanField(default=False)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["key", "-version"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["key", "version"],
+                name="analytics_unique_assessment_scoring_profile_version",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["key", "version"]),
+            models.Index(fields=["is_active", "key"]),
+        ]
+
+    def has_committed_assessments(self) -> bool:
+        if not self.pk:
+            return False
+        return PlayerAssessment.objects.filter(
+            event__scoring_profile_id=self.pk,
+            status=ASSESSMENT_STATUS_COMMITTED,
+        ).exists()
+
+    def save(self, *args, **kwargs):
+        if self.pk and self.has_committed_assessments():
+            original = AssessmentScoringProfile.objects.get(pk=self.pk)
+            for field_name in ["key", "version", "config"]:
+                if getattr(original, field_name) != getattr(self, field_name):
+                    raise ValidationError(
+                        {field_name: "Scoring profile cannot change after use."}
+                    )
+            self.is_locked = True
+        super().save(*args, **kwargs)
+
+    def __str__(self) -> str:
+        return f"{self.name} v{self.version}"
+
+
+class AssessmentImportTemplate(TimeStampedModel):
+    key = models.SlugField(max_length=120)
+    name = models.CharField(max_length=160)
+    version = models.PositiveIntegerField(default=1)
+    description = models.TextField(blank=True)
+    config = models.JSONField(default=dict, blank=True)
+    is_active = models.BooleanField(default=True)
+    is_locked = models.BooleanField(default=False)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["key", "-version"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["key", "version"],
+                name="analytics_unique_assessment_import_template_version",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["key", "version"]),
+            models.Index(fields=["is_active", "key"]),
+        ]
+
+    def has_committed_imports(self) -> bool:
+        if not self.pk:
+            return False
+        return self.import_batches.filter(
+            status=ASSESSMENT_IMPORT_STATUS_COMMITTED
+        ).exists()
+
+    def save(self, *args, **kwargs):
+        if self.pk and self.has_committed_imports():
+            original = AssessmentImportTemplate.objects.get(pk=self.pk)
+            for field_name in ["key", "version", "config"]:
+                if getattr(original, field_name) != getattr(self, field_name):
+                    raise ValidationError(
+                        {field_name: "Import template cannot change after use."}
+                    )
+            self.is_locked = True
+        super().save(*args, **kwargs)
+
+    def __str__(self) -> str:
+        return f"{self.name} v{self.version}"
+
+
+class AssessmentEvent(TimeStampedModel):
+    name = models.CharField(max_length=160)
+    slug = models.SlugField(max_length=180, unique=True, blank=True)
+    season = models.ForeignKey(
+        "seasons.Season", on_delete=models.PROTECT, related_name="assessment_events"
+    )
+    division = models.CharField(max_length=80, blank=True)
+    starts_on = models.DateField(null=True, blank=True)
+    ends_on = models.DateField(null=True, blank=True)
+    template = models.ForeignKey(
+        AssessmentTemplate, on_delete=models.PROTECT, related_name="events"
+    )
+    scoring_profile = models.ForeignKey(
+        AssessmentScoringProfile,
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="events",
+    )
+    is_active = models.BooleanField(default=True)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["-starts_on", "name"]
+        indexes = [
+            models.Index(fields=["season", "is_active"]),
+            models.Index(fields=["division", "is_active"]),
+            models.Index(fields=["slug"]),
+        ]
+
+    def clean(self):
+        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
+            raise ValidationError(
+                {"ends_on": "Assessment event end date cannot be before start date."}
+            )
+
+    def save(self, *args, **kwargs):
+        if not self.slug:
+            self.slug = unique_slug_for_model(self, self.name)
+        self.full_clean()
+        super().save(*args, **kwargs)
+
+    def __str__(self) -> str:
+        return self.name
+
+
+class AssessmentImportBatch(TimeStampedModel):
+    event = models.ForeignKey(
+        AssessmentEvent, on_delete=models.PROTECT, related_name="import_batches"
+    )
+    import_template = models.ForeignKey(
+        AssessmentImportTemplate,
+        on_delete=models.PROTECT,
+        related_name="import_batches",
+    )
+    uploaded_by = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="assessment_import_batches",
+    )
+    original_filename = models.CharField(max_length=255)
+    workbook_sha256 = models.CharField(max_length=64)
+    status = models.CharField(
+        max_length=40,
+        choices=ASSESSMENT_IMPORT_STATUS_CHOICES,
+        default=ASSESSMENT_IMPORT_STATUS_UPLOADED,
+    )
+    preview_snapshot = models.JSONField(default=dict, blank=True)
+    config_snapshot = models.JSONField(default=dict, blank=True)
+    import_summary = models.JSONField(default=dict, blank=True)
+    committed_at = models.DateTimeField(null=True, blank=True)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["-created_at", "-id"]
+        indexes = [
+            models.Index(fields=["event", "status"]),
+            models.Index(fields=["workbook_sha256"]),
+            models.Index(fields=["uploaded_by", "-created_at"]),
+        ]
+
+    def __str__(self) -> str:
+        return self.original_filename
+
+
+class PlayerAssessment(TimeStampedModel):
+    player = models.ForeignKey(
+        "players.Player", on_delete=models.CASCADE, related_name="assessment_records"
+    )
+    event = models.ForeignKey(
+        AssessmentEvent, on_delete=models.PROTECT, related_name="player_assessments"
+    )
+    roster_membership = models.ForeignKey(
+        "seasons.PlayerRosterMembership",
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="assessment_records",
+    )
+    import_batch = models.ForeignKey(
+        AssessmentImportBatch,
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="player_assessments",
+    )
+    source_row_key = models.CharField(max_length=180, blank=True)
+    status = models.CharField(
+        max_length=40,
+        choices=ASSESSMENT_STATUS_CHOICES,
+        default=ASSESSMENT_STATUS_DRAFT,
+    )
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["event", "player__last_name", "player__first_name", "id"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["player", "event"],
+                name="analytics_unique_player_assessment_per_event",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["player", "event"]),
+            models.Index(fields=["event", "status"]),
+            models.Index(fields=["import_batch"]),
+        ]
+
+    def clean(self):
+        errors = {}
+        if self.roster_membership_id:
+            if self.roster_membership.player_id != self.player_id:
+                errors["roster_membership"] = (
+                    "Roster membership must belong to the assessed player."
+                )
+            if (
+                self.event_id
+                and self.roster_membership.season.id != self.event.season_id
+            ):
+                errors["roster_membership"] = (
+                    "Roster membership season must match the assessment event season."
+                )
+        if self.import_batch_id and self.event_id:
+            if self.import_batch.event_id != self.event_id:
+                errors["import_batch"] = (
+                    "Import batch must belong to the same assessment event."
+                )
+        if errors:
+            raise ValidationError(errors)
+
+    def save(self, *args, **kwargs):
+        self.full_clean()
+        super().save(*args, **kwargs)
+
+    def __str__(self) -> str:
+        return f"{self.event}: {self.player}"
+
+
+class AssessmentImportRow(TimeStampedModel):
+    batch = models.ForeignKey(
+        AssessmentImportBatch, on_delete=models.CASCADE, related_name="rows"
+    )
+    row_key = models.CharField(max_length=180)
+    source_sheet = models.CharField(max_length=120)
+    source_row = models.PositiveIntegerField()
+    raw_identity = models.CharField(max_length=180, blank=True)
+    player = models.ForeignKey(
+        "players.Player",
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="assessment_import_rows",
+    )
+    roster_membership = models.ForeignKey(
+        "seasons.PlayerRosterMembership",
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="assessment_import_rows",
+    )
+    action = models.CharField(max_length=40, blank=True)
+    status = models.CharField(
+        max_length=40,
+        choices=ASSESSMENT_IMPORT_ROW_STATUS_CHOICES,
+        default=ASSESSMENT_IMPORT_ROW_UNMATCHED,
+    )
+    errors = models.JSONField(default=list, blank=True)
+    values_snapshot = models.JSONField(default=list, blank=True)
+    raw_row = models.JSONField(default=dict, blank=True)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["batch", "source_sheet", "source_row", "id"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["batch", "row_key"],
+                name="analytics_unique_assessment_import_row_key",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["batch", "status"]),
+            models.Index(fields=["player", "batch"]),
+            models.Index(fields=["source_sheet", "source_row"]),
+        ]
+
+    def __str__(self) -> str:
+        return f"{self.batch} row {self.source_row}"
+
+
+class AssessmentValue(TimeStampedModel):
+    player_assessment = models.ForeignKey(
+        PlayerAssessment, on_delete=models.CASCADE, related_name="values"
+    )
+    template_metric = models.ForeignKey(
+        AssessmentTemplateMetric,
+        on_delete=models.PROTECT,
+        related_name="assessment_values",
+    )
+    numeric_value = models.DecimalField(
+        max_digits=10, decimal_places=3, null=True, blank=True
+    )
+    rating_value = models.DecimalField(
+        max_digits=6, decimal_places=2, null=True, blank=True
+    )
+    rating_scale_min = models.DecimalField(
+        max_digits=6, decimal_places=2, null=True, blank=True
+    )
+    rating_scale_max = models.DecimalField(
+        max_digits=6, decimal_places=2, null=True, blank=True
+    )
+    text_value = models.TextField(blank=True)
+    choice_value = models.CharField(max_length=160, blank=True)
+    raw_value = models.TextField(blank=True)
+    normalized_value = models.TextField(blank=True)
+    unit = models.CharField(max_length=40, blank=True)
+    source_sheet = models.CharField(max_length=120, blank=True)
+    source_row = models.PositiveIntegerField(null=True, blank=True)
+    source_column = models.CharField(max_length=20, blank=True)
+    source_header = models.CharField(max_length=160, blank=True)
+    source_kind = models.CharField(
+        max_length=40,
+        choices=ASSESSMENT_VALUE_SOURCE_CHOICES,
+        default=ASSESSMENT_VALUE_SOURCE_IMPORTED,
+    )
+    is_imported = models.BooleanField(default=True)
+    is_manual_override = models.BooleanField(default=False)
+    import_row = models.ForeignKey(
+        AssessmentImportRow,
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="assessment_values",
+    )
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["template_metric__display_order", "id"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["player_assessment", "template_metric"],
+                name="analytics_unique_assessment_value_per_metric",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["player_assessment", "template_metric"]),
+            models.Index(fields=["template_metric", "numeric_value"]),
+            models.Index(fields=["source_sheet", "source_row"]),
+            models.Index(fields=["is_manual_override"]),
+        ]
+
+    def clean(self):
+        errors = {}
+        if self.player_assessment_id and self.template_metric_id:
+            if (
+                self.template_metric.template_id
+                != self.player_assessment.event.template_id
+            ):
+                errors["template_metric"] = (
+                    "Assessment value metric must belong to the event template."
+                )
+        if errors:
+            raise ValidationError(errors)
+
+    def save(self, *args, **kwargs):
+        self.full_clean()
+        super().save(*args, **kwargs)
+
+    def __str__(self) -> str:
+        return f"{self.player_assessment} - {self.template_metric}"
diff --git a/analytics/services/assessment_feature.py b/analytics/services/assessment_feature.py
new file mode 100644
index 0000000..1e681ce
--- /dev/null
+++ b/analytics/services/assessment_feature.py
@@ -0,0 +1,6 @@
+from django.conf import settings
+
+
+def assessments_enabled() -> bool:
+    """Return whether the versioned assessment subsystem is enabled."""
+    return bool(getattr(settings, "ANALYTICS_ASSESSMENTS_ENABLED", False))
diff --git a/analytics/services/assessment_import_service.py b/analytics/services/assessment_import_service.py
new file mode 100644
index 0000000..75c2248
--- /dev/null
+++ b/analytics/services/assessment_import_service.py
@@ -0,0 +1,862 @@
+from __future__ import annotations
+
+import hashlib
+import json
+from dataclasses import dataclass
+from decimal import Decimal, InvalidOperation
+from io import BytesIO
+from pathlib import Path
+from typing import BinaryIO
+
+from django.core.exceptions import PermissionDenied, ValidationError
+from django.db import transaction
+from django.utils import timezone
+from django.utils.text import slugify
+from openpyxl import load_workbook
+from openpyxl.utils import get_column_letter
+
+from analytics.models import (
+    ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
+    ASSESSMENT_IMPORT_ROW_COMMITTED,
+    ASSESSMENT_IMPORT_ROW_INVALID,
+    ASSESSMENT_IMPORT_ROW_MATCHED,
+    ASSESSMENT_IMPORT_ROW_SKIPPED,
+    ASSESSMENT_IMPORT_ROW_UNMATCHED,
+    ASSESSMENT_IMPORT_STATUS_COMMITTED,
+    ASSESSMENT_IMPORT_STATUS_FAILED,
+    ASSESSMENT_IMPORT_STATUS_PREVIEWED,
+    ASSESSMENT_STATUS_COMMITTED,
+    ASSESSMENT_VALUE_SOURCE_IMPORTED,
+    ASSESSMENT_VALUE_TYPE_NUMBER,
+    ASSESSMENT_VALUE_TYPE_RATING,
+    AssessmentImportBatch,
+    AssessmentImportRow,
+    AssessmentImportTemplate,
+    AssessmentMetricDefinition,
+    AssessmentScoringProfile,
+    AssessmentTemplate,
+    AssessmentTemplateMetric,
+    AssessmentValue,
+    PlayerAssessment,
+)
+from analytics.services.assessment_matching_service import (
+    MATCH_AMBIGUOUS,
+    MATCH_UNMATCHED,
+    match_player_for_assessment,
+    normalize_assessment_name,
+)
+from players.models import Player
+
+BOOTSTRAP_2026_13U_ASSESSMENT_KEY = "2026-13u-house-assessment"
+BOOTSTRAP_2026_13U_IMPORT_KEY = "2026-13u-house-assessment-xlsx"
+
+
+DEFAULT_2026_13U_DATA_SHEETS = [
+    {
+        "name": "Assessment Data",
+        "header_row": 2,
+        "identity_column": "Name",
+        "category_row": 1,
+        "metrics": [
+            {
+                "header": "Home to 1st",
+                "key": "home_to_1st",
+                "category": "Athleticism Evaluation",
+                "unit": "seconds",
+                "direction": "lower",
+            },
+            {
+                "header": "Broad Jump",
+                "key": "broad_jump",
+                "category": "Athleticism Evaluation",
+                "unit": "inches",
+                "direction": "higher",
+            },
+            {
+                "header": "Lateral Jump",
+                "key": "lateral_jump",
+                "category": "Athleticism Evaluation",
+                "unit": "inches",
+                "direction": "higher",
+            },
+            {
+                "header": "Shotput",
+                "key": "shotput",
+                "category": "Athleticism Evaluation",
+                "unit": "feet",
+                "direction": "higher",
+            },
+            {
+                "header": "Bat Speed",
+                "key": "bat_speed",
+                "category": "Hitting Objective Evaluation",
+                "unit": "mph",
+                "direction": "higher",
+            },
+            {
+                "header": "Time 2 Contact",
+                "key": "time_to_contact",
+                "category": "Hitting Objective Evaluation",
+                "unit": "seconds",
+                "direction": "lower",
+            },
+            {
+                "header": "Exit Velocity Avg.",
+                "key": "exit_velocity_avg",
+                "category": "Hitting Objective Evaluation",
+                "unit": "mph",
+                "direction": "higher",
+            },
+            {
+                "header": "Exit Velocity Max",
+                "key": "exit_velocity_max",
+                "category": "Hitting Objective Evaluation",
+                "unit": "mph",
+                "direction": "higher",
+            },
+            {
+                "header": "Athletic Stance",
+                "key": "athletic_stance",
+                "category": "Hitting Subjective Evaluation",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Balance Stride",
+                "key": "balance_stride",
+                "category": "Hitting Subjective Evaluation",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Barrel Level",
+                "key": "barrel_level",
+                "category": "Hitting Subjective Evaluation",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Launch Position",
+                "key": "launch_position",
+                "category": "Hitting Subjective Evaluation",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Follow Through",
+                "key": "follow_through",
+                "category": "Hitting Subjective Evaluation",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Readiness",
+                "key": "fielding_readiness",
+                "category": "Fielding and Throwing Evaluation",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Footwork",
+                "key": "fielding_footwork",
+                "category": "Fielding and Throwing Evaluation",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Glovework",
+                "key": "fielding_glovework",
+                "category": "Fielding and Throwing Evaluation",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Athleticism",
+                "key": "fielding_athleticism",
+                "category": "Fielding and Throwing Evaluation",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Fundamental Throwing",
+                "key": "fundamental_throwing",
+                "category": "Fielding and Throwing Evaluation",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+        ],
+    },
+    {
+        "name": "Pitching Data",
+        "header_row": 2,
+        "identity_column": "Name",
+        "metrics": [
+            {
+                "header": "Velocity Avg.",
+                "key": "pitching_velocity_avg",
+                "category": "Pitching Data",
+                "unit": "mph",
+                "direction": "higher",
+            },
+            {
+                "header": "Velocity Max",
+                "key": "pitching_velocity_max",
+                "category": "Pitching Data",
+                "unit": "mph",
+                "direction": "higher",
+            },
+            {
+                "header": "Pitch 1",
+                "key": "pitch_1",
+                "category": "Pitching Data",
+                "value_type": "text",
+            },
+            {
+                "header": "Pitch 2",
+                "key": "pitch_2",
+                "category": "Pitching Data",
+                "value_type": "text",
+            },
+            {
+                "header": "Pitch 3",
+                "key": "pitch_3",
+                "category": "Pitching Data",
+                "value_type": "text",
+            },
+            {
+                "header": "Pitch 4",
+                "key": "pitch_4",
+                "category": "Pitching Data",
+                "value_type": "text",
+            },
+            {
+                "header": "Athletic Movement",
+                "key": "pitching_athletic_movement",
+                "category": "Pitching Data",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Body Control",
+                "key": "pitching_body_control",
+                "category": "Pitching Data",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Direction",
+                "key": "pitching_direction",
+                "category": "Pitching Data",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Repeatability",
+                "key": "pitching_repeatability",
+                "category": "Pitching Data",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+            {
+                "header": "Command2",
+                "key": "pitching_command",
+                "category": "Pitching Data",
+                "value_type": "rating",
+                "direction": "higher",
+            },
+        ],
+    },
+]
+
+DEFAULT_2026_13U_RANKING_SHEETS = ["Ranking", "Pitcher Ranking"]
+
+
+@dataclass(frozen=True)
+class AssessmentPreviewSummary:
+    rows: int
+    matched: int
+    unmatched: int
+    ambiguous: int
+    invalid: int
+    skipped: int
+    checksum_seen_before: bool
+
+    @property
+    def can_commit(self) -> bool:
+        return self.unmatched == 0 and self.ambiguous == 0 and self.invalid == 0
+
+
+@dataclass(frozen=True)
+class AssessmentCommitResult:
+    processed: int
+    created: int
+    updated: int
+    skipped: int
+
+
+def normalize_sheet_name(value: str) -> str:
+    return " ".join(str(value or "").strip().casefold().split())
+
+
+def normalize_header(value: str) -> str:
+    return normalize_sheet_name(value).replace(".", "").replace(" ", "_")
+
+
+def _workbook_bytes(file_obj: BinaryIO) -> bytes:
+    position = file_obj.tell() if hasattr(file_obj, "tell") else None
+    content = file_obj.read()
+    if position is not None and hasattr(file_obj, "seek"):
+        file_obj.seek(position)
+    return content
+
+
+def workbook_sha256(content: bytes) -> str:
+    return hashlib.sha256(content).hexdigest()
+
+
+def _load_workbook_from_bytes(content: bytes):
+    return load_workbook(BytesIO(content), read_only=True, data_only=True)
+
+
+def _worksheet_by_name(workbook, configured_name: str):
+    normalized = normalize_sheet_name(configured_name)
+    for sheet_name in workbook.sheetnames:
+        if normalize_sheet_name(sheet_name) == normalized:
+            return workbook[sheet_name]
+    return None
+
+
+def _row_values(row) -> list:
+    return [cell for cell in row]
+
+
+def _header_map(row_values: list) -> dict[str, int]:
+    mapping = {}
+    for index, value in enumerate(row_values):
+        if value not in (None, ""):
+            mapping[normalize_header(value)] = index
+    return mapping
+
+
+def _decimal_or_none(value) -> Decimal | None:
+    if value in (None, ""):
+        return None
+    try:
+        return Decimal(str(value).strip())
+    except (InvalidOperation, ValueError):
+        return None
+
+
+def _snapshot_value(
+    metric_config: dict,
+    raw_value,
+    *,
+    sheet_name: str,
+    row_number: int,
+    column_index: int,
+) -> dict | None:
+    if raw_value in (None, ""):
+        return None
+    value_type = metric_config.get("value_type") or ASSESSMENT_VALUE_TYPE_NUMBER
+    raw_text = str(raw_value).strip()
+    snapshot = {
+        "metric_key": metric_config["key"],
+        "header": metric_config["header"],
+        "value_type": value_type,
+        "unit": metric_config.get("unit", ""),
+        "raw_value": raw_text,
+        "source_sheet": sheet_name,
+        "source_row": row_number,
+        "source_column": get_column_letter(column_index + 1),
+    }
+    if value_type in {ASSESSMENT_VALUE_TYPE_NUMBER, ASSESSMENT_VALUE_TYPE_RATING}:
+        decimal_value = _decimal_or_none(raw_value)
+        if decimal_value is None:
+            snapshot["error"] = f"{metric_config['header']} is not numeric."
+        else:
+            snapshot["numeric_value"] = str(decimal_value)
+    else:
+        snapshot["text_value"] = raw_text
+    return snapshot
+
+
+def parse_assessment_workbook(
+    content: bytes, import_template: AssessmentImportTemplate
+) -> dict:
+    """Parse configured workbook sheets into sanitized row/value snapshots."""
+    workbook = _load_workbook_from_bytes(content)
+    config = import_template.config
+    parsed_rows: dict[str, dict] = {}
+    workbook_errors = []
+    for sheet_config in config.get("sheets", []):
+        worksheet = _worksheet_by_name(workbook, sheet_config["name"])
+        if worksheet is None:
+            if sheet_config.get("required", True):
+                workbook_errors.append(f"Missing worksheet: {sheet_config['name']}.")
+            continue
+        rows = list(worksheet.iter_rows(values_only=True))
+        header_index = int(sheet_config.get("header_row", 1)) - 1
+        if header_index >= len(rows):
+            workbook_errors.append(
+                f"Missing header row for worksheet: {worksheet.title}."
+            )
+            continue
+        headers = _header_map(_row_values(rows[header_index]))
+        identity_key = normalize_header(sheet_config.get("identity_column", "Name"))
+        identity_index = headers.get(identity_key)
+        if identity_index is None:
+            workbook_errors.append(
+                f"Missing identity column in worksheet: {worksheet.title}."
+            )
+            continue
+        metric_indexes = []
+        for metric_config in sheet_config.get("metrics", []):
+            metric_index = headers.get(normalize_header(metric_config["header"]))
+            if metric_index is not None:
+                metric_indexes.append((metric_config, metric_index))
+        for zero_based_index, row in enumerate(
+            rows[header_index + 1 :], start=header_index + 2
+        ):
+            row_values = _row_values(row)
+            raw_name = (
+                row_values[identity_index] if identity_index < len(row_values) else ""
+            )
+            if raw_name in (None, ""):
+                continue
+            row_key = (
+                slugify(normalize_assessment_name(raw_name))
+                or f"row-{zero_based_index}"
+            )
+            parsed_row = parsed_rows.setdefault(
+                row_key,
+                {
+                    "row_key": row_key,
+                    "raw_identity": str(raw_name).strip(),
+                    "source_rows": [],
+                    "values": [],
+                    "errors": [],
+                },
+            )
+            parsed_row["source_rows"].append(
+                {"sheet": worksheet.title, "row": zero_based_index}
+            )
+            raw_row = {}
+            for metric_config, metric_index in metric_indexes:
+                value = (
+                    row_values[metric_index] if metric_index < len(row_values) else None
+                )
+                raw_row[metric_config["header"]] = "" if value is None else str(value)
+                snapshot = _snapshot_value(
+                    metric_config,
+                    value,
+                    sheet_name=worksheet.title,
+                    row_number=zero_based_index,
+                    column_index=metric_index,
+                )
+                if snapshot is None:
+                    continue
+                if snapshot.get("error"):
+                    parsed_row["errors"].append(snapshot["error"])
+                parsed_row["values"].append(snapshot)
+            parsed_row.setdefault("raw_rows", []).append(
+                {"sheet": worksheet.title, "row": zero_based_index, "values": raw_row}
+            )
+    return {
+        "rows": list(parsed_rows.values()),
+        "errors": workbook_errors,
+        "ranking_sheets": config.get("ranking_sheets", []),
+    }
+
+
+def _preview_summary(batch: AssessmentImportBatch) -> AssessmentPreviewSummary:
+    rows = list(batch.rows.all())
+    return AssessmentPreviewSummary(
+        rows=len(rows),
+        matched=sum(1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_MATCHED),
+        unmatched=sum(
+            1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_UNMATCHED
+        ),
+        ambiguous=sum(
+            1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_AMBIGUOUS
+        ),
+        invalid=sum(1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_INVALID),
+        skipped=sum(1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_SKIPPED),
+        checksum_seen_before=bool(batch.preview_snapshot.get("checksum_seen_before")),
+    )
+
+
+def summarize_import_batch(batch: AssessmentImportBatch) -> AssessmentPreviewSummary:
+    """Return a read model summary for an assessment import batch."""
+    return _preview_summary(batch)
+
+
+@transaction.atomic
+def create_assessment_import_batch(
+    *, file_obj, event, import_template, uploaded_by
+) -> AssessmentImportBatch:
+    """Create a persisted preview batch without committing assessment values."""
+    filename = Path(file_obj.name).name
+    if not filename.lower().endswith(".xlsx"):
+        raise ValidationError("Upload an .xlsx workbook.")
+    content = _workbook_bytes(file_obj)
+    checksum = workbook_sha256(content)
+    checksum_seen_before = AssessmentImportBatch.objects.filter(
+        event=event,
+        workbook_sha256=checksum,
+        status=ASSESSMENT_IMPORT_STATUS_COMMITTED,
+    ).exists()
+    batch = AssessmentImportBatch.objects.create(
+        event=event,
+        import_template=import_template,
+        uploaded_by=uploaded_by,
+        original_filename=filename,
+        workbook_sha256=checksum,
+        config_snapshot=json.loads(json.dumps(import_template.config)),
+        preview_snapshot={"checksum_seen_before": checksum_seen_before},
+    )
+    try:
+        parsed = parse_assessment_workbook(content, import_template)
+        build_assessment_import_preview(batch=batch, parsed=parsed)
+    except Exception as exc:
+        batch.status = ASSESSMENT_IMPORT_STATUS_FAILED
+        batch.import_summary = {"errors": [str(exc)]}
+        batch.save(update_fields=["status", "import_summary", "updated_at"])
+        raise
+    return batch
+
+
+def _row_status_for_match(match, row_errors: list[str]) -> str:
+    if row_errors:
+        return ASSESSMENT_IMPORT_ROW_INVALID
+    if match.status == MATCH_AMBIGUOUS:
+        return ASSESSMENT_IMPORT_ROW_AMBIGUOUS
+    if match.status == MATCH_UNMATCHED:
+        return ASSESSMENT_IMPORT_ROW_UNMATCHED
+    if match.player:
+        return ASSESSMENT_IMPORT_ROW_MATCHED
+    return ASSESSMENT_IMPORT_ROW_UNMATCHED
+
+
+@transaction.atomic
+def build_assessment_import_preview(
+    *, batch: AssessmentImportBatch, parsed: dict
+) -> AssessmentPreviewSummary:
+    """Refresh import preview rows and conservative player matches."""
+    if batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
+        raise ValidationError("Committed assessment imports cannot be previewed again.")
+    batch.rows.all().delete()
+    workbook_errors = parsed.get("errors", [])
+    for parsed_row in parsed.get("rows", []):
+        match = match_player_for_assessment(
+            raw_name=parsed_row["raw_identity"],
+            event=batch.event,
+        )
+        errors = list(parsed_row.get("errors", []))
+        if workbook_errors:
+            errors.extend(workbook_errors)
+        status = _row_status_for_match(match, errors)
+        action = "skip"
+        if status == ASSESSMENT_IMPORT_ROW_MATCHED:
+            action = "create_or_update"
+        elif status in {
+            ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
+            ASSESSMENT_IMPORT_ROW_UNMATCHED,
+        }:
+            action = "needs_review"
+        AssessmentImportRow.objects.create(
+            batch=batch,
+            row_key=parsed_row["row_key"],
+            source_sheet=(parsed_row.get("source_rows") or [{}])[0].get("sheet", ""),
+            source_row=(parsed_row.get("source_rows") or [{}])[0].get("row", 0) or 0,
+            raw_identity=parsed_row["raw_identity"],
+            player=match.player,
+            roster_membership=match.roster_membership,
+            action=action,
+            status=status,
+            errors=errors,
+            values_snapshot=parsed_row.get("values", []),
+            raw_row={
+                "source_rows": parsed_row.get("source_rows", []),
+                "raw_rows": parsed_row.get("raw_rows", []),
+            },
+            metadata={
+                "match_reason": match.reason,
+                "candidate_ids": [candidate.pk for candidate in match.candidates],
+            },
+        )
+    batch.status = ASSESSMENT_IMPORT_STATUS_PREVIEWED
+    summary = _preview_summary(batch)
+    batch.preview_snapshot = {
+        "checksum_seen_before": batch.preview_snapshot.get(
+            "checksum_seen_before", False
+        ),
+        "ranking_sheets": parsed.get("ranking_sheets", []),
+        "summary": summary.__dict__,
+    }
+    batch.import_summary = summary.__dict__
+    batch.save(
+        update_fields=["status", "preview_snapshot", "import_summary", "updated_at"]
+    )
+    return summary
+
+
+@transaction.atomic
+def resolve_assessment_import_row(
+    *, row: AssessmentImportRow, player: Player | None, skip: bool = False
+):
+    """Resolve an unmatched/ambiguous preview row before commit."""
+    if row.batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
+        raise ValidationError("Committed assessment import rows cannot be changed.")
+    if skip:
+        row.player = None
+        row.roster_membership = None
+        row.status = ASSESSMENT_IMPORT_ROW_SKIPPED
+        row.action = "skip"
+    elif player is None:
+        raise ValidationError("Choose a player or skip the row.")
+    else:
+        row.player = player
+        row.roster_membership = (
+            player.roster_memberships.select_related("season_team")
+            .filter(season_team__season=row.batch.event.season, is_active=True)
+            .order_by("-is_primary", "id")
+            .first()
+        )
+        row.status = ASSESSMENT_IMPORT_ROW_MATCHED
+        row.action = "create_or_update"
+    row.save(
+        update_fields=["player", "roster_membership", "status", "action", "updated_at"]
+    )
+    summary = _preview_summary(row.batch)
+    row.batch.import_summary = summary.__dict__
+    row.batch.save(update_fields=["import_summary", "updated_at"])
+    return row
+
+
+def _metric_by_key(event) -> dict[str, AssessmentTemplateMetric]:
+    return {
+        template_metric.metric.key: template_metric
+        for template_metric in event.template.template_metrics.select_related("metric")
+    }
+
+
+def _apply_snapshot_value(
+    *,
+    player_assessment: PlayerAssessment,
+    template_metric: AssessmentTemplateMetric,
+    import_row: AssessmentImportRow,
+    snapshot: dict,
+):
+    existing = AssessmentValue.objects.filter(
+        player_assessment=player_assessment,
+        template_metric=template_metric,
+    ).first()
+    if existing and existing.is_manual_override:
+        raise ValidationError(
+            f"Manual override exists for {player_assessment.player} / {template_metric.display_name}."
+        )
+    defaults = {
+        "raw_value": snapshot.get("raw_value", ""),
+        "normalized_value": snapshot.get("numeric_value")
+        or snapshot.get("text_value", ""),
+        "unit": snapshot.get("unit", ""),
+        "source_sheet": snapshot.get("source_sheet", ""),
+        "source_row": snapshot.get("source_row"),
+        "source_column": snapshot.get("source_column", ""),
+        "source_header": snapshot.get("header", ""),
+        "source_kind": ASSESSMENT_VALUE_SOURCE_IMPORTED,
+        "is_imported": True,
+        "import_row": import_row,
+    }
+    value_type = snapshot.get("value_type")
+    if value_type == ASSESSMENT_VALUE_TYPE_RATING:
+        defaults["rating_value"] = Decimal(snapshot["numeric_value"])
+        defaults["rating_scale_min"] = template_metric.rating_scale_min
+        defaults["rating_scale_max"] = template_metric.rating_scale_max
+    elif value_type == ASSESSMENT_VALUE_TYPE_NUMBER:
+        defaults["numeric_value"] = Decimal(snapshot["numeric_value"])
+    else:
+        defaults["text_value"] = snapshot.get(
+            "text_value", snapshot.get("raw_value", "")
+        )
+    AssessmentValue.objects.update_or_create(
+        player_assessment=player_assessment,
+        template_metric=template_metric,
+        defaults=defaults,
+    )
+
+
+@transaction.atomic
+def commit_assessment_import_batch(
+    *, batch: AssessmentImportBatch, actor
+) -> AssessmentCommitResult:
+    """Commit a fully resolved preview batch into PlayerAssessment records."""
+    if not actor.is_staff and not actor.is_superuser:
+        raise PermissionDenied("Only staff can commit assessment imports.")
+    batch = AssessmentImportBatch.objects.select_for_update().get(pk=batch.pk)
+    if batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
+        raise ValidationError("This assessment import has already been committed.")
+    unresolved = batch.rows.exclude(
+        status__in=[ASSESSMENT_IMPORT_ROW_MATCHED, ASSESSMENT_IMPORT_ROW_SKIPPED]
+    )
+    if unresolved.exists():
+        raise ValidationError(
+            "Resolve or skip all unmatched, ambiguous, or invalid rows before committing."
+        )
+    metrics = _metric_by_key(batch.event)
+    created = 0
+    updated = 0
+    skipped = 0
+    for row in batch.rows.select_related("player", "roster_membership"):
+        if row.status == ASSESSMENT_IMPORT_ROW_SKIPPED:
+            skipped += 1
+            continue
+        if not row.player_id:
+            raise ValidationError("Resolved assessment import rows require a player.")
+        player_assessment, was_created = PlayerAssessment.objects.get_or_create(
+            player=row.player,
+            event=batch.event,
+            defaults={
+                "roster_membership": row.roster_membership,
+                "import_batch": batch,
+                "source_row_key": row.row_key,
+                "status": ASSESSMENT_STATUS_COMMITTED,
+            },
+        )
+        if was_created:
+            created += 1
+        else:
+            updated += 1
+            player_assessment.roster_membership = (
+                row.roster_membership or player_assessment.roster_membership
+            )
+            player_assessment.import_batch = batch
+            player_assessment.source_row_key = row.row_key
+            player_assessment.status = ASSESSMENT_STATUS_COMMITTED
+            player_assessment.save()
+        for snapshot in row.values_snapshot:
+            template_metric = metrics.get(snapshot.get("metric_key"))
+            if template_metric is None:
+                raise ValidationError(
+                    f"Unknown assessment metric: {snapshot.get('metric_key')}."
+                )
+            _apply_snapshot_value(
+                player_assessment=player_assessment,
+                template_metric=template_metric,
+                import_row=row,
+                snapshot=snapshot,
+            )
+        row.status = ASSESSMENT_IMPORT_ROW_COMMITTED
+        row.save(update_fields=["status", "updated_at"])
+    batch.status = ASSESSMENT_IMPORT_STATUS_COMMITTED
+    batch.committed_at = timezone.now()
+    result = AssessmentCommitResult(
+        processed=created + updated + skipped,
+        created=created,
+        updated=updated,
+        skipped=skipped,
+    )
+    batch.import_summary = result.__dict__
+    batch.save(update_fields=["status", "committed_at", "import_summary", "updated_at"])
+    batch.event.template.is_locked = True
+    batch.event.template.save(update_fields=["is_locked", "updated_at"])
+    batch.import_template.is_locked = True
+    batch.import_template.save(update_fields=["is_locked", "updated_at"])
+    if batch.event.scoring_profile_id:
+        batch.event.scoring_profile.is_locked = True
+        batch.event.scoring_profile.save(update_fields=["is_locked", "updated_at"])
+    return result
+
+
+def default_2026_13u_config() -> dict:
+    """Return configuration derived from the supplied 2026 13U workbook headers."""
+    return {
+        "sheets": DEFAULT_2026_13U_DATA_SHEETS,
+        "ranking_sheets": DEFAULT_2026_13U_RANKING_SHEETS,
+        "notes": "Ranking sheets are provenance/QA only and are not imported as player metrics.",
+    }
+
+
+@transaction.atomic
+def ensure_2026_13u_assessment_configuration(*, dry_run: bool = False) -> dict:
+    """Create idempotent assessment/import templates for the 2026 13U workbook."""
+    config = default_2026_13u_config()
+    plan = {
+        "metrics": [],
+        "template": BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
+        "import_template": BOOTSTRAP_2026_13U_IMPORT_KEY,
+    }
+    if dry_run:
+        for sheet_config in config["sheets"]:
+            for metric_config in sheet_config["metrics"]:
+                plan["metrics"].append(metric_config["key"])
+        return plan
+    template, _ = AssessmentTemplate.objects.get_or_create(
+        key=BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
+        version=1,
+        defaults={"name": "2026 VCB House 13U PeeWee Assessment"},
+    )
+    AssessmentScoringProfile.objects.get_or_create(
+        key=BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
+        version=1,
+        defaults={
+            "name": "2026 VCB House 13U PeeWee Assessment Scoring",
+            "config": {"source": "spreadsheet-derived", "computed_scores": []},
+        },
+    )
+    AssessmentImportTemplate.objects.get_or_create(
+        key=BOOTSTRAP_2026_13U_IMPORT_KEY,
+        version=1,
+        defaults={
+            "name": "2026 VCB House 13U PeeWee Assessment Workbook",
+            "config": config,
+        },
+    )
+    display_order = 0
+    for sheet_config in config["sheets"]:
+        for metric_config in sheet_config["metrics"]:
+            display_order += 10
+            value_type = metric_config.get("value_type") or ASSESSMENT_VALUE_TYPE_NUMBER
+            metric, _ = AssessmentMetricDefinition.objects.get_or_create(
+                key=metric_config["key"],
+                defaults={
+                    "name": metric_config["header"].strip(),
+                    "default_value_type": value_type,
+                    "default_unit": metric_config.get("unit", ""),
+                },
+            )
+            AssessmentTemplateMetric.objects.get_or_create(
+                template=template,
+                metric=metric,
+                defaults={
+                    "category": metric_config.get("category", sheet_config["name"]),
+                    "display_name": metric_config["header"].strip(),
+                    "display_order": display_order,
+                    "value_type": value_type,
+                    "unit": metric_config.get("unit", ""),
+                    "direction": metric_config.get("direction", "neutral"),
+                    "rating_scale_min": (
+                        Decimal("1")
+                        if value_type == ASSESSMENT_VALUE_TYPE_RATING
+                        else None
+                    ),
+                    "rating_scale_max": (
+                        Decimal("5")
+                        if value_type == ASSESSMENT_VALUE_TYPE_RATING
+                        else None
+                    ),
+                    "metadata": {"source_sheet": sheet_config["name"]},
+                },
+            )
+            plan["metrics"].append(metric_config["key"])
+    return plan
+
+
+def assessment_records_for_player(player: Player):
+    """Return staff-visible workbook assessment records for a player profile."""
+    return (
+        PlayerAssessment.objects.filter(player=player)
+        .select_related("event", "event__season")
+        .prefetch_related("values__template_metric")
+        .order_by("-event__starts_on", "-created_at")
+    )
diff --git a/analytics/services/assessment_matching_service.py b/analytics/services/assessment_matching_service.py
new file mode 100644
index 0000000..dc43875
--- /dev/null
+++ b/analytics/services/assessment_matching_service.py
@@ -0,0 +1,121 @@
+from __future__ import annotations
+
+from dataclasses import dataclass
+
+from players.models import Player, PlayerAlias, PlayerSourceIdentifier
+from players.models import normalize_lookup_value as normalize_player_lookup_value
+from seasons.models import PlayerRosterMembership
+
+MATCH_EXACT_IDENTIFIER = "exact_identifier"
+MATCH_EXACT_NAME = "exact_name"
+MATCH_ALIAS = "alias"
+MATCH_UNMATCHED = "unmatched"
+MATCH_AMBIGUOUS = "ambiguous"
+
+
+@dataclass(frozen=True)
+class AssessmentMatchResult:
+    status: str
+    player: Player | None = None
+    roster_membership: PlayerRosterMembership | None = None
+    candidates: tuple[Player, ...] = ()
+    reason: str = ""
+
+    @property
+    def is_committable(self) -> bool:
+        return self.player is not None and self.status != MATCH_AMBIGUOUS
+
+
+def normalize_assessment_name(value: str) -> str:
+    """Normalize workbook player names for exact and alias matching."""
+    return normalize_player_lookup_value(
+        str(value or "").replace("“", '"').replace("”", '"').replace("’", "'")
+    )
+
+
+def _primary_roster_membership(player: Player, event) -> PlayerRosterMembership | None:
+    return (
+        player.roster_memberships.select_related("season_team", "season_team__season")
+        .filter(season_team__season=event.season, is_active=True)
+        .order_by("-is_primary", "season_team__name", "id")
+        .first()
+    )
+
+
+def _result_for_players(
+    players: list[Player], *, event, status: str, reason: str
+) -> AssessmentMatchResult:
+    unique_players = list({player.pk: player for player in players}.values())
+    if len(unique_players) == 1:
+        player = unique_players[0]
+        return AssessmentMatchResult(
+            status=status,
+            player=player,
+            roster_membership=_primary_roster_membership(player, event),
+            candidates=(player,),
+            reason=reason,
+        )
+    if len(unique_players) > 1:
+        return AssessmentMatchResult(
+            status=MATCH_AMBIGUOUS,
+            candidates=tuple(unique_players),
+            reason="Multiple players matched the workbook identity.",
+        )
+    return AssessmentMatchResult(status=MATCH_UNMATCHED, reason=reason)
+
+
+def match_player_for_assessment(
+    *,
+    raw_name: str,
+    event,
+    source_identifiers: dict[str, str] | None = None,
+) -> AssessmentMatchResult:
+    """Match a workbook row to an existing canonical player without fuzzy commits."""
+    source_identifiers = source_identifiers or {}
+    identifier_players = []
+    for identifier_type, identifier_value in source_identifiers.items():
+        if not identifier_value:
+            continue
+        identifiers = PlayerSourceIdentifier.objects.select_related("player").filter(
+            identifier_type=normalize_player_lookup_value(identifier_type),
+            identifier_value=normalize_player_lookup_value(identifier_value),
+        )
+        identifier_players.extend(identifier.player for identifier in identifiers)
+    if identifier_players:
+        return _result_for_players(
+            identifier_players,
+            event=event,
+            status=MATCH_EXACT_IDENTIFIER,
+            reason="Matched by source identifier.",
+        )
+
+    normalized_name = normalize_assessment_name(raw_name)
+    if not normalized_name:
+        return AssessmentMatchResult(
+            status=MATCH_UNMATCHED, reason="Missing player name."
+        )
+
+    name_players = [
+        player
+        for player in Player.objects.filter(is_active=True)
+        if normalize_assessment_name(player.display_name) == normalized_name
+        or normalize_assessment_name(player.full_name) == normalized_name
+    ]
+    if name_players:
+        return _result_for_players(
+            name_players,
+            event=event,
+            status=MATCH_EXACT_NAME,
+            reason="Matched by exact player name.",
+        )
+
+    aliases = PlayerAlias.objects.select_related("player").filter(
+        normalized_alias=normalized_name,
+        player__is_active=True,
+    )
+    return _result_for_players(
+        [alias.player for alias in aliases],
+        event=event,
+        status=MATCH_ALIAS,
+        reason="Matched by player alias." if aliases else "No exact player match.",
+    )
diff --git a/analytics/services/reporting_service.py b/analytics/services/reporting_service.py
index 43a7c4f..6350299 100644
--- a/analytics/services/reporting_service.py
+++ b/analytics/services/reporting_service.py
@@ -6,6 +6,7 @@ from django.utils import timezone
 
 from analytics.models import EvaluationCycle, Observation
 from analytics.services import metrics_service
+from analytics.services.assessment_feature import assessments_enabled
 from analytics.services.metrics_service import (
     CompletionMetrics,
     DraftMatchingMetrics,
@@ -79,7 +80,7 @@ def _recent_observation_rows(observations: list[Observation]) -> list[RecentObse
 
 
 def _navigation_links() -> list[NavigationLink]:
-    return [
+    links = [
         NavigationLink("Player Search", reverse("analytics:player-search"), "Find players and open profiles."),
         NavigationLink("Compare Players", reverse("analytics:player-compare"), "Compare submitted assessment summaries."),
         NavigationLink("Import Players", reverse("analytics:import-list"), "Review player import batches."),
@@ -87,6 +88,22 @@ def _navigation_links() -> list[NavigationLink]:
         NavigationLink("Observation Review", reverse("analytics:observation-review-list"), "Review submitted and draft observations."),
         NavigationLink("Account Operations", reverse("accounts:operations-dashboard"), "Review account status and player links."),
     ]
+    if assessments_enabled():
+        links.extend(
+            [
+                NavigationLink(
+                    "Assessment Events",
+                    reverse("analytics:assessment-event-list"),
+                    "Review workbook-based assessment events.",
+                ),
+                NavigationLink(
+                    "Import Assessment Workbook",
+                    reverse("analytics:assessment-import-list"),
+                    "Import versioned assessment workbooks.",
+                ),
+            ]
+        )
+    return links
 
 
 def _summary_cards(
diff --git a/analytics/templates/analytics/assessment_event_detail.html b/analytics/templates/analytics/assessment_event_detail.html
new file mode 100644
index 0000000..434ab81
--- /dev/null
+++ b/analytics/templates/analytics/assessment_event_detail.html
@@ -0,0 +1,42 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}{{ assessment_event.name }}{% endblock %}
+{% block analytics_subtitle %}{{ assessment_event.season }}{% if assessment_event.division %} · {{ assessment_event.division }}{% endif %}{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Assessment Event</h2>
+    <p>
+        <a class="button button--ghost" href="{% url 'analytics:assessment-event-list' %}">Back to Events</a>
+        <a class="button button--primary" href="{% url 'analytics:assessment-import-new' %}">Import Workbook</a>
+    </p>
+    <dl class="pdp-detail-list">
+        <dt>Template</dt><dd>{{ assessment_event.template }}</dd>
+        <dt>Scoring profile</dt><dd>{{ assessment_event.scoring_profile|default:"-" }}</dd>
+        <dt>Status</dt><dd>{% if assessment_event.is_active %}Active{% else %}Inactive{% endif %}</dd>
+    </dl>
+</article>
+
+<article class="pdp-card">
+    <h2>Player Assessments</h2>
+    {% if player_assessments %}
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
+                <thead><tr><th>Player</th><th>Team</th><th>Values</th><th>Action</th></tr></thead>
+                <tbody>
+                    {% for assessment in player_assessments %}
+                        <tr>
+                            <td data-label="Player">{{ assessment.player.display_name }}</td>
+                            <td data-label="Team">{% if assessment.roster_membership %}{{ assessment.roster_membership.season_team.name }}{% else %}-{% endif %}</td>
+                            <td data-label="Values">{{ assessment.values.count }}</td>
+                            <td data-label="Action"><a class="button button--ghost" href="{% url 'analytics:player-assessment-detail' pk=assessment.pk %}">Review</a></td>
+                        </tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    {% else %}
+        <p>No player assessment records have been committed for this event.</p>
+    {% endif %}
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/assessment_event_list.html b/analytics/templates/analytics/assessment_event_list.html
new file mode 100644
index 0000000..4f5cbe8
--- /dev/null
+++ b/analytics/templates/analytics/assessment_event_list.html
@@ -0,0 +1,36 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}Assessment Events{% endblock %}
+{% block analytics_subtitle %}Staff-only workbook assessment events and imports.{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Assessment Events</h2>
+    <p>
+        <a class="button button--primary" href="{% url 'analytics:assessment-import-new' %}">Import Workbook</a>
+        <a class="button button--ghost" href="{% url 'analytics:assessment-import-list' %}">Import History</a>
+    </p>
+    {% if assessment_events %}
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
+                <thead>
+                    <tr><th>Event</th><th>Season</th><th>Division</th><th>Template</th><th>Action</th></tr>
+                </thead>
+                <tbody>
+                    {% for event in assessment_events %}
+                        <tr>
+                            <td data-label="Event">{{ event.name }}</td>
+                            <td data-label="Season">{{ event.season }}</td>
+                            <td data-label="Division">{{ event.division|default:"-" }}</td>
+                            <td data-label="Template">{{ event.template }}</td>
+                            <td data-label="Action"><a class="button button--ghost" href="{% url 'analytics:assessment-event-detail' event_id=event.pk %}">Open</a></td>
+                        </tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    {% else %}
+        <p>No assessment events have been configured.</p>
+    {% endif %}
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/assessment_import_detail.html b/analytics/templates/analytics/assessment_import_detail.html
new file mode 100644
index 0000000..3fccf5d
--- /dev/null
+++ b/analytics/templates/analytics/assessment_import_detail.html
@@ -0,0 +1,20 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}Assessment Import Detail{% endblock %}
+{% block analytics_subtitle %}{{ import_batch.original_filename }} · {{ import_batch.get_status_display }}{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Import Detail</h2>
+    <p><a class="button button--ghost" href="{% url 'analytics:assessment-import-list' %}">Back to Imports</a></p>
+    <dl class="pdp-detail-list">
+        <dt>Event</dt><dd>{{ import_batch.event.name }}</dd>
+        <dt>Status</dt><dd>{{ import_batch.get_status_display }}</dd>
+        <dt>Uploaded by</dt><dd>{{ import_batch.uploaded_by|default:"-" }}</dd>
+        <dt>Uploaded</dt><dd>{{ import_batch.created_at }}</dd>
+        <dt>Committed</dt><dd>{{ import_batch.committed_at|default:"-" }}</dd>
+        <dt>Workbook checksum</dt><dd>{{ import_batch.workbook_sha256 }}</dd>
+    </dl>
+    <p>{{ summary.rows }} rows · {{ summary.matched }} matched · {{ summary.unmatched }} unmatched · {{ summary.ambiguous }} ambiguous · {{ summary.invalid }} invalid · {{ summary.skipped }} skipped</p>
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/assessment_import_list.html b/analytics/templates/analytics/assessment_import_list.html
new file mode 100644
index 0000000..a018db6
--- /dev/null
+++ b/analytics/templates/analytics/assessment_import_list.html
@@ -0,0 +1,31 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}Assessment Imports{% endblock %}
+{% block analytics_subtitle %}Staff-only workbook import history.{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Assessment Imports</h2>
+    <p><a class="button button--primary" href="{% url 'analytics:assessment-import-new' %}">Import Workbook</a></p>
+    {% if import_batches %}
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
+                <thead><tr><th>File</th><th>Event</th><th>Status</th><th>Uploaded</th><th>Action</th></tr></thead>
+                <tbody>
+                    {% for batch in import_batches %}
+                        <tr>
+                            <td data-label="File">{{ batch.original_filename }}</td>
+                            <td data-label="Event">{{ batch.event.name }}</td>
+                            <td data-label="Status">{{ batch.get_status_display }}</td>
+                            <td data-label="Uploaded">{{ batch.created_at }}</td>
+                            <td data-label="Action"><a class="button button--ghost" href="{% url 'analytics:assessment-import-detail' pk=batch.pk %}">Open</a></td>
+                        </tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    {% else %}
+        <p>No assessment workbook imports yet.</p>
+    {% endif %}
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/assessment_import_preview.html b/analytics/templates/analytics/assessment_import_preview.html
new file mode 100644
index 0000000..f377ff4
--- /dev/null
+++ b/analytics/templates/analytics/assessment_import_preview.html
@@ -0,0 +1,49 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}Assessment Import Preview{% endblock %}
+{% block analytics_subtitle %}{{ import_batch.original_filename }} · {{ import_batch.event.name }}{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Preview Summary</h2>
+    {% if summary.checksum_seen_before %}
+        <p class="form-error">This workbook checksum has already been committed for this event. Review carefully before continuing.</p>
+    {% endif %}
+    <p>{{ summary.rows }} rows · {{ summary.matched }} matched · {{ summary.unmatched }} unmatched · {{ summary.ambiguous }} ambiguous · {{ summary.invalid }} invalid · {{ summary.skipped }} skipped</p>
+    <p>
+        <a class="button button--ghost" href="{% url 'analytics:assessment-import-list' %}">Back to Imports</a>
+        {% if not summary.can_commit %}
+            <a class="button button--primary" href="{% url 'analytics:assessment-import-resolve' pk=import_batch.pk %}">Resolve Rows</a>
+        {% endif %}
+    </p>
+    <form method="post" action="{% url 'analytics:assessment-import-confirm' pk=import_batch.pk %}">
+        {% csrf_token %}
+        <button class="button button--primary" type="submit" {% if not summary.can_commit %}disabled{% endif %}>Confirm Import</button>
+    </form>
+</article>
+
+<article class="pdp-card">
+    <h2>Rows</h2>
+    {% if rows %}
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
+                <thead><tr><th>Row</th><th>Workbook Name</th><th>Matched Player</th><th>Status</th><th>Values</th><th>Issues</th></tr></thead>
+                <tbody>
+                    {% for row in rows %}
+                        <tr>
+                            <td data-label="Row">{{ row.source_sheet }} {{ row.source_row }}</td>
+                            <td data-label="Workbook Name">{{ row.raw_identity }}</td>
+                            <td data-label="Matched Player">{% if row.player %}{{ row.player.display_name }}{% else %}-{% endif %}</td>
+                            <td data-label="Status">{{ row.get_status_display }}</td>
+                            <td data-label="Values">{{ row.values_snapshot|length }}</td>
+                            <td data-label="Issues">{% for error in row.errors %}{{ error }}{% if not forloop.last %}; {% endif %}{% empty %}-{% endfor %}</td>
+                        </tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    {% else %}
+        <p>No rows were parsed from this workbook.</p>
+    {% endif %}
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/assessment_import_resolve.html b/analytics/templates/analytics/assessment_import_resolve.html
new file mode 100644
index 0000000..5774180
--- /dev/null
+++ b/analytics/templates/analytics/assessment_import_resolve.html
@@ -0,0 +1,41 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}Resolve Assessment Import Rows{% endblock %}
+{% block analytics_subtitle %}{{ import_batch.original_filename }}{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Rows Needing Review</h2>
+    {% if forms %}
+        <form method="post">
+            {% csrf_token %}
+            <div class="table-wrap table-wrap--cards">
+                <table class="pdp-table" data-responsive="cards">
+                    <thead><tr><th>Workbook Name</th><th>Status</th><th>Player</th><th>Skip</th></tr></thead>
+                    <tbody>
+                        {% for row, form in forms %}
+                            <tr>
+                                <td data-label="Workbook Name">{{ row.raw_identity }}</td>
+                                <td data-label="Status">{{ row.get_status_display }}</td>
+                                <td data-label="Player">
+                                    <select name="row_{{ row.pk }}_player">
+                                        <option value="">---------</option>
+                                        {% for player in form.fields.player.queryset %}
+                                            <option value="{{ player.pk }}">{{ player.display_name }}</option>
+                                        {% endfor %}
+                                    </select>
+                                </td>
+                                <td data-label="Skip"><input type="checkbox" name="row_{{ row.pk }}_skip" value="1"></td>
+                            </tr>
+                        {% endfor %}
+                    </tbody>
+                </table>
+            </div>
+            <button class="button button--primary" type="submit">Save Resolutions</button>
+        </form>
+    {% else %}
+        <p>No rows require review.</p>
+        <p><a class="button button--primary" href="{% url 'analytics:assessment-import-preview' pk=import_batch.pk %}">Back to Preview</a></p>
+    {% endif %}
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/assessment_import_upload.html b/analytics/templates/analytics/assessment_import_upload.html
new file mode 100644
index 0000000..ddf5de6
--- /dev/null
+++ b/analytics/templates/analytics/assessment_import_upload.html
@@ -0,0 +1,15 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}Import Assessment Workbook{% endblock %}
+{% block analytics_subtitle %}Preview workbook rows before committing assessment values.{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Upload Workbook</h2>
+    <form method="post" enctype="multipart/form-data">
+        {% csrf_token %}
+        {{ form.as_p }}
+        <button class="button button--primary" type="submit">Preview Import</button>
+    </form>
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/player_assessment_detail.html b/analytics/templates/analytics/player_assessment_detail.html
new file mode 100644
index 0000000..5ef2d8b
--- /dev/null
+++ b/analytics/templates/analytics/player_assessment_detail.html
@@ -0,0 +1,34 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}{{ player_assessment.player.display_name }}{% endblock %}
+{% block analytics_subtitle %}{{ player_assessment.event.name }}{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Assessment Values</h2>
+    <p>
+        <a class="button button--ghost" href="{% url 'analytics:assessment-event-detail' event_id=player_assessment.event_id %}">Back to Event</a>
+        <a class="button button--ghost" href="{% url 'analytics:player-profile' player_id=player_assessment.player_id %}">Player Profile</a>
+    </p>
+    {% if values %}
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
+                <thead><tr><th>Metric</th><th>Category</th><th>Value</th><th>Unit</th><th>Source</th></tr></thead>
+                <tbody>
+                    {% for value in values %}
+                        <tr>
+                            <td data-label="Metric">{{ value.template_metric.display_name }}</td>
+                            <td data-label="Category">{{ value.template_metric.category|default:"-" }}</td>
+                            <td data-label="Value">{% if value.numeric_value != None %}{{ value.numeric_value }}{% elif value.rating_value != None %}{{ value.rating_value }}{% elif value.text_value %}{{ value.text_value }}{% else %}{{ value.raw_value|default:"-" }}{% endif %}</td>
+                            <td data-label="Unit">{{ value.unit|default:"-" }}</td>
+                            <td data-label="Source">{{ value.source_sheet }} row {{ value.source_row }}</td>
+                        </tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    {% else %}
+        <p>No assessment values are recorded.</p>
+    {% endif %}
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/player_profile.html b/analytics/templates/analytics/player_profile.html
index 4552a05..7e3c715 100644
--- a/analytics/templates/analytics/player_profile.html
+++ b/analytics/templates/analytics/player_profile.html
@@ -104,5 +104,30 @@
     {% endif %}
 </article>
 
+{% if assessments_enabled %}
+<article class="pdp-card">
+    <h2>Assessment Events</h2>
+    {% if assessment_records %}
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
+                <thead><tr><th>Event</th><th>Season</th><th>Values</th><th>Action</th></tr></thead>
+                <tbody>
+                    {% for assessment in assessment_records %}
+                        <tr>
+                            <td data-label="Event">{{ assessment.event.name }}</td>
+                            <td data-label="Season">{{ assessment.event.season }}</td>
+                            <td data-label="Values">{{ assessment.values.count }}</td>
+                            <td data-label="Action"><a class="button button--ghost" href="{% url 'analytics:player-assessment-detail' pk=assessment.pk %}">Review</a></td>
+                        </tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    {% else %}
+        <p>No workbook assessment records have been committed.</p>
+    {% endif %}
+</article>
+{% endif %}
+
 {% include "analytics/_player_timeline.html" with timeline=timeline %}
 {% endblock %}
diff --git a/analytics/tests/test_assessment_imports.py b/analytics/tests/test_assessment_imports.py
new file mode 100644
index 0000000..4331da0
--- /dev/null
+++ b/analytics/tests/test_assessment_imports.py
@@ -0,0 +1,210 @@
+from decimal import Decimal
+from io import BytesIO
+
+from django.core.exceptions import PermissionDenied, ValidationError
+from django.core.files.uploadedfile import SimpleUploadedFile
+from django.test import override_settings
+from django.urls import reverse
+from openpyxl import Workbook
+
+from analytics.models import (
+    ASSESSMENT_IMPORT_ROW_MATCHED,
+    ASSESSMENT_IMPORT_ROW_SKIPPED,
+    ASSESSMENT_IMPORT_ROW_UNMATCHED,
+    ASSESSMENT_IMPORT_STATUS_COMMITTED,
+    ASSESSMENT_STATUS_COMMITTED,
+    AssessmentEvent,
+    AssessmentImportBatch,
+    AssessmentImportTemplate,
+    AssessmentMetricDefinition,
+    AssessmentScoringProfile,
+    AssessmentTemplate,
+    AssessmentTemplateMetric,
+    AssessmentValue,
+    PlayerAssessment,
+)
+from analytics.services.assessment_import_service import (
+    commit_assessment_import_batch,
+    create_assessment_import_batch,
+    ensure_2026_13u_assessment_configuration,
+    resolve_assessment_import_row,
+)
+from analytics.tests.helpers import (
+    Player,
+    TestCase,
+    User,
+    attach_player_to_season,
+    create_season,
+)
+
+
+def assessment_workbook(rows):
+    workbook = Workbook()
+    worksheet = workbook.active
+    worksheet.title = "Assessment Data"
+    worksheet.append(["", "Athleticism Evaluation", ""])
+    worksheet.append(["Name", "Home to 1st", "Broad Jump"])
+    for row in rows:
+        worksheet.append(row)
+    pitching = workbook.create_sheet("Pitching Data ")
+    pitching.append([])
+    pitching.append(["Name", "Velocity Avg.", "Velocity Max"])
+    for row in rows:
+        pitching.append([row[0], 50, 52])
+    buffer = BytesIO()
+    workbook.save(buffer)
+    return buffer.getvalue()
+
+
+class AssessmentImportTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="test", is_staff=True
+        )
+        self.user = User.objects.create_user(username="regular", password="test")
+        self.season = create_season(name="Spring 2026", key="spring-2026")
+        ensure_2026_13u_assessment_configuration()
+        self.template = AssessmentTemplate.objects.get(key="2026-13u-house-assessment")
+        self.import_template = AssessmentImportTemplate.objects.get(
+            key="2026-13u-house-assessment-xlsx"
+        )
+        self.scoring_profile = AssessmentScoringProfile.objects.get(
+            key="2026-13u-house-assessment"
+        )
+        self.event = AssessmentEvent.objects.create(
+            name="Spring 2026 13U Assessment",
+            season=self.season,
+            division="13U House",
+            template=self.template,
+            scoring_profile=self.scoring_profile,
+        )
+        self.player = Player.objects.create(first_name="Alex", last_name="Example")
+        attach_player_to_season(
+            self.player, self.season, team_name="Yankees", division="13U House"
+        )
+
+    def upload(self, rows):
+        return SimpleUploadedFile(
+            "assessment.xlsx",
+            assessment_workbook(rows),
+            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
+        )
+
+    def test_feature_flag_blocks_assessment_routes_when_disabled(self):
+        self.client.force_login(self.staff)
+        with override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False):
+            response = self.client.get(reverse("analytics:assessment-event-list"))
+        self.assertEqual(response.status_code, 404)
+
+    def test_staff_required_for_assessment_routes(self):
+        self.client.force_login(self.user)
+        with override_settings(ANALYTICS_ASSESSMENTS_ENABLED=True):
+            response = self.client.get(reverse("analytics:assessment-event-list"))
+        self.assertEqual(response.status_code, 403)
+
+    def test_valid_workbook_preview_matches_existing_player(self):
+        batch = create_assessment_import_batch(
+            file_obj=self.upload([["Alex Example", 4.1, 82]]),
+            event=self.event,
+            import_template=self.import_template,
+            uploaded_by=self.staff,
+        )
+
+        row = batch.rows.get()
+        self.assertEqual(row.status, ASSESSMENT_IMPORT_ROW_MATCHED)
+        self.assertEqual(row.player, self.player)
+        self.assertEqual(len(row.values_snapshot), 4)
+
+    def test_commit_creates_player_assessment_values(self):
+        batch = create_assessment_import_batch(
+            file_obj=self.upload([["Alex Example", 4.1, 82]]),
+            event=self.event,
+            import_template=self.import_template,
+            uploaded_by=self.staff,
+        )
+
+        result = commit_assessment_import_batch(batch=batch, actor=self.staff)
+
+        self.assertEqual(result.created, 1)
+        batch.refresh_from_db()
+        self.assertEqual(batch.status, ASSESSMENT_IMPORT_STATUS_COMMITTED)
+        assessment = PlayerAssessment.objects.get(player=self.player, event=self.event)
+        self.assertEqual(assessment.status, ASSESSMENT_STATUS_COMMITTED)
+        self.assertEqual(
+            AssessmentValue.objects.filter(player_assessment=assessment).count(), 4
+        )
+
+    def test_commit_blocks_unmatched_rows_until_resolved_or_skipped(self):
+        batch = create_assessment_import_batch(
+            file_obj=self.upload([["Unknown Player", 4.1, 82]]),
+            event=self.event,
+            import_template=self.import_template,
+            uploaded_by=self.staff,
+        )
+        row = batch.rows.get()
+        self.assertEqual(row.status, ASSESSMENT_IMPORT_ROW_UNMATCHED)
+
+        with self.assertRaises(ValidationError):
+            commit_assessment_import_batch(batch=batch, actor=self.staff)
+
+        resolve_assessment_import_row(row=row, player=None, skip=True)
+        row.refresh_from_db()
+        self.assertEqual(row.status, ASSESSMENT_IMPORT_ROW_SKIPPED)
+        result = commit_assessment_import_batch(batch=batch, actor=self.staff)
+        self.assertEqual(result.skipped, 1)
+
+    def test_commit_blocks_manual_override_overwrite(self):
+        batch = create_assessment_import_batch(
+            file_obj=self.upload([["Alex Example", 4.1, 82]]),
+            event=self.event,
+            import_template=self.import_template,
+            uploaded_by=self.staff,
+        )
+        metric = AssessmentMetricDefinition.objects.get(key="home_to_1st")
+        template_metric = AssessmentTemplateMetric.objects.get(
+            template=self.template, metric=metric
+        )
+        assessment = PlayerAssessment.objects.create(
+            player=self.player,
+            event=self.event,
+            status=ASSESSMENT_STATUS_COMMITTED,
+        )
+        AssessmentValue.objects.create(
+            player_assessment=assessment,
+            template_metric=template_metric,
+            numeric_value=Decimal("9.999"),
+            is_manual_override=True,
+        )
+
+        with self.assertRaises(ValidationError):
+            commit_assessment_import_batch(batch=batch, actor=self.staff)
+
+    def test_non_staff_cannot_commit_batch(self):
+        batch = create_assessment_import_batch(
+            file_obj=self.upload([["Alex Example", 4.1, 82]]),
+            event=self.event,
+            import_template=self.import_template,
+            uploaded_by=self.staff,
+        )
+        with self.assertRaises(PermissionDenied):
+            commit_assessment_import_batch(batch=batch, actor=self.user)
+
+    def test_bootstrap_command_is_idempotent(self):
+        first_count = AssessmentMetricDefinition.objects.count()
+        ensure_2026_13u_assessment_configuration()
+        self.assertEqual(AssessmentMetricDefinition.objects.count(), first_count)
+
+    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=True)
+    def test_upload_view_creates_preview_batch(self):
+        self.client.force_login(self.staff)
+        response = self.client.post(
+            reverse("analytics:assessment-import-new"),
+            {
+                "event": self.event.pk,
+                "import_template": self.import_template.pk,
+                "workbook": self.upload([["Alex Example", 4.1, 82]]),
+            },
+        )
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(AssessmentImportBatch.objects.count(), 1)
diff --git a/analytics/urls.py b/analytics/urls.py
index 2e9ebc7..fe85b37 100644
--- a/analytics/urls.py
+++ b/analytics/urls.py
@@ -2,6 +2,14 @@ from django.urls import path
 
 from analytics.views import (
     AnalyticsCommandCenterView,
+    AssessmentEventDetailView,
+    AssessmentEventListView,
+    AssessmentImportConfirmView,
+    AssessmentImportDetailView,
+    AssessmentImportListView,
+    AssessmentImportPreviewView,
+    AssessmentImportResolveView,
+    AssessmentImportUploadView,
     CoachAssessmentDetailView,
     CoachAssessmentEditView,
     CoachAssessmentListView,
@@ -20,6 +28,7 @@ from analytics.views import (
     PlayerImportListView,
     PlayerImportPreviewView,
     PlayerImportUploadView,
+    PlayerAssessmentDetailView,
     PlayerSearchView,
     StaffObservationReviewDetailView,
     StaffObservationReviewListView,
@@ -33,6 +42,15 @@ urlpatterns = [
     path("players/", PlayerSearchView.as_view(), name="player-search"),
     path("players/compare/", PlayerComparisonView.as_view(), name="player-compare"),
     path("players/<int:player_id>/", PlayerProfileView.as_view(), name="player-profile"),
+    path("assessment-events/", AssessmentEventListView.as_view(), name="assessment-event-list"),
+    path("assessment-events/<int:event_id>/", AssessmentEventDetailView.as_view(), name="assessment-event-detail"),
+    path("player-assessments/<int:pk>/", PlayerAssessmentDetailView.as_view(), name="player-assessment-detail"),
+    path("assessment-imports/", AssessmentImportListView.as_view(), name="assessment-import-list"),
+    path("assessment-imports/new/", AssessmentImportUploadView.as_view(), name="assessment-import-new"),
+    path("assessment-imports/<int:pk>/preview/", AssessmentImportPreviewView.as_view(), name="assessment-import-preview"),
+    path("assessment-imports/<int:pk>/resolve/", AssessmentImportResolveView.as_view(), name="assessment-import-resolve"),
+    path("assessment-imports/<int:pk>/confirm/", AssessmentImportConfirmView.as_view(), name="assessment-import-confirm"),
+    path("assessment-imports/<int:pk>/", AssessmentImportDetailView.as_view(), name="assessment-import-detail"),
     path("evaluations/", EvaluationListView.as_view(), name="evaluation-list"),
     path("evaluations/players/<int:player_id>/", EvaluationPlayerView.as_view(), name="evaluation-player"),
     path("evaluation-review/", EvaluationReviewListView.as_view(), name="evaluation-review-list"),
diff --git a/analytics/views.py b/analytics/views.py
index 53f4621..b0d14df 100644
--- a/analytics/views.py
+++ b/analytics/views.py
@@ -8,8 +8,34 @@ from django.urls import reverse
 from django.views.generic import FormView, ListView, TemplateView, View
 
 from analytics.assessment_forms import CoachAssessmentForm
-from analytics.forms import PlayerImportMappingForm, PlayerImportUploadForm, parse_conflict_resolutions
-from analytics.models import EVALUATION_PERSPECTIVE_CHOICES, OBSERVATION_STATUS_SUBMITTED, OBSERVATION_TYPE_COACH_ASSESSMENT, EvaluationCycle, Observation
+from analytics.forms import (
+    AssessmentImportRowResolutionForm,
+    AssessmentImportUploadForm,
+    PlayerImportMappingForm,
+    PlayerImportUploadForm,
+    parse_conflict_resolutions,
+)
+from analytics.models import (
+    ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
+    ASSESSMENT_IMPORT_ROW_INVALID,
+    ASSESSMENT_IMPORT_ROW_UNMATCHED,
+    EVALUATION_PERSPECTIVE_CHOICES,
+    OBSERVATION_STATUS_SUBMITTED,
+    OBSERVATION_TYPE_COACH_ASSESSMENT,
+    AssessmentEvent,
+    AssessmentImportBatch,
+    EvaluationCycle,
+    Observation,
+    PlayerAssessment,
+)
+from analytics.services.assessment_feature import assessments_enabled
+from analytics.services.assessment_import_service import (
+    assessment_records_for_player,
+    commit_assessment_import_batch,
+    create_assessment_import_batch,
+    resolve_assessment_import_row,
+    summarize_import_batch,
+)
 from analytics.services.coach_assessment_service import (
     assessment_status_for_players,
     get_active_coach_assessment_cycle,
@@ -23,12 +49,6 @@ from analytics.services.comparison_service import (
     get_player_comparison,
     get_player_score_summary,
 )
-from analytics.services.player_service import (
-    parse_player_search_filters,
-    search_players,
-    selected_players_from_ids,
-    staff_player_queryset,
-)
 from analytics.services.draft_service import get_draft_contexts_for_player
 from analytics.services.evaluation_access_service import (
     active_evaluation_cycle,
@@ -37,8 +57,16 @@ from analytics.services.evaluation_access_service import (
     get_my_evaluations,
     get_or_create_evaluation_for_player,
 )
-from analytics.services.evaluation_review_service import get_evaluation_review_detail, get_evaluation_review_list
-from analytics.services.observation_service import get_observation_detail, save_observation_responses, submit_observation
+from analytics.services.evaluation_review_service import (
+    get_evaluation_review_detail,
+    get_evaluation_review_list,
+)
+from analytics.services.metrics_service import normalize_cycle_id
+from analytics.services.observation_service import (
+    get_observation_detail,
+    save_observation_responses,
+    submit_observation,
+)
 from analytics.services.permissions import (
     can_edit_observation,
     can_evaluate_player,
@@ -49,12 +77,15 @@ from analytics.services.permissions import (
     can_view_my_evaluations,
     can_view_observation,
 )
-from analytics.services.metrics_service import normalize_cycle_id
+from analytics.services.player_service import (
+    parse_player_search_filters,
+    search_players,
+    selected_players_from_ids,
+    staff_player_queryset,
+)
 from analytics.services.reporting_service import get_command_center_context
 from analytics.services.timeline_service import get_player_timeline
-from players.models import PlayerImportBatch
-from players.models import Player
-from seasons.models import PlayerRosterMembership
+from players.models import Player, PlayerImportBatch
 from players.services.import_service import (
     MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS,
     MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS,
@@ -63,6 +94,7 @@ from players.services.import_service import (
     create_import_batch,
     current_preview,
 )
+from seasons.models import PlayerRosterMembership
 
 
 class AnalyticsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
@@ -70,6 +102,13 @@ class AnalyticsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
         return self.request.user.is_staff or self.request.user.is_superuser
 
 
+class AssessmentFeatureRequiredMixin(AnalyticsStaffRequiredMixin):
+    def dispatch(self, request, *args, **kwargs):
+        if not assessments_enabled():
+            raise Http404("Assessment events are not enabled.")
+        return super().dispatch(request, *args, **kwargs)
+
+
 class AnalyticsCommandCenterView(AnalyticsStaffRequiredMixin, TemplateView):
     template_name = "analytics/command_center.html"
 
@@ -78,7 +117,9 @@ class AnalyticsCommandCenterView(AnalyticsStaffRequiredMixin, TemplateView):
         cycle_id = normalize_cycle_id(self.request.GET.get("cycle"))
         division = self.request.GET.get("division", "").strip()
         team = self.request.GET.get("team", "").strip()
-        command_center = get_command_center_context(cycle_id=cycle_id, division=division, team=team)
+        command_center = get_command_center_context(
+            cycle_id=cycle_id, division=division, team=team
+        )
         context.update(
             {
                 "command_center": command_center,
@@ -115,9 +156,13 @@ class PlayerImportUploadView(AnalyticsStaffRequiredMixin, FormView):
             source=form.cleaned_data["source"],
             uploaded_by=self.request.user,
             season=form.cleaned_data["season"],
-            provision_player_accounts=form.cleaned_data.get("provision_player_accounts", False),
+            provision_player_accounts=form.cleaned_data.get(
+                "provision_player_accounts", False
+            ),
+        )
+        messages.success(
+            self.request, "CSV uploaded. Review the import preview before committing."
         )
-        messages.success(self.request, "CSV uploaded. Review the import preview before committing.")
         return redirect("analytics:import-preview", pk=batch.pk)
 
 
@@ -152,9 +197,14 @@ class PlayerImportPreviewView(ImportBatchMixin, TemplateView):
         form = self.get_mapping_form(data=request.POST)
         if form.is_valid():
             mapping_config = form.mapping_config()
-            for key in [MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS, MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS]:
+            for key in [
+                MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS,
+                MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS,
+            ]:
                 mapping_config[key] = bool(self.import_batch.mapping_config.get(key))
-            build_import_preview(import_batch=self.import_batch, mapping_config=mapping_config)
+            build_import_preview(
+                import_batch=self.import_batch, mapping_config=mapping_config
+            )
             messages.success(request, "Import preview refreshed.")
             return redirect("analytics:import-preview", pk=self.import_batch.pk)
         return self.render_to_response(self.get_context_data(mapping_form=form))
@@ -167,7 +217,9 @@ class PlayerImportConflictView(ImportBatchMixin, TemplateView):
         context = super().get_context_data(**kwargs)
         preview = context.get("preview") or {}
         context["review_rows"] = [
-            row for row in preview.get("rows", []) if row.get("action") == "needs_review" or row.get("errors")
+            row
+            for row in preview.get("rows", [])
+            if row.get("action") == "needs_review" or row.get("errors")
         ]
         return context
 
@@ -189,7 +241,9 @@ class PlayerImportConfirmView(ImportBatchMixin, View):
             f"Import committed. Created {result.created}, updated {result.updated}, skipped {result.skipped}.",
         )
         if result.errors:
-            messages.warning(request, f"{len(result.errors)} row issue(s) were recorded.")
+            messages.warning(
+                request, f"{len(result.errors)} row issue(s) were recorded."
+            )
         return redirect("analytics:import-detail", pk=self.import_batch.pk)
 
 
@@ -232,15 +286,216 @@ class PlayerProfileView(AnalyticsStaffRequiredMixin, TemplateView):
             {
                 "player": self.player,
                 "tags": self.player.tags.filter(is_active=True).order_by("name"),
-                "source_rows": self.player.source_rows.select_related("import_batch").order_by("-imported_at", "-id"),
+                "source_rows": self.player.source_rows.select_related(
+                    "import_batch"
+                ).order_by("-imported_at", "-id"),
                 "draft_contexts": get_draft_contexts_for_player(self.player),
                 "score_summary": score_summary,
                 "timeline": timeline,
+                "assessments_enabled": assessments_enabled(),
+                "assessment_records": (
+                    assessment_records_for_player(self.player)
+                    if assessments_enabled()
+                    else []
+                ),
             }
         )
         return context
 
 
+class AssessmentEventListView(AssessmentFeatureRequiredMixin, ListView):
+    model = AssessmentEvent
+    template_name = "analytics/assessment_event_list.html"
+    context_object_name = "assessment_events"
+    paginate_by = 25
+
+    def get_queryset(self):
+        return AssessmentEvent.objects.select_related(
+            "season", "template", "scoring_profile"
+        )
+
+
+class AssessmentEventDetailView(AssessmentFeatureRequiredMixin, TemplateView):
+    template_name = "analytics/assessment_event_detail.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        self.assessment_event = get_object_or_404(
+            AssessmentEvent.objects.select_related("season", "template"),
+            pk=kwargs["event_id"],
+        )
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        assessments = (
+            PlayerAssessment.objects.filter(event=self.assessment_event)
+            .select_related(
+                "player", "roster_membership", "roster_membership__season_team"
+            )
+            .prefetch_related("values__template_metric")
+        )
+        context.update(
+            {
+                "assessment_event": self.assessment_event,
+                "player_assessments": assessments,
+            }
+        )
+        return context
+
+
+class PlayerAssessmentDetailView(AssessmentFeatureRequiredMixin, TemplateView):
+    template_name = "analytics/player_assessment_detail.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        self.player_assessment = get_object_or_404(
+            PlayerAssessment.objects.select_related(
+                "player", "event", "event__season"
+            ).prefetch_related(
+                "values__template_metric", "values__template_metric__metric"
+            ),
+            pk=kwargs["pk"],
+        )
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["player_assessment"] = self.player_assessment
+        context["values"] = self.player_assessment.values.all()
+        return context
+
+
+class AssessmentImportListView(AssessmentFeatureRequiredMixin, ListView):
+    model = AssessmentImportBatch
+    template_name = "analytics/assessment_import_list.html"
+    context_object_name = "import_batches"
+    paginate_by = 25
+
+    def get_queryset(self):
+        return AssessmentImportBatch.objects.select_related(
+            "event", "event__season", "uploaded_by"
+        )
+
+
+class AssessmentImportUploadView(AssessmentFeatureRequiredMixin, FormView):
+    template_name = "analytics/assessment_import_upload.html"
+    form_class = AssessmentImportUploadForm
+
+    def form_valid(self, form):
+        try:
+            batch = create_assessment_import_batch(
+                file_obj=form.cleaned_data["workbook"],
+                event=form.cleaned_data["event"],
+                import_template=form.cleaned_data["import_template"],
+                uploaded_by=self.request.user,
+            )
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.render_to_response(self.get_context_data(form=form))
+        messages.success(
+            self.request,
+            "Assessment workbook uploaded. Review matches before committing.",
+        )
+        return redirect("analytics:assessment-import-preview", pk=batch.pk)
+
+
+class AssessmentImportBatchMixin(AssessmentFeatureRequiredMixin):
+    assessment_import_batch = None
+
+    def dispatch(self, request, *args, **kwargs):
+        self.assessment_import_batch = get_object_or_404(
+            AssessmentImportBatch.objects.select_related(
+                "event", "event__season", "import_template"
+            ),
+            pk=kwargs["pk"],
+        )
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["import_batch"] = self.assessment_import_batch
+        context["summary"] = summarize_import_batch(self.assessment_import_batch)
+        return context
+
+
+class AssessmentImportPreviewView(AssessmentImportBatchMixin, TemplateView):
+    template_name = "analytics/assessment_import_preview.html"
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["rows"] = self.assessment_import_batch.rows.select_related(
+            "player", "roster_membership"
+        )
+        return context
+
+
+class AssessmentImportResolveView(AssessmentImportBatchMixin, TemplateView):
+    template_name = "analytics/assessment_import_resolve.html"
+
+    def _review_rows(self):
+        return self.assessment_import_batch.rows.select_related("player").filter(
+            status__in=[
+                ASSESSMENT_IMPORT_ROW_UNMATCHED,
+                ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
+                ASSESSMENT_IMPORT_ROW_INVALID,
+            ]
+        )
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["forms"] = [
+            (row, AssessmentImportRowResolutionForm(row=row))
+            for row in self._review_rows()
+        ]
+        return context
+
+    def post(self, request, *args, **kwargs):
+        for row in self._review_rows():
+            form = AssessmentImportRowResolutionForm(
+                data={
+                    "player": request.POST.get(f"row_{row.pk}_player", ""),
+                    "skip": request.POST.get(f"row_{row.pk}_skip", ""),
+                },
+                row=row,
+            )
+            if form.is_valid():
+                resolve_assessment_import_row(
+                    row=row,
+                    player=form.cleaned_data.get("player"),
+                    skip=form.cleaned_data.get("skip"),
+                )
+        messages.success(request, "Assessment import resolutions updated.")
+        return redirect(
+            "analytics:assessment-import-preview",
+            pk=self.assessment_import_batch.pk,
+        )
+
+
+class AssessmentImportConfirmView(AssessmentImportBatchMixin, View):
+    def post(self, request, *args, **kwargs):
+        try:
+            result = commit_assessment_import_batch(
+                batch=self.assessment_import_batch,
+                actor=request.user,
+            )
+        except (PermissionDenied, ValidationError) as exc:
+            messages.error(request, str(exc))
+            return redirect(
+                "analytics:assessment-import-preview",
+                pk=self.assessment_import_batch.pk,
+            )
+        messages.success(
+            request,
+            f"Assessment import committed. Created {result.created}, updated {result.updated}, skipped {result.skipped}.",
+        )
+        return redirect(
+            "analytics:assessment-import-detail", pk=self.assessment_import_batch.pk
+        )
+
+
+class AssessmentImportDetailView(AssessmentImportBatchMixin, TemplateView):
+    template_name = "analytics/assessment_import_detail.html"
+
+
 class PlayerComparisonView(AnalyticsStaffRequiredMixin, TemplateView):
     template_name = "analytics/player_compare.html"
 
@@ -248,7 +503,9 @@ class PlayerComparisonView(AnalyticsStaffRequiredMixin, TemplateView):
         ids = list(self.request.GET.getlist("players"))
         player_ids = (self.request.GET.get("player_ids") or "").strip()
         if player_ids:
-            ids.extend([value.strip() for value in player_ids.split(",") if value.strip()])
+            ids.extend(
+                [value.strip() for value in player_ids.split(",") if value.strip()]
+            )
         return ids
 
     def get_context_data(self, **kwargs):
@@ -311,9 +568,13 @@ class EvaluationPlayerView(EvaluationSubmitterRequiredMixin, TemplateView):
         membership_id = request.GET.get("membership") or request.POST.get("membership")
         if membership_id:
             membership = get_object_or_404(PlayerRosterMembership, pk=membership_id)
-        self.observation = get_or_create_evaluation_for_player(request.user, player, cycle, player_roster_membership=membership)
+        self.observation = get_or_create_evaluation_for_player(
+            request.user, player, cycle, player_roster_membership=membership
+        )
         if self.observation.status == OBSERVATION_STATUS_SUBMITTED:
-            return redirect("analytics:assessment-detail", observation_id=self.observation.pk)
+            return redirect(
+                "analytics:assessment-detail", observation_id=self.observation.pk
+            )
         return super().dispatch(request, *args, **kwargs)
 
     def get_form(self, data=None, require_required=False):
@@ -348,9 +609,14 @@ class EvaluationPlayerView(EvaluationSubmitterRequiredMixin, TemplateView):
                 if action == "submit":
                     submit_observation(self.observation, actor=request.user)
                     messages.success(request, "Evaluation submitted.")
-                    return redirect("analytics:assessment-detail", observation_id=self.observation.pk)
+                    return redirect(
+                        "analytics:assessment-detail",
+                        observation_id=self.observation.pk,
+                    )
                 messages.success(request, "Evaluation draft saved.")
-                return redirect("analytics:evaluation-player", player_id=self.observation.player_id)
+                return redirect(
+                    "analytics:evaluation-player", player_id=self.observation.player_id
+                )
             except ValidationError as exc:
                 form.add_error(None, exc)
         return self.render_to_response(self.get_context_data(form=form))
@@ -401,7 +667,9 @@ class MyEvaluationDetailView(LoginRequiredMixin, TemplateView):
 
     def dispatch(self, request, *args, **kwargs):
         try:
-            self.detail = get_my_evaluation_detail(request.user, kwargs["observation_id"])
+            self.detail = get_my_evaluation_detail(
+                request.user, kwargs["observation_id"]
+            )
         except Observation.DoesNotExist as exc:
             raise Http404("Evaluation not found.") from exc
         return super().dispatch(request, *args, **kwargs)
@@ -414,7 +682,9 @@ class MyEvaluationDetailView(LoginRequiredMixin, TemplateView):
 
 class EvaluationReviewRequiredMixin(LoginRequiredMixin):
     def dispatch(self, request, *args, **kwargs):
-        if request.user.is_authenticated and not can_review_submitted_evaluations(request.user):
+        if request.user.is_authenticated and not can_review_submitted_evaluations(
+            request.user
+        ):
             raise PermissionDenied("You cannot review submitted evaluations.")
         return super().dispatch(request, *args, **kwargs)
 
@@ -445,7 +715,9 @@ class EvaluationReviewDetailView(EvaluationReviewRequiredMixin, TemplateView):
 
     def dispatch(self, request, *args, **kwargs):
         try:
-            self.detail = get_evaluation_review_detail(request.user, kwargs["observation_id"])
+            self.detail = get_evaluation_review_detail(
+                request.user, kwargs["observation_id"]
+            )
         except Observation.DoesNotExist as exc:
             raise Http404("Evaluation not found.") from exc
         return super().dispatch(request, *args, **kwargs)
@@ -461,19 +733,28 @@ class CoachAssessmentListView(LoginRequiredMixin, TemplateView):
 
     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
-        cycle = get_active_coach_assessment_cycle(normalize_cycle_id(self.request.GET.get("cycle")))
+        cycle = get_active_coach_assessment_cycle(
+            normalize_cycle_id(self.request.GET.get("cycle"))
+        )
         query = self.request.GET.get("q", "").strip()
         division = self.request.GET.get("division", "").strip()
         team = self.request.GET.get("team", "").strip()
         players = Player.objects.none()
         player_statuses = []
         if cycle:
-            players = list_memberships_for_assessment(cycle, query=query, division=division, team=team)
-            player_statuses = assessment_status_for_players(list(players), cycle, self.request.user)
+            players = list_memberships_for_assessment(
+                cycle, query=query, division=division, team=team
+            )
+            player_statuses = assessment_status_for_players(
+                list(players), cycle, self.request.user
+            )
         context.update(
             {
                 "cycle": cycle,
-                "cycles": EvaluationCycle.objects.filter(is_active=True, coach_assessment_question_set__observation_type__key=OBSERVATION_TYPE_COACH_ASSESSMENT),
+                "cycles": EvaluationCycle.objects.filter(
+                    is_active=True,
+                    coach_assessment_question_set__observation_type__key=OBSERVATION_TYPE_COACH_ASSESSMENT,
+                ),
                 "player_statuses": player_statuses,
                 "query": query,
                 "division": division,
@@ -488,31 +769,46 @@ class CoachAssessmentEditView(LoginRequiredMixin, TemplateView):
     observation = None
 
     def dispatch(self, request, *args, **kwargs):
-        if request.user.is_authenticated and not can_submit_coach_assessment(request.user):
+        if request.user.is_authenticated and not can_submit_coach_assessment(
+            request.user
+        ):
             raise PermissionDenied("You cannot submit coach assessments.")
         if "observation_id" in kwargs:
             self.observation = get_object_or_404(
-                Observation.objects.select_related("player", "evaluation_cycle", "question_set", "evaluator"),
+                Observation.objects.select_related(
+                    "player", "evaluation_cycle", "question_set", "evaluator"
+                ),
                 pk=kwargs["observation_id"],
                 observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
             )
             if not can_edit_observation(request.user, self.observation):
                 if can_view_observation(request.user, self.observation):
-                    return redirect("analytics:assessment-detail", observation_id=self.observation.pk)
+                    return redirect(
+                        "analytics:assessment-detail",
+                        observation_id=self.observation.pk,
+                    )
                 raise PermissionDenied("You cannot edit this assessment.")
         else:
-            cycle = get_active_coach_assessment_cycle(normalize_cycle_id(request.GET.get("cycle")))
+            cycle = get_active_coach_assessment_cycle(
+                normalize_cycle_id(request.GET.get("cycle"))
+            )
             if not cycle:
-                messages.error(request, "No active coach assessment cycle is available.")
+                messages.error(
+                    request, "No active coach assessment cycle is available."
+                )
                 return redirect("analytics:assessment-list")
             player = get_object_or_404(Player, pk=kwargs["player_id"], is_active=True)
             if not can_evaluate_player(request.user, player):
                 raise PermissionDenied("You cannot evaluate this player.")
             existing = get_existing_coach_assessment(player, cycle, request.user)
             if existing and existing.status == OBSERVATION_STATUS_SUBMITTED:
-                return redirect("analytics:assessment-detail", observation_id=existing.pk)
+                return redirect(
+                    "analytics:assessment-detail", observation_id=existing.pk
+                )
             membership = None
-            membership_id = request.GET.get("membership") or request.POST.get("membership")
+            membership_id = request.GET.get("membership") or request.POST.get(
+                "membership"
+            )
             if membership_id:
                 membership = get_object_or_404(PlayerRosterMembership, pk=membership_id)
             self.observation = get_or_create_draft_coach_assessment(
@@ -555,9 +851,14 @@ class CoachAssessmentEditView(LoginRequiredMixin, TemplateView):
                 if action == "submit":
                     submit_observation(self.observation, actor=request.user)
                     messages.success(request, "Assessment submitted.")
-                    return redirect("analytics:assessment-detail", observation_id=self.observation.pk)
+                    return redirect(
+                        "analytics:assessment-detail",
+                        observation_id=self.observation.pk,
+                    )
                 messages.success(request, "Assessment draft saved.")
-                return redirect("analytics:assessment-edit", observation_id=self.observation.pk)
+                return redirect(
+                    "analytics:assessment-edit", observation_id=self.observation.pk
+                )
             except ValidationError as exc:
                 form.add_error(None, exc)
         return self.render_to_response(self.get_context_data(form=form))
@@ -568,7 +869,13 @@ class CoachAssessmentDetailView(LoginRequiredMixin, TemplateView):
 
     def dispatch(self, request, *args, **kwargs):
         self.observation = get_object_or_404(
-            Observation.objects.select_related("player", "evaluation_cycle", "question_set", "evaluator", "evaluator_role"),
+            Observation.objects.select_related(
+                "player",
+                "evaluation_cycle",
+                "question_set",
+                "evaluator",
+                "evaluator_role",
+            ),
             pk=kwargs["observation_id"],
             observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
         )
@@ -579,13 +886,18 @@ class CoachAssessmentDetailView(LoginRequiredMixin, TemplateView):
     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         observation = get_observation_detail(self.observation.pk)
-        responses = {response.question_id: response for response in observation.responses.all()}
+        responses = {
+            response.question_id: response for response in observation.responses.all()
+        }
         question_groups = []
         for group in group_questions_for_display(observation.question_set):
             question_groups.append(
                 {
                     "category": group["category"],
-                    "questions": [{"question": question, "response": responses.get(question.id)} for question in group["questions"]],
+                    "questions": [
+                        {"question": question, "response": responses.get(question.id)}
+                        for question in group["questions"]
+                    ],
                 }
             )
         context.update(
@@ -636,7 +948,9 @@ class StaffObservationReviewListView(AnalyticsStaffRequiredMixin, ListView):
         return context
 
 
-class StaffObservationReviewDetailView(AnalyticsStaffRequiredMixin, CoachAssessmentDetailView):
+class StaffObservationReviewDetailView(
+    AnalyticsStaffRequiredMixin, CoachAssessmentDetailView
+):
     template_name = "analytics/assessment_review.html"
 
     def get_context_data(self, **kwargs):
@@ -645,8 +959,16 @@ class StaffObservationReviewDetailView(AnalyticsStaffRequiredMixin, CoachAssessm
         return context
 
     def post(self, request, *args, **kwargs):
-        self.observation = get_object_or_404(Observation, pk=kwargs["observation_id"], observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT)
-        if request.POST.get("action") == "reopen" and can_reopen_observation(request.user, self.observation):
+        self.observation = get_object_or_404(
+            Observation,
+            pk=kwargs["observation_id"],
+            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
+        )
+        if request.POST.get("action") == "reopen" and can_reopen_observation(
+            request.user, self.observation
+        ):
             reopen_observation(self.observation, request.user)
             messages.success(request, "Assessment reopened for editing.")
-        return redirect("analytics:observation-review-detail", observation_id=self.observation.pk)
+        return redirect(
+            "analytics:observation-review-detail", observation_id=self.observation.pk
+        )
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 1c81d34..e0e5433 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -552,6 +552,8 @@ Coach review displays the saved season/team/division from the submitted evaluati
 
 Staff Analytics helps coordinators and administrators manage player records, imports, evaluations, timelines, comparisons, and decision-support summaries.
 
+When enabled by administrators, Staff Analytics can also manage versioned assessment events and import structured `.xlsx` assessment workbooks.
+
 ### Who Uses It
 
 Staff and administrators with Django staff/superuser access.
@@ -564,6 +566,7 @@ Staff and administrators with Django staff/superuser access.
 4. Open player profiles and timelines.
 5. Review imports and submitted evaluations.
 6. Compare players when preparing baseball decisions.
+7. If assessment events are enabled, import and review workbook assessment results.
 
 ### Related Pages
 
@@ -573,6 +576,8 @@ Staff and administrators with Django staff/superuser access.
 - `/analytics/players/compare/`
 - `/analytics/imports/`
 - `/analytics/observations/review/`
+- `/analytics/assessment-events/`
+- `/analytics/assessment-imports/`
 
 ### Analytics Command Center
 
@@ -643,6 +648,36 @@ This page still uses `observations` in the URL because that is the internal Anal
 
 Staff review shows saved season and roster context for submitted evaluations. Older legacy records without season context may display as `Legacy / No Season`.
 
+### Assessment Events
+
+Assessment Events are staff-only workbook assessment records.
+
+They are separate from normal evaluations. Evaluations are submitted by coaches, players, staff, or guest evaluators through the evaluation form. Assessment Events import structured workbook data such as running, hitting, fielding, throwing, or pitching measurements from a configured `.xlsx` file.
+
+Assessment Event pages are available only when the assessment feature has been enabled by administrators.
+
+Staff can use:
+
+```text
+/analytics/assessment-events/
+/analytics/assessment-imports/
+```
+
+Typical workflow:
+
+1. Confirm the assessment configuration and event have been created.
+2. Open Assessment Imports.
+3. Upload the `.xlsx` workbook.
+4. Review the preview.
+5. Resolve unmatched, ambiguous, or invalid player rows.
+6. Skip rows that should not be imported.
+7. Confirm the import.
+8. Review imported assessment values from the Assessment Event or a player profile.
+
+Assessment imports do not create players, teams, roster memberships, or coach assignments. They only attach assessment values to existing players.
+
+Ranking sheets in the workbook are used for quality review only. They are not imported as ordinary player metrics.
+
 ## Player Imports
 
 ### Purpose
diff --git a/docs/analytics/architecture/11_assessments.md b/docs/analytics/architecture/11_assessments.md
new file mode 100644
index 0000000..d4f41ba
--- /dev/null
+++ b/docs/analytics/architecture/11_assessments.md
@@ -0,0 +1,105 @@
+# Versioned Assessment Events
+
+## Purpose
+
+The Analytics assessment-event subsystem stores objective and rubric-style workbook assessment data without changing the existing evaluation workflow.
+
+Existing evaluations continue to use `Observation`, `ObservationResponse`, `ObservationQuestion`, and `ObservationQuestionSet`.
+
+Workbook assessment events use separate models so staff can import structured assessment data while preserving the original evaluation architecture.
+
+## Feature Flag
+
+Assessment-event pages are controlled by:
+
+```text
+ANALYTICS_ASSESSMENTS_ENABLED
+```
+
+The default is `false`.
+
+When disabled:
+
+- assessment-event routes return 404;
+- assessment import routes return 404;
+- assessment-event navigation is hidden;
+- existing evaluations, imports, and reports continue to work normally.
+
+## Ownership
+
+Analytics owns:
+
+- assessment templates;
+- assessment metrics;
+- assessment events;
+- player assessment records;
+- assessment value records;
+- workbook assessment imports.
+
+Players owns canonical player identity.
+
+Seasons owns seasons, teams, player roster memberships, and coach assignments.
+
+Assessment imports must reference existing players and existing season context. They must not create players, teams, roster memberships, or coach assignments.
+
+## Import Workflow
+
+Workbook imports are staff-only.
+
+The workflow is:
+
+1. Staff creates or selects an `AssessmentEvent`.
+2. Staff uploads an `.xlsx` workbook using an active `AssessmentImportTemplate`.
+3. The system creates an `AssessmentImportBatch` and preview rows.
+4. The system performs conservative player matching.
+5. Staff resolves or skips unmatched, ambiguous, or invalid rows.
+6. Staff explicitly confirms the import.
+7. The system creates or updates `PlayerAssessment` and `AssessmentValue` records atomically.
+
+No assessment values are committed during preview.
+
+## Player Matching
+
+Matching must be conservative:
+
+- exact source identifiers first, if provided by a future import template;
+- exact player display/full-name match;
+- exact player alias match;
+- otherwise unresolved.
+
+Fuzzy matches must not auto-commit.
+
+Unresolved rows must be manually matched or skipped before confirmation.
+
+## Historical Safety
+
+Assessment configuration is versioned.
+
+After committed assessment data exists:
+
+- template identity is locked;
+- template metric meaning, units, scale, order, and type are locked;
+- import template configuration is locked;
+- scoring profile configuration is locked.
+
+Corrections should create a new version or use explicit manual override behavior rather than silently changing historical meaning.
+
+## 2026 13U Workbook
+
+The initial workbook support is based on:
+
+```text
+2026 VCB House - 13u PeeWee Assessment.xlsx
+```
+
+Configured data sheets:
+
+- `Assessment Data`
+- `Pitching Data`
+
+Ranking sheets are treated as provenance/QA context only:
+
+- `Ranking`
+- `Pitcher Ranking`
+
+Ranking sheets are not imported as ordinary player metrics.
diff --git a/docs/analytics/architecture/README.md b/docs/analytics/architecture/README.md
index d6cd1fc..f060c01 100644
--- a/docs/analytics/architecture/README.md
+++ b/docs/analytics/architecture/README.md
@@ -31,7 +31,8 @@ Recommended reading order:
 9. [08 Reporting](08_reporting.md)
 10. [09 Services](09_services.md)
 11. [10 Permissions](10_permissions.md)
-12. [90 Implementation Roadmap](90_implementation_roadmap.md)
+12. [11 Assessments](11_assessments.md)
+13. [90 Implementation Roadmap](90_implementation_roadmap.md)
 
 Use [GLOSSARY.md](GLOSSARY.md) as the canonical vocabulary reference.
 
diff --git a/docs/deployment/README.md b/docs/deployment/README.md
index fc544c3..e83987d 100644
--- a/docs/deployment/README.md
+++ b/docs/deployment/README.md
@@ -62,6 +62,7 @@ Future production deployments should:
 - keep secrets out of Git;
 - use environment variables for deployment-specific settings;
 - configure `COACH_IMPORT_DEFAULT_PASSWORD` before creating new imported coach accounts;
+- enable `ANALYTICS_ASSESSMENTS_ENABLED` only for staged rollout of workbook assessment imports;
 - back up the database before migrations;
 - archive media before major upgrades;
 - verify migrations before applying them;
diff --git a/docs/deployment/RUNBOOK.md b/docs/deployment/RUNBOOK.md
index 9c73eba..fd032cc 100644
--- a/docs/deployment/RUNBOOK.md
+++ b/docs/deployment/RUNBOOK.md
@@ -62,6 +62,7 @@ DJANGO_ALLOWED_HOSTS
 DJANGO_STATIC_ROOT
 DJANGO_MEDIA_ROOT
 COACH_IMPORT_DEFAULT_PASSWORD
+ANALYTICS_ASSESSMENTS_ENABLED
 ```
 
 Verify systemd configuration:
@@ -82,6 +83,21 @@ it, communicate it to coaches through an approved operational channel, and
 rotate it when appropriate. Do not paste the value into Git, logs, screenshots,
 or shared documentation.
 
+`ANALYTICS_ASSESSMENTS_ENABLED` defaults to false. Keep it false until the
+assessment configuration has been bootstrapped, assessment events have been
+created, and staff are ready to import workbook assessment data.
+
+Bootstrap the initial 2026 13U assessment configuration without importing player
+results:
+
+```bash
+python manage.py bootstrap_2026_13u_assessment --dry-run
+python manage.py bootstrap_2026_13u_assessment
+```
+
+Then enable the feature flag in the environment and restart the application
+service.
+
 ## Deployment
 
 Activate the production virtual environment if needed, then verify dependencies:
diff --git a/requirements.txt b/requirements.txt
index e197548..9a88bc7 100644
--- a/requirements.txt
+++ b/requirements.txt
@@ -1,5 +1,6 @@
 asgiref==3.10.0
 Django==4.2.30
 gunicorn==21.2.0
+openpyxl==3.1.5
 pillow==11.3.0
 sqlparse==0.5.3
diff --git a/vancouverminor/settings.py b/vancouverminor/settings.py
index ffbb762..7927ca4 100644
--- a/vancouverminor/settings.py
+++ b/vancouverminor/settings.py
@@ -49,6 +49,8 @@ COACH_IMPORT_DEFAULT_PASSWORD = os.environ.get(
     "COACH_IMPORT_DEFAULT_PASSWORD", ""
 ).strip()
 
+ANALYTICS_ASSESSMENTS_ENABLED = env_bool("ANALYTICS_ASSESSMENTS_ENABLED", default=False)
+
 
 # Application definition
 

```

# Prompt 108 - Platform

## User Prompt

```text
You are working in the production Django repository:

/Users/eugenelin/dev/vmba0

GitHub repository:

https://github.com/eugenelin89/vancouverminorbaseball

Current main branch includes:

- 9d5125e Add feature-flagged assessment workbook imports
- bc6c9c3 Archive assessment workbook import prompt

The production system is already actively used.

Do not deploy or enable the assessment feature as part of this task.

The purpose of this task is to harden and correct the new assessment subsystem before it is deployed to production or used to import real player data.

The real workbook should be attached to this task:

2026 VCB House - 13u PeeWee Assessment(1).xlsx

Do not commit the workbook, player names, player measurements, workbook-derived player records, or other real player data to Git.

# Objective

Review the existing implementation first, then correct all identified production-safety, data-integrity, validation, immutability, re-import, unit, rating-scale, and test-coverage problems in the versioned assessment workbook subsystem.

The assessment subsystem must remain:

- additive
- feature-flagged
- staff-only
- isolated from the existing evaluation system
- compatible with future workbook formats
- safe for production deployment
- incapable of silently corrupting or reinterpreting historical data

The existing self, peer, coach, staff, and guest evaluation workflows must continue working exactly as they do now.

# Critical instruction: review before coding

Before changing anything, inspect the current repository and implementation.

At minimum, review:

- the current Git working tree
- commits `9d5125e` and `bc6c9c3`
- `analytics/models.py`
- `analytics/forms.py`
- `analytics/views.py`
- `analytics/urls.py`
- `analytics/admin.py`
- `analytics/services/assessment_feature.py`
- `analytics/services/assessment_matching_service.py`
- `analytics/services/assessment_import_service.py`
- `analytics/management/commands/bootstrap_2026_13u_assessment.py`
- `analytics/tests/test_assessment_imports.py`
- all assessment templates under `analytics/templates/analytics/`
- `analytics/services/reporting_service.py`
- `analytics/templates/analytics/player_profile.html`
- migration `analytics/migrations/0006_assessmentevent_assessmentimportbatch_and_more.py`
- `players/models.py`
- `seasons/models.py`
- `docs/analytics/architecture/11_assessments.md`
- `docs/USER_MANUAL.md`
- `docs/deployment/RUNBOOK.md`
- `requirements.txt`
- the actual attached workbook

Review current evaluation tests and services to confirm that the assessment subsystem remains isolated from:

- `Observation`
- `ObservationResponse`
- evaluation score summaries
- evaluation report views
- player comparison
- evaluation submission
- My Evaluations
- coach assessments
- existing imports

Do not assume the previous implementation report is complete or correct. Verify behaviour from the code.

# Git discipline

Inspect the working tree before making changes.

Preserve this unrelated local modification:

/Users/eugenelin/dev/vmba0/docs/qa/platform_e2e/test_coaches_import.csv

Do not modify, stage, discard, or commit that file.

Do not rewrite migration `0006`.

Create one or more new migrations beginning with `0007`.

Use focused commits.

Push to the current branch after all checks pass.

Archive this prompt as:

docs/prompts/prompt_108_platform.md

unless repository inspection shows that a newer prompt number is required.

Commit the implementation and prompt archive separately, following the project convention.

# Existing production functionality that must not change

Do not change the meaning, validation, permissions, queries, calculations, or workflow of:

- `analytics.Observation`
- `analytics.ObservationResponse`
- `analytics.ObservationQuestion`
- `analytics.ObservationQuestionSet`
- existing 1–5 ratings
- evaluation drafts
- evaluation submission
- self evaluations
- peer evaluations
- coach evaluations
- staff evaluations
- guest evaluations
- submitted evaluation review
- My Evaluations
- current evaluation report averages
- player comparison averages
- existing command-center evaluation metrics
- player imports
- coach imports
- account provisioning
- authentication
- season and roster workflows
- draft workflows
- current URLs

Do not add assessment values to `get_player_score_summary()` or existing evaluation averages.

Do not remove or weaken existing regression tests.

# Known defects that must be fixed

## 1. Correct the 2026 rating scale

The real workbook’s subjective assessment items use a 1–3 scale.

The current bootstrap code configures rating metrics as 1–5.

Correct every applicable 2026 assessment rating metric to:

- minimum: 1
- maximum: 3

This includes applicable:

- hitting mechanics ratings
- fielding ratings
- throwing ratings
- pitching mechanics ratings

Do not alter the existing evaluation system’s `rating_1_5` behaviour.

Assessment ratings must retain their original scale on every `AssessmentValue`.

A rating of `2` from the workbook must display as:

2 / 3

not:

2 / 5

Add tests proving this.

## 2. Add authoritative workbook-level validation

The current implementation can treat a workbook with no parsed rows or missing required worksheets as committable.

Fix this.

Persist workbook-level validation separately from row-level validation.

Add an explicit field or equivalent persisted structure on `AssessmentImportBatch`, such as:

- `validation_errors`
- `validation_warnings`

Do not rely only on `preview_snapshot`.

The batch must not be committable when any of the following is true:

- zero valid source rows were parsed
- a required worksheet is missing
- a required header row is missing
- the identity column is missing
- a required metric header is missing
- duplicate source rows are unresolved
- workbook-level validation errors exist
- row-level validation errors exist
- unmatched players remain
- ambiguous players remain
- manual-override conflicts remain
- required warning acknowledgements remain incomplete

`AssessmentPreviewSummary.can_commit` must explicitly require:

- at least one valid, non-skipped player row
- no blocking workbook errors
- no blocking row errors
- no unresolved identity matches
- no unresolved conflicts

The commit service must repeat all critical validation server-side.

Never trust only the disabled state of a button.

Add tests for empty and structurally invalid workbooks.

## 3. Validate required sheets and required headers

Extend the import-template configuration so that it explicitly supports:

For each sheet:

- `required`
- `header_row`
- `identity_column`
- optional maximum row count
- optional maximum column count

For each configured metric column:

- `required_header`
- `required_value`
- `value_type`
- valid range
- rating scale
- unit
- zero policy
- blank/update policy

For the current 2026 import template:

- `Assessment Data` must be a required sheet
- `Pitching Data` must be handled according to the actual workbook structure
- all expected structural headers must be validated
- individual player pitching rows may remain absent where a player was not assessed as a pitcher
- blank optional player values must not invalidate an otherwise valid row

A missing expected column must not be silently ignored.

If an optional column is absent, record that explicitly in validation/provenance.

Add tests for:

- missing required sheet
- missing optional sheet
- missing identity header
- missing required metric header
- unexpected extra column
- header normalization
- renamed headers through a different mapping version

## 4. Separate identity-resolution errors from data-validation errors

The current resolution screen includes invalid rows and allows choosing a player, which can change an invalid row into a matched row without fixing its data errors.

Correct this architecture.

Use separate concepts, fields, or statuses for:

- player identity match status
- data validation status
- import action
- conflict status

Choosing a player may resolve only an identity problem.

Choosing a player must not:

- clear numeric validation errors
- clear missing-header errors
- clear rating-scale errors
- clear duplicate-row errors
- make invalid data committable

Invalid data must require one of:

- corrected workbook
- corrected mapping/version
- explicit transformation defined by the import template
- explicit row skip
- explicit metric-level resolution where supported

The resolution UI must show all errors and warnings clearly.

Do not silently discard form errors.

When multiple row forms are submitted, show which rows failed validation.

Add tests proving that assigning a player to an invalid row does not make it committable.

## 5. Validate numeric ranges and rating scales

The parser currently verifies only whether a value can be converted to a number.

Add template-driven validation for:

- minimum numeric value
- maximum numeric value
- integer-only rating requirements
- rating minimum
- rating maximum
- allowed choices
- blank handling
- zero handling

For 2026 ratings:

- values must be integers
- allowed values must be 1, 2, or 3

Values such as the following must be rejected:

- 0
- 1.5
- 4
- non-numeric text

Preserve the original raw value in provenance even when invalid.

Add parser and service tests.

## 6. Implement explicit zero-value policies

Inspect the actual workbook and identify zero values.

Do not automatically assume every zero is valid.

Add a configurable zero policy per metric, supporting at least:

- `allow`
- `treat_as_missing`
- `warning`
- `error`

For physical measurements where zero is not a plausible completed measurement, configure a safe policy based on the workbook and domain meaning.

Examples likely requiring review include:

- bat speed
- time to contact
- average exit velocity
- maximum exit velocity
- pitching velocity
- jump distance
- shotput
- sprint time

Do not silently convert zero without recording:

- the raw value
- the transformation
- the reason
- the configured zero policy

For the current workbook, if the correct interpretation cannot be established from the workbook or repository documentation:

- mark the value as requiring review
- do not guess
- make the preview explain the issue
- require explicit staff acknowledgement or skip before commit

Add tests for every supported zero policy.

## 7. Do not guess physical units

The current bootstrap assumes units such as inches and feet even when the workbook headers may not state them.

Inspect the workbook and repository documentation.

Only assign a unit when it is supported by an authoritative source.

For metrics whose units are not verifiable:

- leave the normalized unit blank
- preserve the original source header
- mark metadata such as `unit_status = "unverified"`
- display “Unit not confirmed” in staff UI
- do not use the value for unit-dependent comparisons or transformations

Do not silently label shotput values as feet unless that unit is verified.

Do not silently label jump values as inches unless verified.

If baseball velocity units are established by the workbook, documentation, or an explicit operator-confirmed configuration, record the source of that confirmation in metadata.

The bootstrap dry-run must report:

- every metric
- configured value type
- configured scale
- configured unit
- whether the unit is verified
- zero policy
- blank/update policy

## 8. Make historical immutability real

The current `is_locked` implementation is incomplete.

Once committed assessment data or committed imports reference configuration, prevent semantic changes through:

- model methods
- service methods
- Django admin
- delete operations
- new child records added to locked parents

### AssessmentTemplate

After use, prevent changes to semantic fields, including:

- key
- version
- name where it affects historical identification
- effective dates
- metric membership
- metadata that changes meaning

Allow only explicitly safe lifecycle fields such as deactivation or retirement where appropriate.

### AssessmentTemplateMetric

For a locked or used template:

- existing metrics cannot be semantically edited
- metrics cannot be deleted
- new template metrics cannot be added
- metric order cannot change
- category cannot change
- display name cannot change
- value type cannot change
- unit cannot change
- range cannot change
- scale cannot change
- direction cannot change
- rubric cannot change

Override or otherwise protect `delete()`.

Prevent additions through both services and Django admin.

### AssessmentImportTemplate

After a committed import:

- key cannot change
- version cannot change
- config cannot change
- linked assessment template cannot change
- it cannot be deleted

### AssessmentScoringProfile

After use:

- key cannot change
- version cannot change
- config cannot change
- linked assessment template cannot change
- it cannot be deleted

### AssessmentEvent

After player assessments or committed imports exist, prevent changes to:

- season
- division where it represents historical context
- template
- scoring profile
- assessment dates
- event identity fields that affect historical meaning

Allow only explicitly safe lifecycle changes.

### AssessmentMetricDefinition

Once referenced by a used template:

- stable key cannot change
- default semantic type cannot change in a way that reinterprets history
- it cannot be deleted

### PlayerAssessment

After commit:

- player cannot change
- event cannot change
- provenance cannot be reassigned silently
- record cannot be deleted through ordinary admin operations

### AssessmentValue

Committed imported values must not be freely editable or deletable in Django admin.

Make committed values read-only in admin except through an explicit manual-correction service.

If a manual-correction workflow is included, require:

- staff actor
- reason
- previous-value snapshot
- new-value snapshot
- timestamp
- provenance metadata
- `source_kind = manual_corrected`
- `is_manual_override = true`

Add tests for:

- editing locked records
- deleting locked records
- adding metrics to locked templates
- changing an event template after import
- reassigning a committed player assessment
- direct admin/model changes that should be blocked

## 9. Add template compatibility validation

An import mapping must be compatible with the event’s assessment template.

Add an explicit relationship, preferably:

- `AssessmentImportTemplate.assessment_template`

or an equally strong validated relationship.

The upload form and service must reject:

- event using Template A
- import mapping built for Template B

Filter import-template choices where practical and validate again server-side.

Do not trust form filtering alone.

Consider similarly associating scoring profiles with the template they support.

Add migration and tests.

## 10. Use frozen configuration snapshots

`AssessmentImportBatch.config_snapshot` must be the authoritative mapping used for that batch.

Do not parse using a mutable live `AssessmentImportTemplate.config` after the batch has been created.

At upload time:

1. Validate template compatibility.
2. Deep-copy and persist the configuration snapshot.
3. Parse using that frozen snapshot.
4. Store a configuration checksum.
5. Commit using row snapshots derived from that frozen configuration.

Display the mapping version and checksum in the import detail page.

Add tests showing that editing an unused live mapping after upload does not change an existing batch preview or commit behaviour.

## 11. Correct failed-batch transaction behaviour

Review `create_assessment_import_batch()` carefully.

The current outer atomic transaction may roll back the newly created failed batch when parsing raises an exception.

Ensure that:

- a failed upload or parse can leave an auditable failed batch where appropriate
- failure status and validation errors persist
- no `PlayerAssessment` or `AssessmentValue` records are created
- no partial preview rows remain unless intentionally retained for diagnosis
- sensitive workbook content is not leaked into logs or error messages

Use transaction boundaries deliberately.

Add a test proving that a parse failure results in the intended persisted state.

## 12. Detect duplicate source rows safely

The current parser merges rows by normalized/slugified player name across worksheets.

Combining the same player across `Assessment Data` and `Pitching Data` is expected.

However, duplicate rows within the same source worksheet must not be silently merged.

Detect and report:

- duplicate normalized identity within one sheet
- duplicate source identifiers
- multiple rows for the same player/component
- slug collisions between different raw identities
- conflicting values for the same metric

Keep sheet joining explicit.

Use an internal join key that does not silently collapse distinct names because they create the same slug.

Add tests for:

- one player appearing once in both component sheets
- duplicate player rows within `Assessment Data`
- duplicate player rows within `Pitching Data`
- two distinct raw names normalizing to the same key
- conflicting duplicate metric values

## 13. Improve conservative player matching

Review the current player matching order.

Implement or verify this order:

1. exact configured source identifier including source namespace
2. exact canonical full/display name among active roster memberships for the selected event season and division
3. exact player alias among that season/division roster
4. unique exact canonical name outside the selected roster
5. unique exact alias outside the selected roster
6. manual resolution

Do not automatically fuzzy-match.

Do not iterate through every active player in Python when a normalized indexed lookup or a safer query/read model can be used.

When duplicate canonical names exist:

- return ambiguous
- include useful candidate context such as birth year, team, and division where permitted
- require manual selection

Do not create players or roster memberships.

Add tests for season/division preference and duplicate names.

## 14. Implement deterministic re-import behaviour

The current update path updates present values but leaves old values in place when a corrected workbook cell becomes blank.

Implement a full per-player, per-metric diff during preview.

Every metric must receive an explicit planned action:

- `create`
- `update`
- `unchanged`
- `clear`
- `skip`
- `protected_manual`
- `conflict`
- `invalid`

Do not use a generic `create_or_update` action without showing the actual changes.

### Blank handling

Add a configurable blank/update policy per metric, supporting at least:

- `preserve_existing`
- `clear_existing_imported_value`
- `ignore_on_create`
- `error_if_required`

For the current template, choose policies deliberately and document them.

When a previously imported value becomes blank and policy says clear:

- preview must show the old value
- preview must show that it will be cleared
- commit must clear or remove it deterministically
- provenance must record the action

Do not clear manually overridden values.

### Unchanged values

If the incoming normalized value and relevant provenance are unchanged:

- mark as unchanged
- do not update timestamps unnecessarily
- count it as unchanged, not updated

### Existing imported values

Updates must show:

- prior value
- incoming value
- normalized value
- action
- source
- warning/conflict state

### Removed metrics

A metric absent because the mapping version changed must not silently delete historical data.

Only metrics explicitly represented by the same frozen mapping and blank policy may be cleared.

Add comprehensive re-import tests.

## 15. Strengthen manual-override conflict handling

If an existing value is manually overridden:

- incoming identical value may be marked unchanged/protected
- incoming different value must not overwrite it
- incoming blank must not clear it
- preview must show the conflict
- staff must explicitly choose to preserve the manual value or skip the affected import action

For this release, do not allow workbook import to replace a manual correction.

A manual override conflict must not roll back unrelated valid rows only after a long commit attempt. It should be detected during preview.

Commit must validate again atomically.

Add tests covering:

- identical incoming value
- different incoming value
- blank incoming value
- explicit preserve resolution
- no silent overwrite

## 16. Add warning acknowledgement

Some transformations may be warnings rather than errors, including:

- configured zero treated as missing
- unverified unit
- ignored optional column
- workbook checksum seen before
- source annotation normalization

Add an explicit acknowledgement mechanism before confirmation.

The confirm request must include a server-validated acknowledgement tied to the current preview/version.

A stale acknowledgement must not apply after the preview changes.

Do not permit confirmation through a manually crafted POST that bypasses required acknowledgement.

## 17. Add upload resource limits

Because production accepts `.xlsx` uploads, add conservative protections:

- maximum upload size
- maximum worksheet count
- maximum parsed rows
- maximum columns
- maximum cell text length
- rejection of unsupported file types
- graceful handling of malformed or encrypted workbooks
- no execution of macros or external links
- safe error messages

Use settings or import-template limits where appropriate.

Do not load arbitrarily large workbooks into memory without limits.

Document the limits.

Add focused tests where practical.

## 18. Improve the staff preview UI

The preview must show enough information to make a safe decision.

At minimum show:

- workbook filename
- workbook checksum
- event
- event season/division
- assessment template and version
- import template and version
- configuration checksum
- workbook errors
- warnings
- total source rows
- valid player rows
- matched rows
- ambiguous rows
- unmatched rows
- invalid rows
- skipped rows
- create count
- update count
- unchanged count
- clear count
- protected manual count
- conflict count

For each player row, show:

- workbook identity
- matched canonical player
- match reason
- team/division context
- data-validation state
- source sheets and rows
- planned action
- number of metric changes
- errors
- warnings

Provide a detail view for metric-level changes showing:

- metric
- old value
- incoming raw value
- incoming normalized value
- unit
- scale
- action
- warning/conflict
- source sheet/header/cell

The confirm button must remain disabled and server-blocked until the batch is fully ready.

Invalid rows must not appear as ordinary identity-resolution rows.

Ensure responsive mobile behaviour with no horizontal overflow.

## 19. Improve bootstrap safety

Keep:

python manage.py bootstrap_2026_13u_assessment --dry-run
python manage.py bootstrap_2026_13u_assessment

Enhance the command so it reports:

- configuration objects to create
- objects already present
- conflicts
- locked objects
- metric count
- metric keys
- value types
- rating scales
- units
- unit verification state
- zero policies
- blank/update policies
- required sheets
- required headers
- import mapping version
- scoring profile version

The command must fail safely when an existing unlocked configuration conflicts with expected values.

It must never silently leave an incorrect 1–5 rating scale in place because `get_or_create()` found an existing record.

Idempotency means:

- same correct configuration produces no change
- conflicting configuration produces a clear error
- locked historical configuration is never edited
- no player data is created

Add tests for incorrect existing configuration.

## 20. Reconcile against the real workbook

Use the attached workbook for local verification only.

Do not commit it.

After the parser and bootstrap are corrected:

1. Run the bootstrap in dry-run mode.
2. Create synthetic local configuration/event data.
3. Parse the real workbook without committing player assessments.
4. Produce a local reconciliation summary.
5. Confirm actual:
   - sheet names
   - header rows
   - identity headers
   - metric headers
   - rating scales
   - zero values
   - duplicate names
   - rows appearing in only one sheet
   - formulas
   - blank values
   - annotations
   - workbook-level warnings
6. Confirm no real player data is included in source files, fixtures, snapshots, tests, logs, or prompt archives.

The final response may report aggregate counts, but do not print sensitive player-level data unless necessary for a clearly identified local QA issue.

# Migration requirements

Do not edit migration `0006`.

Create an additive migration beginning with `0007`.

Permitted migration changes include:

- new validation/warning fields
- configuration checksum fields
- compatibility foreign keys
- action/status fields
- provenance fields
- audit fields
- indexes and constraints
- safe nullable fields followed by service validation

Do not:

- alter existing evaluation tables
- rewrite observations
- modify evaluation response validation
- delete assessment records
- perform workbook-specific player data migrations
- run bootstrap configuration automatically in a migration

Running `migrate` must not create player assessments or import configuration data.

# Admin safety

Review all new Django admin registrations.

When the feature flag is disabled:

- assessment models should be hidden from ordinary admin navigation where practical
- direct admin URLs must remain staff/superuser protected
- disabling the feature must not interfere with unrelated admin areas

For committed or locked assessment objects:

- use readonly fields
- block semantic changes
- block unsafe additions
- block unsafe deletion
- do not rely only on HTML readonly controls
- enforce the same rules at model/service level

Do not expose raw player workbook JSON unnecessarily in list pages.

# Required test coverage

Expand `analytics/tests/test_assessment_imports.py` or split it into focused test modules.

Use only synthetic workbooks and fake players in committed tests.

Do not commit the real workbook.

At minimum test:

## Feature flag and permissions

- all assessment routes return 404 when disabled
- navigation is hidden when disabled
- player profile does not query/show assessments when disabled
- non-staff access is denied when enabled
- staff access works when enabled
- existing evaluation pages work with the flag off
- existing evaluation pages work with the flag on

## Workbook validation

- empty workbook
- no parsed player rows
- missing required sheet
- missing optional sheet
- missing header row
- missing identity column
- missing required metric header
- unexpected column
- malformed XLSX
- wrong file extension
- oversized upload
- too many rows
- too many columns

## Rating and numeric validation

- correct 1–3 rating
- zero rating rejected
- decimal rating rejected
- rating above 3 rejected
- invalid numeric text
- min/max numeric range
- raw invalid value retained in provenance

## Zero and blank policies

- allow zero
- zero as missing
- zero warning
- zero error
- blank preserve
- blank clear
- blank required error

## Matching

- source identifier with source namespace
- selected-season exact name
- selected-division exact name
- preferred/display name
- alias
- unique global exact name
- duplicate canonical names
- unmatched player
- no auto-create
- no fuzzy auto-commit

## Duplicate row handling

- one player across two component sheets
- duplicate row in one sheet
- conflicting duplicate values
- normalization collision

## Preview and commit

- preview creates no `PlayerAssessment`
- preview creates no `AssessmentValue`
- workbook errors block commit
- row errors block commit
- unresolved identity blocks commit
- invalid row cannot become valid only by choosing a player
- warning acknowledgement required
- stale acknowledgement rejected
- commit is atomic
- failure midway rolls back all player-assessment changes
- failed batch persistence behaves as designed

## Re-import

- first import creates
- identical re-import marks unchanged
- changed imported value marks update
- blank with clear policy clears old imported value
- blank with preserve policy preserves
- removed mapping metric does not silently delete
- duplicate workbook checksum warning
- no duplicate player assessment
- timestamps do not change for unchanged values where practical

## Manual overrides

- imported value can be explicitly corrected through approved service
- correction records actor/reason/old/new
- same incoming value is preserved
- different incoming value is blocked/protected
- blank incoming value does not clear manual override
- explicit preserve resolution works
- workbook cannot silently replace manual correction

## Immutability

- used template cannot be changed
- used template cannot receive a new metric
- used template metric cannot be changed
- used template metric cannot be deleted
- used import template cannot change
- used scoring profile cannot change
- used event cannot change template or season
- committed player assessment cannot change player/event
- committed values cannot be directly deleted or semantically edited
- safe lifecycle fields remain usable where intended

## Compatibility

- mapping for wrong assessment template is rejected
- scoring profile compatibility is validated
- frozen batch config remains unchanged if live mapping changes

## Bootstrap

- dry-run writes nothing
- first run creates correct configuration
- second run is idempotent
- ratings are 1–3
- conflicting pre-existing configuration is detected
- locked configuration is never rewritten
- no player data is created

# Regression verification

Run the complete existing suite with the feature disabled:

DJANGO_SECRET_KEY=test ANALYTICS_ASSESSMENTS_ENABLED=false python manage.py test

Run the complete existing suite with the feature enabled:

DJANGO_SECRET_KEY=test ANALYTICS_ASSESSMENTS_ENABLED=true python manage.py test

Also run:

DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations --check
DJANGO_SECRET_KEY=test python manage.py migrate --plan
git diff --check

Run project-configured Ruff, Black, and isort checks on every changed Python file.

Run focused tests first, then the full suite.

Do not declare success unless all tests pass in both feature-flag states.

# Production deployment policy

Do not deploy from this task.

In the final response, provide reviewed deployment instructions for a later controlled production rollout.

The intended rollout must remain:

## Stage 1: backup and deploy disabled

- record current commit
- back up `db.sqlite3`
- archive media
- pull corrected commits
- install updated requirements
- keep:

  ANALYTICS_ASSESSMENTS_ENABLED=false

- run checks
- review migration plan
- apply migrations
- collect static files if changed
- restart Gunicorn
- verify all current evaluation workflows
- confirm no assessment navigation is visible

## Stage 2: bootstrap configuration

- run bootstrap with `--dry-run`
- review every scale, unit, zero policy, and blank policy
- run bootstrap normally only after review
- do not import player data

## Stage 3: enable staff-only feature

- enable flag
- restart service
- confirm staff-only access
- create/select the event
- upload workbook
- review every match, warning, zero transformation, unit status, and planned action
- confirm preview has created no player-assessment records

## Stage 4: controlled import

- take a second database backup
- confirm the import
- reconcile database aggregates against workbook aggregates
- inspect representative player records
- keep feature staff-only

# Rollback policy

Immediate visual rollback must remain:

- set `ANALYTICS_ASSESSMENTS_ENABLED=false`
- restart Gunicorn

Because migrations are additive, disabling the feature should restore prior visible behaviour.

Do not recommend reversing assessment migrations after production assessment data exists.

Document a separate destructive rollback plan only if explicitly requested later.

# Documentation updates

Update:

- `docs/analytics/architecture/11_assessments.md`
- `docs/USER_MANUAL.md`
- `docs/deployment/RUNBOOK.md`
- relevant architecture indexes
- relevant README environment-variable documentation

Document:

- corrected 1–3 scale
- workbook-level versus row-level validation
- required sheets and headers
- zero policies
- blank/update policies
- unit verification
- compatibility relationships
- frozen batch configuration
- duplicate-row handling
- deterministic re-import
- manual correction and protection
- warning acknowledgement
- historical immutability
- failed-batch behaviour
- upload limits
- 2027 template/mapping version workflow
- why assessment data remains separate from evaluations

# Suggested commits

Implementation commit:

Harden assessment workbook imports

Prompt archive commit:

Archive assessment import hardening prompt

Use more than one implementation commit only if there is a clear, reviewable reason.

# Final report

When finished, provide:

1. Repository areas reviewed.
2. Defects confirmed from the previous implementation.
3. Final fixes made.
4. New migration name and operations.
5. Corrected 2026 rating scales.
6. Verified and unverified units.
7. Zero-value policies.
8. Blank/re-import policies.
9. Workbook-level validation behaviour.
10. Row-level validation behaviour.
11. Duplicate-row behaviour.
12. Player matching order.
13. Template compatibility enforcement.
14. Frozen configuration behaviour.
15. Re-import diff behaviour.
16. Manual-override behaviour.
17. Historical immutability protections.
18. Admin protections.
19. Upload/resource limits.
20. Real workbook aggregate QA results.
21. Tests added.
22. Full test results with feature flag off and on.
23. Ruff, Black, isort, check, migration-plan, and diff-check results.
24. Confirmation that existing evaluation calculations and workflows were not changed.
25. Confirmation that no workbook or real player data was committed.
26. Production deployment instructions.
27. Rollback instructions.
28. Commit hashes.
29. Remaining limitations.

# Final acceptance standard

The subsystem is not ready merely because a valid workbook can be imported.

It is ready only when:

- invalid or empty workbooks cannot commit
- required structure is enforced
- 2026 ratings retain their true 1–3 scale
- units are not guessed
- zero and blank handling are explicit
- re-imports cannot leave stale values silently
- manual corrections cannot be overwritten silently
- historical templates and events cannot be reinterpreted
- all commits are atomic
- all assessment routes remain hidden when disabled
- all existing production workflows pass unchanged
- the real workbook can be previewed safely without committing player data
```

## Implementation Commit

17c546b Harden assessment workbook imports

## Commit Diff

```diff
diff --git a/README.md b/README.md
index 678c6f2..72a19c2 100644
--- a/README.md
+++ b/README.md
@@ -160,6 +160,8 @@ Key environment variables:
 - `DJANGO_DEBUG` defaults to false.
 - `COACH_IMPORT_DEFAULT_PASSWORD` is required before creating new coach accounts through coach import.
 - `ANALYTICS_ASSESSMENTS_ENABLED` defaults to false. Set to `true` only after assessment templates/events have been configured and staff are ready to import assessment workbooks.
+- `ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES` defaults to `10485760` (10 MiB) and may be lowered for assessment workbook uploads.
+- `ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES` defaults to `52428800` (50 MiB) and caps expanded `.xlsx` archive content.
 - `DJANGO_ALLOWED_HOSTS` defaults to `localhost,127.0.0.1`.
 - `DJANGO_STATIC_ROOT` defaults to `BASE_DIR / "staticfiles"`.
 - `DJANGO_MEDIA_ROOT` defaults to `BASE_DIR / "media"`.
diff --git a/analytics/admin.py b/analytics/admin.py
index 2d3abd6..5a7552c 100644
--- a/analytics/admin.py
+++ b/analytics/admin.py
@@ -10,6 +10,7 @@ from analytics.models import (
     AssessmentTemplate,
     AssessmentTemplateMetric,
     AssessmentValue,
+    AssessmentValueCorrection,
     EvaluationCycle,
     EvaluatorRole,
     Observation,
@@ -20,12 +21,20 @@ from analytics.models import (
     ObservationType,
     PlayerAssessment,
 )
+from analytics.services.assessment_feature import assessments_enabled


 class TimeStampedAdmin(admin.ModelAdmin):
     readonly_fields = ("created_at", "updated_at")


+class AssessmentFeatureAdminMixin:
+    def get_model_perms(self, request):
+        if not assessments_enabled():
+            return {}
+        return super().get_model_perms(request)
+
+
 @admin.register(EvaluationCycle)
 class EvaluationCycleAdmin(TimeStampedAdmin):
     list_display = (
@@ -201,11 +210,32 @@ class ObservationResponseAdmin(TimeStampedAdmin):


 @admin.register(AssessmentMetricDefinition)
-class AssessmentMetricDefinitionAdmin(TimeStampedAdmin):
+class AssessmentMetricDefinitionAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
     list_display = ("key", "name", "default_value_type", "default_unit", "is_active")
     list_filter = ("default_value_type", "is_active")
     search_fields = ("key", "name")

+    def get_readonly_fields(self, request, obj=None):
+        fields = list(super().get_readonly_fields(request, obj))
+        if obj and obj.has_historical_use():
+            fields.extend(
+                [
+                    "key",
+                    "name",
+                    "description",
+                    "default_value_type",
+                    "default_unit",
+                    "metadata",
+                ]
+            )
+        return fields
+
+    def has_delete_permission(self, request, obj=None):
+        return bool(
+            super().has_delete_permission(request, obj)
+            and not (obj and obj.has_historical_use())
+        )
+

 class AssessmentTemplateMetricInline(admin.TabularInline):
     model = AssessmentTemplateMetric
@@ -222,17 +252,50 @@ class AssessmentTemplateMetricInline(admin.TabularInline):
         "direction",
     )

+    def has_add_permission(self, request, obj=None):
+        return bool(obj and not obj.is_locked and not obj.has_historical_use())
+
+    def has_delete_permission(self, request, obj=None):
+        return bool(obj and not obj.is_locked and not obj.has_historical_use())
+
+    def get_readonly_fields(self, request, obj=None):
+        if obj and (obj.is_locked or obj.has_historical_use()):
+            return self.fields
+        return ()
+

 @admin.register(AssessmentTemplate)
-class AssessmentTemplateAdmin(TimeStampedAdmin):
+class AssessmentTemplateAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
     list_display = ("name", "key", "version", "is_active", "is_locked")
     list_filter = ("is_active", "is_locked")
     search_fields = ("key", "name")
     inlines = [AssessmentTemplateMetricInline]

+    def get_readonly_fields(self, request, obj=None):
+        fields = list(super().get_readonly_fields(request, obj))
+        if obj and (obj.is_locked or obj.has_historical_use()):
+            fields.extend(
+                [
+                    "key",
+                    "name",
+                    "version",
+                    "description",
+                    "effective_from",
+                    "metadata",
+                    "is_locked",
+                ]
+            )
+        return fields
+
+    def has_delete_permission(self, request, obj=None):
+        return bool(
+            super().has_delete_permission(request, obj)
+            and not (obj and (obj.is_locked or obj.has_historical_use()))
+        )
+

 @admin.register(AssessmentTemplateMetric)
-class AssessmentTemplateMetricAdmin(TimeStampedAdmin):
+class AssessmentTemplateMetricAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
     list_display = (
         "display_name",
         "template",
@@ -246,30 +309,117 @@ class AssessmentTemplateMetricAdmin(TimeStampedAdmin):
     search_fields = ("display_name", "metric__key", "metric__name", "template__name")
     autocomplete_fields = ("template", "metric")

+    def get_readonly_fields(self, request, obj=None):
+        fields = list(super().get_readonly_fields(request, obj))
+        if obj and (obj.template.is_locked or obj.template.has_historical_use()):
+            fields.extend(
+                field.name for field in obj._meta.fields if field.name not in fields
+            )
+        return fields
+
+    def has_delete_permission(self, request, obj=None):
+        return bool(
+            super().has_delete_permission(request, obj)
+            and not (
+                obj and (obj.template.is_locked or obj.template.has_historical_use())
+            )
+        )
+

 @admin.register(AssessmentScoringProfile)
-class AssessmentScoringProfileAdmin(TimeStampedAdmin):
+class AssessmentScoringProfileAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
     list_display = ("name", "key", "version", "is_active", "is_locked")
     list_filter = ("is_active", "is_locked")
     search_fields = ("key", "name")
+    autocomplete_fields = ("assessment_template",)
+
+    def get_readonly_fields(self, request, obj=None):
+        fields = list(super().get_readonly_fields(request, obj))
+        if obj and (obj.is_locked or obj.has_committed_assessments()):
+            fields.extend(
+                [
+                    "key",
+                    "name",
+                    "version",
+                    "description",
+                    "assessment_template",
+                    "config",
+                    "metadata",
+                    "is_locked",
+                ]
+            )
+        return fields
+
+    def has_delete_permission(self, request, obj=None):
+        return bool(
+            super().has_delete_permission(request, obj)
+            and not (obj and (obj.is_locked or obj.has_committed_assessments()))
+        )


 @admin.register(AssessmentImportTemplate)
-class AssessmentImportTemplateAdmin(TimeStampedAdmin):
+class AssessmentImportTemplateAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
     list_display = ("name", "key", "version", "is_active", "is_locked")
     list_filter = ("is_active", "is_locked")
     search_fields = ("key", "name")
-    readonly_fields = TimeStampedAdmin.readonly_fields + ("config", "metadata")
+    autocomplete_fields = ("assessment_template",)
+
+    def get_readonly_fields(self, request, obj=None):
+        fields = list(super().get_readonly_fields(request, obj))
+        if obj and (obj.is_locked or obj.has_committed_imports()):
+            fields.extend(
+                [
+                    "key",
+                    "name",
+                    "version",
+                    "description",
+                    "assessment_template",
+                    "config",
+                    "metadata",
+                    "is_locked",
+                ]
+            )
+        return fields
+
+    def has_delete_permission(self, request, obj=None):
+        return bool(
+            super().has_delete_permission(request, obj)
+            and not (obj and (obj.is_locked or obj.has_committed_imports()))
+        )


 @admin.register(AssessmentEvent)
-class AssessmentEventAdmin(TimeStampedAdmin):
+class AssessmentEventAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
     list_display = ("name", "season", "division", "template", "is_active")
     list_filter = ("season", "division", "is_active", "template")
     search_fields = ("name", "slug", "season__name", "division")
     autocomplete_fields = ("template", "scoring_profile")
     prepopulated_fields = {"slug": ("name",)}

+    def get_readonly_fields(self, request, obj=None):
+        fields = list(super().get_readonly_fields(request, obj))
+        if obj and obj.has_historical_use():
+            fields.extend(
+                [
+                    "name",
+                    "slug",
+                    "season",
+                    "division",
+                    "starts_on",
+                    "ends_on",
+                    "template",
+                    "scoring_profile",
+                    "metadata",
+                ]
+            )
+        return fields
+
+    def has_delete_permission(self, request, obj=None):
+        return bool(
+            super().has_delete_permission(request, obj)
+            and not (obj and obj.has_historical_use())
+        )
+

 class AssessmentValueInline(admin.TabularInline):
     model = AssessmentValue
@@ -299,16 +449,38 @@ class AssessmentValueInline(admin.TabularInline):


 @admin.register(PlayerAssessment)
-class PlayerAssessmentAdmin(TimeStampedAdmin):
+class PlayerAssessmentAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
     list_display = ("player", "event", "status", "roster_membership", "import_batch")
     list_filter = ("event", "status", "event__season")
     search_fields = ("player__first_name", "player__last_name", "event__name")
     autocomplete_fields = ("player", "event", "roster_membership", "import_batch")
     inlines = [AssessmentValueInline]

+    def get_readonly_fields(self, request, obj=None):
+        fields = list(super().get_readonly_fields(request, obj))
+        if obj and obj.status == "committed":
+            fields.extend(
+                [
+                    "player",
+                    "event",
+                    "roster_membership",
+                    "import_batch",
+                    "source_row_key",
+                    "status",
+                    "metadata",
+                ]
+            )
+        return fields
+
+    def has_delete_permission(self, request, obj=None):
+        return bool(
+            super().has_delete_permission(request, obj)
+            and not (obj and obj.status == "committed")
+        )
+

 @admin.register(AssessmentValue)
-class AssessmentValueAdmin(TimeStampedAdmin):
+class AssessmentValueAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
     list_display = (
         "player_assessment",
         "template_metric",
@@ -325,6 +497,20 @@ class AssessmentValueAdmin(TimeStampedAdmin):
     )
     autocomplete_fields = ("player_assessment", "template_metric", "import_row")

+    def get_readonly_fields(self, request, obj=None):
+        fields = list(super().get_readonly_fields(request, obj))
+        if obj and obj.player_assessment.status == "committed":
+            fields.extend(
+                field.name for field in obj._meta.fields if field.name not in fields
+            )
+        return fields
+
+    def has_delete_permission(self, request, obj=None):
+        return bool(
+            super().has_delete_permission(request, obj)
+            and not (obj and obj.player_assessment.status == "committed")
+        )
+

 class AssessmentImportRowInline(admin.TabularInline):
     model = AssessmentImportRow
@@ -339,8 +525,13 @@ class AssessmentImportRowInline(admin.TabularInline):
         "roster_membership",
         "action",
         "status",
+        "match_status",
+        "validation_status",
+        "conflict_status",
         "errors",
+        "warnings",
         "values_snapshot",
+        "metric_changes",
         "raw_row",
         "metadata",
         "created_at",
@@ -353,7 +544,7 @@ class AssessmentImportRowInline(admin.TabularInline):


 @admin.register(AssessmentImportBatch)
-class AssessmentImportBatchAdmin(TimeStampedAdmin):
+class AssessmentImportBatchAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
     list_display = (
         "original_filename",
         "event",
@@ -364,27 +555,86 @@ class AssessmentImportBatchAdmin(TimeStampedAdmin):
     )
     list_filter = ("status", "event", "event__season")
     search_fields = ("original_filename", "workbook_sha256", "event__name")
-    autocomplete_fields = ("event", "import_template", "uploaded_by")
     readonly_fields = TimeStampedAdmin.readonly_fields + (
+        "event",
+        "import_template",
+        "uploaded_by",
+        "original_filename",
+        "status",
         "workbook_sha256",
         "preview_snapshot",
         "config_snapshot",
+        "config_checksum",
+        "validation_errors",
+        "validation_warnings",
+        "required_warning_codes",
+        "preview_version",
+        "acknowledgement_token",
+        "warnings_acknowledged_at",
+        "warnings_acknowledged_by",
         "import_summary",
         "committed_at",
         "metadata",
     )
     inlines = [AssessmentImportRowInline]

+    def has_add_permission(self, request):
+        return False
+
+    def has_delete_permission(self, request, obj=None):
+        return bool(
+            super().has_delete_permission(request, obj)
+            and not (obj and obj.status == "committed")
+        )
+

 @admin.register(AssessmentImportRow)
-class AssessmentImportRowAdmin(TimeStampedAdmin):
+class AssessmentImportRowAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
     list_display = ("batch", "source_sheet", "source_row", "raw_identity", "status")
     list_filter = ("status", "source_sheet", "batch__event")
     search_fields = ("raw_identity", "batch__original_filename", "batch__event__name")
-    autocomplete_fields = ("batch", "player", "roster_membership")
     readonly_fields = TimeStampedAdmin.readonly_fields + (
+        "batch",
+        "row_key",
+        "source_sheet",
+        "source_row",
+        "raw_identity",
+        "player",
+        "roster_membership",
+        "action",
+        "status",
+        "match_status",
+        "validation_status",
+        "conflict_status",
         "raw_row",
         "values_snapshot",
+        "metric_changes",
         "errors",
+        "warnings",
         "metadata",
     )
+
+    def has_add_permission(self, request):
+        return False
+
+    def has_delete_permission(self, request, obj=None):
+        return False
+
+
+@admin.register(AssessmentValueCorrection)
+class AssessmentValueCorrectionAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
+    list_display = ("assessment_value", "actor", "created_at")
+    search_fields = (
+        "assessment_value__player_assessment__player__first_name",
+        "assessment_value__player_assessment__player__last_name",
+        "reason",
+    )
+    readonly_fields = tuple(
+        field.name for field in AssessmentValueCorrection._meta.fields
+    )
+
+    def has_add_permission(self, request):
+        return False
+
+    def has_delete_permission(self, request, obj=None):
+        return False
diff --git a/analytics/forms.py b/analytics/forms.py
index f68ae3c..15d0fa3 100644
--- a/analytics/forms.py
+++ b/analytics/forms.py
@@ -1,4 +1,5 @@
 from django import forms
+from django.conf import settings

 from analytics.models import (
     AssessmentEvent,
@@ -130,17 +131,37 @@ class AssessmentImportUploadForm(forms.Form):
             .order_by("-starts_on", "name")
         )
         self.fields["import_template"].queryset = (
-            AssessmentImportTemplate.objects.filter(is_active=True).order_by(
-                "key", "-version"
+            AssessmentImportTemplate.objects.filter(
+                is_active=True,
+                assessment_template__events__is_active=True,
             )
+            .select_related("assessment_template")
+            .distinct()
+            .order_by("key", "-version")
         )

     def clean_workbook(self):
         workbook = self.cleaned_data["workbook"]
         if not workbook.name.lower().endswith(".xlsx"):
             raise forms.ValidationError("Upload an .xlsx workbook.")
+        maximum = settings.ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES
+        if workbook.size > maximum:
+            raise forms.ValidationError(
+                f"Workbook exceeds the configured {maximum}-byte upload limit."
+            )
         return workbook

+    def clean(self):
+        cleaned_data = super().clean()
+        event = cleaned_data.get("event")
+        import_template = cleaned_data.get("import_template")
+        if event and import_template:
+            if import_template.assessment_template_id != event.template_id:
+                raise forms.ValidationError(
+                    "Import template is not compatible with the selected assessment event."
+                )
+        return cleaned_data
+

 class AssessmentImportRowResolutionForm(forms.Form):
     player = forms.ModelChoiceField(
diff --git a/analytics/management/commands/bootstrap_2026_13u_assessment.py b/analytics/management/commands/bootstrap_2026_13u_assessment.py
index 28caeb7..718eba0 100644
--- a/analytics/management/commands/bootstrap_2026_13u_assessment.py
+++ b/analytics/management/commands/bootstrap_2026_13u_assessment.py
@@ -1,3 +1,4 @@
+from django.core.exceptions import ValidationError
 from django.core.management.base import BaseCommand

 from analytics.services.assessment_import_service import (
@@ -16,12 +17,55 @@ class Command(BaseCommand):
         )

     def handle(self, *args, **options):
-        plan = ensure_2026_13u_assessment_configuration(
-            dry_run=options.get("dry_run", False)
-        )
+        try:
+            plan = ensure_2026_13u_assessment_configuration(
+                dry_run=options.get("dry_run", False)
+            )
+        except ValidationError as exc:
+            self.stderr.write(self.style.ERROR(str(exc)))
+            raise
         mode = "Dry run" if options.get("dry_run", False) else "Configured"
         self.stdout.write(
             self.style.SUCCESS(
                 f"{mode} 2026 13U assessment template with {len(plan['metrics'])} metrics."
             )
         )
+        self.stdout.write(
+            f"Required sheets: {', '.join(plan['required_sheets'])}; "
+            f"optional sheets: {', '.join(plan['optional_sheets']) or 'none'}"
+        )
+        for sheet in plan["sheets"]:
+            self.stdout.write(
+                f"- {sheet['name']}: header row={sheet['header_row']}; "
+                f"identity={sheet['identity_column']}; required headers="
+                f"{', '.join(sheet['required_headers'])}"
+            )
+        self.stdout.write(
+            "Import mapping: "
+            f"{plan['import_template']['key']} v{plan['import_template']['version']} "
+            f"({plan['import_template']['config_checksum']})"
+        )
+        self.stdout.write(
+            "Scoring profile: "
+            f"{plan['scoring_profile']['key']} v{plan['scoring_profile']['version']}"
+        )
+        for state in plan.get("states", []):
+            self.stdout.write(
+                f"{state['object']}: {state['state']}"
+                f"{' (locked)' if state['locked'] else ''}"
+            )
+            for field_name, conflict in state.get("conflicts", {}).items():
+                self.stdout.write(
+                    self.style.WARNING(
+                        f"  conflict {field_name}: actual={conflict['actual']!r}; "
+                        f"expected={conflict['expected']!r}"
+                    )
+                )
+        for metric in plan["metrics"]:
+            scale = metric["rating_scale"] or "n/a"
+            unit = metric["unit"] or "not configured"
+            self.stdout.write(
+                f"- {metric['key']}: type={metric['value_type']}; scale={scale}; "
+                f"unit={unit}; unit_status={metric['unit_status']}; "
+                f"zero={metric['zero_policy']}; blank={metric['blank_policy']}"
+            )
diff --git a/analytics/migrations/0007_assessmentimportbatch_acknowledgement_token_and_more.py b/analytics/migrations/0007_assessmentimportbatch_acknowledgement_token_and_more.py
new file mode 100644
index 0000000..a53db75
--- /dev/null
+++ b/analytics/migrations/0007_assessmentimportbatch_acknowledgement_token_and_more.py
@@ -0,0 +1,208 @@
+# Generated by Django 4.2.30 on 2026-07-31 20:42
+
+import django.db.models.deletion
+from django.conf import settings
+from django.db import migrations, models
+
+
+class Migration(migrations.Migration):
+
+    dependencies = [
+        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
+        ("players", "0003_playerimportbatch_season_and_more"),
+        ("analytics", "0006_assessmentevent_assessmentimportbatch_and_more"),
+    ]
+
+    operations = [
+        migrations.AddField(
+            model_name="assessmentimportbatch",
+            name="acknowledgement_token",
+            field=models.CharField(blank=True, max_length=64),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportbatch",
+            name="config_checksum",
+            field=models.CharField(blank=True, max_length=64),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportbatch",
+            name="preview_version",
+            field=models.PositiveIntegerField(default=1),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportbatch",
+            name="required_warning_codes",
+            field=models.JSONField(blank=True, default=list),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportbatch",
+            name="validation_errors",
+            field=models.JSONField(blank=True, default=list),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportbatch",
+            name="validation_warnings",
+            field=models.JSONField(blank=True, default=list),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportbatch",
+            name="warnings_acknowledged_at",
+            field=models.DateTimeField(blank=True, null=True),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportbatch",
+            name="warnings_acknowledged_by",
+            field=models.ForeignKey(
+                blank=True,
+                null=True,
+                on_delete=django.db.models.deletion.SET_NULL,
+                related_name="acknowledged_assessment_import_batches",
+                to=settings.AUTH_USER_MODEL,
+            ),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportrow",
+            name="conflict_status",
+            field=models.CharField(
+                choices=[
+                    ("none", "No conflict"),
+                    ("unresolved", "Unresolved"),
+                    ("resolved", "Resolved"),
+                ],
+                default="none",
+                max_length=40,
+            ),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportrow",
+            name="match_status",
+            field=models.CharField(
+                choices=[
+                    ("matched", "Matched"),
+                    ("unmatched", "Unmatched"),
+                    ("ambiguous", "Ambiguous"),
+                ],
+                default="unmatched",
+                max_length=40,
+            ),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportrow",
+            name="metric_changes",
+            field=models.JSONField(blank=True, default=list),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportrow",
+            name="validation_status",
+            field=models.CharField(
+                choices=[("valid", "Valid"), ("invalid", "Invalid")],
+                default="valid",
+                max_length=40,
+            ),
+        ),
+        migrations.AddField(
+            model_name="assessmentimportrow",
+            name="warnings",
+            field=models.JSONField(blank=True, default=list),
+        ),
+        migrations.AddField(
+            model_name="assessmentimporttemplate",
+            name="assessment_template",
+            field=models.ForeignKey(
+                blank=True,
+                null=True,
+                on_delete=django.db.models.deletion.PROTECT,
+                related_name="import_templates",
+                to="analytics.assessmenttemplate",
+            ),
+        ),
+        migrations.AddField(
+            model_name="assessmentscoringprofile",
+            name="assessment_template",
+            field=models.ForeignKey(
+                blank=True,
+                null=True,
+                on_delete=django.db.models.deletion.PROTECT,
+                related_name="scoring_profiles",
+                to="analytics.assessmenttemplate",
+            ),
+        ),
+        migrations.AlterField(
+            model_name="assessmentvalue",
+            name="import_row",
+            field=models.ForeignKey(
+                blank=True,
+                null=True,
+                on_delete=django.db.models.deletion.PROTECT,
+                related_name="assessment_values",
+                to="analytics.assessmentimportrow",
+            ),
+        ),
+        migrations.AlterField(
+            model_name="playerassessment",
+            name="import_batch",
+            field=models.ForeignKey(
+                blank=True,
+                null=True,
+                on_delete=django.db.models.deletion.PROTECT,
+                related_name="player_assessments",
+                to="analytics.assessmentimportbatch",
+            ),
+        ),
+        migrations.AlterField(
+            model_name="playerassessment",
+            name="player",
+            field=models.ForeignKey(
+                on_delete=django.db.models.deletion.PROTECT,
+                related_name="assessment_records",
+                to="players.player",
+            ),
+        ),
+        migrations.CreateModel(
+            name="AssessmentValueCorrection",
+            fields=[
+                (
+                    "id",
+                    models.BigAutoField(
+                        auto_created=True,
+                        primary_key=True,
+                        serialize=False,
+                        verbose_name="ID",
+                    ),
+                ),
+                ("created_at", models.DateTimeField(auto_now_add=True)),
+                ("updated_at", models.DateTimeField(auto_now=True)),
+                ("reason", models.TextField()),
+                ("previous_snapshot", models.JSONField(default=dict)),
+                ("new_snapshot", models.JSONField(default=dict)),
+                ("provenance", models.JSONField(blank=True, default=dict)),
+                (
+                    "actor",
+                    models.ForeignKey(
+                        blank=True,
+                        null=True,
+                        on_delete=django.db.models.deletion.SET_NULL,
+                        related_name="assessment_value_corrections",
+                        to=settings.AUTH_USER_MODEL,
+                    ),
+                ),
+                (
+                    "assessment_value",
+                    models.ForeignKey(
+                        on_delete=django.db.models.deletion.PROTECT,
+                        related_name="corrections",
+                        to="analytics.assessmentvalue",
+                    ),
+                ),
+            ],
+            options={
+                "ordering": ["-created_at", "-id"],
+                "indexes": [
+                    models.Index(
+                        fields=["assessment_value", "-created_at"],
+                        name="analytics_a_assessm_24e7ed_idx",
+                    )
+                ],
+            },
+        ),
+    ]
diff --git a/analytics/models.py b/analytics/models.py
index c538d29..1e5fdd0 100644
--- a/analytics/models.py
+++ b/analytics/models.py
@@ -115,6 +115,34 @@ ASSESSMENT_IMPORT_ROW_STATUS_CHOICES = [
     (ASSESSMENT_IMPORT_ROW_COMMITTED, "Committed"),
 ]

+ASSESSMENT_MATCH_MATCHED = "matched"
+ASSESSMENT_MATCH_UNMATCHED = "unmatched"
+ASSESSMENT_MATCH_AMBIGUOUS = "ambiguous"
+
+ASSESSMENT_MATCH_STATUS_CHOICES = [
+    (ASSESSMENT_MATCH_MATCHED, "Matched"),
+    (ASSESSMENT_MATCH_UNMATCHED, "Unmatched"),
+    (ASSESSMENT_MATCH_AMBIGUOUS, "Ambiguous"),
+]
+
+ASSESSMENT_VALIDATION_VALID = "valid"
+ASSESSMENT_VALIDATION_INVALID = "invalid"
+
+ASSESSMENT_VALIDATION_STATUS_CHOICES = [
+    (ASSESSMENT_VALIDATION_VALID, "Valid"),
+    (ASSESSMENT_VALIDATION_INVALID, "Invalid"),
+]
+
+ASSESSMENT_CONFLICT_NONE = "none"
+ASSESSMENT_CONFLICT_UNRESOLVED = "unresolved"
+ASSESSMENT_CONFLICT_RESOLVED = "resolved"
+
+ASSESSMENT_CONFLICT_STATUS_CHOICES = [
+    (ASSESSMENT_CONFLICT_NONE, "No conflict"),
+    (ASSESSMENT_CONFLICT_UNRESOLVED, "Unresolved"),
+    (ASSESSMENT_CONFLICT_RESOLVED, "Resolved"),
+]
+
 ASSESSMENT_VALUE_SOURCE_IMPORTED = "imported"
 ASSESSMENT_VALUE_SOURCE_MANUAL = "manual"
 ASSESSMENT_VALUE_SOURCE_MANUAL_CORRECTED = "manual_corrected"
@@ -599,6 +627,40 @@ class AssessmentMetricDefinition(TimeStampedModel):
             models.Index(fields=["is_active", "key"]),
         ]

+    def has_historical_use(self) -> bool:
+        if not self.pk:
+            return False
+        return self.template_metrics.filter(
+            Q(template__events__player_assessments__status=ASSESSMENT_STATUS_COMMITTED)
+            | Q(
+                template__events__import_batches__status=ASSESSMENT_IMPORT_STATUS_COMMITTED
+            )
+        ).exists()
+
+    def save(self, *args, **kwargs):
+        if self.pk and self.has_historical_use():
+            original = AssessmentMetricDefinition.objects.get(pk=self.pk)
+            for field_name in [
+                "key",
+                "name",
+                "description",
+                "default_value_type",
+                "default_unit",
+                "metadata",
+            ]:
+                if getattr(original, field_name) != getattr(self, field_name):
+                    raise ValidationError(
+                        {
+                            field_name: "Metric meaning cannot change after historical use."
+                        }
+                    )
+        super().save(*args, **kwargs)
+
+    def delete(self, *args, **kwargs):
+        if self.has_historical_use():
+            raise ValidationError("Metrics with historical use cannot be deleted.")
+        return super().delete(*args, **kwargs)
+
     def __str__(self) -> str:
         return self.name

@@ -627,26 +689,48 @@ class AssessmentTemplate(TimeStampedModel):
             models.Index(fields=["is_active", "key"]),
         ]

-    def has_committed_assessments(self) -> bool:
+    def has_historical_use(self) -> bool:
         if not self.pk:
             return False
-        return PlayerAssessment.objects.filter(
-            event__template_id=self.pk,
-            status=ASSESSMENT_STATUS_COMMITTED,
-        ).exists()
+        return (
+            PlayerAssessment.objects.filter(
+                event__template_id=self.pk,
+                status=ASSESSMENT_STATUS_COMMITTED,
+            ).exists()
+            or AssessmentImportBatch.objects.filter(
+                event__template_id=self.pk,
+                status=ASSESSMENT_IMPORT_STATUS_COMMITTED,
+            ).exists()
+        )
+
+    def has_committed_assessments(self) -> bool:
+        return self.has_historical_use()

     def save(self, *args, **kwargs):
-        if self.pk and self.has_committed_assessments():
+        if self.pk:
             original = AssessmentTemplate.objects.get(pk=self.pk)
-            locked_fields = ["key", "version"]
-            for field_name in locked_fields:
-                if getattr(original, field_name) != getattr(self, field_name):
-                    raise ValidationError(
-                        {field_name: "Template identity cannot change after use."}
-                    )
-            self.is_locked = True
+            if original.is_locked or self.has_historical_use():
+                locked_fields = [
+                    "key",
+                    "version",
+                    "name",
+                    "description",
+                    "effective_from",
+                    "metadata",
+                ]
+                for field_name in locked_fields:
+                    if getattr(original, field_name) != getattr(self, field_name):
+                        raise ValidationError(
+                            {field_name: "Locked template identity cannot change."}
+                        )
+                self.is_locked = True
         super().save(*args, **kwargs)

+    def delete(self, *args, **kwargs):
+        if self.is_locked or self.has_historical_use():
+            raise ValidationError("Locked assessment templates cannot be deleted.")
+        return super().delete(*args, **kwargs)
+
     def __str__(self) -> str:
         return f"{self.name} v{self.version}"

@@ -719,9 +803,26 @@ class AssessmentTemplateMetric(TimeStampedModel):
             raise ValidationError(errors)

     def save(self, *args, **kwargs):
-        if self.pk and self.template.has_committed_assessments():
-            original = AssessmentTemplateMetric.objects.get(pk=self.pk)
+        original = AssessmentTemplateMetric.objects.filter(pk=self.pk).first()
+        original_template = original.template if original else None
+        template_locked = (
+            self.template.is_locked
+            or self.template.has_historical_use()
+            or bool(
+                original_template
+                and (
+                    original_template.is_locked
+                    or original_template.has_historical_use()
+                )
+            )
+        )
+        if template_locked and original is None:
+            raise ValidationError(
+                {"template": "Metrics cannot be added to a locked assessment template."}
+            )
+        if original and template_locked:
             locked_fields = [
+                "template_id",
                 "metric_id",
                 "category",
                 "display_name",
@@ -735,22 +836,39 @@ class AssessmentTemplateMetric(TimeStampedModel):
                 "rating_scale_max",
                 "direction",
                 "rubric",
+                "help_text",
+                "metadata",
             ]
             for field_name in locked_fields:
                 if getattr(original, field_name) != getattr(self, field_name):
                     raise ValidationError(
-                        {field_name: "Template metrics cannot change after use."}
+                        {field_name: "Locked template metrics cannot change."}
                     )
             self.template.is_locked = True
             self.template.save(update_fields=["is_locked", "updated_at"])
         self.full_clean()
         super().save(*args, **kwargs)

+    def delete(self, *args, **kwargs):
+        persisted = AssessmentTemplateMetric.objects.select_related("template").get(
+            pk=self.pk
+        )
+        if persisted.template.is_locked or persisted.template.has_historical_use():
+            raise ValidationError("Metrics cannot be removed from a locked template.")
+        return super().delete(*args, **kwargs)
+
     def __str__(self) -> str:
         return self.display_name


 class AssessmentScoringProfile(TimeStampedModel):
+    assessment_template = models.ForeignKey(
+        AssessmentTemplate,
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="scoring_profiles",
+    )
     key = models.SlugField(max_length=120)
     name = models.CharField(max_length=160)
     version = models.PositiveIntegerField(default=1)
@@ -776,27 +894,54 @@ class AssessmentScoringProfile(TimeStampedModel):
     def has_committed_assessments(self) -> bool:
         if not self.pk:
             return False
-        return PlayerAssessment.objects.filter(
-            event__scoring_profile_id=self.pk,
-            status=ASSESSMENT_STATUS_COMMITTED,
-        ).exists()
+        return (
+            PlayerAssessment.objects.filter(
+                event__scoring_profile_id=self.pk,
+                status=ASSESSMENT_STATUS_COMMITTED,
+            ).exists()
+            or AssessmentImportBatch.objects.filter(
+                event__scoring_profile_id=self.pk,
+                status=ASSESSMENT_IMPORT_STATUS_COMMITTED,
+            ).exists()
+        )

     def save(self, *args, **kwargs):
-        if self.pk and self.has_committed_assessments():
+        if self.pk:
             original = AssessmentScoringProfile.objects.get(pk=self.pk)
-            for field_name in ["key", "version", "config"]:
-                if getattr(original, field_name) != getattr(self, field_name):
-                    raise ValidationError(
-                        {field_name: "Scoring profile cannot change after use."}
-                    )
-            self.is_locked = True
+            if original.is_locked or self.has_committed_assessments():
+                for field_name in [
+                    "key",
+                    "version",
+                    "name",
+                    "description",
+                    "assessment_template_id",
+                    "config",
+                    "metadata",
+                ]:
+                    if getattr(original, field_name) != getattr(self, field_name):
+                        raise ValidationError(
+                            {field_name: "Locked scoring profile cannot change."}
+                        )
+                self.is_locked = True
         super().save(*args, **kwargs)

+    def delete(self, *args, **kwargs):
+        if self.is_locked or self.has_committed_assessments():
+            raise ValidationError("Locked scoring profiles cannot be deleted.")
+        return super().delete(*args, **kwargs)
+
     def __str__(self) -> str:
         return f"{self.name} v{self.version}"


 class AssessmentImportTemplate(TimeStampedModel):
+    assessment_template = models.ForeignKey(
+        AssessmentTemplate,
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="import_templates",
+    )
     key = models.SlugField(max_length=120)
     name = models.CharField(max_length=160)
     version = models.PositiveIntegerField(default=1)
@@ -827,16 +972,30 @@ class AssessmentImportTemplate(TimeStampedModel):
         ).exists()

     def save(self, *args, **kwargs):
-        if self.pk and self.has_committed_imports():
+        if self.pk:
             original = AssessmentImportTemplate.objects.get(pk=self.pk)
-            for field_name in ["key", "version", "config"]:
-                if getattr(original, field_name) != getattr(self, field_name):
-                    raise ValidationError(
-                        {field_name: "Import template cannot change after use."}
-                    )
-            self.is_locked = True
+            if original.is_locked or self.has_committed_imports():
+                for field_name in [
+                    "key",
+                    "version",
+                    "name",
+                    "description",
+                    "assessment_template_id",
+                    "config",
+                    "metadata",
+                ]:
+                    if getattr(original, field_name) != getattr(self, field_name):
+                        raise ValidationError(
+                            {field_name: "Locked import template cannot change."}
+                        )
+                self.is_locked = True
         super().save(*args, **kwargs)

+    def delete(self, *args, **kwargs):
+        if self.is_locked or self.has_committed_imports():
+            raise ValidationError("Locked import templates cannot be deleted.")
+        return super().delete(*args, **kwargs)
+
     def __str__(self) -> str:
         return f"{self.name} v{self.version}"

@@ -872,17 +1031,63 @@ class AssessmentEvent(TimeStampedModel):
         ]

     def clean(self):
+        errors = {}
         if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
-            raise ValidationError(
-                {"ends_on": "Assessment event end date cannot be before start date."}
-            )
+            errors["ends_on"] = "Assessment event end date cannot be before start date."
+        if self.scoring_profile_id:
+            compatible_template_id = self.scoring_profile.assessment_template_id
+            if not compatible_template_id:
+                errors["scoring_profile"] = (
+                    "Scoring profile must identify its compatible assessment template."
+                )
+            elif self.template_id and compatible_template_id != self.template_id:
+                errors["scoring_profile"] = (
+                    "Scoring profile is not compatible with this assessment template."
+                )
+        if errors:
+            raise ValidationError(errors)
+
+    def has_historical_use(self) -> bool:
+        if not self.pk:
+            return False
+        return (
+            self.player_assessments.filter(status=ASSESSMENT_STATUS_COMMITTED).exists()
+            or self.import_batches.filter(
+                status=ASSESSMENT_IMPORT_STATUS_COMMITTED
+            ).exists()
+        )

     def save(self, *args, **kwargs):
         if not self.slug:
             self.slug = unique_slug_for_model(self, self.name)
+        if self.pk and self.has_historical_use():
+            original = AssessmentEvent.objects.get(pk=self.pk)
+            locked_fields = [
+                "name",
+                "slug",
+                "season_id",
+                "division",
+                "starts_on",
+                "ends_on",
+                "template_id",
+                "scoring_profile_id",
+                "metadata",
+            ]
+            for field_name in locked_fields:
+                if getattr(original, field_name) != getattr(self, field_name):
+                    raise ValidationError(
+                        {
+                            field_name: "Assessment event history cannot change after use."
+                        }
+                    )
         self.full_clean()
         super().save(*args, **kwargs)

+    def delete(self, *args, **kwargs):
+        if self.has_historical_use():
+            raise ValidationError("Used assessment events cannot be deleted.")
+        return super().delete(*args, **kwargs)
+
     def __str__(self) -> str:
         return self.name

@@ -912,6 +1117,20 @@ class AssessmentImportBatch(TimeStampedModel):
     )
     preview_snapshot = models.JSONField(default=dict, blank=True)
     config_snapshot = models.JSONField(default=dict, blank=True)
+    config_checksum = models.CharField(max_length=64, blank=True)
+    validation_errors = models.JSONField(default=list, blank=True)
+    validation_warnings = models.JSONField(default=list, blank=True)
+    required_warning_codes = models.JSONField(default=list, blank=True)
+    preview_version = models.PositiveIntegerField(default=1)
+    acknowledgement_token = models.CharField(max_length=64, blank=True)
+    warnings_acknowledged_at = models.DateTimeField(null=True, blank=True)
+    warnings_acknowledged_by = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="acknowledged_assessment_import_batches",
+    )
     import_summary = models.JSONField(default=dict, blank=True)
     committed_at = models.DateTimeField(null=True, blank=True)
     metadata = models.JSONField(default=dict, blank=True)
@@ -924,13 +1143,59 @@ class AssessmentImportBatch(TimeStampedModel):
             models.Index(fields=["uploaded_by", "-created_at"]),
         ]

+    def save(self, *args, **kwargs):
+        if self.pk:
+            original = AssessmentImportBatch.objects.get(pk=self.pk)
+            frozen_fields = [
+                "event_id",
+                "import_template_id",
+                "uploaded_by_id",
+                "original_filename",
+                "workbook_sha256",
+                "config_snapshot",
+                "config_checksum",
+            ]
+            for field_name in frozen_fields:
+                if getattr(original, field_name) != getattr(self, field_name):
+                    raise ValidationError(
+                        {
+                            field_name: "Assessment import source configuration is immutable."
+                        }
+                    )
+            if original.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
+                committed_fields = [
+                    "status",
+                    "preview_snapshot",
+                    "validation_errors",
+                    "validation_warnings",
+                    "required_warning_codes",
+                    "preview_version",
+                    "acknowledgement_token",
+                    "warnings_acknowledged_at",
+                    "warnings_acknowledged_by_id",
+                    "import_summary",
+                    "committed_at",
+                    "metadata",
+                ]
+                for field_name in committed_fields:
+                    if getattr(original, field_name) != getattr(self, field_name):
+                        raise ValidationError(
+                            {field_name: "Committed assessment imports are immutable."}
+                        )
+        super().save(*args, **kwargs)
+
+    def delete(self, *args, **kwargs):
+        if self.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
+            raise ValidationError("Committed assessment imports cannot be deleted.")
+        return super().delete(*args, **kwargs)
+
     def __str__(self) -> str:
         return self.original_filename


 class PlayerAssessment(TimeStampedModel):
     player = models.ForeignKey(
-        "players.Player", on_delete=models.CASCADE, related_name="assessment_records"
+        "players.Player", on_delete=models.PROTECT, related_name="assessment_records"
     )
     event = models.ForeignKey(
         AssessmentEvent, on_delete=models.PROTECT, related_name="player_assessments"
@@ -946,7 +1211,7 @@ class PlayerAssessment(TimeStampedModel):
         AssessmentImportBatch,
         null=True,
         blank=True,
-        on_delete=models.SET_NULL,
+        on_delete=models.PROTECT,
         related_name="player_assessments",
     )
     source_row_key = models.CharField(max_length=180, blank=True)
@@ -994,9 +1259,32 @@ class PlayerAssessment(TimeStampedModel):
             raise ValidationError(errors)

     def save(self, *args, **kwargs):
+        if self.pk:
+            original = PlayerAssessment.objects.get(pk=self.pk)
+            if original.status == ASSESSMENT_STATUS_COMMITTED:
+                for field_name in [
+                    "status",
+                    "player_id",
+                    "event_id",
+                    "roster_membership_id",
+                    "import_batch_id",
+                    "source_row_key",
+                    "metadata",
+                ]:
+                    if getattr(original, field_name) != getattr(self, field_name):
+                        raise ValidationError(
+                            {
+                                field_name: "Committed assessment provenance cannot change."
+                            }
+                        )
         self.full_clean()
         super().save(*args, **kwargs)

+    def delete(self, *args, **kwargs):
+        if self.status == ASSESSMENT_STATUS_COMMITTED:
+            raise ValidationError("Committed player assessments cannot be deleted.")
+        return super().delete(*args, **kwargs)
+
     def __str__(self) -> str:
         return f"{self.event}: {self.player}"

@@ -1029,8 +1317,25 @@ class AssessmentImportRow(TimeStampedModel):
         choices=ASSESSMENT_IMPORT_ROW_STATUS_CHOICES,
         default=ASSESSMENT_IMPORT_ROW_UNMATCHED,
     )
+    match_status = models.CharField(
+        max_length=40,
+        choices=ASSESSMENT_MATCH_STATUS_CHOICES,
+        default=ASSESSMENT_MATCH_UNMATCHED,
+    )
+    validation_status = models.CharField(
+        max_length=40,
+        choices=ASSESSMENT_VALIDATION_STATUS_CHOICES,
+        default=ASSESSMENT_VALIDATION_VALID,
+    )
+    conflict_status = models.CharField(
+        max_length=40,
+        choices=ASSESSMENT_CONFLICT_STATUS_CHOICES,
+        default=ASSESSMENT_CONFLICT_NONE,
+    )
     errors = models.JSONField(default=list, blank=True)
+    warnings = models.JSONField(default=list, blank=True)
     values_snapshot = models.JSONField(default=list, blank=True)
+    metric_changes = models.JSONField(default=list, blank=True)
     raw_row = models.JSONField(default=dict, blank=True)
     metadata = models.JSONField(default=dict, blank=True)

@@ -1048,6 +1353,28 @@ class AssessmentImportRow(TimeStampedModel):
             models.Index(fields=["source_sheet", "source_row"]),
         ]

+    def save(self, *args, **kwargs):
+        original = (
+            AssessmentImportRow.objects.select_related("batch")
+            .filter(pk=self.pk)
+            .first()
+        )
+        if original and original.batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
+            for field in self._meta.fields:
+                if field.name in {"updated_at"}:
+                    continue
+                if getattr(original, field.attname) != getattr(self, field.attname):
+                    raise ValidationError(
+                        {field.name: "Committed assessment import rows are immutable."}
+                    )
+        super().save(*args, **kwargs)
+
+    def delete(self, *args, **kwargs):
+        persisted = AssessmentImportRow.objects.select_related("batch").get(pk=self.pk)
+        if persisted.batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
+            raise ValidationError("Committed assessment import rows cannot be deleted.")
+        return super().delete(*args, **kwargs)
+
     def __str__(self) -> str:
         return f"{self.batch} row {self.source_row}"

@@ -1093,7 +1420,7 @@ class AssessmentValue(TimeStampedModel):
         AssessmentImportRow,
         null=True,
         blank=True,
-        on_delete=models.SET_NULL,
+        on_delete=models.PROTECT,
         related_name="assessment_values",
     )
     metadata = models.JSONField(default=dict, blank=True)
@@ -1127,8 +1454,106 @@ class AssessmentValue(TimeStampedModel):
             raise ValidationError(errors)

     def save(self, *args, **kwargs):
+        allow_committed_change = getattr(self, "_allow_committed_change", False)
+        original = (
+            AssessmentValue.objects.select_related("player_assessment")
+            .filter(pk=self.pk)
+            .first()
+        )
+        source_is_committed = bool(
+            original
+            and original.player_assessment.status == ASSESSMENT_STATUS_COMMITTED
+        )
+        target_is_committed = bool(
+            self.player_assessment_id
+            and self.player_assessment.status == ASSESSMENT_STATUS_COMMITTED
+        )
+        if (source_is_committed or target_is_committed) and not allow_committed_change:
+            if original is None:
+                raise ValidationError(
+                    "Values cannot be added directly to a committed assessment."
+                )
+            semantic_fields = [
+                "player_assessment_id",
+                "template_metric_id",
+                "numeric_value",
+                "rating_value",
+                "rating_scale_min",
+                "rating_scale_max",
+                "text_value",
+                "choice_value",
+                "raw_value",
+                "normalized_value",
+                "unit",
+                "source_sheet",
+                "source_row",
+                "source_column",
+                "source_header",
+                "source_kind",
+                "is_imported",
+                "is_manual_override",
+                "import_row_id",
+                "metadata",
+            ]
+            for field_name in semantic_fields:
+                if getattr(original, field_name) != getattr(self, field_name):
+                    raise ValidationError(
+                        {
+                            field_name: (
+                                "Committed assessment values require an approved "
+                                "correction service."
+                            )
+                        }
+                    )
         self.full_clean()
         super().save(*args, **kwargs)

+    def delete(self, *args, **kwargs):
+        persisted = AssessmentValue.objects.select_related("player_assessment").get(
+            pk=self.pk
+        )
+        if (
+            persisted.player_assessment.status == ASSESSMENT_STATUS_COMMITTED
+            and not getattr(self, "_allow_committed_change", False)
+        ):
+            raise ValidationError(
+                "Committed assessment values cannot be deleted directly."
+            )
+        return super().delete(*args, **kwargs)
+
     def __str__(self) -> str:
         return f"{self.player_assessment} - {self.template_metric}"
+
+
+class AssessmentValueCorrection(TimeStampedModel):
+    assessment_value = models.ForeignKey(
+        AssessmentValue,
+        on_delete=models.PROTECT,
+        related_name="corrections",
+    )
+    actor = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="assessment_value_corrections",
+    )
+    reason = models.TextField()
+    previous_snapshot = models.JSONField(default=dict)
+    new_snapshot = models.JSONField(default=dict)
+    provenance = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["-created_at", "-id"]
+        indexes = [models.Index(fields=["assessment_value", "-created_at"])]
+
+    def save(self, *args, **kwargs):
+        if self.pk:
+            raise ValidationError("Assessment correction audit records are immutable.")
+        super().save(*args, **kwargs)
+
+    def delete(self, *args, **kwargs):
+        raise ValidationError("Assessment correction audit records cannot be deleted.")
+
+    def __str__(self) -> str:
+        return f"Correction for {self.assessment_value}"
diff --git a/analytics/services/assessment_import_service.py b/analytics/services/assessment_import_service.py
index 75c2248..03a65a0 100644
--- a/analytics/services/assessment_import_service.py
+++ b/analytics/services/assessment_import_service.py
@@ -2,20 +2,27 @@ from __future__ import annotations

 import hashlib
 import json
-from dataclasses import dataclass
+import zipfile
+from copy import deepcopy
+from dataclasses import asdict, dataclass
 from decimal import Decimal, InvalidOperation
 from io import BytesIO
 from pathlib import Path
 from typing import BinaryIO

+from django.conf import settings
 from django.core.exceptions import PermissionDenied, ValidationError
 from django.db import transaction
+from django.db.models import Q
 from django.utils import timezone
 from django.utils.text import slugify
 from openpyxl import load_workbook
 from openpyxl.utils import get_column_letter

 from analytics.models import (
+    ASSESSMENT_CONFLICT_NONE,
+    ASSESSMENT_CONFLICT_RESOLVED,
+    ASSESSMENT_CONFLICT_UNRESOLVED,
     ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
     ASSESSMENT_IMPORT_ROW_COMMITTED,
     ASSESSMENT_IMPORT_ROW_INVALID,
@@ -25,8 +32,15 @@ from analytics.models import (
     ASSESSMENT_IMPORT_STATUS_COMMITTED,
     ASSESSMENT_IMPORT_STATUS_FAILED,
     ASSESSMENT_IMPORT_STATUS_PREVIEWED,
+    ASSESSMENT_MATCH_AMBIGUOUS,
+    ASSESSMENT_MATCH_MATCHED,
+    ASSESSMENT_MATCH_UNMATCHED,
     ASSESSMENT_STATUS_COMMITTED,
+    ASSESSMENT_STATUS_DRAFT,
+    ASSESSMENT_VALIDATION_INVALID,
+    ASSESSMENT_VALIDATION_VALID,
     ASSESSMENT_VALUE_SOURCE_IMPORTED,
+    ASSESSMENT_VALUE_SOURCE_MANUAL_CORRECTED,
     ASSESSMENT_VALUE_TYPE_NUMBER,
     ASSESSMENT_VALUE_TYPE_RATING,
     AssessmentImportBatch,
@@ -37,6 +51,7 @@ from analytics.models import (
     AssessmentTemplate,
     AssessmentTemplateMetric,
     AssessmentValue,
+    AssessmentValueCorrection,
     PlayerAssessment,
 )
 from analytics.services.assessment_matching_service import (
@@ -50,220 +65,252 @@ from players.models import Player
 BOOTSTRAP_2026_13U_ASSESSMENT_KEY = "2026-13u-house-assessment"
 BOOTSTRAP_2026_13U_IMPORT_KEY = "2026-13u-house-assessment-xlsx"

+ZERO_ALLOW = "allow"
+ZERO_TREAT_AS_MISSING = "treat_as_missing"
+ZERO_WARNING = "warning"
+ZERO_ERROR = "error"
+ZERO_POLICIES = {ZERO_ALLOW, ZERO_TREAT_AS_MISSING, ZERO_WARNING, ZERO_ERROR}
+
+BLANK_PRESERVE = "preserve_existing"
+BLANK_CLEAR = "clear_existing_imported_value"
+BLANK_IGNORE_CREATE = "ignore_on_create"
+BLANK_REQUIRED_ERROR = "error_if_required"
+BLANK_POLICIES = {
+    BLANK_PRESERVE,
+    BLANK_CLEAR,
+    BLANK_IGNORE_CREATE,
+    BLANK_REQUIRED_ERROR,
+}
+
+METRIC_ACTION_CREATE = "create"
+METRIC_ACTION_UPDATE = "update"
+METRIC_ACTION_UNCHANGED = "unchanged"
+METRIC_ACTION_CLEAR = "clear"
+METRIC_ACTION_SKIP = "skip"
+METRIC_ACTION_PROTECTED_MANUAL = "protected_manual"
+METRIC_ACTION_CONFLICT = "conflict"
+METRIC_ACTION_INVALID = "invalid"
+
+DEFAULT_MAX_UPLOAD_BYTES = 10 * 1024 * 1024
+DEFAULT_MAX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024
+DEFAULT_MAX_WORKSHEETS = 12
+DEFAULT_MAX_ROWS = 500
+DEFAULT_MAX_COLUMNS = 50
+DEFAULT_MAX_CELL_TEXT_LENGTH = 500
+
+
+def _number_metric(
+    header,
+    key,
+    category,
+    *,
+    direction="neutral",
+    min_value=None,
+    max_value=None,
+    zero_policy=ZERO_ERROR,
+):
+    return {
+        "header": header,
+        "key": key,
+        "category": category,
+        "value_type": ASSESSMENT_VALUE_TYPE_NUMBER,
+        "direction": direction,
+        "required_header": True,
+        "required_value": False,
+        "min_value": min_value,
+        "max_value": max_value,
+        "unit": "",
+        "unit_status": "unverified",
+        "unit_source": "",
+        "zero_policy": zero_policy,
+        "blank_policy": BLANK_CLEAR,
+    }
+
+
+def _rating_metric(header, key, category):
+    return {
+        "header": header,
+        "key": key,
+        "category": category,
+        "value_type": ASSESSMENT_VALUE_TYPE_RATING,
+        "direction": "higher",
+        "required_header": True,
+        "required_value": False,
+        "rating_scale_min": 1,
+        "rating_scale_max": 3,
+        "integer_only": True,
+        "allowed_choices": [1, 2, 3],
+        "unit": "",
+        "unit_status": "not_applicable",
+        "zero_policy": ZERO_ERROR,
+        "blank_policy": BLANK_CLEAR,
+    }
+
+
+def _text_metric(header, key, category):
+    return {
+        "header": header,
+        "key": key,
+        "category": category,
+        "value_type": "text",
+        "required_header": True,
+        "required_value": False,
+        "unit": "",
+        "unit_status": "not_applicable",
+        "zero_policy": ZERO_ALLOW,
+        "blank_policy": BLANK_CLEAR,
+    }
+

 DEFAULT_2026_13U_DATA_SHEETS = [
     {
         "name": "Assessment Data",
+        "required": True,
         "header_row": 2,
         "identity_column": "Name",
         "category_row": 1,
+        "max_rows": 500,
+        "max_columns": 30,
         "metrics": [
-            {
-                "header": "Home to 1st",
-                "key": "home_to_1st",
-                "category": "Athleticism Evaluation",
-                "unit": "seconds",
-                "direction": "lower",
-            },
-            {
-                "header": "Broad Jump",
-                "key": "broad_jump",
-                "category": "Athleticism Evaluation",
-                "unit": "inches",
-                "direction": "higher",
-            },
-            {
-                "header": "Lateral Jump",
-                "key": "lateral_jump",
-                "category": "Athleticism Evaluation",
-                "unit": "inches",
-                "direction": "higher",
-            },
-            {
-                "header": "Shotput",
-                "key": "shotput",
-                "category": "Athleticism Evaluation",
-                "unit": "feet",
-                "direction": "higher",
-            },
-            {
-                "header": "Bat Speed",
-                "key": "bat_speed",
-                "category": "Hitting Objective Evaluation",
-                "unit": "mph",
-                "direction": "higher",
-            },
-            {
-                "header": "Time 2 Contact",
-                "key": "time_to_contact",
-                "category": "Hitting Objective Evaluation",
-                "unit": "seconds",
-                "direction": "lower",
-            },
-            {
-                "header": "Exit Velocity Avg.",
-                "key": "exit_velocity_avg",
-                "category": "Hitting Objective Evaluation",
-                "unit": "mph",
-                "direction": "higher",
-            },
-            {
-                "header": "Exit Velocity Max",
-                "key": "exit_velocity_max",
-                "category": "Hitting Objective Evaluation",
-                "unit": "mph",
-                "direction": "higher",
-            },
-            {
-                "header": "Athletic Stance",
-                "key": "athletic_stance",
-                "category": "Hitting Subjective Evaluation",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Balance Stride",
-                "key": "balance_stride",
-                "category": "Hitting Subjective Evaluation",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Barrel Level",
-                "key": "barrel_level",
-                "category": "Hitting Subjective Evaluation",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Launch Position",
-                "key": "launch_position",
-                "category": "Hitting Subjective Evaluation",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Follow Through",
-                "key": "follow_through",
-                "category": "Hitting Subjective Evaluation",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Readiness",
-                "key": "fielding_readiness",
-                "category": "Fielding and Throwing Evaluation",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Footwork",
-                "key": "fielding_footwork",
-                "category": "Fielding and Throwing Evaluation",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Glovework",
-                "key": "fielding_glovework",
-                "category": "Fielding and Throwing Evaluation",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Athleticism",
-                "key": "fielding_athleticism",
-                "category": "Fielding and Throwing Evaluation",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Fundamental Throwing",
-                "key": "fundamental_throwing",
-                "category": "Fielding and Throwing Evaluation",
-                "value_type": "rating",
-                "direction": "higher",
-            },
+            _number_metric(
+                "Home to 1st",
+                "home_to_1st",
+                "Athleticism Evaluation",
+                direction="lower",
+                min_value=2,
+                max_value=10,
+            ),
+            _number_metric(
+                "Broad Jump",
+                "broad_jump",
+                "Athleticism Evaluation",
+                direction="higher",
+                min_value=1,
+                max_value=200,
+            ),
+            _number_metric(
+                "Lateral Jump",
+                "lateral_jump",
+                "Athleticism Evaluation",
+                direction="higher",
+                min_value=1,
+                max_value=200,
+            ),
+            _number_metric(
+                "Shotput",
+                "shotput",
+                "Athleticism Evaluation",
+                direction="higher",
+                min_value=1,
+                max_value=1000,
+            ),
+            _number_metric(
+                "Bat Speed",
+                "bat_speed",
+                "Hitting Objective Evaluation",
+                direction="higher",
+                min_value=1,
+                max_value=150,
+                zero_policy=ZERO_TREAT_AS_MISSING,
+            ),
+            _number_metric(
+                "Time 2 Contact",
+                "time_to_contact",
+                "Hitting Objective Evaluation",
+                direction="lower",
+                min_value="0.01",
+                max_value=2,
+                zero_policy=ZERO_TREAT_AS_MISSING,
+            ),
+            _number_metric(
+                "Exit Velocity Avg.",
+                "exit_velocity_avg",
+                "Hitting Objective Evaluation",
+                direction="higher",
+                min_value=1,
+                max_value=150,
+                zero_policy=ZERO_TREAT_AS_MISSING,
+            ),
+            _number_metric(
+                "Exit Velocity Max",
+                "exit_velocity_max",
+                "Hitting Objective Evaluation",
+                direction="higher",
+                min_value=1,
+                max_value=150,
+                zero_policy=ZERO_TREAT_AS_MISSING,
+            ),
+            _rating_metric(
+                "Athletic Stance", "athletic_stance", "Hitting Subjective Evaluation"
+            ),
+            _rating_metric(
+                "Balance Stride", "balance_stride", "Hitting Subjective Evaluation"
+            ),
+            _rating_metric(
+                "Barrel Level", "barrel_level", "Hitting Subjective Evaluation"
+            ),
+            _rating_metric(
+                "Launch Position", "launch_position", "Hitting Subjective Evaluation"
+            ),
+            _rating_metric(
+                "Follow Through", "follow_through", "Hitting Subjective Evaluation"
+            ),
+            _rating_metric(
+                "Readiness", "fielding_readiness", "Fielding and Throwing Evaluation"
+            ),
+            _rating_metric(
+                "Footwork", "fielding_footwork", "Fielding and Throwing Evaluation"
+            ),
+            _rating_metric(
+                "Glovework", "fielding_glovework", "Fielding and Throwing Evaluation"
+            ),
+            _rating_metric(
+                "Athleticism",
+                "fielding_athleticism",
+                "Fielding and Throwing Evaluation",
+            ),
+            _rating_metric(
+                "Fundamental Throwing",
+                "fundamental_throwing",
+                "Fielding and Throwing Evaluation",
+            ),
         ],
     },
     {
         "name": "Pitching Data",
+        "required": False,
         "header_row": 2,
         "identity_column": "Name",
+        "max_rows": 500,
+        "max_columns": 20,
         "metrics": [
-            {
-                "header": "Velocity Avg.",
-                "key": "pitching_velocity_avg",
-                "category": "Pitching Data",
-                "unit": "mph",
-                "direction": "higher",
-            },
-            {
-                "header": "Velocity Max",
-                "key": "pitching_velocity_max",
-                "category": "Pitching Data",
-                "unit": "mph",
-                "direction": "higher",
-            },
-            {
-                "header": "Pitch 1",
-                "key": "pitch_1",
-                "category": "Pitching Data",
-                "value_type": "text",
-            },
-            {
-                "header": "Pitch 2",
-                "key": "pitch_2",
-                "category": "Pitching Data",
-                "value_type": "text",
-            },
-            {
-                "header": "Pitch 3",
-                "key": "pitch_3",
-                "category": "Pitching Data",
-                "value_type": "text",
-            },
-            {
-                "header": "Pitch 4",
-                "key": "pitch_4",
-                "category": "Pitching Data",
-                "value_type": "text",
-            },
-            {
-                "header": "Athletic Movement",
-                "key": "pitching_athletic_movement",
-                "category": "Pitching Data",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Body Control",
-                "key": "pitching_body_control",
-                "category": "Pitching Data",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Direction",
-                "key": "pitching_direction",
-                "category": "Pitching Data",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Repeatability",
-                "key": "pitching_repeatability",
-                "category": "Pitching Data",
-                "value_type": "rating",
-                "direction": "higher",
-            },
-            {
-                "header": "Command2",
-                "key": "pitching_command",
-                "category": "Pitching Data",
-                "value_type": "rating",
-                "direction": "higher",
-            },
+            _number_metric(
+                "Velocity Avg.",
+                "pitching_velocity_avg",
+                "Pitching Data",
+                direction="higher",
+                min_value=1,
+                max_value=120,
+            ),
+            _number_metric(
+                "Velocity Max",
+                "pitching_velocity_max",
+                "Pitching Data",
+                direction="higher",
+                min_value=1,
+                max_value=120,
+            ),
+            _text_metric("Pitch 1", "pitch_1", "Pitching Data"),
+            _text_metric("Pitch 2", "pitch_2", "Pitching Data"),
+            _text_metric("Pitch 3", "pitch_3", "Pitching Data"),
+            _text_metric("Pitch 4", "pitch_4", "Pitching Data"),
+            _rating_metric(
+                "Athletic Movement", "pitching_athletic_movement", "Pitching Data"
+            ),
+            _rating_metric("Body Control", "pitching_body_control", "Pitching Data"),
+            _rating_metric("Direction", "pitching_direction", "Pitching Data"),
+            _rating_metric("Repeatability", "pitching_repeatability", "Pitching Data"),
+            _rating_metric("Command2", "pitching_command", "Pitching Data"),
         ],
     },
 ]
@@ -274,16 +321,40 @@ DEFAULT_2026_13U_RANKING_SHEETS = ["Ranking", "Pitcher Ranking"]
 @dataclass(frozen=True)
 class AssessmentPreviewSummary:
     rows: int
+    valid_player_rows: int
     matched: int
     unmatched: int
     ambiguous: int
     invalid: int
     skipped: int
+    conflicts: int
+    creates: int
+    updates: int
+    unchanged: int
+    clears: int
+    protected_manual: int
+    workbook_errors: int
+    workbook_warnings: int
+    acknowledgement_required: bool
+    acknowledgement_complete: bool
     checksum_seen_before: bool

+    @property
+    def structurally_ready(self) -> bool:
+        return (
+            self.valid_player_rows > 0
+            and self.workbook_errors == 0
+            and self.invalid == 0
+            and self.unmatched == 0
+            and self.ambiguous == 0
+            and self.conflicts == 0
+        )
+
     @property
     def can_commit(self) -> bool:
-        return self.unmatched == 0 and self.ambiguous == 0 and self.invalid == 0
+        return self.structurally_ready and (
+            not self.acknowledgement_required or self.acknowledgement_complete
+        )


 @dataclass(frozen=True)
@@ -291,7 +362,25 @@ class AssessmentCommitResult:
     processed: int
     created: int
     updated: int
+    unchanged: int
     skipped: int
+    values_created: int
+    values_updated: int
+    values_cleared: int
+    values_unchanged: int
+    values_protected: int
+
+
+def _issue(code, message, *, blocking=False, requires_ack=False, **context):
+    issue = {
+        "code": code,
+        "message": message,
+        "blocking": bool(blocking),
+        "requires_ack": bool(requires_ack),
+    }
+    if context:
+        issue["context"] = context
+    return issue


 def normalize_sheet_name(value: str) -> str:
@@ -299,7 +388,16 @@ def normalize_sheet_name(value: str) -> str:


 def normalize_header(value: str) -> str:
-    return normalize_sheet_name(value).replace(".", "").replace(" ", "_")
+    normalized = normalize_sheet_name(value)
+    return "_".join(part for part in normalized.replace(".", " ").split() if part)
+
+
+def _config_json(config: dict) -> str:
+    return json.dumps(config, sort_keys=True, separators=(",", ":"), default=str)
+
+
+def config_checksum(config: dict) -> str:
+    return hashlib.sha256(_config_json(config).encode("utf-8")).hexdigest()


 def _workbook_bytes(file_obj: BinaryIO) -> bytes:
@@ -314,8 +412,78 @@ def workbook_sha256(content: bytes) -> str:
     return hashlib.sha256(content).hexdigest()


-def _load_workbook_from_bytes(content: bytes):
-    return load_workbook(BytesIO(content), read_only=True, data_only=True)
+def _limits(config: dict) -> dict:
+    configured = config.get("limits", {})
+    return {
+        "max_upload_bytes": min(
+            int(configured.get("max_upload_bytes", DEFAULT_MAX_UPLOAD_BYTES)),
+            int(
+                getattr(
+                    settings,
+                    "ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES",
+                    DEFAULT_MAX_UPLOAD_BYTES,
+                )
+            ),
+        ),
+        "max_worksheets": int(configured.get("max_worksheets", DEFAULT_MAX_WORKSHEETS)),
+        "max_archive_uncompressed_bytes": min(
+            int(
+                configured.get(
+                    "max_archive_uncompressed_bytes",
+                    DEFAULT_MAX_UNCOMPRESSED_BYTES,
+                )
+            ),
+            int(
+                getattr(
+                    settings,
+                    "ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES",
+                    DEFAULT_MAX_UNCOMPRESSED_BYTES,
+                )
+            ),
+        ),
+        "max_rows": int(configured.get("max_rows", DEFAULT_MAX_ROWS)),
+        "max_columns": int(configured.get("max_columns", DEFAULT_MAX_COLUMNS)),
+        "max_cell_text_length": int(
+            configured.get("max_cell_text_length", DEFAULT_MAX_CELL_TEXT_LENGTH)
+        ),
+    }
+
+
+def _load_workbook_from_bytes(content: bytes, config: dict):
+    limits = _limits(config)
+    if len(content) > limits["max_upload_bytes"]:
+        raise ValidationError("Workbook exceeds the configured upload size limit.")
+    if not zipfile.is_zipfile(BytesIO(content)):
+        raise ValidationError("Workbook is not a valid .xlsx file.")
+    with zipfile.ZipFile(BytesIO(content)) as archive:
+        members = archive.infolist()
+        names = {member.filename for member in members}
+        if (
+            sum(member.file_size for member in members)
+            > limits["max_archive_uncompressed_bytes"]
+        ):
+            raise ValidationError(
+                "Workbook expands beyond the configured safe processing limit."
+            )
+        if any(name.lower().endswith("vbaproject.bin") for name in names):
+            raise ValidationError("Macro-enabled workbooks are not supported.")
+        if any(name.startswith("xl/externalLinks/") for name in names):
+            raise ValidationError("Workbooks with external links are not supported.")
+    try:
+        workbook = load_workbook(
+            BytesIO(content),
+            read_only=True,
+            data_only=False,
+            keep_links=False,
+        )
+    except Exception as exc:
+        raise ValidationError(
+            "Workbook could not be read as a valid .xlsx file."
+        ) from exc
+    if len(workbook.sheetnames) > limits["max_worksheets"]:
+        workbook.close()
+        raise ValidationError("Workbook contains too many worksheets.")
+    return workbook


 def _worksheet_by_name(workbook, configured_name: str):
@@ -326,25 +494,42 @@ def _worksheet_by_name(workbook, configured_name: str):
     return None


-def _row_values(row) -> list:
-    return [cell for cell in row]
-
-
-def _header_map(row_values: list) -> dict[str, int]:
+def _header_map(row_values: list) -> tuple[dict[str, int], list[str]]:
     mapping = {}
+    duplicates = []
     for index, value in enumerate(row_values):
-        if value not in (None, ""):
-            mapping[normalize_header(value)] = index
-    return mapping
+        if value in (None, ""):
+            continue
+        normalized = normalize_header(value)
+        if normalized in mapping:
+            duplicates.append(str(value).strip())
+        else:
+            mapping[normalized] = index
+    return mapping, duplicates
+
+
+def _header_candidates(config: dict) -> list[str]:
+    return [config.get("header", ""), *config.get("header_aliases", [])]
+
+
+def _find_header_index(headers: dict[str, int], config: dict) -> int | None:
+    for candidate in _header_candidates(config):
+        index = headers.get(normalize_header(candidate))
+        if index is not None:
+            return index
+    return None


 def _decimal_or_none(value) -> Decimal | None:
     if value in (None, ""):
         return None
     try:
-        return Decimal(str(value).strip())
+        result = Decimal(str(value).strip())
     except (InvalidOperation, ValueError):
         return None
+    if not result.is_finite():
+        return None
+    return result


 def _snapshot_value(
@@ -354,151 +539,898 @@ def _snapshot_value(
     sheet_name: str,
     row_number: int,
     column_index: int,
-) -> dict | None:
-    if raw_value in (None, ""):
-        return None
+    max_cell_text_length: int,
+) -> dict:
     value_type = metric_config.get("value_type") or ASSESSMENT_VALUE_TYPE_NUMBER
-    raw_text = str(raw_value).strip()
+    raw_text = "" if raw_value is None else str(raw_value).strip()
     snapshot = {
         "metric_key": metric_config["key"],
         "header": metric_config["header"],
         "value_type": value_type,
         "unit": metric_config.get("unit", ""),
+        "unit_status": metric_config.get("unit_status", "not_applicable"),
+        "unit_source": metric_config.get("unit_source", ""),
+        "rating_scale_min": metric_config.get("rating_scale_min"),
+        "rating_scale_max": metric_config.get("rating_scale_max"),
+        "zero_policy": metric_config.get("zero_policy", ZERO_ALLOW),
+        "blank_policy": metric_config.get("blank_policy", BLANK_PRESERVE),
         "raw_value": raw_text,
+        "normalized_value": "",
+        "is_blank": raw_value in (None, ""),
         "source_sheet": sheet_name,
         "source_row": row_number,
         "source_column": get_column_letter(column_index + 1),
+        "source_header": metric_config["header"],
+        "errors": [],
+        "warnings": [],
+        "transformations": [],
     }
-    if value_type in {ASSESSMENT_VALUE_TYPE_NUMBER, ASSESSMENT_VALUE_TYPE_RATING}:
-        decimal_value = _decimal_or_none(raw_value)
-        if decimal_value is None:
-            snapshot["error"] = f"{metric_config['header']} is not numeric."
-        else:
-            snapshot["numeric_value"] = str(decimal_value)
-    else:
+    if len(raw_text) > max_cell_text_length:
+        snapshot["errors"].append(
+            _issue(
+                "cell_text_too_long",
+                f"{metric_config['header']} exceeds the cell text limit.",
+                blocking=True,
+            )
+        )
+        return snapshot
+    if snapshot["is_blank"]:
+        if (
+            metric_config.get("required_value")
+            or snapshot["blank_policy"] == BLANK_REQUIRED_ERROR
+        ):
+            snapshot["errors"].append(
+                _issue(
+                    "required_value_missing",
+                    f"{metric_config['header']} is required for this row.",
+                    blocking=True,
+                )
+            )
+        return snapshot
+    if isinstance(raw_value, str) and raw_value.startswith("="):
+        snapshot["errors"].append(
+            _issue(
+                "formula_not_supported",
+                f"{metric_config['header']} contains a formula instead of a value.",
+                blocking=True,
+            )
+        )
+        return snapshot
+    if value_type not in {ASSESSMENT_VALUE_TYPE_NUMBER, ASSESSMENT_VALUE_TYPE_RATING}:
         snapshot["text_value"] = raw_text
+        snapshot["normalized_value"] = raw_text
+        return snapshot
+
+    decimal_value = _decimal_or_none(raw_value)
+    if decimal_value is None:
+        snapshot["errors"].append(
+            _issue(
+                "invalid_numeric_value",
+                f"{metric_config['header']} is not a valid finite number.",
+                blocking=True,
+            )
+        )
+        return snapshot
+
+    zero_policy = snapshot["zero_policy"]
+    if zero_policy not in ZERO_POLICIES:
+        snapshot["errors"].append(
+            _issue(
+                "invalid_zero_policy",
+                f"{metric_config['header']} has an invalid zero policy.",
+                blocking=True,
+            )
+        )
+        return snapshot
+    if decimal_value == 0:
+        if zero_policy == ZERO_ERROR:
+            snapshot["errors"].append(
+                _issue(
+                    "zero_not_allowed",
+                    f"{metric_config['header']} cannot be zero.",
+                    blocking=True,
+                )
+            )
+            return snapshot
+        if zero_policy == ZERO_TREAT_AS_MISSING:
+            snapshot["is_blank"] = True
+            snapshot["warnings"].append(
+                _issue(
+                    "zero_treated_as_missing",
+                    f"{metric_config['header']} zero will be treated as missing.",
+                    requires_ack=True,
+                )
+            )
+            snapshot["transformations"].append(
+                {
+                    "kind": "zero_to_missing",
+                    "reason": "Configured zero policy treats implausible zero as missing.",
+                    "policy": ZERO_TREAT_AS_MISSING,
+                }
+            )
+            return snapshot
+        if zero_policy == ZERO_WARNING:
+            snapshot["warnings"].append(
+                _issue(
+                    "zero_requires_review",
+                    f"{metric_config['header']} contains zero and requires review.",
+                    requires_ack=True,
+                )
+            )
+
+    min_value = _decimal_or_none(metric_config.get("min_value"))
+    max_value = _decimal_or_none(metric_config.get("max_value"))
+    if min_value is not None and decimal_value < min_value:
+        snapshot["errors"].append(
+            _issue(
+                "value_below_minimum",
+                f"{metric_config['header']} is below the configured minimum {min_value}.",
+                blocking=True,
+            )
+        )
+    if max_value is not None and decimal_value > max_value:
+        snapshot["errors"].append(
+            _issue(
+                "value_above_maximum",
+                f"{metric_config['header']} is above the configured maximum {max_value}.",
+                blocking=True,
+            )
+        )
+    if (
+        metric_config.get("integer_only")
+        and decimal_value != decimal_value.to_integral_value()
+    ):
+        snapshot["errors"].append(
+            _issue(
+                "integer_required",
+                f"{metric_config['header']} must be a whole number.",
+                blocking=True,
+            )
+        )
+    allowed_choices = {
+        Decimal(str(value)) for value in metric_config.get("allowed_choices", [])
+    }
+    if allowed_choices and decimal_value not in allowed_choices:
+        snapshot["errors"].append(
+            _issue(
+                "value_not_allowed",
+                f"{metric_config['header']} must be one of {sorted(allowed_choices)}.",
+                blocking=True,
+            )
+        )
+    if value_type == ASSESSMENT_VALUE_TYPE_RATING:
+        rating_min = _decimal_or_none(metric_config.get("rating_scale_min"))
+        rating_max = _decimal_or_none(metric_config.get("rating_scale_max"))
+        if rating_min is None or rating_max is None:
+            snapshot["errors"].append(
+                _issue(
+                    "rating_scale_missing",
+                    f"{metric_config['header']} has no configured rating scale.",
+                    blocking=True,
+                )
+            )
+        elif decimal_value < rating_min or decimal_value > rating_max:
+            snapshot["errors"].append(
+                _issue(
+                    "rating_out_of_range",
+                    f"{metric_config['header']} must be between {rating_min} and {rating_max}.",
+                    blocking=True,
+                )
+            )
+    if snapshot["unit_status"] == "unverified":
+        snapshot["warnings"].append(
+            _issue(
+                "unit_unverified",
+                f"{metric_config['header']} unit is not confirmed.",
+                requires_ack=True,
+            )
+        )
+    if not snapshot["errors"]:
+        snapshot["numeric_value"] = str(decimal_value)
+        snapshot["normalized_value"] = str(decimal_value)
     return snapshot


-def parse_assessment_workbook(
-    content: bytes, import_template: AssessmentImportTemplate
-) -> dict:
-    """Parse configured workbook sheets into sanitized row/value snapshots."""
-    workbook = _load_workbook_from_bytes(content)
-    config = import_template.config
-    parsed_rows: dict[str, dict] = {}
-    workbook_errors = []
-    for sheet_config in config.get("sheets", []):
-        worksheet = _worksheet_by_name(workbook, sheet_config["name"])
-        if worksheet is None:
-            if sheet_config.get("required", True):
-                workbook_errors.append(f"Missing worksheet: {sheet_config['name']}.")
-            continue
-        rows = list(worksheet.iter_rows(values_only=True))
-        header_index = int(sheet_config.get("header_row", 1)) - 1
-        if header_index >= len(rows):
-            workbook_errors.append(
-                f"Missing header row for worksheet: {worksheet.title}."
+def _configured_header_names(sheet_config: dict) -> set[str]:
+    names = {normalize_header(sheet_config.get("identity_column", "Name"))}
+    for alias in sheet_config.get("identity_aliases", []):
+        names.add(normalize_header(alias))
+    for metric in sheet_config.get("metrics", []):
+        names.update(normalize_header(value) for value in _header_candidates(metric))
+    for identifier in sheet_config.get("source_identifiers", []):
+        names.update(
+            normalize_header(value) for value in _header_candidates(identifier)
+        )
+    return names
+
+
+def _parse_sheet(
+    workbook, sheet_config: dict, config: dict
+) -> tuple[list[dict], list, list]:
+    worksheet = _worksheet_by_name(workbook, sheet_config["name"])
+    errors = []
+    warnings = []
+    if worksheet is None:
+        issue = _issue(
+            (
+                "required_sheet_missing"
+                if sheet_config.get("required", True)
+                else "optional_sheet_missing"
+            ),
+            f"{'Required' if sheet_config.get('required', True) else 'Optional'} worksheet is missing: {sheet_config['name']}.",
+            blocking=sheet_config.get("required", True),
+            requires_ack=not sheet_config.get("required", True),
+            sheet=sheet_config["name"],
+        )
+        (errors if issue["blocking"] else warnings).append(issue)
+        return [], errors, warnings
+
+    limits = _limits(config)
+    max_rows = min(
+        int(sheet_config.get("max_rows", limits["max_rows"])), limits["max_rows"]
+    )
+    max_columns = min(
+        int(sheet_config.get("max_columns", limits["max_columns"])),
+        limits["max_columns"],
+    )
+    if worksheet.max_row > max_rows:
+        errors.append(
+            _issue(
+                "worksheet_row_limit",
+                f"Worksheet {worksheet.title} exceeds the {max_rows}-row limit.",
+                blocking=True,
+                sheet=worksheet.title,
             )
-            continue
-        headers = _header_map(_row_values(rows[header_index]))
-        identity_key = normalize_header(sheet_config.get("identity_column", "Name"))
-        identity_index = headers.get(identity_key)
-        if identity_index is None:
-            workbook_errors.append(
-                f"Missing identity column in worksheet: {worksheet.title}."
+        )
+        return [], errors, warnings
+    if worksheet.max_column > max_columns:
+        errors.append(
+            _issue(
+                "worksheet_column_limit",
+                f"Worksheet {worksheet.title} exceeds the {max_columns}-column limit.",
+                blocking=True,
+                sheet=worksheet.title,
+            )
+        )
+        return [], errors, warnings
+
+    header_row = int(sheet_config.get("header_row", 1))
+    if header_row < 1 or header_row > worksheet.max_row:
+        errors.append(
+            _issue(
+                "header_row_missing",
+                f"Required header row {header_row} is missing from {worksheet.title}.",
+                blocking=True,
+                sheet=worksheet.title,
+            )
+        )
+        return [], errors, warnings
+    header_cells = next(
+        worksheet.iter_rows(
+            min_row=header_row,
+            max_row=header_row,
+            max_col=worksheet.max_column,
+            values_only=True,
+        ),
+        (),
+    )
+    if not any(value not in (None, "") for value in header_cells):
+        errors.append(
+            _issue(
+                "header_row_empty",
+                f"Required header row is empty in {worksheet.title}.",
+                blocking=True,
+                sheet=worksheet.title,
+            )
+        )
+        return [], errors, warnings
+    headers, duplicate_headers = _header_map(list(header_cells))
+    for duplicate_header in duplicate_headers:
+        errors.append(
+            _issue(
+                "duplicate_header",
+                f"Duplicate header {duplicate_header} in {worksheet.title}.",
+                blocking=True,
+                sheet=worksheet.title,
+            )
+        )
+
+    identity_config = {
+        "header": sheet_config.get("identity_column", "Name"),
+        "header_aliases": sheet_config.get("identity_aliases", []),
+    }
+    identity_index = _find_header_index(headers, identity_config)
+    if identity_index is None:
+        errors.append(
+            _issue(
+                "identity_header_missing",
+                f"Identity header {identity_config['header']} is missing from {worksheet.title}.",
+                blocking=True,
+                sheet=worksheet.title,
+            )
+        )
+
+    metric_indexes = []
+    for metric_config in sheet_config.get("metrics", []):
+        metric_index = _find_header_index(headers, metric_config)
+        if metric_index is None:
+            issue = _issue(
+                (
+                    "required_metric_header_missing"
+                    if metric_config.get("required_header", True)
+                    else "optional_metric_header_missing"
+                ),
+                f"Expected header {metric_config['header']} is missing from {worksheet.title}.",
+                blocking=metric_config.get("required_header", True),
+                requires_ack=not metric_config.get("required_header", True),
+                sheet=worksheet.title,
+                metric=metric_config["key"],
+            )
+            (errors if issue["blocking"] else warnings).append(issue)
+        else:
+            metric_indexes.append((metric_config, metric_index))
+
+    identifier_indexes = []
+    for identifier_config in sheet_config.get("source_identifiers", []):
+        identifier_index = _find_header_index(headers, identifier_config)
+        if identifier_index is not None:
+            identifier_indexes.append((identifier_config, identifier_index))
+        elif identifier_config.get("required_header"):
+            errors.append(
+                _issue(
+                    "source_identifier_header_missing",
+                    f"Source identifier header {identifier_config['header']} is missing from {worksheet.title}.",
+                    blocking=True,
+                )
+            )
+
+    expected_headers = _configured_header_names(sheet_config)
+    for normalized, index in headers.items():
+        if normalized not in expected_headers:
+            warnings.append(
+                _issue(
+                    "unexpected_column",
+                    f"Unexpected column {header_cells[index]} in {worksheet.title} will be ignored.",
+                    requires_ack=True,
+                    sheet=worksheet.title,
+                    column=get_column_letter(index + 1),
+                )
             )
+
+    if identity_index is None or errors:
+        return [], errors, warnings
+
+    parsed_rows = []
+    seen_identities: dict[str, list[dict]] = {}
+    for row_number, row in enumerate(
+        worksheet.iter_rows(
+            min_row=header_row + 1,
+            max_row=worksheet.max_row,
+            max_col=worksheet.max_column,
+            values_only=True,
+        ),
+        start=header_row + 1,
+    ):
+        raw_identity = row[identity_index] if identity_index < len(row) else None
+        has_other_data = any(value not in (None, "") for value in row)
+        if raw_identity in (None, "") and not has_other_data:
             continue
-        metric_indexes = []
-        for metric_config in sheet_config.get("metrics", []):
-            metric_index = headers.get(normalize_header(metric_config["header"]))
-            if metric_index is not None:
-                metric_indexes.append((metric_config, metric_index))
-        for zero_based_index, row in enumerate(
-            rows[header_index + 1 :], start=header_index + 2
-        ):
-            row_values = _row_values(row)
-            raw_name = (
-                row_values[identity_index] if identity_index < len(row_values) else ""
+        normalized_identity = normalize_assessment_name(raw_identity)
+        row_errors = []
+        if not normalized_identity:
+            row_errors.append(
+                _issue(
+                    "identity_value_missing",
+                    f"Row {row_number} in {worksheet.title} has data but no player identity.",
+                    blocking=True,
+                )
             )
-            if raw_name in (None, ""):
-                continue
-            row_key = (
-                slugify(normalize_assessment_name(raw_name))
-                or f"row-{zero_based_index}"
+            normalized_identity = (
+                f"__missing__:{normalize_sheet_name(worksheet.title)}:{row_number}"
+            )
+        values = []
+        row_warnings = []
+        for metric_config, metric_index in metric_indexes:
+            raw_value = row[metric_index] if metric_index < len(row) else None
+            snapshot = _snapshot_value(
+                metric_config,
+                raw_value,
+                sheet_name=worksheet.title,
+                row_number=row_number,
+                column_index=metric_index,
+                max_cell_text_length=limits["max_cell_text_length"],
             )
-            parsed_row = parsed_rows.setdefault(
-                row_key,
+            row_errors.extend(snapshot["errors"])
+            row_warnings.extend(snapshot["warnings"])
+            values.append(snapshot)
+        source_identifiers = []
+        for identifier_config, identifier_index in identifier_indexes:
+            raw_value = row[identifier_index] if identifier_index < len(row) else None
+            if raw_value in (None, ""):
+                continue
+            source_identifiers.append(
                 {
-                    "row_key": row_key,
-                    "raw_identity": str(raw_name).strip(),
-                    "source_rows": [],
-                    "values": [],
-                    "errors": [],
-                },
+                    "source": identifier_config.get("source", ""),
+                    "identifier_type": identifier_config.get("identifier_type", ""),
+                    "identifier_value": str(raw_value).strip(),
+                }
             )
-            parsed_row["source_rows"].append(
-                {"sheet": worksheet.title, "row": zero_based_index}
+        parsed_row = {
+            "normalized_identity": normalized_identity,
+            "raw_identity": "" if raw_identity is None else str(raw_identity).strip(),
+            "source_rows": [{"sheet": worksheet.title, "row": row_number}],
+            "source_identifiers": source_identifiers,
+            "values": values,
+            "errors": row_errors,
+            "warnings": row_warnings,
+        }
+        parsed_rows.append(parsed_row)
+        seen_identities.setdefault(normalized_identity, []).append(parsed_row)
+
+    for normalized_identity, duplicate_rows in seen_identities.items():
+        if len(duplicate_rows) < 2:
+            continue
+        for duplicate_row in duplicate_rows:
+            duplicate_row["errors"].append(
+                _issue(
+                    "duplicate_identity_in_sheet",
+                    f"Player identity appears more than once in {worksheet.title}.",
+                    blocking=True,
+                    normalized_identity=normalized_identity,
+                )
             )
-            raw_row = {}
-            for metric_config, metric_index in metric_indexes:
-                value = (
-                    row_values[metric_index] if metric_index < len(row_values) else None
+    return parsed_rows, errors, warnings
+
+
+def _combine_component_rows(component_rows: list[dict]) -> list[dict]:
+    combined: dict[str, dict] = {}
+    slug_identities: dict[str, set[str]] = {}
+    source_identifier_rows: dict[tuple[str, str, str], list[dict]] = {}
+    for component in component_rows:
+        normalized_identity = component["normalized_identity"]
+        row = combined.setdefault(
+            normalized_identity,
+            {
+                "row_key": hashlib.sha256(
+                    normalized_identity.encode("utf-8")
+                ).hexdigest()[:32],
+                "normalized_identity": normalized_identity,
+                "raw_identity": component["raw_identity"],
+                "source_rows": [],
+                "source_identifiers": [],
+                "values": [],
+                "errors": [],
+                "warnings": [],
+            },
+        )
+        row["source_rows"].extend(component["source_rows"])
+        row["source_identifiers"].extend(component["source_identifiers"])
+        row["errors"].extend(component["errors"])
+        row["warnings"].extend(component["warnings"])
+        existing_values = {value["metric_key"]: value for value in row["values"]}
+        for value in component["values"]:
+            existing = existing_values.get(value["metric_key"])
+            if existing and existing.get("raw_value") != value.get("raw_value"):
+                row["errors"].append(
+                    _issue(
+                        "conflicting_duplicate_metric",
+                        f"Conflicting source values exist for {value['header']}.",
+                        blocking=True,
+                    )
                 )
-                raw_row[metric_config["header"]] = "" if value is None else str(value)
-                snapshot = _snapshot_value(
-                    metric_config,
-                    value,
-                    sheet_name=worksheet.title,
-                    row_number=zero_based_index,
-                    column_index=metric_index,
+            elif not existing:
+                row["values"].append(value)
+                existing_values[value["metric_key"]] = value
+        slug_identities.setdefault(slugify(normalized_identity), set()).add(
+            normalized_identity
+        )
+        for identifier in component["source_identifiers"]:
+            key = (
+                normalize_sheet_name(identifier.get("source", "")),
+                normalize_sheet_name(identifier.get("identifier_type", "")),
+                normalize_sheet_name(identifier.get("identifier_value", "")),
+            )
+            source_identifier_rows.setdefault(key, []).append(row)
+
+    for identities in slug_identities.values():
+        if len(identities) < 2:
+            continue
+        for identity in identities:
+            combined[identity]["errors"].append(
+                _issue(
+                    "identity_slug_collision",
+                    "Distinct player identities would collide under slug matching; manual correction is required.",
+                    blocking=True,
                 )
-                if snapshot is None:
-                    continue
-                if snapshot.get("error"):
-                    parsed_row["errors"].append(snapshot["error"])
-                parsed_row["values"].append(snapshot)
-            parsed_row.setdefault("raw_rows", []).append(
-                {"sheet": worksheet.title, "row": zero_based_index, "values": raw_row}
             )
+    for identifier, rows in source_identifier_rows.items():
+        unique_rows = {row["row_key"]: row for row in rows}
+        if identifier == ("", "", "") or len(unique_rows) < 2:
+            continue
+        for row in unique_rows.values():
+            row["errors"].append(
+                _issue(
+                    "duplicate_source_identifier",
+                    "A source identifier is assigned to multiple workbook rows.",
+                    blocking=True,
+                )
+            )
+    return list(combined.values())
+
+
+def parse_assessment_workbook(content: bytes, config_or_template) -> dict:
+    """Parse a workbook using a frozen configuration without writing player data."""
+    config = (
+        config_or_template.config
+        if isinstance(config_or_template, AssessmentImportTemplate)
+        else deepcopy(config_or_template)
+    )
+    workbook = _load_workbook_from_bytes(content, config)
+    workbook_errors = []
+    workbook_warnings = []
+    component_rows = []
+    try:
+        for sheet_config in config.get("sheets", []):
+            rows, errors, warnings = _parse_sheet(workbook, sheet_config, config)
+            component_rows.extend(rows)
+            workbook_errors.extend(errors)
+            workbook_warnings.extend(warnings)
+    finally:
+        workbook.close()
+    rows = _combine_component_rows(component_rows)
+    if not rows:
+        workbook_errors.append(
+            _issue(
+                "no_player_rows",
+                "No valid source player rows were parsed from the workbook.",
+                blocking=True,
+            )
+        )
     return {
-        "rows": list(parsed_rows.values()),
+        "rows": rows,
         "errors": workbook_errors,
+        "warnings": workbook_warnings,
         "ranking_sheets": config.get("ranking_sheets", []),
     }


-def _preview_summary(batch: AssessmentImportBatch) -> AssessmentPreviewSummary:
+def _value_snapshot(value: AssessmentValue | None) -> dict | None:
+    if value is None:
+        return None
+    return {
+        "id": value.pk,
+        "numeric_value": (
+            str(value.numeric_value) if value.numeric_value is not None else None
+        ),
+        "rating_value": (
+            str(value.rating_value) if value.rating_value is not None else None
+        ),
+        "rating_scale_min": (
+            str(value.rating_scale_min) if value.rating_scale_min is not None else None
+        ),
+        "rating_scale_max": (
+            str(value.rating_scale_max) if value.rating_scale_max is not None else None
+        ),
+        "text_value": value.text_value,
+        "choice_value": value.choice_value,
+        "raw_value": value.raw_value,
+        "normalized_value": value.normalized_value,
+        "unit": value.unit,
+        "source_kind": value.source_kind,
+        "is_manual_override": value.is_manual_override,
+        "source_sheet": value.source_sheet,
+        "source_header": value.source_header,
+    }
+
+
+def _existing_normalized(value: AssessmentValue) -> str:
+    if value.rating_value is not None:
+        return str(value.rating_value)
+    if value.numeric_value is not None:
+        return str(value.numeric_value)
+    if value.choice_value:
+        return value.choice_value
+    return value.text_value
+
+
+def _values_equal(value: AssessmentValue, snapshot: dict) -> bool:
+    incoming = snapshot.get("normalized_value", "")
+    if snapshot.get("value_type") in {
+        ASSESSMENT_VALUE_TYPE_NUMBER,
+        ASSESSMENT_VALUE_TYPE_RATING,
+    }:
+        existing_decimal = _decimal_or_none(_existing_normalized(value))
+        incoming_decimal = _decimal_or_none(incoming)
+        return existing_decimal is not None and existing_decimal == incoming_decimal
+    return _existing_normalized(value) == incoming
+
+
+def _plan_metric_changes(
+    parsed_row: dict, *, event, player: Player | None
+) -> list[dict]:
+    existing_assessment = None
+    existing_values = {}
+    if player:
+        existing_assessment = PlayerAssessment.objects.filter(
+            player=player, event=event
+        ).first()
+        if existing_assessment:
+            existing_values = {
+                value.template_metric.metric.key: value
+                for value in existing_assessment.values.select_related(
+                    "template_metric__metric"
+                )
+            }
+    changes = []
+    for snapshot in parsed_row.get("values", []):
+        existing = existing_values.get(snapshot["metric_key"])
+        change = {
+            "metric_key": snapshot["metric_key"],
+            "header": snapshot["header"],
+            "value_type": snapshot["value_type"],
+            "unit": snapshot.get("unit", ""),
+            "unit_status": snapshot.get("unit_status", "not_applicable"),
+            "rating_scale_min": snapshot.get("rating_scale_min"),
+            "rating_scale_max": snapshot.get("rating_scale_max"),
+            "old_value": _value_snapshot(existing),
+            "incoming_raw_value": snapshot.get("raw_value", ""),
+            "incoming_normalized_value": snapshot.get("normalized_value", ""),
+            "source_sheet": snapshot.get("source_sheet", ""),
+            "source_row": snapshot.get("source_row"),
+            "source_column": snapshot.get("source_column", ""),
+            "source_header": snapshot.get("source_header", ""),
+            "warnings": snapshot.get("warnings", []),
+            "errors": snapshot.get("errors", []),
+            "transformations": snapshot.get("transformations", []),
+            "resolution": "",
+        }
+        if snapshot.get("errors"):
+            change["action"] = METRIC_ACTION_INVALID
+        elif snapshot.get("is_blank"):
+            if existing and existing.is_manual_override:
+                change["action"] = METRIC_ACTION_CONFLICT
+                change["conflict"] = "manual_override_blank"
+            elif existing and snapshot.get("blank_policy") == BLANK_CLEAR:
+                change["action"] = METRIC_ACTION_CLEAR
+            elif existing:
+                change["action"] = METRIC_ACTION_UNCHANGED
+            else:
+                change["action"] = METRIC_ACTION_SKIP
+        elif existing and existing.is_manual_override:
+            if _values_equal(existing, snapshot):
+                change["action"] = METRIC_ACTION_PROTECTED_MANUAL
+            else:
+                change["action"] = METRIC_ACTION_CONFLICT
+                change["conflict"] = "manual_override_difference"
+        elif existing is None:
+            change["action"] = METRIC_ACTION_CREATE
+        elif (
+            _values_equal(existing, snapshot)
+            and existing.unit == snapshot.get("unit", "")
+            and (
+                snapshot["value_type"] != ASSESSMENT_VALUE_TYPE_RATING
+                or (
+                    existing.rating_scale_min
+                    == _decimal_or_none(snapshot.get("rating_scale_min"))
+                    and existing.rating_scale_max
+                    == _decimal_or_none(snapshot.get("rating_scale_max"))
+                )
+            )
+        ):
+            change["action"] = METRIC_ACTION_UNCHANGED
+        else:
+            change["action"] = METRIC_ACTION_UPDATE
+        changes.append(change)
+    return changes
+
+
+def _match_status(match) -> str:
+    if match.status == MATCH_AMBIGUOUS:
+        return ASSESSMENT_MATCH_AMBIGUOUS
+    if match.status == MATCH_UNMATCHED:
+        return ASSESSMENT_MATCH_UNMATCHED
+    return ASSESSMENT_MATCH_MATCHED
+
+
+def _legacy_row_status(row) -> str:
+    if row.status in {ASSESSMENT_IMPORT_ROW_SKIPPED, ASSESSMENT_IMPORT_ROW_COMMITTED}:
+        return row.status
+    if row.validation_status == ASSESSMENT_VALIDATION_INVALID:
+        return ASSESSMENT_IMPORT_ROW_INVALID
+    if row.conflict_status == ASSESSMENT_CONFLICT_UNRESOLVED:
+        return ASSESSMENT_IMPORT_ROW_INVALID
+    if row.match_status == ASSESSMENT_MATCH_AMBIGUOUS:
+        return ASSESSMENT_IMPORT_ROW_AMBIGUOUS
+    if row.match_status == ASSESSMENT_MATCH_UNMATCHED:
+        return ASSESSMENT_IMPORT_ROW_UNMATCHED
+    return ASSESSMENT_IMPORT_ROW_MATCHED
+
+
+def _planned_row_action(row) -> str:
+    if row.status == ASSESSMENT_IMPORT_ROW_SKIPPED:
+        return "skip"
+    actions = {change.get("action") for change in row.metric_changes}
+    if METRIC_ACTION_INVALID in actions:
+        return "invalid"
+    if METRIC_ACTION_CONFLICT in actions:
+        return "conflict"
+    if row.match_status != ASSESSMENT_MATCH_MATCHED:
+        return "needs_identity_resolution"
+    if METRIC_ACTION_CREATE in actions and row.player_id:
+        return "create"
+    if actions & {METRIC_ACTION_UPDATE, METRIC_ACTION_CLEAR}:
+        return "update"
+    if actions <= {
+        METRIC_ACTION_UNCHANGED,
+        METRIC_ACTION_SKIP,
+        METRIC_ACTION_PROTECTED_MANUAL,
+    }:
+        return "unchanged"
+    return "skip"
+
+
+def _summary_counts(batch: AssessmentImportBatch) -> AssessmentPreviewSummary:
     rows = list(batch.rows.all())
+    metric_actions = [
+        change.get("action") for row in rows for change in row.metric_changes
+    ]
+    valid_rows = [
+        row
+        for row in rows
+        if row.status != ASSESSMENT_IMPORT_ROW_SKIPPED
+        and row.validation_status == ASSESSMENT_VALIDATION_VALID
+    ]
+    acknowledgement_required = bool(batch.required_warning_codes)
+    acknowledgement_complete = bool(
+        not acknowledgement_required
+        or (
+            batch.warnings_acknowledged_at
+            and batch.metadata.get("acknowledged_token") == batch.acknowledgement_token
+        )
+    )
     return AssessmentPreviewSummary(
         rows=len(rows),
-        matched=sum(1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_MATCHED),
+        valid_player_rows=len(valid_rows),
+        matched=sum(
+            1 for row in valid_rows if row.match_status == ASSESSMENT_MATCH_MATCHED
+        ),
         unmatched=sum(
-            1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_UNMATCHED
+            1 for row in valid_rows if row.match_status == ASSESSMENT_MATCH_UNMATCHED
         ),
         ambiguous=sum(
-            1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_AMBIGUOUS
+            1 for row in valid_rows if row.match_status == ASSESSMENT_MATCH_AMBIGUOUS
+        ),
+        invalid=sum(
+            1
+            for row in rows
+            if row.status != ASSESSMENT_IMPORT_ROW_SKIPPED
+            and row.validation_status == ASSESSMENT_VALIDATION_INVALID
         ),
-        invalid=sum(1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_INVALID),
         skipped=sum(1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_SKIPPED),
+        conflicts=sum(
+            1
+            for row in rows
+            if row.status != ASSESSMENT_IMPORT_ROW_SKIPPED
+            and row.conflict_status == ASSESSMENT_CONFLICT_UNRESOLVED
+        ),
+        creates=metric_actions.count(METRIC_ACTION_CREATE),
+        updates=metric_actions.count(METRIC_ACTION_UPDATE),
+        unchanged=metric_actions.count(METRIC_ACTION_UNCHANGED),
+        clears=metric_actions.count(METRIC_ACTION_CLEAR),
+        protected_manual=metric_actions.count(METRIC_ACTION_PROTECTED_MANUAL),
+        workbook_errors=len(batch.validation_errors),
+        workbook_warnings=len(batch.validation_warnings),
+        acknowledgement_required=acknowledgement_required,
+        acknowledgement_complete=acknowledgement_complete,
         checksum_seen_before=bool(batch.preview_snapshot.get("checksum_seen_before")),
     )


+def _warning_codes(batch: AssessmentImportBatch) -> list[str]:
+    issues = list(batch.validation_warnings)
+    for row in batch.rows.all():
+        issues.extend(row.warnings)
+        for change in row.metric_changes:
+            issues.extend(change.get("warnings", []))
+    return sorted(
+        {
+            issue.get("code")
+            for issue in issues
+            if issue.get("requires_ack") and issue.get("code")
+        }
+    )
+
+
+def _acknowledgement_token(batch: AssessmentImportBatch) -> str:
+    payload = {
+        "batch": batch.pk,
+        "workbook": batch.workbook_sha256,
+        "config": batch.config_checksum,
+        "preview_version": batch.preview_version,
+        "warning_codes": batch.required_warning_codes,
+        "row_state": list(
+            batch.rows.order_by("pk").values(
+                "pk",
+                "player_id",
+                "status",
+                "match_status",
+                "validation_status",
+                "conflict_status",
+                "metric_changes",
+            )
+        ),
+    }
+    return hashlib.sha256(_config_json(payload).encode("utf-8")).hexdigest()
+
+
+def _refresh_batch_state(batch: AssessmentImportBatch, *, bump_version=True):
+    if bump_version:
+        batch.preview_version += 1
+    batch.required_warning_codes = _warning_codes(batch)
+    batch.acknowledgement_token = _acknowledgement_token(batch)
+    batch.warnings_acknowledged_at = None
+    batch.warnings_acknowledged_by = None
+    batch.metadata.pop("acknowledged_token", None)
+    summary = _summary_counts(batch)
+    batch.import_summary = asdict(summary)
+    batch.preview_snapshot = {
+        **batch.preview_snapshot,
+        "summary": asdict(summary),
+        "mapping_version": batch.import_template.version,
+        "config_checksum": batch.config_checksum,
+    }
+    batch.save(
+        update_fields=[
+            "preview_version",
+            "required_warning_codes",
+            "acknowledgement_token",
+            "warnings_acknowledged_at",
+            "warnings_acknowledged_by",
+            "metadata",
+            "import_summary",
+            "preview_snapshot",
+            "updated_at",
+        ]
+    )
+    return summary
+
+
 def summarize_import_batch(batch: AssessmentImportBatch) -> AssessmentPreviewSummary:
-    """Return a read model summary for an assessment import batch."""
-    return _preview_summary(batch)
+    """Return the current authoritative preview summary."""
+    return _summary_counts(batch)
+
+
+def _validate_template_compatibility(event, import_template):
+    if not import_template.assessment_template_id:
+        raise ValidationError(
+            "Import template does not declare a compatible assessment template."
+        )
+    if import_template.assessment_template_id != event.template_id:
+        raise ValidationError(
+            "Import template is not compatible with the selected assessment event."
+        )
+    if event.scoring_profile_id:
+        if event.scoring_profile.assessment_template_id != event.template_id:
+            raise ValidationError(
+                "Assessment event scoring profile is not compatible with its template."
+            )


-@transaction.atomic
 def create_assessment_import_batch(
     *, file_obj, event, import_template, uploaded_by
 ) -> AssessmentImportBatch:
-    """Create a persisted preview batch without committing assessment values."""
+    """Create an auditable preview batch without committing assessment values."""
     filename = Path(file_obj.name).name
     if not filename.lower().endswith(".xlsx"):
         raise ValidationError("Upload an .xlsx workbook.")
+    _validate_template_compatibility(event, import_template)
+    frozen_config = deepcopy(import_template.config)
     content = _workbook_bytes(file_obj)
+    max_upload = _limits(frozen_config)["max_upload_bytes"]
+    if len(content) > max_upload:
+        raise ValidationError(
+            f"Workbook exceeds the configured {max_upload}-byte upload limit."
+        )
     checksum = workbook_sha256(content)
     checksum_seen_before = AssessmentImportBatch.objects.filter(
         event=event,
@@ -511,59 +1443,107 @@ def create_assessment_import_batch(
         uploaded_by=uploaded_by,
         original_filename=filename,
         workbook_sha256=checksum,
-        config_snapshot=json.loads(json.dumps(import_template.config)),
+        config_snapshot=frozen_config,
+        config_checksum=config_checksum(frozen_config),
         preview_snapshot={"checksum_seen_before": checksum_seen_before},
     )
     try:
-        parsed = parse_assessment_workbook(content, import_template)
+        parsed = parse_assessment_workbook(content, frozen_config)
         build_assessment_import_preview(batch=batch, parsed=parsed)
+    except ValidationError:
+        batch.status = ASSESSMENT_IMPORT_STATUS_FAILED
+        batch.validation_errors = [
+            _issue(
+                "workbook_parse_failed",
+                "Workbook could not be read safely. Verify the file and try again.",
+                blocking=True,
+            )
+        ]
+        batch.import_summary = {"errors": len(batch.validation_errors)}
+        batch.save(
+            update_fields=[
+                "status",
+                "validation_errors",
+                "import_summary",
+                "updated_at",
+            ]
+        )
     except Exception as exc:
         batch.status = ASSESSMENT_IMPORT_STATUS_FAILED
-        batch.import_summary = {"errors": [str(exc)]}
-        batch.save(update_fields=["status", "import_summary", "updated_at"])
-        raise
+        batch.validation_errors = [
+            _issue(
+                "workbook_parse_failed",
+                "Workbook parsing failed without creating assessment data.",
+                blocking=True,
+            )
+        ]
+        batch.metadata = {
+            **batch.metadata,
+            "failure_type": exc.__class__.__name__,
+        }
+        batch.import_summary = {"errors": len(batch.validation_errors)}
+        batch.save(
+            update_fields=[
+                "status",
+                "validation_errors",
+                "metadata",
+                "import_summary",
+                "updated_at",
+            ]
+        )
+    batch.refresh_from_db()
     return batch


-def _row_status_for_match(match, row_errors: list[str]) -> str:
-    if row_errors:
-        return ASSESSMENT_IMPORT_ROW_INVALID
-    if match.status == MATCH_AMBIGUOUS:
-        return ASSESSMENT_IMPORT_ROW_AMBIGUOUS
-    if match.status == MATCH_UNMATCHED:
-        return ASSESSMENT_IMPORT_ROW_UNMATCHED
-    if match.player:
-        return ASSESSMENT_IMPORT_ROW_MATCHED
-    return ASSESSMENT_IMPORT_ROW_UNMATCHED
-
-
 @transaction.atomic
 def build_assessment_import_preview(
     *, batch: AssessmentImportBatch, parsed: dict
 ) -> AssessmentPreviewSummary:
-    """Refresh import preview rows and conservative player matches."""
+    """Persist structural validation, identity matches, and per-metric actions."""
+    batch = AssessmentImportBatch.objects.select_for_update().get(pk=batch.pk)
     if batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
         raise ValidationError("Committed assessment imports cannot be previewed again.")
     batch.rows.all().delete()
-    workbook_errors = parsed.get("errors", [])
+    batch.validation_errors = list(parsed.get("errors", []))
+    batch.validation_warnings = list(parsed.get("warnings", []))
+    if batch.preview_snapshot.get("checksum_seen_before"):
+        batch.validation_warnings.append(
+            _issue(
+                "duplicate_workbook_checksum",
+                "This workbook checksum has already been committed for the event.",
+                requires_ack=True,
+            )
+        )
+    batch.status = ASSESSMENT_IMPORT_STATUS_PREVIEWED
+    batch.save(
+        update_fields=[
+            "validation_errors",
+            "validation_warnings",
+            "status",
+            "updated_at",
+        ]
+    )
     for parsed_row in parsed.get("rows", []):
         match = match_player_for_assessment(
             raw_name=parsed_row["raw_identity"],
             event=batch.event,
+            source_identifiers=parsed_row.get("source_identifiers", []),
+        )
+        row_errors = list(parsed_row.get("errors", []))
+        row_warnings = list(parsed_row.get("warnings", []))
+        validation_status = (
+            ASSESSMENT_VALIDATION_INVALID if row_errors else ASSESSMENT_VALIDATION_VALID
+        )
+        match_status = _match_status(match)
+        metric_changes = _plan_metric_changes(
+            parsed_row,
+            event=batch.event,
+            player=match.player,
         )
-        errors = list(parsed_row.get("errors", []))
-        if workbook_errors:
-            errors.extend(workbook_errors)
-        status = _row_status_for_match(match, errors)
-        action = "skip"
-        if status == ASSESSMENT_IMPORT_ROW_MATCHED:
-            action = "create_or_update"
-        elif status in {
-            ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
-            ASSESSMENT_IMPORT_ROW_UNMATCHED,
-        }:
-            action = "needs_review"
-        AssessmentImportRow.objects.create(
+        has_conflict = any(
+            change.get("action") == METRIC_ACTION_CONFLICT for change in metric_changes
+        )
+        row = AssessmentImportRow(
             batch=batch,
             row_key=parsed_row["row_key"],
             source_sheet=(parsed_row.get("source_rows") or [{}])[0].get("sheet", ""),
@@ -571,40 +1551,66 @@ def build_assessment_import_preview(
             raw_identity=parsed_row["raw_identity"],
             player=match.player,
             roster_membership=match.roster_membership,
-            action=action,
-            status=status,
-            errors=errors,
+            match_status=match_status,
+            validation_status=validation_status,
+            conflict_status=(
+                ASSESSMENT_CONFLICT_UNRESOLVED
+                if has_conflict
+                else ASSESSMENT_CONFLICT_NONE
+            ),
+            errors=row_errors,
+            warnings=row_warnings,
             values_snapshot=parsed_row.get("values", []),
-            raw_row={
-                "source_rows": parsed_row.get("source_rows", []),
-                "raw_rows": parsed_row.get("raw_rows", []),
-            },
+            metric_changes=metric_changes,
+            raw_row={"source_rows": parsed_row.get("source_rows", [])},
             metadata={
                 "match_reason": match.reason,
                 "candidate_ids": [candidate.pk for candidate in match.candidates],
+                "candidate_contexts": [
+                    {
+                        "player_id": context.player.pk,
+                        "birth_year": context.birth_year,
+                        "team": context.team,
+                        "division": context.division,
+                    }
+                    for context in match.candidate_contexts
+                ],
+                "source_identifiers": parsed_row.get("source_identifiers", []),
             },
         )
-    batch.status = ASSESSMENT_IMPORT_STATUS_PREVIEWED
-    summary = _preview_summary(batch)
+        row.status = _legacy_row_status(row)
+        row.action = _planned_row_action(row)
+        row.save()
+    if not batch.rows.filter(validation_status=ASSESSMENT_VALIDATION_VALID).exists():
+        batch.validation_errors.append(
+            _issue(
+                "no_valid_player_rows",
+                "No valid player rows are available for import.",
+                blocking=True,
+            )
+        )
+        batch.save(update_fields=["validation_errors", "updated_at"])
     batch.preview_snapshot = {
-        "checksum_seen_before": batch.preview_snapshot.get(
-            "checksum_seen_before", False
-        ),
+        **batch.preview_snapshot,
         "ranking_sheets": parsed.get("ranking_sheets", []),
-        "summary": summary.__dict__,
     }
-    batch.import_summary = summary.__dict__
-    batch.save(
-        update_fields=["status", "preview_snapshot", "import_summary", "updated_at"]
-    )
-    return summary
+    return _refresh_batch_state(batch)


 @transaction.atomic
 def resolve_assessment_import_row(
-    *, row: AssessmentImportRow, player: Player | None, skip: bool = False
+    *,
+    row: AssessmentImportRow,
+    player: Player | None,
+    skip: bool = False,
+    refresh_batch: bool = True,
 ):
-    """Resolve an unmatched/ambiguous preview row before commit."""
+    """Resolve only identity state, or explicitly skip any invalid row."""
+    row = (
+        AssessmentImportRow.objects.select_for_update()
+        .select_related("batch", "batch__event")
+        .get(pk=row.pk)
+    )
     if row.batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
         raise ValidationError("Committed assessment import rows cannot be changed.")
     if skip:
@@ -612,27 +1618,110 @@ def resolve_assessment_import_row(
         row.roster_membership = None
         row.status = ASSESSMENT_IMPORT_ROW_SKIPPED
         row.action = "skip"
+    elif row.validation_status == ASSESSMENT_VALIDATION_INVALID:
+        raise ValidationError(
+            "Choosing a player cannot resolve data-validation errors; correct or skip the row."
+        )
     elif player is None:
         raise ValidationError("Choose a player or skip the row.")
     else:
         row.player = player
         row.roster_membership = (
             player.roster_memberships.select_related("season_team")
-            .filter(season_team__season=row.batch.event.season, is_active=True)
+            .filter(
+                season_team__season=row.batch.event.season,
+                is_active=True,
+            )
             .order_by("-is_primary", "id")
             .first()
         )
-        row.status = ASSESSMENT_IMPORT_ROW_MATCHED
-        row.action = "create_or_update"
-    row.save(
-        update_fields=["player", "roster_membership", "status", "action", "updated_at"]
+        row.match_status = ASSESSMENT_MATCH_MATCHED
+        parsed_row = {"values": row.values_snapshot}
+        row.metric_changes = _plan_metric_changes(
+            parsed_row,
+            event=row.batch.event,
+            player=player,
+        )
+        row.conflict_status = (
+            ASSESSMENT_CONFLICT_UNRESOLVED
+            if any(
+                change.get("action") == METRIC_ACTION_CONFLICT
+                for change in row.metric_changes
+            )
+            else ASSESSMENT_CONFLICT_NONE
+        )
+        row.status = _legacy_row_status(row)
+        row.action = _planned_row_action(row)
+    row.save()
+    if refresh_batch:
+        _refresh_batch_state(row.batch)
+    return row
+
+
+@transaction.atomic
+def preserve_manual_override_conflicts(*, row: AssessmentImportRow, actor):
+    """Resolve import conflicts by preserving every existing manual correction."""
+    if not actor.is_staff and not actor.is_superuser:
+        raise PermissionDenied("Only staff can resolve assessment import conflicts.")
+    row = (
+        AssessmentImportRow.objects.select_for_update()
+        .select_related("batch")
+        .get(pk=row.pk)
     )
-    summary = _preview_summary(row.batch)
-    row.batch.import_summary = summary.__dict__
-    row.batch.save(update_fields=["import_summary", "updated_at"])
+    if row.batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
+        raise ValidationError("Committed assessment import rows cannot be changed.")
+    changes = deepcopy(row.metric_changes)
+    conflict_found = False
+    for change in changes:
+        if change.get("action") == METRIC_ACTION_CONFLICT:
+            conflict_found = True
+            change["action"] = METRIC_ACTION_PROTECTED_MANUAL
+            change["resolution"] = "preserve_manual"
+    if not conflict_found:
+        raise ValidationError("This row has no manual-override conflict to resolve.")
+    row.metric_changes = changes
+    row.conflict_status = ASSESSMENT_CONFLICT_RESOLVED
+    row.status = _legacy_row_status(row)
+    row.action = _planned_row_action(row)
+    row.save()
+    _refresh_batch_state(row.batch)
     return row


+@transaction.atomic
+def acknowledge_assessment_import_warnings(*, batch, actor, token):
+    """Persist acknowledgement only for the current immutable preview state."""
+    if not actor.is_staff and not actor.is_superuser:
+        raise PermissionDenied("Only staff can acknowledge assessment warnings.")
+    batch = AssessmentImportBatch.objects.select_for_update().get(pk=batch.pk)
+    summary = _summary_counts(batch)
+    if not summary.structurally_ready:
+        raise ValidationError(
+            "Resolve all blocking issues before acknowledging warnings."
+        )
+    if not batch.required_warning_codes:
+        raise ValidationError("This assessment import has no warnings to acknowledge.")
+    if not token or token != batch.acknowledgement_token:
+        raise ValidationError(
+            "Warning acknowledgement is stale; review the latest preview."
+        )
+    batch.warnings_acknowledged_at = timezone.now()
+    batch.warnings_acknowledged_by = actor
+    batch.metadata = {
+        **batch.metadata,
+        "acknowledged_token": batch.acknowledgement_token,
+    }
+    batch.save(
+        update_fields=[
+            "warnings_acknowledged_at",
+            "warnings_acknowledged_by",
+            "metadata",
+            "updated_at",
+        ]
+    )
+    return _summary_counts(batch)
+
+
 def _metric_by_key(event) -> dict[str, AssessmentTemplateMetric]:
     return {
         template_metric.metric.key: template_metric
@@ -640,215 +1729,680 @@ def _metric_by_key(event) -> dict[str, AssessmentTemplateMetric]:
     }


-def _apply_snapshot_value(
+def _assign_snapshot_value(value: AssessmentValue, snapshot: dict):
+    value.numeric_value = None
+    value.rating_value = None
+    value.text_value = ""
+    value.choice_value = ""
+    value.raw_value = snapshot.get("raw_value", "")
+    value.normalized_value = snapshot.get("normalized_value", "")
+    value.unit = snapshot.get("unit", "")
+    value.source_sheet = snapshot.get("source_sheet", "")
+    value.source_row = snapshot.get("source_row")
+    value.source_column = snapshot.get("source_column", "")
+    value.source_header = snapshot.get("source_header", snapshot.get("header", ""))
+    value.source_kind = ASSESSMENT_VALUE_SOURCE_IMPORTED
+    value.is_imported = True
+    value.is_manual_override = False
+    value.metadata = {
+        "unit_status": snapshot.get("unit_status", "not_applicable"),
+        "unit_source": snapshot.get("unit_source", ""),
+        "zero_policy": snapshot.get("zero_policy", ZERO_ALLOW),
+        "blank_policy": snapshot.get("blank_policy", BLANK_PRESERVE),
+        "transformations": snapshot.get("transformations", []),
+    }
+    if snapshot.get("value_type") == ASSESSMENT_VALUE_TYPE_RATING:
+        value.rating_value = Decimal(snapshot["normalized_value"])
+        value.rating_scale_min = Decimal(str(snapshot["rating_scale_min"]))
+        value.rating_scale_max = Decimal(str(snapshot["rating_scale_max"]))
+    elif snapshot.get("value_type") == ASSESSMENT_VALUE_TYPE_NUMBER:
+        value.numeric_value = Decimal(snapshot["normalized_value"])
+        value.rating_scale_min = None
+        value.rating_scale_max = None
+    else:
+        value.text_value = snapshot.get("text_value", snapshot.get("raw_value", ""))
+        value.rating_scale_min = None
+        value.rating_scale_max = None
+
+
+def _apply_metric_change(
     *,
-    player_assessment: PlayerAssessment,
-    template_metric: AssessmentTemplateMetric,
-    import_row: AssessmentImportRow,
-    snapshot: dict,
+    player_assessment,
+    template_metric,
+    import_row,
+    snapshot,
+    change,
 ):
     existing = AssessmentValue.objects.filter(
         player_assessment=player_assessment,
         template_metric=template_metric,
     ).first()
+    action = change["action"]
+    if action in {
+        METRIC_ACTION_SKIP,
+        METRIC_ACTION_UNCHANGED,
+        METRIC_ACTION_PROTECTED_MANUAL,
+    }:
+        return action
+    if action == METRIC_ACTION_CLEAR:
+        if existing:
+            if existing.is_manual_override:
+                raise ValidationError("Manual corrections cannot be cleared by import.")
+            existing._allow_committed_change = True
+            existing.delete()
+        return action
+    if action not in {METRIC_ACTION_CREATE, METRIC_ACTION_UPDATE}:
+        raise ValidationError("Assessment import contains an unresolved metric action.")
     if existing and existing.is_manual_override:
-        raise ValidationError(
-            f"Manual override exists for {player_assessment.player} / {template_metric.display_name}."
-        )
-    defaults = {
-        "raw_value": snapshot.get("raw_value", ""),
-        "normalized_value": snapshot.get("numeric_value")
-        or snapshot.get("text_value", ""),
-        "unit": snapshot.get("unit", ""),
-        "source_sheet": snapshot.get("source_sheet", ""),
-        "source_row": snapshot.get("source_row"),
-        "source_column": snapshot.get("source_column", ""),
-        "source_header": snapshot.get("header", ""),
-        "source_kind": ASSESSMENT_VALUE_SOURCE_IMPORTED,
-        "is_imported": True,
-        "import_row": import_row,
-    }
-    value_type = snapshot.get("value_type")
-    if value_type == ASSESSMENT_VALUE_TYPE_RATING:
-        defaults["rating_value"] = Decimal(snapshot["numeric_value"])
-        defaults["rating_scale_min"] = template_metric.rating_scale_min
-        defaults["rating_scale_max"] = template_metric.rating_scale_max
-    elif value_type == ASSESSMENT_VALUE_TYPE_NUMBER:
-        defaults["numeric_value"] = Decimal(snapshot["numeric_value"])
-    else:
-        defaults["text_value"] = snapshot.get(
-            "text_value", snapshot.get("raw_value", "")
-        )
-    AssessmentValue.objects.update_or_create(
+        raise ValidationError("Assessment import cannot overwrite a manual correction.")
+    value = existing or AssessmentValue(
         player_assessment=player_assessment,
         template_metric=template_metric,
-        defaults=defaults,
     )
+    _assign_snapshot_value(value, snapshot)
+    value.import_row = import_row
+    value._allow_committed_change = True
+    value.save()
+    return action
+
+
+def _validate_commit_ready(batch: AssessmentImportBatch):
+    if batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
+        raise ValidationError("This assessment import has already been committed.")
+    if batch.status != ASSESSMENT_IMPORT_STATUS_PREVIEWED:
+        raise ValidationError("Only a successfully previewed import can be committed.")
+    _validate_template_compatibility(batch.event, batch.import_template)
+    if config_checksum(batch.config_snapshot) != batch.config_checksum:
+        raise ValidationError("Frozen import configuration checksum is invalid.")
+    summary = _summary_counts(batch)
+    if not summary.can_commit:
+        raise ValidationError(
+            "Assessment import is not ready: resolve workbook, row, identity, conflict, and warning issues first."
+        )
+    if batch.validation_errors:
+        raise ValidationError("Workbook-level validation errors block this import.")
+    blocking_rows = batch.rows.exclude(status=ASSESSMENT_IMPORT_ROW_SKIPPED).filter(
+        Q(validation_status=ASSESSMENT_VALIDATION_INVALID)
+        | ~Q(match_status=ASSESSMENT_MATCH_MATCHED)
+        | Q(conflict_status=ASSESSMENT_CONFLICT_UNRESOLVED)
+    )
+    if blocking_rows.exists():
+        raise ValidationError(
+            "Row-level validation or resolution issues block this import."
+        )
+    if not batch.rows.exclude(status=ASSESSMENT_IMPORT_ROW_SKIPPED).exists():
+        raise ValidationError("At least one valid player row is required.")


 @transaction.atomic
 def commit_assessment_import_batch(
     *, batch: AssessmentImportBatch, actor
 ) -> AssessmentCommitResult:
-    """Commit a fully resolved preview batch into PlayerAssessment records."""
+    """Commit the frozen, fully resolved metric plan atomically."""
     if not actor.is_staff and not actor.is_superuser:
         raise PermissionDenied("Only staff can commit assessment imports.")
-    batch = AssessmentImportBatch.objects.select_for_update().get(pk=batch.pk)
-    if batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
-        raise ValidationError("This assessment import has already been committed.")
-    unresolved = batch.rows.exclude(
-        status__in=[ASSESSMENT_IMPORT_ROW_MATCHED, ASSESSMENT_IMPORT_ROW_SKIPPED]
-    )
-    if unresolved.exists():
-        raise ValidationError(
-            "Resolve or skip all unmatched, ambiguous, or invalid rows before committing."
+    batch = (
+        AssessmentImportBatch.objects.select_for_update()
+        .select_related(
+            "event",
+            "event__template",
+            "event__scoring_profile",
+            "import_template",
         )
+        .get(pk=batch.pk)
+    )
+    _validate_commit_ready(batch)
     metrics = _metric_by_key(batch.event)
-    created = 0
-    updated = 0
-    skipped = 0
-    for row in batch.rows.select_related("player", "roster_membership"):
+    created = updated = unchanged = skipped = 0
+    value_counts = {
+        METRIC_ACTION_CREATE: 0,
+        METRIC_ACTION_UPDATE: 0,
+        METRIC_ACTION_CLEAR: 0,
+        METRIC_ACTION_UNCHANGED: 0,
+        METRIC_ACTION_PROTECTED_MANUAL: 0,
+    }
+    for row in batch.rows.select_for_update().select_related("player"):
         if row.status == ASSESSMENT_IMPORT_ROW_SKIPPED:
             skipped += 1
             continue
         if not row.player_id:
-            raise ValidationError("Resolved assessment import rows require a player.")
-        player_assessment, was_created = PlayerAssessment.objects.get_or_create(
+            raise ValidationError("Every committed import row requires a player.")
+        player_assessment = PlayerAssessment.objects.filter(
             player=row.player,
             event=batch.event,
-            defaults={
-                "roster_membership": row.roster_membership,
-                "import_batch": batch,
-                "source_row_key": row.row_key,
-                "status": ASSESSMENT_STATUS_COMMITTED,
-            },
-        )
+        ).first()
+        was_created = player_assessment is None
         if was_created:
-            created += 1
-        else:
-            updated += 1
-            player_assessment.roster_membership = (
-                row.roster_membership or player_assessment.roster_membership
+            player_assessment = PlayerAssessment.objects.create(
+                player=row.player,
+                event=batch.event,
+                roster_membership=row.roster_membership,
+                import_batch=batch,
+                source_row_key=row.row_key,
+                status=ASSESSMENT_STATUS_DRAFT,
+                metadata={"initial_import_batch_id": batch.pk},
             )
-            player_assessment.import_batch = batch
-            player_assessment.source_row_key = row.row_key
-            player_assessment.status = ASSESSMENT_STATUS_COMMITTED
-            player_assessment.save()
-        for snapshot in row.values_snapshot:
-            template_metric = metrics.get(snapshot.get("metric_key"))
+            created += 1
+        snapshots = {
+            snapshot["metric_key"]: snapshot for snapshot in row.values_snapshot
+        }
+        changed = False
+        for change in row.metric_changes:
+            if change.get("action") in {METRIC_ACTION_CONFLICT, METRIC_ACTION_INVALID}:
+                raise ValidationError("Unresolved metric actions block this import.")
+            template_metric = metrics.get(change.get("metric_key"))
             if template_metric is None:
                 raise ValidationError(
-                    f"Unknown assessment metric: {snapshot.get('metric_key')}."
+                    f"Unknown assessment metric: {change.get('metric_key')}."
                 )
-            _apply_snapshot_value(
+            snapshot = snapshots.get(change["metric_key"])
+            if snapshot is None:
+                raise ValidationError("Frozen metric snapshot is missing.")
+            action = _apply_metric_change(
                 player_assessment=player_assessment,
                 template_metric=template_metric,
                 import_row=row,
                 snapshot=snapshot,
+                change=change,
             )
+            if action in value_counts:
+                value_counts[action] += 1
+            if action in {
+                METRIC_ACTION_CREATE,
+                METRIC_ACTION_UPDATE,
+                METRIC_ACTION_CLEAR,
+            }:
+                changed = True
+        if was_created:
+            player_assessment.status = ASSESSMENT_STATUS_COMMITTED
+            player_assessment.save(update_fields=["status", "updated_at"])
+        elif changed:
+            updated += 1
+        else:
+            unchanged += 1
         row.status = ASSESSMENT_IMPORT_ROW_COMMITTED
         row.save(update_fields=["status", "updated_at"])
     batch.status = ASSESSMENT_IMPORT_STATUS_COMMITTED
     batch.committed_at = timezone.now()
     result = AssessmentCommitResult(
-        processed=created + updated + skipped,
+        processed=created + updated + unchanged + skipped,
         created=created,
         updated=updated,
+        unchanged=unchanged,
         skipped=skipped,
+        values_created=value_counts[METRIC_ACTION_CREATE],
+        values_updated=value_counts[METRIC_ACTION_UPDATE],
+        values_cleared=value_counts[METRIC_ACTION_CLEAR],
+        values_unchanged=value_counts[METRIC_ACTION_UNCHANGED],
+        values_protected=value_counts[METRIC_ACTION_PROTECTED_MANUAL],
     )
-    batch.import_summary = result.__dict__
+    batch.import_summary = asdict(result)
     batch.save(update_fields=["status", "committed_at", "import_summary", "updated_at"])
-    batch.event.template.is_locked = True
-    batch.event.template.save(update_fields=["is_locked", "updated_at"])
-    batch.import_template.is_locked = True
-    batch.import_template.save(update_fields=["is_locked", "updated_at"])
-    if batch.event.scoring_profile_id:
-        batch.event.scoring_profile.is_locked = True
-        batch.event.scoring_profile.save(update_fields=["is_locked", "updated_at"])
+    for locked_object in [
+        batch.event.template,
+        batch.import_template,
+        batch.event.scoring_profile,
+    ]:
+        if locked_object and not locked_object.is_locked:
+            locked_object.is_locked = True
+            locked_object.save(update_fields=["is_locked", "updated_at"])
     return result


+def _correction_value_snapshot(value: AssessmentValue) -> dict:
+    return _value_snapshot(value) or {}
+
+
+@transaction.atomic
+def correct_assessment_value(*, assessment_value, actor, reason, new_value):
+    """Apply an audited staff correction without permitting import replacement."""
+    if not actor.is_staff and not actor.is_superuser:
+        raise PermissionDenied("Only staff can correct assessment values.")
+    reason = str(reason or "").strip()
+    if not reason:
+        raise ValidationError("A correction reason is required.")
+    value = (
+        AssessmentValue.objects.select_for_update()
+        .select_related("template_metric")
+        .get(pk=assessment_value.pk)
+    )
+    previous = _correction_value_snapshot(value)
+    metric = value.template_metric
+    snapshot = {
+        "value_type": metric.value_type,
+        "raw_value": str(new_value),
+        "normalized_value": str(new_value),
+        "unit": metric.unit,
+        "unit_status": metric.metadata.get("unit_status", "not_applicable"),
+        "rating_scale_min": metric.rating_scale_min,
+        "rating_scale_max": metric.rating_scale_max,
+        "source_sheet": "",
+        "source_row": None,
+        "source_column": "",
+        "source_header": metric.display_name,
+        "zero_policy": metric.metadata.get("zero_policy", ZERO_ALLOW),
+        "blank_policy": metric.metadata.get("blank_policy", BLANK_PRESERVE),
+        "transformations": [],
+    }
+    if metric.value_type in {
+        ASSESSMENT_VALUE_TYPE_NUMBER,
+        ASSESSMENT_VALUE_TYPE_RATING,
+    }:
+        decimal_value = _decimal_or_none(new_value)
+        if decimal_value is None:
+            raise ValidationError("Correction must be a valid finite number.")
+        if metric.min_value is not None and decimal_value < metric.min_value:
+            raise ValidationError("Correction is below the metric minimum.")
+        if metric.max_value is not None and decimal_value > metric.max_value:
+            raise ValidationError("Correction is above the metric maximum.")
+        if metric.value_type == ASSESSMENT_VALUE_TYPE_RATING:
+            if decimal_value != decimal_value.to_integral_value():
+                raise ValidationError("Rating corrections must be whole numbers.")
+            if (
+                metric.rating_scale_min is None
+                or metric.rating_scale_max is None
+                or decimal_value < metric.rating_scale_min
+                or decimal_value > metric.rating_scale_max
+            ):
+                raise ValidationError("Correction is outside the rating scale.")
+        snapshot["normalized_value"] = str(decimal_value)
+    else:
+        snapshot["text_value"] = str(new_value)
+    _assign_snapshot_value(value, snapshot)
+    value.source_kind = ASSESSMENT_VALUE_SOURCE_MANUAL_CORRECTED
+    value.is_imported = False
+    value.is_manual_override = True
+    value.metadata = {
+        **value.metadata,
+        "correction_reason": reason,
+        "corrected_at": timezone.now().isoformat(),
+        "corrected_by_id": actor.pk,
+    }
+    value._allow_committed_change = True
+    value.save()
+    current = _correction_value_snapshot(value)
+    AssessmentValueCorrection.objects.create(
+        assessment_value=value,
+        actor=actor,
+        reason=reason,
+        previous_snapshot=previous,
+        new_snapshot=current,
+        provenance={"source_kind": ASSESSMENT_VALUE_SOURCE_MANUAL_CORRECTED},
+    )
+    return value
+
+
 def default_2026_13u_config() -> dict:
-    """Return configuration derived from the supplied 2026 13U workbook headers."""
+    """Return the versioned mapping verified against the supplied 2026 workbook."""
     return {
-        "sheets": DEFAULT_2026_13U_DATA_SHEETS,
+        "mapping_version": 1,
+        "sheets": deepcopy(DEFAULT_2026_13U_DATA_SHEETS),
         "ranking_sheets": DEFAULT_2026_13U_RANKING_SHEETS,
-        "notes": "Ranking sheets are provenance/QA only and are not imported as player metrics.",
+        "limits": {
+            "max_upload_bytes": DEFAULT_MAX_UPLOAD_BYTES,
+            "max_archive_uncompressed_bytes": DEFAULT_MAX_UNCOMPRESSED_BYTES,
+            "max_worksheets": DEFAULT_MAX_WORKSHEETS,
+            "max_rows": DEFAULT_MAX_ROWS,
+            "max_columns": DEFAULT_MAX_COLUMNS,
+            "max_cell_text_length": DEFAULT_MAX_CELL_TEXT_LENGTH,
+        },
+        "notes": (
+            "Ranking sheets are QA/provenance only. Physical measurement units are "
+            "unverified because the workbook does not state them."
+        ),
     }


+def _expected_metric_rows(config):
+    display_order = 0
+    for sheet_config in config["sheets"]:
+        for metric_config in sheet_config["metrics"]:
+            display_order += 10
+            yield sheet_config, metric_config, display_order
+
+
+def _field_conflicts(instance, expected):
+    conflicts = {}
+    for field_name, expected_value in expected.items():
+        actual_value = getattr(instance, field_name)
+        if actual_value != expected_value:
+            conflicts[field_name] = {
+                "actual": actual_value,
+                "expected": expected_value,
+            }
+    return conflicts
+
+
+def _assert_fields(object_name, instance, expected):
+    conflicts = _field_conflicts(instance, expected)
+    if conflicts:
+        raise ValidationError(
+            f"Existing {object_name} configuration conflicts with the expected version: {conflicts}"
+        )
+
+
+def _configuration_plan(config) -> dict:
+    metric_details = []
+    for sheet_config, metric_config, _ in _expected_metric_rows(config):
+        metric_details.append(
+            {
+                "key": metric_config["key"],
+                "sheet": sheet_config["name"],
+                "header": metric_config["header"],
+                "value_type": metric_config["value_type"],
+                "rating_scale": (
+                    [
+                        metric_config.get("rating_scale_min"),
+                        metric_config.get("rating_scale_max"),
+                    ]
+                    if metric_config["value_type"] == ASSESSMENT_VALUE_TYPE_RATING
+                    else None
+                ),
+                "unit": metric_config.get("unit", ""),
+                "unit_status": metric_config.get("unit_status", "not_applicable"),
+                "zero_policy": metric_config.get("zero_policy"),
+                "blank_policy": metric_config.get("blank_policy"),
+                "required_header": metric_config.get("required_header", True),
+            }
+        )
+    return {
+        "template": {
+            "key": BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
+            "version": 1,
+        },
+        "import_template": {
+            "key": BOOTSTRAP_2026_13U_IMPORT_KEY,
+            "version": 1,
+            "config_checksum": config_checksum(config),
+        },
+        "scoring_profile": {
+            "key": BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
+            "version": 1,
+        },
+        "required_sheets": [
+            sheet["name"] for sheet in config["sheets"] if sheet.get("required", True)
+        ],
+        "optional_sheets": [
+            sheet["name"]
+            for sheet in config["sheets"]
+            if not sheet.get("required", True)
+        ],
+        "sheets": [
+            {
+                "name": sheet["name"],
+                "required": sheet.get("required", True),
+                "header_row": sheet.get("header_row", 1),
+                "identity_column": sheet.get("identity_column", "Name"),
+                "required_headers": [
+                    metric["header"]
+                    for metric in sheet.get("metrics", [])
+                    if metric.get("required_header", True)
+                ],
+            }
+            for sheet in config["sheets"]
+        ],
+        "metrics": metric_details,
+    }
+
+
+def _dry_run_state(*, label, instance, expected):
+    conflicts = _field_conflicts(instance, expected) if instance else {}
+    return {
+        "object": label,
+        "state": (
+            "create" if instance is None else ("conflict" if conflicts else "present")
+        ),
+        "locked": bool(instance and getattr(instance, "is_locked", False)),
+        "conflicts": conflicts,
+    }
+
+
+def _dry_run_configuration_states(config) -> list[dict]:
+    template = AssessmentTemplate.objects.filter(
+        key=BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
+        version=1,
+    ).first()
+    states = [
+        _dry_run_state(
+            label="template",
+            instance=template,
+            expected={"name": "2026 VCB House 13U PeeWee Assessment"},
+        )
+    ]
+    scoring_config = {"source": "workbook", "computed_scores": []}
+    scoring_profile = AssessmentScoringProfile.objects.filter(
+        key=BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
+        version=1,
+    ).first()
+    states.append(
+        _dry_run_state(
+            label="scoring_profile",
+            instance=scoring_profile,
+            expected={
+                "name": "2026 VCB House 13U PeeWee Assessment Scoring",
+                "assessment_template_id": template.pk if template else None,
+                "config": scoring_config,
+            },
+        )
+    )
+    import_template = AssessmentImportTemplate.objects.filter(
+        key=BOOTSTRAP_2026_13U_IMPORT_KEY,
+        version=1,
+    ).first()
+    states.append(
+        _dry_run_state(
+            label="import_template",
+            instance=import_template,
+            expected={
+                "name": "2026 VCB House 13U PeeWee Assessment Workbook",
+                "assessment_template_id": template.pk if template else None,
+                "config": config,
+            },
+        )
+    )
+    for sheet_config, metric_config, display_order in _expected_metric_rows(config):
+        metric = AssessmentMetricDefinition.objects.filter(
+            key=metric_config["key"]
+        ).first()
+        value_type = metric_config["value_type"]
+        states.append(
+            _dry_run_state(
+                label=f"metric:{metric_config['key']}",
+                instance=metric,
+                expected={
+                    "name": metric_config["header"].strip(),
+                    "default_value_type": value_type,
+                    "default_unit": metric_config.get("unit", ""),
+                    "metadata": {
+                        "unit_status": metric_config.get(
+                            "unit_status", "not_applicable"
+                        ),
+                        "unit_source": metric_config.get("unit_source", ""),
+                    },
+                },
+            )
+        )
+        template_metric = None
+        if template and metric:
+            template_metric = AssessmentTemplateMetric.objects.filter(
+                template=template,
+                metric=metric,
+            ).first()
+        metric_metadata = {
+            "source_sheet": sheet_config["name"],
+            "source_header": metric_config["header"],
+            "unit_status": metric_config.get("unit_status", "not_applicable"),
+            "unit_source": metric_config.get("unit_source", ""),
+            "zero_policy": metric_config.get("zero_policy", ZERO_ALLOW),
+            "blank_policy": metric_config.get("blank_policy", BLANK_PRESERVE),
+            "allowed_choices": metric_config.get("allowed_choices", []),
+            "integer_only": metric_config.get("integer_only", False),
+        }
+        states.append(
+            _dry_run_state(
+                label=f"template_metric:{metric_config['key']}",
+                instance=template_metric,
+                expected={
+                    "category": metric_config.get("category", sheet_config["name"]),
+                    "display_name": metric_config["header"].strip(),
+                    "display_order": display_order,
+                    "value_type": value_type,
+                    "unit": metric_config.get("unit", ""),
+                    "direction": metric_config.get("direction", "neutral"),
+                    "min_value": _decimal_or_none(metric_config.get("min_value")),
+                    "max_value": _decimal_or_none(metric_config.get("max_value")),
+                    "rating_scale_min": _decimal_or_none(
+                        metric_config.get("rating_scale_min")
+                    ),
+                    "rating_scale_max": _decimal_or_none(
+                        metric_config.get("rating_scale_max")
+                    ),
+                    "metadata": metric_metadata,
+                },
+            )
+        )
+    return states
+
+
 @transaction.atomic
 def ensure_2026_13u_assessment_configuration(*, dry_run: bool = False) -> dict:
-    """Create idempotent assessment/import templates for the 2026 13U workbook."""
+    """Create exact versioned configuration or fail on any existing conflict."""
     config = default_2026_13u_config()
-    plan = {
-        "metrics": [],
-        "template": BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
-        "import_template": BOOTSTRAP_2026_13U_IMPORT_KEY,
-    }
+    plan = _configuration_plan(config)
+    plan["states"] = _dry_run_configuration_states(config)
     if dry_run:
-        for sheet_config in config["sheets"]:
-            for metric_config in sheet_config["metrics"]:
-                plan["metrics"].append(metric_config["key"])
         return plan
-    template, _ = AssessmentTemplate.objects.get_or_create(
+
+    template, created = AssessmentTemplate.objects.get_or_create(
         key=BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
         version=1,
         defaults={"name": "2026 VCB House 13U PeeWee Assessment"},
     )
-    AssessmentScoringProfile.objects.get_or_create(
+    if not created:
+        _assert_fields(
+            "assessment template",
+            template,
+            {"name": "2026 VCB House 13U PeeWee Assessment"},
+        )
+    scoring_config = {"source": "workbook", "computed_scores": []}
+    scoring_profile, created = AssessmentScoringProfile.objects.get_or_create(
         key=BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
         version=1,
         defaults={
             "name": "2026 VCB House 13U PeeWee Assessment Scoring",
-            "config": {"source": "spreadsheet-derived", "computed_scores": []},
+            "assessment_template": template,
+            "config": scoring_config,
         },
     )
-    AssessmentImportTemplate.objects.get_or_create(
+    if not created:
+        _assert_fields(
+            "scoring profile",
+            scoring_profile,
+            {
+                "name": "2026 VCB House 13U PeeWee Assessment Scoring",
+                "assessment_template_id": template.pk,
+                "config": scoring_config,
+            },
+        )
+    import_template, created = AssessmentImportTemplate.objects.get_or_create(
         key=BOOTSTRAP_2026_13U_IMPORT_KEY,
         version=1,
         defaults={
             "name": "2026 VCB House 13U PeeWee Assessment Workbook",
+            "assessment_template": template,
             "config": config,
         },
     )
-    display_order = 0
-    for sheet_config in config["sheets"]:
-        for metric_config in sheet_config["metrics"]:
-            display_order += 10
-            value_type = metric_config.get("value_type") or ASSESSMENT_VALUE_TYPE_NUMBER
-            metric, _ = AssessmentMetricDefinition.objects.get_or_create(
-                key=metric_config["key"],
-                defaults={
+    if not created:
+        _assert_fields(
+            "import template",
+            import_template,
+            {
+                "name": "2026 VCB House 13U PeeWee Assessment Workbook",
+                "assessment_template_id": template.pk,
+                "config": config,
+            },
+        )
+
+    for sheet_config, metric_config, display_order in _expected_metric_rows(config):
+        value_type = metric_config["value_type"]
+        metric, created = AssessmentMetricDefinition.objects.get_or_create(
+            key=metric_config["key"],
+            defaults={
+                "name": metric_config["header"].strip(),
+                "default_value_type": value_type,
+                "default_unit": metric_config.get("unit", ""),
+                "metadata": {
+                    "unit_status": metric_config.get("unit_status", "not_applicable"),
+                    "unit_source": metric_config.get("unit_source", ""),
+                },
+            },
+        )
+        if not created:
+            _assert_fields(
+                f"metric {metric_config['key']}",
+                metric,
+                {
                     "name": metric_config["header"].strip(),
                     "default_value_type": value_type,
                     "default_unit": metric_config.get("unit", ""),
+                    "metadata": {
+                        "unit_status": metric_config.get(
+                            "unit_status", "not_applicable"
+                        ),
+                        "unit_source": metric_config.get("unit_source", ""),
+                    },
                 },
             )
-            AssessmentTemplateMetric.objects.get_or_create(
-                template=template,
-                metric=metric,
-                defaults={
+        metric_metadata = {
+            "source_sheet": sheet_config["name"],
+            "source_header": metric_config["header"],
+            "unit_status": metric_config.get("unit_status", "not_applicable"),
+            "unit_source": metric_config.get("unit_source", ""),
+            "zero_policy": metric_config.get("zero_policy", ZERO_ALLOW),
+            "blank_policy": metric_config.get("blank_policy", BLANK_PRESERVE),
+            "allowed_choices": metric_config.get("allowed_choices", []),
+            "integer_only": metric_config.get("integer_only", False),
+        }
+        template_metric, created = AssessmentTemplateMetric.objects.get_or_create(
+            template=template,
+            metric=metric,
+            defaults={
+                "category": metric_config.get("category", sheet_config["name"]),
+                "display_name": metric_config["header"].strip(),
+                "display_order": display_order,
+                "value_type": value_type,
+                "unit": metric_config.get("unit", ""),
+                "direction": metric_config.get("direction", "neutral"),
+                "min_value": metric_config.get("min_value"),
+                "max_value": metric_config.get("max_value"),
+                "rating_scale_min": metric_config.get("rating_scale_min"),
+                "rating_scale_max": metric_config.get("rating_scale_max"),
+                "metadata": metric_metadata,
+            },
+        )
+        if not created:
+            _assert_fields(
+                f"template metric {metric_config['key']}",
+                template_metric,
+                {
                     "category": metric_config.get("category", sheet_config["name"]),
                     "display_name": metric_config["header"].strip(),
                     "display_order": display_order,
                     "value_type": value_type,
                     "unit": metric_config.get("unit", ""),
                     "direction": metric_config.get("direction", "neutral"),
-                    "rating_scale_min": (
-                        Decimal("1")
-                        if value_type == ASSESSMENT_VALUE_TYPE_RATING
-                        else None
+                    "min_value": _decimal_or_none(metric_config.get("min_value")),
+                    "max_value": _decimal_or_none(metric_config.get("max_value")),
+                    "rating_scale_min": _decimal_or_none(
+                        metric_config.get("rating_scale_min")
                     ),
-                    "rating_scale_max": (
-                        Decimal("5")
-                        if value_type == ASSESSMENT_VALUE_TYPE_RATING
-                        else None
+                    "rating_scale_max": _decimal_or_none(
+                        metric_config.get("rating_scale_max")
                     ),
-                    "metadata": {"source_sheet": sheet_config["name"]},
+                    "metadata": metric_metadata,
                 },
             )
-            plan["metrics"].append(metric_config["key"])
     return plan


diff --git a/analytics/services/assessment_matching_service.py b/analytics/services/assessment_matching_service.py
index dc43875..7f45d7c 100644
--- a/analytics/services/assessment_matching_service.py
+++ b/analytics/services/assessment_matching_service.py
@@ -2,23 +2,37 @@ from __future__ import annotations

 from dataclasses import dataclass

+from django.db.models import CharField, F, Q, Value
+from django.db.models.functions import Coalesce, Concat, Lower, Trim
+
 from players.models import Player, PlayerAlias, PlayerSourceIdentifier
 from players.models import normalize_lookup_value as normalize_player_lookup_value
-from seasons.models import PlayerRosterMembership
+from seasons.models import PlayerRosterMembership, normalize_lookup_value

 MATCH_EXACT_IDENTIFIER = "exact_identifier"
-MATCH_EXACT_NAME = "exact_name"
-MATCH_ALIAS = "alias"
+MATCH_EXACT_ROSTER_NAME = "exact_roster_name"
+MATCH_EXACT_ROSTER_ALIAS = "exact_roster_alias"
+MATCH_EXACT_GLOBAL_NAME = "exact_global_name"
+MATCH_EXACT_GLOBAL_ALIAS = "exact_global_alias"
 MATCH_UNMATCHED = "unmatched"
 MATCH_AMBIGUOUS = "ambiguous"


+@dataclass(frozen=True)
+class AssessmentMatchCandidate:
+    player: Player
+    birth_year: int | None
+    team: str
+    division: str
+
+
 @dataclass(frozen=True)
 class AssessmentMatchResult:
     status: str
     player: Player | None = None
     roster_membership: PlayerRosterMembership | None = None
     candidates: tuple[Player, ...] = ()
+    candidate_contexts: tuple[AssessmentMatchCandidate, ...] = ()
     reason: str = ""

     @property
@@ -33,19 +47,42 @@ def normalize_assessment_name(value: str) -> str:
     )


+def _roster_memberships(event, *, player_ids=None):
+    memberships = PlayerRosterMembership.objects.select_related(
+        "player", "season_team", "season_team__season"
+    ).filter(
+        season_team__season=event.season,
+        player__is_active=True,
+        is_active=True,
+    )
+    if event.division:
+        memberships = memberships.filter(
+            season_team__normalized_division=normalize_lookup_value(event.division)
+        )
+    if player_ids is not None:
+        memberships = memberships.filter(player_id__in=player_ids)
+    return memberships.order_by("-is_primary", "season_team__name", "id")
+
+
 def _primary_roster_membership(player: Player, event) -> PlayerRosterMembership | None:
-    return (
-        player.roster_memberships.select_related("season_team", "season_team__season")
-        .filter(season_team__season=event.season, is_active=True)
-        .order_by("-is_primary", "season_team__name", "id")
-        .first()
+    return _roster_memberships(event, player_ids=[player.pk]).first()
+
+
+def _candidate_context(player: Player, event) -> AssessmentMatchCandidate:
+    membership = _primary_roster_membership(player, event)
+    return AssessmentMatchCandidate(
+        player=player,
+        birth_year=player.birth_year,
+        team=membership.season_team.name if membership else player.team_name,
+        division=(membership.season_team.division if membership else player.division),
     )


 def _result_for_players(
-    players: list[Player], *, event, status: str, reason: str
+    players, *, event, status: str, reason: str
 ) -> AssessmentMatchResult:
     unique_players = list({player.pk: player for player in players}.values())
+    contexts = tuple(_candidate_context(player, event) for player in unique_players)
     if len(unique_players) == 1:
         player = unique_players[0]
         return AssessmentMatchResult(
@@ -53,69 +90,153 @@ def _result_for_players(
             player=player,
             roster_membership=_primary_roster_membership(player, event),
             candidates=(player,),
+            candidate_contexts=contexts,
             reason=reason,
         )
     if len(unique_players) > 1:
         return AssessmentMatchResult(
             status=MATCH_AMBIGUOUS,
             candidates=tuple(unique_players),
-            reason="Multiple players matched the workbook identity.",
+            candidate_contexts=contexts,
+            reason="Multiple exact player matches require staff selection.",
         )
     return AssessmentMatchResult(status=MATCH_UNMATCHED, reason=reason)


+def _players_with_exact_name(normalized_name: str, *, player_ids=None):
+    queryset = Player.objects.filter(is_active=True)
+    if player_ids is not None:
+        queryset = queryset.filter(pk__in=player_ids)
+    full_name = Lower(
+        Trim(
+            Concat(
+                F("first_name"),
+                Value(" "),
+                F("last_name"),
+                output_field=CharField(),
+            )
+        )
+    )
+    display_name = Lower(
+        Trim(
+            Concat(
+                Coalesce("preferred_name", "first_name"),
+                Value(" "),
+                F("last_name"),
+                output_field=CharField(),
+            )
+        )
+    )
+    return queryset.annotate(
+        assessment_full_name=full_name,
+        assessment_display_name=display_name,
+    ).filter(
+        Q(assessment_full_name=normalized_name)
+        | Q(assessment_display_name=normalized_name)
+    )
+
+
+def _roster_player_ids(event) -> list[int]:
+    return list(
+        _roster_memberships(event).values_list("player_id", flat=True).distinct()
+    )
+
+
+def _identifier_players(source_identifiers: list[dict]) -> list[Player]:
+    players = []
+    for source_identifier in source_identifiers:
+        source = normalize_player_lookup_value(source_identifier.get("source", ""))
+        identifier_type = normalize_player_lookup_value(
+            source_identifier.get("identifier_type", "")
+        )
+        identifier_value = normalize_player_lookup_value(
+            source_identifier.get("identifier_value", "")
+        )
+        if not source or not identifier_type or not identifier_value:
+            continue
+        identifiers = PlayerSourceIdentifier.objects.select_related("player").filter(
+            source=source,
+            identifier_type=identifier_type,
+            identifier_value=identifier_value,
+            player__is_active=True,
+        )
+        players.extend(identifier.player for identifier in identifiers)
+    return players
+
+
 def match_player_for_assessment(
     *,
     raw_name: str,
     event,
-    source_identifiers: dict[str, str] | None = None,
+    source_identifiers: list[dict] | None = None,
 ) -> AssessmentMatchResult:
-    """Match a workbook row to an existing canonical player without fuzzy commits."""
-    source_identifiers = source_identifiers or {}
-    identifier_players = []
-    for identifier_type, identifier_value in source_identifiers.items():
-        if not identifier_value:
-            continue
-        identifiers = PlayerSourceIdentifier.objects.select_related("player").filter(
-            identifier_type=normalize_player_lookup_value(identifier_type),
-            identifier_value=normalize_player_lookup_value(identifier_value),
-        )
-        identifier_players.extend(identifier.player for identifier in identifiers)
+    """Match a row conservatively without creating players or using fuzzy matches."""
+    identifier_players = _identifier_players(source_identifiers or [])
     if identifier_players:
         return _result_for_players(
             identifier_players,
             event=event,
             status=MATCH_EXACT_IDENTIFIER,
-            reason="Matched by source identifier.",
+            reason="Matched by exact namespaced source identifier.",
         )

     normalized_name = normalize_assessment_name(raw_name)
     if not normalized_name:
         return AssessmentMatchResult(
-            status=MATCH_UNMATCHED, reason="Missing player name."
+            status=MATCH_UNMATCHED, reason="Missing player identity."
+        )
+
+    roster_ids = _roster_player_ids(event)
+    roster_name_players = list(
+        _players_with_exact_name(normalized_name, player_ids=roster_ids)
+    )
+    if roster_name_players:
+        return _result_for_players(
+            roster_name_players,
+            event=event,
+            status=MATCH_EXACT_ROSTER_NAME,
+            reason="Matched by exact name in the event season and division roster.",
         )

-    name_players = [
-        player
-        for player in Player.objects.filter(is_active=True)
-        if normalize_assessment_name(player.display_name) == normalized_name
-        or normalize_assessment_name(player.full_name) == normalized_name
+    roster_alias_players = [
+        alias.player
+        for alias in PlayerAlias.objects.select_related("player").filter(
+            normalized_alias=normalized_name,
+            player_id__in=roster_ids,
+            player__is_active=True,
+        )
     ]
-    if name_players:
+    if roster_alias_players:
         return _result_for_players(
-            name_players,
+            roster_alias_players,
             event=event,
-            status=MATCH_EXACT_NAME,
-            reason="Matched by exact player name.",
+            status=MATCH_EXACT_ROSTER_ALIAS,
+            reason="Matched by exact alias in the event season and division roster.",
         )

-    aliases = PlayerAlias.objects.select_related("player").filter(
-        normalized_alias=normalized_name,
-        player__is_active=True,
-    )
+    global_name_players = list(_players_with_exact_name(normalized_name))
+    if global_name_players:
+        return _result_for_players(
+            global_name_players,
+            event=event,
+            status=MATCH_EXACT_GLOBAL_NAME,
+            reason="Matched by a unique exact canonical name outside the event roster.",
+        )
+
+    global_alias_players = [
+        alias.player
+        for alias in PlayerAlias.objects.select_related("player").filter(
+            normalized_alias=normalized_name,
+            player__is_active=True,
+        )
+    ]
     return _result_for_players(
-        [alias.player for alias in aliases],
+        global_alias_players,
         event=event,
-        status=MATCH_ALIAS,
-        reason="Matched by player alias." if aliases else "No exact player match.",
+        status=MATCH_EXACT_GLOBAL_ALIAS,
+        reason=(
+            "Matched by a unique exact alias outside the event roster."
+            if global_alias_players
+            else "No exact player match; manual resolution is required."
+        ),
     )
diff --git a/analytics/templates/analytics/assessment_import_detail.html b/analytics/templates/analytics/assessment_import_detail.html
index 3fccf5d..bf67b9a 100644
--- a/analytics/templates/analytics/assessment_import_detail.html
+++ b/analytics/templates/analytics/assessment_import_detail.html
@@ -14,7 +14,17 @@
         <dt>Uploaded</dt><dd>{{ import_batch.created_at }}</dd>
         <dt>Committed</dt><dd>{{ import_batch.committed_at|default:"-" }}</dd>
         <dt>Workbook checksum</dt><dd>{{ import_batch.workbook_sha256 }}</dd>
+        <dt>Import mapping</dt><dd>{{ import_batch.import_template }} · {{ import_batch.config_checksum }}</dd>
+        <dt>Preview version</dt><dd>{{ import_batch.preview_version }}</dd>
     </dl>
-    <p>{{ summary.rows }} rows · {{ summary.matched }} matched · {{ summary.unmatched }} unmatched · {{ summary.ambiguous }} ambiguous · {{ summary.invalid }} invalid · {{ summary.skipped }} skipped</p>
+    {% if import_batch.validation_errors %}
+        <h3>Workbook errors</h3>
+        <ul class="form-error">{% for issue in import_batch.validation_errors %}<li>{{ issue.message|default:issue }}</li>{% endfor %}</ul>
+    {% endif %}
+    {% if import_batch.validation_warnings %}
+        <h3>Workbook warnings</h3>
+        <ul>{% for issue in import_batch.validation_warnings %}<li>{{ issue.message|default:issue }}</li>{% endfor %}</ul>
+    {% endif %}
+    <p>{{ summary.rows }} rows · {{ summary.matched }} matched · {{ summary.unmatched }} unmatched · {{ summary.ambiguous }} ambiguous · {{ summary.invalid }} invalid · {{ summary.conflicts }} conflicts · {{ summary.skipped }} skipped</p>
 </article>
 {% endblock %}
diff --git a/analytics/templates/analytics/assessment_import_preview.html b/analytics/templates/analytics/assessment_import_preview.html
index f377ff4..22c5b90 100644
--- a/analytics/templates/analytics/assessment_import_preview.html
+++ b/analytics/templates/analytics/assessment_import_preview.html
@@ -5,17 +5,62 @@

 {% block analytics_content %}
 <article class="pdp-card">
-    <h2>Preview Summary</h2>
-    {% if summary.checksum_seen_before %}
-        <p class="form-error">This workbook checksum has already been committed for this event. Review carefully before continuing.</p>
+    <h2>Import Context</h2>
+    <dl class="pdp-detail-list">
+        <dt>Workbook</dt><dd>{{ import_batch.original_filename }}</dd>
+        <dt>Workbook checksum</dt><dd><code>{{ import_batch.workbook_sha256 }}</code></dd>
+        <dt>Event</dt><dd>{{ import_batch.event.name }}</dd>
+        <dt>Season / division</dt><dd>{{ import_batch.event.season }}{% if import_batch.event.division %} · {{ import_batch.event.division }}{% endif %}</dd>
+        <dt>Assessment template</dt><dd>{{ import_batch.event.template }}</dd>
+        <dt>Import mapping</dt><dd>{{ import_batch.import_template }} · <code>{{ import_batch.config_checksum }}</code></dd>
+    </dl>
+</article>
+
+<article class="pdp-card">
+    <h2>Validation</h2>
+    {% if import_batch.validation_errors %}
+        <h3>Workbook errors</h3>
+        <ul class="form-error">
+            {% for issue in import_batch.validation_errors %}<li>{{ issue.message|default:issue }}</li>{% endfor %}
+        </ul>
+    {% endif %}
+    {% if import_batch.validation_warnings %}
+        <h3>Workbook warnings</h3>
+        <ul>
+            {% for issue in import_batch.validation_warnings %}<li>{{ issue.message|default:issue }}</li>{% endfor %}
+        </ul>
+    {% endif %}
+    {% if not import_batch.validation_errors and not import_batch.validation_warnings %}
+        <p>No workbook-level validation issues.</p>
     {% endif %}
-    <p>{{ summary.rows }} rows · {{ summary.matched }} matched · {{ summary.unmatched }} unmatched · {{ summary.ambiguous }} ambiguous · {{ summary.invalid }} invalid · {{ summary.skipped }} skipped</p>
+</article>
+
+<article class="pdp-card">
+    <h2>Preview Summary</h2>
+    <dl class="pdp-detail-list">
+        <dt>Total source rows</dt><dd>{{ summary.rows }}</dd>
+        <dt>Valid player rows</dt><dd>{{ summary.valid_player_rows }}</dd>
+        <dt>Matched / unmatched / ambiguous</dt><dd>{{ summary.matched }} / {{ summary.unmatched }} / {{ summary.ambiguous }}</dd>
+        <dt>Invalid / skipped / conflicts</dt><dd>{{ summary.invalid }} / {{ summary.skipped }} / {{ summary.conflicts }}</dd>
+        <dt>Create / update / unchanged</dt><dd>{{ summary.creates }} / {{ summary.updates }} / {{ summary.unchanged }}</dd>
+        <dt>Clear / protected manual</dt><dd>{{ summary.clears }} / {{ summary.protected_manual }}</dd>
+    </dl>
     <p>
         <a class="button button--ghost" href="{% url 'analytics:assessment-import-list' %}">Back to Imports</a>
-        {% if not summary.can_commit %}
-            <a class="button button--primary" href="{% url 'analytics:assessment-import-resolve' pk=import_batch.pk %}">Resolve Rows</a>
+        {% if not summary.structurally_ready %}
+            <a class="button button--primary" href="{% url 'analytics:assessment-import-resolve' pk=import_batch.pk %}">Resolve Issues</a>
         {% endif %}
     </p>
+    {% if summary.structurally_ready and summary.acknowledgement_required and not summary.acknowledgement_complete %}
+        <form method="post">
+            {% csrf_token %}
+            <input type="hidden" name="acknowledgement_token" value="{{ import_batch.acknowledgement_token }}">
+            <p>Review the warnings above and in the metric details before continuing.</p>
+            <button class="button button--primary" type="submit">Acknowledge Current Warnings</button>
+        </form>
+    {% elif summary.acknowledgement_complete %}
+        <p>Warnings acknowledged by {{ import_batch.warnings_acknowledged_by }} at {{ import_batch.warnings_acknowledged_at }}.</p>
+    {% endif %}
     <form method="post" action="{% url 'analytics:assessment-import-confirm' pk=import_batch.pk %}">
         {% csrf_token %}
         <button class="button button--primary" type="submit" {% if not summary.can_commit %}disabled{% endif %}>Confirm Import</button>
@@ -23,20 +68,51 @@
 </article>

 <article class="pdp-card">
-    <h2>Rows</h2>
+    <h2>Player Rows</h2>
     {% if rows %}
         <div class="table-wrap table-wrap--cards">
             <table class="pdp-table" data-responsive="cards">
-                <thead><tr><th>Row</th><th>Workbook Name</th><th>Matched Player</th><th>Status</th><th>Values</th><th>Issues</th></tr></thead>
+                <thead><tr><th>Workbook Player</th><th>Matched Player</th><th>Context</th><th>Validation</th><th>Plan</th><th>Issues</th></tr></thead>
                 <tbody>
                     {% for row in rows %}
                         <tr>
-                            <td data-label="Row">{{ row.source_sheet }} {{ row.source_row }}</td>
-                            <td data-label="Workbook Name">{{ row.raw_identity }}</td>
-                            <td data-label="Matched Player">{% if row.player %}{{ row.player.display_name }}{% else %}-{% endif %}</td>
-                            <td data-label="Status">{{ row.get_status_display }}</td>
-                            <td data-label="Values">{{ row.values_snapshot|length }}</td>
-                            <td data-label="Issues">{% for error in row.errors %}{{ error }}{% if not forloop.last %}; {% endif %}{% empty %}-{% endfor %}</td>
+                            <td data-label="Workbook Player">
+                                <strong>{{ row.raw_identity|default:"Missing identity" }}</strong><br>
+                                {% for source in row.raw_row.source_rows %}{{ source.sheet }} row {{ source.row }}{% if not forloop.last %}<br>{% endif %}{% endfor %}
+                            </td>
+                            <td data-label="Matched Player">
+                                {% if row.player %}{{ row.player.display_name }}{% else %}-{% endif %}<br>
+                                <small>{{ row.metadata.match_reason }}</small>
+                            </td>
+                            <td data-label="Context">
+                                {% if row.roster_membership %}{{ row.roster_membership.season_team.division }} · {{ row.roster_membership.season_team.name }}{% else %}-{% endif %}
+                            </td>
+                            <td data-label="Validation">{{ row.get_validation_status_display }} · {{ row.get_match_status_display }} · {{ row.get_conflict_status_display }}</td>
+                            <td data-label="Plan">
+                                {{ row.action }} · {{ row.metric_changes|length }} metrics
+                                <details>
+                                    <summary>Metric changes</summary>
+                                    {% for change in row.metric_changes %}
+                                        <div class="pdp-list__item pdp-list__item--stack">
+                                            <strong>{{ change.header }}</strong>
+                                            <span>Action: {{ change.action }}</span>
+                                            <span>Old: {{ change.old_value.normalized_value|default:"-" }}</span>
+                                            <span>Incoming raw: {{ change.incoming_raw_value|default:"blank" }}</span>
+                                            <span>Normalized: {{ change.incoming_normalized_value|default:"blank" }}</span>
+                                            <span>{% if change.unit_status == "unverified" %}Unit not confirmed{% else %}Unit: {{ change.unit|default:"-" }}{% endif %}</span>
+                                            {% if change.rating_scale_max %}<span>Scale: {{ change.rating_scale_min }}–{{ change.rating_scale_max }}</span>{% endif %}
+                                            <span>Source: {{ change.source_sheet }} {{ change.source_column }}{{ change.source_row }} · {{ change.source_header }}</span>
+                                            {% for issue in change.errors %}<span class="form-error">{{ issue.message|default:issue }}</span>{% endfor %}
+                                            {% for issue in change.warnings %}<span>{{ issue.message|default:issue }}</span>{% endfor %}
+                                        </div>
+                                    {% endfor %}
+                                </details>
+                            </td>
+                            <td data-label="Issues">
+                                {% for issue in row.errors %}<span class="form-error">{{ issue.message|default:issue }}</span><br>{% endfor %}
+                                {% for issue in row.warnings %}<span>{{ issue.message|default:issue }}</span><br>{% endfor %}
+                                {% if not row.errors and not row.warnings %}-{% endif %}
+                            </td>
                         </tr>
                     {% endfor %}
                 </tbody>
diff --git a/analytics/templates/analytics/assessment_import_resolve.html b/analytics/templates/analytics/assessment_import_resolve.html
index 5774180..bc0e7dc 100644
--- a/analytics/templates/analytics/assessment_import_resolve.html
+++ b/analytics/templates/analytics/assessment_import_resolve.html
@@ -1,28 +1,31 @@
 {% extends "analytics/base.html" %}

-{% block analytics_title %}Resolve Assessment Import Rows{% endblock %}
+{% block analytics_title %}Resolve Assessment Import{% endblock %}
 {% block analytics_subtitle %}{{ import_batch.original_filename }}{% endblock %}

 {% block analytics_content %}
-<article class="pdp-card">
-    <h2>Rows Needing Review</h2>
-    {% if forms %}
-        <form method="post">
-            {% csrf_token %}
+<form method="post">
+    {% csrf_token %}
+
+    <article class="pdp-card">
+        <h2>Identity Resolution</h2>
+        <p>Choosing a player resolves identity only. It cannot clear workbook or numeric validation errors.</p>
+        {% if forms %}
             <div class="table-wrap table-wrap--cards">
                 <table class="pdp-table" data-responsive="cards">
-                    <thead><tr><th>Workbook Name</th><th>Status</th><th>Player</th><th>Skip</th></tr></thead>
+                    <thead><tr><th>Workbook Player</th><th>Match reason</th><th>Player</th><th>Skip</th></tr></thead>
                     <tbody>
                         {% for row, form in forms %}
                             <tr>
-                                <td data-label="Workbook Name">{{ row.raw_identity }}</td>
-                                <td data-label="Status">{{ row.get_status_display }}</td>
+                                <td data-label="Workbook Player">{{ row.raw_identity }}</td>
+                                <td data-label="Match reason">
+                                    {{ row.metadata.match_reason }}
+                                    {% for candidate in row.metadata.candidate_contexts %}<br><small>{{ candidate.birth_year|default:"Birth year unknown" }} · {{ candidate.division|default:"No division" }} · {{ candidate.team|default:"No team" }}</small>{% endfor %}
+                                </td>
                                 <td data-label="Player">
                                     <select name="row_{{ row.pk }}_player">
                                         <option value="">---------</option>
-                                        {% for player in form.fields.player.queryset %}
-                                            <option value="{{ player.pk }}">{{ player.display_name }}</option>
-                                        {% endfor %}
+                                        {% for player in form.fields.player.queryset %}<option value="{{ player.pk }}">{{ player.display_name }}</option>{% endfor %}
                                     </select>
                                 </td>
                                 <td data-label="Skip"><input type="checkbox" name="row_{{ row.pk }}_skip" value="1"></td>
@@ -31,11 +34,62 @@
                     </tbody>
                 </table>
             </div>
-            <button class="button button--primary" type="submit">Save Resolutions</button>
-        </form>
-    {% else %}
-        <p>No rows require review.</p>
-        <p><a class="button button--primary" href="{% url 'analytics:assessment-import-preview' pk=import_batch.pk %}">Back to Preview</a></p>
-    {% endif %}
-</article>
+        {% else %}
+            <p>No player identities require resolution.</p>
+        {% endif %}
+    </article>
+
+    <article class="pdp-card">
+        <h2>Invalid Data Rows</h2>
+        <p>Correct the workbook or mapping version, or explicitly skip the affected row.</p>
+        {% if invalid_rows %}
+            <div class="table-wrap table-wrap--cards">
+                <table class="pdp-table" data-responsive="cards">
+                    <thead><tr><th>Workbook Player</th><th>Errors</th><th>Skip</th></tr></thead>
+                    <tbody>
+                        {% for row in invalid_rows %}
+                            <tr>
+                                <td data-label="Workbook Player">{{ row.raw_identity|default:"Missing identity" }}</td>
+                                <td data-label="Errors">{% for issue in row.errors %}{{ issue.message|default:issue }}{% if not forloop.last %}<br>{% endif %}{% endfor %}</td>
+                                <td data-label="Skip"><input type="checkbox" name="row_{{ row.pk }}_skip" value="1"></td>
+                            </tr>
+                        {% endfor %}
+                    </tbody>
+                </table>
+            </div>
+        {% else %}
+            <p>No data-validation rows require action.</p>
+        {% endif %}
+    </article>
+
+    <article class="pdp-card">
+        <h2>Manual Correction Conflicts</h2>
+        <p>Workbook imports cannot replace manual corrections. Preserve the manual value to continue.</p>
+        {% if conflict_rows %}
+            <div class="table-wrap table-wrap--cards">
+                <table class="pdp-table" data-responsive="cards">
+                    <thead><tr><th>Workbook Player</th><th>Conflicting metrics</th><th>Resolution</th></tr></thead>
+                    <tbody>
+                        {% for row in conflict_rows %}
+                            <tr>
+                                <td data-label="Workbook Player">{{ row.raw_identity }}</td>
+                                <td data-label="Conflicting metrics">
+                                    {% for change in row.metric_changes %}{% if change.action == "conflict" %}{{ change.header }}{% if not forloop.last %}<br>{% endif %}{% endif %}{% endfor %}
+                                </td>
+                                <td data-label="Resolution"><label><input type="checkbox" name="row_{{ row.pk }}_preserve_manual" value="1"> Preserve manual values</label></td>
+                            </tr>
+                        {% endfor %}
+                    </tbody>
+                </table>
+            </div>
+        {% else %}
+            <p>No manual-correction conflicts require action.</p>
+        {% endif %}
+    </article>
+
+    <p>
+        <button class="button button--primary" type="submit">Save Resolutions</button>
+        <a class="button button--ghost" href="{% url 'analytics:assessment-import-preview' pk=import_batch.pk %}">Back to Preview</a>
+    </p>
+</form>
 {% endblock %}
diff --git a/analytics/templates/analytics/player_assessment_detail.html b/analytics/templates/analytics/player_assessment_detail.html
index 5ef2d8b..ff43ff8 100644
--- a/analytics/templates/analytics/player_assessment_detail.html
+++ b/analytics/templates/analytics/player_assessment_detail.html
@@ -19,8 +19,8 @@
                         <tr>
                             <td data-label="Metric">{{ value.template_metric.display_name }}</td>
                             <td data-label="Category">{{ value.template_metric.category|default:"-" }}</td>
-                            <td data-label="Value">{% if value.numeric_value != None %}{{ value.numeric_value }}{% elif value.rating_value != None %}{{ value.rating_value }}{% elif value.text_value %}{{ value.text_value }}{% else %}{{ value.raw_value|default:"-" }}{% endif %}</td>
-                            <td data-label="Unit">{{ value.unit|default:"-" }}</td>
+                            <td data-label="Value">{% if value.numeric_value != None %}{{ value.numeric_value }}{% elif value.rating_value != None %}{{ value.rating_value|floatformat:0 }} / {{ value.rating_scale_max|floatformat:0 }}{% elif value.text_value %}{{ value.text_value }}{% else %}{{ value.raw_value|default:"-" }}{% endif %}</td>
+                            <td data-label="Unit">{% if value.metadata.unit_status == "unverified" %}Unit not confirmed{% else %}{{ value.unit|default:"-" }}{% endif %}</td>
                             <td data-label="Source">{{ value.source_sheet }} row {{ value.source_row }}</td>
                         </tr>
                     {% endfor %}
diff --git a/analytics/tests/assessment_test_helpers.py b/analytics/tests/assessment_test_helpers.py
new file mode 100644
index 0000000..8e0310d
--- /dev/null
+++ b/analytics/tests/assessment_test_helpers.py
@@ -0,0 +1,279 @@
+from copy import deepcopy
+from io import BytesIO
+
+from django.core.files.uploadedfile import SimpleUploadedFile
+from openpyxl import Workbook
+
+from analytics.models import (
+    AssessmentEvent,
+    AssessmentImportTemplate,
+    AssessmentScoringProfile,
+    AssessmentTemplate,
+)
+from analytics.services.assessment_import_service import (
+    acknowledge_assessment_import_warnings,
+    default_2026_13u_config,
+    ensure_2026_13u_assessment_configuration,
+)
+from analytics.tests.helpers import Player, User, attach_player_to_season, create_season
+
+ASSESSMENT_HEADERS = [
+    "Name",
+    "Home to 1st",
+    "Broad Jump",
+    "Lateral Jump",
+    "Shotput",
+    "Bat Speed",
+    "Time 2 Contact",
+    "Exit Velocity Avg.",
+    "Exit Velocity Max",
+    "Athletic Stance",
+    "Balance Stride",
+    "Barrel Level",
+    "Launch Position",
+    "Follow Through",
+    "Readiness",
+    "Footwork",
+    "Glovework",
+    "Athleticism",
+    "Fundamental Throwing",
+]
+
+PITCHING_HEADERS = [
+    "Name",
+    "Velocity Avg.",
+    "Velocity Max",
+    "Pitch 1",
+    "Pitch 2",
+    "Pitch 3",
+    "Pitch 4",
+    "Athletic Movement",
+    "Body Control",
+    "Direction",
+    "Repeatability",
+    "Command2",
+]
+
+
+def assessment_row(name="Alex Example", **overrides):
+    values = {
+        "Home to 1st": 4.1,
+        "Broad Jump": 82,
+        "Lateral Jump": 60,
+        "Shotput": 200,
+        "Bat Speed": 55.2,
+        "Time 2 Contact": 0.18,
+        "Exit Velocity Avg.": 61.2,
+        "Exit Velocity Max": 67.5,
+        "Athletic Stance": 2,
+        "Balance Stride": 2,
+        "Barrel Level": 2,
+        "Launch Position": 2,
+        "Follow Through": 2,
+        "Readiness": 2,
+        "Footwork": 2,
+        "Glovework": 2,
+        "Athleticism": 2,
+        "Fundamental Throwing": 2,
+    }
+    values.update(overrides)
+    return [name, *[values[header] for header in ASSESSMENT_HEADERS[1:]]]
+
+
+def pitching_row(name="Alex Example", **overrides):
+    values = {
+        "Velocity Avg.": 50,
+        "Velocity Max": 53,
+        "Pitch 1": "Fastball",
+        "Pitch 2": "Changeup",
+        "Pitch 3": "",
+        "Pitch 4": "",
+        "Athletic Movement": 2,
+        "Body Control": 2,
+        "Direction": 2,
+        "Repeatability": 2,
+        "Command2": 2,
+    }
+    values.update(overrides)
+    return [name, *[values[header] for header in PITCHING_HEADERS[1:]]]
+
+
+def workbook_bytes(
+    *,
+    assessment_rows=None,
+    pitching_rows=None,
+    include_assessment=True,
+    include_pitching=True,
+    assessment_headers=None,
+    pitching_headers=None,
+    assessment_header_row=2,
+    pitching_header_row=2,
+    extra_assessment_headers=None,
+):
+    workbook = Workbook()
+    workbook.remove(workbook.active)
+    if include_assessment:
+        sheet = workbook.create_sheet("Assessment Data")
+        for _ in range(1, assessment_header_row):
+            sheet.append(["Athleticism Evaluation"])
+        headers = list(assessment_headers or ASSESSMENT_HEADERS)
+        headers.extend(extra_assessment_headers or [])
+        sheet.append(headers)
+        for row in assessment_rows or []:
+            sheet.append([*row, *(["extra"] * len(extra_assessment_headers or []))])
+    if include_pitching:
+        sheet = workbook.create_sheet("Pitching Data ")
+        for _ in range(1, pitching_header_row):
+            sheet.append([])
+        sheet.append(list(pitching_headers or PITCHING_HEADERS))
+        for row in pitching_rows or []:
+            sheet.append(row)
+    if not workbook.worksheets:
+        workbook.create_sheet("Empty")
+    output = BytesIO()
+    workbook.save(output)
+    return output.getvalue()
+
+
+def uploaded_workbook(content, name="assessment.xlsx"):
+    return SimpleUploadedFile(
+        name,
+        content,
+        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
+    )
+
+
+def minimal_config(
+    *,
+    value_type="number",
+    required_sheet=True,
+    required_header=True,
+    required_value=False,
+    zero_policy="allow",
+    blank_policy="preserve_existing",
+    min_value=None,
+    max_value=None,
+    header="Metric",
+    header_aliases=None,
+):
+    metric = {
+        "header": header,
+        "header_aliases": header_aliases or [],
+        "key": "metric",
+        "category": "Testing",
+        "value_type": value_type,
+        "required_header": required_header,
+        "required_value": required_value,
+        "zero_policy": zero_policy,
+        "blank_policy": blank_policy,
+        "unit": "",
+        "unit_status": "not_applicable",
+    }
+    if value_type == "rating":
+        metric.update(
+            {
+                "rating_scale_min": 1,
+                "rating_scale_max": 3,
+                "integer_only": True,
+                "allowed_choices": [1, 2, 3],
+            }
+        )
+    if min_value is not None:
+        metric["min_value"] = min_value
+    if max_value is not None:
+        metric["max_value"] = max_value
+    return {
+        "mapping_version": 1,
+        "sheets": [
+            {
+                "name": "Testing",
+                "required": required_sheet,
+                "header_row": 1,
+                "identity_column": "Name",
+                "max_rows": 20,
+                "max_columns": 10,
+                "metrics": [metric],
+            }
+        ],
+        "limits": {
+            "max_upload_bytes": 1024 * 1024,
+            "max_worksheets": 5,
+            "max_rows": 20,
+            "max_columns": 10,
+            "max_cell_text_length": 100,
+        },
+    }
+
+
+def minimal_workbook(rows, *, header="Metric", extra_headers=None):
+    workbook = Workbook()
+    sheet = workbook.active
+    sheet.title = "Testing"
+    sheet.append(["Name", header, *(extra_headers or [])])
+    for row in rows:
+        sheet.append(row)
+    output = BytesIO()
+    workbook.save(output)
+    return output.getvalue()
+
+
+class AssessmentTestMixin:
+    def setUp(self):
+        super().setUp()
+        self.staff = User.objects.create_user(
+            username="assessment.staff", password="test", is_staff=True
+        )
+        self.user = User.objects.create_user(
+            username="assessment.user", password="test"
+        )
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
+        self.membership = attach_player_to_season(
+            self.player,
+            self.season,
+            team_name="Yankees",
+            division="13U House",
+        )
+
+    def valid_upload(self, **assessment_overrides):
+        return uploaded_workbook(
+            workbook_bytes(
+                assessment_rows=[assessment_row(**assessment_overrides)],
+                pitching_rows=[pitching_row()],
+            )
+        )
+
+    def acknowledge(self, batch):
+        batch.refresh_from_db()
+        if batch.required_warning_codes:
+            acknowledge_assessment_import_warnings(
+                batch=batch,
+                actor=self.staff,
+                token=batch.acknowledgement_token,
+            )
+        batch.refresh_from_db()
+        return batch
+
+    def custom_import_template(self, config=None, version=99):
+        return AssessmentImportTemplate.objects.create(
+            key="synthetic-assessment-import",
+            name="Synthetic Assessment Import",
+            version=version,
+            assessment_template=self.template,
+            config=deepcopy(config or default_2026_13u_config()),
+        )
diff --git a/analytics/tests/test_assessment_configuration.py b/analytics/tests/test_assessment_configuration.py
new file mode 100644
index 0000000..2957f1d
--- /dev/null
+++ b/analytics/tests/test_assessment_configuration.py
@@ -0,0 +1,157 @@
+from django.core.exceptions import ValidationError
+from django.test import override_settings
+from django.urls import reverse
+
+from analytics.models import (
+    AssessmentEvent,
+    AssessmentImportTemplate,
+    AssessmentMetricDefinition,
+    AssessmentScoringProfile,
+    AssessmentTemplate,
+    AssessmentTemplateMetric,
+    PlayerAssessment,
+)
+from analytics.services.assessment_import_service import (
+    create_assessment_import_batch,
+    default_2026_13u_config,
+    ensure_2026_13u_assessment_configuration,
+)
+from analytics.tests.assessment_test_helpers import (
+    AssessmentTestMixin,
+)
+from analytics.tests.helpers import TestCase
+
+
+class AssessmentConfigurationTests(TestCase):
+    def test_dry_run_writes_nothing_and_reports_safety_configuration(self):
+        plan = ensure_2026_13u_assessment_configuration(dry_run=True)
+        self.assertEqual(AssessmentTemplate.objects.count(), 0)
+        self.assertEqual(AssessmentMetricDefinition.objects.count(), 0)
+        self.assertEqual(PlayerAssessment.objects.count(), 0)
+        self.assertEqual(plan["required_sheets"], ["Assessment Data"])
+        self.assertEqual(plan["optional_sheets"], ["Pitching Data"])
+        self.assertTrue(all("zero_policy" in metric for metric in plan["metrics"]))
+        self.assertEqual(plan["sheets"][0]["header_row"], 2)
+        self.assertIn("Athletic Stance", plan["sheets"][0]["required_headers"])
+
+    def test_first_run_creates_and_second_run_is_idempotent(self):
+        ensure_2026_13u_assessment_configuration()
+        counts = (
+            AssessmentTemplate.objects.count(),
+            AssessmentMetricDefinition.objects.count(),
+            AssessmentTemplateMetric.objects.count(),
+            AssessmentImportTemplate.objects.count(),
+            AssessmentScoringProfile.objects.count(),
+        )
+        ensure_2026_13u_assessment_configuration()
+        self.assertEqual(
+            counts,
+            (
+                AssessmentTemplate.objects.count(),
+                AssessmentMetricDefinition.objects.count(),
+                AssessmentTemplateMetric.objects.count(),
+                AssessmentImportTemplate.objects.count(),
+                AssessmentScoringProfile.objects.count(),
+            ),
+        )
+        self.assertEqual(PlayerAssessment.objects.count(), 0)
+
+    def test_conflicting_existing_rating_scale_is_detected(self):
+        ensure_2026_13u_assessment_configuration()
+        metric = AssessmentTemplateMetric.objects.get(
+            template__key="2026-13u-house-assessment",
+            metric__key="athletic_stance",
+        )
+        metric.rating_scale_max = 5
+        metric.save()
+        with self.assertRaises(ValidationError):
+            ensure_2026_13u_assessment_configuration()
+        metric.refresh_from_db()
+        self.assertEqual(metric.rating_scale_max, 5)
+
+        plan = ensure_2026_13u_assessment_configuration(dry_run=True)
+        state = next(
+            state
+            for state in plan["states"]
+            if state["object"] == "template_metric:athletic_stance"
+        )
+        self.assertEqual(state["state"], "conflict")
+        self.assertIn("rating_scale_max", state["conflicts"])
+
+    def test_locked_conflicting_configuration_is_never_rewritten(self):
+        ensure_2026_13u_assessment_configuration()
+        template = AssessmentTemplate.objects.get(key="2026-13u-house-assessment")
+        template.is_locked = True
+        template.save()
+        metric = template.template_metrics.get(metric__key="athletic_stance")
+        AssessmentTemplateMetric.objects.filter(pk=metric.pk).update(rating_scale_max=5)
+        with self.assertRaises(ValidationError):
+            ensure_2026_13u_assessment_configuration()
+        metric.refresh_from_db()
+        self.assertEqual(metric.rating_scale_max, 5)
+
+
+class AssessmentCompatibilityTests(AssessmentTestMixin, TestCase):
+    def test_wrong_import_template_is_rejected_by_form_and_service(self):
+        other_template = AssessmentTemplate.objects.create(
+            key="other-template", name="Other", version=1
+        )
+        wrong_import = AssessmentImportTemplate.objects.create(
+            key="wrong-import",
+            name="Wrong Import",
+            version=1,
+            assessment_template=other_template,
+            config=default_2026_13u_config(),
+        )
+        with self.assertRaises(ValidationError):
+            create_assessment_import_batch(
+                file_obj=self.valid_upload(),
+                event=self.event,
+                import_template=wrong_import,
+                uploaded_by=self.staff,
+            )
+
+        self.client.force_login(self.staff)
+        with override_settings(ANALYTICS_ASSESSMENTS_ENABLED=True):
+            response = self.client.post(
+                reverse("analytics:assessment-import-new"),
+                {
+                    "event": self.event.pk,
+                    "import_template": wrong_import.pk,
+                    "workbook": self.valid_upload(),
+                },
+            )
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Select a valid choice")
+
+    def test_scoring_profile_must_match_event_template(self):
+        other_template = AssessmentTemplate.objects.create(
+            key="other-template", name="Other", version=1
+        )
+        wrong_profile = AssessmentScoringProfile.objects.create(
+            key="other-profile",
+            name="Other Profile",
+            version=1,
+            assessment_template=other_template,
+        )
+        event = AssessmentEvent(
+            name="Invalid Event",
+            season=self.season,
+            template=self.template,
+            scoring_profile=wrong_profile,
+        )
+        with self.assertRaises(ValidationError):
+            event.save()
+
+    def test_batch_snapshot_is_authoritative_and_checksum_is_persisted(self):
+        batch = create_assessment_import_batch(
+            file_obj=self.valid_upload(),
+            event=self.event,
+            import_template=self.import_template,
+            uploaded_by=self.staff,
+        )
+        self.assertTrue(batch.config_checksum)
+        self.assertEqual(batch.config_snapshot, self.import_template.config)
+        self.assertEqual(
+            batch.preview_snapshot["config_checksum"], batch.config_checksum
+        )
diff --git a/analytics/tests/test_assessment_immutability.py b/analytics/tests/test_assessment_immutability.py
new file mode 100644
index 0000000..f5fd2c5
--- /dev/null
+++ b/analytics/tests/test_assessment_immutability.py
@@ -0,0 +1,167 @@
+from django.core.exceptions import ValidationError
+from django.db.models.deletion import ProtectedError
+
+from analytics.models import (
+    AssessmentImportBatch,
+    AssessmentMetricDefinition,
+    AssessmentTemplate,
+    AssessmentTemplateMetric,
+    AssessmentValue,
+    PlayerAssessment,
+)
+from analytics.services.assessment_import_service import (
+    commit_assessment_import_batch,
+    create_assessment_import_batch,
+)
+from analytics.tests.assessment_test_helpers import AssessmentTestMixin
+from analytics.tests.helpers import Player, TestCase, create_season
+
+
+class AssessmentImmutabilityTests(AssessmentTestMixin, TestCase):
+    def setUp(self):
+        super().setUp()
+        batch = create_assessment_import_batch(
+            file_obj=self.valid_upload(),
+            event=self.event,
+            import_template=self.import_template,
+            uploaded_by=self.staff,
+        )
+        self.batch = self.acknowledge(batch)
+        commit_assessment_import_batch(batch=self.batch, actor=self.staff)
+        self.assessment = PlayerAssessment.objects.get(
+            player=self.player, event=self.event
+        )
+        self.value = self.assessment.values.get(
+            template_metric__metric__key="home_to_1st"
+        )
+
+    def assert_validation_error(self, callback):
+        with self.assertRaises(ValidationError):
+            callback()
+
+    def test_used_template_cannot_change_or_receive_metric(self):
+        self.template.name = "Reinterpreted Template"
+        self.assert_validation_error(self.template.save)
+
+        metric = AssessmentMetricDefinition.objects.create(
+            key="new_metric", name="New Metric"
+        )
+        new_template_metric = AssessmentTemplateMetric(
+            template=self.template,
+            metric=metric,
+            display_name="New Metric",
+        )
+        self.assert_validation_error(new_template_metric.save)
+
+    def test_used_template_metric_cannot_change_or_delete(self):
+        template_metric = self.value.template_metric
+        template_metric.display_name = "Changed Meaning"
+        self.assert_validation_error(template_metric.save)
+        template_metric.refresh_from_db()
+        self.assert_validation_error(template_metric.delete)
+
+        unlocked_template = AssessmentTemplate.objects.create(
+            key="future-template",
+            name="Future Template",
+            version=1,
+        )
+        template_metric.template = unlocked_template
+        self.assert_validation_error(template_metric.save)
+
+    def test_used_import_template_and_scoring_profile_cannot_change_or_delete(self):
+        self.import_template.config = {"changed": True}
+        self.assert_validation_error(self.import_template.save)
+        self.import_template.refresh_from_db()
+        self.assert_validation_error(self.import_template.delete)
+
+        self.scoring_profile.config = {"changed": True}
+        self.assert_validation_error(self.scoring_profile.save)
+        self.scoring_profile.refresh_from_db()
+        self.assert_validation_error(self.scoring_profile.delete)
+
+    def test_used_event_cannot_change_template_season_or_dates(self):
+        other_season = create_season(name="Fall 2026", key="fall-2026")
+        self.event.season = other_season
+        self.assert_validation_error(self.event.save)
+        self.event.refresh_from_db()
+        self.event.starts_on = other_season.starts_on
+        self.event.name = "Changed Event Identity"
+        self.assert_validation_error(self.event.save)
+        self.event.refresh_from_db()
+        self.assert_validation_error(self.event.delete)
+
+    def test_committed_player_assessment_cannot_be_reassigned_or_deleted(self):
+        other = Player.objects.create(first_name="Other", last_name="Player")
+        self.assessment.player = other
+        self.assert_validation_error(self.assessment.save)
+        self.assessment.refresh_from_db()
+        self.assessment.status = "draft"
+        self.assert_validation_error(self.assessment.save)
+        self.assessment.refresh_from_db()
+        self.assert_validation_error(self.assessment.delete)
+        with self.assertRaises(ProtectedError):
+            self.player.delete()
+
+    def test_committed_value_cannot_be_edited_deleted_or_added_directly(self):
+        self.value.numeric_value = 9
+        self.assert_validation_error(self.value.save)
+        self.value.refresh_from_db()
+        self.assert_validation_error(self.value.delete)
+
+        draft_assessment = PlayerAssessment.objects.create(
+            player=Player.objects.create(first_name="Draft", last_name="Player"),
+            event=self.event,
+        )
+        self.value.player_assessment = draft_assessment
+        self.assert_validation_error(self.value.save)
+
+        other_metric = self.template.template_metrics.get(metric__key="pitch_3")
+        direct = AssessmentValue(
+            player_assessment=self.assessment,
+            template_metric=other_metric,
+            numeric_value=1,
+        )
+        self.assert_validation_error(direct.save)
+
+    def test_metric_definition_with_historical_use_is_locked(self):
+        metric = self.value.template_metric.metric
+        metric.default_value_type = "text"
+        self.assert_validation_error(metric.save)
+        metric.refresh_from_db()
+        self.assert_validation_error(metric.delete)
+
+    def test_committed_batch_and_rows_are_immutable(self):
+        self.batch.original_filename = "different.xlsx"
+        self.assert_validation_error(self.batch.save)
+        self.batch.refresh_from_db()
+        self.assert_validation_error(self.batch.delete)
+
+        row = self.batch.rows.first()
+        row.raw_identity = "Changed"
+        self.assert_validation_error(row.save)
+        row.refresh_from_db()
+        self.assert_validation_error(row.delete)
+
+        other_batch = AssessmentImportBatch.objects.create(
+            event=self.event,
+            import_template=self.import_template,
+            uploaded_by=self.staff,
+            original_filename="other.xlsx",
+            workbook_sha256="0" * 64,
+            config_snapshot=self.import_template.config,
+        )
+        row.batch = other_batch
+        self.assert_validation_error(row.save)
+
+        with self.assertRaises(ProtectedError):
+            self.batch.rows.all().delete()
+
+    def test_safe_lifecycle_deactivation_remains_available(self):
+        self.template.is_active = False
+        self.template.save()
+        self.event.is_active = False
+        self.event.save()
+        self.template.refresh_from_db()
+        self.event.refresh_from_db()
+        self.assertFalse(self.template.is_active)
+        self.assertFalse(self.event.is_active)
diff --git a/analytics/tests/test_assessment_imports.py b/analytics/tests/test_assessment_imports.py
index 4331da0..a5b2790 100644
--- a/analytics/tests/test_assessment_imports.py
+++ b/analytics/tests/test_assessment_imports.py
@@ -1,127 +1,52 @@
 from decimal import Decimal
-from io import BytesIO
+from unittest.mock import patch

+from django.contrib.auth import get_user_model
 from django.core.exceptions import PermissionDenied, ValidationError
-from django.core.files.uploadedfile import SimpleUploadedFile
 from django.test import override_settings
 from django.urls import reverse
-from openpyxl import Workbook

 from analytics.models import (
     ASSESSMENT_IMPORT_ROW_MATCHED,
-    ASSESSMENT_IMPORT_ROW_SKIPPED,
-    ASSESSMENT_IMPORT_ROW_UNMATCHED,
     ASSESSMENT_IMPORT_STATUS_COMMITTED,
     ASSESSMENT_STATUS_COMMITTED,
-    AssessmentEvent,
     AssessmentImportBatch,
-    AssessmentImportTemplate,
     AssessmentMetricDefinition,
-    AssessmentScoringProfile,
-    AssessmentTemplate,
     AssessmentTemplateMetric,
     AssessmentValue,
     PlayerAssessment,
 )
 from analytics.services.assessment_import_service import (
+    acknowledge_assessment_import_warnings,
     commit_assessment_import_batch,
+    correct_assessment_value,
     create_assessment_import_batch,
     ensure_2026_13u_assessment_configuration,
-    resolve_assessment_import_row,
 )
-from analytics.tests.helpers import (
-    Player,
-    TestCase,
-    User,
-    attach_player_to_season,
-    create_season,
-)
-
-
-def assessment_workbook(rows):
-    workbook = Workbook()
-    worksheet = workbook.active
-    worksheet.title = "Assessment Data"
-    worksheet.append(["", "Athleticism Evaluation", ""])
-    worksheet.append(["Name", "Home to 1st", "Broad Jump"])
-    for row in rows:
-        worksheet.append(row)
-    pitching = workbook.create_sheet("Pitching Data ")
-    pitching.append([])
-    pitching.append(["Name", "Velocity Avg.", "Velocity Max"])
-    for row in rows:
-        pitching.append([row[0], 50, 52])
-    buffer = BytesIO()
-    workbook.save(buffer)
-    return buffer.getvalue()
-
-
-class AssessmentImportTests(TestCase):
-    def setUp(self):
-        self.staff = User.objects.create_user(
-            username="staff", password="test", is_staff=True
-        )
-        self.user = User.objects.create_user(username="regular", password="test")
-        self.season = create_season(name="Spring 2026", key="spring-2026")
-        ensure_2026_13u_assessment_configuration()
-        self.template = AssessmentTemplate.objects.get(key="2026-13u-house-assessment")
-        self.import_template = AssessmentImportTemplate.objects.get(
-            key="2026-13u-house-assessment-xlsx"
-        )
-        self.scoring_profile = AssessmentScoringProfile.objects.get(
-            key="2026-13u-house-assessment"
-        )
-        self.event = AssessmentEvent.objects.create(
-            name="Spring 2026 13U Assessment",
-            season=self.season,
-            division="13U House",
-            template=self.template,
-            scoring_profile=self.scoring_profile,
-        )
-        self.player = Player.objects.create(first_name="Alex", last_name="Example")
-        attach_player_to_season(
-            self.player, self.season, team_name="Yankees", division="13U House"
-        )
-
-    def upload(self, rows):
-        return SimpleUploadedFile(
-            "assessment.xlsx",
-            assessment_workbook(rows),
-            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
-        )
-
-    def test_feature_flag_blocks_assessment_routes_when_disabled(self):
-        self.client.force_login(self.staff)
-        with override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False):
-            response = self.client.get(reverse("analytics:assessment-event-list"))
-        self.assertEqual(response.status_code, 404)
+from analytics.tests.assessment_test_helpers import AssessmentTestMixin
+from analytics.tests.helpers import TestCase

-    def test_staff_required_for_assessment_routes(self):
-        self.client.force_login(self.user)
-        with override_settings(ANALYTICS_ASSESSMENTS_ENABLED=True):
-            response = self.client.get(reverse("analytics:assessment-event-list"))
-        self.assertEqual(response.status_code, 403)

-    def test_valid_workbook_preview_matches_existing_player(self):
-        batch = create_assessment_import_batch(
-            file_obj=self.upload([["Alex Example", 4.1, 82]]),
+class AssessmentImportIntegrationTests(AssessmentTestMixin, TestCase):
+    def create_batch(self, upload=None):
+        return create_assessment_import_batch(
+            file_obj=upload or self.valid_upload(),
             event=self.event,
             import_template=self.import_template,
             uploaded_by=self.staff,
         )

+    def test_valid_preview_matches_without_writing_assessments(self):
+        batch = self.create_batch()
+
         row = batch.rows.get()
         self.assertEqual(row.status, ASSESSMENT_IMPORT_ROW_MATCHED)
         self.assertEqual(row.player, self.player)
-        self.assertEqual(len(row.values_snapshot), 4)
+        self.assertEqual(PlayerAssessment.objects.count(), 0)
+        self.assertEqual(AssessmentValue.objects.count(), 0)

-    def test_commit_creates_player_assessment_values(self):
-        batch = create_assessment_import_batch(
-            file_obj=self.upload([["Alex Example", 4.1, 82]]),
-            event=self.event,
-            import_template=self.import_template,
-            uploaded_by=self.staff,
-        )
+    def test_commit_creates_values_and_preserves_rating_scale(self):
+        batch = self.acknowledge(self.create_batch())

         result = commit_assessment_import_batch(batch=batch, actor=self.staff)

@@ -130,69 +55,162 @@ class AssessmentImportTests(TestCase):
         self.assertEqual(batch.status, ASSESSMENT_IMPORT_STATUS_COMMITTED)
         assessment = PlayerAssessment.objects.get(player=self.player, event=self.event)
         self.assertEqual(assessment.status, ASSESSMENT_STATUS_COMMITTED)
-        self.assertEqual(
-            AssessmentValue.objects.filter(player_assessment=assessment).count(), 4
-        )
+        rating = assessment.values.get(template_metric__metric__key="athletic_stance")
+        self.assertEqual(rating.rating_value, Decimal("2"))
+        self.assertEqual(rating.rating_scale_min, Decimal("1"))
+        self.assertEqual(rating.rating_scale_max, Decimal("3"))

-    def test_commit_blocks_unmatched_rows_until_resolved_or_skipped(self):
-        batch = create_assessment_import_batch(
-            file_obj=self.upload([["Unknown Player", 4.1, 82]]),
-            event=self.event,
-            import_template=self.import_template,
-            uploaded_by=self.staff,
-        )
-        row = batch.rows.get()
-        self.assertEqual(row.status, ASSESSMENT_IMPORT_ROW_UNMATCHED)
+    def test_warning_acknowledgement_is_required_and_stale_token_is_rejected(self):
+        batch = self.create_batch()
+        self.assertTrue(batch.required_warning_codes)

         with self.assertRaises(ValidationError):
             commit_assessment_import_batch(batch=batch, actor=self.staff)
+        with self.assertRaises(ValidationError):
+            acknowledge_assessment_import_warnings(
+                batch=batch, actor=self.staff, token="stale"
+            )

-        resolve_assessment_import_row(row=row, player=None, skip=True)
-        row.refresh_from_db()
-        self.assertEqual(row.status, ASSESSMENT_IMPORT_ROW_SKIPPED)
-        result = commit_assessment_import_batch(batch=batch, actor=self.staff)
-        self.assertEqual(result.skipped, 1)
-
-    def test_commit_blocks_manual_override_overwrite(self):
-        batch = create_assessment_import_batch(
-            file_obj=self.upload([["Alex Example", 4.1, 82]]),
-            event=self.event,
-            import_template=self.import_template,
-            uploaded_by=self.staff,
+        batch.refresh_from_db()
+        acknowledge_assessment_import_warnings(
+            batch=batch,
+            actor=self.staff,
+            token=batch.acknowledgement_token,
         )
-        metric = AssessmentMetricDefinition.objects.get(key="home_to_1st")
-        template_metric = AssessmentTemplateMetric.objects.get(
-            template=self.template, metric=metric
+        commit_assessment_import_batch(batch=batch, actor=self.staff)
+
+    def test_non_staff_cannot_commit_or_acknowledge(self):
+        batch = self.create_batch()
+        with self.assertRaises(PermissionDenied):
+            acknowledge_assessment_import_warnings(
+                batch=batch,
+                actor=self.user,
+                token=batch.acknowledgement_token,
+            )
+        with self.assertRaises(PermissionDenied):
+            commit_assessment_import_batch(batch=batch, actor=self.user)
+
+    def test_commit_is_atomic_when_metric_write_fails(self):
+        batch = self.acknowledge(self.create_batch())
+        with patch(
+            "analytics.services.assessment_import_service._apply_metric_change",
+            side_effect=ValidationError("synthetic failure"),
+        ):
+            with self.assertRaises(ValidationError):
+                commit_assessment_import_batch(batch=batch, actor=self.staff)
+
+        self.assertEqual(PlayerAssessment.objects.count(), 0)
+        self.assertEqual(AssessmentValue.objects.count(), 0)
+        batch.refresh_from_db()
+        self.assertNotEqual(batch.status, ASSESSMENT_IMPORT_STATUS_COMMITTED)
+
+    def test_approved_manual_correction_records_audit_history(self):
+        batch = self.acknowledge(self.create_batch())
+        commit_assessment_import_batch(batch=batch, actor=self.staff)
+        value = AssessmentValue.objects.get(
+            player_assessment__player=self.player,
+            template_metric__metric__key="home_to_1st",
         )
-        assessment = PlayerAssessment.objects.create(
-            player=self.player,
-            event=self.event,
-            status=ASSESSMENT_STATUS_COMMITTED,
+
+        corrected = correct_assessment_value(
+            assessment_value=value,
+            actor=self.staff,
+            reason="Verified timing correction",
+            new_value="4.2",
         )
-        AssessmentValue.objects.create(
-            player_assessment=assessment,
-            template_metric=template_metric,
-            numeric_value=Decimal("9.999"),
-            is_manual_override=True,
+
+        self.assertEqual(corrected.numeric_value, Decimal("4.2"))
+        self.assertTrue(corrected.is_manual_override)
+        self.assertEqual(corrected.corrections.count(), 1)
+
+    def test_bootstrap_is_idempotent_and_ratings_are_one_to_three(self):
+        first_count = AssessmentMetricDefinition.objects.count()
+        ensure_2026_13u_assessment_configuration()
+        self.assertEqual(AssessmentMetricDefinition.objects.count(), first_count)
+        rating_metrics = AssessmentTemplateMetric.objects.filter(
+            template=self.template,
+            value_type="rating",
         )
+        self.assertTrue(rating_metrics.exists())
+        self.assertFalse(rating_metrics.exclude(rating_scale_min=1).exists())
+        self.assertFalse(rating_metrics.exclude(rating_scale_max=3).exists())

-        with self.assertRaises(ValidationError):
-            commit_assessment_import_batch(batch=batch, actor=self.staff)

-    def test_non_staff_cannot_commit_batch(self):
-        batch = create_assessment_import_batch(
-            file_obj=self.upload([["Alex Example", 4.1, 82]]),
+class AssessmentRouteTests(AssessmentTestMixin, TestCase):
+    def setUp(self):
+        super().setUp()
+        self.batch = create_assessment_import_batch(
+            file_obj=self.valid_upload(),
             event=self.event,
             import_template=self.import_template,
             uploaded_by=self.staff,
         )
-        with self.assertRaises(PermissionDenied):
-            commit_assessment_import_batch(batch=batch, actor=self.user)

-    def test_bootstrap_command_is_idempotent(self):
-        first_count = AssessmentMetricDefinition.objects.count()
-        ensure_2026_13u_assessment_configuration()
-        self.assertEqual(AssessmentMetricDefinition.objects.count(), first_count)
+    def assessment_urls(self):
+        return [
+            reverse("analytics:assessment-event-list"),
+            reverse("analytics:assessment-event-detail", args=[self.event.pk]),
+            reverse("analytics:assessment-import-list"),
+            reverse("analytics:assessment-import-new"),
+            reverse("analytics:assessment-import-preview", args=[self.batch.pk]),
+            reverse("analytics:assessment-import-resolve", args=[self.batch.pk]),
+            reverse("analytics:assessment-import-confirm", args=[self.batch.pk]),
+            reverse("analytics:assessment-import-detail", args=[self.batch.pk]),
+        ]
+
+    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False)
+    def test_all_assessment_routes_are_hidden_when_disabled(self):
+        self.client.force_login(self.staff)
+        for url in self.assessment_urls():
+            self.assertEqual(self.client.get(url).status_code, 404, url)
+
+    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=True)
+    def test_non_staff_is_denied_and_staff_can_access(self):
+        self.client.force_login(self.user)
+        self.assertEqual(
+            self.client.get(reverse("analytics:assessment-event-list")).status_code,
+            403,
+        )
+        self.client.force_login(self.staff)
+        self.assertEqual(
+            self.client.get(reverse("analytics:assessment-event-list")).status_code,
+            200,
+        )
+
+    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False)
+    def test_command_center_navigation_is_hidden_when_disabled(self):
+        self.client.force_login(self.staff)
+        response = self.client.get(reverse("analytics:command-center"))
+        self.assertNotContains(response, "Assessment Events")
+
+    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False)
+    def test_player_profile_does_not_query_or_show_assessments_when_disabled(self):
+        self.client.force_login(self.staff)
+        with patch(
+            "analytics.views.assessment_records_for_player"
+        ) as assessment_records:
+            response = self.client.get(
+                reverse(
+                    "analytics:player-profile",
+                    kwargs={"player_id": self.player.pk},
+                )
+            )
+        self.assertEqual(response.status_code, 200)
+        assessment_records.assert_not_called()
+        self.assertNotContains(response, "Assessment Events")
+
+    def test_existing_evaluation_pages_work_with_assessment_flag_off_and_on(self):
+        self.client.force_login(self.staff)
+        for enabled in (False, True):
+            with override_settings(ANALYTICS_ASSESSMENTS_ENABLED=enabled):
+                self.assertEqual(
+                    self.client.get(reverse("analytics:evaluation-list")).status_code,
+                    200,
+                )
+                self.assertEqual(
+                    self.client.get(reverse("analytics:assessment-list")).status_code,
+                    200,
+                )

     @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=True)
     def test_upload_view_creates_preview_batch(self):
@@ -202,9 +220,35 @@ class AssessmentImportTests(TestCase):
             {
                 "event": self.event.pk,
                 "import_template": self.import_template.pk,
-                "workbook": self.upload([["Alex Example", 4.1, 82]]),
+                "workbook": self.valid_upload(),
             },
         )
-
         self.assertEqual(response.status_code, 302)
-        self.assertEqual(AssessmentImportBatch.objects.count(), 1)
+        self.assertEqual(AssessmentImportBatch.objects.count(), 2)
+
+
+class AssessmentAdminSafetyTests(AssessmentTestMixin, TestCase):
+    def setUp(self):
+        super().setUp()
+        self.superuser = get_user_model().objects.create_superuser(
+            username="assessment.admin",
+            password="test",
+            email="admin@example.invalid",
+        )
+        self.client.force_login(self.superuser)
+
+    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False)
+    def test_assessment_models_are_hidden_from_admin_navigation_when_disabled(self):
+        response = self.client.get(reverse("admin:index"))
+        self.assertEqual(response.status_code, 200)
+        self.assertNotContains(response, "Assessment templates")
+
+    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False)
+    def test_direct_admin_url_remains_superuser_protected_when_disabled(self):
+        response = self.client.get(
+            reverse(
+                "admin:analytics_assessmenttemplate_change",
+                args=[self.template.pk],
+            )
+        )
+        self.assertEqual(response.status_code, 200)
diff --git a/analytics/tests/test_assessment_matching_and_duplicates.py b/analytics/tests/test_assessment_matching_and_duplicates.py
new file mode 100644
index 0000000..f5a28e5
--- /dev/null
+++ b/analytics/tests/test_assessment_matching_and_duplicates.py
@@ -0,0 +1,224 @@
+from analytics.services.assessment_import_service import (
+    create_assessment_import_batch,
+    parse_assessment_workbook,
+)
+from analytics.services.assessment_matching_service import (
+    MATCH_AMBIGUOUS,
+    MATCH_EXACT_GLOBAL_ALIAS,
+    MATCH_EXACT_GLOBAL_NAME,
+    MATCH_EXACT_IDENTIFIER,
+    MATCH_EXACT_ROSTER_ALIAS,
+    MATCH_EXACT_ROSTER_NAME,
+    MATCH_UNMATCHED,
+    match_player_for_assessment,
+)
+from analytics.tests.assessment_test_helpers import (
+    AssessmentTestMixin,
+    assessment_row,
+    minimal_config,
+    minimal_workbook,
+    pitching_row,
+    uploaded_workbook,
+    workbook_bytes,
+)
+from analytics.tests.helpers import (
+    Player,
+    TestCase,
+    attach_player_to_season,
+    create_season,
+)
+from players.models import PlayerAlias, PlayerSourceIdentifier
+
+
+def row_issue_codes(parsed):
+    return {issue["code"] for row in parsed["rows"] for issue in row.get("errors", [])}
+
+
+class AssessmentMatchingTests(AssessmentTestMixin, TestCase):
+    def test_matching_order_prefers_namespaced_identifier(self):
+        PlayerSourceIdentifier.objects.create(
+            player=self.player,
+            source="registration",
+            identifier_type="player_id",
+            identifier_value="ABC-123",
+        )
+        result = match_player_for_assessment(
+            raw_name="Different Name",
+            event=self.event,
+            source_identifiers=[
+                {
+                    "source": "registration",
+                    "identifier_type": "player_id",
+                    "identifier_value": "ABC-123",
+                }
+            ],
+        )
+        self.assertEqual(result.status, MATCH_EXACT_IDENTIFIER)
+        self.assertEqual(result.player, self.player)
+
+    def test_roster_name_and_alias_precede_global_matches(self):
+        global_player = Player.objects.create(first_name="Alex", last_name="Example")
+        roster_result = match_player_for_assessment(
+            raw_name="Alex Example", event=self.event
+        )
+        self.assertEqual(roster_result.status, MATCH_EXACT_ROSTER_NAME)
+        self.assertEqual(roster_result.player, self.player)
+
+        PlayerAlias.objects.create(player=self.player, alias="A Example")
+        PlayerAlias.objects.create(player=global_player, alias="A Example")
+        alias_result = match_player_for_assessment(
+            raw_name="A Example", event=self.event
+        )
+        self.assertEqual(alias_result.status, MATCH_EXACT_ROSTER_ALIAS)
+        self.assertEqual(alias_result.player, self.player)
+
+    def test_unique_global_name_and_alias_are_supported(self):
+        outside = Player.objects.create(first_name="Outside", last_name="Player")
+        result = match_player_for_assessment(
+            raw_name="Outside Player", event=self.event
+        )
+        self.assertEqual(result.status, MATCH_EXACT_GLOBAL_NAME)
+        self.assertEqual(result.player, outside)
+
+        alias_player = Player.objects.create(first_name="Alias", last_name="Owner")
+        PlayerAlias.objects.create(player=alias_player, alias="Unique Alias")
+        result = match_player_for_assessment(raw_name="Unique Alias", event=self.event)
+        self.assertEqual(result.status, MATCH_EXACT_GLOBAL_ALIAS)
+
+    def test_duplicate_global_names_are_ambiguous_with_candidate_context(self):
+        other_season = create_season(name="Fall 2025", key="fall-2025")
+        first = Player.objects.create(
+            first_name="Duplicate", last_name="Name", birth_year=2012
+        )
+        second = Player.objects.create(
+            first_name="Duplicate", last_name="Name", birth_year=2013
+        )
+        attach_player_to_season(first, other_season, team_name="One", division="13U")
+        attach_player_to_season(second, other_season, team_name="Two", division="13U")
+
+        result = match_player_for_assessment(
+            raw_name="Duplicate Name", event=self.event
+        )
+
+        self.assertEqual(result.status, MATCH_AMBIGUOUS)
+        self.assertEqual(len(result.candidates), 2)
+        self.assertEqual(
+            {item.birth_year for item in result.candidate_contexts}, {2012, 2013}
+        )
+
+    def test_unmatched_never_creates_or_fuzzy_matches(self):
+        player_count = Player.objects.count()
+        result = match_player_for_assessment(raw_name="Alek Exampel", event=self.event)
+        self.assertEqual(result.status, MATCH_UNMATCHED)
+        self.assertEqual(Player.objects.count(), player_count)
+
+
+class DuplicateWorkbookRowTests(AssessmentTestMixin, TestCase):
+    def test_one_player_across_component_sheets_is_one_combined_row(self):
+        parsed = parse_assessment_workbook(
+            workbook_bytes(
+                assessment_rows=[assessment_row()],
+                pitching_rows=[pitching_row()],
+            ),
+            self.import_template.config,
+        )
+        self.assertEqual(len(parsed["rows"]), 1)
+        self.assertEqual(len(parsed["rows"][0]["source_rows"]), 2)
+
+    def test_duplicate_rows_within_each_sheet_are_blocking(self):
+        assessment_duplicate = parse_assessment_workbook(
+            workbook_bytes(
+                assessment_rows=[assessment_row(), assessment_row()],
+                pitching_rows=[],
+            ),
+            self.import_template.config,
+        )
+        self.assertIn(
+            "duplicate_identity_in_sheet", row_issue_codes(assessment_duplicate)
+        )
+
+        pitching_duplicate = parse_assessment_workbook(
+            workbook_bytes(
+                assessment_rows=[assessment_row()],
+                pitching_rows=[pitching_row(), pitching_row()],
+            ),
+            self.import_template.config,
+        )
+        self.assertIn(
+            "duplicate_identity_in_sheet", row_issue_codes(pitching_duplicate)
+        )
+
+    def test_conflicting_duplicate_metric_values_are_reported(self):
+        config = minimal_config()
+        config["sheets"].append(
+            {
+                **config["sheets"][0],
+                "name": "Testing Two",
+            }
+        )
+        from io import BytesIO
+
+        from openpyxl import Workbook
+
+        workbook = Workbook()
+        first = workbook.active
+        first.title = "Testing"
+        first.append(["Name", "Metric"])
+        first.append(["Synthetic Player", 1])
+        second = workbook.create_sheet("Testing Two")
+        second.append(["Name", "Metric"])
+        second.append(["Synthetic Player", 2])
+        output = BytesIO()
+        workbook.save(output)
+
+        parsed = parse_assessment_workbook(output.getvalue(), config)
+        self.assertIn("conflicting_duplicate_metric", row_issue_codes(parsed))
+
+    def test_distinct_names_that_share_a_slug_are_not_silently_merged(self):
+        parsed = parse_assessment_workbook(
+            minimal_workbook([["Anne-Marie Test", 1], ["Anne Marie Test", 1]]),
+            minimal_config(),
+        )
+        self.assertEqual(len(parsed["rows"]), 2)
+        self.assertIn("identity_slug_collision", row_issue_codes(parsed))
+
+    def test_duplicate_source_identifiers_are_blocked(self):
+        config = minimal_config()
+        config["sheets"][0]["source_identifiers"] = [
+            {
+                "header": "Registration ID",
+                "source": "registration",
+                "identifier_type": "player_id",
+            }
+        ]
+        from io import BytesIO
+
+        from openpyxl import Workbook
+
+        workbook = Workbook()
+        sheet = workbook.active
+        sheet.title = "Testing"
+        sheet.append(["Name", "Metric", "Registration ID"])
+        sheet.append(["One Player", 1, "same-id"])
+        sheet.append(["Two Player", 2, "same-id"])
+        output = BytesIO()
+        workbook.save(output)
+
+        parsed = parse_assessment_workbook(output.getvalue(), config)
+        self.assertIn("duplicate_source_identifier", row_issue_codes(parsed))
+
+    def test_preview_does_not_create_players_for_unmatched_rows(self):
+        initial_count = Player.objects.count()
+        batch = create_assessment_import_batch(
+            file_obj=uploaded_workbook(
+                workbook_bytes(
+                    assessment_rows=[assessment_row(name="Unknown Person")],
+                    pitching_rows=[],
+                )
+            ),
+            event=self.event,
+            import_template=self.import_template,
+            uploaded_by=self.staff,
+        )
+        self.assertEqual(Player.objects.count(), initial_count)
+        self.assertEqual(batch.rows.get().match_status, "unmatched")
diff --git a/analytics/tests/test_assessment_reimport.py b/analytics/tests/test_assessment_reimport.py
new file mode 100644
index 0000000..e303252
--- /dev/null
+++ b/analytics/tests/test_assessment_reimport.py
@@ -0,0 +1,211 @@
+from copy import deepcopy
+from decimal import Decimal
+
+from django.core.exceptions import ValidationError
+
+from analytics.models import AssessmentValue, PlayerAssessment
+from analytics.services.assessment_import_service import (
+    acknowledge_assessment_import_warnings,
+    commit_assessment_import_batch,
+    correct_assessment_value,
+    create_assessment_import_batch,
+    preserve_manual_override_conflicts,
+)
+from analytics.tests.assessment_test_helpers import (
+    AssessmentTestMixin,
+    assessment_row,
+    pitching_row,
+    uploaded_workbook,
+    workbook_bytes,
+)
+from analytics.tests.helpers import TestCase
+
+
+class AssessmentReimportTests(AssessmentTestMixin, TestCase):
+    def import_rows(self, *, assessment_overrides=None, pitching_overrides=None):
+        batch = create_assessment_import_batch(
+            file_obj=uploaded_workbook(
+                workbook_bytes(
+                    assessment_rows=[assessment_row(**(assessment_overrides or {}))],
+                    pitching_rows=[pitching_row(**(pitching_overrides or {}))],
+                )
+            ),
+            event=self.event,
+            import_template=self.import_template,
+            uploaded_by=self.staff,
+        )
+        batch.refresh_from_db()
+        if batch.required_warning_codes:
+            acknowledge_assessment_import_warnings(
+                batch=batch,
+                actor=self.staff,
+                token=batch.acknowledgement_token,
+            )
+        return batch, commit_assessment_import_batch(batch=batch, actor=self.staff)
+
+    def preview_rows(self, *, assessment_overrides=None, pitching_overrides=None):
+        batch = create_assessment_import_batch(
+            file_obj=uploaded_workbook(
+                workbook_bytes(
+                    assessment_rows=[assessment_row(**(assessment_overrides or {}))],
+                    pitching_rows=[pitching_row(**(pitching_overrides or {}))],
+                )
+            ),
+            event=self.event,
+            import_template=self.import_template,
+            uploaded_by=self.staff,
+        )
+        return batch
+
+    def metric_change(self, batch, metric_key):
+        return next(
+            change
+            for change in batch.rows.get().metric_changes
+            if change["metric_key"] == metric_key
+        )
+
+    def test_identical_reimport_is_unchanged_without_value_timestamp_churn(self):
+        _, first = self.import_rows()
+        self.assertEqual(first.created, 1)
+        value = AssessmentValue.objects.get(
+            player_assessment__player=self.player,
+            template_metric__metric__key="home_to_1st",
+        )
+        original_updated_at = value.updated_at
+
+        batch = self.preview_rows()
+        self.assertEqual(
+            self.metric_change(batch, "home_to_1st")["action"], "unchanged"
+        )
+        batch = self.acknowledge(batch)
+        result = commit_assessment_import_batch(batch=batch, actor=self.staff)
+
+        value.refresh_from_db()
+        self.assertEqual(result.unchanged, 1)
+        self.assertEqual(value.updated_at, original_updated_at)
+        self.assertEqual(PlayerAssessment.objects.count(), 1)
+
+    def test_duplicate_workbook_checksum_requires_acknowledgement(self):
+        self.import_rows()
+        batch = self.preview_rows()
+        batch.refresh_from_db()
+
+        self.assertTrue(batch.preview_snapshot["checksum_seen_before"])
+        self.assertIn("duplicate_workbook_checksum", batch.required_warning_codes)
+        with self.assertRaises(ValidationError):
+            commit_assessment_import_batch(batch=batch, actor=self.staff)
+
+    def test_changed_value_updates_and_blank_clear_removes_imported_value(self):
+        self.import_rows()
+        changed = self.preview_rows(assessment_overrides={"Home to 1st": 4.2})
+        self.assertEqual(self.metric_change(changed, "home_to_1st")["action"], "update")
+        commit_assessment_import_batch(
+            batch=self.acknowledge(changed), actor=self.staff
+        )
+        value = AssessmentValue.objects.get(
+            player_assessment__player=self.player,
+            template_metric__metric__key="home_to_1st",
+        )
+        self.assertEqual(value.numeric_value, Decimal("4.2"))
+
+        blank = self.preview_rows(assessment_overrides={"Home to 1st": None})
+        self.assertEqual(self.metric_change(blank, "home_to_1st")["action"], "clear")
+        commit_assessment_import_batch(batch=self.acknowledge(blank), actor=self.staff)
+        self.assertFalse(
+            AssessmentValue.objects.filter(
+                player_assessment__player=self.player,
+                template_metric__metric__key="home_to_1st",
+            ).exists()
+        )
+
+    def test_removed_mapping_metric_does_not_delete_historical_value(self):
+        self.import_rows()
+        config = deepcopy(self.import_template.config)
+        config["sheets"][0]["metrics"] = [
+            metric
+            for metric in config["sheets"][0]["metrics"]
+            if metric["key"] != "home_to_1st"
+        ]
+        mapping = self.custom_import_template(config, version=101)
+        headers = [
+            header
+            for header in self.import_template.config["sheets"][0]["metrics"]
+            if header["key"] != "home_to_1st"
+        ]
+        source_headers = ["Name", *[metric["header"] for metric in headers]]
+        source_values = assessment_row()[2:]
+        batch = create_assessment_import_batch(
+            file_obj=uploaded_workbook(
+                workbook_bytes(
+                    assessment_headers=source_headers,
+                    assessment_rows=[["Alex Example", *source_values]],
+                    pitching_rows=[pitching_row()],
+                )
+            ),
+            event=self.event,
+            import_template=mapping,
+            uploaded_by=self.staff,
+        )
+        commit_assessment_import_batch(batch=self.acknowledge(batch), actor=self.staff)
+        self.assertTrue(
+            AssessmentValue.objects.filter(
+                player_assessment__player=self.player,
+                template_metric__metric__key="home_to_1st",
+            ).exists()
+        )
+
+    def test_frozen_mapping_is_used_after_live_mapping_changes(self):
+        batch = self.preview_rows()
+        frozen_checksum = batch.config_checksum
+        live = batch.import_template
+        live.config = {"mapping_version": 999, "sheets": []}
+        live.save()
+        batch.refresh_from_db()
+        self.assertEqual(batch.config_checksum, frozen_checksum)
+        self.assertTrue(batch.config_snapshot["sheets"])
+        commit_assessment_import_batch(batch=self.acknowledge(batch), actor=self.staff)
+        self.assertTrue(PlayerAssessment.objects.filter(player=self.player).exists())
+
+    def test_manual_override_identical_is_protected_without_conflict(self):
+        self.import_rows()
+        value = AssessmentValue.objects.get(
+            player_assessment__player=self.player,
+            template_metric__metric__key="home_to_1st",
+        )
+        correct_assessment_value(
+            assessment_value=value,
+            actor=self.staff,
+            reason="Confirmed existing value",
+            new_value="4.1",
+        )
+        batch = self.preview_rows()
+        change = self.metric_change(batch, "home_to_1st")
+        self.assertEqual(change["action"], "protected_manual")
+        self.assertEqual(batch.rows.get().conflict_status, "none")
+
+    def test_manual_override_difference_and_blank_require_preserve_resolution(self):
+        self.import_rows()
+        value = AssessmentValue.objects.get(
+            player_assessment__player=self.player,
+            template_metric__metric__key="home_to_1st",
+        )
+        correct_assessment_value(
+            assessment_value=value,
+            actor=self.staff,
+            reason="Timing video review",
+            new_value="4.3",
+        )
+        for incoming in [4.2, None]:
+            batch = self.preview_rows(assessment_overrides={"Home to 1st": incoming})
+            row = batch.rows.get()
+            self.assertEqual(row.conflict_status, "unresolved")
+            self.assertEqual(
+                self.metric_change(batch, "home_to_1st")["action"], "conflict"
+            )
+            with self.assertRaises(ValidationError):
+                commit_assessment_import_batch(batch=batch, actor=self.staff)
+            preserve_manual_override_conflicts(row=row, actor=self.staff)
+            batch = self.acknowledge(batch)
+            commit_assessment_import_batch(batch=batch, actor=self.staff)
+            value.refresh_from_db()
+            self.assertEqual(value.numeric_value, Decimal("4.3"))
diff --git a/analytics/tests/test_assessment_workbook_validation.py b/analytics/tests/test_assessment_workbook_validation.py
new file mode 100644
index 0000000..48b1ef6
--- /dev/null
+++ b/analytics/tests/test_assessment_workbook_validation.py
@@ -0,0 +1,277 @@
+from copy import deepcopy
+from io import BytesIO
+
+from django.core.exceptions import ValidationError
+from django.test import override_settings
+from openpyxl import Workbook
+
+from analytics.models import ASSESSMENT_IMPORT_STATUS_FAILED
+from analytics.services.assessment_import_service import (
+    create_assessment_import_batch,
+    parse_assessment_workbook,
+    resolve_assessment_import_row,
+    summarize_import_batch,
+)
+from analytics.tests.assessment_test_helpers import (
+    ASSESSMENT_HEADERS,
+    AssessmentTestMixin,
+    assessment_row,
+    minimal_config,
+    minimal_workbook,
+    uploaded_workbook,
+    workbook_bytes,
+)
+from analytics.tests.helpers import TestCase
+
+
+def issue_codes(issues):
+    return {issue["code"] for issue in issues}
+
+
+class WorkbookStructureTests(AssessmentTestMixin, TestCase):
+    def create_batch(self, content, *, import_template=None, name="assessment.xlsx"):
+        return create_assessment_import_batch(
+            file_obj=uploaded_workbook(content, name=name),
+            event=self.event,
+            import_template=import_template or self.import_template,
+            uploaded_by=self.staff,
+        )
+
+    def test_empty_workbook_and_no_player_rows_are_not_committable(self):
+        empty = Workbook()
+        output = BytesIO()
+        empty.save(output)
+        batch = self.create_batch(output.getvalue())
+        self.assertIn("required_sheet_missing", issue_codes(batch.validation_errors))
+        self.assertIn("no_valid_player_rows", issue_codes(batch.validation_errors))
+        self.assertFalse(summarize_import_batch(batch).can_commit)
+
+        no_rows = self.create_batch(
+            workbook_bytes(assessment_rows=[], pitching_rows=[])
+        )
+        self.assertIn("no_player_rows", issue_codes(no_rows.validation_errors))
+        self.assertFalse(summarize_import_batch(no_rows).can_commit)
+
+    def test_missing_required_sheet_blocks_and_missing_optional_sheet_warns(self):
+        missing_required = self.create_batch(
+            workbook_bytes(
+                include_assessment=False,
+                pitching_rows=[],
+            )
+        )
+        self.assertIn(
+            "required_sheet_missing", issue_codes(missing_required.validation_errors)
+        )
+
+        missing_optional = self.create_batch(
+            workbook_bytes(
+                assessment_rows=[assessment_row()],
+                include_pitching=False,
+            )
+        )
+        self.assertIn(
+            "optional_sheet_missing", issue_codes(missing_optional.validation_warnings)
+        )
+
+    def test_missing_header_row_identity_and_metric_header_block(self):
+        missing_header_row = self.create_batch(
+            workbook_bytes(
+                assessment_rows=[assessment_row()],
+                include_pitching=False,
+                assessment_header_row=2,
+            ),
+            import_template=self.custom_import_template(
+                {
+                    **deepcopy(self.import_template.config),
+                    "sheets": [
+                        {
+                            **deepcopy(self.import_template.config["sheets"][0]),
+                            "header_row": 99,
+                        }
+                    ],
+                },
+                version=100,
+            ),
+        )
+        self.assertIn(
+            "header_row_missing", issue_codes(missing_header_row.validation_errors)
+        )
+
+        headers_without_identity = ["Player", *ASSESSMENT_HEADERS[1:]]
+        missing_identity = self.create_batch(
+            workbook_bytes(
+                assessment_rows=[assessment_row()],
+                assessment_headers=headers_without_identity,
+                include_pitching=False,
+            )
+        )
+        self.assertIn(
+            "identity_header_missing", issue_codes(missing_identity.validation_errors)
+        )
+
+        missing_metric = self.create_batch(
+            workbook_bytes(
+                assessment_rows=[assessment_row()[:-1]],
+                assessment_headers=ASSESSMENT_HEADERS[:-1],
+                include_pitching=False,
+            )
+        )
+        self.assertIn(
+            "required_metric_header_missing",
+            issue_codes(missing_metric.validation_errors),
+        )
+
+    def test_unexpected_column_warns_and_header_alias_supports_new_mapping_version(
+        self,
+    ):
+        unexpected = self.create_batch(
+            workbook_bytes(
+                assessment_rows=[assessment_row()],
+                pitching_rows=[],
+                extra_assessment_headers=["Operator Note"],
+            )
+        )
+        self.assertIn("unexpected_column", issue_codes(unexpected.validation_warnings))
+
+        config = minimal_config(header="Time", header_aliases=["Sprint Time"])
+        parsed = parse_assessment_workbook(
+            minimal_workbook([["Synthetic Player", 4.2]], header="  SPRINT   TIME. "),
+            config,
+        )
+        self.assertFalse(parsed["errors"])
+        self.assertEqual(parsed["rows"][0]["values"][0]["numeric_value"], "4.2")
+
+    def test_malformed_workbook_persists_failed_batch_without_player_data(self):
+        batch = self.create_batch(b"not a workbook")
+        self.assertEqual(batch.status, ASSESSMENT_IMPORT_STATUS_FAILED)
+        self.assertIn("workbook_parse_failed", issue_codes(batch.validation_errors))
+        self.assertFalse(batch.rows.exists())
+
+    def test_wrong_extension_and_upload_size_are_rejected(self):
+        with self.assertRaises(ValidationError):
+            self.create_batch(b"data", name="assessment.csv")
+        with override_settings(ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES=10):
+            with self.assertRaises(ValidationError):
+                self.create_batch(workbook_bytes(assessment_rows=[], pitching_rows=[]))
+
+        with override_settings(ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES=100):
+            batch = self.create_batch(
+                workbook_bytes(
+                    assessment_rows=[assessment_row()],
+                    pitching_rows=[],
+                )
+            )
+        self.assertEqual(batch.status, ASSESSMENT_IMPORT_STATUS_FAILED)
+
+    def test_row_and_column_limits_block_preview(self):
+        row_config = minimal_config()
+        row_config["sheets"][0]["max_rows"] = 2
+        parsed = parse_assessment_workbook(
+            minimal_workbook([["One", 1], ["Two", 2]]), row_config
+        )
+        self.assertIn("worksheet_row_limit", issue_codes(parsed["errors"]))
+
+        column_config = minimal_config()
+        column_config["sheets"][0]["max_columns"] = 2
+        parsed = parse_assessment_workbook(
+            minimal_workbook([["One", 1]], extra_headers=["Extra"]), column_config
+        )
+        self.assertIn("worksheet_column_limit", issue_codes(parsed["errors"]))
+
+    def test_worksheet_and_cell_text_limits_block_preview(self):
+        worksheet_config = minimal_config()
+        worksheet_config["limits"]["max_worksheets"] = 1
+        parsed_batch = self.create_batch(
+            workbook_bytes(assessment_rows=[assessment_row()], pitching_rows=[]),
+            import_template=self.custom_import_template(
+                worksheet_config,
+                version=102,
+            ),
+        )
+        self.assertEqual(parsed_batch.status, ASSESSMENT_IMPORT_STATUS_FAILED)
+
+        cell_config = minimal_config(value_type="text")
+        cell_config["limits"]["max_cell_text_length"] = 5
+        parsed = parse_assessment_workbook(
+            minimal_workbook([["Synthetic Player", "too long"]]),
+            cell_config,
+        )
+        row_codes = {
+            issue["code"] for row in parsed["rows"] for issue in row.get("errors", [])
+        }
+        self.assertIn("cell_text_too_long", row_codes)
+
+    def test_assigning_player_does_not_clear_numeric_validation_errors(self):
+        content = workbook_bytes(
+            assessment_rows=[assessment_row(**{"Athletic Stance": 4})],
+            pitching_rows=[],
+        )
+        batch = self.create_batch(content)
+        row = batch.rows.get()
+        self.assertEqual(row.validation_status, "invalid")
+
+        with self.assertRaises(ValidationError):
+            resolve_assessment_import_row(row=row, player=self.player)
+
+        row.refresh_from_db()
+        self.assertEqual(row.validation_status, "invalid")
+        self.assertFalse(summarize_import_batch(batch).can_commit)
+
+
+class NumericPolicyTests(TestCase):
+    def parse_value(self, value, **config_options):
+        parsed = parse_assessment_workbook(
+            minimal_workbook([["Synthetic Player", value]]),
+            minimal_config(**config_options),
+        )
+        return parsed["rows"][0]["values"][0]
+
+    def test_rating_accepts_only_integers_one_to_three(self):
+        valid = self.parse_value(2, value_type="rating")
+        self.assertFalse(valid["errors"])
+        for invalid in [0, 1.5, 4, "not numeric"]:
+            snapshot = self.parse_value(invalid, value_type="rating")
+            self.assertTrue(snapshot["errors"], invalid)
+            self.assertEqual(snapshot["raw_value"], str(invalid))
+
+    def test_numeric_minimum_maximum_and_invalid_text(self):
+        self.assertIn(
+            "value_below_minimum",
+            issue_codes(self.parse_value(2, min_value=3)["errors"]),
+        )
+        self.assertIn(
+            "value_above_maximum",
+            issue_codes(self.parse_value(8, max_value=7)["errors"]),
+        )
+        self.assertIn(
+            "invalid_numeric_value",
+            issue_codes(self.parse_value("bad")["errors"]),
+        )
+
+    def test_all_zero_policies(self):
+        allowed = self.parse_value(0, zero_policy="allow")
+        self.assertEqual(allowed["numeric_value"], "0")
+
+        missing = self.parse_value(0, zero_policy="treat_as_missing")
+        self.assertTrue(missing["is_blank"])
+        self.assertIn("zero_treated_as_missing", issue_codes(missing["warnings"]))
+        self.assertTrue(missing["transformations"])
+
+        warning = self.parse_value(0, zero_policy="warning")
+        self.assertEqual(warning["numeric_value"], "0")
+        self.assertIn("zero_requires_review", issue_codes(warning["warnings"]))
+
+        error = self.parse_value(0, zero_policy="error")
+        self.assertIn("zero_not_allowed", issue_codes(error["errors"]))
+
+    def test_blank_policies_and_required_blank(self):
+        for policy in [
+            "preserve_existing",
+            "clear_existing_imported_value",
+            "ignore_on_create",
+        ]:
+            snapshot = self.parse_value(None, blank_policy=policy)
+            self.assertTrue(snapshot["is_blank"])
+            self.assertFalse(snapshot["errors"])
+        required = self.parse_value(None, blank_policy="error_if_required")
+        self.assertIn("required_value_missing", issue_codes(required["errors"]))
diff --git a/analytics/views.py b/analytics/views.py
index b0d14df..a831e45 100644
--- a/analytics/views.py
+++ b/analytics/views.py
@@ -16,9 +16,13 @@ from analytics.forms import (
     parse_conflict_resolutions,
 )
 from analytics.models import (
-    ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
-    ASSESSMENT_IMPORT_ROW_INVALID,
-    ASSESSMENT_IMPORT_ROW_UNMATCHED,
+    ASSESSMENT_CONFLICT_UNRESOLVED,
+    ASSESSMENT_IMPORT_ROW_SKIPPED,
+    ASSESSMENT_IMPORT_STATUS_FAILED,
+    ASSESSMENT_MATCH_AMBIGUOUS,
+    ASSESSMENT_MATCH_UNMATCHED,
+    ASSESSMENT_VALIDATION_INVALID,
+    ASSESSMENT_VALIDATION_VALID,
     EVALUATION_PERSPECTIVE_CHOICES,
     OBSERVATION_STATUS_SUBMITTED,
     OBSERVATION_TYPE_COACH_ASSESSMENT,
@@ -30,9 +34,11 @@ from analytics.models import (
 )
 from analytics.services.assessment_feature import assessments_enabled
 from analytics.services.assessment_import_service import (
+    acknowledge_assessment_import_warnings,
     assessment_records_for_player,
     commit_assessment_import_batch,
     create_assessment_import_batch,
+    preserve_manual_override_conflicts,
     resolve_assessment_import_row,
     summarize_import_batch,
 )
@@ -391,6 +397,12 @@ class AssessmentImportUploadView(AssessmentFeatureRequiredMixin, FormView):
         except ValidationError as exc:
             form.add_error(None, exc)
             return self.render_to_response(self.get_context_data(form=form))
+        if batch.status == ASSESSMENT_IMPORT_STATUS_FAILED:
+            messages.error(
+                self.request,
+                "Assessment workbook could not be parsed safely. Review the persisted failure details.",
+            )
+            return redirect("analytics:assessment-import-detail", pk=batch.pk)
         messages.success(
             self.request,
             "Assessment workbook uploaded. Review matches before committing.",
@@ -404,7 +416,13 @@ class AssessmentImportBatchMixin(AssessmentFeatureRequiredMixin):
     def dispatch(self, request, *args, **kwargs):
         self.assessment_import_batch = get_object_or_404(
             AssessmentImportBatch.objects.select_related(
-                "event", "event__season", "import_template"
+                "event",
+                "event__season",
+                "event__template",
+                "event__scoring_profile",
+                "import_template",
+                "import_template__assessment_template",
+                "warnings_acknowledged_by",
             ),
             pk=kwargs["pk"],
         )
@@ -423,21 +441,36 @@ class AssessmentImportPreviewView(AssessmentImportBatchMixin, TemplateView):
     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context["rows"] = self.assessment_import_batch.rows.select_related(
-            "player", "roster_membership"
+            "player", "roster_membership", "roster_membership__season_team"
         )
         return context

+    def post(self, request, *args, **kwargs):
+        try:
+            acknowledge_assessment_import_warnings(
+                batch=self.assessment_import_batch,
+                actor=request.user,
+                token=request.POST.get("acknowledgement_token", ""),
+            )
+        except (PermissionDenied, ValidationError) as exc:
+            messages.error(request, str(exc))
+        else:
+            messages.success(
+                request, "Current assessment import warnings acknowledged."
+            )
+        return redirect(
+            "analytics:assessment-import-preview",
+            pk=self.assessment_import_batch.pk,
+        )
+

 class AssessmentImportResolveView(AssessmentImportBatchMixin, TemplateView):
     template_name = "analytics/assessment_import_resolve.html"

     def _review_rows(self):
         return self.assessment_import_batch.rows.select_related("player").filter(
-            status__in=[
-                ASSESSMENT_IMPORT_ROW_UNMATCHED,
-                ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
-                ASSESSMENT_IMPORT_ROW_INVALID,
-            ]
+            validation_status=ASSESSMENT_VALIDATION_VALID,
+            match_status__in=[ASSESSMENT_MATCH_UNMATCHED, ASSESSMENT_MATCH_AMBIGUOUS],
         )

     def get_context_data(self, **kwargs):
@@ -446,9 +479,17 @@ class AssessmentImportResolveView(AssessmentImportBatchMixin, TemplateView):
             (row, AssessmentImportRowResolutionForm(row=row))
             for row in self._review_rows()
         ]
+        context["invalid_rows"] = self.assessment_import_batch.rows.filter(
+            validation_status=ASSESSMENT_VALIDATION_INVALID
+        ).exclude(status=ASSESSMENT_IMPORT_ROW_SKIPPED)
+        context["conflict_rows"] = self.assessment_import_batch.rows.filter(
+            conflict_status=ASSESSMENT_CONFLICT_UNRESOLVED
+        ).exclude(status=ASSESSMENT_IMPORT_ROW_SKIPPED)
         return context

     def post(self, request, *args, **kwargs):
+        saved = 0
+        failed = 0
         for row in self._review_rows():
             form = AssessmentImportRowResolutionForm(
                 data={
@@ -458,12 +499,41 @@ class AssessmentImportResolveView(AssessmentImportBatchMixin, TemplateView):
                 row=row,
             )
             if form.is_valid():
-                resolve_assessment_import_row(
-                    row=row,
-                    player=form.cleaned_data.get("player"),
-                    skip=form.cleaned_data.get("skip"),
-                )
-        messages.success(request, "Assessment import resolutions updated.")
+                try:
+                    resolve_assessment_import_row(
+                        row=row,
+                        player=form.cleaned_data.get("player"),
+                        skip=form.cleaned_data.get("skip"),
+                    )
+                except ValidationError as exc:
+                    failed += 1
+                    messages.error(request, f"{row.raw_identity}: {exc}")
+                else:
+                    saved += 1
+            else:
+                failed += 1
+                messages.error(request, f"{row.raw_identity}: {form.errors.as_text()}")
+        for row in self.assessment_import_batch.rows.filter(
+            validation_status=ASSESSMENT_VALIDATION_INVALID
+        ).exclude(status=ASSESSMENT_IMPORT_ROW_SKIPPED):
+            if request.POST.get(f"row_{row.pk}_skip"):
+                resolve_assessment_import_row(row=row, player=None, skip=True)
+                saved += 1
+        for row in self.assessment_import_batch.rows.filter(
+            conflict_status=ASSESSMENT_CONFLICT_UNRESOLVED
+        ).exclude(status=ASSESSMENT_IMPORT_ROW_SKIPPED):
+            if request.POST.get(f"row_{row.pk}_preserve_manual"):
+                try:
+                    preserve_manual_override_conflicts(row=row, actor=request.user)
+                except (PermissionDenied, ValidationError) as exc:
+                    failed += 1
+                    messages.error(request, f"{row.raw_identity}: {exc}")
+                else:
+                    saved += 1
+        if saved:
+            messages.success(request, f"Updated {saved} assessment import row(s).")
+        if failed:
+            messages.error(request, f"{failed} row resolution(s) require attention.")
         return redirect(
             "analytics:assessment-import-preview",
             pk=self.assessment_import_batch.pk,
@@ -485,7 +555,7 @@ class AssessmentImportConfirmView(AssessmentImportBatchMixin, View):
             )
         messages.success(
             request,
-            f"Assessment import committed. Created {result.created}, updated {result.updated}, skipped {result.skipped}.",
+            f"Assessment import committed. Created {result.created}, updated {result.updated}, unchanged {result.unchanged}, skipped {result.skipped}.",
         )
         return redirect(
             "analytics:assessment-import-detail", pk=self.assessment_import_batch.pk
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index e0e5433..165e2f7 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -668,16 +668,34 @@ Typical workflow:
 1. Confirm the assessment configuration and event have been created.
 2. Open Assessment Imports.
 3. Upload the `.xlsx` workbook.
-4. Review the preview.
-5. Resolve unmatched, ambiguous, or invalid player rows.
-6. Skip rows that should not be imported.
-7. Confirm the import.
-8. Review imported assessment values from the Assessment Event or a player profile.
+4. Confirm the filename, event, season/division, template versions, row counts, and workbook checksums.
+5. Review workbook errors and warnings. Required workbook errors must be corrected in the source file or mapping before import.
+6. Review every player match and the metric-level planned changes.
+7. Resolve unmatched or ambiguous identities. Choosing a player does not fix invalid workbook data.
+8. Correct the workbook or explicitly skip invalid rows.
+9. Review zero-to-missing transformations and values marked **Unit not confirmed**.
+10. Acknowledge required warnings for the current preview.
+11. Confirm the import only when the page reports that it is ready.
+12. Review imported assessment values from the Assessment Event or a player profile.

 Assessment imports do not create players, teams, roster memberships, or coach assignments. They only attach assessment values to existing players.

 Ranking sheets in the workbook are used for quality review only. They are not imported as ordinary player metrics.

+For the 2026 13U workbook:
+
+- subjective ratings use a 1–3 scale and display as values such as `2 / 3`;
+- `Assessment Data` is required and `Pitching Data` is optional;
+- a player may be absent from the pitching sheet;
+- physical measurement units are not stated by the workbook and display as **Unit not confirmed**;
+- zero Bat Speed, Time 2 Contact, Exit Velocity Average, or Exit Velocity Maximum is treated as missing and requires acknowledgement;
+- other zero physical measurements are rejected;
+- a blank mapped cell can clear a prior imported value during re-import, but it cannot clear a staff correction.
+
+The preview uses separate statuses for player matching, data validation, planned action, and conflicts. An import is blocked until all required errors, unresolved matches, conflicts, and warning acknowledgements are handled. Refreshing or changing the preview invalidates an earlier warning acknowledgement.
+
+On re-import, each metric is shown as create, update, unchanged, clear, skip, protected manual, conflict, or invalid. Unchanged values are not rewritten. Staff corrections are protected and cannot be overwritten by a workbook.
+
 ## Player Imports

 ### Purpose
diff --git a/docs/analytics/architecture/11_assessments.md b/docs/analytics/architecture/11_assessments.md
index d4f41ba..ab5ff5d 100644
--- a/docs/analytics/architecture/11_assessments.md
+++ b/docs/analytics/architecture/11_assessments.md
@@ -2,104 +2,143 @@

 ## Purpose

-The Analytics assessment-event subsystem stores objective and rubric-style workbook assessment data without changing the existing evaluation workflow.
+The Analytics assessment-event subsystem stores structured workbook results without changing the existing evaluation workflow. Evaluations continue to use `Observation`, `ObservationResponse`, `ObservationQuestion`, and `ObservationQuestionSet`; workbook assessments use separate versioned models and are not included in evaluation averages, reports, or comparisons.

-Existing evaluations continue to use `Observation`, `ObservationResponse`, `ObservationQuestion`, and `ObservationQuestionSet`.
+This separation prevents an imported measurement or 1–3 workbook rating from being reinterpreted as an evaluator's 1–5 response.

-Workbook assessment events use separate models so staff can import structured assessment data while preserving the original evaluation architecture.
+## Feature Flag And Access

-## Feature Flag
+Assessment pages are staff-only and controlled by `ANALYTICS_ASSESSMENTS_ENABLED`, which defaults to `false`.

-Assessment-event pages are controlled by:
+When disabled:

-```text
-ANALYTICS_ASSESSMENTS_ENABLED
-```
+- assessment routes return 404;
+- assessment navigation and admin navigation are hidden;
+- player profiles do not query assessment records;
+- existing evaluations, imports, reports, and score calculations continue unchanged.

-The default is `false`.
+## Ownership

-When disabled:
+Analytics owns assessment templates, metric definitions, events, values, imports, matching orchestration, and staff assessment views. Players owns canonical player identity. Seasons owns seasons, teams, roster memberships, and coach assignments.

-- assessment-event routes return 404;
-- assessment import routes return 404;
-- assessment-event navigation is hidden;
-- existing evaluations, imports, and reports continue to work normally.
+Assessment imports attach data to existing players. They never create players, teams, memberships, assignments, or evaluation observations.

-## Ownership
+## Versioned Configuration
+
+An `AssessmentEvent` uses one `AssessmentTemplate` and a compatible `AssessmentScoringProfile`. An `AssessmentImportTemplate` explicitly identifies the assessment template it supports. Upload forms filter incompatible mappings, and the service validates compatibility again.
+
+At upload, the import batch stores a deep copy of the mapping in `config_snapshot` plus a checksum. Parsing and commit use this frozen configuration and persisted row snapshots, not the live mapping. A future mapping change therefore cannot alter an existing preview.
+
+## 2026 13U Workbook Mapping
+
+The initial mapping supports `2026 VCB House - 13u PeeWee Assessment.xlsx`.
+
+- `Assessment Data` is required, with headers on row 2 and `Name` as identity.
+- `Pitching Data` is optional, with headers on row 2 and `Name` as identity. When present, its configured headers are required. Individual players may have no pitching row.
+- `Ranking` and `Pitcher Ranking` are QA/provenance context only and are not imported as metrics.
+
+Required `Assessment Data` metric headers are Home to 1st, Broad Jump, Lateral Jump, Shotput, Bat Speed, Time 2 Contact, Exit Velocity Avg., Exit Velocity Max, Athletic Stance, Balance Stride, Barrel Level, Launch Position, Follow Through, Readiness, Footwork, Glovework, Athleticism, and Fundamental Throwing.
+
+Required `Pitching Data` metric headers are Velocity Avg., Velocity Max, Pitch 1, Pitch 2, Pitch 3, Pitch 4, Athletic Movement, Body Control, Direction, Repeatability, and Command2.

-Analytics owns:
+Header and sheet-name comparison trims whitespace, ignores case, and supports aliases declared by a new mapping version. Missing required structure blocks import. Unexpected or optional missing columns are recorded as warnings rather than silently ignored.

-- assessment templates;
-- assessment metrics;
-- assessment events;
-- player assessment records;
-- assessment value records;
-- workbook assessment imports.
+### Rating Scale

-Players owns canonical player identity.
+All 2026 subjective hitting, fielding, throwing, and pitching ratings are integer choices `1`, `2`, or `3`. Each imported rating preserves scale minimum 1 and maximum 3 on `AssessmentValue`; staff pages display a value such as `2 / 3`. This does not change evaluation `rating_1_5` responses.

-Seasons owns seasons, teams, player roster memberships, and coach assignments.
+### Units

-Assessment imports must reference existing players and existing season context. They must not create players, teams, roster memberships, or coach assignments.
+The workbook does not authoritatively state units for physical measurements or velocities. Their normalized unit is therefore blank and metadata records `unit_status = unverified`. Staff UI displays **Unit not confirmed**. These values must not be used for unit-dependent transformations or comparisons until a new operator-confirmed mapping version records an authoritative unit source.

-## Import Workflow
+### Zero Policies

-Workbook imports are staff-only.
+- Home to 1st, Broad Jump, Lateral Jump, Shotput, Pitching Velocity Average, and Pitching Velocity Maximum reject zero.
+- Bat Speed, Time 2 Contact, Exit Velocity Average, and Exit Velocity Maximum treat zero as missing.
+- Every zero-to-missing conversion preserves the raw zero, transformation reason, and policy and requires staff acknowledgement.
+- The import engine also supports `allow`, `warning`, and `error` policies for future mapping versions.

-The workflow is:
+### Blank And Update Policies

-1. Staff creates or selects an `AssessmentEvent`.
-2. Staff uploads an `.xlsx` workbook using an active `AssessmentImportTemplate`.
-3. The system creates an `AssessmentImportBatch` and preview rows.
-4. The system performs conservative player matching.
-5. Staff resolves or skips unmatched, ambiguous, or invalid rows.
-6. Staff explicitly confirms the import.
-7. The system creates or updates `PlayerAssessment` and `AssessmentValue` records atomically.
+The 2026 mapped metrics use `clear_existing_imported_value`. A blank cell explicitly represented by the same frozen mapping clears a prior imported value during re-import. It never clears a manual correction. A metric absent because a sheet or mapping version is absent is not cleared.

-No assessment values are committed during preview.
+Future mappings may use `preserve_existing`, `ignore_on_create`, or `error_if_required` as appropriate.
+
+## Validation And Preview
+
+Workbook-level validation is persisted separately from row-level validation. A preview cannot commit unless it has at least one valid, non-skipped player row and has no:
+
+- required workbook structure errors;
+- row data errors;
+- unmatched or ambiguous identities;
+- unresolved duplicate rows or values;
+- unresolved manual-correction conflicts;
+- unacknowledged required warnings.
+
+Identity match status, data validation status, import action, and conflict status are separate. Selecting a player resolves only identity; it cannot clear an invalid rating, numeric error, duplicate, or structural error. Invalid rows must be corrected in a new workbook/mapping or explicitly skipped.
+
+Warnings that can affect interpretation, including unverified units, zero transformations, optional missing sheets/columns, unexpected columns, and repeated workbook checksums, require an acknowledgement token tied to the current preview version. Any preview change invalidates the prior acknowledgement. The commit service repeats all readiness, compatibility, checksum, row, conflict, and acknowledgement checks server-side.
+
+Malformed uploads leave an auditable failed batch with safe validation details. They create no preview rows, player assessments, or values.
+
+## Duplicate Handling
+
+Rows from `Assessment Data` and `Pitching Data` for the same normalized identity are joined explicitly. The parser blocks duplicate identities within one worksheet, duplicate namespaced source identifiers, conflicting values for one metric, and distinct identities that collide under slug normalization. It never silently collapses these cases.

 ## Player Matching

-Matching must be conservative:
+Matching is exact and conservative:
+
+1. Exact configured source identifier, including source namespace and identifier type.
+2. Exact canonical full/display name among active memberships in the event season and division.
+3. Exact alias in that season/division roster.
+4. Unique exact canonical full/display name outside the selected roster.
+5. Unique exact alias outside the selected roster.
+6. Manual staff resolution.
+
+Duplicate exact matches are ambiguous and include permitted birth-year, team, and division context. No fuzzy matching or player creation occurs.
+
+## Deterministic Re-import

-- exact source identifiers first, if provided by a future import template;
-- exact player display/full-name match;
-- exact player alias match;
-- otherwise unresolved.
+Preview plans every represented metric as `create`, `update`, `unchanged`, `clear`, `skip`, `protected_manual`, `conflict`, or `invalid`. It displays prior value, incoming raw and normalized values, source location, unit/scale, and warnings.

-Fuzzy matches must not auto-commit.
+Unchanged values are not saved and do not receive timestamp churn. Updates and clears apply atomically. Re-import reuses the unique player/event assessment and does not reassign its original import provenance. A repeated workbook checksum is visible and must be acknowledged.

-Unresolved rows must be manually matched or skipped before confirmation.
+## Manual Corrections

-## Historical Safety
+Workbook import never replaces a manual correction. Identical incoming data is protected without a write. Different or blank incoming data creates a preview conflict that staff must explicitly resolve by preserving the manual value.

-Assessment configuration is versioned.
+Approved corrections use the correction service and require a staff actor and reason. They store old/new snapshots, timestamp, provenance, `source_kind = manual_corrected`, and `is_manual_override = true` in an immutable audit record.

-After committed assessment data exists:
+## Historical Immutability And Admin

-- template identity is locked;
-- template metric meaning, units, scale, order, and type are locked;
-- import template configuration is locked;
-- scoring profile configuration is locked.
+After use, templates, template metrics, metric definitions, mappings, scoring profiles, events, committed assessments, values, batches, and rows reject semantic edit/delete operations at the model boundary. Locked parents cannot receive new metrics. Safe lifecycle deactivation remains available where defined.

-Corrections should create a new version or use explicit manual override behavior rather than silently changing historical meaning.
+Django admin makes locked/committed records read-only and blocks unsafe add/delete operations. Raw workbook JSON is not shown in ordinary list pages. Disabling the feature hides assessment models from admin navigation without affecting unrelated admin pages.

-## 2026 13U Workbook
+## Resource Limits

-The initial workbook support is based on:
+The default limits are:

-```text
-2026 VCB House - 13u PeeWee Assessment.xlsx
-```
+- 10 MiB uploaded `.xlsx` file;
+- 50 MiB total uncompressed workbook archive content;
+- 12 worksheets;
+- 500 rows per configured sheet;
+- 50 columns globally, with stricter sheet-specific limits;
+- 500 characters per cell.

-Configured data sheets:
+Macros, external workbook links, unsupported extensions, malformed/encrypted workbooks, and oversized archives are rejected with safe messages. Operators may lower the byte limits with `ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES` and `ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES`.

-- `Assessment Data`
-- `Pitching Data`
+## Creating A Future Mapping Version

-Ranking sheets are treated as provenance/QA context only:
+Do not edit the 2026 version for a 2027 workbook.

-- `Ranking`
-- `Pitcher Ranking`
+1. Inspect the new workbook and obtain authoritative scale/unit decisions.
+2. Create a new assessment template version if metric meaning changes.
+3. Create a compatible import-template version with explicit sheets, headers, ranges, units, zero policies, and blank policies.
+4. Create a compatible scoring-profile version when needed.
+5. Run bootstrap/configuration validation in dry-run mode.
+6. Test with synthetic fixtures and preview the real workbook without committing.
+7. Create a new event referencing the approved versions.

-Ranking sheets are not imported as ordinary player metrics.
+Historical configuration remains locked; retirement/deactivation is preferred over deletion.
diff --git a/docs/deployment/README.md b/docs/deployment/README.md
index e83987d..adfeca3 100644
--- a/docs/deployment/README.md
+++ b/docs/deployment/README.md
@@ -63,6 +63,7 @@ Future production deployments should:
 - use environment variables for deployment-specific settings;
 - configure `COACH_IMPORT_DEFAULT_PASSWORD` before creating new imported coach accounts;
 - enable `ANALYTICS_ASSESSMENTS_ENABLED` only for staged rollout of workbook assessment imports;
+- retain conservative `ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES` and `ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES` limits;
 - back up the database before migrations;
 - archive media before major upgrades;
 - verify migrations before applying them;
diff --git a/docs/deployment/RUNBOOK.md b/docs/deployment/RUNBOOK.md
index fd032cc..9a6c2b0 100644
--- a/docs/deployment/RUNBOOK.md
+++ b/docs/deployment/RUNBOOK.md
@@ -63,6 +63,8 @@ DJANGO_STATIC_ROOT
 DJANGO_MEDIA_ROOT
 COACH_IMPORT_DEFAULT_PASSWORD
 ANALYTICS_ASSESSMENTS_ENABLED
+ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES
+ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES
 ```

 Verify systemd configuration:
@@ -87,6 +89,11 @@ or shared documentation.
 assessment configuration has been bootstrapped, assessment events have been
 created, and staff are ready to import workbook assessment data.

+Assessment workbook uploads default to a 10 MiB file limit and a 50 MiB
+uncompressed archive limit. Override `ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES` or
+`ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES` only after reviewing production
+memory limits. Lower values are safer; do not raise them casually.
+
 Bootstrap the initial 2026 13U assessment configuration without importing player
 results:

@@ -95,8 +102,45 @@ python manage.py bootstrap_2026_13u_assessment --dry-run
 python manage.py bootstrap_2026_13u_assessment
 ```

-Then enable the feature flag in the environment and restart the application
-service.
+Do not enable the feature as part of a routine deploy. Use the controlled rollout below.
+
+### Controlled Assessment Rollout
+
+#### Stage 1: Back Up And Deploy Disabled
+
+1. Record the current production commit.
+2. Back up `db.sqlite3` and archive media.
+3. Pull the reviewed release and install `requirements.txt`.
+4. Keep `ANALYTICS_ASSESSMENTS_ENABLED=false`.
+5. Run Django checks, review `migrate --plan`, apply migrations, and collect static files if changed.
+6. Restart Gunicorn and verify current self, peer, coach, staff, and guest evaluation workflows.
+7. Confirm assessment navigation is absent.
+
+#### Stage 2: Bootstrap Configuration
+
+1. Run `bootstrap_2026_13u_assessment --dry-run`.
+2. Review every sheet/header requirement, 1–3 rating scale, unit status, zero policy, and blank policy.
+3. Run the bootstrap normally only when the dry run is correct.
+4. Do not import player data during bootstrap.
+
+#### Stage 3: Enable Staff-Only Preview
+
+1. Set `ANALYTICS_ASSESSMENTS_ENABLED=true` and restart Gunicorn.
+2. Confirm only staff can access the pages.
+3. Create/select the assessment event and upload the workbook.
+4. Review every match, warning, zero transformation, unverified unit, and planned action.
+5. Confirm preview created no player-assessment values.
+
+#### Stage 4: Controlled Import
+
+1. Take a second database backup.
+2. Confirm the fully resolved and acknowledged import.
+3. Reconcile database aggregate counts with workbook aggregate counts.
+4. Inspect representative player records and keep the feature staff-only.
+
+### Assessment Rollback
+
+For immediate visual rollback, set `ANALYTICS_ASSESSMENTS_ENABLED=false` and restart Gunicorn. The assessment migrations are additive, so existing evaluations remain available. Do not reverse assessment migrations after production assessment data exists; restore a verified pre-import database backup only as part of an approved destructive rollback.

 ## Deployment

diff --git a/vancouverminor/settings.py b/vancouverminor/settings.py
index 7927ca4..5e2b18e 100644
--- a/vancouverminor/settings.py
+++ b/vancouverminor/settings.py
@@ -40,6 +40,16 @@ def env_list(name, *, default):
     return values or list(default)


+def env_int(name, *, default):
+    raw_value = os.environ.get(name, "").strip()
+    if not raw_value:
+        return default
+    try:
+        return int(raw_value)
+    except ValueError as exc:
+        raise ImproperlyConfigured(f"{name} must be an integer.") from exc
+
+
 # SECURITY WARNING: don't run with debug turned on in production!
 DEBUG = env_bool("DJANGO_DEBUG", default=False)

@@ -50,68 +60,74 @@ COACH_IMPORT_DEFAULT_PASSWORD = os.environ.get(
 ).strip()

 ANALYTICS_ASSESSMENTS_ENABLED = env_bool("ANALYTICS_ASSESSMENTS_ENABLED", default=False)
+ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES = env_int(
+    "ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES", default=10 * 1024 * 1024
+)
+ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES = env_int(
+    "ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES", default=50 * 1024 * 1024
+)


 # Application definition

 INSTALLED_APPS = [
-    'django.contrib.admin',
-    'django.contrib.auth',
-    'django.contrib.contenttypes',
-    'django.contrib.sessions',
-    'django.contrib.messages',
-    'django.contrib.staticfiles',
-    'drafts',
-    'home',
-    'pdp',
-    'leaguehub',
-    'scholarships',
-    'players',
-    'seasons',
-    'analytics',
-    'accounts',
+    "django.contrib.admin",
+    "django.contrib.auth",
+    "django.contrib.contenttypes",
+    "django.contrib.sessions",
+    "django.contrib.messages",
+    "django.contrib.staticfiles",
+    "drafts",
+    "home",
+    "pdp",
+    "leaguehub",
+    "scholarships",
+    "players",
+    "seasons",
+    "analytics",
+    "accounts",
 ]

 MIDDLEWARE = [
-    'django.middleware.security.SecurityMiddleware',
-    'django.contrib.sessions.middleware.SessionMiddleware',
-    'django.middleware.common.CommonMiddleware',
-    'django.middleware.csrf.CsrfViewMiddleware',
-    'django.contrib.auth.middleware.AuthenticationMiddleware',
-    'pdp.middleware.FirstLoginPasswordChangeMiddleware',
-    'accounts.middleware.AccountPasswordChangeRequiredMiddleware',
-    'django.contrib.messages.middleware.MessageMiddleware',
-    'django.middleware.clickjacking.XFrameOptionsMiddleware',
+    "django.middleware.security.SecurityMiddleware",
+    "django.contrib.sessions.middleware.SessionMiddleware",
+    "django.middleware.common.CommonMiddleware",
+    "django.middleware.csrf.CsrfViewMiddleware",
+    "django.contrib.auth.middleware.AuthenticationMiddleware",
+    "pdp.middleware.FirstLoginPasswordChangeMiddleware",
+    "accounts.middleware.AccountPasswordChangeRequiredMiddleware",
+    "django.contrib.messages.middleware.MessageMiddleware",
+    "django.middleware.clickjacking.XFrameOptionsMiddleware",
 ]

-ROOT_URLCONF = 'vancouverminor.urls'
+ROOT_URLCONF = "vancouverminor.urls"

 TEMPLATES = [
     {
-        'BACKEND': 'django.template.backends.django.DjangoTemplates',
-        'DIRS': [BASE_DIR / 'templates'],
-        'APP_DIRS': True,
-        'OPTIONS': {
-            'context_processors': [
-                'django.template.context_processors.debug',
-                'django.template.context_processors.request',
-                'django.contrib.auth.context_processors.auth',
-                'django.contrib.messages.context_processors.messages',
+        "BACKEND": "django.template.backends.django.DjangoTemplates",
+        "DIRS": [BASE_DIR / "templates"],
+        "APP_DIRS": True,
+        "OPTIONS": {
+            "context_processors": [
+                "django.template.context_processors.debug",
+                "django.template.context_processors.request",
+                "django.contrib.auth.context_processors.auth",
+                "django.contrib.messages.context_processors.messages",
             ],
         },
     },
 ]

-WSGI_APPLICATION = 'vancouverminor.wsgi.application'
+WSGI_APPLICATION = "vancouverminor.wsgi.application"


 # Database
 # https://docs.djangoproject.com/en/4.2/ref/settings/#databases

 DATABASES = {
-    'default': {
-        'ENGINE': 'django.db.backends.sqlite3',
-        'NAME': BASE_DIR / 'db.sqlite3',
+    "default": {
+        "ENGINE": "django.db.backends.sqlite3",
+        "NAME": BASE_DIR / "db.sqlite3",
     }
 }

@@ -121,16 +137,16 @@ DATABASES = {

 AUTH_PASSWORD_VALIDATORS = [
     {
-        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
+        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
     },
     {
-        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
+        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     },
     {
-        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
+        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
     },
     {
-        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
+        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
     },
 ]

@@ -138,9 +154,9 @@ AUTH_PASSWORD_VALIDATORS = [
 # Internationalization
 # https://docs.djangoproject.com/en/4.2/topics/i18n/

-LANGUAGE_CODE = 'en-us'
+LANGUAGE_CODE = "en-us"

-TIME_ZONE = 'America/Vancouver'
+TIME_ZONE = "America/Vancouver"

 USE_I18N = True

@@ -150,16 +166,16 @@ USE_TZ = True
 # Static files (CSS, JavaScript, Images)
 # https://docs.djangoproject.com/en/4.2/howto/static-files/

-STATIC_URL = 'static/'
+STATIC_URL = "static/"
 STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", BASE_DIR / "staticfiles")
-STATICFILES_DIRS = [BASE_DIR / 'static']
-MEDIA_URL = '/media/'
+STATICFILES_DIRS = [BASE_DIR / "static"]
+MEDIA_URL = "/media/"
 MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", BASE_DIR / "media")

-LOGIN_URL = '/accounts/login/'
-LOGIN_REDIRECT_URL = '/accounts/profile/'
+LOGIN_URL = "/accounts/login/"
+LOGIN_REDIRECT_URL = "/accounts/profile/"

 # Default primary key field type
 # https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

-DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
+DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

# Versioned Assessment Events

## Purpose

The Analytics assessment-event subsystem stores structured workbook results without changing the existing evaluation workflow. Evaluations continue to use `Observation`, `ObservationResponse`, `ObservationQuestion`, and `ObservationQuestionSet`; workbook assessments use separate versioned models and are not included in evaluation averages, reports, or comparisons.

This separation prevents an imported measurement or 1–3 workbook rating from being reinterpreted as an evaluator's 1–5 response.

## Feature Flag And Access

Assessment pages are staff-only and controlled by `ANALYTICS_ASSESSMENTS_ENABLED`, which defaults to `false`.

When disabled:

- assessment routes return 404;
- assessment navigation and admin navigation are hidden;
- player profiles do not query assessment records;
- existing evaluations, imports, reports, and score calculations continue unchanged.

## Ownership

Analytics owns assessment templates, metric definitions, events, values, imports, matching orchestration, and staff assessment views. Players owns canonical player identity. Seasons owns seasons, teams, roster memberships, and coach assignments.

Assessment imports attach data to existing players. They never create players, teams, memberships, assignments, or evaluation observations.

## Versioned Configuration

An `AssessmentEvent` uses one `AssessmentTemplate` and a compatible `AssessmentScoringProfile`. An `AssessmentImportTemplate` explicitly identifies the assessment template it supports. Upload forms filter incompatible mappings, and the service validates compatibility again.

At upload, the import batch stores a deep copy of the mapping in `config_snapshot` plus a checksum. Parsing and commit use this frozen configuration and persisted row snapshots, not the live mapping. A future mapping change therefore cannot alter an existing preview.

## 2026 13U Workbook Mapping

The initial mapping supports `2026 VCB House - 13u PeeWee Assessment.xlsx`.

- `Assessment Data` is required, with headers on row 2 and `Name` as identity.
- `Pitching Data` is optional, with headers on row 2 and `Name` as identity. When present, its configured headers are required. Individual players may have no pitching row.
- `Ranking` and `Pitcher Ranking` are QA/provenance context only and are not imported as metrics.

Required `Assessment Data` metric headers are Home to 1st, Broad Jump, Lateral Jump, Shotput, Bat Speed, Time 2 Contact, Exit Velocity Avg., Exit Velocity Max, Athletic Stance, Balance Stride, Barrel Level, Launch Position, Follow Through, Readiness, Footwork, Glovework, Athleticism, and Fundamental Throwing.

Required `Pitching Data` metric headers are Velocity Avg., Velocity Max, Pitch 1, Pitch 2, Pitch 3, Pitch 4, Athletic Movement, Body Control, Direction, Repeatability, and Command2.

Header and sheet-name comparison trims whitespace, ignores case, and supports aliases declared by a new mapping version. Missing required structure blocks import. Unexpected or optional missing columns are recorded as warnings rather than silently ignored.

### Rating Scale

All 2026 subjective hitting, fielding, throwing, and pitching ratings are integer choices `1`, `2`, or `3`. Each imported rating preserves scale minimum 1 and maximum 3 on `AssessmentValue`; staff pages display a value such as `2 / 3`. This does not change evaluation `rating_1_5` responses.

### Units

The workbook does not authoritatively state units for physical measurements or velocities. Their normalized unit is therefore blank and metadata records `unit_status = unverified`. Staff UI displays **Unit not confirmed**. These values must not be used for unit-dependent transformations or comparisons until a new operator-confirmed mapping version records an authoritative unit source.

### Zero Policies

- Home to 1st, Broad Jump, Lateral Jump, Shotput, Pitching Velocity Average, and Pitching Velocity Maximum reject zero.
- Bat Speed, Time 2 Contact, Exit Velocity Average, and Exit Velocity Maximum treat zero as missing.
- Every zero-to-missing conversion preserves the raw zero, transformation reason, and policy and requires staff acknowledgement.
- The import engine also supports `allow`, `warning`, and `error` policies for future mapping versions.

### Blank And Update Policies

The 2026 mapped metrics use `clear_existing_imported_value`. A blank cell explicitly represented by the same frozen mapping clears a prior imported value during re-import. It never clears a manual correction. A metric absent because a sheet or mapping version is absent is not cleared.

Future mappings may use `preserve_existing`, `ignore_on_create`, or `error_if_required` as appropriate.

## Validation And Preview

Workbook-level validation is persisted separately from row-level validation. A preview cannot commit unless it has at least one valid, non-skipped player row and has no:

- required workbook structure errors;
- row data errors;
- unmatched or ambiguous identities;
- unresolved duplicate rows or values;
- unresolved manual-correction conflicts;
- unacknowledged required warnings.

Identity match status, data validation status, import action, and conflict status are separate. Selecting a player resolves only identity; it cannot clear an invalid rating, numeric error, duplicate, or structural error. Invalid rows must be corrected in a new workbook/mapping or explicitly skipped.

Warnings that can affect interpretation, including unverified units, zero transformations, optional missing sheets/columns, unexpected columns, and repeated workbook checksums, require an acknowledgement token tied to the current preview version. Any preview change invalidates the prior acknowledgement. The commit service repeats all readiness, compatibility, checksum, row, conflict, and acknowledgement checks server-side.

Malformed uploads leave an auditable failed batch with safe validation details. They create no preview rows, player assessments, or values.

## Duplicate Handling

Rows from `Assessment Data` and `Pitching Data` for the same normalized identity are joined explicitly. The parser blocks duplicate identities within one worksheet, duplicate namespaced source identifiers, conflicting values for one metric, and distinct identities that collide under slug normalization. It never silently collapses these cases.

## Player Matching

Matching is exact and conservative:

1. Exact configured source identifier, including source namespace and identifier type.
2. Exact canonical full/display name among active memberships in the event season and division.
3. Exact alias in that season/division roster.
4. Unique exact canonical full/display name outside the selected roster.
5. Unique exact alias outside the selected roster.
6. Manual staff resolution.

Duplicate exact matches are ambiguous and include permitted birth-year, team, and division context. No fuzzy matching or player creation occurs.

## Deterministic Re-import

Preview plans every represented metric as `create`, `update`, `unchanged`, `clear`, `skip`, `protected_manual`, `conflict`, or `invalid`. It displays prior value, incoming raw and normalized values, source location, unit/scale, and warnings.

Unchanged values are not saved and do not receive timestamp churn. Updates and clears apply atomically. Re-import reuses the unique player/event assessment and does not reassign its original import provenance. A repeated workbook checksum is visible and must be acknowledged.

## Manual Corrections

Workbook import never replaces a manual correction. Identical incoming data is protected without a write. Different or blank incoming data creates a preview conflict that staff must explicitly resolve by preserving the manual value.

Approved corrections use the correction service and require a staff actor and reason. They store old/new snapshots, timestamp, provenance, `source_kind = manual_corrected`, and `is_manual_override = true` in an immutable audit record.

## Historical Immutability And Admin

After use, templates, template metrics, metric definitions, mappings, scoring profiles, events, committed assessments, values, batches, and rows reject semantic edit/delete operations at the model boundary. Locked parents cannot receive new metrics. Safe lifecycle deactivation remains available where defined.

Django admin makes locked/committed records read-only and blocks unsafe add/delete operations. Raw workbook JSON is not shown in ordinary list pages. Disabling the feature hides assessment models from admin navigation without affecting unrelated admin pages.

## Resource Limits

The default limits are:

- 10 MiB uploaded `.xlsx` file;
- 50 MiB total uncompressed workbook archive content;
- 12 worksheets;
- 500 rows per configured sheet;
- 50 columns globally, with stricter sheet-specific limits;
- 500 characters per cell.

Macros, external workbook links, unsupported extensions, malformed/encrypted workbooks, and oversized archives are rejected with safe messages. Operators may lower the byte limits with `ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES` and `ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES`.

## Creating A Future Mapping Version

Do not edit the 2026 version for a 2027 workbook.

1. Inspect the new workbook and obtain authoritative scale/unit decisions.
2. Create a new assessment template version if metric meaning changes.
3. Create a compatible import-template version with explicit sheets, headers, ranges, units, zero policies, and blank policies.
4. Create a compatible scoring-profile version when needed.
5. Run bootstrap/configuration validation in dry-run mode.
6. Test with synthetic fixtures and preview the real workbook without committing.
7. Create a new event referencing the approved versions.

Historical configuration remains locked; retirement/deactivation is preferred over deletion.

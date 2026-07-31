# Versioned Assessment Events

## Purpose

The Analytics assessment-event subsystem stores objective and rubric-style workbook assessment data without changing the existing evaluation workflow.

Existing evaluations continue to use `Observation`, `ObservationResponse`, `ObservationQuestion`, and `ObservationQuestionSet`.

Workbook assessment events use separate models so staff can import structured assessment data while preserving the original evaluation architecture.

## Feature Flag

Assessment-event pages are controlled by:

```text
ANALYTICS_ASSESSMENTS_ENABLED
```

The default is `false`.

When disabled:

- assessment-event routes return 404;
- assessment import routes return 404;
- assessment-event navigation is hidden;
- existing evaluations, imports, and reports continue to work normally.

## Ownership

Analytics owns:

- assessment templates;
- assessment metrics;
- assessment events;
- player assessment records;
- assessment value records;
- workbook assessment imports.

Players owns canonical player identity.

Seasons owns seasons, teams, player roster memberships, and coach assignments.

Assessment imports must reference existing players and existing season context. They must not create players, teams, roster memberships, or coach assignments.

## Import Workflow

Workbook imports are staff-only.

The workflow is:

1. Staff creates or selects an `AssessmentEvent`.
2. Staff uploads an `.xlsx` workbook using an active `AssessmentImportTemplate`.
3. The system creates an `AssessmentImportBatch` and preview rows.
4. The system performs conservative player matching.
5. Staff resolves or skips unmatched, ambiguous, or invalid rows.
6. Staff explicitly confirms the import.
7. The system creates or updates `PlayerAssessment` and `AssessmentValue` records atomically.

No assessment values are committed during preview.

## Player Matching

Matching must be conservative:

- exact source identifiers first, if provided by a future import template;
- exact player display/full-name match;
- exact player alias match;
- otherwise unresolved.

Fuzzy matches must not auto-commit.

Unresolved rows must be manually matched or skipped before confirmation.

## Historical Safety

Assessment configuration is versioned.

After committed assessment data exists:

- template identity is locked;
- template metric meaning, units, scale, order, and type are locked;
- import template configuration is locked;
- scoring profile configuration is locked.

Corrections should create a new version or use explicit manual override behavior rather than silently changing historical meaning.

## 2026 13U Workbook

The initial workbook support is based on:

```text
2026 VCB House - 13u PeeWee Assessment.xlsx
```

Configured data sheets:

- `Assessment Data`
- `Pitching Data`

Ranking sheets are treated as provenance/QA context only:

- `Ranking`
- `Pitcher Ranking`

Ranking sheets are not imported as ordinary player metrics.

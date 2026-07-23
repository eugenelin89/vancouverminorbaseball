# Prompt 98 - Platform

## User Prompt

Review the existing Platform E2E QA package under:

`docs/qa/platform_e2e/`

This is an incremental documentation improvement only.

Do not rewrite the QA package from scratch.

Do not reorganize existing sections unless a small change is necessary to add references cleanly.

Do not modify application code.

Do not modify CSV fixtures unless documentation inspection reveals a clear inconsistency.

The current package already includes:

- a production smoke test
- release-blocking tests
- standard regression tests
- extended edge-case tests
- repeat-deployment guidance
- reusable QA fixture and lifecycle guidance
- cleanup and retention guidance

The goal of this task is to make the package easier to maintain, prioritize, audit, and automate as the VCB Platform grows.

---

# Goal

Add:

1. Stable feature and requirement identifiers.
2. A feature-to-test traceability matrix.
3. Risk classification.
4. Automation-readiness classification.
5. QA package version history.
6. Release-pipeline guidance.
7. Lightweight conventions for maintaining traceability in future changes.

Keep the documentation practical for a small team.

Do not introduce heavyweight enterprise process, unnecessary approval gates, or duplicate test instructions.

---

# 1. Inspect the Existing QA Package

Read all files under:

`docs/qa/platform_e2e/`

At minimum, inspect:

```text
README.md
platform_e2e_test_script.md
production_smoke_test.md
manual_test_records.md
negative_test_fixtures.md
cleanup_checklist.md
```

Identify the major tested platform capabilities.

Likely capability groups include:

- player import
- coach import
- account provisioning
- username generation
- email reuse and conflict handling
- manual account creation
- account activation
- password change
- season and team assignments
- coach evaluation
- self-evaluation
- peer evaluation
- evaluation cycles
- review and reopen workflow
- permissions
- Analytics Command Center
- player timeline
- player comparison
- mobile behavior
- cleanup and retention

Use the existing documentation and actual application terminology.

Do not invent platform features or claim unsupported behavior.

---

# 2. Define Stable Requirement IDs

Create a concise requirement-ID convention.

Use prefixes based on capability area.

Recommended prefixes:

```text
IMP  Imports
ACC  Accounts and provisioning
ASN  Assignments and memberships
EVL  Evaluations
REV  Review workflow
SEC  Security and permissions
ANA  Analytics and reporting
NAV  Navigation and usability
OPS  QA operations and lifecycle
```

Assign stable IDs to the important behaviors already tested.

Example format:

```text
IMP-001
ACC-001
EVL-001
SEC-001
```

Use three-digit numbering.

Do not assign an ID to every individual checkbox.

Assign IDs at the feature or testable-requirement level.

Suggested initial set:

```text
IMP-001  Player CSV import
IMP-002  Coach CSV import
IMP-003  Import idempotency
IMP-004  Import preview and conflict reporting

ACC-001  Player account provisioning
ACC-002  Coach account provisioning
ACC-003  Username generation and collision handling
ACC-004  Email normalization, reuse, and conflict handling
ACC-005  Account activation lifecycle
ACC-006  Temporary password and forced password change
ACC-007  Manual account creation

ASN-001  Player roster membership
ASN-002  Coach season assignment
ASN-003  Historical assignment preservation

EVL-001  Coach evaluation
EVL-002  Player self-evaluation
EVL-003  Player peer evaluation
EVL-004  Draft save and reopen
EVL-005  Evaluation uniqueness and duplicate prevention
EVL-006  Evaluation-cycle isolation
EVL-007  Imported/manual workflow consistency

REV-001  Evaluation review
REV-002  Reopen and resubmit
REV-003  Evaluation metadata and attribution

SEC-001  Staff-only import permissions
SEC-002  Account and season administration permissions
SEC-003  Evaluation privacy and ownership
SEC-004  Anonymous-user redirects

ANA-001  Command Center integrity
ANA-002  Command Center metrics
ANA-003  Player timeline
ANA-004  Player comparison
ANA-005  Review and reporting filters

NAV-001  Core navigation
NAV-002  Mobile usability
NAV-003  Browser refresh and back-button behavior
NAV-004  Multi-tab stale-update behavior

OPS-001  Production smoke-test repeatability
OPS-002  QA environment retention
OPS-003  Cleanup and archival
OPS-004  Negative-test fixture isolation
```

Inspect the current documentation and adjust the list where needed.

Avoid numbering gaps unless they support clear grouping.

Once assigned, IDs should remain stable across future documentation updates.

---

# 3. Create `feature_traceability.md`

Create:

`docs/qa/platform_e2e/feature_traceability.md`

Include:

## Purpose

Explain briefly that this file maps platform capabilities to:

- requirement IDs
- risk
- smoke-test coverage
- release-blocking coverage
- standard regression coverage
- extended edge-case coverage
- automation readiness
- primary QA document section

## Risk levels

Use:

```text
Critical
High
Medium
Low
```

Define them concisely.

Suggested meanings:

- Critical: failure could expose data, break access control, corrupt imports, prevent login, or invalidate core evaluations.
- High: failure materially breaks a major workflow or reporting result.
- Medium: failure reduces usability or affects a secondary workflow.
- Low: uncommon edge case or limited operational inconvenience.

## Automation readiness

Use:

```text
Manual
Semi-automatable
Fully automatable
```

Define them:

- Manual: requires human judgment, visual review, or environment decisions.
- Semi-automatable: setup or verification can be automated, but some human review remains.
- Fully automatable: deterministic behavior suitable for unit, integration, or browser automation.

## Matrix

Create a Markdown table with columns similar to:

| Requirement | Capability | Risk | Smoke | Release-blocking | Standard regression | Extended edge | Automation readiness | Primary location |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Use clear indicators such as:

```text
Yes
No
Partial
```

Do not use decorative emoji.

Map every requirement ID to its current coverage.

Examples:

- Player import should appear in Smoke, Release-blocking, and Standard regression.
- Username collision may appear only in Extended edge.
- Command Center basic integrity may be Release-blocking, while detailed metric verification may be Standard regression.
- Mobile layout may be Standard regression and Manual.
- Duplicate prevention should be Release-blocking and suitable for automation.
- Multi-tab stale-update behavior may be Extended edge and Manual or Semi-automatable.

Ensure the matrix accurately reflects existing QA documents.

Do not claim coverage that does not exist.

---

# 4. Add Requirement IDs to Existing QA Documents

Update:

```text
platform_e2e_test_script.md
production_smoke_test.md
```

Add requirement IDs at the section level, not beside every checkbox.

Preferred style:

```markdown
## Player Import

Requirements: `IMP-001`, `IMP-003`, `ACC-001`, `ASN-001`
```

or:

```markdown
Requirements covered: `EVL-001`, `EVL-004`, `REV-003`
```

Add IDs to all major sections.

Keep the text readable.

Do not overload headings with long ID lists.

Where a section covers many requirements, place the IDs immediately below the heading.

Update the test-classification section so release-blocking items refer to both the feature name and ID where helpful.

Example:

```text
- [ ] Player import (`IMP-001`)
- [ ] Duplicate evaluation prevention (`EVL-005`)
- [ ] Direct URL permissions (`SEC-001` to `SEC-004`)
```

---

# 5. Add Risk Priority to the Full Test Script

In `platform_e2e_test_script.md`, add:

```markdown
## Risk Priority
```

near the existing test classification section.

Briefly explain:

- Critical and High tests should be prioritized when release time is limited.
- Medium and Low tests should not be permanently skipped; they may be deferred based on release scope.
- Release-blocking classification and risk classification are related but not identical.

Add a compact table mapping the major test areas to risk.

Example:

| Area | Requirement IDs | Risk |
| --- | --- | --- |
| Imports | `IMP-001` to `IMP-004` | Critical |
| Account provisioning and passwords | `ACC-001` to `ACC-006` | Critical |
| Core evaluation workflows | `EVL-001` to `EVL-006` | Critical |
| Permissions | `SEC-001` to `SEC-004` | Critical |
| Review and attribution | `REV-001` to `REV-003` | High |
| Command Center and reporting | `ANA-001` to `ANA-005` | High |
| Navigation and mobile | `NAV-001`, `NAV-002` | Medium |
| Multi-tab stale edits | `NAV-004` | Low or Medium based on actual product risk |
| QA retention and cleanup | `OPS-002`, `OPS-003` | Medium |

Adjust risks based on the current platform.

---

# 6. Add Automation-Readiness Tags

In `platform_e2e_test_script.md`, tag each major section with one of:

```text
Automation readiness: Manual
Automation readiness: Semi-automatable
Automation readiness: Fully automatable
```

Use the most realistic classification.

Examples:

- CSV parse validation: Fully automatable.
- Duplicate evaluation uniqueness: Fully automatable.
- Direct URL permission checks: Fully automatable.
- Import preview appearance and message clarity: Semi-automatable.
- Mobile visual usability: Manual or Semi-automatable.
- Multi-tab stale-edit behavior: Semi-automatable.
- Cleanup and retention review: Manual.
- Dashboard numerical deltas: Fully automatable if fixtures are controlled.
- Overall production smoke test: Semi-automatable.

Do not claim that browser workflows are already automated.

This is a readiness assessment only.

---

# 7. Add QA Package Version History

Create:

`docs/qa/platform_e2e/CHANGELOG.md`

Use a simple documentation changelog.

Do not attempt to create semantic versions based on guesses.

Use date-based or milestone-based entries.

Suggested structure:

```markdown
# Platform E2E QA Package History

## Current

### Added

- feature traceability
- stable requirement IDs
- risk classification
- automation-readiness classification
- release-pipeline guidance

## Previous milestones

### Initial E2E package

- happy-path imports
- manual records
- evaluations
- permissions
- cleanup

### Expanded regression coverage

- collisions
- inactive accounts
- cycle isolation
- duplicate submission
- browser state
- analytics reporting
- production smoke test

### Repeatability and lifecycle

- first-deployment and repeat-deployment modes
- evaluation reuse guidance
- permanent QA environment guidance
- retention-first cleanup
```

Where commit hashes are available from the current repository history, include them.

Known commits may include:

```text
d85aea5  Add platform end-to-end QA package
fd8afb8  Expand platform end-to-end QA coverage
613b2d4  Improve long-term QA workflow and smoke-test repeatability
```

Verify the hashes from Git before documenting them.

Do not include prompt-archive commits unless useful to the QA package history.

---

# 8. Add Release Pipeline Guidance

Create:

`docs/qa/platform_e2e/release_pipeline.md`

Keep it concise and operational.

Suggested flow:

```text
Developer changes
-> code review
-> Django checks
-> focused automated tests
-> full relevant automated test suite
-> deployment preparation
-> database backup
-> deployment
-> production smoke test
-> release-blocking E2E tests when required
-> standard regression based on change scope
-> extended edge cases for high-risk changes
-> sign-off
```

Include sections:

## Before merge

- Django checks
- migrations check
- focused tests
- relevant regression tests
- documentation update if workflows changed

## Before deployment

- confirm commit
- confirm backup
- confirm rollback plan
- determine smoke-test mode and evaluation cycle
- select risk-based test scope

## After deployment

- run production smoke test
- record observation IDs and results
- run release-blocking tests for affected Critical requirements
- run Standard regression for affected High requirements
- record defects and release decision

## Release decision

Use:

```text
Pass
Conditional pass
Fail
```

Define briefly:

- Pass: all required tests pass.
- Conditional pass: no Critical failure; known non-critical issue is documented and accepted.
- Fail: Critical or release-blocking behavior fails.

Do not add organizational approval roles that are not established in the project.

---

# 9. Add Change-Impact Guidance

In `release_pipeline.md` or `README.md`, add a compact mapping from change area to QA scope.

Example:

| Code area changed | Minimum QA scope |
| --- | --- |
| Player import or provisioning | `IMP-*`, `ACC-001`, `ACC-003`, `ACC-004`, `ASN-001` |
| Coach import | `IMP-002`, `IMP-003`, `ACC-002` to `ACC-005`, `ASN-002` |
| Evaluations | `EVL-*`, `REV-*`, relevant `ANA-*` |
| Permissions | `SEC-*` plus affected workflows |
| Analytics services | `ANA-*`, player timeline, comparison, Command Center |
| Account login/password | `ACC-005`, `ACC-006`, `SEC-004` |
| Templates/navigation | `NAV-*` and relevant smoke tests |
| Season models | `ASN-*`, `EVL-006`, `ANA-005`, `OPS-*` |

This table should help a developer select tests without running every manual case after a small change.

---

# 10. Update README.md

Add the new files:

```text
feature_traceability.md
CHANGELOG.md
release_pipeline.md
```

Add a brief section explaining:

- requirement IDs are stable references
- traceability shows where each feature is tested
- risk helps prioritize when release time is limited
- automation readiness guides future test investment
- release pipeline connects development and production QA

Keep the README concise.

Do not duplicate the full contents of the new documents.

---

# 11. Future Maintenance Convention

Add a short section to `README.md`:

```markdown
## Maintaining Traceability
```

State that when a feature is added or materially changed:

1. Create or reuse a stable requirement ID.
2. Update the traceability matrix.
3. Add or update the appropriate smoke, release-blocking, regression, or edge test.
4. Update risk only if the impact changed.
5. Update automation readiness when automated coverage is added.
6. Add a changelog entry.
7. Update release-pipeline impact mapping if a new capability area is introduced.

Do not renumber existing IDs merely to improve ordering.

Deprecated requirements should remain listed and be marked deprecated rather than silently removed.

---

# 12. Internal Consistency Review

Before finishing, verify:

- every requirement ID used in a QA document exists in `feature_traceability.md`;
- every requirement in the traceability matrix has at least one test location;
- no requirement claims smoke coverage unless it appears in `production_smoke_test.md`;
- release-blocking coverage matches `platform_e2e_test_script.md`;
- risk labels are consistent across documents;
- automation-readiness labels are consistent;
- IDs are not duplicated;
- IDs are not assigned to unrelated behaviors;
- existing route names and workflows remain unchanged;
- no unsupported application claims were added.

---

# 13. Validation

Run:

```bash
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations --check
git diff --check
```

Also run a lightweight documentation validation script.

At minimum, verify:

- requirement-ID format matches `[A-Z]{3}-[0-9]{3}`;
- no duplicate IDs exist in the traceability matrix;
- all IDs referenced in Markdown files exist in the traceability matrix;
- all new Markdown files are linked from README.md;
- no existing CSV fixtures changed unexpectedly.

A small standalone Python validation script may be added under:

```text
docs/qa/platform_e2e/
```

only if it is simple, reusable, and clearly documented.

Otherwise, run the validation as an inline Python command without committing a script.

Do not change application code.

Do not run production imports.

Do not create or modify production database data.

---

# 14. Completion Report

At completion, report:

1. Files modified.
2. Files added.
3. Requirement-ID convention created.
4. Number of requirements added to the traceability matrix.
5. Risk levels assigned.
6. Automation-readiness classifications assigned.
7. QA history entries added.
8. Release-pipeline guidance added.
9. Change-impact mapping added.
10. Documentation consistency checks and results.
11. Django validation results.
12. Any unresolved classification or policy decisions.

Commit with a clear message, for example:

```text
Add QA traceability and release guidance
```

Do not push unless explicitly instructed.

## Implementation Commit Diff

Commit: e8be795 Add QA traceability and release guidance

```diff
commit e8be795dde671ced4b78159e733c96c9360f7e6a
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 23 15:00:27 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 23 15:00:27 2026 -0700

    Add QA traceability and release guidance
---
 docs/qa/platform_e2e/CHANGELOG.md                |  64 +++++++++++
 docs/qa/platform_e2e/README.md                   |  27 +++++
 docs/qa/platform_e2e/feature_traceability.md     |  94 +++++++++++++++
 docs/qa/platform_e2e/platform_e2e_test_script.md | 139 +++++++++++++++++++++--
 docs/qa/platform_e2e/production_smoke_test.md    |  16 +++
 docs/qa/platform_e2e/release_pipeline.md         |  74 ++++++++++++
 6 files changed, 402 insertions(+), 12 deletions(-)

diff --git a/docs/qa/platform_e2e/CHANGELOG.md b/docs/qa/platform_e2e/CHANGELOG.md
new file mode 100644
index 0000000..81cff6c
--- /dev/null
+++ b/docs/qa/platform_e2e/CHANGELOG.md
@@ -0,0 +1,64 @@
+# Platform E2E QA Package History
+
+## Current
+
+### Added
+
+- Feature traceability matrix.
+- Stable requirement IDs.
+- Risk classification.
+- Automation-readiness classification.
+- Release-pipeline guidance.
+- Change-impact guidance for selecting QA scope.
+- Lightweight maintenance conventions for future traceability changes.
+
+## Previous Milestones
+
+### Repeatability and lifecycle
+
+Commit:
+
+```text
+613b2d4 Improve long-term QA workflow and smoke-test repeatability
+```
+
+Added:
+
+- first-deployment and repeat-deployment smoke-test modes;
+- evaluation reuse guidance;
+- permanent QA environment guidance;
+- retention-first cleanup.
+
+### Expanded regression coverage
+
+Commit:
+
+```text
+fd8afb8 Expand platform end-to-end QA coverage
+```
+
+Added:
+
+- collision scenarios;
+- inactive-account lifecycle coverage;
+- evaluation-cycle isolation;
+- duplicate-submission coverage;
+- browser state checks;
+- analytics reporting verification;
+- production smoke test.
+
+### Initial E2E package
+
+Commit:
+
+```text
+d85aea5 Add platform end-to-end QA package
+```
+
+Added:
+
+- happy-path imports;
+- manual test records;
+- evaluation workflows;
+- permission checks;
+- cleanup checklist.
diff --git a/docs/qa/platform_e2e/README.md b/docs/qa/platform_e2e/README.md
index a5ad520..6161951 100644
--- a/docs/qa/platform_e2e/README.md
+++ b/docs/qa/platform_e2e/README.md
@@ -24,6 +24,33 @@ Recommended QA teams:
 - `production_smoke_test.md`: concise post-deployment smoke-test checklist.
 - `manual_test_records.md`: records intentionally left for manual creation.
 - `cleanup_checklist.md`: safe cleanup checklist after testing.
+- `feature_traceability.md`: stable requirement IDs, risk levels, coverage, and automation-readiness matrix.
+- `release_pipeline.md`: release QA sequence and change-impact guidance.
+- `CHANGELOG.md`: QA package history.
+
+## Traceability And Release Planning
+
+Use `feature_traceability.md` when a release, defect, or code review needs a stable reference to tested behavior.
+
+- Requirement IDs are stable references for platform capabilities.
+- The traceability matrix shows where each capability is tested.
+- Risk levels help prioritize when release time is limited.
+- Automation readiness identifies where future unit, integration, or browser automation can replace manual checks.
+- `release_pipeline.md` connects development changes to production QA scope.
+
+## Maintaining Traceability
+
+When a feature is added or materially changed:
+
+1. Create or reuse a stable requirement ID.
+2. Update the traceability matrix.
+3. Add or update the appropriate smoke, release-blocking, regression, or edge test.
+4. Update risk only if the impact changed.
+5. Update automation readiness when automated coverage is added.
+6. Add a changelog entry.
+7. Update release-pipeline impact mapping if a new capability area is introduced.
+
+Do not renumber existing IDs merely to improve ordering. Deprecated requirements should remain listed and be marked deprecated rather than silently removed.

 ## Current UI Paths

diff --git a/docs/qa/platform_e2e/feature_traceability.md b/docs/qa/platform_e2e/feature_traceability.md
new file mode 100644
index 0000000..8e3f782
--- /dev/null
+++ b/docs/qa/platform_e2e/feature_traceability.md
@@ -0,0 +1,94 @@
+# Platform E2E Feature Traceability
+
+## Purpose
+
+This file maps tested VCB Platform capabilities to stable requirement IDs, risk level, current QA coverage, automation readiness, and the primary QA document section.
+
+Requirement IDs are stable references for release notes, defects, commits, and future automation. Do not renumber existing IDs merely to improve ordering.
+
+## Requirement ID Convention
+
+Use three-letter capability prefixes and three-digit numbers:
+
+```text
+IMP-001
+ACC-001
+EVL-001
+```
+
+Current prefixes:
+
+| Prefix | Area |
+| --- | --- |
+| `IMP` | Imports |
+| `ACC` | Accounts and provisioning |
+| `ASN` | Assignments and memberships |
+| `EVL` | Evaluations |
+| `REV` | Review workflow |
+| `SEC` | Security and permissions |
+| `ANA` | Analytics and reporting |
+| `NAV` | Navigation and usability |
+| `OPS` | QA operations and lifecycle |
+
+## Risk Levels
+
+| Risk | Meaning |
+| --- | --- |
+| Critical | Failure could expose data, break access control, corrupt imports, prevent login, or invalidate core evaluations. |
+| High | Failure materially breaks a major workflow or reporting result. |
+| Medium | Failure reduces usability or affects a secondary workflow. |
+| Low | Failure is an uncommon edge case or limited operational inconvenience. |
+
+## Automation Readiness
+
+| Readiness | Meaning |
+| --- | --- |
+| Manual | Requires human judgment, visual review, or environment decisions. |
+| Semi-automatable | Setup or verification can be automated, but some human review remains. |
+| Fully automatable | Deterministic behavior suitable for unit, integration, or browser automation. |
+
+## Matrix
+
+| Requirement | Capability | Risk | Smoke | Release-blocking | Standard regression | Extended edge | Automation readiness | Primary location |
+| --- | --- | --- | --- | --- | --- | --- | --- | --- |
+| `IMP-001` | Player CSV import | Critical | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Player Import |
+| `IMP-002` | Coach CSV import | Critical | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Coach Import |
+| `IMP-003` | Import idempotency | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Player Import / Coach Import |
+| `IMP-004` | Import preview and conflict reporting | High | Partial | Yes | Yes | Yes | Semi-automatable | `platform_e2e_test_script.md` - Player Import / Coach Import / Extended Edge Cases |
+| `ACC-001` | Player account provisioning | Critical | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Player Import |
+| `ACC-002` | Coach account provisioning | Critical | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Coach Import |
+| `ACC-003` | Username generation and collision handling | High | Partial | Yes | Partial | Yes | Fully automatable | `platform_e2e_test_script.md` - Username Collision Tests |
+| `ACC-004` | Email normalization, reuse, and conflict handling | High | Partial | Yes | Partial | Yes | Fully automatable | `platform_e2e_test_script.md` - Email Reuse and Conflict Tests |
+| `ACC-005` | Account activation lifecycle | Critical | Partial | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Account Activation And Password Workflow |
+| `ACC-006` | Temporary password and forced password change | Critical | Yes | Yes | Yes | Yes | Semi-automatable | `platform_e2e_test_script.md` - Account Activation And Password Workflow |
+| `ACC-007` | Manual account creation | High | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Manual Creation |
+| `ASN-001` | Player roster membership | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Player Import / Manual Creation |
+| `ASN-002` | Coach season assignment | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Coach Import / Manual Creation |
+| `ASN-003` | Historical assignment preservation | High | No | No | Yes | Yes | Semi-automatable | `platform_e2e_test_script.md` - Archive and Deactivation Behavior Tests |
+| `EVL-001` | Coach evaluation | Critical | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Coach Evaluation Workflow |
+| `EVL-002` | Player self-evaluation | Critical | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Player Self-Evaluations |
+| `EVL-003` | Player peer evaluation | Critical | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Player Peer Evaluations |
+| `EVL-004` | Draft save and reopen | Critical | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Coach Evaluation Workflow / Review Workflow |
+| `EVL-005` | Evaluation uniqueness and duplicate prevention | Critical | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Duplicate Evaluation and Repeat Submission Tests |
+| `EVL-006` | Evaluation-cycle isolation | Critical | No | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Evaluation Cycle Isolation Tests |
+| `EVL-007` | Imported/manual workflow consistency | High | Partial | No | Yes | No | Semi-automatable | `platform_e2e_test_script.md` - Cross-Workflow Consistency Tests |
+| `REV-001` | Evaluation review | High | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Review Workflow |
+| `REV-002` | Reopen and resubmit | High | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Review Workflow |
+| `REV-003` | Evaluation metadata and attribution | High | Partial | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Review Workflow |
+| `SEC-001` | Staff-only import permissions | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Permission Testing |
+| `SEC-002` | Account and season administration permissions | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Permission Testing |
+| `SEC-003` | Evaluation privacy and ownership | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Permission Testing / Player Peer Evaluations |
+| `SEC-004` | Anonymous-user redirects | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Permission Testing |
+| `ANA-001` | Command Center integrity | High | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Expanded Analytics Command Center and Reporting Verification |
+| `ANA-002` | Command Center metrics | High | Yes | Partial | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Expanded Analytics Command Center and Reporting Verification |
+| `ANA-003` | Player timeline | High | Yes | Partial | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Analytics And Timeline |
+| `ANA-004` | Player comparison | High | Yes | Partial | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Analytics And Timeline |
+| `ANA-005` | Review and reporting filters | High | Partial | Partial | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Review Workflow / Analytics And Timeline |
+| `NAV-001` | Core navigation | Medium | Yes | Partial | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Administrator Navigation And Permissions |
+| `NAV-002` | Mobile usability | Medium | No | No | Yes | No | Manual | `platform_e2e_test_script.md` - Mobile Testing |
+| `NAV-003` | Browser refresh and back-button behavior | Medium | No | Partial | Yes | Yes | Semi-automatable | `platform_e2e_test_script.md` - Browser State and Navigation Tests |
+| `NAV-004` | Multi-tab stale-update behavior | Medium | No | No | No | Yes | Semi-automatable | `platform_e2e_test_script.md` - Browser State and Navigation Tests |
+| `OPS-001` | Production smoke-test repeatability | High | Yes | No | No | No | Semi-automatable | `production_smoke_test.md` - Smoke Test Mode |
+| `OPS-002` | QA environment retention | Medium | Partial | No | Yes | Partial | Manual | `README.md` - Recommended Long-Term QA Strategy |
+| `OPS-003` | Cleanup and archival | Medium | Yes | No | Yes | Partial | Manual | `cleanup_checklist.md` |
+| `OPS-004` | Negative-test fixture isolation | Medium | No | No | No | Yes | Manual | `negative_test_fixtures.md` |
diff --git a/docs/qa/platform_e2e/platform_e2e_test_script.md b/docs/qa/platform_e2e/platform_e2e_test_script.md
index 468896e..42ea06d 100644
--- a/docs/qa/platform_e2e/platform_e2e_test_script.md
+++ b/docs/qa/platform_e2e/platform_e2e_test_script.md
@@ -19,18 +19,18 @@ Production smoke test

 These tests must pass before a production release is accepted:

-- [ ] player import
-- [ ] player account provisioning
-- [ ] coach import
-- [ ] manual account creation
-- [ ] coach evaluation submission
-- [ ] player self-evaluation submission
-- [ ] player peer-evaluation submission
-- [ ] evaluation review
-- [ ] direct URL permissions
-- [ ] forced password change
-- [ ] no duplicate submissions after refresh or repeat submit
-- [ ] basic Analytics Command Center integrity
+- [ ] player import (`IMP-001`, `IMP-003`)
+- [ ] player account provisioning (`ACC-001`)
+- [ ] coach import (`IMP-002`, `IMP-003`)
+- [ ] manual account creation (`ACC-007`)
+- [ ] coach evaluation submission (`EVL-001`)
+- [ ] player self-evaluation submission (`EVL-002`)
+- [ ] player peer-evaluation submission (`EVL-003`)
+- [ ] evaluation review (`REV-001`, `REV-003`)
+- [ ] direct URL permissions (`SEC-001` to `SEC-004`)
+- [ ] forced password change (`ACC-006`)
+- [ ] no duplicate submissions after refresh or repeat submit (`EVL-005`)
+- [ ] basic Analytics Command Center integrity (`ANA-001`)

 ### Standard Regression

@@ -56,6 +56,29 @@ These tests are useful before major pilots, after import/account changes, or whe
 - [ ] case and whitespace normalization
 - [ ] conflicting cross-role emails

+## Risk Priority
+
+Critical and High tests should be prioritized when release time is limited. Medium and Low tests should not be permanently skipped; they may be deferred based on release scope. Release-blocking classification and risk classification are related but not identical.
+
+| Area | Requirement IDs | Risk |
+| --- | --- | --- |
+| Import data creation and idempotency | `IMP-001` to `IMP-003` | Critical |
+| Import preview and conflict reporting | `IMP-004` | High |
+| Account provisioning, activation, and passwords | `ACC-001`, `ACC-002`, `ACC-005`, `ACC-006` | Critical |
+| Username and email handling | `ACC-003`, `ACC-004` | High |
+| Manual account creation | `ACC-007` | High |
+| Active assignments and memberships | `ASN-001`, `ASN-002` | Critical |
+| Historical assignment preservation | `ASN-003` | High |
+| Core evaluation workflows | `EVL-001` to `EVL-006` | Critical |
+| Imported/manual workflow consistency | `EVL-007` | High |
+| Review and attribution | `REV-001` to `REV-003` | High |
+| Permissions | `SEC-001` to `SEC-004` | Critical |
+| Command Center and reporting | `ANA-001` to `ANA-005` | High |
+| Navigation and mobile | `NAV-001`, `NAV-002` | Medium |
+| Browser refresh and back-button behavior | `NAV-003` | Medium |
+| Multi-tab stale edits | `NAV-004` | Medium |
+| QA retention and cleanup | `OPS-002`, `OPS-003` | Medium |
+
 ## QA Fixture Summary

 QA season:
@@ -123,6 +146,10 @@ Coach import:

 ## A. Initial Setup

+Requirements covered: `OPS-001`, `OPS-002`, `NAV-001`
+
+Automation readiness: Manual
+
 Tester:

 ```text
@@ -160,6 +187,10 @@ Notes:

 ## B. Player Import

+Requirements covered: `IMP-001`, `IMP-003`, `IMP-004`, `ACC-001`, `ACC-003`, `ACC-004`, `ACC-005`, `ACC-006`, `ASN-001`
+
+Automation readiness: Semi-automatable
+
 Path:

 ```text
@@ -217,6 +248,10 @@ Notes:

 ## C. Coach Import

+Requirements covered: `IMP-002`, `IMP-003`, `IMP-004`, `ACC-002`, `ACC-003`, `ACC-004`, `ACC-005`, `ACC-006`, `ASN-002`
+
+Automation readiness: Semi-automatable
+
 Path:

 ```text
@@ -269,6 +304,10 @@ Notes:

 ## D. Manual Creation

+Requirements covered: `ACC-007`, `ACC-005`, `ACC-006`, `ASN-001`, `ASN-002`
+
+Automation readiness: Semi-automatable
+
 Use `manual_test_records.md`.

 Steps:
@@ -296,6 +335,10 @@ Notes:

 ## E. Administrator Navigation And Permissions

+Requirements covered: `NAV-001`, `SEC-001`, `SEC-002`
+
+Automation readiness: Semi-automatable
+
 As a staff or superuser account, verify visible navigation:

 - [ ] Operations Home opens `/analytics/`.
@@ -324,6 +367,10 @@ Notes:

 ## F. Coach Evaluation Workflow

+Requirements covered: `EVL-001`, `EVL-004`, `REV-003`, `SEC-003`
+
+Automation readiness: Semi-automatable
+
 Test all three coaches.

 Minimum submissions:
@@ -369,6 +416,10 @@ Notes:

 ## G. Player Self-Evaluations

+Requirements covered: `EVL-002`, `EVL-004`, `SEC-003`
+
+Automation readiness: Semi-automatable
+
 Minimum submissions:

 - Player QA One self-evaluates.
@@ -405,6 +456,10 @@ Notes:

 ## H. Player Peer Evaluations

+Requirements covered: `EVL-003`, `EVL-004`, `SEC-003`, `REV-003`
+
+Automation readiness: Semi-automatable
+
 Minimum submissions:

 - Player QA One evaluates Player QA Two.
@@ -439,6 +494,10 @@ Notes:

 ## I. Review Workflow

+Requirements covered: `REV-001`, `REV-002`, `REV-003`, `ANA-005`, `EVL-005`
+
+Automation readiness: Semi-automatable
+
 As an administrator, staff user, or coach reviewer:

 - [ ] Open `/analytics/evaluation-review/`.
@@ -487,6 +546,10 @@ Notes:

 ## J. Permission Testing

+Requirements covered: `SEC-001`, `SEC-002`, `SEC-003`, `SEC-004`
+
+Automation readiness: Fully automatable
+
 Direct URL access must be tested. Navigation hiding is not enough.

 As a coach, directly attempt:
@@ -520,6 +583,10 @@ Notes:

 ## K. Account Activation And Password Workflow

+Requirements covered: `ACC-005`, `ACC-006`, `SEC-004`
+
+Automation readiness: Semi-automatable
+
 Test:

 - one imported coach
@@ -554,6 +621,10 @@ Notes:

 ## L. Analytics And Timeline

+Requirements covered: `ANA-001`, `ANA-002`, `ANA-003`, `ANA-004`, `ANA-005`
+
+Automation readiness: Semi-automatable
+
 As staff:

 - [ ] Open `/analytics/players/`.
@@ -576,6 +647,10 @@ Notes:

 ## M. Mobile Testing

+Requirements covered: `NAV-002`
+
+Automation readiness: Manual
+
 At approximately 390-pixel width, test:

 - [ ] login
@@ -599,6 +674,10 @@ Notes:

 ## N. Cleanup

+Requirements covered: `OPS-003`
+
+Automation readiness: Manual
+
 Use `cleanup_checklist.md`.

 - [ ] Record defects and screenshots.
@@ -620,6 +699,10 @@ Notes:

 Level: Standard regression.

+Requirements covered: `EVL-007`, `REV-003`
+
+Automation readiness: Semi-automatable
+
 Use these tests to verify that imported and manually created accounts behave the same in evaluation workflows.

 | Combination | Example | Tested | Result |
@@ -662,6 +745,10 @@ Notes:

 Level: Extended edge cases.

+Requirements covered: `ACC-003`, `IMP-004`
+
+Automation readiness: Fully automatable
+
 Actual behavior discovered from code:

 - Generated usernames use `firstname.lastname`.
@@ -713,6 +800,10 @@ Notes:

 Level: Extended edge cases.

+Requirements covered: `ACC-004`, `IMP-004`
+
+Automation readiness: Fully automatable
+
 Actual behavior discovered from code:

 - Emails are normalized by trimming whitespace and comparing case-insensitively.
@@ -767,6 +858,10 @@ Notes:

 Level: Standard regression.

+Requirements covered: `ACC-005`, `ACC-006`, `ASN-003`
+
+Automation readiness: Fully automatable
+
 Use optional fixture:

 ```text
@@ -809,6 +904,10 @@ Notes:

 Level: Standard regression.

+Requirements covered: `EVL-006`, `ANA-005`
+
+Automation readiness: Fully automatable
+
 Use two QA evaluation cycles where supported:

 - `TEST - Cycle A`
@@ -854,6 +953,10 @@ Notes:

 Level: Release-blocking for basic duplicate protection; extended for multi-tab concurrency.

+Requirements covered: `EVL-005`, `REV-002`, `NAV-003`, `NAV-004`
+
+Automation readiness: Semi-automatable
+
 Actual behavior discovered from code:

 - Starting the same evaluator/player/perspective/cycle evaluation reuses the existing draft or redirects to the submitted detail.
@@ -896,6 +999,10 @@ Notes:

 Level: Extended edge cases.

+Requirements covered: `NAV-003`, `NAV-004`, `EVL-005`
+
+Automation readiness: Semi-automatable
+
 Run for coach, self, and peer evaluations.

 ### Refresh
@@ -945,6 +1052,10 @@ Notes:

 Level: Standard regression.

+Requirements covered: `ACC-005`, `ASN-003`, `OPS-002`, `OPS-003`
+
+Automation readiness: Manual
+
 Do not delete records during the normal test run.

 ### Season
@@ -1001,6 +1112,10 @@ Notes:

 Level: Release-blocking for basic dashboard integrity; standard regression for detailed counts.

+Requirements covered: `ANA-001`, `ANA-002`, `ANA-003`, `ANA-004`, `ANA-005`, `EVL-005`
+
+Automation readiness: Semi-automatable
+
 Current implemented outputs include:

 - summary cards
diff --git a/docs/qa/platform_e2e/production_smoke_test.md b/docs/qa/platform_e2e/production_smoke_test.md
index 6446183..3683910 100644
--- a/docs/qa/platform_e2e/production_smoke_test.md
+++ b/docs/qa/platform_e2e/production_smoke_test.md
@@ -6,6 +6,8 @@ Do not use optional negative fixtures during the smoke test.

 ## Smoke Test Mode

+Requirements covered: `OPS-001`
+
 Choose one mode before starting.

 ### Mode A: First Deployment
@@ -43,6 +45,8 @@ Non-critical defects:

 ## Setup

+Requirements covered: `OPS-001`, `OPS-002`
+
 - [ ] Confirm the deployed commit.
 - [ ] Confirm a recent database backup exists.
 - [ ] Confirm QA season `TEST - Platform QA 2026` is active for testing.
@@ -52,6 +56,8 @@ Non-critical defects:

 ## Admin Workflow

+Requirements covered: `IMP-001`, `IMP-002`, `IMP-003`, `IMP-004`, `ACC-001`, `ACC-002`, `ACC-003`, `ACC-004`, `ACC-005`, `ACC-006`, `ACC-007`, `ASN-001`, `ASN-002`, `NAV-001`
+
 - [ ] Sign in as an administrator or Django staff user.
 - [ ] Open Operations Home `/analytics/`.
 - [ ] Confirm Imports, User Accounts, Seasons, Evaluations, and Review links work.
@@ -78,6 +84,8 @@ Repeat deployment:

 ## Coach Workflow

+Requirements covered: `EVL-001`, `EVL-004`, `EVL-005`, `EVL-007`, `REV-002`, `REV-003`
+
 - [ ] Sign in as imported coach `coach.qa.one`.
 - [ ] Sign in as manual coach `coach.qa.manual`.

@@ -98,6 +106,8 @@ Repeat deployment:

 ## Player Workflow

+Requirements covered: `EVL-002`, `EVL-003`, `EVL-004`, `EVL-005`, `EVL-007`, `SEC-003`, `REV-003`
+
 - [ ] Sign in as imported player `player.qa.one`.
 - [ ] Sign in as manual player `player.qa.manual.one`.

@@ -122,6 +132,8 @@ Repeat deployment:

 ## Review Workflow

+Requirements covered: `REV-001`, `REV-002`, `REV-003`, `EVL-005`, `ANA-001`, `ANA-002`, `ANA-003`, `ANA-004`, `ANA-005`
+
 - [ ] Sign back in as administrator or Django staff.
 - [ ] Confirm all smoke-test evaluations appear in `/analytics/evaluation-review/`.
 - [ ] Record the observation IDs for each smoke-test evaluation.
@@ -135,6 +147,8 @@ Repeat deployment:

 ## Security Workflow

+Requirements covered: `SEC-001`, `SEC-002`, `SEC-003`, `SEC-004`
+
 - [ ] Coach receives 403 from `/analytics/imports/`.
 - [ ] Coach receives 403 from `/accounts/`.
 - [ ] Player receives 403 from `/analytics/evaluation-review/`.
@@ -143,6 +157,8 @@ Repeat deployment:

 ## Cleanup

+Requirements covered: `OPS-003`
+
 - [ ] Deactivate QA accounts not needed for continued testing.
 - [ ] Archive or deactivate the QA season when appropriate.
 - [ ] Remove temporary passwords from notes.
diff --git a/docs/qa/platform_e2e/release_pipeline.md b/docs/qa/platform_e2e/release_pipeline.md
new file mode 100644
index 0000000..99d6512
--- /dev/null
+++ b/docs/qa/platform_e2e/release_pipeline.md
@@ -0,0 +1,74 @@
+# Platform E2E Release Pipeline Guidance
+
+Use this guide to choose practical QA coverage for a release without running every manual case after every small change.
+
+## Release Flow
+
+```text
+Developer changes
+-> code review
+-> Django checks
+-> focused automated tests
+-> full relevant automated test suite
+-> deployment preparation
+-> database backup
+-> deployment
+-> production smoke test
+-> release-blocking E2E tests when required
+-> standard regression based on change scope
+-> extended edge cases for high-risk changes
+-> sign-off
+```
+
+## Before Merge
+
+- Run Django checks.
+- Run migration checks.
+- Run focused tests for the changed subsystem.
+- Run relevant regression tests for affected requirement IDs.
+- Update documentation if user-visible workflows changed.
+- Update `feature_traceability.md` if a tested requirement was added, changed, deprecated, or reclassified.
+
+## Before Deployment
+
+- Confirm the exact commit being deployed.
+- Confirm a recent database backup exists.
+- Confirm the rollback plan.
+- Determine smoke-test mode:
+  - first deployment;
+  - repeat deployment.
+- Determine the evaluation cycle to use.
+- Select risk-based test scope from `feature_traceability.md`.
+
+## After Deployment
+
+- Run `production_smoke_test.md`.
+- Record observation IDs and smoke-test results.
+- Run release-blocking tests for affected Critical requirements.
+- Run standard regression for affected High requirements.
+- Use extended edge cases for import, account, permission, evaluation uniqueness, browser-state, or reporting changes.
+- Record defects and release decision.
+
+## Release Decision
+
+| Decision | Meaning |
+| --- | --- |
+| Pass | All required tests pass. |
+| Conditional pass | No Critical failure; known non-critical issue is documented and accepted. |
+| Fail | Critical or release-blocking behavior fails. |
+
+## Change-Impact Guidance
+
+| Code area changed | Minimum QA scope |
+| --- | --- |
+| Player import or provisioning | `IMP-*`, `ACC-001`, `ACC-003`, `ACC-004`, `ASN-001` |
+| Coach import | `IMP-002`, `IMP-003`, `ACC-002` to `ACC-005`, `ASN-002` |
+| Account operations | `ACC-*`, `SEC-002`, `SEC-004`, affected `ASN-*` |
+| Account login or password workflow | `ACC-005`, `ACC-006`, `SEC-004` |
+| Evaluations | `EVL-*`, `REV-*`, relevant `ANA-*` |
+| Permissions | `SEC-*` plus affected workflows |
+| Analytics services | `ANA-*`, `EVL-005`, `REV-*` where relevant |
+| Player timeline or comparison | `ANA-003`, `ANA-004`, relevant `EVL-*` |
+| Templates or navigation | `NAV-*` and relevant smoke-test sections |
+| Season models, memberships, or coach assignments | `ASN-*`, `EVL-006`, `ANA-005`, `OPS-*` |
+| QA fixtures or cleanup guidance | `OPS-*`, affected import or account requirements |
```

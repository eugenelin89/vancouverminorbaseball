# Platform E2E Release Pipeline Guidance

Use this guide to choose practical QA coverage for a release without running every manual case after every small change.

## Release Flow

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

## Before Merge

- Run Django checks.
- Run migration checks.
- Run focused tests for the changed subsystem.
- Run relevant regression tests for affected requirement IDs.
- Update documentation if user-visible workflows changed.
- Update `feature_traceability.md` if a tested requirement was added, changed, deprecated, or reclassified.

## Before Deployment

- Confirm the exact commit being deployed.
- Confirm a recent database backup exists.
- Confirm the rollback plan.
- Determine smoke-test mode:
  - first deployment;
  - repeat deployment.
- Determine the evaluation cycle to use.
- Select risk-based test scope from `feature_traceability.md`.

## After Deployment

- Run `production_smoke_test.md`.
- Record observation IDs and smoke-test results.
- Run release-blocking tests for affected Critical requirements.
- Run standard regression for affected High requirements.
- Use extended edge cases for import, account, permission, evaluation uniqueness, browser-state, or reporting changes.
- Record defects and release decision.

## Release Decision

| Decision | Meaning |
| --- | --- |
| Pass | All required tests pass. |
| Conditional pass | No Critical failure; known non-critical issue is documented and accepted. |
| Fail | Critical or release-blocking behavior fails. |

## Change-Impact Guidance

| Code area changed | Minimum QA scope |
| --- | --- |
| Player import or provisioning | `IMP-*`, `ACC-001`, `ACC-003`, `ACC-004`, `ASN-001` |
| Coach import | `IMP-002`, `IMP-003`, `ACC-002` to `ACC-005`, `ASN-002` |
| Account operations | `ACC-*`, `SEC-002`, `SEC-004`, affected `ASN-*` |
| Account login or password workflow | `ACC-005`, `ACC-006`, `SEC-004` |
| Evaluations | `EVL-*`, `REV-*`, relevant `ANA-*` |
| Permissions | `SEC-*` plus affected workflows |
| Analytics services | `ANA-*`, `EVL-005`, `REV-*` where relevant |
| Player timeline or comparison | `ANA-003`, `ANA-004`, relevant `EVL-*` |
| Templates or navigation | `NAV-*` and relevant smoke-test sections |
| Season models, memberships, or coach assignments | `ASN-*`, `EVL-006`, `ANA-005`, `OPS-*` |
| QA fixtures or cleanup guidance | `OPS-*`, affected import or account requirements |

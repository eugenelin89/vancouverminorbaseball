# Platform E2E Feature Traceability

## Purpose

This file maps tested VCB Platform capabilities to stable requirement IDs, risk level, current QA coverage, automation readiness, and the primary QA document section.

Requirement IDs are stable references for release notes, defects, commits, and future automation. Do not renumber existing IDs merely to improve ordering.

## Requirement ID Convention

Use three-letter capability prefixes and three-digit numbers:

```text
IMP-001
ACC-001
EVL-001
```

Current prefixes:

| Prefix | Area |
| --- | --- |
| `IMP` | Imports |
| `ACC` | Accounts and provisioning |
| `ASN` | Assignments and memberships |
| `EVL` | Evaluations |
| `REV` | Review workflow |
| `SEC` | Security and permissions |
| `ANA` | Analytics and reporting |
| `NAV` | Navigation and usability |
| `OPS` | QA operations and lifecycle |

## Risk Levels

| Risk | Meaning |
| --- | --- |
| Critical | Failure could expose data, break access control, corrupt imports, prevent login, or invalidate core evaluations. |
| High | Failure materially breaks a major workflow or reporting result. |
| Medium | Failure reduces usability or affects a secondary workflow. |
| Low | Failure is an uncommon edge case or limited operational inconvenience. |

## Automation Readiness

| Readiness | Meaning |
| --- | --- |
| Manual | Requires human judgment, visual review, or environment decisions. |
| Semi-automatable | Setup or verification can be automated, but some human review remains. |
| Fully automatable | Deterministic behavior suitable for unit, integration, or browser automation. |

## Matrix

| Requirement | Capability | Risk | Smoke | Release-blocking | Standard regression | Extended edge | Automation readiness | Primary location |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `IMP-001` | Player CSV import | Critical | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Player Import |
| `IMP-002` | Coach CSV import | Critical | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Coach Import |
| `IMP-003` | Import idempotency | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Player Import / Coach Import |
| `IMP-004` | Import preview and conflict reporting | High | Partial | Yes | Yes | Yes | Semi-automatable | `platform_e2e_test_script.md` - Player Import / Coach Import / Extended Edge Cases |
| `ACC-001` | Player account provisioning | Critical | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Player Import |
| `ACC-002` | Coach account provisioning | Critical | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Coach Import |
| `ACC-003` | Username generation and collision handling | High | Partial | Yes | Partial | Yes | Fully automatable | `platform_e2e_test_script.md` - Username Collision Tests |
| `ACC-004` | Email normalization, reuse, and conflict handling | High | Partial | Yes | Partial | Yes | Fully automatable | `platform_e2e_test_script.md` - Email Reuse and Conflict Tests |
| `ACC-005` | Account activation lifecycle | Critical | Partial | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Account Activation And Password Workflow |
| `ACC-006` | Temporary password and forced password change | Critical | Yes | Yes | Yes | Yes | Semi-automatable | `platform_e2e_test_script.md` - Account Activation And Password Workflow |
| `ACC-007` | Manual account creation | High | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Manual Creation |
| `ASN-001` | Player roster membership | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Player Import / Manual Creation |
| `ASN-002` | Coach season assignment | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Coach Import / Manual Creation |
| `ASN-003` | Historical assignment preservation | High | No | No | Yes | Yes | Semi-automatable | `platform_e2e_test_script.md` - Archive and Deactivation Behavior Tests |
| `EVL-001` | Coach evaluation | Critical | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Coach Evaluation Workflow |
| `EVL-002` | Player self-evaluation | Critical | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Player Self-Evaluations |
| `EVL-003` | Player peer evaluation | Critical | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Player Peer Evaluations |
| `EVL-004` | Draft save and reopen | Critical | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Coach Evaluation Workflow / Review Workflow |
| `EVL-005` | Evaluation uniqueness and duplicate prevention | Critical | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Duplicate Evaluation and Repeat Submission Tests |
| `EVL-006` | Evaluation-cycle isolation | Critical | No | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Evaluation Cycle Isolation Tests |
| `EVL-007` | Imported/manual workflow consistency | High | Partial | No | Yes | No | Semi-automatable | `platform_e2e_test_script.md` - Cross-Workflow Consistency Tests |
| `EVL-008` | Optional evaluation questions | High | Partial | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Optional Evaluation Question Tests |
| `REV-001` | Evaluation review | High | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Review Workflow |
| `REV-002` | Reopen and resubmit | High | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Review Workflow |
| `REV-003` | Evaluation metadata and attribution | High | Partial | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Review Workflow |
| `SEC-001` | Staff-only import permissions | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Permission Testing |
| `SEC-002` | Account and season administration permissions | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Permission Testing |
| `SEC-003` | Evaluation privacy and ownership | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Permission Testing / Player Peer Evaluations |
| `SEC-004` | Anonymous-user redirects | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Permission Testing |
| `ANA-001` | Command Center integrity | High | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Expanded Analytics Command Center and Reporting Verification |
| `ANA-002` | Command Center metrics | High | Yes | Partial | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Expanded Analytics Command Center and Reporting Verification |
| `ANA-003` | Player timeline | High | Yes | Partial | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Analytics And Timeline |
| `ANA-004` | Player comparison | High | Yes | Partial | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Analytics And Timeline |
| `ANA-005` | Review and reporting filters | High | Partial | Partial | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Review Workflow / Analytics And Timeline |
| `NAV-001` | Core navigation | Medium | Yes | Partial | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Administrator Navigation And Permissions |
| `NAV-002` | Mobile usability | Medium | No | No | Yes | No | Manual | `platform_e2e_test_script.md` - Mobile Testing |
| `NAV-003` | Browser refresh and back-button behavior | Medium | No | Partial | Yes | Yes | Semi-automatable | `platform_e2e_test_script.md` - Browser State and Navigation Tests |
| `NAV-004` | Multi-tab stale-update behavior | Medium | No | No | No | Yes | Semi-automatable | `platform_e2e_test_script.md` - Browser State and Navigation Tests |
| `OPS-001` | Production smoke-test repeatability | High | Yes | No | No | No | Semi-automatable | `production_smoke_test.md` - Smoke Test Mode |
| `OPS-002` | QA environment retention | Medium | Partial | No | Yes | Partial | Manual | `README.md` - Recommended Long-Term QA Strategy |
| `OPS-003` | Cleanup and archival | Medium | Yes | No | Yes | Partial | Manual | `cleanup_checklist.md` |
| `OPS-004` | Negative-test fixture isolation | Medium | No | No | No | Yes | Manual | `negative_test_fixtures.md` |

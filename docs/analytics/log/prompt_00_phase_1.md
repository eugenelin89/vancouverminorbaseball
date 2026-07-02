The Analytics Architecture Handbook, Implementation Handbook, Repository Assessment, and Phase 1 Engineering Plan are now complete.

This task begins implementation of Phase 1.

Read the following documents first:

Architecture
- docs/analytics/architecture/README.md

Implementation
- docs/analytics/implementation/README.md
- docs/analytics/implementation/STATUS.md
- docs/analytics/implementation/phase_01_players_foundation.md

Engineering
- docs/analytics/implementation/engineering/phase_01_players_foundation.md

Repository Assessment
- docs/analytics/implementation/repository_assessment.md

Treat these documents as the authoritative specification.

---

# Objective

Implement **Phase 1 – Players Foundation** exactly as described.

The goal is to create the new `players` app and establish the canonical player identity model that future Analytics modules will build upon.

---

# Important Architectural Rules

These rules are mandatory.

- `players.Player` is the canonical future player identity model.
- `pdp.PlayerProfile` is legacy/transitionary.
- Do NOT make `players.Player` depend on `pdp.PlayerProfile`.
- Do NOT migrate PDP workflows.
- Do NOT create bridge models unless absolutely necessary.
- Do NOT implement Analytics observations.
- Do NOT implement CSV upload UI.
- Do NOT implement Analytics pages.
- Do NOT implement future roadmap phases.

If implementation appears to require violating the Architecture Handbook or Engineering Plan:

STOP.

Explain the issue.

Do not silently redesign the architecture.

---

# Implementation Requirements

Implement only the deliverables described in the Engineering Plan.

This includes:

- players app
- models
- migrations
- admin
- services
- tests

Follow the repository conventions identified in the Repository Assessment.

Use existing project patterns wherever possible.

Keep views, templates, URLs, CSS, and frontend work out of Phase 1.

---

# Code Quality Expectations

Write production-quality Django code.

Prefer readability over cleverness.

Use:

- explicit typing where appropriate
- clear docstrings for public service functions
- transaction.atomic where appropriate
- model validation where appropriate
- sensible indexes and constraints
- descriptive error messages

Avoid premature abstraction.

Avoid unnecessary generic base classes.

---

# Testing

Create all tests described in the Engineering Plan.

Run:

python manage.py makemigrations players

python manage.py migrate

python manage.py test players

python manage.py test

Resolve any failures before considering Phase 1 complete.

---

# Documentation Updates

When implementation is complete:

Update:

docs/analytics/implementation/STATUS.md

Update:

docs/analytics/implementation/phase_01_players_foundation.md

- mark completed checklist items
- update Definition of Done
- complete Phase Review
- add lessons learned
- note technical debt (if any)

Update:

docs/analytics/implementation/engineering/phase_01_players_foundation.md

Add sections if they do not already exist:

## Implementation Decisions

Record important engineering decisions made during implementation that do not require architecture changes.

Examples:

- why a particular index was chosen
- why a constraint was added
- normalization decisions
- service implementation decisions

Rename the existing "Notes" section to:

## Implementation Notes

If implementation uncovered architectural issues, document them separately.

Do NOT modify the Architecture Handbook unless explicitly instructed.

---

# Git

Work in logical commits.

Group related changes together.

Do not create one massive commit.

---

# Final Output

When finished provide:

1. Summary of what was implemented.
2. Files created.
3. Files modified.
4. Migrations created.
5. Tests added.
6. Test results.
7. Any implementation decisions recorded.
8. Any technical debt discovered.
9. Any recommendations before starting Phase 2.

If implementation cannot be completed because of an architectural issue, stop and explain the issue instead of inventing a solution.
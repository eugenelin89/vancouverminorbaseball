# Prompt 68 - Platform

## User Prompt

```text
The VCB Platform User Manual has become feature-complete, but it has evolved incrementally over many implementation phases.

Your task is NOT to add significant new functionality.

Your task is to transform the manual into a polished production-quality user manual.

==================================================
Goals
==================================================

Optimize for usability.

Assume the audience consists of:

- administrators
- coordinators
- staff
- coaches
- players

Many readers are not technical.

The manual should help users accomplish tasks quickly.

==================================================
Review
==================================================

Review:

- docs/USER_MANUAL.md
- docs/ARCHITECTURE.md
- docs/deployment/README.md
- docs/deployment/RUNBOOK.md
- docs/evaluations/
- docs/account_management/

Review the current implementation to ensure the manual accurately reflects the application.

==================================================
Objectives
==================================================

Improve the manual by:

1.

Reorganizing the document into a logical flow.

2.

Creating role-based quick start sections:

- Administrator Quick Start
- Staff Quick Start
- Coach Quick Start
- Player Quick Start

Each should explain:

- where to log in
- where to begin
- typical daily workflow
- pages they normally use

3.

Separate beginner guidance from reference material.

New users should understand the system without reading the entire manual.

4.

Move deployment and environment configuration out of the user manual.

The user manual should not discuss:

DJANGO_SECRET_KEY

DJANGO_DEBUG

STATIC_ROOT

ALLOWED_HOSTS

or any deployment configuration.

Instead, reference:

docs/deployment/

5.

Reduce repetition.

If a concept is explained once, avoid repeating it elsewhere.

6.

Improve terminology consistency.

Prefer "evaluation" for user-facing language.

If internal terminology still uses "assessment" or "observation", briefly explain the relationship once.

Avoid switching terminology throughout the document.

7.

Improve navigation.

Each major section should begin with:

Purpose

Who uses it

Typical workflow

Related pages

8.

Improve readability.

Use:

- shorter paragraphs
- concise bullets
- task-oriented headings

Avoid walls of text.

9.

Clearly distinguish:

Player-facing features

Coach-facing features

Staff-only features

Administrator-only features

10.

Improve the FAQ.

Focus on real user questions.

Remove redundant questions.

11.

Keep all documented URLs accurate.

12.

Review every documented feature against the current implementation.

Remove anything obsolete.

Document anything implemented but missing.

==================================================
Do NOT
==================================================

Do not invent features.

Do not describe future ideas as current functionality.

Do not remove important operational information.

Do not rewrite merely for style if the existing wording is already clear.

==================================================
Deliverable
==================================================

Update only:

docs/USER_MANUAL.md

No other documentation should require significant modification unless a broken cross-reference is discovered.

==================================================
Review Loop
==================================================

After completing the rewrite:

Perform a documentation review as if you were:

- a coach
- a player
- an administrator

Identify:

- confusing sections
- duplicated information
- missing navigation
- inconsistent terminology

Fix every issue found.

Repeat this review until no significant usability improvements remain.

==================================================
Verification
==================================================

Run:

git diff --check

==================================================
Commit
==================================================

Create two commits:

1.

Improve USER_MANUAL usability

2.

Archive prompt

==================================================
Final Report
==================================================

Report:

- sections reorganized
- obsolete material removed
- new quick-start sections added
- terminology improvements
- usability improvements
- verification result
- commits created
```

## Documentation Commit

Commit: `7bfc110`

Message: `Improve USER_MANUAL usability`

Changed files:

```text
docs/USER_MANUAL.md
```

Diff summary:

```text
docs/USER_MANUAL.md | 830 +++++++++++++++++++++++++++++++---------------------
1 file changed, 503 insertions(+), 327 deletions(-)
```

Full diff note: the implementation commit rewrites the user manual into a production-quality, role-based guide. The prompt archive records the commit hash and summary instead of duplicating the full manual diff.

# Prompt 82 - Platform

## User Prompt

```text
Perform Repository Cleanup Phase 2 only: Dependency and Tooling Hygiene.

Use continuous loop engineering.

Continue until dependency versions are internally consistent, repository tooling is standardized, verification passes, commits are pushed, and the working tree is clean.

Do not intentionally change application behavior.

Do not perform architectural refactoring.

Do not modify business logic except where required to maintain compatibility with dependency updates.

==================================================
Objective
=========

The platform is now feature complete through Seasonal Participation V1.

Before structural refactoring begins, establish a clean, consistent development environment.

This phase should only improve repository hygiene and developer experience.

==================================================
Scope
=====

Review at minimum:

* `requirements.txt`
* `README.md`
* `AGENTS.md`
* current Python version assumptions
* Django version
* any existing formatting or lint configuration
* test configuration

Determine whether the repository currently has:

* consistent dependency versions
* outdated Django patch versions
* missing repository-wide formatter configuration
* missing repository-wide lint configuration
* missing import sorting configuration
* missing pre-commit configuration

==================================================
Django Version
==============

Review the Django version currently pinned.

If the repository is not using the latest compatible Django 4.2 LTS patch release:

* upgrade only within Django 4.2 LTS
* do NOT migrate to Django 5.x
* keep behavior identical

Do not modify historical migration headers merely because Django version comments differ.

==================================================
Repository Tooling
==================

Introduce conservative repository-wide tooling if missing.

Preferred stack:

* Ruff
* Black
* isort
* pre-commit

Configuration should be conservative and compatible with the existing coding style.

Avoid large formatting changes.

If introducing Ruff, configure it to enforce correctness first rather than aggressive stylistic rules.

==================================================
Formatting
==========

Run formatting only where necessary.

Do not reformat the entire repository unless required.

Avoid generating massive whitespace-only diffs.

==================================================
Verification
============

Run:

* `python manage.py check`
* `python manage.py makemigrations --check`
* `python manage.py migrate --plan`
* full test suite
* `git diff --check`

==================================================
Acceptance Criteria
===================

Do not declare PASS until:

✓ dependency versions are internally consistent

✓ repository tooling is standardized

✓ no unnecessary formatting churn

✓ Django remains on supported 4.2 LTS

✓ application behavior unchanged

✓ full test suite passes

✓ `git diff --check` passes

✓ implementation commit pushed

✓ prompt archive committed separately

✓ working tree clean

==================================================
Loop Workflow
=============

Every loop must:

1. inspect repository tooling
2. identify concrete improvements
3. implement only tooling/dependency changes
4. verify compatibility
5. run full verification
6. commit implementation
7. archive the prompt according to AGENTS.md
8. commit the prompt archive separately
9. push both commits
10. confirm working tree clean
11. determine CONTINUE, PASS, BLOCKED, or NO_PROGRESS

If CONTINUE, immediately begin the next loop.

==================================================
Suggested Commit Message
========================

Standardize repository tooling

==================================================
Final Report
============

Report:

* terminal state
* loops completed
* dependency updates
* tooling added or configured
* verification
* commits
* push result
* confirmation that application behavior is unchanged
* confirmation that working tree is clean
```

## Implementation Commit

`cbb2963` - Standardize repository tooling

## Commit Diff

```diff
commit cbb2963795d6a611745128c710ae62ba8a133739
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 16 02:48:31 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 16 02:48:31 2026 -0700

    Standardize repository tooling
---
 .pre-commit-config.yaml | 22 ++++++++++++++++++++++
 AGENTS.md               | 11 +++++++++++
 README.md               | 26 ++++++++++++++++++++++++++
 pyproject.toml          | 41 +++++++++++++++++++++++++++++++++++++++++
 requirements-dev.txt    |  6 ++++++
 requirements.txt        |  6 +++---
 6 files changed, 109 insertions(+), 3 deletions(-)

diff --git a/.pre-commit-config.yaml b/.pre-commit-config.yaml
new file mode 100644
index 0000000..591776b
--- /dev/null
+++ b/.pre-commit-config.yaml
@@ -0,0 +1,22 @@
+repos:
+  - repo: https://github.com/astral-sh/ruff-pre-commit
+    rev: v0.15.21
+    hooks:
+      - id: ruff-check
+
+  - repo: https://github.com/psf/black
+    rev: 25.11.0
+    hooks:
+      - id: black
+
+  - repo: https://github.com/PyCQA/isort
+    rev: 6.1.0
+    hooks:
+      - id: isort
+
+  - repo: https://github.com/pre-commit/pre-commit-hooks
+    rev: v6.0.0
+    hooks:
+      - id: check-yaml
+      - id: end-of-file-fixer
+      - id: trailing-whitespace
diff --git a/AGENTS.md b/AGENTS.md
index 7811510..34772ee 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -67,6 +67,17 @@ When a user prompt causes any file to be created, modified, moved, or deleted:
 - Use `select_related()` and `prefetch_related()` where practical to avoid obvious N+1 queries.
 - Do not introduce new models, migrations, APIs, JavaScript, charts, exports, background jobs, caching, or AI functionality unless the task explicitly calls for them.
 
+## Repository Tooling
+
+- Runtime dependencies live in `requirements.txt`.
+- Development tooling lives in `requirements-dev.txt`.
+- Black, isort, and Ruff configuration lives in `pyproject.toml`.
+- Pre-commit hook configuration lives in `.pre-commit-config.yaml`.
+- Use Ruff primarily for correctness checks. Do not expand lint rules aggressively without a specific cleanup task.
+- Avoid whole-repository formatting unless explicitly requested. Prefer formatting only files already touched by the current task.
+- Run Black, isort, Ruff, and pre-commit on touched Python files when practical. Do not treat existing untouched formatting drift as part of an unrelated task.
+- Do not modify historical migration headers or generated files solely to satisfy formatting tools.
+
 ## Documentation
 
 - Keep subsystem documentation consistent with implementation changes.
diff --git a/README.md b/README.md
index f4d60f2..8231ec0 100644
--- a/README.md
+++ b/README.md
@@ -92,6 +92,32 @@ DJANGO_SECRET_KEY=test python manage.py test
 DJANGO_SECRET_KEY=test python manage.py test accounts analytics players seasons drafts
 ```
 
+## Development Tooling
+
+Runtime dependencies are pinned in `requirements.txt`. Developer tooling is pinned separately in `requirements-dev.txt`.
+
+Install development tools when you want local formatting, linting, or pre-commit checks:
+
+```bash
+pip install -r requirements-dev.txt
+```
+
+Repository-wide tooling configuration lives in:
+
+- `pyproject.toml` for Black, isort, and Ruff settings.
+- `.pre-commit-config.yaml` for pre-commit hook definitions.
+
+Use conservative checks on files changed by the current task:
+
+```bash
+ruff check path/to/file.py
+black --check path/to/file.py
+isort --check-only path/to/file.py
+pre-commit run --files path/to/file.py
+```
+
+Avoid whole-repository formatting unless the task explicitly calls for it. Prefer formatting only files that are already part of the current change. The repository now has shared tooling configuration, but historical Python files have not been bulk reformatted.
+
 ## Repository Structure
 
 ```text
diff --git a/pyproject.toml b/pyproject.toml
new file mode 100644
index 0000000..a1ff1e5
--- /dev/null
+++ b/pyproject.toml
@@ -0,0 +1,41 @@
+[tool.black]
+line-length = 88
+target-version = ["py39"]
+extend-exclude = '''
+/(
+    \.git
+  | \.venv
+  | __pycache__
+  | migrations
+  | media
+  | staticfiles
+)/
+'''
+
+[tool.isort]
+profile = "black"
+line_length = 88
+py_version = 39
+skip = [
+    ".git",
+    ".venv",
+    "__pycache__",
+    "migrations",
+    "media",
+    "staticfiles",
+]
+
+[tool.ruff]
+line-length = 88
+target-version = "py39"
+extend-exclude = [
+    ".git",
+    ".venv",
+    "__pycache__",
+    "migrations",
+    "media",
+    "staticfiles",
+]
+
+[tool.ruff.lint]
+select = ["E4", "E7", "E9", "F"]
diff --git a/requirements-dev.txt b/requirements-dev.txt
new file mode 100644
index 0000000..4208080
--- /dev/null
+++ b/requirements-dev.txt
@@ -0,0 +1,6 @@
+-r requirements.txt
+
+black==25.11.0
+isort==6.1.0
+pre-commit==4.3.0
+ruff==0.15.21
diff --git a/requirements.txt b/requirements.txt
index 04325a3..e197548 100644
--- a/requirements.txt
+++ b/requirements.txt
@@ -1,5 +1,5 @@
-asgiref==3.8.1
-Django==4.2.11
+asgiref==3.10.0
+Django==4.2.30
 gunicorn==21.2.0
 pillow==11.3.0
-sqlparse==0.4.4
+sqlparse==0.5.3
```

## Verification

- `pre-commit run --files AGENTS.md README.md requirements.txt requirements-dev.txt pyproject.toml .pre-commit-config.yaml`: passed.
- `DJANGO_SECRET_KEY=test python manage.py check`: passed.
- `DJANGO_SECRET_KEY=test python manage.py makemigrations --check`: passed.
- `DJANGO_SECRET_KEY=test python manage.py migrate --plan`: passed.
- `DJANGO_SECRET_KEY=test python manage.py test`: passed, 458 tests.
- `git diff --check`: passed.

## Notes

- Whole-repository Black/isort formatting was intentionally not run because it would create a large whitespace-only diff across historical Python files.
- Ruff was configured for correctness-oriented checks only: `E4`, `E7`, `E9`, and `F`.

## Terminal State

PASS

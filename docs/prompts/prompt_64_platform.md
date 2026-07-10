# Prompt 64 - Platform

## Prompt

```text
Fix the tracked Django `SECRET_KEY` issue before regenerating the repository flat-file snapshot.

This is a focused security/configuration task.

Do NOT change application behavior beyond secure settings configuration.

Do NOT regenerate `project_flat_file.txt` in this task.

==================================================
Goal
====

Remove the hardcoded tracked Django `SECRET_KEY` from:

* `vancouverminor/settings.py`

Replace it with environment-based configuration suitable for development and production.

==================================================
Before Coding
=============

Read:

* AGENTS.md
* README.md
* `.gitignore`
* `vancouverminor/settings.py`
* any existing deployment/environment documentation
* any existing environment-variable helpers or settings patterns in the repository

Inspect Git history only as needed to understand whether the key has already been committed and pushed.

Do not print or repeat the existing secret value in output, logs, prompt archives, commit messages, or documentation.

==================================================
Required Behavior
=================

1. Environment variable

Read Django’s secret key from:

`DJANGO_SECRET_KEY`

Production must require this environment variable.

Do not silently use the old tracked value.

2. Development behavior

Choose the smallest safe approach consistent with the current repository.

Preferred options, in order:

A. Require `DJANGO_SECRET_KEY` in every environment and document how to set it.

B. If the project already has an explicit development-mode convention, permit a clearly non-secret development-only fallback when `DEBUG=True`.

Any fallback must:

* be obviously development-only;
* never be suitable for production;
* never reuse the exposed tracked value;
* not be generated randomly on every process start if that would break sessions unpredictably;
* be documented.

Do not create a `.env` file containing a real secret.

3. Production safety

Ensure production startup fails clearly if:

* `DEBUG=False`; and
* `DJANGO_SECRET_KEY` is missing or blank.

Use Django’s `ImproperlyConfigured` or the project’s existing configuration-error pattern.

4. `.gitignore`

Ensure local environment files are ignored, including as appropriate:

* `.env`
* `.env.*`

Do not ignore committed example files such as `.env.example` if one exists or is added.

5. Example configuration

If consistent with the repository, add or update a safe example file such as:

* `.env.example`

It may contain:

`DJANGO_SECRET_KEY=replace-with-a-secure-random-value`

It must not contain a real key.

Do not add unnecessary dependencies merely to load `.env` files unless the project already uses them.

6. Documentation

Update the smallest appropriate documentation file to explain:

* `DJANGO_SECRET_KEY` is required for production;
* developers must set it in their environment;
* a secure value can be generated locally;
* real secrets must never be committed.

Do not include an actual generated secret.

7. Rotation note

Document that the previously committed key must be considered exposed and rotated in every deployed environment that used it.

Do not attempt to rewrite Git history in this task.

Do not expose the old key while documenting the issue.

==================================================
Security Review
===============

Search tracked source/configuration files for other obvious secret-like values, including:

* `SECRET_KEY`
* API keys
* access tokens
* database passwords
* cloud credentials
* OAuth client secrets
* private keys

Do not make unrelated broad changes.

If another real secret is found:

* stop;
* report only the file path and variable/key name;
* do not print the value;
* do not commit partial fixes unless the repository instructions clearly allow it.

==================================================
Testing
=======

Add focused tests or settings checks if practical.

Verify at minimum:

1. Development startup/check succeeds with `DJANGO_SECRET_KEY` set.
2. Production-style configuration fails clearly when `DJANGO_SECRET_KEY` is missing.
3. Production-style configuration succeeds when `DJANGO_SECRET_KEY` is set.
4. The old hardcoded secret is no longer present in tracked current files.

Run:

* `DJANGO_SECRET_KEY=test-only-not-production python manage.py check`
* `DJANGO_SECRET_KEY=test-only-not-production python manage.py test`
* `git diff --check`

If the test suite relies on environment settings, use a clearly fake test-only value.

==================================================
Git Hygiene
===========

Before committing, verify:

* no real secret appears in the diff;
* no `.env` file with secret values is tracked;
* no secret appears in prompt archives;
* no application functionality was changed beyond settings/configuration safety.

Commit the security fix first.

Suggested commit message:

`Move Django secret key to environment`

Create the next prompt archive according to `AGENTS.md`, but redact all secret values.

Commit the prompt archive separately.

Push both commits.

==================================================
Final Report
============

Report:

* terminal state: PASS or BLOCKED;
* files modified;
* configuration approach chosen;
* development behavior;
* production missing-key behavior;
* `.gitignore` or example-environment changes;
* documentation updates;
* additional secret-like findings, listing only paths and variable names;
* tests run and results;
* commit hashes;
* push result;
* confirmation that no secret values were printed or committed;
* confirmation that `project_flat_file.txt` was not regenerated yet.

```

## Implementation Commit

`f690686 Move Django secret key to environment`

## Summary

Moved Django `SECRET_KEY` configuration to the `DJANGO_SECRET_KEY` environment variable, added safe environment documentation, ignored local `.env` files, and added settings configuration tests.

`project_flat_file.txt` was not regenerated in this task, per the prompt.

## Tests Run

- `DJANGO_SECRET_KEY=test-only-not-production python manage.py check` - passed
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py test` - passed, 387 tests
- `git diff --check` - passed

## Security Notes

- The prompt archive redacts the removed tracked key from the commit diff.
- Active source/configuration files no longer contain the removed hardcoded Django key.
- `project_flat_file.txt` still contains the old snapshot copy and must be regenerated next.

## Commit Diff

```diff
commit f69068616be6eb725983a161d863ff17b5319ee5
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Fri Jul 10 12:42:32 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Fri Jul 10 12:42:32 2026 -0700

    Move Django secret key to environment
---
 .env.example               |  1 +
 .gitignore                 |  5 ++++-
 README.md                  | 18 +++++++++++++++---
 home/tests.py              | 37 +++++++++++++++++++++++++++++++++++++
 vancouverminor/settings.py |  7 ++++++-
 5 files changed, 63 insertions(+), 5 deletions(-)

diff --git a/.env.example b/.env.example
new file mode 100644
index 0000000..7ffc22d
--- /dev/null
+++ b/.env.example
@@ -0,0 +1 @@
+DJANGO_SECRET_KEY=replace-with-a-secure-random-value
diff --git a/.gitignore b/.gitignore
index ce97ed3..d4b6b90 100644
--- a/.gitignore
+++ b/.gitignore
@@ -3,4 +3,7 @@ __pycache__/
 *.pyc
 db.sqlite3
 staticfiles/
-vmba0.code-workspace
\ No newline at end of file
+vmba0.code-workspace
+.env
+.env.*
+!.env.example
diff --git a/README.md b/README.md
index b622ef0..e9ede04 100644
--- a/README.md
+++ b/README.md
@@ -62,12 +62,21 @@ Because the project is simple, most customization happens through data dictionar
 
 1. Create and activate a virtual environment (Python 3.10+ recommended).
 2. Install dependencies (if you add a `requirements.txt`, install from there).
-3. Run migrations if/when models are introduced.
-4. Start the dev server:
+3. Set a local Django secret key in your shell. Use a development-only value locally, and never commit real secrets:
+   ```bash
+   export DJANGO_SECRET_KEY="replace-with-a-secure-random-value"
+   ```
+   You can generate a secure value locally with:
+   ```bash
+   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
+   ```
+   If you use a local `.env` file for your shell tooling, keep it untracked. `.env.example` shows the required variable name without containing a real secret.
+4. Run migrations if/when models are introduced.
+5. Start the dev server:
    ```bash
    python manage.py runserver
    ```
-5. Optional – regenerate placeholder imagery:
+6. Optional – regenerate placeholder imagery:
    ```bash
    pip install Pillow
    python scripts/generate_placeholders.py
@@ -177,6 +186,7 @@ User=www-data
 Group=www-data
 WorkingDirectory=/var/www/vancouverminor/website
 Environment="PATH=/var/www/vancouverminor/website/venv/bin"
+Environment="DJANGO_SECRET_KEY=replace-with-a-secure-random-value"
 ExecStart=/var/www/vancouverminor/website/venv/bin/gunicorn \
           --workers 3 \
           --bind unix:/var/www/vancouverminor/website/vancouverminor.sock \
@@ -195,6 +205,8 @@ sudo systemctl enable --now vancouverminor
 sudo systemctl status vancouverminor
 ```
 
+Use a real secure random value for `DJANGO_SECRET_KEY` in production. The previously committed development key must be treated as exposed and rotated in any deployed environment that used it. Do not commit production secrets to Git.
+
 ### 5. Configure Nginx
 
 Create a new server block `/etc/nginx/sites-available/vancouverminor.com`:
diff --git a/home/tests.py b/home/tests.py
index 2682186..21a3cba 100644
--- a/home/tests.py
+++ b/home/tests.py
@@ -1,3 +1,7 @@
+import os
+import subprocess
+import sys
+
 from django.test import TestCase
 
 
@@ -6,3 +10,36 @@ class HomeNavigationTests(TestCase):
         response = self.client.get("/")
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, '/drafts/live/2026-vcb-13u/')
+
+
+class SettingsConfigurationTests(TestCase):
+    def test_settings_require_django_secret_key(self):
+        env = os.environ.copy()
+        env.pop("DJANGO_SECRET_KEY", None)
+
+        result = subprocess.run(
+            [sys.executable, "-c", "import vancouverminor.settings"],
+            cwd=os.getcwd(),
+            env=env,
+            capture_output=True,
+            text=True,
+            check=False,
+        )
+
+        self.assertNotEqual(result.returncode, 0)
+        self.assertIn("DJANGO_SECRET_KEY", result.stderr)
+
+    def test_settings_load_with_django_secret_key(self):
+        env = os.environ.copy()
+        env["DJANGO_SECRET_KEY"] = "test-only-not-production"
+
+        result = subprocess.run(
+            [sys.executable, "-c", "import vancouverminor.settings"],
+            cwd=os.getcwd(),
+            env=env,
+            capture_output=True,
+            text=True,
+            check=False,
+        )
+
+        self.assertEqual(result.returncode, 0, result.stderr)
diff --git a/vancouverminor/settings.py b/vancouverminor/settings.py
index d2bd938..e7de4b8 100644
--- a/vancouverminor/settings.py
+++ b/vancouverminor/settings.py
@@ -10,8 +10,11 @@ For the full list of settings and their values, see
 https://docs.djangoproject.com/en/4.2/ref/settings/
 """
 
+import os
 from pathlib import Path
 
+from django.core.exceptions import ImproperlyConfigured
+
 # Build paths inside the project like this: BASE_DIR / 'subdir'.
 BASE_DIR = Path(__file__).resolve().parent.parent
 
@@ -20,7 +23,9 @@ BASE_DIR = Path(__file__).resolve().parent.parent
 # See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
 
 # SECURITY WARNING: keep the secret key used in production secret!
-SECRET_KEY = '[REDACTED-REMOVED-SECRET]'
+SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "").strip()
+if not SECRET_KEY:
+    raise ImproperlyConfigured("DJANGO_SECRET_KEY environment variable is required.")
 
 # SECURITY WARNING: don't run with debug turned on in production!
 DEBUG = True

```

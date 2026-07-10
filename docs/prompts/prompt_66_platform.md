# Prompt 66 - Platform

## User Prompt

```text
Implement a deployment-compatibility refactor for Django settings only.

This is NOT a deployment.

The goal is to allow the repository's settings.py to run in both local development and production without requiring production to keep a permanently modified tracked settings.py.

==================================================
Requirements
==================================================

Use environment variables only where environment-specific configuration belongs.

Do NOT change application behavior.

Do NOT change URLs.

Do NOT change models.

Do NOT change migrations.

Do NOT change templates.

Do NOT change any application logic.

==================================================
Implement
==================================================

Refactor vancouverminor/settings.py.

1.

SECRET_KEY

Continue requiring

DJANGO_SECRET_KEY

Raise ImproperlyConfigured if missing.

No fallback.

2.

DEBUG

Replace the hardcoded value with

DJANGO_DEBUG

Accept common true values:

true
1
yes
on

Everything else is False.

Default should be False.

3.

ALLOWED_HOSTS

Read from

DJANGO_ALLOWED_HOSTS

Comma-separated.

Trim whitespace.

Empty entries removed.

Default:

localhost
127.0.0.1

4.

STATIC_ROOT

Read from

DJANGO_STATIC_ROOT

Default:

BASE_DIR / "staticfiles"

Leave STATIC_URL unchanged.

5.

MEDIA_ROOT

Allow override with

DJANGO_MEDIA_ROOT

Default:

BASE_DIR / "media"

6.

Keep SQLite exactly as it is.

Do NOT introduce PostgreSQL.

7.

Do NOT touch INSTALLED_APPS.

Do NOT touch middleware.

Do NOT touch authentication.

Do NOT change login URLs.

==================================================
Documentation
==================================================

Update:

README.md

Add a Deployment Configuration section documenting:

DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_STATIC_ROOT
DJANGO_MEDIA_ROOT

Provide example values.

Explain that production should configure these via the process manager (systemd, Apache, Nginx+Gunicorn, etc.) or shell environment rather than editing settings.py.

Update:

docs/USER_MANUAL.md

Add a short Deployment Configuration section referencing the same environment variables.

==================================================
Tests
==================================================

Add tests covering the settings helper behavior where practical.

Run:

DJANGO_SECRET_KEY=test python manage.py check

DJANGO_SECRET_KEY=test python manage.py test

python manage.py makemigrations --check

git diff --check

==================================================
Review
==================================================

Perform one review loop.

Look specifically for:

- hardcoded environment-specific values
- duplicated environment parsing
- backward compatibility
- production safety
- documentation consistency

Fix anything found.

Re-run the full verification.

==================================================
Documentation
==================================================

Archive this prompt as the next prompt document.

Update any architecture/deployment documentation that references configuration if necessary.

==================================================
Git workflow
==================================================

Follow the standard workflow:

- implement
- self review
- fix review findings
- run verification
- git stage
- commit
- archive prompt
- commit prompt
- push

==================================================
Final report
==================================================

Report:

- implementation summary
- review findings
- fixes applied
- files modified
- tests executed
- verification results
- commits
- push result
- any remaining deployment risks
```

## Implementation Commit

Commit: `bcfc86d8561859aedcbad3b3e1dbdb259b79b4ec`

Message: `Make settings environment-driven for deployment`

Changed files:

```text
README.md
docs/USER_MANUAL.md
docs/deployment/production_readiness_review.md
home/tests.py
vancouverminor/settings.py
```

Diff summary:

```text
README.md                                      |  35 +++
docs/USER_MANUAL.md                            |  14 +
docs/deployment/production_readiness_review.md | 401 +++++++++++++++++++++++++
home/tests.py                                  |  91 ++++++
vancouverminor/settings.py                     |  20 +-
5 files changed, 558 insertions(+), 3 deletions(-)
```

Full diff note: the implementation commit contains a newly added deployment review document plus the settings refactor, tests, and documentation updates. The prompt archive records the commit hash, changed files, and diff summary to avoid duplicating the full deployment review text inside the prompt archive.

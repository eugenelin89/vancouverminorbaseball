# Prompt 67 - Platform

## User Prompt

```text
The production deployment has completed successfully.

Your task is NOT to modify application code.

Your task is to permanently document the deployment and establish a deployment standard for this repository.

==================================================
Review
==================================================

Review the repository:

- AGENTS.md
- README.md
- docs/ARCHITECTURE.md
- docs/USER_MANUAL.md
- docs/deployment/
- requirements.txt
- current settings.py

Review existing deployment documentation and avoid duplication.

==================================================
Historical deployment
==================================================

Document the following deployment as historical fact.

This deployment upgraded production from the original PDP-only system to Platform V1.

The following work was completed successfully.

--------------------------------------------------
Repository
--------------------------------------------------

- Production was approximately 152 commits behind.
- Repository was fast-forwarded to current main.
- Production now matches the repository.

--------------------------------------------------
Backups
--------------------------------------------------

Created before deployment:

- recorded current Git commit
- SQLite backup
- media archive

These backups were completed successfully before any migration.

--------------------------------------------------
Environment configuration
--------------------------------------------------

Deployment moved production from hardcoded configuration to environment configuration.

Created:

/etc/vancouverminorbaseball.env

Configured:

DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_STATIC_ROOT
DJANGO_MEDIA_ROOT

Configured systemd override:

EnvironmentFile=/etc/vancouverminorbaseball.env

Verified using:

- systemd-analyze verify
- systemctl show EnvironmentFiles

Production settings.py is now repository-owned.

Environment-specific configuration is no longer maintained by editing tracked files.

--------------------------------------------------
Dependency verification
--------------------------------------------------

Executed:

pip install -r requirements.txt

No package upgrades were required.

--------------------------------------------------
Django verification
--------------------------------------------------

Executed:

manage.py check

manage.py makemigrations --check

manage.py showmigrations

Verified:

- no model drift
- pending migrations only

--------------------------------------------------
Database migration
--------------------------------------------------

Applied successfully:

players

accounts

analytics

All migrations completed successfully.

--------------------------------------------------
Static files
--------------------------------------------------

Executed:

collectstatic --noinput

Completed successfully.

--------------------------------------------------
Final verification
--------------------------------------------------

Executed:

manage.py check

showmigrations

Verified:

all migrations applied.

--------------------------------------------------
Service restart
--------------------------------------------------

Restarted:

vancouverminor.service

Verified:

- active (running)
- three Gunicorn workers
- clean startup

--------------------------------------------------
Smoke testing
--------------------------------------------------

Verified:

Homepage HTTP 200

/accounts/login/ HTTP 200

/admin/ redirect

Gunicorn startup successful

Expected Internet bot probes returned normal 404 responses.

==================================================
Deliverables
==================================================

Create or update:

docs/deployment/README.md

This becomes the landing page for deployment documentation.

Include:

- deployment philosophy
- deployment workflow
- links to deployment history
- links to operational runbook

--------------------------------------------------

Create:

docs/deployment/production_deployment_2026_07_11.md

Include:

1.
Executive summary

2.
Deployment objective

3.
Production state before deployment

4.
Repository state before deployment

5.
Backups

6.
Environment configuration

7.
Repository upgrade

8.
Dependency verification

9.
Migration execution

10.
Static deployment

11.
Service restart

12.
Smoke testing

13.
Deployment outcome

14.
Lessons learned

15.
Rollback strategy

--------------------------------------------------

Create:

docs/deployment/RUNBOOK.md

This should become the permanent operational deployment guide.

Include:

Pre-deployment

- backup database
- backup media
- record commit
- verify Git status

Repository update

- fetch
- pull
- verify branch

Environment

- verify EnvironmentFile
- verify required variables
- verify systemd configuration

Deployment

- pip install
- manage.py check
- makemigrations --check
- migrate --plan
- migrate
- collectstatic

Restart

- restart service
- verify status
- inspect journal

Verification

- homepage
- admin
- accounts
- static files
- media
- login
- migrations

Rollback

- restore Git commit
- restore SQLite
- restore media
- restart service

Common troubleshooting

Examples:

ImproperlyConfigured

Missing environment variable

Migration failure

collectstatic failure

Gunicorn startup failure

Static files missing

==================================================
Documentation quality
==================================================

Review all deployment documentation.

Remove duplication.

Cross-reference related documents.

Ensure README points to RUNBOOK and deployment history.

==================================================
Rules
==================================================

Documentation only.

No application code.

No settings changes.

No tests.

No migrations.

Do not regenerate project_flat_file.txt.

==================================================
Verification
==================================================

Run only:

git diff --check

==================================================
Commit
==================================================

Create two commits:

1.

Document production deployment

2.

Archive prompt

==================================================
Final Report
==================================================

Report:

- files created
- files modified
- documentation improvements
- verification result
- commits
```

## Documentation Commit

Commit: `9ef8309`

Message: `Document production deployment`

Changed files:

```text
docs/deployment/README.md
docs/deployment/RUNBOOK.md
docs/deployment/production_deployment_2026_07_11.md
```

Diff summary:

```text
3 files changed, 542 insertions(+)
```

Full diff note: the implementation commit creates deployment documentation only. The full diff is intentionally summarized here to avoid duplicating the deployment runbook and historical record inside the prompt archive.

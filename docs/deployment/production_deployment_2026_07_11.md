# Production Deployment - 2026-07-11

This document records the completed production upgrade of Vancouver Minor Baseball from the original PDP-only deployment to Platform V1.

This is a historical deployment record. It does not contain secrets, production-only settings file contents, or executable deployment automation.

## 1. Executive Summary

The production deployment completed successfully.

The upgrade moved production from the original PDP-only system to the current Platform V1 repository. The deployment introduced the platform-forward `players`, `accounts`, and `analytics` apps in production, moved environment-specific configuration out of tracked files, applied database migrations, collected static files, restarted Gunicorn, and verified the production site.

Production now matches the repository and no longer relies on permanent local edits to tracked `settings.py`.

## 2. Deployment Objective

The deployment objective was to safely upgrade production to Platform V1 while preserving production data, media, and service availability.

The deployment specifically aimed to:

- preserve the existing production database and media files;
- replace production-only tracked settings edits with environment-based configuration;
- update production from the older deployed commit to current `main`;
- deploy Platform V1 apps for player identity, account management, and analytics;
- apply database migrations safely;
- collect static assets for the upgraded code;
- restart the Gunicorn service cleanly;
- verify the upgraded site responds correctly after deployment.

## 3. Production State Before Deployment

Before deployment:

- production was running the original PDP-oriented system;
- production was approximately 152 commits behind current `main`;
- production had local uncommitted changes to `vancouverminor/settings.py`;
- those local settings changes contained production-specific host/static/media configuration;
- production used SQLite;
- production stored uploaded media under the production media directory.

The local production settings edits were intentionally replaced by systemd-managed environment configuration before the repository upgrade.

## 4. Repository State Before Deployment

Before deployment:

- the repository had advanced to Platform V1;
- the repository included `players`, `accounts`, and `analytics`;
- deployment-specific values had been refactored into environment variables;
- tracked `vancouverminor/settings.py` could run in production when required environment variables were present;
- production had not yet been fast-forwarded to current `main`.

## 5. Backups

Before deployment, these backups were completed successfully:

- recorded the current production Git commit;
- backed up the SQLite database;
- archived the media directory.

These backups were created before any migration was applied.

## 6. Environment Configuration

The deployment moved production from hardcoded/tracked configuration to environment configuration.

Created:

```text
/etc/vancouverminorbaseball.env
```

Configured environment variable names:

```text
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_STATIC_ROOT
DJANGO_MEDIA_ROOT
```

Configured systemd override:

```text
EnvironmentFile=/etc/vancouverminorbaseball.env
```

Verified using:

```text
systemd-analyze verify
systemctl show EnvironmentFiles
```

Production `settings.py` is now repository-owned. Environment-specific configuration is no longer maintained by editing tracked files.

The environment file is production server configuration. It must not be committed to Git and must not be reproduced in documentation.

## 7. Repository Upgrade

Production was fast-forwarded to current `main`.

Production had local modifications to `vancouverminor/settings.py`. After those values were replaced by environment variables, the local settings changes were intentionally discarded so production could use the tracked repository version.

The repository upgrade brought production onto Platform V1, including first production deployment of:

- `players`
- `accounts`
- `analytics`

After the repository upgrade, production matched the repository.

## 8. Dependency Verification

Dependency verification was performed with:

```text
pip install -r requirements.txt
```

No package upgrades were required.

## 9. Migration Execution

Before applying migrations, Django verification commands were run:

```text
manage.py check
manage.py makemigrations --check
manage.py showmigrations
```

These checks confirmed:

- Django could load with the production environment;
- there was no model drift;
- only expected pending migrations remained.

The production database migration then applied the Platform V1 migration chains for:

- `players`
- `accounts`
- `analytics`

All migrations completed successfully.

## 10. Static Deployment

Static files were collected with:

```text
collectstatic --noinput
```

Static collection completed successfully using the production `DJANGO_STATIC_ROOT` value loaded by systemd.

## 11. Service Restart

The production service was restarted:

```text
vancouverminor.service
```

Post-restart verification confirmed:

- service was active and running;
- three Gunicorn workers started;
- Gunicorn startup was clean;
- no startup failures were reported.

## 12. Smoke Testing

Smoke tests verified:

- homepage returned HTTP 200;
- `/accounts/login/` returned HTTP 200;
- `/admin/` redirected as expected;
- Gunicorn startup was successful;
- expected Internet bot probes returned normal 404 responses.

Final verification commands executed:

```text
manage.py check
showmigrations
```

Verified:

- Django system check passed;
- all migrations were applied.

## 13. Deployment Outcome

The deployment completed successfully.

Outcome:

- production was fast-forwarded to current `main`;
- production now matches the repository;
- production no longer maintains environment-specific tracked-file edits;
- `/etc/vancouverminorbaseball.env` provides production configuration;
- systemd loads the production environment file;
- `players`, `accounts`, and `analytics` are deployed;
- migrations are applied;
- static files are collected;
- Gunicorn is active with three workers;
- smoke tests passed.

## 14. Lessons Learned

Deployment observations:

- avoid production-only edits to tracked files;
- keep deployment configuration outside Git;
- always verify migrations before applying them;
- back up the database before migration;
- archive media before major upgrades;
- verify dependency state before migrating;
- run Django checks before and after deployment;
- verify Gunicorn after restart;
- smoke test public and authenticated entry points after the service restart;
- keep a written deployment record for future releases.

## 15. Rollback Strategy

Rollback should restore the pre-deployment state using the backups created before deployment.

Rollback steps:

1. Stop or isolate the production service.
2. Restore the SQLite database backup.
3. Restore the archived media directory if media changes need to be rolled back.
4. Return the repository to the previously recorded production Git commit.
5. Restore previous service configuration if necessary.
6. Restart Gunicorn.
7. Verify homepage, login, admin redirect, static assets, media access, and service logs.

Because migrations were applied during the deployment, rolling back code without restoring the database backup is not the preferred rollback path. The safest rollback restores both the previous code revision and the pre-migration database backup.

For future releases, use the permanent [Deployment Runbook](RUNBOOK.md).

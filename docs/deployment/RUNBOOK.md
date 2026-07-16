# Deployment Runbook

This runbook is the standard operational deployment guide for the Vancouver Minor Baseball platform.

It assumes production uses the tracked repository, systemd, Gunicorn, SQLite, and environment configuration loaded from `/etc/vancouverminorbaseball.env`.

Do not paste secrets into this document.

## Pre-Deployment

Before changing production code:

1. Review the release scope.
2. Confirm no unexpected local source changes are present.
3. Record the current production Git commit.
4. Back up the SQLite database.
5. Archive the media directory.
6. Confirm the rollback target is known.

Required checks:

```bash
git status
git log -n1
```

Backups should be completed before running migrations.

## Repository Update

Fetch and update the repository to the intended release:

```bash
git fetch
git pull
git status
git log -n1
```

Verify:

- production is on the expected branch;
- production is at the intended commit;
- no unexpected tracked-file modifications remain.

If production has local tracked-file changes, stop and understand them before proceeding.

## Environment

Production configuration should be supplied by:

```text
/etc/vancouverminorbaseball.env
```

Required environment variable names:

```text
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_STATIC_ROOT
DJANGO_MEDIA_ROOT
```

Verify systemd configuration:

```bash
systemd-analyze verify /etc/systemd/system/vancouverminor.service
systemctl show vancouverminor.service --property=EnvironmentFiles
```

Verify that production uses `EnvironmentFile=/etc/vancouverminorbaseball.env`.

Do not commit `/etc/vancouverminorbaseball.env`.

## Deployment

Activate the production virtual environment if needed, then verify dependencies:

```bash
pip install -r requirements.txt
```

Run Django checks:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py showmigrations
```

Review planned migrations:

```bash
python manage.py migrate --plan
```

### Seasonal Participation Empty-State Check

Before applying the initial `seasons` app migration, verify production still has no Platform V1 roster/evaluation data requiring seasonal backfill:

```text
Players: 0
Coach profiles: 0
Observations: 0
```

If these counts are no longer zero, stop the deployment and create a reviewed migration/backfill plan. Do not fabricate legacy seasons, player roster memberships, coach assignments, or observation context during the schema migration.

Apply migrations:

```bash
python manage.py migrate
```

Collect static files:

```bash
python manage.py collectstatic --noinput
```

## Restart

Restart the production service:

```bash
sudo systemctl restart vancouverminor.service
sudo systemctl status vancouverminor.service
```

Inspect the journal:

```bash
sudo journalctl -u vancouverminor.service -n 100 --no-pager
```

Verify:

- service is active;
- Gunicorn workers started;
- no startup traceback appears;
- no missing environment variable error appears.

## Verification

After restart, verify:

- homepage returns HTTP 200;
- `/accounts/login/` returns HTTP 200;
- `/admin/` redirects as expected;
- static files load;
- media files load where expected;
- login page renders;
- migrations are applied;
- service logs remain clean.

Suggested checks:

```bash
python manage.py check
python manage.py showmigrations
```

Also inspect web server and Gunicorn logs for unexpected errors.

## Rollback

Rollback should restore the pre-deployment state.

Rollback steps:

1. Stop or isolate the production service.
2. Restore the previous Git commit.
3. Restore the SQLite backup.
4. Restore the media archive if needed.
5. Restore previous service configuration if it changed.
6. Restart `vancouverminor.service`.
7. Verify homepage, login, admin redirect, static files, media files, and service logs.

If migrations were applied, do not assume the old code can safely run against the migrated database. Prefer restoring the pre-migration SQLite backup.

## Common Troubleshooting

### ImproperlyConfigured

Likely causes:

- missing required environment variable;
- systemd not loading the environment file;
- typo in `/etc/vancouverminorbaseball.env`.

Check:

```bash
systemctl show vancouverminor.service --property=EnvironmentFiles
sudo journalctl -u vancouverminor.service -n 100 --no-pager
```

### Missing Environment Variable

If Django reports a missing setting such as `DJANGO_SECRET_KEY`, verify:

- the variable exists in `/etc/vancouverminorbaseball.env`;
- the systemd service includes `EnvironmentFile=/etc/vancouverminorbaseball.env`;
- systemd was reloaded after service file changes;
- the service was restarted.

### Migration Failure

If migration fails:

1. Stop and preserve the error output.
2. Do not continue applying unrelated changes.
3. Confirm the database backup exists.
4. Decide whether to fix forward or restore the pre-deployment backup.

### collectstatic Failure

Check:

- `DJANGO_STATIC_ROOT` value;
- directory permissions;
- available disk space;
- whether the virtual environment has all required dependencies.

### Gunicorn Startup Failure

Check:

- service status;
- Gunicorn journal;
- environment file loading;
- Python virtual environment path;
- `DJANGO_SECRET_KEY`;
- import or migration errors.

### Static Files Missing

Check:

- `collectstatic` completed successfully;
- `DJANGO_STATIC_ROOT` matches the web server static alias;
- file permissions allow the web server to read collected files;
- browser cache is not showing stale results.

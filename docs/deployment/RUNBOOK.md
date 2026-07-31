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
COACH_IMPORT_DEFAULT_PASSWORD
ANALYTICS_ASSESSMENTS_ENABLED
ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES
ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES
```

Verify systemd configuration:

```bash
systemd-analyze verify /etc/systemd/system/vancouverminor.service
systemctl show vancouverminor.service --property=EnvironmentFiles
```

Verify that production uses `EnvironmentFile=/etc/vancouverminorbaseball.env`.

Do not commit `/etc/vancouverminorbaseball.env`.

`COACH_IMPORT_DEFAULT_PASSWORD` must be set before staff create new coach
accounts through coach import. Set it securely in
`/etc/vancouverminorbaseball.env`, restart the application service after changing
it, communicate it to coaches through an approved operational channel, and
rotate it when appropriate. Do not paste the value into Git, logs, screenshots,
or shared documentation.

`ANALYTICS_ASSESSMENTS_ENABLED` defaults to false. Keep it false until the
assessment configuration has been bootstrapped, assessment events have been
created, and staff are ready to import workbook assessment data.

Assessment workbook uploads default to a 10 MiB file limit and a 50 MiB
uncompressed archive limit. Override `ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES` or
`ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES` only after reviewing production
memory limits. Lower values are safer; do not raise them casually.

Bootstrap the initial 2026 13U assessment configuration without importing player
results:

```bash
python manage.py bootstrap_2026_13u_assessment --dry-run
python manage.py bootstrap_2026_13u_assessment
```

Do not enable the feature as part of a routine deploy. Use the controlled rollout below.

### Controlled Assessment Rollout

#### Stage 1: Back Up And Deploy Disabled

1. Record the current production commit.
2. Back up `db.sqlite3` and archive media.
3. Pull the reviewed release and install `requirements.txt`.
4. Keep `ANALYTICS_ASSESSMENTS_ENABLED=false`.
5. Run Django checks, review `migrate --plan`, apply migrations, and collect static files if changed.
6. Restart Gunicorn and verify current self, peer, coach, staff, and guest evaluation workflows.
7. Confirm assessment navigation is absent.

#### Stage 2: Bootstrap Configuration

1. Run `bootstrap_2026_13u_assessment --dry-run`.
2. Review every sheet/header requirement, 1–3 rating scale, unit status, zero policy, and blank policy.
3. Run the bootstrap normally only when the dry run is correct.
4. Do not import player data during bootstrap.

#### Stage 3: Enable Staff-Only Preview

1. Set `ANALYTICS_ASSESSMENTS_ENABLED=true` and restart Gunicorn.
2. Confirm only staff can access the pages.
3. Create/select the assessment event and upload the workbook.
4. Review every match, warning, zero transformation, unverified unit, and planned action.
5. Confirm preview created no player-assessment values.

#### Stage 4: Controlled Import

1. Take a second database backup.
2. Confirm the fully resolved and acknowledged import.
3. Reconcile database aggregate counts with workbook aggregate counts.
4. Inspect representative player records and keep the feature staff-only.

### Assessment Rollback

For immediate visual rollback, set `ANALYTICS_ASSESSMENTS_ENABLED=false` and restart Gunicorn. The assessment migrations are additive, so existing evaluations remain available. Do not reverse assessment migrations after production assessment data exists; restore a verified pre-import database backup only as part of an approved destructive rollback.

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

## Seasonal Participation V1 Rollout

Seasonal Participation V1 is additive and keeps legacy/no-season records readable. Do not fabricate seasons, teams, roster memberships, coach assignments, or evaluation context during deployment.

Use these steps when deploying the completed Seasonal Participation V1 release.

### 1. Become The Production User

```bash
sudo -iu django-user
cd /var/www/vancouverminorbaseball
source venv/bin/activate
```

### 2. Record Current State And Back Up

```bash
git status
git log -n1 --oneline > /tmp/vcb_pre_deploy_commit.txt
cp db.sqlite3 "db.sqlite3.pre_seasons_v1.$(date +%Y%m%d%H%M%S).bak"
tar -czf "media.pre_seasons_v1.$(date +%Y%m%d%H%M%S).tgz" media
```

### 3. Update Code

```bash
git fetch origin
git pull --ff-only origin main
pip install -r requirements.txt
```

If `git pull --ff-only` fails, stop and resolve the repository state before continuing.

### 4. Load Production Environment

```bash
set -a
. /etc/vancouverminorbaseball.env
set +a
```

### 5. Run Pre-Migration Checks

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate --plan
python manage.py showmigrations seasons players accounts analytics
python manage.py shell -c "from players.models import Player; from accounts.models import AccountProfile, AccountRole; from analytics.models import Observation; from seasons.models import Season, SeasonTeam, PlayerRosterMembership, CoachSeasonAssignment; print({'players': Player.objects.count(), 'coach_profiles': AccountProfile.objects.filter(role=AccountRole.COACH).count(), 'observations': Observation.objects.count(), 'seasons': Season.objects.count(), 'season_teams': SeasonTeam.objects.count(), 'player_roster_memberships': PlayerRosterMembership.objects.count(), 'coach_season_assignments': CoachSeasonAssignment.objects.count()})"
```

If unexpected production data exists before rollout, stop. Do not fabricate historical context. Create a reviewed migration/backfill plan before applying migrations that would require historical interpretation.

### 6. Stop Service, Migrate, Collect Static, Restart

```bash
sudo systemctl stop vancouverminor.service
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl start vancouverminor.service
sudo systemctl status vancouverminor.service
sudo journalctl -u vancouverminor.service -n 100 --no-pager
```

### 7. HTTP Smoke Tests

```bash
curl -I https://vancouverminor.com/
curl -I https://vancouverminor.com/accounts/login/
curl -I https://vancouverminor.com/seasons/
curl -I https://vancouverminor.com/analytics/
```

Unauthenticated staff pages such as `/seasons/` and `/analytics/` should redirect to login rather than expose data.

### 8. Browser Workflow Verification

Use optional test data only if the production operator has approved it. If test data is created in production, record what was created and clean it up only through approved application workflows.

Checklist:

1. Sign in as a Django staff user.
2. Open Season Operations at `/seasons/`.
3. Create a clearly named test season if approved.
4. Create a test season team if approved.
5. Import a small player CSV for the test season if approved.
6. Verify the player roster membership appears under Season Operations.
7. Import a small coach CSV for the test season if approved.
8. Verify the coach assignment appears under Season Operations.
9. Verify a returning coach import does not change the coach password hash.
10. Create an evaluation cycle linked to the season if approved.
11. Submit a self-evaluation.
12. Submit a coach evaluation.
13. Review saved season/team snapshots in evaluation review.
14. Transfer the test player to another team.
15. Verify the old submitted evaluation still displays the original season/team snapshot.
16. View player season history.
17. View coach assignment history.
18. Sign in as a non-staff coach/player and verify `/seasons/` access is denied.

### Seasonal Participation Empty-State Check

Before applying the initial `seasons` app migration or the Analytics migration that adds observation season context, verify production still has no Platform V1 roster/evaluation data requiring seasonal backfill:

```text
Players: 0
Coach profiles: 0
Observations: 0
```

If these counts are no longer zero, stop the deployment and create a reviewed migration/backfill plan. Do not fabricate legacy seasons, player roster memberships, coach assignments, or observation context during the schema migration. Existing observations in non-production environments should remain nullable and display as `Legacy / No Season` unless a reviewed backfill plan exists.

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

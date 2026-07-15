# Production Readiness Review

Date: 2026-07-10

Scope: engineering review only. This document does not deploy code, modify settings, create migrations, or reproduce the production-only `vancouverminor/settings.py`.

Status: historical pre-deployment review. The production upgrade described as a future action in this document was completed on 2026-07-11 and is recorded in [Production Deployment - 2026-07-11](production_deployment_2026_07_11.md). Keep this document as the readiness record that informed that deployment.

## Executive Summary

At the time of this review, the repository should not replace the production code in a direct `git pull` without preparation.

At the time of this review, production was based on commit `551dd0de458ba09628dc85183ef04f9e778fa98f` with local, uncommitted production edits to `vancouverminor/settings.py`. The repository had advanced substantially since that revision and included completed Players V1, Analytics V1, Account Management V1, Platform V1 Account Operations, and Evaluation Access V1.

The main blockers were configuration and migration readiness, not a need for a different database engine. Production needed to preserve domain/static/media settings, rotate and externalize the Django secret key, install the new apps in settings, add the account password-change middleware, update login settings, install current dependencies, run all new migrations, and collect static files before switching traffic to the new code.

Historical go/no-go recommendation: **NO-GO for direct replacement at review time. GO only after the required production changes and a rehearsed backup/migration/rollback sequence were completed.**

## Repository Status

Current repository head at review time:

```text
fcfd18b42362ab31a7f6772775801765c2953d31
```

The current repository includes:

- `home`
- `drafts`
- `pdp`
- `leaguehub`
- `scholarships`
- `players`
- `analytics`
- `accounts`

Relevant completed platform subsystems:

- Players V1
- Analytics V1
- Account Management V1
- Platform V1 Account Operations
- Evaluation Access V1

Current repository settings are environment-driven in the key deployment-specific places:

- `DEBUG` is controlled by `DJANGO_DEBUG`, defaulting to false
- `ALLOWED_HOSTS` is controlled by `DJANGO_ALLOWED_HOSTS`, defaulting to `localhost` and `127.0.0.1`
- `STATIC_URL = 'static/'`
- `STATIC_ROOT` is controlled by `DJANGO_STATIC_ROOT`, defaulting to `BASE_DIR / "staticfiles"`
- `MEDIA_ROOT` is controlled by `DJANGO_MEDIA_ROOT`, defaulting to `BASE_DIR / "media"`
- `SECRET_KEY` is required from `DJANGO_SECRET_KEY`
- account login is the default platform login
- both PDP forced-password middleware and Account Management forced-password middleware are installed

## Production Status

The production server is currently on:

```text
551dd0de458ba09628dc85183ef04f9e778fa98f
```

The production checkout has an uncommitted `vancouverminor/settings.py` modification containing production-specific domain and static-file settings.

Production also has untracked runtime files under `media/` and a local `venv/`. Those should be treated as server runtime data, not source code.

The production settings context provided for this review shows that production currently has:

- production hostnames configured in `ALLOWED_HOSTS`
- static URL and static root configured for the server
- media URL and media root configured
- SQLite database under the project directory
- old PDP login defaults
- only the older apps installed
- only PDP forced-password middleware installed
- a hardcoded Django secret key
- `DEBUG = True`

The production settings file is not reproduced here by design.

## Settings Comparison

### Must Preserve

These production-specific settings must be preserved or replaced with equivalent environment-driven configuration before deployment:

- production hostnames through `DJANGO_ALLOWED_HOSTS`
- existing static URL behavior, noting that this settings refactor intentionally leaves `STATIC_URL` unchanged
- production `STATIC_ROOT` through `DJANGO_STATIC_ROOT`
- existing `MEDIA_URL`
- existing `MEDIA_ROOT` through `DJANGO_MEDIA_ROOT`, unless a deliberate media migration is planned
- existing SQLite database path for the first rollout, unless a database migration plan is separately approved
- existing media files under production `media/`

### Must Change

These production settings are incompatible with the current repository or unsafe for production:

- The hardcoded Django secret key must be removed from production settings and replaced with `DJANGO_SECRET_KEY` in the process environment.
- The production secret must be rotated because the old committed secret should be treated as exposed.
- `INSTALLED_APPS` must include the current repository apps: `players`, `analytics`, and `accounts`.
- `MIDDLEWARE` must include `accounts.middleware.AccountPasswordChangeRequiredMiddleware` after Django authentication and after the existing PDP forced-password middleware.
- `LOGIN_URL` must point to the Account Management login route.
- `LOGIN_REDIRECT_URL` must point to the Account Management profile or platform landing route used by the current repository.
- Dependencies must match `requirements.txt`, including the current Django and Gunicorn versions.
- All new migrations must be applied.
- Static files must be collected against the configured `STATIC_ROOT`.

### Optional Improvements

These are recommended but should not block a first controlled rollout unless the deployment target requires them:

- Move any remaining server-local settings to environment variables or a separate untracked production settings module.
- Keep `DJANGO_DEBUG=false` with proper static/media serving and error handling.
- Add standard production security settings such as secure cookies and HTTPS proxy settings after confirming the Nginx/Gunicorn configuration.
- Add a documented deployment checklist or runbook.
- Add a staging rehearsal using a copy of production SQLite and media.

## Deployment Blockers

1. Production settings are not compatible with the current repository as-is.

   If production keeps the old settings, Django will not have `players`, `analytics`, and `accounts` installed. Current URLs and imported models depend on those apps. The application may fail to load URL patterns or fail at runtime when account, analytics, or player models are imported.

2. `DJANGO_SECRET_KEY` is required by the current repository.

   The current repository raises `ImproperlyConfigured` if `DJANGO_SECRET_KEY` is not set. Production currently uses a hardcoded secret in its local settings context. A new secret must be generated, stored outside Git, and loaded by the service manager before starting the upgraded app.

3. Production must preserve local host/static/media settings.

   The repository supports production host/static/media values through environment variables. Replacing production settings without setting those variables would fall back to local-development defaults and would not be appropriate for the public site.

4. The production database must be backed up before migrations.

   The upgrade introduces new tables and constraints for `players`, `analytics`, and `accounts`. These appear additive, but the production SQLite database must be backed up before applying migrations.

5. The deployment must account for login behavior changes.

   The current repository changes the platform login from PDP-centered routes to Account Management routes. Staff and user access expectations should be verified before production switch-over.

## Repository Blockers

The repository itself does not show an obvious code-level blocker from this review, but production must supply deployment environment variables before startup.

Repository-side concerns before production rollout:

- `DJANGO_SECRET_KEY` is required.
- `DJANGO_ALLOWED_HOSTS` must be set to production domains.
- `DJANGO_STATIC_ROOT` should be set to the path served by Nginx.
- `DJANGO_MEDIA_ROOT` should be set to the existing production media path if it differs from the default.
- `DJANGO_DEBUG` should remain false in production.

These are deployment configuration blockers, not application feature blockers.

## Production Settings Compatibility

### Installed Apps

Production currently lacks apps that the current repository requires:

- `players`
- `analytics`
- `accounts`

These apps were added after the production revision. Production settings must include them for the current repository to work.

### Middleware

Production currently has the legacy PDP forced-password middleware only.

The current repository requires both:

- PDP forced-password middleware for legacy PDP coexistence
- Account Management forced-password middleware for `accounts.AccountProfile.must_change_password`

Ordering should preserve the current repository order:

1. Django session middleware
2. common/csrf/authentication middleware
3. PDP forced-password middleware
4. Account Management forced-password middleware
5. messages/clickjacking middleware

The Account Management middleware depends on authenticated users and must remain after Django authentication middleware.

### Authentication Settings

Production currently uses PDP login defaults. The current repository uses Account Management login defaults.

The production upgrade must switch to the Account Management login settings because:

- imported player accounts use `accounts.AccountProfile`
- coach imports use `accounts`
- forced password change for new accounts is enforced through `accounts`
- staff Account Operations are under `/accounts/`
- Evaluation Access V1 assumes authenticated users and account roles from `accounts`

PDP routes can remain installed for legacy coexistence, but they should not remain the global login default after the upgrade.

### SECRET_KEY Handling

The current repository is compatible only if `DJANGO_SECRET_KEY` is set in the runtime environment.

The old production secret should be treated as exposed and rotated. Rotating the secret may invalidate existing sessions and password reset tokens. That is acceptable if planned, but staff should expect users to log in again after deployment.

### DEBUG

Production currently has `DEBUG = True`. The repository defaults `DEBUG` to false unless `DJANGO_DEBUG` is set to a true value.

This does not block a technical first rollout, but it is not production-grade. The recommended target is `DJANGO_DEBUG=false` after confirming:

- `ALLOWED_HOSTS` is correct
- static files are served by Nginx
- media files are served by Nginx or another approved mechanism
- error pages/logging are acceptable

If `DJANGO_DEBUG=true` remains necessary for a short first rollout, treat that as temporary technical debt.

### Static Files

Production has a server-specific `STATIC_ROOT`. The repository supports this through `DJANGO_STATIC_ROOT`.

The upgrade must preserve the production static root by setting `DJANGO_STATIC_ROOT` or configure an equivalent value. After code update and dependency install, run `collectstatic` before serving the upgraded app.

The Nginx configuration should serve from the same static root used by Django's `collectstatic`.

### Media Files

Production uses local media under the project path and has existing uploaded scholarship files.

The upgrade should preserve the media directory and avoid deleting untracked media files. Because the URL configuration only serves media through Django when `DEBUG` is true, production media serving should be confirmed at the Nginx level before setting `DEBUG = False`.

### Database

SQLite is acceptable for the first production rollout if the operational expectations remain modest and only a small staff/coach/player user base is expected initially.

PostgreSQL is not required before the first rollout based on the current code review. SQLite risks should be managed with:

- a database backup before deployment
- a brief maintenance window during migrations
- avoiding concurrent writes during migration
- monitoring write contention once account imports/evaluations begin

Move to PostgreSQL later if usage grows, concurrent write pressure increases, or operational backup/restore needs exceed SQLite comfort.

## Migration Review

Tracked migrations since the production revision include:

- `players/migrations/0001_initial.py`
- `players/migrations/0002_playerimportbatch_and_more.py`
- `analytics/migrations/0001_initial.py`
- `analytics/migrations/0002_seed_observation_defaults.py`
- `accounts/migrations/0001_initial.py`
- `accounts/migrations/0002_userplayerlink_and_more.py`

The reviewed migrations are primarily additive:

- new player identity tables
- player import batch/source/provenance tables
- analytics observation/question/evaluation tables
- seeded default analytics lookup data and questions
- account profile table
- user-player link table and constraints

No obvious destructive migration was found in the new V1 platform migrations. The main risk is not data deletion; it is applying a large set of new tables and constraints to a live SQLite database without a backup and maintenance window.

The existing older app migrations for `drafts`, `pdp`, `leaguehub`, and `scholarships` remain part of the project and should already be applied in production if those apps are operational.

## Deployment Risks

- Production settings drift could be overwritten accidentally by a direct `git pull` or checkout if server-local edits remain in tracked files.
- Missing `DJANGO_SECRET_KEY` would prevent Django from starting.
- Missing installed apps would cause current URLs/models to fail.
- Missing Account Management middleware would allow temporary-password users to bypass the new forced-password flow.
- Old login settings would send users to PDP instead of Account Management.
- Static files could fail if `DJANGO_STATIC_ROOT` and Nginx aliases do not match.
- Media files could become inaccessible if `DEBUG` is set false without Nginx media serving.
- SQLite migrations could lock the database during deployment.
- Secret rotation will invalidate existing sessions.
- Existing production untracked media must not be removed during cleanup.
- The production virtual environment may not match current `requirements.txt`.

## Required Production Changes

Before replacing production code with the current repository:

1. Back up the production SQLite database.
2. Back up the production media directory.
3. Save the current production settings diff outside the repo.
4. Generate a new Django secret key.
5. Configure the production service environment with `DJANGO_SECRET_KEY`.
6. Set `DJANGO_ALLOWED_HOSTS` to production domains.
7. Set `DJANGO_STATIC_ROOT` to the production static collection path.
8. Set `DJANGO_MEDIA_ROOT` to the existing production media path if needed.
9. Ensure `players`, `analytics`, and `accounts` are in `INSTALLED_APPS`.
10. Ensure Account Management middleware is installed in the current repository order.
11. Switch global login settings to Account Management routes.
12. Install current `requirements.txt` into the production virtual environment.
13. Run `python manage.py migrate` during a maintenance window.
14. Run `python manage.py collectstatic`.
15. Restart Gunicorn/systemd.
16. Verify staff login, account password change, account operations, player import, coach import, analytics command center, player evaluation submission, player "My Evaluations," coach evaluation review, draft routes, PDP routes, static assets, and media links.

## Optional Improvements

These improvements should be planned but do not have to block the first controlled upgrade:

- Create a dedicated production settings module only if the environment-variable settings layer becomes insufficient.
- Keep `DJANGO_DEBUG=false`.
- Add `CSRF_TRUSTED_ORIGINS` if required by the production domain/proxy setup.
- Add secure cookie settings after confirming HTTPS termination.
- Configure structured server logging.
- Add a deployment checklist under `docs/deployment/`.
- Rehearse deployment on a copy of the production database and media.
- Add a simple health-check URL if operational monitoring requires one.

## Recommended Deployment Sequence

This is a planning sequence, not an executable script.

1. Freeze production writes if practical.
2. Snapshot current production state:
   - Git commit hash
   - current production settings diff
   - SQLite database backup
   - media directory backup
   - current systemd/Gunicorn/Nginx configuration
3. Prepare production configuration:
   - set `DJANGO_SECRET_KEY`
   - set `DJANGO_ALLOWED_HOSTS`
   - set `DJANGO_STATIC_ROOT`
   - set `DJANGO_MEDIA_ROOT` if needed
   - confirm Account Management login and middleware settings
4. Stage the new code in a separate directory or release path if possible.
5. Install dependencies from `requirements.txt`.
6. Run `python manage.py check` with the production environment.
7. Run migrations against a copied production database first, if possible.
8. During maintenance window, run migrations against production database.
9. Run `collectstatic`.
10. Restart application service.
11. Smoke test critical flows:
    - public homepage
    - admin login
    - account login
    - forced password change
    - Account Operations dashboard
    - player import page
    - coach import page
    - analytics command center
    - evaluation submission
    - player "My Evaluations"
    - coach evaluation review
    - draft command center
    - PDP login/legacy route
    - scholarship media access
12. Monitor logs and user reports.

## Rollback Considerations

Rollback must account for database migrations.

Recommended rollback position:

- Keep a full pre-upgrade SQLite database backup.
- Keep a full pre-upgrade media backup.
- Keep the pre-upgrade production code checkout or release directory.
- Keep the old production service configuration available.

If deployment fails before migrations, rollback is likely a code/config revert.

If deployment fails after migrations, rollback should restore the pre-upgrade database backup before running the old code. Do not point old code at a database that has already been migrated for `players`, `analytics`, and `accounts` unless that compatibility has been explicitly tested.

Because the new migrations are additive, the upgraded database may still contain old app data safely, but old code will not know about new tables. The safest rollback remains database restore plus code restore.

Secret rotation rollback:

- Rotating the secret invalidates sessions.
- Rolling back the code does not necessarily require restoring the old secret, but doing so would reintroduce a known exposed secret.
- Prefer keeping the new secret and accepting session invalidation unless a specific compatibility issue is found.

## Final Go/No-Go Recommendation

Historical recommendation: **NO-GO for direct replacement by pulling then-current `main` over the production checkout.**

Historical recommendation: **GO for a planned deployment only after blockers were resolved.**

Required conditions for GO:

- production settings are supplied through environment variables without committing or reproducing production-only secrets
- `DJANGO_SECRET_KEY` is configured and rotated
- production domain/static/media settings are preserved through environment variables
- new apps and middleware are installed
- login settings are updated to Account Management
- dependencies are installed
- database and media are backed up
- migrations are rehearsed or at least reviewed with a rollback plan
- `collectstatic` and Nginx static/media serving are confirmed
- smoke-test checklist is ready

The repository can become the production codebase, but not by directly overwriting production settings or skipping migration/configuration preparation.

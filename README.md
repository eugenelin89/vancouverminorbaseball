# Vancouver Minor Baseball / VCB Platform

This repository contains the public Vancouver Minor Baseball website and the VCB Platform used for baseball operations.

The platform is intentionally lightweight:

- Django powers routing, templates, models, migrations, and staff workflows.
- Plain HTML/CSS keeps the user interface maintainable without frontend build tooling.
- Static assets live under `static/`.
- Operational subsystems use Django apps, service modules, templates, and tests.

## Current Platform

Installed platform areas include:

- `home`: public website pages, navigation, and content-driven page rendering.
- `players`: canonical player identity, imports, matching, provenance, aliases, and tags.
- `accounts`: authentication, account metadata, account operations, coach import, password workflows, and user-player links.
- `analytics`: evaluations, review workflows, command center summaries, player profiles, timelines, comparison, draft context, and reporting surfaces.
- `seasons`: season-aware teams, roster memberships, coach assignments, and evaluation context.
- `drafts`: staff-facing draft operations.
- `pdp`: legacy/transitionary player-development functionality that remains installed until an explicit migration or retirement plan is approved.
- `leaguehub` and `scholarships`: existing site/application areas that remain part of the project.

## Authoritative Documentation

Use these documents as the current source of truth:

- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- User workflows: [docs/USER_MANUAL.md](docs/USER_MANUAL.md)
- Deployment overview: [docs/deployment/README.md](docs/deployment/README.md)
- Deployment runbook: [docs/deployment/RUNBOOK.md](docs/deployment/RUNBOOK.md)
- Account Management V1: [docs/account_management/V1_SUMMARY.md](docs/account_management/V1_SUMMARY.md)
- Seasonal Participation V1: [docs/seasons/README.md](docs/seasons/README.md)
- Product planning: [docs/product/README.md](docs/product/README.md)
- Platform V2 roadmap: [docs/product/PLATFORM_V2_ROADMAP.md](docs/product/PLATFORM_V2_ROADMAP.md)
- Historical prompt archive: [docs/prompts/README.md](docs/prompts/README.md)
- Historical archive: [docs/archive/](docs/archive/)

Engineering plans under `docs/**/implementation/engineering/` are historical implementation records. They are useful for understanding why work was done, but current operational behavior should be checked against the architecture, user manual, deployment runbook, and subsystem summary documents above.

## Local Development

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set a local Django secret key. Use a development-only value locally, and never commit real secrets:

   ```bash
   export DJANGO_SECRET_KEY="replace-with-a-secure-random-value"
   ```

   You can generate a value with:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

4. Optional local environment settings:

   ```bash
   export DJANGO_DEBUG="true"
   export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
   ```

5. Apply migrations:

   ```bash
   python manage.py migrate
   ```

6. Run a project check:

   ```bash
   python manage.py check
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

Common test commands:

```bash
DJANGO_SECRET_KEY=test python manage.py test
DJANGO_SECRET_KEY=test python manage.py test accounts analytics players seasons drafts
```

## Development Tooling

Runtime dependencies are pinned in `requirements.txt`. Developer tooling is pinned separately in `requirements-dev.txt`.

Install development tools when you want local formatting, linting, or pre-commit checks:

```bash
pip install -r requirements-dev.txt
```

Repository-wide tooling configuration lives in:

- `pyproject.toml` for Black, isort, and Ruff settings.
- `.pre-commit-config.yaml` for pre-commit hook definitions.

Use conservative checks on files changed by the current task:

```bash
ruff check path/to/file.py
black --check path/to/file.py
isort --check-only path/to/file.py
pre-commit run --files path/to/file.py
```

Avoid whole-repository formatting unless the task explicitly calls for it. Prefer formatting only files that are already part of the current change. The repository now has shared tooling configuration, but historical Python files have not been bulk reformatted.

## Repository Structure

```text
accounts/                 Account management, authentication, operations, links, coach import
analytics/                Evaluation workflows, reporting surfaces, player experience
drafts/                   Draft workflows
home/                     Public website content and pages
leaguehub/                Existing LeagueHub app
pdp/                      Legacy/transitionary player-development app
players/                  Canonical player identity and imports
scholarships/             Existing scholarships app
seasons/                  Season-aware teams, rosters, assignments, context
static/                   CSS, images, and static source assets
templates/                Shared and app templates
docs/                     Architecture, user, deployment, product, and implementation docs
scripts/                  Maintenance/helper scripts
```

## Public Website Content

Most public website customization happens through data dictionaries and templates:

- `home/content.py` is the main source for navigation items, hero messaging, and public content cards.
- `templates/home/` renders the public pages.
- `static/css/styles.css` controls shared styling and responsive behavior.
- `static/images/` contains hero images, logos, and public artwork.
- `scripts/generate_placeholders.py` can regenerate placeholder imagery if Pillow is installed.

## Deployment

The root README is not the deployment runbook.

Use [docs/deployment/README.md](docs/deployment/README.md) for deployment policy and [docs/deployment/RUNBOOK.md](docs/deployment/RUNBOOK.md) for operational commands.

Production configuration belongs outside Git. Production should supply environment-specific values through the process manager or shell environment rather than editing tracked `vancouverminor/settings.py`.

Key environment variables:

- `DJANGO_SECRET_KEY` is required.
- `DJANGO_DEBUG` defaults to false.
- `COACH_IMPORT_DEFAULT_PASSWORD` is required before creating new coach accounts through coach import.
- `ANALYTICS_ASSESSMENTS_ENABLED` defaults to false. Set to `true` only after assessment templates/events have been configured and staff are ready to import assessment workbooks.
- `ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES` defaults to `10485760` (10 MiB) and may be lowered for assessment workbook uploads.
- `ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES` defaults to `52428800` (50 MiB) and caps expanded `.xlsx` archive content.
- `DJANGO_ALLOWED_HOSTS` defaults to `localhost,127.0.0.1`.
- `DJANGO_STATIC_ROOT` defaults to `BASE_DIR / "staticfiles"`.
- `DJANGO_MEDIA_ROOT` defaults to `BASE_DIR / "media"`.

Do not commit production secrets or server-local settings to Git.

## Project Snapshot Policy

Do not regenerate or update `project_flat_file.txt` during normal work. Treat it as an on-request artifact only.

Prompt archive records should store the user prompt and commit diffs, not full repository snapshots. If a full-project snapshot is explicitly requested, exclude dependency, generated, and cache directories such as `.git`, `.venv`, `__pycache__`, `node_modules`, `dist`, and `build`. Binary files should be represented by metadata and a short description rather than embedding their full contents.

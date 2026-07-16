# Prompt 81 - Platform

## User Prompt

Repository Cleanup Phase 1: Documentation Reconciliation.

Source prompt file:
`/Users/eugenelin/.codex/attachments/68834b16-fa44-40dc-87fa-e991305949cd/pasted-text.txt`

```text
Perform Repository Cleanup Phase 1 only: Documentation Reconciliation.

Use continuous loop engineering.

Continue until all current documentation is internally consistent, stale operational guidance has been removed or clearly marked historical, verification passes, commits are pushed, and the working tree is clean.

Do not change application behavior.

Do not modify Python code, models, migrations, services, views, forms, templates, URLs, settings, requirements, or tests except where documentation references them.

Do not begin dependency upgrades, lint tooling, or refactoring.

==================================================
Objective
=========

Seasonal Participation V1 has been completed, reviewed, frozen, and documented.

The documentation is generally excellent, but a repository-wide review identified several areas where documentation may no longer accurately reflect the current state of the project.

This phase is strictly a documentation reconciliation exercise.

The goal is to ensure there is exactly one authoritative source for every operational topic and that new developers (or future Codex sessions) cannot be misled by stale documentation.

==================================================
Repository Review
=================

Read at minimum:

* `AGENTS.md`
* `README.md`
* `docs/ARCHITECTURE.md`
* `docs/USER_MANUAL.md`
* `docs/deployment/README.md`
* `docs/deployment/RUNBOOK.md`
* `docs/product/README.md`
* `docs/product/PLATFORM_V2_ROADMAP.md`
* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`

Also review:

* subsystem README files
* deployment documentation
* completed engineering plans
* implementation summaries
* historical deployment records

Do **not** modify prompt archives except for creating the new prompt archive for this task.

==================================================
Required Review
===============

Review documentation for:

• stale deployment instructions

• stale local development instructions

• contradictory setup instructions

• duplicate operational procedures

• references to future work that is already complete

• references describing the system before Seasonal Participation V1

• broken internal links

• missing cross-links

• outdated terminology

• duplicate explanations

• documentation that should instead point to another authoritative document

==================================================
README Review
=============

Pay particular attention to `README.md`.

Determine whether it still contains:

* obsolete deployment examples
* obsolete server paths
* obsolete service names
* obsolete Linux usernames
* obsolete environment-variable instructions
* obsolete local setup instructions
* statements from when the project was much smaller

If so:

Update the README so that it reflects today's repository.

The README should become:

* project overview
* architecture overview
* quick local development setup
* repository structure
* links to detailed documentation

The README should **not** duplicate the production deployment runbook.

Instead, point readers to:

* `docs/deployment/README.md`
* `docs/deployment/RUNBOOK.md`

==================================================
Historical Documents
====================

Review completed engineering plans.

If a completed engineering plan could reasonably be mistaken for current operational documentation:

add a short historical notice near the beginning.

Example wording:

> Historical implementation record.
> This document reflects the design decisions, assumptions, and scope at the time this phase was executed.
> For current behavior, consult the subsystem README, Architecture document, User Manual, and Deployment Runbook.

Do **not** rewrite history.

Do **not** remove historical decisions.

Simply distinguish historical planning from current behavior.

==================================================
Authoritative Sources
=====================

Ensure there is only one authoritative location for each topic.

Examples:

Deployment:
→ Deployment Runbook

Architecture:
→ Architecture document

User workflows:
→ User Manual

Season implementation:
→ Seasonal Participation documentation

Product direction:
→ Platform V2 Roadmap

The README should link to these rather than duplicate them.

==================================================
Documentation Consistency
=========================

Ensure the following agree:

* README
* Architecture
* User Manual
* Deployment docs
* Seasonal docs
* Product roadmap

If the same workflow is described in multiple places:

keep one authoritative explanation.

Other documents should summarize and link.

==================================================
Scope Restrictions
==================

Do NOT:

* change application behavior
* add migrations
* refactor code
* update requirements
* add lint tools
* regenerate flat-file snapshots
* create deployment scripts
* modify tests
* modify Python code

Documentation only.

==================================================
Verification
============

Run:

git diff --check

If documentation validation already exists, run it.

Do not add new validation tooling.

==================================================
Acceptance Criteria
===================

Do not declare PASS until:

✓ README reflects the current platform

✓ stale deployment instructions removed

✓ local setup instructions are current

✓ deployment documentation has one authoritative location

✓ architecture documentation is consistent

✓ user documentation is consistent

✓ seasonal documentation is consistent

✓ product roadmap is consistent

✓ historical engineering plans are clearly distinguishable from current operational documentation where appropriate

✓ no broken documentation links remain

✓ git diff --check passes

✓ no application code changed

✓ implementation commit pushed

✓ prompt archive committed separately

✓ working tree clean

==================================================
Loop Workflow
=============

Every loop must:

1. review repository documentation
2. identify concrete inconsistencies
3. update documentation only
4. perform a senior documentation review
5. eliminate duplicate operational guidance
6. verify authoritative source ownership
7. run verification
8. commit documentation changes
9. archive the prompt according to AGENTS.md
10. commit the prompt archive separately
11. push both commits
12. confirm working tree clean
13. determine CONTINUE, PASS, BLOCKED, or NO_PROGRESS

If CONTINUE, immediately begin the next loop.

==================================================
Suggested Commit Message
========================

Reconcile repository documentation

==================================================
Final Report
============

Report:

* terminal state
* loops completed
* documentation reviewed
* files modified
* stale documentation removed
* authoritative source decisions
* historical notices added
* documentation consistency improvements
* verification performed
* commits
* push result
* confirmation that no application code changed
* confirmation that the working tree is clean
```

## Implementation Commit

`4a36059` - Reconcile repository documentation

## Commit Diff

```diff
commit 4a36059e53a7ec18348aae46a29b2af72512b699
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 16 02:38:48 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 16 02:38:48 2026 -0700

    Reconcile repository documentation
---
 README.md                                          | 396 +++++----------------
 docs/ARCHITECTURE.md                               |   6 +-
 .../engineering/phase_02_user_player_link.md       |   3 +
 .../phase_03_player_import_account_provisioning.md |   3 +
 ...ase_04_authentication_forced_password_change.md |   3 +
 .../engineering/platform_v1_account_operations.md  |   3 +
 .../engineering/phase_01_players_foundation.md     |   3 +
 .../engineering/phase_02_player_import_workflow.md |   3 +
 .../phase_03_analytics_observation_foundation.md   |   3 +
 .../phase_04_coach_assessment_workflow.md          |   3 +
 .../engineering/phase_06_player_experience.md      |   3 +
 .../engineering/phase_07_command_center.md         |   3 +
 docs/deployment/production_deployment_steps.md     |   5 +-
 .../engineering/evaluation_access_v1.md            |   3 +
 docs/product/PLATFORM_V2_ROADMAP.md                |   6 +-
 .../engineering/seasonal_participation_v1.md       |   3 +
 16 files changed, 142 insertions(+), 307 deletions(-)

diff --git a/README.md b/README.md
index e1598a0..f4d60f2 100644
--- a/README.md
+++ b/README.md
@@ -1,351 +1,145 @@
 # Vancouver Minor Baseball / VCB Platform
 
-This repository contains the public-facing Vancouver Minor Baseball site and the VCB Platform used for baseball operations.
+This repository contains the public Vancouver Minor Baseball website and the VCB Platform used for baseball operations.
 
-The project now also includes:
+The platform is intentionally lightweight:
 
-- `players`: canonical player identity, imports, matching, provenance, and tags
-- `accounts`: account management, authentication workflows, account operations, and user-player links
-- `analytics`: evaluations, review workflows, command center summaries, player profiles, timelines, comparison, and draft context
-- `drafts`: staff-facing draft operations
-- `pdp`: legacy/transitionary player-development functionality that remains installed until an explicit migration/retirement plan is approved
+- Django powers routing, templates, models, migrations, and staff workflows.
+- Plain HTML/CSS keeps the user interface maintainable without frontend build tooling.
+- Static assets live under `static/`.
+- Operational subsystems use Django apps, service modules, templates, and tests.
 
-Platform architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Legacy PDP notes live in [docs/archive/pdp.md](docs/archive/pdp.md).
+## Current Platform
 
-Platform product strategy lives in [docs/product/](docs/product/), including the [Platform V2 Roadmap](docs/product/PLATFORM_V2_ROADMAP.md).
+Installed platform areas include:
 
-The stack is intentionally lightweight:
+- `home`: public website pages, navigation, and content-driven page rendering.
+- `players`: canonical player identity, imports, matching, provenance, aliases, and tags.
+- `accounts`: authentication, account metadata, account operations, coach import, password workflows, and user-player links.
+- `analytics`: evaluations, review workflows, command center summaries, player profiles, timelines, comparison, draft context, and reporting surfaces.
+- `seasons`: season-aware teams, roster memberships, coach assignments, and evaluation context.
+- `drafts`: staff-facing draft operations.
+- `pdp`: legacy/transitionary player-development functionality that remains installed until an explicit migration or retirement plan is approved.
+- `leaguehub` and `scholarships`: existing site/application areas that remain part of the project.
 
-- **Django** powers templating and routing.
-- **Plain HTML/CSS** (no frontend build tooling) keeps the site easy to maintain.
-- **Static assets** (images, CSS) live under `static/`.
+## Authoritative Documentation
 
-For the public-facing home site, most content customization happens through data dictionaries and templates. Operational platform apps such as `accounts`, `players`, `analytics`, and `drafts` use Django models, migrations, services, and templates documented under `docs/`.
+Use these documents as the current source of truth:
 
----
+- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
+- User workflows: [docs/USER_MANUAL.md](docs/USER_MANUAL.md)
+- Deployment overview: [docs/deployment/README.md](docs/deployment/README.md)
+- Deployment runbook: [docs/deployment/RUNBOOK.md](docs/deployment/RUNBOOK.md)
+- Account Management V1: [docs/account_management/V1_SUMMARY.md](docs/account_management/V1_SUMMARY.md)
+- Seasonal Participation V1: [docs/seasons/README.md](docs/seasons/README.md)
+- Product planning: [docs/product/README.md](docs/product/README.md)
+- Platform V2 roadmap: [docs/product/PLATFORM_V2_ROADMAP.md](docs/product/PLATFORM_V2_ROADMAP.md)
+- Historical prompt archive: [docs/prompts/README.md](docs/prompts/README.md)
+- Historical archive: [docs/archive/](docs/archive/)
 
-## Public Site Layout
+Engineering plans under `docs/**/implementation/engineering/` are historical implementation records. They are useful for understanding why work was done, but current operational behavior should be checked against the architecture, user manual, deployment runbook, and subsystem summary documents above.
 
-```
-├── README.md                     # You are here
-├── home/
-│   ├── content.py                # Centralized static content + navigation config
-│   ├── urls.py                   # Route definitions, including generated placeholder pages
-│   └── views.py                  # Class-based views that feed templates their content
-├── scripts/
-│   └── generate_placeholders.py  # Utility to generate placeholder images (requires Pillow)
-├── static/
-│   ├── css/styles.css            # Global styling (baby-blue theme, layout, components)
-│   └── images/                   # Hero images, logos, highlight artwork
-└── templates/
-    ├── base.html                 # Shared HTML skeleton and stylesheet include
-    └── home/
-        ├── includes/
-        │   ├── site_header.html  # Header + navigation
-        │   ├── nav.html          # Recursive menu renderer
-        │   └── nav_script.html   # Shared navigation behavior script
-        ├── index.html            # Home page
-        ├── programs.html         # Programs page
-        ├── registration.html     # Registration page
-        └── page.html             # Placeholder page used for unimplemented routes
-```
+## Local Development
 
-### How Content Is Managed
+1. Create and activate a virtual environment.
+2. Install dependencies:
 
-- **`home/content.py`** is the single source of truth for navigation items, hero messaging, and card content. Updating the site typically means editing this file rather than the templates.
-  - `NAVIGATION` drives the header menu.
-  - `HERO`, `PROGRAMS_PAGE`, and `REGISTRATION_PAGE` feed the hero sections and content cards.
-  - `ACHIEVEMENTS` supplies the highlight cards on the home page.
-- **Templates** read those dictionaries and render markup. Minimal presentation logic lives inside the templates to keep them declarative.
-- **CSS** in `static/css/styles.css` controls theme colors, layout, and responsive behavior. It’s safe to extend existing utility classes or add section-specific styles as needed.
-- **Placeholder pages**: unknown slugs picked up by navigation automatically render via `templates/home/page.html`, which keeps the navigation functional until bespoke pages are added.
-- **Images**: hero assets follow a naming convention (`vmb_hero-banner.jpg`, `programs-hero.jpg`, `registration-hero.jpg`). Update the files under `static/images/` and ensure filenames match what `home/content.py` expects.
-
----
+   ```bash
+   pip install -r requirements.txt
+   ```
 
-## Local Development Basics
+3. Set a local Django secret key. Use a development-only value locally, and never commit real secrets:
 
-1. Create and activate a virtual environment (Python 3.10+ recommended).
-2. Install dependencies (if you add a `requirements.txt`, install from there).
-3. Set a local Django secret key in your shell. Use a development-only value locally, and never commit real secrets:
    ```bash
    export DJANGO_SECRET_KEY="replace-with-a-secure-random-value"
    ```
-   You can generate a secure value locally with:
+
+   You can generate a value with:
+
    ```bash
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    ```
-   If you use a local `.env` file for your shell tooling, keep it untracked. `.env.example` shows the required variable name without containing a real secret.
-4. Run migrations if/when models are introduced.
-5. Start the dev server:
-   ```bash
-   python manage.py runserver
-   ```
-6. Optional – regenerate placeholder imagery:
-   ```bash
-   pip install Pillow
-   python scripts/generate_placeholders.py
-   ```
-
-Because the site is mostly static, productivity comes from editing `content.py` and refreshing the browser.
-
----
-
-## Project Snapshot Policy
-
-Do not regenerate or update `project_flat_file.txt` during normal work. Treat it as an on-request artifact only.
-
-Prompt archive records should store the user prompt and commit diffs, not full repository snapshots. If a full-project snapshot is explicitly requested, exclude dependency, generated, and cache directories such as `.git`, `.venv`, `__pycache__`, `node_modules`, `dist`, and `build`. Binary files should be represented by metadata and a short description rather than embedding their full contents.
-
----
-
-## Deployment Configuration
-
-Environment-specific configuration should be provided through environment variables rather than by editing `vancouverminor/settings.py` on the server.
-
-Required:
-
-```bash
-DJANGO_SECRET_KEY="replace-with-a-secure-random-value"
-```
-
-Optional:
-
-```bash
-DJANGO_DEBUG="false"
-DJANGO_ALLOWED_HOSTS="vancouverminor.com,www.vancouverminor.com"
-DJANGO_STATIC_ROOT="/var/www/vancouverminorbaseball/staticfiles"
-DJANGO_MEDIA_ROOT="/var/www/vancouverminorbaseball/media"
-```
-
-Notes:
-
-- `DJANGO_SECRET_KEY` is required. Django will not start without it.
-- `DJANGO_DEBUG` accepts `true`, `1`, `yes`, or `on` as true. Any other value is false. The default is false.
-- `DJANGO_ALLOWED_HOSTS` is comma-separated. Whitespace is trimmed. The default is `localhost,127.0.0.1`.
-- `DJANGO_STATIC_ROOT` defaults to `BASE_DIR / "staticfiles"`.
-- `DJANGO_MEDIA_ROOT` defaults to `BASE_DIR / "media"`.
-
-Production should configure these values through the process manager or shell environment, such as systemd, Apache, Nginx plus Gunicorn, or another deployment supervisor. Do not commit production secrets or server-local settings to Git.
-
----
-
-## Production Deployment on DigitalOcean (Ubuntu 20.04+)
-
-The following steps assume you already operate other subdomains (e.g. `dev.vancouverminor.com`) on the same Droplet and that this application should serve the apex domain at `https://vancouverminor.com`. Adjust paths and names to suit your environment.
-
-### 1. Prepare the Server
-
-SSH into the Droplet:
-
-```bash
-ssh user@your-droplet-ip
-```
-
-Update packages:
-
-```bash
-sudo apt update && sudo apt upgrade
-```
-
-Install required system packages:
-
-```bash
-sudo apt install python3-pip python3-venv python3-dev build-essential \
-                 nginx git ufw
-```
-
-### 2. Clone the Repository
-
-Decide on a base path for web apps, e.g. `/var/www/vancouverminor`.
-
-```bash
-sudo mkdir -p /var/www/vancouverminor
-sudo chown $USER:$USER /var/www/vancouverminor
-cd /var/www/vancouverminor
-git clone <your-repo-url> website
-```
 
-### 3. Set Up the Virtual Environment
+4. Optional local environment settings:
 
-```bash
-cd website
-python3 -m venv venv
-source venv/bin/activate
-pip install --upgrade pip
-pip install -r requirements.txt   # create this file if it doesn't already exist
-```
-
-Collect static files (configure `STATIC_ROOT` in `settings.py` first):
-
-```bash
-python manage.py collectstatic
-```
-
-Run database migrations when applicable:
-
-```bash
-python manage.py migrate
-```
-
-Create an admin user if needed:
-
-```bash
-python manage.py createsuperuser
-```
-
-### 4. Configure Gunicorn
-
-Install Gunicorn inside the virtual environment:
-
-```bash
-pip install gunicorn
-```
-
-Test that Gunicorn can serve the project:
-
-```bash
-gunicorn --bind 0.0.0.0:8000 vancouverminor.wsgi
-```
-
-If successful, stop the test with `Ctrl+C`.
-
-Create a systemd service file, e.g. `/etc/systemd/system/vancouverminor.service`:
-
-```ini
-[Unit]
-Description=Gunicorn instance for vancouverminor.com
-After=network.target
-
-[Service]
-User=www-data
-Group=www-data
-WorkingDirectory=/var/www/vancouverminor/website
-Environment="PATH=/var/www/vancouverminor/website/venv/bin"
-Environment="DJANGO_SECRET_KEY=replace-with-a-secure-random-value"
-Environment="DJANGO_DEBUG=false"
-Environment="DJANGO_ALLOWED_HOSTS=vancouverminor.com,www.vancouverminor.com"
-Environment="DJANGO_STATIC_ROOT=/var/www/vancouverminor/website/staticfiles"
-Environment="DJANGO_MEDIA_ROOT=/var/www/vancouverminor/website/media"
-ExecStart=/var/www/vancouverminor/website/venv/bin/gunicorn \
-          --workers 3 \
-          --bind unix:/var/www/vancouverminor/website/vancouverminor.sock \
-          vancouverminor.wsgi:application
-Restart=always
-
-[Install]
-WantedBy=multi-user.target
-```
-
-Reload systemd and enable the service:
-
-```bash
-sudo systemctl daemon-reload
-sudo systemctl enable --now vancouverminor
-sudo systemctl status vancouverminor
-```
-
-Use a real secure random value for `DJANGO_SECRET_KEY` in production. The previously committed development key must be treated as exposed and rotated in any deployed environment that used it. Do not commit production secrets to Git.
-
-### 5. Configure Nginx
-
-Create a new server block `/etc/nginx/sites-available/vancouverminor.com`:
-
-```nginx
-server {
-    listen 80;
-    server_name vancouverminor.com www.vancouverminor.com;
-
-    location = /favicon.ico { access_log off; log_not_found off; }
+   ```bash
+   export DJANGO_DEBUG="true"
+   export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
+   ```
 
-    location /static/ {
-        alias /var/www/vancouverminor/website/static/;
-    }
+5. Apply migrations:
 
-    location / {
-        include proxy_params;
-        proxy_pass http://unix:/var/www/vancouverminor/website/vancouverminor.sock;
-    }
-}
-```
+   ```bash
+   python manage.py migrate
+   ```
 
-Enable the site and test:
+6. Run a project check:
 
-```bash
-sudo ln -s /etc/nginx/sites-available/vancouverminor.com /etc/nginx/sites-enabled/
-sudo nginx -t
-sudo systemctl reload nginx
-```
+   ```bash
+   python manage.py check
+   ```
 
+7. Start the development server:
 
-### 6. Obtain HTTPS with Let’s Encrypt
+   ```bash
+   python manage.py runserver
+   ```
 
-Ensure the `snapd` version of Certbot is installed:
+Common test commands:
 
 ```bash
-sudo snap install core
-sudo snap refresh core
-sudo snap install --classic certbot
-sudo ln -s /snap/bin/certbot /usr/bin/certbot
+DJANGO_SECRET_KEY=test python manage.py test
+DJANGO_SECRET_KEY=test python manage.py test accounts analytics players seasons drafts
 ```
 
-Run Certbot using the Nginx plugin (this will edit the server block to listen on 443 and configure redirects):
+## Repository Structure
 
-```bash
-sudo certbot --nginx -d vancouverminor.com -d www.vancouverminor.com
+```text
+accounts/                 Account management, authentication, operations, links, coach import
+analytics/                Evaluation workflows, reporting surfaces, player experience
+drafts/                   Draft workflows
+home/                     Public website content and pages
+leaguehub/                Existing LeagueHub app
+pdp/                      Legacy/transitionary player-development app
+players/                  Canonical player identity and imports
+scholarships/             Existing scholarships app
+seasons/                  Season-aware teams, rosters, assignments, context
+static/                   CSS, images, and static source assets
+templates/                Shared and app templates
+docs/                     Architecture, user, deployment, product, and implementation docs
+scripts/                  Maintenance/helper scripts
 ```
 
-Follow the prompts. Certbot will create the necessary certificates and update the Nginx config.
-
-Automatic renewal runs via systemd. Test renewal:
-
-```bash
-sudo certbot renew --dry-run
-```
+## Public Website Content
 
-### 7. Integrate with Existing Subdomains
+Most public website customization happens through data dictionaries and templates:
 
-Because the apex domain shares infrastructure with other subdomains:
+- `home/content.py` is the main source for navigation items, hero messaging, and public content cards.
+- `templates/home/` renders the public pages.
+- `static/css/styles.css` controls shared styling and responsive behavior.
+- `static/images/` contains hero images, logos, and public artwork.
+- `scripts/generate_placeholders.py` can regenerate placeholder imagery if Pillow is installed.
 
-- Each app should have its own systemd service, socket, static root, and Nginx server block.
-- Ensure DNS has `A` / `CNAME` records for both `vancouverminor.com` and `www.vancouverminor.com` pointing to the Droplet’s IP. Keep existing records for subdomains like `dev.vancouverminor.com`.
-- To avoid certificate rate limits, only request certificates for subdomains that will serve traffic.
-- Keep firewall rules permissive for HTTP/HTTPS (e.g. `sudo ufw allow 'Nginx Full'`).
+## Deployment
 
-### 8. Ongoing Maintenance
+The root README is not the deployment runbook.
 
-- **Deploy updates**: pull latest changes, reinstall dependencies if needed, re-run `collectstatic`, then restart Gunicorn:
-  ```bash
-  cd /var/www/vancouverminor/website
-  source venv/bin/activate
-  git pull origin main
-  pip install -r requirements.txt
-  python manage.py collectstatic
-  sudo systemctl restart home-site
-  ```
-- **Monitor logs**:
-  ```bash
-  sudo journalctl -u home-site -f
-  sudo tail -f /var/log/nginx/home.vancouverminor.com.error.log
-  ```
-- **Rotate assets**: update hero images under `static/images/` and re-run `collectstatic`.
+Use [docs/deployment/README.md](docs/deployment/README.md) for deployment policy and [docs/deployment/RUNBOOK.md](docs/deployment/RUNBOOK.md) for operational commands.
 
----
+Production configuration belongs outside Git. Production should supply environment-specific values through the process manager or shell environment rather than editing tracked `vancouverminor/settings.py`.
 
-## Contributing Guidelines
+Key environment variables:
 
-1. Work from feature branches, keep PRs focused.
-2. Update `home/content.py` for text/navigation changes; reflect any structural modifications in templates.
-3. Run through the site on mobile and desktop whenever you touch CSS.
-4. Document any new deployment steps in this README so future developers stay aligned.
+- `DJANGO_SECRET_KEY` is required.
+- `DJANGO_DEBUG` defaults to false.
+- `DJANGO_ALLOWED_HOSTS` defaults to `localhost,127.0.0.1`.
+- `DJANGO_STATIC_ROOT` defaults to `BASE_DIR / "staticfiles"`.
+- `DJANGO_MEDIA_ROOT` defaults to `BASE_DIR / "media"`.
 
-## Prompt Archive
+Do not commit production secrets or server-local settings to Git.
 
-Historical and reusable Codex prompts live in [docs/prompts/](docs/prompts/).
+## Project Snapshot Policy
 
-- Name prompt files with the format `prompt_[ID]_[app_name].md`.
-- Use the next unused zero-padded integer ID.
-- Use `platform` when a prompt spans multiple subsystems.
-- Treat prompt files as historical execution records; current architecture and user guidance live under `docs/`.
+Do not regenerate or update `project_flat_file.txt` during normal work. Treat it as an on-request artifact only.
 
-With this structure and deployment workflow, future developers can maintain the public site and the VCB Platform from the same repository.
+Prompt archive records should store the user prompt and commit diffs, not full repository snapshots. If a full-project snapshot is explicitly requested, exclude dependency, generated, and cache directories such as `.git`, `.venv`, `__pycache__`, `node_modules`, `dist`, and `build`. Binary files should be represented by metadata and a short description rather than embedding their full contents.
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 3a3ac29..02dcb14 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -256,7 +256,7 @@ PDP retirement requires a dedicated migration and regression plan. Do not remove
 
 Documentation:
 
-- [PDP Notes](pdp.md)
+- [PDP Notes](archive/pdp.md)
 
 ## Ownership Matrix
 
@@ -408,8 +408,8 @@ Drafts:
 
 PDP:
 
-- [PDP Notes](pdp.md)
-- [PDP Import Discovery Log](pdp_import_discovery_log.md)
+- [PDP Notes](archive/pdp.md)
+- [PDP Import Discovery Log](archive/pdp_import_discovery_log.md)
 
 Future documentation areas:
 
diff --git a/docs/account_management/implementation/engineering/phase_02_user_player_link.md b/docs/account_management/implementation/engineering/phase_02_user_player_link.md
index b3aa668..820de93 100644
--- a/docs/account_management/implementation/engineering/phase_02_user_player_link.md
+++ b/docs/account_management/implementation/engineering/phase_02_user_player_link.md
@@ -1,5 +1,8 @@
 # Account Management v1 Phase 2 Engineering Plan: User Player Linking
 
+> Historical implementation record.
+> This document preserves the plan and decisions used during implementation. For current Account Management behavior, use [../../V1_SUMMARY.md](../../V1_SUMMARY.md), [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), and [../../../USER_MANUAL.md](../../../USER_MANUAL.md).
+
 ## Phase Goal
 
 Create the foundation for linking Django `User` accounts to canonical `players.Player` records.
diff --git a/docs/account_management/implementation/engineering/phase_03_player_import_account_provisioning.md b/docs/account_management/implementation/engineering/phase_03_player_import_account_provisioning.md
index 53f6731..13bff0e 100644
--- a/docs/account_management/implementation/engineering/phase_03_player_import_account_provisioning.md
+++ b/docs/account_management/implementation/engineering/phase_03_player_import_account_provisioning.md
@@ -1,5 +1,8 @@
 # Account Management v1 Phase 3 Engineering Plan: Player Import Account Provisioning
 
+> Historical implementation record.
+> This document preserves the plan and decisions used during implementation. For current Account Management behavior, use [../../V1_SUMMARY.md](../../V1_SUMMARY.md), [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), and [../../../USER_MANUAL.md](../../../USER_MANUAL.md).
+
 ## Phase Goal
 
 Allow staff/admin player imports to optionally provision linked Django login accounts for committed `players.Player` records.
diff --git a/docs/account_management/implementation/engineering/phase_04_authentication_forced_password_change.md b/docs/account_management/implementation/engineering/phase_04_authentication_forced_password_change.md
index b3c0bea..c86ada2 100644
--- a/docs/account_management/implementation/engineering/phase_04_authentication_forced_password_change.md
+++ b/docs/account_management/implementation/engineering/phase_04_authentication_forced_password_change.md
@@ -1,5 +1,8 @@
 # Account Management v1 Phase 4 Engineering Plan: Authentication and Forced Password Change
 
+> Historical implementation record.
+> This document preserves the plan and decisions used during implementation. For current Account Management behavior, use [../../V1_SUMMARY.md](../../V1_SUMMARY.md), [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), and [../../../USER_MANUAL.md](../../../USER_MANUAL.md).
+
 ## Phase Goal
 
 Define the platform-forward authentication flow for Account Management v1 and enforce password changes for users with `accounts.AccountProfile.must_change_password=True`.
diff --git a/docs/account_management/implementation/engineering/platform_v1_account_operations.md b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
index b7f92b8..b9e48b9 100644
--- a/docs/account_management/implementation/engineering/platform_v1_account_operations.md
+++ b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
@@ -1,5 +1,8 @@
 # Platform V1 Account Operations Engineering Plan
 
+> Historical implementation record.
+> This document preserves the plan and decisions used to implement Platform V1 Account Operations. For current behavior, use [../../V1_SUMMARY.md](../../V1_SUMMARY.md), [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), and [../../../USER_MANUAL.md](../../../USER_MANUAL.md).
+
 ## 1. Objectives
 
 Players V1, Analytics V1, Account Management V1, Platform V1 Account Operations, and the platform architecture documentation are complete and frozen. This document records the operational account-management plan that was used to complete the staff-facing production workflows for managing accounts, links, passwords, and bulk account actions.
diff --git a/docs/analytics/implementation/engineering/phase_01_players_foundation.md b/docs/analytics/implementation/engineering/phase_01_players_foundation.md
index 4a5e5f9..e558e07 100644
--- a/docs/analytics/implementation/engineering/phase_01_players_foundation.md
+++ b/docs/analytics/implementation/engineering/phase_01_players_foundation.md
@@ -1,5 +1,8 @@
 # Phase 1 Engineering Plan: Players Foundation
 
+> Historical implementation record.
+> This document preserves the plan and decisions used during implementation. For current behavior, use [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the relevant subsystem summaries.
+
 ## Overview
 
 Phase 1 creates the independent `players` app as the canonical future player identity foundation for Analytics and future VCB systems.
diff --git a/docs/analytics/implementation/engineering/phase_02_player_import_workflow.md b/docs/analytics/implementation/engineering/phase_02_player_import_workflow.md
index 769a1b4..b6fa26b 100644
--- a/docs/analytics/implementation/engineering/phase_02_player_import_workflow.md
+++ b/docs/analytics/implementation/engineering/phase_02_player_import_workflow.md
@@ -1,5 +1,8 @@
 # Phase 2 Engineering Plan: Player Import Workflow
 
+> Historical implementation record.
+> This document preserves the plan and decisions used during implementation. For current behavior, use [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the relevant subsystem summaries.
+
 ## Overview
 
 Phase 2 builds the staff/admin player import workflow that turns roster/member CSV files into canonical `players.Player` records with conservative matching, preview, conflict review, and provenance.
diff --git a/docs/analytics/implementation/engineering/phase_03_analytics_observation_foundation.md b/docs/analytics/implementation/engineering/phase_03_analytics_observation_foundation.md
index 17e6d90..acb8430 100644
--- a/docs/analytics/implementation/engineering/phase_03_analytics_observation_foundation.md
+++ b/docs/analytics/implementation/engineering/phase_03_analytics_observation_foundation.md
@@ -1,5 +1,8 @@
 # Phase 3 Engineering Plan: Analytics Observation Foundation
 
+> Historical implementation record.
+> This document preserves the plan and decisions used during implementation. For current behavior, use [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the relevant subsystem summaries.
+
 ## Overview
 
 Phase 3 creates the Analytics observation foundation required for Version 1 coach assessments.
diff --git a/docs/analytics/implementation/engineering/phase_04_coach_assessment_workflow.md b/docs/analytics/implementation/engineering/phase_04_coach_assessment_workflow.md
index c2c0eaa..c519819 100644
--- a/docs/analytics/implementation/engineering/phase_04_coach_assessment_workflow.md
+++ b/docs/analytics/implementation/engineering/phase_04_coach_assessment_workflow.md
@@ -1,5 +1,8 @@
 # Phase 4 Engineering Plan: Coach Assessment Workflow
 
+> Historical implementation record.
+> This document preserves the plan and decisions used during implementation. For current behavior, use [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the relevant subsystem summaries.
+
 ## Overview
 
 Phase 4 implements the Version 1 coach assessment workflow on top of the completed Phase 3 observation foundation.
diff --git a/docs/analytics/implementation/engineering/phase_06_player_experience.md b/docs/analytics/implementation/engineering/phase_06_player_experience.md
index 2d81d4a..97f4a18 100644
--- a/docs/analytics/implementation/engineering/phase_06_player_experience.md
+++ b/docs/analytics/implementation/engineering/phase_06_player_experience.md
@@ -1,5 +1,8 @@
 # Phase 6 Engineering Plan: Player Experience
 
+> Historical implementation record.
+> This document preserves the plan and decisions used during implementation. For current behavior, use [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the relevant subsystem summaries.
+
 ## Phase Goal
 
 Create the practical staff-facing player experience for Version 1 of Analytics:
diff --git a/docs/analytics/implementation/engineering/phase_07_command_center.md b/docs/analytics/implementation/engineering/phase_07_command_center.md
index d39c702..46cc478 100644
--- a/docs/analytics/implementation/engineering/phase_07_command_center.md
+++ b/docs/analytics/implementation/engineering/phase_07_command_center.md
@@ -1,5 +1,8 @@
 # Phase 7 Engineering Plan: Command Center And Reporting
 
+> Historical implementation record.
+> This document preserves the plan and decisions used during implementation. For current behavior, use [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the relevant subsystem summaries.
+
 ## Phase Goal
 
 Provide staff/admin users with the Version 1 Analytics Command Center and simple reporting summaries.
diff --git a/docs/deployment/production_deployment_steps.md b/docs/deployment/production_deployment_steps.md
index ce7ceff..f9b0b65 100644
--- a/docs/deployment/production_deployment_steps.md
+++ b/docs/deployment/production_deployment_steps.md
@@ -1,5 +1,8 @@
 # Updating Production
 
+> Historical helper.
+> This file preserves an earlier deployment checklist. The authoritative deployment process is [RUNBOOK.md](RUNBOOK.md). Use the runbook for current production deployments and treat this file as historical context only.
+
 ## 1. Become the deployment user
 
 ```bash
@@ -144,4 +147,4 @@ They will fail because the production environment variables are stored in:
 /etc/vancouverminorbaseball.env
 ```
 
-Always use the wrapped commands shown above.
\ No newline at end of file
+Always use the wrapped commands shown above.
diff --git a/docs/evaluations/implementation/engineering/evaluation_access_v1.md b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
index 0ef52a6..e7e96d4 100644
--- a/docs/evaluations/implementation/engineering/evaluation_access_v1.md
+++ b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
@@ -1,5 +1,8 @@
 # Evaluation Access V1 Engineering Plan
 
+> Historical implementation record.
+> This document preserves the plan and decisions used to implement Evaluation Access V1. For current behavior, use [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the relevant subsystem summaries.
+
 Status: COMPLETE and FROZEN.
 
 Frozen on: 2026-07-10.
diff --git a/docs/product/PLATFORM_V2_ROADMAP.md b/docs/product/PLATFORM_V2_ROADMAP.md
index 3bd083a..f6d15eb 100644
--- a/docs/product/PLATFORM_V2_ROADMAP.md
+++ b/docs/product/PLATFORM_V2_ROADMAP.md
@@ -2,7 +2,7 @@
 
 ## 1. Executive Summary
 
-Platform V1 is the stable operational foundation for the VCB Platform. It supports player identity, imports, account management, authentication, user-player links, coach import, evaluations, player My Evaluations, coach review, staff review, Analytics Command Center, player search/profile/timeline/comparison, draft context, draft workflows, deployment documentation, and role-based user documentation.
+Platform V1 is the stable operational foundation for the VCB Platform. It supports player identity, imports, account management, authentication, user-player links, coach import, season-aware roster participation, evaluations, player My Evaluations, coach review, staff review, Analytics Command Center, player search/profile/timeline/comparison, draft context, draft workflows, deployment documentation, and role-based user documentation.
 
 The recommended next product milestone is:
 
@@ -10,7 +10,7 @@ The recommended next product milestone is:
 Platform V2: Player Development Intelligence
 ```
 
-Before deeper player-development intelligence work, the platform needs season-aware roster participation so permanent players and coach accounts can be reused across seasons while evaluations retain historical team/division context. See [Seasonal Participation V1 Engineering Plan](../seasons/implementation/engineering/seasonal_participation_v1.md).
+Seasonal Participation V1 is complete and frozen. It allows permanent players and coach accounts to be reused across seasons while evaluations retain historical team/division context. See [Seasonal Participation V1](../seasons/README.md).
 
 Platform V2 should turn collected evaluation data into useful player-development decision support. It should not begin with large dashboards, AI, rankings, or parent-facing raw data. The next immediate activity should be a real-world pilot using the completed Platform V1 workflows. Product decisions for Platform V2 should be driven by pilot evidence, data quality, privacy requirements, and user value.
 
@@ -29,6 +29,7 @@ Platform V1 currently includes:
 - canonical player identity and player records;
 - player CSV import and player account provisioning;
 - coach account import;
+- season-aware teams, player roster memberships, coach assignments, and evaluation context;
 - account management and Account Operations;
 - user-player relationships;
 - authentication and forced password change;
@@ -49,6 +50,7 @@ Current subsystem ownership remains:
 
 - `accounts` owns authentication, account metadata, roles, links, provisioning, and account operations.
 - `players` owns canonical player identity, player imports, matching, and player provenance.
+- `seasons` owns season-aware teams, player roster memberships, coach assignments, and roster context.
 - `analytics` owns observations, evaluation cycles, responses, evaluator snapshots, perspective snapshots, metrics, timelines, comparisons, command center summaries, and reporting surfaces.
 - `drafts` owns draft workflows and draft actions.
 - `pdp` remains legacy/transitionary.
diff --git a/docs/seasons/implementation/engineering/seasonal_participation_v1.md b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
index ffd96a2..f73e410 100644
--- a/docs/seasons/implementation/engineering/seasonal_participation_v1.md
+++ b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
@@ -1,5 +1,8 @@
 # Seasonal Participation V1 Engineering Plan
 
+> Historical implementation record.
+> This document preserves the plan and decisions used to implement Seasonal Participation V1. For current behavior, use [../../README.md](../../README.md), [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the deployment runbook.
+
 Status: Seasonal Participation V1 is Feature Complete, Production Ready, and Frozen. Phase 1 foundation, Phase 2 season-aware player import, Phase 3 season-aware coach import, Phase 4 season-aware evaluation context, Phase 5 season and roster operations UI, and Phase 6 production review/freeze are complete.
 
 Created: 2026-07-15.
```

## Verification

- Local Markdown link sanity check outside prompt archives: passed.
- `git diff --check`: passed before the documentation commit.
- Application tests were not run because this was a documentation-only reconciliation task.

## Terminal State

PASS

# Analytics Local Development And Testing

This document covers local setup and smoke testing for the Analytics subsystem.

Run all commands from the repository root:

```bash
cd /Users/eugenelin/dev/vmba0
```

## First-Time Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Create a staff/admin user if needed:

```bash
python manage.py createsuperuser
```

## Run Locally

Start the Django development server:

```bash
python manage.py runserver
```

Open the Analytics Command Center:

```text
http://127.0.0.1:8000/analytics/
```

Analytics V1 is staff-only. Log in with a staff/admin user.

Admin is available at:

```text
http://127.0.0.1:8000/admin/
```

The project uses local SQLite by default at `db.sqlite3`, so `python manage.py migrate` is enough for local database setup.

No frontend build step is required.

## Analytics UI Smoke Test

After logging in as staff, check these pages:

```text
/analytics/
/analytics/imports/
/analytics/players/
/analytics/players/compare/
/analytics/assessments/
/analytics/observations/review/
```

## Verification Commands

Use these commands before considering Analytics work complete:

```bash
python manage.py check
python manage.py makemigrations analytics --check
python manage.py test analytics
python manage.py test players
python manage.py test drafts
python manage.py test
```

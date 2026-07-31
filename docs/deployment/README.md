# Deployment Documentation

This folder contains the permanent deployment documentation for the Vancouver Minor Baseball platform.

## Deployment Philosophy

Deployment configuration belongs outside Git.

The tracked repository should contain application code, migrations, templates, static source files, and documentation. Production-only values such as secrets, hostnames, static roots, media roots, and debug settings should be supplied through the production environment.

Current production uses:

- tracked `vancouverminor/settings.py`;
- systemd-managed environment variables;
- `/etc/vancouverminorbaseball.env` for production configuration;
- SQLite for the current production database;
- Gunicorn behind the production web server.

Do not keep permanent production-only edits in tracked files.

## Deployment Workflow

Standard deployment flow:

1. Review the intended release.
2. Record the current production Git commit.
3. Back up SQLite.
4. Archive production media.
5. Verify production environment configuration.
6. Update the repository.
7. Verify dependencies.
8. Run Django checks and migration checks.
9. Apply migrations.
10. Collect static files.
11. Restart Gunicorn.
12. Smoke test public and authenticated routes.
13. Verify logs.

Use the operational runbook for step-by-step commands and checks:

- [Deployment Runbook](RUNBOOK.md)

## Deployment History

Historical deployment records:

- [Production Deployment - 2026-07-11](production_deployment_2026_07_11.md)

## Planning And Readiness

Pre-deployment review documentation:

- [Production Readiness Review](production_readiness_review.md)

Seasonal Participation V1 production rollout and browser verification steps are maintained in the [Deployment Runbook](RUNBOOK.md#seasonal-participation-v1-rollout).

## Operational Standard

Future production deployments should:

- avoid production-only edits to tracked files;
- keep secrets out of Git;
- use environment variables for deployment-specific settings;
- configure `COACH_IMPORT_DEFAULT_PASSWORD` before creating new imported coach accounts;
- enable `ANALYTICS_ASSESSMENTS_ENABLED` only for staged rollout of workbook assessment imports;
- retain conservative `ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES` and `ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES` limits;
- back up the database before migrations;
- archive media before major upgrades;
- verify migrations before applying them;
- restart and inspect Gunicorn after deployment;
- perform smoke tests before considering the release complete.

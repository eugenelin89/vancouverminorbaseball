# Repository Assessment

## Purpose

This document records the existing Django repository conventions before Analytics Phase 1 implementation begins.

Use this assessment to make the Analytics and `players` work fit the current project instead of treating it as a greenfield Django codebase. This document is implementation guidance only; architecture decisions remain in the Analytics Architecture Handbook.

## Existing Django Project Structure

The Django project package is `vancouverminor`.

Project-level files and folders:

- `manage.py`
- `vancouverminor/settings.py`
- `vancouverminor/urls.py`
- `vancouverminor/asgi.py`
- `vancouverminor/wsgi.py`
- `templates/` for project-level templates.
- `static/` for shared static assets.
- `media/` for uploaded files during local development.
- App folders at the repository root: `home`, `drafts`, `pdp`, `leaguehub`, and `scholarships`.

The project uses a conventional single settings module, SQLite local database, root URL includes per app, and app-local templates. Static CSS is separated by subsystem, such as `static/css/styles.css`, `pdp.css`, `leaguehub.css`, and `scholarships.css`.

## Existing Apps

Existing installed Django apps:

- `home`: public website pages. Uses `home.urls`, class-based template views, project-level templates under `templates/home`, and shared includes such as `site_header.html`, `nav.html`, `footer.html`, and `nav_script.html`.
- `drafts`: staff-only draft room. Owns draft-specific models, CSV import preview/confirm workflow, draft actions, audit-style action records, live public board, command center, and export.
- `pdp`: current player development platform. Owns existing `PlayerProfile`, seasons, coach/parent access, evaluation imports, metrics, development logs, goals, reports, snapshots, roadmaps, drills, AI scaffolding, import workbench, account provisioning, and PDP permissions.
- `leaguehub`: league/season/team/game management, score submission and verification, standings, game stories/photos, and score audit entries.
- `scholarships`: scholarship applicant signup/login, application workflow, staff review, downloads, references, and scholarship cycles.

Analytics implementation needs to coexist with `pdp.PlayerProfile`, but `pdp.PlayerProfile` is legacy/transitionary. The new `players.Player` model should be treated as the canonical future player identity model, not as a dependent extension of `pdp.PlayerProfile`. Phase 1 should introduce `players.Player` carefully without migrating PDP workflows unless explicitly instructed.

## User/Auth Model And Permission Patterns

The project uses Django's default auth user model. There is no custom `AUTH_USER_MODEL` setting in `vancouverminor/settings.py`.

Observed auth conventions:

- Use `django.contrib.auth.get_user_model()` in tests and services where user creation is needed.
- Staff/admin capability is commonly represented by `user.is_staff` or `user.is_superuser`.
- App-specific permissions are implemented with service functions and view mixins rather than Django groups or model permissions.
- Class-based views use `LoginRequiredMixin` and `UserPassesTestMixin` for protected workflows.
- Unauthorized workflow actions often raise `PermissionDenied`.
- User-facing success, warning, and error feedback uses `django.contrib.messages`.

Existing permission examples:

- `drafts.views.StaffRequiredMixin` limits draft management to staff.
- `pdp.services.permissions` defines functions such as `is_platform_admin`, `get_accessible_players`, `can_view_player`, `can_manage_player`, `can_manage_imports`, and `visible_logs_for_user`.
- `leaguehub.services.permissions` is consumed by score workflow services and views.
- `pdp.middleware.FirstLoginPasswordChangeMiddleware` redirects PDP player users with `must_change_password` to the password change page.

Phase 1 should follow the existing pattern: put reusable permission decisions in services, keep view mixins thin, and use staff/superuser checks unless a more specific role model is introduced by the architecture.

## Installed Apps And Settings Conventions

`INSTALLED_APPS` is a simple literal list in `vancouverminor/settings.py`. Local apps are added by app label only:

- `drafts`
- `home`
- `pdp`
- `leaguehub`
- `scholarships`

Other settings conventions:

- Django version in `requirements.txt` is `Django==4.2.11`.
- `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"`.
- Database is local SQLite at `BASE_DIR / "db.sqlite3"`.
- `TIME_ZONE = "America/Vancouver"` and `USE_TZ = True`.
- Templates use `DIRS = [BASE_DIR / "templates"]` and `APP_DIRS = True`.
- Static files use `STATIC_URL = "static/"` and `STATICFILES_DIRS = [BASE_DIR / "static"]`.
- Media uploads use `MEDIA_URL = "/media/"` and `MEDIA_ROOT = BASE_DIR / "media"`.
- `LOGIN_URL = "/pdp/login/"` and `LOGIN_REDIRECT_URL = "/pdp/"`.
- Root URLs serve media in `DEBUG`.

There is no environment-variable settings layer currently visible. Analytics Phase 1 should make minimal settings changes: add new apps to `INSTALLED_APPS`, add URL includes, and avoid introducing new configuration machinery.

## URL Routing Conventions

The root URL configuration in `vancouverminor/urls.py` uses `include()` for each app:

- `/drafts/`
- `/leaguehub/`
- `/pdp/`
- `/scholarships/`
- `/` for `home`

App URL files define `app_name` where namespacing is needed. Existing route style uses clear nouns and slugs/IDs:

- Draft routes use draft slugs, for example `drafts:<name>` paths under `<slug:slug>/`.
- PDP player pages use `players/<int:player_id>/...`.
- League Hub uses both IDs for game actions and slugs for public league/season/team pages.
- Scholarships use application primary keys and cycle slugs.

Analytics should add its own namespaced URL include, likely under `/analytics/`, and the future `players` app should expose only player-specific routes if needed by Phase 1. Do not bury player identity routes under Analytics if they are intended to be reusable.

## Template/Layout Conventions

The project has a root `templates/base.html` with static loading, global metadata, skip link, content blocks, optional `extra_head`, `extra_js`, and an analytics script placeholder.

Subsystem layout patterns:

- `pdp/templates/pdp/base.html` extends `base.html`, loads `static/css/pdp.css`, provides a PDP app shell, navigation, and message rendering.
- `leaguehub/templates/leaguehub/base.html` extends `pdp/base.html`, adds `static/css/leaguehub.css`, and provides League Hub toolbar/navigation blocks.
- `scholarships/templates/scholarships/base.html` extends `base.html`, includes home site header/footer, loads `static/css/scholarships.css`, and renders messages.
- `drafts` uses app templates and a partial `_header.html` rather than a full app base template.

Message rendering is duplicated in app base templates with `.message-stack` and `message--{{ message.tags }}` classes. Forms are rendered using standard Django templates rather than a third-party form rendering library. No frontend framework is present.

Analytics should probably create an app-specific base template that extends `pdp/base.html` or follows the PDP shell, because Analytics is a staff/player operations surface rather than a public marketing page. It should use a dedicated `static/css/analytics.css` only if needed.

## Admin Configuration Patterns

Admin registration uses `@admin.register(Model)` and `ModelAdmin` classes.

Common admin conventions:

- `list_display` for key fields and timestamps.
- `list_filter` for status, season, active flags, and related ownership fields.
- `search_fields` for names, slugs, usernames, emails, and related text.
- `prepopulated_fields` for slug fields where appropriate.
- Inline admin classes for child records, such as draft teams, scholarship references, end-of-season report items, and roadmap items.
- Readonly timestamp fields are centralized in app-local `TimeStampedAdmin` classes in `pdp` and `leaguehub`.

Analytics and `players` should register new models with practical list/search/filter configuration from the start. Timestamp fields should be readonly in admin. Avoid exposing large JSON payloads as primary admin editing surfaces unless useful for debugging.

## Model Conventions

Observed model conventions:

- Most newer apps use `created_at = models.DateTimeField(auto_now_add=True)` and `updated_at = models.DateTimeField(auto_now=True)`.
- `pdp`, `leaguehub`, and `scholarships` define app-local abstract `TimeStampedModel`.
- `drafts` uses timestamp fields directly on each model.
- Slugs are generated in `save()` using `django.utils.text.slugify`, often with numeric suffixes for uniqueness.
- `leaguehub` calls `self.full_clean()` in several `save()` methods to enforce model validation.
- Ordering is defined in `Meta` for most models.
- Constraints and indexes are used where relationships require uniqueness or query performance, especially in `leaguehub`.
- Older `unique_together` is still used in `drafts` and `pdp`; `leaguehub` uses `models.UniqueConstraint`.
- JSON fields are common for flexible payloads, imported rows, metadata, preview snapshots, mappings, AI payloads, and external source payloads.
- File/image uploads use `FileField` and `ImageField` with app-specific `upload_to` paths.
- There is no broad soft-delete convention. Some models use `is_active`; League Hub games have `is_archived`.

Analytics Phase 1 should use a local abstract timestamp base or a shared one only if a shared utility already exists by implementation time. The current repo does not have a project-wide base model. Prefer explicit constraints/indexes for player identity, source identifiers, imports, observations, and responses.

## Service-Layer Patterns

The repository uses services for non-trivial business logic.

Existing service organization:

- `drafts/services.py` is a single module containing CSV parsing, import preview serialization, draft creation, draft actions, transactions, and audit action creation.
- `pdp/services/` is a package with `accounts.py`, `ai.py`, `development.py`, `imports.py`, and `permissions.py`.
- `leaguehub/services/` is a package with `content.py`, `permissions.py`, `presentation.py`, `score_workflow.py`, and `standings.py`.

Service conventions:

- Business operations are plain functions.
- `@transaction.atomic` wraps operations that create or update multiple records.
- Services raise `ValidationError` for business validation failures and `PermissionDenied` for authorization failures.
- Dataclasses are used for structured service results, such as draft import row results, PDP account provisioning results, workbook sheets, and League Hub score workflow results.
- Services use `select_for_update()` where concurrent workflow changes matter.
- Views parse forms, call services, handle messages, and redirect/render.

Analytics should follow the package-style service organization for new work:

- `players/services/identity_service.py`
- `players/services/matching_service.py`
- `players/services/import_service.py`
- `players/services/tag_service.py`
- `analytics/services/observations.py`
- `analytics/services/questions.py`
- `analytics/services/timelines.py`
- `analytics/services/reports.py`

Keep player identity logic out of `analytics/services`.

## Test Organization And Fixtures

Tests currently live in app-level `tests.py` files rather than `tests/` packages.

Observed test style:

- Uses `django.test.TestCase`.
- Uses `django.urls.reverse`.
- Uses `get_user_model()` for auth users.
- Uses `self.client.force_login(user)` for authenticated view tests.
- Uses `SimpleUploadedFile` for upload tests.
- Uses `override_settings` for temporary `MEDIA_ROOT` during file upload tests.
- Tests cover both service functions and rendered views.
- Fixture data is built inline in `setUp()` or helper methods; no factory library is present.
- No pytest-specific setup is visible.

The expected test command is the standard Django test runner, for example `python manage.py test`.

Analytics Phase 1 should add focused tests in app-level `tests.py` unless the project adopts test packages first. Tests should cover model constraints, player matching/import services, permissions, admin-critical service behavior, and basic view access/rendering.

## File Upload / CSV Handling Patterns

Existing upload/import patterns:

- `drafts` has `CSVUploadForm`, `parse_player_csv`, `serialize_import_preview`, `deserialize_import_preview`, and `import_players`.
- Draft CSV import uses `csv.DictReader`, UTF-8 BOM handling, header normalization, duplicate/blank header detection, required header validation, row-level errors, preview payload hidden fields, and a preview/confirm workflow.
- Draft imported player records store flexible `extra_data` and `imported_row` JSON.
- `pdp` has `WorkbookUploadForm`, `WorkbookMappingForm`, `parse_workbook`, preview serialization, column choices, mapping config, and import execution.
- PDP import supports `.csv` and `.xlsx`. XLSX parsing is implemented with Python standard library `zipfile` and `xml.etree.ElementTree`; no pandas/openpyxl dependency is present.
- PDP import stores workbook metadata, mapping config, preview snapshots, raw payload, and row errors on `EvaluationImport`.
- `leaguehub` uses `ImageField` for game photos and tests uploads with a temporary media root.
- `scholarships` uses `FileField` for transcript/supporting documents with app-specific upload paths.

For Phase 1 player imports, reuse the preview/confirm mental model. Because the architecture assigns player imports to `players`, the Analytics Command Center can host the page, but parsing, matching, duplicate handling, merge behavior, and provenance should call `players.services.import_service`.

## Reusable Utilities

Reusable or repeatable patterns found:

- `pdp.services.accounts.generate_unique_username` and `provision_player_account` for account provisioning patterns.
- `pdp.services.permissions` for player access and visibility patterns.
- `leaguehub.services.permissions` and `leaguehub.services.score_workflow` for workflow permission checks plus transaction-wrapped state changes.
- `leaguehub.services.presentation` likely supports common League Hub context/navigation presentation.
- Template tags exist in `drafts/templatetags/draft_tags.py` and `pdp/templatetags/pdp_tags.py`.
- Root and app base templates provide reusable CSS/message/navigation patterns.
- Home includes provide public site header/footer/navigation.
- Existing import parsers include useful header normalization, row cleaning, preview serialization, and upload-test examples.

There is no project-wide `common` or `core` app, no shared abstract timestamp model, and no shared service base class. Avoid creating broad shared infrastructure during Phase 1 unless an immediate cross-app need exists.

## Integration Notes For Analytics

Practical implementation guidance:

- Create the new `players` app as the canonical player identity bounded context. Treat `pdp.PlayerProfile` only as a legacy coexistence, migration-planning, or temporary bridge concern if required.
- Analytics should reference `players.Player` directly rather than going through `pdp.PlayerProfile`.
- Keep `players` services reusable and independent of Analytics UI. Analytics should call these services for import, matching, aliases, source identifiers, and tags.
- Keep Analytics focused on observations, question sets, responses, evaluator roles, timelines, comparison, reports, and draft context.
- Follow the existing view pattern: class-based views, forms for validation, services for business logic, messages for user feedback, and redirects after successful POSTs.
- Add root URL includes and app namespaces consistently.
- Use app-local templates and CSS rather than introducing a frontend framework.
- Use JSON fields for provenance and flexible payloads where the architecture calls for future extensibility.
- Prefer transaction-wrapped service functions for imports, matching/merge decisions, and observation submission.
- Add admin registrations early because current apps expose operational data through Django admin.
- Use `get_user_model()` in services/tests, but model FKs may continue using settings/auth-compatible references as appropriate.

## Risks / Ambiguities

- The existing `pdp.PlayerProfile` overlaps with the planned `players.Player`, but it is legacy/transitionary. Phase 1 must avoid making `players.Player` depend on `pdp.PlayerProfile` while still avoiding disruption to existing PDP workflows.
- Existing apps reference `pdp.models.Season`; there is no shared season app. Analytics may need seasons/cycles and should avoid creating a conflicting season concept without an architecture update.
- Draft players currently live in `drafts.DraftPlayer`, separate from canonical player identity. Draft context integration will need matching/linking rules later.
- There is no custom role/group framework. Evaluator roles for Analytics need a clear model/service boundary and should not rely only on `is_staff`.
- Existing import workflows store preview payloads in hidden fields; this is simple but may be limiting for large files. Phase 1 should keep imports practical and test file sizes expected by VCB.
- The settings file contains development defaults and no environment configuration layer. Avoid assuming production deployment conventions.
- Media uploads are served locally in debug. Any future sensitive uploads will need deliberate access controls.
- There is no shared base model or common utility app; creating one would be an architectural change and should not be done casually in Phase 1.

## Recommendations For Phase 1

- Implement only the `players` foundation needed by later Analytics phases: `Player`, aliases, source identifiers, source rows/provenance, tags, and the matching/import service surface called for by the architecture.
- Before creating models, map the exact field overlap between legacy `pdp.PlayerProfile`, `drafts.DraftPlayer`, and the planned canonical `players.Player`.
- Keep the first `players.Player` model minimal and stable: identity fields, active flag if needed, timestamps, and metadata/provenance fields only where justified.
- Use an app-local abstract `TimeStampedModel` in `players` unless a shared base model is approved later.
- Put matching, import, alias, identity, and tag behavior under `players/services/`.
- Write service tests first for player matching/import behavior, including exact match, likely duplicate, conflict, and no-match cases.
- Add practical admin registrations for all Phase 1 `players` models with search by name, email, source identifiers, and aliases.
- Do not implement Analytics observation UI in Phase 1.
- Do not migrate PDP workflows to `players.Player` during Phase 1 unless explicitly instructed; document any coexistence or temporary bridge requirement for a later phase.
- Use the existing preview/confirm import pattern, but keep the import business rules inside `players`, even if the later entry point is shown from Analytics.

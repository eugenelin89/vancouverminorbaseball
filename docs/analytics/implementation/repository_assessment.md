# Repository Assessment

## Purpose

One-time assessment of the existing Django repository before Phase 1 implementation begins.

Use this document to adapt the Analytics implementation to the current codebase rather than assuming a greenfield Django project.

Do not fill this in from assumptions. Complete it by inspecting the repository immediately before Phase 1 implementation planning.

## Existing Django Project Structure

Document the project package, settings module, root URL configuration, app layout, static/media layout, and any notable project-level conventions.

## Existing Apps

List existing Django apps and summarize their responsibilities, models, services, templates, URLs, and tests relevant to Analytics implementation.

## User/Auth Model And Permission Patterns

Document the auth model, staff/admin conventions, login patterns, group/role usage, decorators/mixins, and any app-specific permission services.

## Installed Apps And Settings Conventions

Document how apps are added to `INSTALLED_APPS`, settings style, static/media settings, middleware conventions, and environment/configuration patterns.

## URL Routing Conventions

Document root URL inclusion patterns, app namespace conventions, path naming, route style, and redirect conventions.

## Template/Layout Conventions

Document base templates, app-specific base templates, shared includes, CSS conventions, form rendering patterns, message display, and navigation conventions.

## Admin Configuration Patterns

Document admin registration style, list displays, search fields, filters, readonly fields, inlines, and any safety conventions for sensitive data.

## Model Conventions

Document model conventions found in the repo, including timestamp fields, slug generation, soft delete/archive flags, ordering, constraints, indexes, naming conventions, `clean()` usage, and `save()` patterns.

## Service-Layer Patterns

Document existing service modules, function style, transaction usage, validation/permission boundaries, and how views call services.

## Test Organization And Fixtures

Document test file locations, test style, fixture/factory patterns, auth helpers, upload tests, service tests, and command used to run tests.

## File Upload / CSV Handling Patterns

Document existing upload forms, file parsing, CSV handling, preview workflows, import services, media usage, validation, and row-level error patterns.

## Reusable Utilities

Document reusable helpers, template tags, middleware, form utilities, service functions, CSS/layout utilities, or other patterns that Analytics should reuse.

## Integration Notes For Analytics

Document concrete guidance for implementing Analytics in this repo, including where to align with existing conventions and where to avoid coupling.

## Risks / Ambiguities

Document repo-specific uncertainties, risky assumptions, naming conflicts, migration concerns, sensitive data concerns, and integration questions.

## Recommendations For Phase 1

Document actionable recommendations for Phase 1 implementation based on this repository assessment.

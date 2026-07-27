# Prompt 104 - Platform

## User Prompt

```text
You are working in the Django project located at:

/Users/eugenelin/dev/vmba0

The production site is Vancouver Community Baseball’s internal platform at:

https://vancouverminor.com/

The application has several Django apps, including accounts, analytics, players, drafts, leaguehub, pdp, scholarships, and seasons.

## Objective

Perform a comprehensive mobile-responsive UI audit and improvement pass across the entire application.

The current site works reasonably on desktop, but several pages look poor or become difficult to use on mobile devices. A clear example is a submitted-evaluations table where five or more columns are compressed into the width of an iPhone. Words wrap one or two letters per line, rows become extremely tall, and the content is effectively unusable.

Do not fix only that one page. Review all user-facing application pages and make the whole platform polished, readable, and easy to use on phones while preserving a strong desktop experience.

## Primary design approach

Use responsive layouts appropriate to the content.

For tabular lists:

- Keep useful full tables on desktop and larger tablets.
- On mobile, replace wide tables with readable stacked cards or another mobile-first representation.
- Do not simply squeeze desktop tables into the phone width.
- Do not rely on horizontal scrolling as the default solution.
- Horizontal scrolling may be used only where the information genuinely cannot be represented effectively as cards or a reduced table.
- Preserve all meaningful information and actions.
- Make the primary record name prominent at the top of each card.
- Show remaining fields as clearly labelled values.
- Make row actions easy to tap.

For example, a submitted evaluation should appear approximately like this on mobile:

Andrew Macmillan

Season: Spring 2026
Team: Mariners
Division: 13U House
Evaluator: Sean Choi

[View evaluation]

The desktop version may remain a conventional table.

## Scope

Audit all user-facing templates and shared components, including pages under:

- accounts
- analytics
- players
- drafts
- leaguehub
- pdp
- scholarships
- seasons
- shared/base templates
- authentication and password-change pages
- staff/admin-facing custom pages, excluding Django’s built-in admin unless it has project-specific overrides

Review all of the following types of interfaces:

- navigation and headers
- dashboards
- command centres
- tables and result lists
- evaluation lists
- evaluation forms
- player search
- player profiles
- player timelines
- player comparisons
- coach assessment pages
- self-evaluation pages
- peer-evaluation pages
- review pages
- import forms
- import previews
- import results
- draft pages
- filters and search controls
- cards
- alerts
- pagination
- modals, if any
- login and password-change screens
- empty states
- error messages
- detail pages
- forms with multiple fields or question sections
- action toolbars and button groups

Use the project’s URL configuration to identify reachable pages rather than relying only on templates that are easy to find.

## Mobile requirements

Target common phone widths, especially:

- 320 px
- 375 px
- 390 px
- 430 px

Also preserve good behaviour on tablets and desktops.

At mobile widths:

1. No page should create unintended horizontal page scrolling.
2. Text must not wrap one or two characters per line because a column is too narrow.
3. Main content must fit naturally within the viewport.
4. Buttons and links must remain visible and easy to tap.
5. Important actions must not be pushed offscreen.
6. Forms must use the available width.
7. Inputs, selects, and textareas should generally be full width where appropriate.
8. Labels, help text, validation errors, and required/optional indicators must remain readable.
9. Button groups should wrap or stack cleanly.
10. Filter toolbars should stack logically.
11. Headings should not overflow.
12. Long usernames, email addresses, team names, and player names must wrap safely.
13. Cards and panels should not have excessive nested padding.
14. Tables used on mobile must be either:
    - converted to cards,
    - reduced to a small number of essential columns, or
    - intentionally placed in a labelled horizontal-scroll container when no better representation exists.
15. Tap targets should be approximately 44 px high where practical.
16. Fixed-width elements must be removed or made responsive.
17. Content should not sit underneath fixed headers or navigation.
18. Mobile cards should not duplicate desktop tables for screen readers unless visibility and accessibility are handled correctly.

## Navigation

Review the main navigation carefully.

On mobile:

- Navigation must collapse or reorganize cleanly.
- Menu items must not overflow.
- The logged-in user/account controls must remain accessible.
- Logout, profile, and password-related actions must be easy to find.
- Large desktop navigation bars should not consume excessive vertical space.
- Ensure expanded mobile navigation can be closed and does not obscure content incorrectly.

Do not introduce a large JavaScript framework solely for navigation.

## Forms and evaluation workflows

Many users will complete evaluations on their phones.

Improve form usability by ensuring:

- question text is readable
- radio buttons, checkboxes, and select fields are easy to tap
- rating controls do not overflow
- optional questions are visually distinguishable without being distracting
- long forms have sensible vertical spacing
- section headings remain clear
- validation errors appear next to the relevant field
- save draft, submit, cancel, back, reopen, and review actions are arranged clearly
- destructive or final actions are visually distinct
- sticky action bars are used only if they improve usability and do not cover content
- submitted/read-only answers are easy to scan on mobile

Preserve all existing behaviour, permissions, validation, and workflows.

## Tables and mobile-card implementation

Create reusable patterns rather than implementing unrelated one-off fixes.

Prefer one of these approaches:

### Approach A: Separate desktop table and mobile card markup

Render:

- a desktop/tablet table visible at an appropriate breakpoint
- a mobile card list visible below that breakpoint

Ensure both use the same server-side data and actions.

### Approach B: CSS transformation

Use semantic data-label attributes and CSS to turn rows/cells into stacked mobile records, but only where this remains readable and accessible.

Choose the approach that best fits the existing codebase.

Avoid global CSS that transforms every table blindly. Different tables have different needs.

Create shared CSS classes or template partials where practical, for example:

- .responsive-data-table
- .mobile-record-list
- .mobile-record-card
- .record-field
- .record-actions
- .responsive-toolbar
- .form-actions

Names may differ if the project already has established conventions.

## Styling constraints

Before changing styles:

1. Inspect the existing CSS architecture.
2. Identify whether the project uses Bootstrap, custom CSS, or another framework.
3. Reuse existing components and conventions.
4. Avoid replacing the visual identity of the application.
5. Avoid introducing a new CSS framework.
6. Avoid a large redesign unrelated to responsiveness.
7. Keep the implementation maintainable.
8. Prefer shared styles over inline styles.
9. Remove obsolete styles only when confident they are unused.
10. Do not modify generated static files directly when source files exist elsewhere.

Preserve the current branding, colour palette, typography, and overall desktop appearance unless a small adjustment is needed for usability.

## Accessibility

Maintain or improve accessibility:

- retain semantic headings
- retain table semantics on desktop
- use visible labels for form fields
- preserve keyboard navigation
- provide visible focus states
- avoid using colour as the only status indicator
- ensure reasonable colour contrast
- use aria-expanded, aria-controls, or other attributes where appropriate
- ensure mobile and desktop duplicate representations do not both appear to assistive technology simultaneously
- maintain logical tab order
- ensure clickable cards do not create invalid nested links
- use buttons for actions and links for navigation

## Testing and audit process

Start by inventorying the application.

1. Inspect URL configuration in every app.
2. Identify each user-facing route.
3. Map each route to its view and template.
4. Inspect shared base templates and CSS.
5. Search for:
   - <table
   - fixed widths
   - min-width
   - nowrap rules
   - large grids
   - multi-column forms
   - inflexible flex containers
   - button toolbars
   - overflow issues
6. Identify pages likely to fail on narrow screens.
7. Implement fixes systematically.

Use browser automation if the project already contains Playwright, Selenium, Django LiveServer tests, or another suitable setup. Do not add a heavy browser-test dependency unless necessary.

At minimum, add focused automated tests that verify important responsive markup and classes are rendered for representative pages.

Where practical, test or manually inspect representative pages at:

- 390 × 844, representative modern iPhone
- 375 × 667, smaller phone
- 768 × 1024, tablet
- 1440 × 900, desktop

Test with:

- long player names
- long team/division names
- long evaluator names
- long email addresses
- empty values
- many records
- validation errors
- no results
- records with multiple action buttons

## Specific known issue

Locate the page that displays text similar to:

“8 submitted evaluations found.”

Its desktop table currently includes columns similar to:

- Player
- Season
- Team
- Division
- Evaluator

On an iPhone, the columns are squeezed so severely that words are displayed vertically across many lines.

Fix this page using the desktop-table/mobile-card pattern. Ensure:

- the player name is prominent
- season, team, division, and evaluator are clearly labelled
- all current actions remain available
- cards have sensible spacing
- the result count remains visible
- filters remain usable
- pagination, if present, remains usable
- desktop table behaviour remains strong

Use this page as one representative example, but continue auditing every other page.

## Regression protection

Do not alter:

- business logic
- permissions
- account roles
- evaluation scoring
- submission rules
- database models unless absolutely required
- URL names
- import behaviour
- authentication behaviour
- service-layer logic

Avoid migrations unless a genuine functional requirement makes one necessary. A mobile UI pass should normally require no database migration.

Do not expose passwords, secret settings, private metadata, or sensitive information.

## Documentation

Update project documentation with:

- an overview of the responsive design approach
- breakpoints used
- reusable CSS/template patterns
- guidance for making future pages mobile-friendly
- which pages were audited
- any pages that intentionally retain horizontal scrolling and why
- a mobile QA checklist

Update the existing user manual only where UI instructions or screenshots/descriptions have materially changed.

Create or update a developer-facing responsive UI document under docs/.

## Deliverables

When finished, provide:

1. A concise summary of the mobile problems found.
2. A route/page inventory showing what was reviewed.
3. A list of templates and CSS files changed.
4. A description of the reusable responsive patterns introduced.
5. A list of pages converted from tables to mobile cards.
6. A list of pages intentionally left as horizontally scrolling tables and the reason.
7. Automated tests added or updated.
8. Commands run and results.
9. Any remaining limitations or pages requiring manual data/setup to inspect.
10. Deployment notes, including whether collectstatic is required.
11. Confirmation whether migrations are required.
12. Git commit hashes.

## Verification commands

Run the appropriate project checks, including at least:

python manage.py check
python manage.py makemigrations --check
python manage.py test
git diff --check

Also run any existing linting, formatting, frontend, or QA commands documented by the project.

If the complete test suite is very large, run the relevant app tests first, then the full suite if practical.

## Git discipline

- Inspect the current working tree before making changes.
- Do not overwrite unrelated work.
- Do not include unrelated modified files in commits.
- Make logical commits with clear messages.
- Push the completed commits to the current branch.
- Archive this prompt in the project’s normal prompt archive location, following the existing numbering and naming convention.
- Commit the prompt archive separately if that matches the existing project convention.

## Final standard

The completed application should feel deliberately designed for mobile, not merely technically responsive.

A coach, parent, player, or staff member using an iPhone should be able to:

- navigate the platform
- find records
- review information
- fill out an evaluation
- submit or save forms
- use filters
- open details
- change a password
- complete their primary workflow

without zooming, rotating the phone, deciphering vertically wrapped table text, or repeatedly scrolling sideways.
```

## Implementation Commit Diff

```diff
diff --git a/accounts/templates/accounts/coach_import_preview.html b/accounts/templates/accounts/coach_import_preview.html
index 2100c8f..64e361a 100644
--- a/accounts/templates/accounts/coach_import_preview.html
+++ b/accounts/templates/accounts/coach_import_preview.html
@@ -30,8 +30,8 @@
 
     <article class="pdp-card">
         <h2>Rows</h2>
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>Row</th>
@@ -51,18 +51,18 @@
                 <tbody>
                     {% for row in preview.rows %}
                         <tr>
-                            <td>{{ row.row_number }}</td>
-                            <td>{{ row.first_name }} {{ row.last_name }}</td>
-                            <td>{{ row.email }}</td>
-                            <td>{{ row.final_username|default:"-" }}</td>
-                            <td>{{ row.division }} {{ row.team }}</td>
-                            <td>{{ row.assignment_role_label }}</td>
-                            <td>{{ row.account_label|default:"-" }}</td>
-                            <td>{{ row.assignment_label|default:"-" }}</td>
-                            <td>{{ row.password_behavior|default:"-" }}</td>
-                            <td>{{ row.is_active|yesno:"Yes,No" }}</td>
-                            <td>{{ row.status }}</td>
-                            <td>
+                            <td data-label="Row">{{ row.row_number }}</td>
+                            <td data-label="Name">{{ row.first_name }} {{ row.last_name }}</td>
+                            <td data-label="Email">{{ row.email }}</td>
+                            <td data-label="Username">{{ row.final_username|default:"-" }}</td>
+                            <td data-label="Team">{{ row.division }} {{ row.team }}</td>
+                            <td data-label="Role">{{ row.assignment_role_label }}</td>
+                            <td data-label="Account">{{ row.account_label|default:"-" }}</td>
+                            <td data-label="Assignment">{{ row.assignment_label|default:"-" }}</td>
+                            <td data-label="Password">{{ row.password_behavior|default:"-" }}</td>
+                            <td data-label="Active">{{ row.is_active|yesno:"Yes,No" }}</td>
+                            <td data-label="Status">{{ row.status }}</td>
+                            <td data-label="Messages">
                                 {% for message in row.messages %}
                                     <div>{{ message }}</div>
                                 {% empty %}
diff --git a/accounts/templates/accounts/coach_import_result.html b/accounts/templates/accounts/coach_import_result.html
index 65d8c31..1e0c10e 100644
--- a/accounts/templates/accounts/coach_import_result.html
+++ b/accounts/templates/accounts/coach_import_result.html
@@ -27,8 +27,8 @@
 
     <article class="pdp-card">
         <h2>Rows</h2>
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>Row</th>
@@ -45,21 +45,21 @@
                 <tbody>
                     {% for row in result.rows %}
                         <tr>
-                            <td>{{ row.row_number|default:"-" }}</td>
-                            <td>{{ row.status }}</td>
-                            <td>
+                            <td data-label="Row">{{ row.row_number|default:"-" }}</td>
+                            <td data-label="Status">{{ row.status }}</td>
+                            <td data-label="Username">
                                 {% if row.user_id %}
                                     <a href="{% url 'accounts:user-detail' user_id=row.user_id %}">{{ row.username }}</a>
                                 {% else %}
                                     {{ row.username|default:"-" }}
                                 {% endif %}
                             </td>
-                            <td>{{ row.division }} {{ row.team }}</td>
-                            <td>{{ row.assignment_role_label|default:"-" }}</td>
-                            <td>{{ row.assignment_status|default:"-" }}</td>
-                            <td>{{ row.password_behavior|default:"-" }}</td>
-                            <td>{% if row.user_id %}{{ row.is_active|yesno:"Yes,No" }}{% else %}-{% endif %}</td>
-                            <td>
+                            <td data-label="Team">{{ row.division }} {{ row.team }}</td>
+                            <td data-label="Role">{{ row.assignment_role_label|default:"-" }}</td>
+                            <td data-label="Assignment">{{ row.assignment_status|default:"-" }}</td>
+                            <td data-label="Password">{{ row.password_behavior|default:"-" }}</td>
+                            <td data-label="Active">{% if row.user_id %}{{ row.is_active|yesno:"Yes,No" }}{% else %}-{% endif %}</td>
+                            <td data-label="Messages">
                                 {% for message in row.messages %}
                                     <div>{{ message }}</div>
                                 {% empty %}
diff --git a/accounts/templates/accounts/operations_dashboard.html b/accounts/templates/accounts/operations_dashboard.html
index e0daa34..6cc8dd7 100644
--- a/accounts/templates/accounts/operations_dashboard.html
+++ b/accounts/templates/accounts/operations_dashboard.html
@@ -33,18 +33,18 @@
 
     <article class="pdp-card">
         <h2>Accounts Requiring Password Change</h2>
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr><th>Username</th><th>Name</th><th>Role</th><th></th></tr>
                 </thead>
                 <tbody>
                     {% for row in users_requiring_password_change %}
                         <tr>
-                            <td>{{ row.user.username }}</td>
-                            <td>{{ row.user.get_full_name|default:"-" }}</td>
-                            <td>{{ row.role_label }}</td>
-                            <td><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
+                            <td data-label="Username">{{ row.user.username }}</td>
+                            <td data-label="Name">{{ row.user.get_full_name|default:"-" }}</td>
+                            <td data-label="Role">{{ row.role_label }}</td>
+                            <td data-label="Action"><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
                         </tr>
                     {% empty %}
                         <tr><td colspan="4">No accounts currently require password change.</td></tr>
@@ -56,18 +56,18 @@
 
     <article class="pdp-card">
         <h2>Users Without Player Links</h2>
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr><th>Username</th><th>Name</th><th>Role</th><th></th></tr>
                 </thead>
                 <tbody>
                     {% for row in unlinked_users %}
                         <tr>
-                            <td>{{ row.user.username }}</td>
-                            <td>{{ row.user.get_full_name|default:"-" }}</td>
-                            <td>{{ row.role_label }}</td>
-                            <td><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
+                            <td data-label="Username">{{ row.user.username }}</td>
+                            <td data-label="Name">{{ row.user.get_full_name|default:"-" }}</td>
+                            <td data-label="Role">{{ row.role_label }}</td>
+                            <td data-label="Action"><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
                         </tr>
                     {% empty %}
                         <tr><td colspan="4">No unlinked users found.</td></tr>
diff --git a/accounts/templates/accounts/user_detail.html b/accounts/templates/accounts/user_detail.html
index ee24f27..3f8be24 100644
--- a/accounts/templates/accounts/user_detail.html
+++ b/accounts/templates/accounts/user_detail.html
@@ -59,8 +59,8 @@
 
     <article class="pdp-card">
         <h2>Linked Players</h2>
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>Player</th>
@@ -74,12 +74,12 @@
                 <tbody>
                     {% for row in linked_players %}
                         <tr>
-                            <td>{{ row.player.display_name }}</td>
-                            <td>{{ row.relationship }}</td>
-                            <td>{% if row.is_primary %}Yes{% else %}No{% endif %}</td>
-                            <td>{% if row.is_active %}Active{% else %}Inactive{% endif %}</td>
-                            <td>{% if row.created_from_import %}Yes{% else %}No{% endif %}</td>
-                            <td>{{ row.import_label|default:"-" }}</td>
+                            <td data-label="Player">{{ row.player.display_name }}</td>
+                            <td data-label="Relationship">{{ row.relationship }}</td>
+                            <td data-label="Primary">{% if row.is_primary %}Yes{% else %}No{% endif %}</td>
+                            <td data-label="Active">{% if row.is_active %}Active{% else %}Inactive{% endif %}</td>
+                            <td data-label="Imported">{% if row.created_from_import %}Yes{% else %}No{% endif %}</td>
+                            <td data-label="Import Batch">{{ row.import_label|default:"-" }}</td>
                         </tr>
                     {% empty %}
                         <tr><td colspan="6">No linked players found.</td></tr>
diff --git a/accounts/templates/accounts/user_links.html b/accounts/templates/accounts/user_links.html
index 35a1a7f..8d57ac9 100644
--- a/accounts/templates/accounts/user_links.html
+++ b/accounts/templates/accounts/user_links.html
@@ -35,8 +35,8 @@
 
     <article class="pdp-card">
         <h2>Existing Links</h2>
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>Player</th>
@@ -50,12 +50,12 @@
                 <tbody>
                     {% for row in linked_players %}
                         <tr>
-                            <td>{{ row.player.display_name }}</td>
-                            <td>{{ row.relationship }}</td>
-                            <td>{% if row.is_primary %}Yes{% else %}No{% endif %}</td>
-                            <td>{% if row.is_active %}Active{% else %}Inactive{% endif %}</td>
-                            <td>{% if row.created_from_import %}Yes{% else %}No{% endif %}</td>
-                            <td>
+                            <td data-label="Player">{{ row.player.display_name }}</td>
+                            <td data-label="Relationship">{{ row.relationship }}</td>
+                            <td data-label="Primary">{% if row.is_primary %}Yes{% else %}No{% endif %}</td>
+                            <td data-label="Status">{% if row.is_active %}Active{% else %}Inactive{% endif %}</td>
+                            <td data-label="Imported">{% if row.created_from_import %}Yes{% else %}No{% endif %}</td>
+                            <td data-label="Actions">
                                 <div class="pdp-actions">
                                     {% if row.is_active %}
                                         <form method="post">
diff --git a/accounts/templates/accounts/user_list.html b/accounts/templates/accounts/user_list.html
index bb3c9e7..ad3617f 100644
--- a/accounts/templates/accounts/user_list.html
+++ b/accounts/templates/accounts/user_list.html
@@ -97,16 +97,16 @@
                     <h3>Bulk Operation Result</h3>
                     <p>{{ bulk_result.successful }} succeeded, {{ bulk_result.failed }} failed, {{ bulk_result.processed }} processed.</p>
                     {% if bulk_result.errors %}
-                        <div class="table-wrap">
-                            <table class="pdp-table">
+                        <div class="table-wrap table-wrap--cards">
+                            <table class="pdp-table" data-responsive="cards">
                                 <thead>
                                     <tr><th>Account</th><th>Error</th></tr>
                                 </thead>
                                 <tbody>
                                     {% for error in bulk_result.errors %}
                                         <tr>
-                                            <td>{{ error.username }}</td>
-                                            <td>{{ error.message }}</td>
+                                            <td data-label="Account">{{ error.username }}</td>
+                                            <td data-label="Error">{{ error.message }}</td>
                                         </tr>
                                     {% endfor %}
                                 </tbody>
@@ -115,8 +115,8 @@
                     {% endif %}
                 </section>
             {% endif %}
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>Select</th>
@@ -136,33 +136,33 @@
                 <tbody>
                     {% for row in rows %}
                         <tr>
-                            <td>
+                            <td data-label="Select">
                                 <input type="hidden" name="visible_user_ids" value="{{ row.user.id }}">
                                 <input type="checkbox" name="user_ids" value="{{ row.user.id }}">
                             </td>
-                            <td>{{ row.user.username }}</td>
-                            <td>{{ row.user.get_full_name|default:"-" }}</td>
-                            <td>{{ row.user.email|default:"-" }}</td>
-                            <td>{{ row.role_label }}</td>
-                            <td>{% if row.user.is_active %}Active{% else %}Inactive{% endif %}</td>
-                            <td>{% if row.user.is_staff %}Yes{% else %}No{% endif %}</td>
-                            <td>{% if row.user.is_superuser %}Yes{% else %}No{% endif %}</td>
-                            <td>
+                            <td data-label="Username">{{ row.user.username }}</td>
+                            <td data-label="Name">{{ row.user.get_full_name|default:"-" }}</td>
+                            <td data-label="Email">{{ row.user.email|default:"-" }}</td>
+                            <td data-label="Role">{{ row.role_label }}</td>
+                            <td data-label="Active">{% if row.user.is_active %}Active{% else %}Inactive{% endif %}</td>
+                            <td data-label="Staff">{% if row.user.is_staff %}Yes{% else %}No{% endif %}</td>
+                            <td data-label="Superuser">{% if row.user.is_superuser %}Yes{% else %}No{% endif %}</td>
+                            <td data-label="Password Change">
                                 {% if row.user.account_profile.must_change_password %}
                                     Required
                                 {% else %}
                                     No
                                 {% endif %}
                             </td>
-                            <td>{{ row.linked_player_count }}</td>
-                            <td>
+                            <td data-label="Player Links">{{ row.linked_player_count }}</td>
+                            <td data-label="Imported">
                                 {% if row.user.account_profile.created_from_import %}
                                     Yes
                                 {% else %}
                                     No
                                 {% endif %}
                             </td>
-                            <td><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
+                            <td data-label="Action"><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
                         </tr>
                     {% empty %}
                         <tr><td colspan="12">No accounts match these filters.</td></tr>
diff --git a/accounts/tests/test_account_operations.py b/accounts/tests/test_account_operations.py
index 0ae9c3c..dce2960 100644
--- a/accounts/tests/test_account_operations.py
+++ b/accounts/tests/test_account_operations.py
@@ -873,6 +873,8 @@ class AccountOperationsViewTests(TestCase):
         self.assertNotContains(response, "regular")
         self.assertContains(response, "Bulk action")
         self.assertContains(response, "Select all accounts shown")
+        self.assertContains(response, 'data-responsive="cards"')
+        self.assertContains(response, 'data-label="Email"')
 
     def test_user_list_bulk_post_requires_staff(self):
         self.client.force_login(self.regular)
@@ -1514,6 +1516,8 @@ class AccountOperationsViewTests(TestCase):
         self.assertEqual(preview_response.status_code, 200)
         self.assertContains(preview_response, "Ready to create")
         self.assertContains(preview_response, "new.coach@example.com")
+        self.assertContains(preview_response, 'data-responsive="cards"')
+        self.assertContains(preview_response, 'data-label="Email"')
 
         confirm_response = self.client.post(
             reverse("accounts:coach-import-confirm"), {"confirm": "on"}
diff --git a/analytics/templates/analytics/assessment_list.html b/analytics/templates/analytics/assessment_list.html
index 46a4d3e..fa113d5 100644
--- a/analytics/templates/analytics/assessment_list.html
+++ b/analytics/templates/analytics/assessment_list.html
@@ -25,8 +25,8 @@
             <button class="button button--primary" type="submit">Filter</button>
         </form>
         <p>{{ cycle.name }}</p>
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>Player</th>
@@ -40,12 +40,12 @@
                 <tbody>
                     {% for item in player_statuses %}
                         <tr>
-                            <td>{{ item.player.display_name }}</td>
-                            <td>{{ item.player_division }}</td>
-                            <td>{{ item.player_team }}</td>
-                            <td>{{ item.evaluation_perspective_label }}</td>
-                            <td>{% include "analytics/_assessment_status_badge.html" with status=item.status %}</td>
-                            <td>
+                            <td data-label="Player">{{ item.player.display_name }}</td>
+                            <td data-label="Division">{{ item.player_division }}</td>
+                            <td data-label="Team">{{ item.player_team }}</td>
+                            <td data-label="Type">{{ item.evaluation_perspective_label }}</td>
+                            <td data-label="Status">{% include "analytics/_assessment_status_badge.html" with status=item.status %}</td>
+                            <td data-label="Action">
                                 {% if item.observation and item.status == "submitted" %}
                                     <a class="button button--ghost" href="{% url 'analytics:assessment-detail' observation_id=item.observation.id %}">View</a>
                                 {% elif item.observation %}
diff --git a/analytics/templates/analytics/evaluation_list.html b/analytics/templates/analytics/evaluation_list.html
index 33d08f2..c7487b2 100644
--- a/analytics/templates/analytics/evaluation_list.html
+++ b/analytics/templates/analytics/evaluation_list.html
@@ -25,8 +25,8 @@
             <button class="button button--primary" type="submit">Filter</button>
         </form>
         <p>{{ cycle.name }}</p>
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>Player</th>
@@ -40,12 +40,12 @@
                 <tbody>
                     {% for item in player_statuses %}
                         <tr>
-                            <td>{{ item.player.display_name }}</td>
-                            <td>{{ item.player_division }}</td>
-                            <td>{{ item.player_team }}</td>
-                            <td>{{ item.evaluation_perspective_label }}</td>
-                            <td>{% include "analytics/_assessment_status_badge.html" with status=item.status %}</td>
-                            <td>
+                            <td data-label="Player">{{ item.player.display_name }}</td>
+                            <td data-label="Division">{{ item.player_division }}</td>
+                            <td data-label="Team">{{ item.player_team }}</td>
+                            <td data-label="Type">{{ item.evaluation_perspective_label }}</td>
+                            <td data-label="My submission">{% include "analytics/_assessment_status_badge.html" with status=item.status %}</td>
+                            <td data-label="Action">
                                 {% if not item.can_evaluate %}
                                     <span class="pdp-badge pdp-badge--muted">Unavailable</span>
                                 {% elif item.observation and item.status == "submitted" %}
diff --git a/analytics/templates/analytics/evaluation_review_list.html b/analytics/templates/analytics/evaluation_review_list.html
index 0a204a7..9cb44eb 100644
--- a/analytics/templates/analytics/evaluation_review_list.html
+++ b/analytics/templates/analytics/evaluation_review_list.html
@@ -74,8 +74,8 @@
         <button class="button button--primary" type="submit">Filter</button>
     </form>
     <p>{{ total_count }} submitted evaluation{{ total_count|pluralize }} found.</p>
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr>
                     <th>Player</th>
@@ -93,16 +93,16 @@
             <tbody>
                 {% for row in rows %}
                     <tr>
-                        <td>{{ row.player_name }}</td>
-                        <td>{{ row.season_name }}</td>
-                        <td>{{ row.player_team }}</td>
-                        <td>{{ row.player_division }}</td>
-                        <td>{{ row.evaluator_name }}</td>
-                        <td>{{ row.evaluator_role_name }}</td>
-                        <td>{{ row.evaluation_perspective_label }}</td>
-                        <td>{{ row.cycle_name }}</td>
-                        <td>{{ row.submitted_at|date:"M j, Y" }}</td>
-                        <td><a class="button button--ghost" href="{% url 'analytics:evaluation-review-detail' observation_id=row.observation_id %}">Review</a></td>
+                        <td data-label="Player">{{ row.player_name }}</td>
+                        <td data-label="Season">{{ row.season_name }}</td>
+                        <td data-label="Team">{{ row.player_team }}</td>
+                        <td data-label="Division">{{ row.player_division }}</td>
+                        <td data-label="Evaluator">{{ row.evaluator_name }}</td>
+                        <td data-label="Role">{{ row.evaluator_role_name }}</td>
+                        <td data-label="Type">{{ row.evaluation_perspective_label }}</td>
+                        <td data-label="Cycle">{{ row.cycle_name }}</td>
+                        <td data-label="Submitted">{{ row.submitted_at|date:"M j, Y" }}</td>
+                        <td data-label="Action"><a class="button button--ghost" href="{% url 'analytics:evaluation-review-detail' observation_id=row.observation_id %}">Review</a></td>
                     </tr>
                 {% empty %}
                     <tr><td colspan="10">No submitted evaluations found.</td></tr>
diff --git a/analytics/templates/analytics/import_list.html b/analytics/templates/analytics/import_list.html
index 79562de..c949b05 100644
--- a/analytics/templates/analytics/import_list.html
+++ b/analytics/templates/analytics/import_list.html
@@ -9,8 +9,8 @@
         <h2>Import batches</h2>
         <a class="button button--primary" href="{% url 'analytics:import-new' %}">New Import</a>
     </div>
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr>
                     <th>File</th>
@@ -25,13 +25,13 @@
             <tbody>
                 {% for batch in import_batches %}
                     <tr>
-                        <td><a href="{% url 'analytics:import-detail' pk=batch.pk %}">{{ batch.original_filename }}</a></td>
-                        <td>{% if batch.season %}{{ batch.season }}{% else %}Legacy / No Season{% endif %}</td>
-                        <td>{{ batch.source }}</td>
-                        <td>{{ batch.get_status_display }}</td>
-                        <td>{{ batch.rows_processed }}</td>
-                        <td>{{ batch.rows_created }}</td>
-                        <td>{{ batch.rows_updated }}</td>
+                        <td data-label="File"><a href="{% url 'analytics:import-detail' pk=batch.pk %}">{{ batch.original_filename }}</a></td>
+                        <td data-label="Season">{% if batch.season %}{{ batch.season }}{% else %}Legacy / No Season{% endif %}</td>
+                        <td data-label="Source">{{ batch.source }}</td>
+                        <td data-label="Status">{{ batch.get_status_display }}</td>
+                        <td data-label="Rows">{{ batch.rows_processed }}</td>
+                        <td data-label="Created">{{ batch.rows_created }}</td>
+                        <td data-label="Updated">{{ batch.rows_updated }}</td>
                     </tr>
                 {% empty %}
                     <tr><td colspan="7">No imports yet.</td></tr>
diff --git a/analytics/templates/analytics/import_preview.html b/analytics/templates/analytics/import_preview.html
index 1ca09ed..2350042 100644
--- a/analytics/templates/analytics/import_preview.html
+++ b/analytics/templates/analytics/import_preview.html
@@ -37,8 +37,8 @@
             <div><strong>{{ preview.summary.memberships_update }}</strong><span>Memberships Update</span></div>
         </div>
     {% endif %}
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr>
                     <th>Row</th>
@@ -53,13 +53,13 @@
             <tbody>
                 {% for row in preview.rows %}
                     <tr>
-                        <td>{{ row.row_number }}</td>
-                        <td>{{ row.identity.first_name }} {{ row.identity.last_name }}</td>
-                        <td>{{ row.roster.division }} {{ row.roster.team_name }}</td>
-                        <td>{{ row.action }}</td>
-                        <td>{{ row.membership.label }}</td>
-                        <td>{% if row.matched_player_name %}{{ row.matched_player_name }}{% else %}{{ row.match_status }}{% endif %}</td>
-                        <td>
+                        <td data-label="Row">{{ row.row_number }}</td>
+                        <td data-label="Player">{{ row.identity.first_name }} {{ row.identity.last_name }}</td>
+                        <td data-label="Roster">{{ row.roster.division }} {{ row.roster.team_name }}</td>
+                        <td data-label="Action">{{ row.action }}</td>
+                        <td data-label="Membership">{{ row.membership.label }}</td>
+                        <td data-label="Match">{% if row.matched_player_name %}{{ row.matched_player_name }}{% else %}{{ row.match_status }}{% endif %}</td>
+                        <td data-label="Issues">
                             {% if row.errors %}{{ row.errors|join:", " }}{% endif %}
                             {% if row.field_conflicts %}{{ row.field_conflicts|length }} conflict{{ row.field_conflicts|length|pluralize }}{% endif %}
                             {% if row.candidate_names %}{{ row.candidate_names|join:", " }}{% endif %}
diff --git a/analytics/templates/analytics/my_evaluations.html b/analytics/templates/analytics/my_evaluations.html
index d27f1c4..a4f4163 100644
--- a/analytics/templates/analytics/my_evaluations.html
+++ b/analytics/templates/analytics/my_evaluations.html
@@ -19,8 +19,8 @@
                 </ul>
             </section>
         {% endif %}
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>Player</th>
@@ -34,12 +34,12 @@
                 <tbody>
                     {% for item in evaluations %}
                         <tr>
-                            <td>{{ item.player.display_name }}</td>
-                            <td>{{ item.cycle_name }}</td>
-                            <td>{{ item.evaluation_perspective_label }}</td>
-                            <td>{{ item.evaluator_role_name }}</td>
-                            <td>{{ item.submitted_at|date:"M j, Y" }}</td>
-                            <td><a class="button button--ghost" href="{% url 'analytics:my-evaluation-detail' observation_id=item.observation_id %}">View Evaluation</a></td>
+                            <td data-label="Player">{{ item.player.display_name }}</td>
+                            <td data-label="Cycle">{{ item.cycle_name }}</td>
+                            <td data-label="Type">{{ item.evaluation_perspective_label }}</td>
+                            <td data-label="Evaluator Role">{{ item.evaluator_role_name }}</td>
+                            <td data-label="Submitted">{{ item.submitted_at|date:"M j, Y" }}</td>
+                            <td data-label="Action"><a class="button button--ghost" href="{% url 'analytics:my-evaluation-detail' observation_id=item.observation_id %}">View Evaluation</a></td>
                         </tr>
                     {% empty %}
                         <tr><td colspan="6">No submitted evaluations are available yet.</td></tr>
diff --git a/analytics/templates/analytics/observation_review_list.html b/analytics/templates/analytics/observation_review_list.html
index ae6c787..5c10ab3 100644
--- a/analytics/templates/analytics/observation_review_list.html
+++ b/analytics/templates/analytics/observation_review_list.html
@@ -22,8 +22,8 @@
         </label>
         <button class="button button--primary" type="submit">Filter</button>
     </form>
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr>
                     <th>Player</th>
@@ -40,15 +40,15 @@
             <tbody>
                 {% for observation in observations %}
                     <tr>
-                        <td>{{ observation.player.display_name }}</td>
-                        <td>{{ observation.season_name_snapshot|default:"Legacy / No Season" }}</td>
-                        <td>{{ observation.player_division_snapshot|default:observation.player.division }} {{ observation.player_team_name_snapshot|default:observation.player.team_name }}</td>
-                        <td>{{ observation.evaluation_cycle.name }}</td>
-                        <td>{{ observation.evaluator }}</td>
-                        <td>{{ observation.evaluation_perspective_label }}</td>
-                        <td>{{ observation.get_status_display }}</td>
-                        <td>{{ observation.submitted_at|default:"" }}</td>
-                        <td><a class="button button--ghost" href="{% url 'analytics:observation-review-detail' observation_id=observation.id %}">Review</a></td>
+                        <td data-label="Player">{{ observation.player.display_name }}</td>
+                        <td data-label="Season">{{ observation.season_name_snapshot|default:"Legacy / No Season" }}</td>
+                        <td data-label="Roster">{{ observation.player_division_snapshot|default:observation.player.division }} {{ observation.player_team_name_snapshot|default:observation.player.team_name }}</td>
+                        <td data-label="Cycle">{{ observation.evaluation_cycle.name }}</td>
+                        <td data-label="Evaluator">{{ observation.evaluator }}</td>
+                        <td data-label="Type">{{ observation.evaluation_perspective_label }}</td>
+                        <td data-label="Status">{{ observation.get_status_display }}</td>
+                        <td data-label="Submitted">{{ observation.submitted_at|default:"" }}</td>
+                        <td data-label="Action"><a class="button button--ghost" href="{% url 'analytics:observation-review-detail' observation_id=observation.id %}">Review</a></td>
                     </tr>
                 {% empty %}
                     <tr><td colspan="9">No observations found.</td></tr>
diff --git a/analytics/templates/analytics/player_compare.html b/analytics/templates/analytics/player_compare.html
index be182ba..bd7f6aa 100644
--- a/analytics/templates/analytics/player_compare.html
+++ b/analytics/templates/analytics/player_compare.html
@@ -18,16 +18,16 @@
         <button class="button button--primary" type="submit">Find Players</button>
     </form>
     {% if players %}
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead><tr><th>Player</th><th>Division</th><th>Team</th><th></th></tr></thead>
                 <tbody>
                     {% for player in players %}
                         <tr>
-                            <td>{{ player.display_name }}</td>
-                            <td>{{ player.division }}</td>
-                            <td>{{ player.team_name }}</td>
-                            <td><a class="button button--ghost" href="{% url 'analytics:player-compare' %}?players={{ player.id }}">Compare</a></td>
+                            <td data-label="Player">{{ player.display_name }}</td>
+                            <td data-label="Division">{{ player.division }}</td>
+                            <td data-label="Team">{{ player.team_name }}</td>
+                            <td data-label="Action"><a class="button button--ghost" href="{% url 'analytics:player-compare' %}?players={{ player.id }}">Compare</a></td>
                         </tr>
                     {% endfor %}
                 </tbody>
@@ -41,8 +41,8 @@
     {% if comparison.empty %}
         <p>Select players to compare.</p>
     {% else %}
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>Player</th>
@@ -59,33 +59,33 @@
                 <tbody>
                     {% for summary in comparison.summaries %}
                         <tr>
-                            <td><a href="{% url 'analytics:player-profile' player_id=summary.player.id %}">{{ summary.player.display_name }}</a></td>
-                            <td>{{ summary.player.team_name|default:"-" }} / {{ summary.player.division|default:"-" }}</td>
-                            <td>
+                            <td data-label="Player"><a href="{% url 'analytics:player-profile' player_id=summary.player.id %}">{{ summary.player.display_name }}</a></td>
+                            <td data-label="Team / Division">{{ summary.player.team_name|default:"-" }} / {{ summary.player.division|default:"-" }}</td>
+                            <td data-label="Tags">
                                 {% for tag in summary.tags %}
                                     {{ tag.name }}{% if not forloop.last %}, {% endif %}
                                 {% empty %}
                                     -
                                 {% endfor %}
                             </td>
-                            <td>{% if summary.submitted_observation_count %}{{ summary.submitted_observation_count }}{% else %}No submitted assessments{% endif %}</td>
-                            <td>{{ summary.evaluator_count }}</td>
-                            <td>{% if summary.average_rating %}{{ summary.average_rating|floatformat:1 }}{% else %}-{% endif %}</td>
-                            <td>
+                            <td data-label="Assessments">{% if summary.submitted_observation_count %}{{ summary.submitted_observation_count }}{% else %}No submitted assessments{% endif %}</td>
+                            <td data-label="Evaluators">{{ summary.evaluator_count }}</td>
+                            <td data-label="Average">{% if summary.average_rating %}{{ summary.average_rating|floatformat:1 }}{% else %}-{% endif %}</td>
+                            <td data-label="Category Scores">
                                 {% for category in summary.category_scores %}
                                     <div>{{ category.category }}: {% if category.average_rating %}{{ category.average_rating|floatformat:1 }}{% else %}-{% endif %}</div>
                                 {% empty %}
                                     -
                                 {% endfor %}
                             </td>
-                            <td>
+                            <td data-label="Notes">
                                 {% for note in summary.notes %}
                                     <div>{{ note }}</div>
                                 {% empty %}
                                     -
                                 {% endfor %}
                             </td>
-                            <td>
+                            <td data-label="Draft Context">
                                 {% for context in summary.draft_contexts %}
                                     <div>
                                         {{ context.draft_player.draft.name }}:
diff --git a/analytics/templates/analytics/player_profile.html b/analytics/templates/analytics/player_profile.html
index 4b436ec..4552a05 100644
--- a/analytics/templates/analytics/player_profile.html
+++ b/analytics/templates/analytics/player_profile.html
@@ -42,16 +42,16 @@
 <article class="pdp-card">
     <h2>Imported Context</h2>
     {% if source_rows %}
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead><tr><th>Source</th><th>File</th><th>Row</th><th>Imported</th></tr></thead>
                 <tbody>
                     {% for row in source_rows %}
                         <tr>
-                            <td>{{ row.source }}</td>
-                            <td>{{ row.source_filename|default:"-" }}</td>
-                            <td>{{ row.row_number|default:"-" }}</td>
-                            <td>{{ row.imported_at }}</td>
+                            <td data-label="Source">{{ row.source }}</td>
+                            <td data-label="File">{{ row.source_filename|default:"-" }}</td>
+                            <td data-label="Row">{{ row.row_number|default:"-" }}</td>
+                            <td data-label="Imported">{{ row.imported_at }}</td>
                         </tr>
                     {% endfor %}
                 </tbody>
@@ -65,17 +65,17 @@
 <article class="pdp-card">
     <h2>Draft Context</h2>
     {% if draft_contexts %}
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead><tr><th>Draft</th><th>Status</th><th>Team</th><th>Pick</th><th>Round</th></tr></thead>
                 <tbody>
                     {% for context in draft_contexts %}
                         <tr>
-                            <td>{{ context.draft_player.draft.name }}</td>
-                            <td>{{ context.match_status }}</td>
-                            <td>{% if context.selected_team %}{{ context.selected_team.name }}{% elif context.current_team %}{{ context.current_team.name }}{% else %}-{% endif %}</td>
-                            <td>{{ context.pick_number|default:"-" }}</td>
-                            <td>{{ context.selected_round|default:"-" }}</td>
+                            <td data-label="Draft">{{ context.draft_player.draft.name }}</td>
+                            <td data-label="Status">{{ context.match_status }}</td>
+                            <td data-label="Team">{% if context.selected_team %}{{ context.selected_team.name }}{% elif context.current_team %}{{ context.current_team.name }}{% else %}-{% endif %}</td>
+                            <td data-label="Pick">{{ context.pick_number|default:"-" }}</td>
+                            <td data-label="Round">{{ context.selected_round|default:"-" }}</td>
                         </tr>
                     {% endfor %}
                 </tbody>
diff --git a/analytics/templates/analytics/player_search.html b/analytics/templates/analytics/player_search.html
index 6a85279..1366b0d 100644
--- a/analytics/templates/analytics/player_search.html
+++ b/analytics/templates/analytics/player_search.html
@@ -70,8 +70,8 @@
 
 <article class="pdp-card">
     <h2>{{ result_count }} player{{ result_count|pluralize }}</h2>
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr>
                     <th>Player</th>
@@ -85,12 +85,12 @@
             <tbody>
                 {% for player in players %}
                     <tr>
-                        <td>{{ player.display_name }}</td>
-                        <td>{{ player.division }}</td>
-                        <td>{{ player.team_name }}</td>
-                        <td>{{ player.birth_year|default:"" }}</td>
-                        <td>{% if player.is_active %}Active{% else %}Inactive{% endif %}</td>
-                        <td>
+                        <td data-label="Player">{{ player.display_name }}</td>
+                        <td data-label="Division">{{ player.division }}</td>
+                        <td data-label="Team">{{ player.team_name }}</td>
+                        <td data-label="Birth year">{{ player.birth_year|default:"" }}</td>
+                        <td data-label="Status">{% if player.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td data-label="Actions">
                             <a class="button button--ghost" href="{% url 'analytics:player-profile' player_id=player.id %}">Profile</a>
                             <a class="button button--ghost" href="{% url 'analytics:player-compare' %}?players={{ player.id }}">Compare</a>
                         </td>
diff --git a/analytics/tests/test_evaluation_review.py b/analytics/tests/test_evaluation_review.py
index c225163..41c596c 100644
--- a/analytics/tests/test_evaluation_review.py
+++ b/analytics/tests/test_evaluation_review.py
@@ -154,6 +154,9 @@ class EvaluationReviewViewTests(TestCase):
         self.assertContains(response, "Casey Coach")
         self.assertContains(response, "Sam Coach")
         self.assertContains(response, "Self Evaluation")
+        self.assertContains(response, 'data-responsive="cards"')
+        self.assertContains(response, 'data-label="Evaluator"')
+        self.assertContains(response, 'data-label="Role"')
         self.assertContains(
             response,
             reverse(
diff --git a/analytics/tests/test_evaluation_submission.py b/analytics/tests/test_evaluation_submission.py
index 916b203..e803e78 100644
--- a/analytics/tests/test_evaluation_submission.py
+++ b/analytics/tests/test_evaluation_submission.py
@@ -125,6 +125,9 @@ class EvaluationAccessSubmissionViewTests(TestCase):
         self.assertContains(response, "Evaluate Player")
         self.assertContains(response, "My submission")
         self.assertContains(response, "Self Evaluation")
+        self.assertContains(response, 'data-responsive="cards"')
+        self.assertContains(response, 'data-label="Player"')
+        self.assertContains(response, 'data-label="My submission"')
         self.assertContains(
             response,
             reverse(
diff --git a/analytics/tests/test_import_views.py b/analytics/tests/test_import_views.py
index 523cbf4..8a2a9ea 100644
--- a/analytics/tests/test_import_views.py
+++ b/analytics/tests/test_import_views.py
@@ -37,12 +37,20 @@ class AnalyticsImportViewTests(TestCase):
         self.assertEqual(response.status_code, 403)
 
     def test_staff_can_open_import_list(self):
+        PlayerImportBatch.objects.create(
+            source=SOURCE_MEMBER_LIST,
+            original_filename="member.csv",
+            uploaded_by=self.staff,
+            season=self.season,
+        )
         self.client.force_login(self.staff)
 
         response = self.client.get(reverse("analytics:import-list"))
 
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "Player Imports")
+        self.assertContains(response, 'data-responsive="cards"')
+        self.assertContains(response, 'data-label="File"')
 
     def test_upload_redirects_to_preview(self):
         self.client.force_login(self.staff)
diff --git a/docs/ui/responsive_design.md b/docs/ui/responsive_design.md
new file mode 100644
index 0000000..bd7b078
--- /dev/null
+++ b/docs/ui/responsive_design.md
@@ -0,0 +1,117 @@
+# Responsive UI Guide
+
+This guide documents the responsive layout conventions used by the VCB platform.
+It is intended for developers and maintainers who add or update Django templates.
+
+## Purpose
+
+The platform is used on phones, tablets, laptops, and desktops. Staff workflows
+often include dense tables, but key user journeys must remain readable and usable
+on narrow screens.
+
+Responsive work should preserve existing server-rendered behavior. Do not add
+JavaScript solely to make a table usable on mobile unless a workflow explicitly
+requires it.
+
+## Breakpoints
+
+- Mobile: up to `640px`.
+- Tablet and narrow desktop: existing app layouts use intermediate breakpoints
+  around `760px`, `820px`, `900px`, `960px`, and `1180px`.
+- Desktop: layouts should continue to use the existing table and grid patterns.
+
+When testing manually, check at least:
+
+- `320px`
+- `375px`
+- `390px`
+- `430px`
+- tablet portrait
+- desktop
+
+## Responsive Tables
+
+Most user-facing tables should use the table-to-card pattern on mobile.
+
+Use:
+
+```html
+<div class="table-wrap table-wrap--cards">
+  <table class="pdp-table" data-responsive="cards">
+    <thead>...</thead>
+    <tbody>
+      <tr>
+        <td data-label="Player">...</td>
+        <td data-label="Team">...</td>
+      </tr>
+    </tbody>
+  </table>
+</div>
+```
+
+For non-PDP tables, the same `data-responsive="cards"` pattern is supported for:
+
+- `.draft-table`
+- `.team-table`
+- `.scholarship-table`
+- `.tryout-table`
+
+Each mobile card cell must include a concise `data-label` matching the column
+meaning. Empty-state rows may omit `data-label`.
+
+## Form Layouts
+
+Use the existing form containers and field patterns. Forms should stack naturally
+on mobile, with full-width inputs and buttons where practical.
+
+The PDP-style form utility `.pdp-form` uses a responsive grid so labels and
+controls remain readable on mobile without fixed widths.
+
+## Pages Converted To Mobile Cards
+
+The responsive card pattern is used across representative high-traffic workflows:
+
+- Account operations dashboard, user list, user detail, user links, coach import
+  preview, and coach import result.
+- Analytics player imports, coach assessments, evaluation submission, submitted
+  evaluation review, staff review, player search, player profile context,
+  comparison, and My Evaluations.
+- Season operations lists and detail tables for seasons, teams, memberships,
+  coach assignments, player history, and coach history.
+- Draft list and draft import previews.
+- Public registration, tryouts, scholarship staff review, LeagueHub summary
+  tables, and legacy PDP data tables.
+
+## Intentionally Scrollable Tables
+
+Some dense operational tables remain horizontally scrollable instead of becoming
+cards:
+
+- Draft command center roster/player-pool tables.
+- Public live draft board tables.
+- Analytics command center summary/matrix tables.
+
+These pages are dense comparison or live-operation surfaces where preserving
+side-by-side columns is more useful than stacking every cell into cards. If these
+surfaces become primary mobile workflows, redesign them as dedicated mobile
+views rather than forcing the same desktop matrix into cards.
+
+## Accessibility Notes
+
+- Do not duplicate table content for mobile.
+- Keep the original `<table>` structure in the template.
+- Use CSS display changes for the mobile card layout.
+- Ensure every meaningful cell has a `data-label`.
+- Keep action links and buttons keyboard accessible.
+
+## QA Checklist
+
+Before finishing a template change:
+
+- The page has no unreadable fixed-width table on mobile.
+- Table card labels are clear and not duplicated in confusing ways.
+- Actions remain reachable without horizontal scrolling.
+- Empty states still read correctly.
+- Desktop table layout is unchanged.
+- `git diff --check` passes.
+- Existing page/view tests still pass.
diff --git a/drafts/templates/drafts/draft_import.html b/drafts/templates/drafts/draft_import.html
index d3dadd4..b5fa159 100644
--- a/drafts/templates/drafts/draft_import.html
+++ b/drafts/templates/drafts/draft_import.html
@@ -36,7 +36,7 @@
                         </div>
                     </div>
                     <div class="draft-table-wrap">
-                        <table class="draft-table">
+                        <table class="draft-table" data-responsive="cards">
                             <thead>
                                 <tr>
                                     <th>Row</th>
@@ -48,16 +48,16 @@
                             <tbody>
                                 {% for row in preview.rows %}
                                     <tr>
-                                        <td>{{ row.row_number }}</td>
-                                        <td>{{ row.cleaned_row.first_name }} {{ row.cleaned_row.last_name }}</td>
-                                        <td>
+                                        <td data-label="Row">{{ row.row_number }}</td>
+                                        <td data-label="Player">{{ row.cleaned_row.first_name }} {{ row.cleaned_row.last_name }}</td>
+                                        <td data-label="Status">
                                             {% if row.imported %}
                                                 <span class="status-badge status-badge--open">Ready</span>
                                             {% else %}
                                                 <span class="status-badge status-badge--closed">Rejected</span>
                                             {% endif %}
                                         </td>
-                                        <td>
+                                        <td data-label="Details">
                                             {% if row.errors %}
                                                 {{ row.errors|join:", " }}
                                             {% else %}
diff --git a/drafts/templates/drafts/draft_list.html b/drafts/templates/drafts/draft_list.html
index cf6338f..ec68a19 100644
--- a/drafts/templates/drafts/draft_list.html
+++ b/drafts/templates/drafts/draft_list.html
@@ -32,7 +32,7 @@
                 <a class="button button--primary" href="{% url 'drafts:create' %}">New Draft</a>
             </div>
             <div class="draft-table-wrap">
-                <table class="draft-table">
+                <table class="draft-table" data-responsive="cards">
                     <thead>
                         <tr>
                             <th>Draft</th>
@@ -46,15 +46,15 @@
                     <tbody>
                         {% for draft in drafts %}
                             <tr>
-                                <td>
+                                <td data-label="Draft">
                                     <strong>{{ draft.name }}</strong>
                                     <div class="draft-table__meta">{{ draft.year }} · {{ draft.division }}</div>
                                 </td>
-                                <td><span class="status-badge status-badge--{{ draft.status }}">{{ draft.get_status_display }}</span></td>
-                                <td>{{ draft.teams.count }}</td>
-                                <td>{{ draft.total_player_count }}</td>
-                                <td>{{ draft.updated_at|date:"M j, Y g:i A" }}</td>
-                                <td class="draft-table__actions">
+                                <td data-label="Status"><span class="status-badge status-badge--{{ draft.status }}">{{ draft.get_status_display }}</span></td>
+                                <td data-label="Teams">{{ draft.teams.count }}</td>
+                                <td data-label="Players">{{ draft.total_player_count }}</td>
+                                <td data-label="Updated">{{ draft.updated_at|date:"M j, Y g:i A" }}</td>
+                                <td data-label="Actions" class="draft-table__actions">
                                     <a href="{% url 'drafts:command-center' slug=draft.slug %}">Open room</a>
                                     <span class="draft-table__divider">·</span>
                                     <a href="{% url 'drafts:public-live' slug=draft.slug %}">Public board</a>
diff --git a/leaguehub/templates/leaguehub/dashboard.html b/leaguehub/templates/leaguehub/dashboard.html
index 614c25f..16f10ee 100644
--- a/leaguehub/templates/leaguehub/dashboard.html
+++ b/leaguehub/templates/leaguehub/dashboard.html
@@ -40,8 +40,8 @@
             </div>
             <a class="button button--ghost" href="{% url 'leaguehub:standings' league_slug=league_season.league.slug season_slug=league_season.season.slug %}">Full Standings</a>
         </div>
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>Team</th>
@@ -56,13 +56,13 @@
                 <tbody>
                     {% for row in standings %}
                         <tr>
-                            <td><strong><a href="{{ row.team_url }}">{{ row.team_name }}</a></strong></td>
-                            <td>{{ row.games_played }}</td>
-                            <td>{{ row.wins }}</td>
-                            <td>{{ row.losses }}</td>
-                            <td>{{ row.ties }}</td>
-                            <td>{{ row.points }}</td>
-                            <td>{{ row.run_differential }}</td>
+                            <td data-label="Team"><strong><a href="{{ row.team_url }}">{{ row.team_name }}</a></strong></td>
+                            <td data-label="GP">{{ row.games_played }}</td>
+                            <td data-label="W">{{ row.wins }}</td>
+                            <td data-label="L">{{ row.losses }}</td>
+                            <td data-label="T">{{ row.ties }}</td>
+                            <td data-label="Pts">{{ row.points }}</td>
+                            <td data-label="Diff">{{ row.run_differential }}</td>
                         </tr>
                     {% empty %}
                         <tr><td colspan="7">No verified final games yet.</td></tr>
diff --git a/leaguehub/templates/leaguehub/game_detail.html b/leaguehub/templates/leaguehub/game_detail.html
index ac13857..f5483e0 100644
--- a/leaguehub/templates/leaguehub/game_detail.html
+++ b/leaguehub/templates/leaguehub/game_detail.html
@@ -57,14 +57,14 @@
             </div>
             <a class="button button--ghost" href="{% url 'leaguehub:dashboard' league_slug=league_season.league.slug season_slug=league_season.season.slug %}">Season Dashboard</a>
         </div>
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr><th>Team</th><th>Score</th></tr>
                 </thead>
                 <tbody>
-                    <tr><td><a href="{{ game_display.away_team_url }}">{{ game_display.away_team.name }}</a></td><td>{{ game_display.away_score|default_if_none:"-" }}</td></tr>
-                    <tr><td><a href="{{ game_display.home_team_url }}">{{ game_display.home_team.name }}</a></td><td>{{ game_display.home_score|default_if_none:"-" }}</td></tr>
+                    <tr><td data-label="Team"><a href="{{ game_display.away_team_url }}">{{ game_display.away_team.name }}</a></td><td data-label="Score">{{ game_display.away_score|default_if_none:"-" }}</td></tr>
+                    <tr><td data-label="Team"><a href="{{ game_display.home_team_url }}">{{ game_display.home_team.name }}</a></td><td data-label="Score">{{ game_display.home_score|default_if_none:"-" }}</td></tr>
                 </tbody>
             </table>
         </div>
diff --git a/leaguehub/templates/leaguehub/standings.html b/leaguehub/templates/leaguehub/standings.html
index 833aa3c..40dee27 100644
--- a/leaguehub/templates/leaguehub/standings.html
+++ b/leaguehub/templates/leaguehub/standings.html
@@ -14,8 +14,8 @@
             </div>
             <a class="button button--ghost" href="{% url 'leaguehub:dashboard' league_slug=league_season.league.slug season_slug=league_season.season.slug %}">Back To Dashboard</a>
         </div>
-        <div class="table-wrap">
-            <table class="pdp-table">
+        <div class="table-wrap table-wrap--cards">
+            <table class="pdp-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>#</th>
@@ -33,16 +33,16 @@
                 <tbody>
                     {% for row in standings %}
                         <tr>
-                            <td>{{ row.rank }}</td>
-                            <td><strong><a href="{{ row.team_url }}">{{ row.team_name }}</a></strong></td>
-                            <td>{{ row.games_played }}</td>
-                            <td>{{ row.wins }}</td>
-                            <td>{{ row.losses }}</td>
-                            <td>{{ row.ties }}</td>
-                            <td>{{ row.points }}</td>
-                            <td>{{ row.runs_for }}</td>
-                            <td>{{ row.runs_against }}</td>
-                            <td>{{ row.run_differential }}</td>
+                            <td data-label="#">{{ row.rank }}</td>
+                            <td data-label="Team"><strong><a href="{{ row.team_url }}">{{ row.team_name }}</a></strong></td>
+                            <td data-label="GP">{{ row.games_played }}</td>
+                            <td data-label="W">{{ row.wins }}</td>
+                            <td data-label="L">{{ row.losses }}</td>
+                            <td data-label="T">{{ row.ties }}</td>
+                            <td data-label="Pts">{{ row.points }}</td>
+                            <td data-label="RF">{{ row.runs_for }}</td>
+                            <td data-label="RA">{{ row.runs_against }}</td>
+                            <td data-label="Diff">{{ row.run_differential }}</td>
                         </tr>
                     {% empty %}
                         <tr><td colspan="10">No verified standings data yet.</td></tr>
diff --git a/leaguehub/templates/leaguehub/team_detail.html b/leaguehub/templates/leaguehub/team_detail.html
index 0a31edd..c64c3fd 100644
--- a/leaguehub/templates/leaguehub/team_detail.html
+++ b/leaguehub/templates/leaguehub/team_detail.html
@@ -41,8 +41,8 @@
             <a class="button button--ghost" href="{{ leaguehub_standings_url }}">Full Standings</a>
         </div>
         {% if team_standing %}
-            <div class="table-wrap">
-                <table class="pdp-table">
+            <div class="table-wrap table-wrap--cards">
+                <table class="pdp-table" data-responsive="cards">
                     <thead>
                         <tr>
                             <th>GP</th>
@@ -57,14 +57,14 @@
                     </thead>
                     <tbody>
                         <tr>
-                            <td>{{ team_standing.games_played }}</td>
-                            <td>{{ team_standing.wins }}</td>
-                            <td>{{ team_standing.losses }}</td>
-                            <td>{{ team_standing.ties }}</td>
-                            <td>{{ team_standing.points }}</td>
-                            <td>{{ team_standing.runs_for }}</td>
-                            <td>{{ team_standing.runs_against }}</td>
-                            <td>{{ team_standing.run_differential }}</td>
+                            <td data-label="GP">{{ team_standing.games_played }}</td>
+                            <td data-label="W">{{ team_standing.wins }}</td>
+                            <td data-label="L">{{ team_standing.losses }}</td>
+                            <td data-label="T">{{ team_standing.ties }}</td>
+                            <td data-label="Pts">{{ team_standing.points }}</td>
+                            <td data-label="RF">{{ team_standing.runs_for }}</td>
+                            <td data-label="RA">{{ team_standing.runs_against }}</td>
+                            <td data-label="Diff">{{ team_standing.run_differential }}</td>
                         </tr>
                     </tbody>
                 </table>
diff --git a/pdp/templates/pdp/evaluation_history.html b/pdp/templates/pdp/evaluation_history.html
index 5dbc7bf..216774f 100644
--- a/pdp/templates/pdp/evaluation_history.html
+++ b/pdp/templates/pdp/evaluation_history.html
@@ -13,8 +13,8 @@
                     <h2>{{ category }}</h2>
                 </div>
             </div>
-            <div class="table-wrap">
-                <table class="pdp-table">
+            <div class="table-wrap table-wrap--cards">
+                <table class="pdp-table" data-responsive="cards">
                     <thead>
                         <tr>
                             <th>Metric</th>
@@ -25,9 +25,9 @@
                     <tbody>
                         {% for metric in metrics %}
                             <tr>
-                                <td>{{ metric.display_name }}</td>
-                                <td>{{ metric.numeric_value|default:metric.text_value|default:metric.raw_value }}</td>
-                                <td>{{ metric.evaluation_event.name }} · {{ metric.evaluation_event.evaluated_on }}</td>
+                                <td data-label="Metric">{{ metric.display_name }}</td>
+                                <td data-label="Value">{{ metric.numeric_value|default:metric.text_value|default:metric.raw_value }}</td>
+                                <td data-label="Event">{{ metric.evaluation_event.name }} · {{ metric.evaluation_event.evaluated_on }}</td>
                             </tr>
                         {% endfor %}
                     </tbody>
diff --git a/pdp/templates/pdp/import_workbench.html b/pdp/templates/pdp/import_workbench.html
index 5af1d58..dba1588 100644
--- a/pdp/templates/pdp/import_workbench.html
+++ b/pdp/templates/pdp/import_workbench.html
@@ -58,8 +58,8 @@
     <section class="pdp-grid pdp-grid--single">
         <article class="pdp-card">
             <h2>Account provisioning report</h2>
-            <div class="table-wrap">
-                <table class="pdp-table">
+            <div class="table-wrap table-wrap--cards">
+                <table class="pdp-table" data-responsive="cards">
                     <thead>
                         <tr>
                             <th>Player</th>
@@ -71,10 +71,10 @@
                     <tbody>
                         {% for item in onboarding_report %}
                             <tr>
-                                <td>{{ item.player_name }}</td>
-                                <td>{{ item.username }}</td>
-                                <td>{{ item.created|yesno:"Yes,No" }}</td>
-                                <td>{{ item.password_reset|yesno:"Yes,No" }}</td>
+                                <td data-label="Player">{{ item.player_name }}</td>
+                                <td data-label="Username">{{ item.username }}</td>
+                                <td data-label="Created">{{ item.created|yesno:"Yes,No" }}</td>
+                                <td data-label="Password Reset">{{ item.password_reset|yesno:"Yes,No" }}</td>
                             </tr>
                         {% endfor %}
                     </tbody>
diff --git a/scholarships/templates/scholarships/staff_application_list.html b/scholarships/templates/scholarships/staff_application_list.html
index 1e49f73..f3c86f0 100644
--- a/scholarships/templates/scholarships/staff_application_list.html
+++ b/scholarships/templates/scholarships/staff_application_list.html
@@ -35,7 +35,7 @@
     <article class="scholarship-panel">
         <p class="scholarship-section-label">Applications</p>
         <div class="table-shell">
-            <table class="scholarship-table">
+            <table class="scholarship-table" data-responsive="cards">
                 <thead>
                     <tr>
                         <th>Applicant</th>
@@ -48,14 +48,14 @@
                 <tbody>
                     {% for application in object_list %}
                         <tr>
-                            <td>
+                            <td data-label="Applicant">
                                 <strong>{{ application.player_full_name }}</strong>
                                 <div class="table-subtext">{{ application.applicant.email }}</div>
                             </td>
-                            <td>{{ application.cycle.year }}</td>
-                            <td><span class="status-pill status-pill--{{ application.status }}">{{ application.get_status_display }}</span></td>
-                            <td>{% if application.submitted_at %}{{ application.submitted_at|date:"M j, Y" }}{% else %}Draft{% endif %}</td>
-                            <td class="table-actions">
+                            <td data-label="Cycle">{{ application.cycle.year }}</td>
+                            <td data-label="Status"><span class="status-pill status-pill--{{ application.status }}">{{ application.get_status_display }}</span></td>
+                            <td data-label="Submitted">{% if application.submitted_at %}{{ application.submitted_at|date:"M j, Y" }}{% else %}Draft{% endif %}</td>
+                            <td data-label="Actions" class="table-actions">
                                 <a href="{% url 'scholarships:staff-application-detail' pk=application.pk %}">Open</a>
                                 <a href="{% url 'scholarships:staff-application-download' pk=application.pk %}">Download</a>
                             </td>
@@ -89,4 +89,3 @@
     </article>
 </section>
 {% endblock %}
-
diff --git a/seasons/templates/seasons/assignment_list.html b/seasons/templates/seasons/assignment_list.html
index 05e1f27..ced3c79 100644
--- a/seasons/templates/seasons/assignment_list.html
+++ b/seasons/templates/seasons/assignment_list.html
@@ -39,21 +39,21 @@
     </form>
 </article>
 <article class="pdp-card">
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr><th>Coach</th><th>Season</th><th>Team</th><th>Role</th><th>Primary</th><th>Active</th><th></th></tr>
             </thead>
             <tbody>
                 {% for assignment in assignments %}
                     <tr>
-                        <td>{{ assignment.user.get_full_name|default:assignment.user.username }}</td>
-                        <td>{{ assignment.season.name }}</td>
-                        <td>{{ assignment.season_team.division }} {{ assignment.season_team.name }}</td>
-                        <td>{{ assignment.get_assignment_role_display }}</td>
-                        <td>{% if assignment.is_primary %}Yes{% else %}No{% endif %}</td>
-                        <td>{% if assignment.is_active %}Active{% else %}Inactive{% endif %}</td>
-                        <td>
+                        <td data-label="Coach">{{ assignment.user.get_full_name|default:assignment.user.username }}</td>
+                        <td data-label="Season">{{ assignment.season.name }}</td>
+                        <td data-label="Team">{{ assignment.season_team.division }} {{ assignment.season_team.name }}</td>
+                        <td data-label="Role">{{ assignment.get_assignment_role_display }}</td>
+                        <td data-label="Primary">{% if assignment.is_primary %}Yes{% else %}No{% endif %}</td>
+                        <td data-label="Active">{% if assignment.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td data-label="Actions">
                             <a class="button button--ghost" href="{% url 'seasons:coach-history' assignment.user_id %}">History</a>
                             <a class="button button--ghost" href="{% url 'seasons:coach-assignment-edit' assignment.id %}">Edit</a>
                         </td>
diff --git a/seasons/templates/seasons/coach_history.html b/seasons/templates/seasons/coach_history.html
index 7193a68..fe2c15c 100644
--- a/seasons/templates/seasons/coach_history.html
+++ b/seasons/templates/seasons/coach_history.html
@@ -6,22 +6,22 @@
 {% block seasons_content %}
 <article class="pdp-card">
     <h2>{{ coach.get_full_name|default:coach.username }}</h2>
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr><th>Season</th><th>Team</th><th>Role</th><th>Primary</th><th>Active</th><th>Dates</th><th>Source</th><th></th></tr>
             </thead>
             <tbody>
                 {% for assignment in assignments %}
                     <tr>
-                        <td>{{ assignment.season.name }}</td>
-                        <td>{{ assignment.season_team.division }} {{ assignment.season_team.name }}</td>
-                        <td>{{ assignment.get_assignment_role_display }}</td>
-                        <td>{% if assignment.is_primary %}Yes{% else %}No{% endif %}</td>
-                        <td>{% if assignment.is_active %}Active{% else %}Inactive{% endif %}</td>
-                        <td>{{ assignment.starts_on|default:"-" }} - {{ assignment.ends_on|default:"-" }}</td>
-                        <td>{{ assignment.source|default:"manual" }}</td>
-                        <td><a class="button button--ghost" href="{% url 'seasons:coach-assignment-edit' assignment.id %}">Edit</a></td>
+                        <td data-label="Season">{{ assignment.season.name }}</td>
+                        <td data-label="Team">{{ assignment.season_team.division }} {{ assignment.season_team.name }}</td>
+                        <td data-label="Role">{{ assignment.get_assignment_role_display }}</td>
+                        <td data-label="Primary">{% if assignment.is_primary %}Yes{% else %}No{% endif %}</td>
+                        <td data-label="Active">{% if assignment.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td data-label="Dates">{{ assignment.starts_on|default:"-" }} - {{ assignment.ends_on|default:"-" }}</td>
+                        <td data-label="Source">{{ assignment.source|default:"manual" }}</td>
+                        <td data-label="Action"><a class="button button--ghost" href="{% url 'seasons:coach-assignment-edit' assignment.id %}">Edit</a></td>
                     </tr>
                 {% empty %}
                     <tr><td colspan="8">No season assignments are recorded for this coach.</td></tr>
diff --git a/seasons/templates/seasons/membership_list.html b/seasons/templates/seasons/membership_list.html
index bf51ab9..12dd3e6 100644
--- a/seasons/templates/seasons/membership_list.html
+++ b/seasons/templates/seasons/membership_list.html
@@ -39,21 +39,21 @@
     </form>
 </article>
 <article class="pdp-card">
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr><th>Player</th><th>Season</th><th>Team</th><th>Status</th><th>Primary</th><th>Active</th><th></th></tr>
             </thead>
             <tbody>
                 {% for membership in memberships %}
                     <tr>
-                        <td>{{ membership.player.display_name }}</td>
-                        <td>{{ membership.season.name }}</td>
-                        <td>{{ membership.season_team.division }} {{ membership.season_team.name }}</td>
-                        <td>{{ membership.get_status_display }}</td>
-                        <td>{% if membership.is_primary %}Yes{% else %}No{% endif %}</td>
-                        <td>{% if membership.is_active %}Active{% else %}Inactive{% endif %}</td>
-                        <td>
+                        <td data-label="Player">{{ membership.player.display_name }}</td>
+                        <td data-label="Season">{{ membership.season.name }}</td>
+                        <td data-label="Team">{{ membership.season_team.division }} {{ membership.season_team.name }}</td>
+                        <td data-label="Status">{{ membership.get_status_display }}</td>
+                        <td data-label="Primary">{% if membership.is_primary %}Yes{% else %}No{% endif %}</td>
+                        <td data-label="Active">{% if membership.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td data-label="Actions">
                             <a class="button button--ghost" href="{% url 'seasons:player-history' membership.player_id %}">History</a>
                             <a class="button button--ghost" href="{% url 'seasons:membership-edit' membership.id %}">Edit</a>
                         </td>
diff --git a/seasons/templates/seasons/player_history.html b/seasons/templates/seasons/player_history.html
index e016cb7..6ee3d27 100644
--- a/seasons/templates/seasons/player_history.html
+++ b/seasons/templates/seasons/player_history.html
@@ -10,22 +10,22 @@
         <a class="button button--ghost" href="{% url 'analytics:player-profile' player.id %}">Analytics Profile</a>
         <a class="button button--ghost" href="{% url 'seasons:membership-new' %}">Create Membership</a>
     </div>
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr><th>Season</th><th>Team</th><th>Status</th><th>Primary</th><th>Active</th><th>Dates</th><th>Source</th><th></th></tr>
             </thead>
             <tbody>
                 {% for membership in memberships %}
                     <tr>
-                        <td>{{ membership.season.name }}</td>
-                        <td>{{ membership.season_team.division }} {{ membership.season_team.name }}</td>
-                        <td>{{ membership.get_status_display }}</td>
-                        <td>{% if membership.is_primary %}Yes{% else %}No{% endif %}</td>
-                        <td>{% if membership.is_active %}Active{% else %}Inactive{% endif %}</td>
-                        <td>{{ membership.starts_on|default:"-" }} - {{ membership.ends_on|default:"-" }}</td>
-                        <td>{{ membership.source|default:"manual" }}</td>
-                        <td>
+                        <td data-label="Season">{{ membership.season.name }}</td>
+                        <td data-label="Team">{{ membership.season_team.division }} {{ membership.season_team.name }}</td>
+                        <td data-label="Status">{{ membership.get_status_display }}</td>
+                        <td data-label="Primary">{% if membership.is_primary %}Yes{% else %}No{% endif %}</td>
+                        <td data-label="Active">{% if membership.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td data-label="Dates">{{ membership.starts_on|default:"-" }} - {{ membership.ends_on|default:"-" }}</td>
+                        <td data-label="Source">{{ membership.source|default:"manual" }}</td>
+                        <td data-label="Actions">
                             <a class="button button--ghost" href="{% url 'seasons:membership-edit' membership.id %}">Edit</a>
                             {% if membership.is_active %}
                                 <a class="button button--ghost" href="{% url 'seasons:membership-transfer' membership.id %}">Transfer/Add</a>
diff --git a/seasons/templates/seasons/season_detail.html b/seasons/templates/seasons/season_detail.html
index f6cea65..f0308f6 100644
--- a/seasons/templates/seasons/season_detail.html
+++ b/seasons/templates/seasons/season_detail.html
@@ -26,20 +26,20 @@
 
 <article class="pdp-card">
     <h2>Teams</h2>
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr><th>Team</th><th>Division</th><th>Active</th><th>Memberships</th><th>Assignments</th><th></th></tr>
             </thead>
             <tbody>
                 {% for team in teams %}
                     <tr>
-                        <td>{{ team.name }}</td>
-                        <td>{{ team.division }}</td>
-                        <td>{% if team.is_active %}Active{% else %}Inactive{% endif %}</td>
-                        <td>{{ team.membership_count }}</td>
-                        <td>{{ team.assignment_count }}</td>
-                        <td><a class="button button--ghost" href="{% url 'seasons:team-edit' team.id %}">Edit</a></td>
+                        <td data-label="Team">{{ team.name }}</td>
+                        <td data-label="Division">{{ team.division }}</td>
+                        <td data-label="Active">{% if team.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td data-label="Memberships">{{ team.membership_count }}</td>
+                        <td data-label="Assignments">{{ team.assignment_count }}</td>
+                        <td data-label="Action"><a class="button button--ghost" href="{% url 'seasons:team-edit' team.id %}">Edit</a></td>
                     </tr>
                 {% empty %}
                     <tr><td colspan="6">No teams are recorded for this season.</td></tr>
diff --git a/seasons/templates/seasons/season_list.html b/seasons/templates/seasons/season_list.html
index 28fff2a..e28bb53 100644
--- a/seasons/templates/seasons/season_list.html
+++ b/seasons/templates/seasons/season_list.html
@@ -8,8 +8,8 @@
     <div class="pdp-actions">
         <a class="button button--primary" href="{% url 'seasons:season-new' %}">Create Season</a>
     </div>
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr>
                     <th>Season</th>
@@ -25,14 +25,14 @@
             <tbody>
                 {% for season in seasons %}
                     <tr>
-                        <td>{{ season.name }}<br><small>{{ season.key }}</small></td>
-                        <td>{{ season.starts_on|default:"-" }} - {{ season.ends_on|default:"-" }}</td>
-                        <td>{% if season.is_current %}Yes{% else %}No{% endif %}</td>
-                        <td>{% if season.is_active %}Active{% else %}Inactive{% endif %}</td>
-                        <td>{{ season.team_count }}</td>
-                        <td>{{ season.membership_count }}</td>
-                        <td>{{ season.assignment_count }}</td>
-                        <td><a class="button button--ghost" href="{% url 'seasons:season-detail' season.id %}">Open</a></td>
+                        <td data-label="Season">{{ season.name }}<br><small>{{ season.key }}</small></td>
+                        <td data-label="Dates">{{ season.starts_on|default:"-" }} - {{ season.ends_on|default:"-" }}</td>
+                        <td data-label="Current">{% if season.is_current %}Yes{% else %}No{% endif %}</td>
+                        <td data-label="Active">{% if season.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td data-label="Teams">{{ season.team_count }}</td>
+                        <td data-label="Memberships">{{ season.membership_count }}</td>
+                        <td data-label="Assignments">{{ season.assignment_count }}</td>
+                        <td data-label="Action"><a class="button button--ghost" href="{% url 'seasons:season-detail' season.id %}">Open</a></td>
                     </tr>
                 {% empty %}
                     <tr><td colspan="8">No seasons have been created.</td></tr>
diff --git a/seasons/templates/seasons/team_list.html b/seasons/templates/seasons/team_list.html
index 9bea3a3..0dc32a4 100644
--- a/seasons/templates/seasons/team_list.html
+++ b/seasons/templates/seasons/team_list.html
@@ -21,21 +21,21 @@
     </form>
 </article>
 <article class="pdp-card">
-    <div class="table-wrap">
-        <table class="pdp-table">
+    <div class="table-wrap table-wrap--cards">
+        <table class="pdp-table" data-responsive="cards">
             <thead>
                 <tr><th>Season</th><th>Team</th><th>Division</th><th>Active</th><th>Memberships</th><th>Assignments</th><th></th></tr>
             </thead>
             <tbody>
                 {% for team in teams %}
                     <tr>
-                        <td>{{ team.season.name }}</td>
-                        <td>{{ team.name }}</td>
-                        <td>{{ team.division }}</td>
-                        <td>{% if team.is_active %}Active{% else %}Inactive{% endif %}</td>
-                        <td>{{ team.membership_count }}</td>
-                        <td>{{ team.assignment_count }}</td>
-                        <td><a class="button button--ghost" href="{% url 'seasons:team-edit' team.id %}">Edit</a></td>
+                        <td data-label="Season">{{ team.season.name }}</td>
+                        <td data-label="Team">{{ team.name }}</td>
+                        <td data-label="Division">{{ team.division }}</td>
+                        <td data-label="Active">{% if team.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td data-label="Memberships">{{ team.membership_count }}</td>
+                        <td data-label="Assignments">{{ team.assignment_count }}</td>
+                        <td data-label="Action"><a class="button button--ghost" href="{% url 'seasons:team-edit' team.id %}">Edit</a></td>
                     </tr>
                 {% empty %}
                     <tr><td colspan="7">No teams match these filters.</td></tr>
diff --git a/seasons/tests/test_operations_views.py b/seasons/tests/test_operations_views.py
index 5fd9035..69c7dbb 100644
--- a/seasons/tests/test_operations_views.py
+++ b/seasons/tests/test_operations_views.py
@@ -325,6 +325,8 @@ class SeasonOperationsUITests(TestCase):
 
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "Page 1 of 2")
+        self.assertContains(response, 'data-responsive="cards"')
+        self.assertContains(response, 'data-label="Team"')
         self.assertContains(
             response, f"?season={self.spring.id}&amp;active=yes&amp;page=2"
         )
diff --git a/static/css/pdp.css b/static/css/pdp.css
index 3077993..afe6199 100644
--- a/static/css/pdp.css
+++ b/static/css/pdp.css
@@ -218,6 +218,16 @@
     margin-bottom: 1rem;
 }
 
+.pdp-form {
+    display: grid;
+    gap: 1rem;
+}
+
+.pdp-form label {
+    min-width: 0;
+    overflow-wrap: anywhere;
+}
+
 .pdp-form input,
 .pdp-form select,
 .pdp-form textarea {
@@ -263,6 +273,10 @@
     border-radius: 18px;
 }
 
+.table-wrap--cards {
+    overflow-x: visible;
+}
+
 .pdp-table {
     width: 100%;
     border-collapse: collapse;
@@ -345,8 +359,84 @@
         width: 100%;
     }
 
-    .pdp-table {
-        min-width: 560px;
+    .table-wrap--cards {
+        border-radius: 0;
+    }
+
+    .pdp-table[data-responsive="cards"] {
+        min-width: 0;
+        border-collapse: separate;
+        border-spacing: 0 0.85rem;
+    }
+
+    .pdp-table[data-responsive="cards"] thead {
+        display: none;
+    }
+
+    .pdp-table[data-responsive="cards"],
+    .pdp-table[data-responsive="cards"] tbody,
+    .pdp-table[data-responsive="cards"] tr,
+    .pdp-table[data-responsive="cards"] td {
+        display: block;
+        width: 100%;
+    }
+
+    .pdp-table[data-responsive="cards"] tr {
+        overflow: hidden;
+        border: 1px solid rgba(16, 42, 67, 0.1);
+        border-radius: 18px;
+        background: rgba(255, 255, 255, 0.96);
+        box-shadow: 0 10px 28px rgba(16, 42, 67, 0.08);
+    }
+
+    .pdp-table[data-responsive="cards"] tr:nth-child(even) {
+        background: rgba(255, 255, 255, 0.96);
+    }
+
+    .pdp-table[data-responsive="cards"] td {
+        display: grid;
+        grid-template-columns: minmax(7.5rem, 0.42fr) minmax(0, 1fr);
+        gap: 0.75rem;
+        align-items: start;
+        border: 0;
+        border-bottom: 1px solid rgba(16, 42, 67, 0.07);
+        padding: 0.78rem 0.9rem;
+    }
+
+    .pdp-table[data-responsive="cards"] td:first-child {
+        background: rgba(47, 111, 235, 0.08);
+        font-weight: 800;
+        color: var(--color-navy);
+    }
+
+    .pdp-table[data-responsive="cards"] td:last-child {
+        border-bottom: 0;
+    }
+
+    .pdp-table[data-responsive="cards"] td::before {
+        content: attr(data-label);
+        font-size: 0.78rem;
+        font-weight: 800;
+        letter-spacing: 0.08em;
+        text-transform: uppercase;
+        color: var(--color-text-muted);
+        overflow-wrap: normal;
+    }
+
+    .pdp-table[data-responsive="cards"] td[data-label=""],
+    .pdp-table[data-responsive="cards"] td:not([data-label]) {
+        display: block;
+    }
+
+    .pdp-table[data-responsive="cards"] td[data-label=""]::before,
+    .pdp-table[data-responsive="cards"] td:not([data-label])::before {
+        content: none;
+    }
+
+    .pdp-table[data-responsive="cards"] td .button,
+    .pdp-table[data-responsive="cards"] td button {
+        width: 100%;
+        justify-content: center;
     }
 
     .pdp-table th,
diff --git a/static/css/styles.css b/static/css/styles.css
index d65902e..023b804 100644
--- a/static/css/styles.css
+++ b/static/css/styles.css
@@ -2631,6 +2631,120 @@ table.tryout-table td:last-child {
     .tryout-table {
         min-width: 620px;
     }
+
+    .draft-table[data-responsive="cards"],
+    .team-table[data-responsive="cards"],
+    .scholarship-table[data-responsive="cards"],
+    .tryout-table[data-responsive="cards"] {
+        min-width: 0;
+        border-collapse: separate;
+        border-spacing: 0 0.85rem;
+        border: 0;
+        box-shadow: none;
+    }
+
+    .draft-table[data-responsive="cards"] thead,
+    .team-table[data-responsive="cards"] thead,
+    .scholarship-table[data-responsive="cards"] thead,
+    .tryout-table[data-responsive="cards"] thead {
+        display: none;
+    }
+
+    .draft-table[data-responsive="cards"],
+    .draft-table[data-responsive="cards"] tbody,
+    .draft-table[data-responsive="cards"] tr,
+    .draft-table[data-responsive="cards"] td,
+    .team-table[data-responsive="cards"],
+    .team-table[data-responsive="cards"] tbody,
+    .team-table[data-responsive="cards"] tr,
+    .team-table[data-responsive="cards"] td,
+    .scholarship-table[data-responsive="cards"],
+    .scholarship-table[data-responsive="cards"] tbody,
+    .scholarship-table[data-responsive="cards"] tr,
+    .scholarship-table[data-responsive="cards"] td,
+    .tryout-table[data-responsive="cards"],
+    .tryout-table[data-responsive="cards"] tbody,
+    .tryout-table[data-responsive="cards"] tr,
+    .tryout-table[data-responsive="cards"] td {
+        display: block;
+        width: 100%;
+    }
+
+    .draft-table[data-responsive="cards"] tr,
+    .team-table[data-responsive="cards"] tr,
+    .scholarship-table[data-responsive="cards"] tr,
+    .tryout-table[data-responsive="cards"] tr {
+        overflow: hidden;
+        border: 1px solid rgba(16, 42, 67, 0.1);
+        border-radius: 18px;
+        background: rgba(255, 255, 255, 0.96);
+        box-shadow: 0 10px 28px rgba(16, 42, 67, 0.08);
+    }
+
+    .draft-table[data-responsive="cards"] td,
+    .team-table[data-responsive="cards"] td,
+    .scholarship-table[data-responsive="cards"] td,
+    .tryout-table[data-responsive="cards"] td {
+        display: grid;
+        grid-template-columns: minmax(7.5rem, 0.42fr) minmax(0, 1fr);
+        gap: 0.75rem;
+        align-items: start;
+        border: 0;
+        border-bottom: 1px solid rgba(16, 42, 67, 0.07);
+        padding: 0.78rem 0.9rem;
+        text-align: left;
+        overflow-wrap: anywhere;
+    }
+
+    .draft-table[data-responsive="cards"] td:first-child,
+    .team-table[data-responsive="cards"] td:first-child,
+    .scholarship-table[data-responsive="cards"] td:first-child,
+    .tryout-table[data-responsive="cards"] td:first-child {
+        background: rgba(47, 111, 235, 0.08);
+        font-weight: 800;
+        color: var(--color-navy);
+    }
+
+    .draft-table[data-responsive="cards"] td:last-child,
+    .team-table[data-responsive="cards"] td:last-child,
+    .scholarship-table[data-responsive="cards"] td:last-child,
+    .tryout-table[data-responsive="cards"] td:last-child {
+        border-bottom: 0;
+    }
+
+    .draft-table[data-responsive="cards"] td::before,
+    .team-table[data-responsive="cards"] td::before,
+    .scholarship-table[data-responsive="cards"] td::before,
+    .tryout-table[data-responsive="cards"] td::before {
+        content: attr(data-label);
+        font-size: 0.78rem;
+        font-weight: 800;
+        letter-spacing: 0.08em;
+        text-transform: uppercase;
+        color: var(--color-text-muted);
+    }
+
+    .draft-table[data-responsive="cards"] td[data-label=""],
+    .draft-table[data-responsive="cards"] td:not([data-label]),
+    .team-table[data-responsive="cards"] td[data-label=""],
+    .team-table[data-responsive="cards"] td:not([data-label]),
+    .scholarship-table[data-responsive="cards"] td[data-label=""],
+    .scholarship-table[data-responsive="cards"] td:not([data-label]),
+    .tryout-table[data-responsive="cards"] td[data-label=""],
+    .tryout-table[data-responsive="cards"] td:not([data-label]) {
+        display: block;
+    }
+
+    .draft-table[data-responsive="cards"] td[data-label=""]::before,
+    .draft-table[data-responsive="cards"] td:not([data-label])::before,
+    .team-table[data-responsive="cards"] td[data-label=""]::before,
+    .team-table[data-responsive="cards"] td:not([data-label])::before,
+    .scholarship-table[data-responsive="cards"] td[data-label=""]::before,
+    .scholarship-table[data-responsive="cards"] td:not([data-label])::before,
+    .tryout-table[data-responsive="cards"] td[data-label=""]::before,
+    .tryout-table[data-responsive="cards"] td:not([data-label])::before {
+        content: none;
+    }
 }
 
 @media (max-width: 380px) {
diff --git a/templates/home/registration.html b/templates/home/registration.html
index 424e4fa..1c5de1c 100644
--- a/templates/home/registration.html
+++ b/templates/home/registration.html
@@ -125,7 +125,7 @@
                             <h3>Assessment Sessions</h3>
                             <p>Tentative sessions are noted; arrive early for check-in.</p>
                         </div>
-                        <table class="tryout-table">
+                        <table class="tryout-table" data-responsive="cards">
                             <thead>
                                 <tr>
                                     <th scope="col">Day</th>
@@ -137,10 +137,10 @@
                             <tbody>
                                 {% for slot in registration.tryouts.schedule %}
                                     <tr{% if slot.tentative %} class="is-tentative"{% endif %}>
-                                        <td>{{ slot.day }}</td>
-                                        <td>{{ slot.date }}</td>
-                                        <td>{{ slot.time }}</td>
-                                        <td>{{ slot.group }}</td>
+                                        <td data-label="Day">{{ slot.day }}</td>
+                                        <td data-label="Date">{{ slot.date }}</td>
+                                        <td data-label="Time">{{ slot.time }}</td>
+                                        <td data-label="Group">{{ slot.group }}</td>
                                     </tr>
                                 {% endfor %}
                             </tbody>
diff --git a/templates/home/tryouts.html b/templates/home/tryouts.html
index 8df192d..6e091a7 100644
--- a/templates/home/tryouts.html
+++ b/templates/home/tryouts.html
@@ -90,7 +90,7 @@
                             <h3>Assessment Sessions</h3>
                             <p>Tentative sessions are noted; arrive early for check-in.</p>
                         </div>
-                        <table class="tryout-table">
+                        <table class="tryout-table" data-responsive="cards">
                             <thead>
                                 <tr>
                                     <th scope="col">Day</th>
@@ -102,10 +102,10 @@
                             <tbody>
                                 {% for slot in tryouts.schedule %}
                                     <tr{% if slot.tentative %} class="is-tentative"{% endif %}>
-                                        <td><span class="tryout-chip">{{ slot.day }}</span></td>
-                                        <td><span class="tryout-chip tryout-chip--subtle">{{ slot.date }}</span></td>
-                                        <td><span class="tryout-time">{{ slot.time }}</span></td>
-                                        <td>
+                                        <td data-label="Day"><span class="tryout-chip">{{ slot.day }}</span></td>
+                                        <td data-label="Date"><span class="tryout-chip tryout-chip--subtle">{{ slot.date }}</span></td>
+                                        <td data-label="Time"><span class="tryout-time">{{ slot.time }}</span></td>
+                                        <td data-label="Group">
                                             <div class="tryout-group">
                                                 <span>{{ slot.group }}</span>
                                                 {% if slot.tentative %}
```

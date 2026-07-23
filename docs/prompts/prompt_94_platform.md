Review the Django project at:

`/Users/eugenelin/dev/vmba0`

Goal: audit all user-facing navigation and links across the application, fix broken or stale routes, and remove confusing references to retired or unrelated apps from the UI.

Context:
- The Analytics dashboard is now the primary operational interface.
- PDP is being retired.
- A known bug exists where the “Imports” button on `/analytics/` links to `/pdp/import/`.
- The correct current destination is `/analytics/imports/`.
- `/players/import/` does not exist and should not be introduced unless the architecture clearly requires it.
- The user-facing UI should not mention or expose internal app names such as “PDP,” “leaguehub,” or other implementation-oriented app labels unless they are intentionally part of the product language.

Please perform a complete review, not just a one-line fix.

Tasks:

1. Audit all user-facing links
- Review templates, shared navigation, dashboards, cards, buttons, breadcrumbs, sidebars, headers, footers, empty states, tables, detail pages, and action menus.
- Check links created through:
  - `{% url %}`
  - hard-coded `href` values
  - redirects in views
  - `reverse()` and `reverse_lazy()`
  - model `get_absolute_url()` methods
  - context processors
  - inclusion tags
  - JavaScript-generated URLs
- Look for stale links to retired, renamed, or unrelated apps.
- Confirm every visible link resolves to an existing route and points to the correct current workflow.

2. Remove PDP references from the UI
- Search for all user-visible references to:
  - `PDP`
  - `pdp`
  - `/pdp/`
  - `pdp:`
- Distinguish between internal implementation references and user-facing references.
- Internal code may remain where still required for compatibility, but users should not see PDP in:
  - page titles
  - headings
  - buttons
  - navigation labels
  - breadcrumbs
  - help text
  - URLs linked from current interfaces
  - error messages
  - templates
- Replace PDP-facing links with the current Analytics route where appropriate.
- Specifically change the Analytics “Imports” link to the named route for `/analytics/imports/`.

3. Review unrelated app references
- Identify any user-facing references to Django app names or legacy subsystem names that could confuse users.
- Examples may include `leaguehub`, `players`, `accounts`, `analytics`, `drafts`, or other internal labels used as product-facing text.
- Do not blindly remove legitimate product sections.
- Replace implementation names with clear user-facing labels where needed, such as:
  - “Player Management”
  - “Imports”
  - “Evaluations”
  - “Draft Management”
  - “User Accounts”
- Preserve established product terminology when it is already clear and intentional.

4. Review route consistency
- Inspect all `urls.py` files and create a map of major user-facing routes and their intended ownership.
- Verify that navigation uses named URLs rather than hard-coded paths wherever practical.
- Flag duplicate, obsolete, compatibility-only, or misleading routes.
- Do not remove compatibility routes unless it is clearly safe.
- Prefer updating visible links so users only enter through current routes.

5. Check permissions and visibility
- Ensure links are only shown to users who can access their destinations.
- Review staff-only, coach-only, player-only, and anonymous navigation.
- Prevent visible buttons that lead to 403, 404, or irrelevant pages for the current user role.

6. Add or update tests
Add focused regression tests covering:
- The Analytics “Imports” button resolves to `/analytics/imports/`.
- No user-facing Analytics template links to `/pdp/`.
- Major dashboard/navigation links reverse successfully.
- Visible navigation links do not point to missing routes.
- Role-specific links are hidden when users lack permission.
- User-facing templates do not contain the text “PDP” unless there is a documented intentional exception.

Prefer robust tests using URL names and rendered responses rather than brittle full-page string snapshots.

7. Run validation
Run:
- the relevant app tests
- the full Django test suite
- `python manage.py check`
- a search for remaining PDP references

Suggested searches:

```bash
grep -RInE 'PDP|pdp:|/pdp/' \
  --exclude-dir=.git \
  --exclude-dir=venv \
  --exclude-dir=node_modules \
  .
```

Also search for hard-coded links:

```bash
grep -RInE 'href=["'\'']/|window\.location|location\.href|reverse\(|reverse_lazy\(' \
  --include='*.html' \
  --include='*.py' \
  --include='*.js' \
  .
```

Be careful not to treat migrations, historical comments, internal module imports, tests of compatibility behavior, or database table names as user-facing defects.

Deliverables:
1. A concise audit summary of what was reviewed.
2. A list of broken, stale, confusing, or misleading links found.
3. The fixes implemented.
4. Any legacy routes or PDP internals intentionally retained, with reasons.
5. Tests added or updated.
6. Commands run and results.
7. Any unresolved risks or follow-up recommendations.

Implementation constraints:
- Keep views thin.
- Reuse existing services and permission helpers.
- Use named URL routes.
- Avoid broad refactors unrelated to navigation.
- Do not rename Django apps or database tables as part of this task.
- Do not remove PDP backend code solely because it is retired from the UI.
- Preserve backward compatibility unless removal is clearly safe and covered by tests.
- Make the smallest coherent set of changes needed to give users a clean, current, consistent interface.

==================================================
Implementation Commit Diff
==================================================

```diff
commit 0f2c91f7896028c1ac1a6d84ccbb02780a63b942
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 23 13:38:16 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 23 13:38:16 2026 -0700

    Clean up platform navigation links
---
 accounts/tests/test_account_operations.py       |   5 +-
 analytics/templatetags/analytics_account_nav.py |  19 +++-
 analytics/tests/test_navigation.py              | 132 ++++++++++++++++++++++++
 pdp/templates/pdp/base.html                     |  33 ++++--
 templates/home/index.html                       |   6 +-
 5 files changed, 179 insertions(+), 16 deletions(-)

diff --git a/accounts/tests/test_account_operations.py b/accounts/tests/test_account_operations.py
index 3012878..4cf714d 100644
--- a/accounts/tests/test_account_operations.py
+++ b/accounts/tests/test_account_operations.py
@@ -1342,7 +1342,10 @@ class AccountOperationsViewTests(TestCase):
         response = self.client.get(reverse("accounts:profile"))

         self.assertEqual(response.status_code, 200)
-        self.assertNotContains(response, reverse("accounts:operations-dashboard"))
+        self.assertNotContains(
+            response, f'href="{reverse("accounts:operations-dashboard")}"'
+        )
+        self.assertNotContains(response, "Account Operations")

     def test_account_create_requires_staff(self):
         self.client.force_login(self.regular)
diff --git a/analytics/templatetags/analytics_account_nav.py b/analytics/templatetags/analytics_account_nav.py
index 9a6a020..4101ea0 100644
--- a/analytics/templatetags/analytics_account_nav.py
+++ b/analytics/templatetags/analytics_account_nav.py
@@ -6,7 +6,6 @@ from analytics.services.permissions import (
     can_view_my_evaluations,
 )

-
 register = template.Library()


@@ -18,3 +17,21 @@ def analytics_account_profile_actions(user):
         "can_view_my_evaluations": can_view_my_evaluations(user),
         "can_review_submitted_evaluations": can_review_submitted_evaluations(user),
     }
+
+
+@register.simple_tag
+def analytics_can_submit_evaluation(user):
+    """Return whether the user should see evaluation submission navigation."""
+    return can_submit_evaluation(user)
+
+
+@register.simple_tag
+def analytics_can_view_my_evaluations(user):
+    """Return whether the user should see player-facing evaluation navigation."""
+    return can_view_my_evaluations(user)
+
+
+@register.simple_tag
+def analytics_can_review_evaluations(user):
+    """Return whether the user should see evaluation review navigation."""
+    return can_review_submitted_evaluations(user)
diff --git a/analytics/tests/test_navigation.py b/analytics/tests/test_navigation.py
new file mode 100644
index 0000000..f8d3cae
--- /dev/null
+++ b/analytics/tests/test_navigation.py
@@ -0,0 +1,132 @@
+from html.parser import HTMLParser
+from urllib.parse import urlsplit
+
+from django.urls import Resolver404, resolve, reverse
+
+from accounts.models import AccountRole
+from accounts.services.profile_service import set_account_role
+from analytics.tests.helpers import TestCase, User
+
+
+class LinkParser(HTMLParser):
+    def __init__(self):
+        super().__init__()
+        self.links = []
+
+    def handle_starttag(self, tag, attrs):
+        if tag != "a":
+            return
+        attr_map = dict(attrs)
+        href = attr_map.get("href")
+        if href:
+            self.links.append(href)
+
+
+def rendered_links(response):
+    parser = LinkParser()
+    parser.feed(response.content.decode())
+    return parser.links
+
+
+class PlatformNavigationTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        set_account_role(self.staff, AccountRole.STAFF)
+        self.coach = User.objects.create_user(username="coach", password="testpass")
+        set_account_role(self.coach, AccountRole.COACH)
+        self.player_user = User.objects.create_user(
+            username="player", password="testpass"
+        )
+        set_account_role(self.player_user, AccountRole.PLAYER)
+
+    def assert_local_links_resolve(self, response):
+        for href in rendered_links(response):
+            if href.startswith(("#", "mailto:", "tel:", "http://", "https://")):
+                continue
+            path = urlsplit(href).path
+            if not path:
+                continue
+            try:
+                resolve(path)
+            except Resolver404 as exc:
+                raise AssertionError(f"Rendered link does not resolve: {href}") from exc
+
+    def test_analytics_import_navigation_uses_current_route(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("analytics:command-center"))
+        links = rendered_links(response)
+
+        self.assertEqual(response.status_code, 200)
+        self.assertIn(reverse("analytics:import-list"), links)
+        self.assertNotIn(reverse("pdp:import-workbench"), links)
+        self.assertNotIn("/pdp/import/", links)
+
+    def test_analytics_pages_do_not_expose_pdp_links_or_text(self):
+        self.client.force_login(self.staff)
+
+        for route_name in (
+            "analytics:command-center",
+            "analytics:import-list",
+            "analytics:evaluation-list",
+            "analytics:evaluation-review-list",
+        ):
+            with self.subTest(route_name=route_name):
+                response = self.client.get(reverse(route_name))
+                self.assertEqual(response.status_code, 200)
+                self.assertNotContains(response, "PDP")
+                self.assertFalse(
+                    any(
+                        urlsplit(href).path.startswith("/pdp/")
+                        for href in rendered_links(response)
+                    ),
+                    f"{route_name} rendered a PDP link.",
+                )
+                self.assert_local_links_resolve(response)
+
+    def test_staff_navigation_links_resolve(self):
+        self.client.force_login(self.staff)
+
+        for route_name in (
+            "analytics:command-center",
+            "accounts:operations-dashboard",
+            "accounts:profile",
+            "seasons:season-list",
+        ):
+            with self.subTest(route_name=route_name):
+                response = self.client.get(reverse(route_name))
+                self.assertEqual(response.status_code, 200)
+                self.assert_local_links_resolve(response)
+
+    def test_non_staff_profile_hides_staff_only_navigation(self):
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("accounts:profile"))
+        links = rendered_links(response)
+
+        self.assertEqual(response.status_code, 200)
+        self.assertNotIn(reverse("analytics:command-center"), links)
+        self.assertNotIn(reverse("accounts:operations-dashboard"), links)
+        self.assertNotIn(reverse("analytics:import-list"), links)
+        self.assertNotIn(reverse("seasons:season-list"), links)
+        self.assertNotIn(reverse("analytics:evaluation-review-list"), links)
+        self.assertFalse(
+            any(urlsplit(href).path.startswith("/pdp/") for href in links),
+            "Non-staff profile rendered a PDP link.",
+        )
+
+    def test_coach_navigation_hides_staff_only_links_but_keeps_review_access(self):
+        self.client.force_login(self.coach)
+
+        response = self.client.get(reverse("accounts:profile"))
+        links = rendered_links(response)
+
+        self.assertEqual(response.status_code, 200)
+        self.assertIn(reverse("analytics:evaluation-list"), links)
+        self.assertIn(reverse("analytics:evaluation-review-list"), links)
+        self.assertNotIn(reverse("analytics:command-center"), links)
+        self.assertNotIn(reverse("accounts:operations-dashboard"), links)
+        self.assertNotIn(reverse("analytics:import-list"), links)
+        self.assertNotIn(reverse("seasons:season-list"), links)
diff --git a/pdp/templates/pdp/base.html b/pdp/templates/pdp/base.html
index 4b42fde..c13526b 100644
--- a/pdp/templates/pdp/base.html
+++ b/pdp/templates/pdp/base.html
@@ -1,5 +1,6 @@
 {% extends "base.html" %}
 {% load static %}
+{% load analytics_account_nav %}

 {% block extra_head %}
     {{ block.super }}
@@ -13,24 +14,34 @@
     <section class="pdp-app">
         <header class="pdp-hero">
             <div>
-                <p class="pdp-kicker">Player Development Platform</p>
-                <h1>{% block pdp_title %}Premium athlete growth system{% endblock %}</h1>
-                <p class="pdp-subtitle">{% block pdp_subtitle %}Track progress, guide development, and keep the experience motivating for players and families.{% endblock %}</p>
+                <p class="pdp-kicker">VCB Platform</p>
+                <h1>{% block pdp_title %}Baseball operations{% endblock %}</h1>
+                <p class="pdp-subtitle">{% block pdp_subtitle %}Manage accounts, seasons, players, evaluations, and baseball operations workflows.{% endblock %}</p>
             </div>
             <nav class="pdp-nav">
                 {% if request.user.is_authenticated %}
                     <a href="/">Site Home</a>
-                    <a href="{% url 'leaguehub:index' %}">League Hub</a>
-                    <a href="{% url 'pdp:home' %}">Home</a>
-                    <a href="{% url 'pdp:coach-dashboard' %}">Coach</a>
-                    <a href="{% url 'pdp:parent-dashboard' %}">Parent</a>
+                    {% analytics_can_submit_evaluation request.user as can_submit_evaluations %}
+                    {% if can_submit_evaluations %}
+                        <a href="{% url 'analytics:evaluation-list' %}">Evaluations</a>
+                    {% endif %}
+                    {% analytics_can_view_my_evaluations request.user as can_view_my_evaluations %}
+                    {% if can_view_my_evaluations %}
+                        <a href="{% url 'analytics:my-evaluations' %}">My Evaluations</a>
+                    {% endif %}
+                    {% analytics_can_review_evaluations request.user as can_review_evaluations %}
+                    {% if can_review_evaluations %}
+                        <a href="{% url 'analytics:evaluation-review-list' %}">Review Evaluations</a>
+                    {% endif %}
                     {% if request.user.is_staff or request.user.is_superuser %}
+                        <a href="{% url 'analytics:command-center' %}">Operations Home</a>
+                        <a href="{% url 'accounts:operations-dashboard' %}">User Accounts</a>
                         <a href="{% url 'seasons:season-list' %}">Seasons</a>
+                        <a href="{% url 'analytics:import-list' %}">Imports</a>
                     {% endif %}
-                    <a href="{% url 'pdp:import-workbench' %}">Imports</a>
-                    <a href="{% url 'pdp:drill-library' %}">Drills</a>
-                    <a href="{% url 'pdp:password-change' %}">Password</a>
-                    <a href="{% url 'pdp:logout' %}">Log out</a>
+                    <a href="{% url 'accounts:profile' %}">Profile</a>
+                    <a href="{% url 'accounts:password-change' %}">Password</a>
+                    <a href="{% url 'accounts:logout' %}">Log out</a>
                 {% endif %}
             </nav>
         </header>
diff --git a/templates/home/index.html b/templates/home/index.html
index 7074a19..a84cd34 100644
--- a/templates/home/index.html
+++ b/templates/home/index.html
@@ -30,7 +30,7 @@
             <div class="hero-actions">
                 <a class="button button--primary" href="{{ hero.cta_primary.url }}">{{ hero.cta_primary.label }}</a>
                 <a class="button button--ghost-inverse" href="{{ hero.cta_secondary.url }}">{{ hero.cta_secondary.label }}</a>
-                <a class="button button--ghost-inverse" href="/leaguehub/">League Hub</a>
+                <a class="button button--ghost-inverse" href="{% url 'leaguehub:index' %}">League Hub</a>
             </div>
         </div>
     </section>
@@ -106,7 +106,7 @@
             <div class="schedule-cta">
                 <a class="button button--primary" href="/registration/">Secure Your Spot</a>
                 <a class="button button--text" href="/programs/">View Full Program Overview</a>
-                <a class="button button--text" href="/leaguehub/">Open League Hub</a>
+                <a class="button button--text" href="{% url 'leaguehub:index' %}">Open League Hub</a>
             </div>
         </div>
     </section>
@@ -240,7 +240,7 @@
             <div class="cta-banner-actions">
                 <a class="button button--primary" href="/registration/">Start Registration</a>
                 <a class="button button--text" href="/programs/">Download Program Details</a>
-                <a class="button button--text" href="/leaguehub/">League Hub</a>
+                <a class="button button--text" href="{% url 'leaguehub:index' %}">League Hub</a>
             </div>
         </div>
     </section>

```

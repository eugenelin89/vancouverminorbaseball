# Prompt 41: Account Management

## User Prompt

```text
You are implementing Platform V1 Account Operations.

Implement Phase A only:

Account Operations Foundation

Do NOT implement Phase B, C, D, E, or F.

Do NOT implement manual account creation yet.

Do NOT implement link management actions yet.

Do NOT implement activation/deactivation actions yet.

Do NOT implement password reset or username-change workflows yet.

==================================================
Before Coding
==================================================

Read:

- docs/ARCHITECTURE.md
- docs/account_management/V1_SUMMARY.md
- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/platform_v1_account_operations.md
- AGENTS.md

Review existing implementation:

- accounts/
- players/
- analytics/
- drafts/
- pdp/

Pay particular attention to:

- accounts.services.permissions
- accounts.services.profile_service
- accounts.services.link_service
- accounts.services.auth_redirect_service
- accounts.views
- accounts.urls
- accounts.templates.accounts.profile.html
- analytics command center/navigation patterns

==================================================
Scope
==================================================

Implement Phase A only.

Phase A goals:

- Account Operations staff dashboard.
- Account user search/list.
- Account user detail page.
- Reusable account query service.
- Account operations orchestration service foundation.
- Permission helpers for staff/superuser account operations.
- Thin views.
- Server-rendered templates.
- Tests.

Expected routes:

- /accounts/
- /accounts/users/
- /accounts/users/<id>/

Expected URL names:

- accounts:operations-dashboard
- accounts:user-list
- accounts:user-detail

==================================================
Architecture Rules
==================================================

accounts owns:

- Account Operations UI
- account search/query services
- account operation orchestration
- account permission helpers

players owns:

- canonical player identity
- player matching
- player imports
- player merge behavior

analytics owns:

- evaluations
- observations
- reports
- Analytics UI

drafts owns:

- draft workflow

Do not bypass subsystem services.

Do not place account-operation business logic in views.

Views should:

- validate permissions
- bind forms
- call services
- render templates

==================================================
Required Services
==================================================

Create:

accounts/services/account_query_service.py

Responsibilities:

- user queryset construction
- user search/filtering
- reusable account list read models if useful
- detail-page account context helpers if useful

Search/filter support:

- search text across username, email, first name, last name
- role
- active status
- staff status
- superuser status
- imported status
- must_change_password
- linked-player status

Use select_related("account_profile") where practical.

Use prefetch_related for player links where practical.

--------------------------------------------------

Create:

accounts/services/account_operations_service.py

This service is the public orchestration boundary for staff account operations.

For Phase A, implement only read-only / foundation helpers.

Do NOT implement mutation workflows yet.

Recommended Phase A helpers:

- get_account_operations_dashboard()
- get_account_list()
- get_account_detail()

If useful, define dataclass read models such as:

- AccountOperationsDashboard
- AccountSummaryCard
- AccountListFilters
- AccountListRow
- AccountDetailContext
- LinkedPlayerRow

This service should call account_query_service and existing account services.

Future phases should extend this service with mutation methods such as:

- create_account_only(...)
- create_player_account(...)
- activate_account(...)
- deactivate_account(...)
- change_role(...)
- change_username(...)
- reset_password(...)
- link_player(...)
- unlink_player(...)

But do NOT implement those mutation methods in Phase A.

==================================================
Permissions
==================================================

Update:

accounts/services/permissions.py

Add helpers if needed:

- can_access_account_operations(user)
- can_view_account_operations_dashboard(user)
- can_view_account_list(user)
- can_view_account_detail(user, target_user)
- can_manage_privileged_accounts(user)

Rules:

- Staff or superuser can access Account Operations.
- Regular authenticated users cannot access staff account operation pages.
- Superuser-only checks should remain available for later phases.
- AccountProfile.role must NOT grant staff access.
- Staff access is based on Django User.is_staff or User.is_superuser.

==================================================
Views
==================================================

Update/create account views as needed.

Implement:

AccountOperationsDashboardView

- staff-only
- renders dashboard cards and issue queues
- calls account_operations_service.get_account_operations_dashboard()

AccountUserListView

- staff-only
- supports GET filters
- calls account_operations_service.get_account_list()

AccountUserDetailView

- staff-only
- shows account details
- linked players
- role
- is_active
- is_staff
- is_superuser
- must_change_password
- created_from_import
- import provenance where available
- calls account_operations_service.get_account_detail()

Do NOT implement POST actions in Phase A.

Do NOT add mutation buttons that perform changes.

It is okay to show disabled/future action links only if clearly marked unavailable, but prefer not to include unavailable actions yet.

==================================================
Templates
==================================================

Create templates as needed:

- accounts/templates/accounts/operations_dashboard.html
- accounts/templates/accounts/user_list.html
- accounts/templates/accounts/user_detail.html
- optional small partials for summary cards/status badges

Keep templates simple and consistent with existing server-rendered PDP/account style.

Dashboard should include summary cards such as:

- Total accounts
- Active accounts
- Inactive accounts
- Imported accounts
- Accounts requiring password change
- Users without player links
- Players without self-linked accounts if reasonably available

Do not implement charts.

Do not implement a reporting engine.

Do not implement caching.

Do not implement audit activity unless already available from existing data.

User list should show:

- username
- name
- email
- role
- active state
- staff/superuser state
- must_change_password
- linked-player count
- imported state
- detail link

User detail should show:

- Django user fields
- account profile fields
- linked players
- relationship
- primary status
- active/inactive link state
- import provenance where relevant

==================================================
Navigation
==================================================

Add an Account Operations link for staff users where appropriate.

Acceptable places:

- account profile page for staff
- Analytics command center/navigation links

Do not make Analytics own account logic.

If adding a link from Analytics, it should simply link to accounts:operations-dashboard.

==================================================
Do NOT Implement
==================================================

Do NOT implement:

- manual account creation
- coach creation workflow
- parent creation workflow
- player account creation workflow
- link creation
- link activation/deactivation
- user activation/deactivation
- role changes
- username changes
- password reset
- bulk operations
- coach import
- account merge
- duplicate account resolution
- player merge
- audit logging
- email invitations
- password reset emails
- portals
- API endpoints
- JavaScript workflows
- charts
- caching
- background jobs
- new models unless absolutely unavoidable

==================================================
Testing
==================================================

Add tests for:

services:

- account query filters by search text
- filters by role
- filters by active status
- filters by staff/superuser status
- filters by imported status
- filters by must_change_password
- filters by linked/unlinked status
- dashboard counts
- user detail context includes profile and linked players
- players without self-linked accounts count if implemented

permissions:

- staff can access account operations
- superuser can access account operations
- regular authenticated user cannot access account operations
- AccountProfile.role=staff without User.is_staff does not grant access

views:

- dashboard requires staff
- user list requires staff
- user detail requires staff
- dashboard renders expected summary cards
- user list renders users and filters
- user detail renders profile and linked players
- non-staff denied or redirected appropriately

regression:

- /accounts/profile/ still works for regular users
- forced password-change middleware still works
- Account Management V1 auth behavior unchanged
- Analytics tests still pass
- Players tests still pass
- Drafts tests still pass
- PDP tests still pass

==================================================
Documentation
==================================================

Update implementation status/checklist only if an existing Account Operations status document exists.

Do not create broad new architecture docs unless necessary.

Do update project_flat_file.txt before finishing, per AGENTS.md.

==================================================
Verification
==================================================

Run:

python manage.py check
python manage.py makemigrations accounts --check
python manage.py test accounts
python manage.py test analytics
python manage.py test players
python manage.py test drafts
python manage.py test pdp
python manage.py test
git diff --check

==================================================
Self Review
==================================================

Before finishing, verify:

- Phase A only was implemented
- account_operations_service is the orchestration boundary
- account_query_service owns filtering/search
- views remain thin
- no mutation workflows were added
- no manual account creation was added
- no password reset was added
- no activation/deactivation was added
- AccountProfile.role does not grant staff access
- no plaintext passwords are displayed
- no new models/migrations were added unless absolutely unavoidable
- no TODO/FIXME placeholders
- no architecture violations
- project_flat_file.txt was updated

==================================================
Final Report
==================================================

Report:

- implementation summary
- files created
- files modified
- migrations added, if any
- services implemented
- views/urls/templates implemented
- dashboard summary cards implemented
- filters implemented
- tests added
- test results
- implementation decisions
- deviations from the engineering plan
- technical debt
- self-review findings
- confirmation that Phase B/C/D/E/F were NOT started
```

## App / Subsystem

account_management

## Work Commit

`8d35427`

## Work Commit Diff

```diff
diff --git a/accounts/services/account_operations_service.py b/accounts/services/account_operations_service.py
new file mode 100644
index 0000000..a1c4c69
--- /dev/null
+++ b/accounts/services/account_operations_service.py
@@ -0,0 +1,193 @@
+from __future__ import annotations
+
+from dataclasses import dataclass
+
+from django.contrib.auth import get_user_model
+from django.urls import reverse
+from django.utils import timezone
+
+from accounts.models import AccountRole, UserPlayerLink
+from accounts.services import account_query_service
+from accounts.services.account_query_service import AccountListFilters
+from accounts.services.role_service import role_label
+
+
+User = get_user_model()
+
+
+@dataclass(frozen=True)
+class AccountSummaryCard:
+    label: str
+    value: int
+    help_text: str = ""
+    url: str = ""
+
+
+@dataclass(frozen=True)
+class AccountListRow:
+    user: User
+    role: str
+    role_label: str
+    linked_player_count: int
+    detail_url: str
+
+
+@dataclass(frozen=True)
+class LinkedPlayerRow:
+    link: UserPlayerLink
+    player: object
+    relationship: str
+    is_primary: bool
+    is_active: bool
+    created_from_import: bool
+    import_label: str
+
+
+@dataclass(frozen=True)
+class AccountOperationsDashboard:
+    summary_cards: list[AccountSummaryCard]
+    users_requiring_password_change: list[AccountListRow]
+    unlinked_users: list[AccountListRow]
+    players_without_self_link_count: int
+    generated_at: object
+
+
+@dataclass(frozen=True)
+class AccountListContext:
+    filters: AccountListFilters
+    rows: list[AccountListRow]
+    role_choices: tuple
+    total_count: int
+
+
+@dataclass(frozen=True)
+class AccountDetailContext:
+    user: User
+    role: str
+    role_label: str
+    linked_players: list[LinkedPlayerRow]
+
+
+def _role_for_user(user: User) -> str:
+    profile = getattr(user, "account_profile", None)
+    if profile:
+        return profile.role
+    if user.is_superuser:
+        return AccountRole.ADMIN
+    if user.is_staff:
+        return AccountRole.STAFF
+    return AccountRole.GUEST_EVALUATOR
+
+
+def _list_row(user: User) -> AccountListRow:
+    role = _role_for_user(user)
+    linked_count = getattr(user, "active_player_link_count", None)
+    if linked_count is None:
+        linked_count = user.player_links.filter(is_active=True).count()
+    return AccountListRow(
+        user=user,
+        role=role,
+        role_label=role_label(role),
+        linked_player_count=linked_count,
+        detail_url=reverse("accounts:user-detail", kwargs={"user_id": user.id}),
+    )
+
+
+def _linked_player_row(link: UserPlayerLink) -> LinkedPlayerRow:
+    import_label = ""
+    if link.import_batch_id:
+        import_label = link.import_batch.original_filename
+    return LinkedPlayerRow(
+        link=link,
+        player=link.player,
+        relationship=link.get_relationship_display(),
+        is_primary=link.is_primary,
+        is_active=link.is_active,
+        created_from_import=link.created_from_import,
+        import_label=import_label,
+    )
+
+
+def get_account_operations_dashboard() -> AccountOperationsDashboard:
+    """Return the read-only Account Operations dashboard context."""
+    users = User.objects.select_related("account_profile")
+    total_accounts = users.count()
+    active_accounts = users.filter(is_active=True).count()
+    inactive_accounts = users.filter(is_active=False).count()
+    imported_accounts = users.filter(account_profile__created_from_import=True).count()
+    password_change_accounts = users.filter(account_profile__must_change_password=True).count()
+    unlinked_users_count = account_query_service.filter_account_users(
+        AccountListFilters(linked_status="unlinked")
+    ).count()
+    players_without_self_link_count = account_query_service.count_players_without_self_link()
+
+    summary_cards = [
+        AccountSummaryCard("Total accounts", total_accounts, "All Django user accounts.", reverse("accounts:user-list")),
+        AccountSummaryCard("Active accounts", active_accounts, "Accounts that can authenticate.", reverse("accounts:user-list") + "?active=yes"),
+        AccountSummaryCard("Inactive accounts", inactive_accounts, "Accounts blocked from login.", reverse("accounts:user-list") + "?active=no"),
+        AccountSummaryCard("Imported accounts", imported_accounts, "Accounts created from player imports.", reverse("accounts:user-list") + "?imported=yes"),
+        AccountSummaryCard(
+            "Password change required",
+            password_change_accounts,
+            "Users who must change a temporary password.",
+            reverse("accounts:user-list") + "?must_change_password=yes",
+        ),
+        AccountSummaryCard(
+            "Users without player links",
+            unlinked_users_count,
+            "Accounts with no active player links.",
+            reverse("accounts:user-list") + "?linked=unlinked",
+        ),
+        AccountSummaryCard(
+            "Players without self-linked accounts",
+            players_without_self_link_count,
+            "Active players without an active self-linked user account.",
+        ),
+    ]
+
+    password_rows = [
+        _list_row(user)
+        for user in account_query_service.filter_account_users(AccountListFilters(must_change_password="yes"))[:10]
+    ]
+    unlinked_rows = [
+        _list_row(user)
+        for user in account_query_service.filter_account_users(AccountListFilters(linked_status="unlinked"))[:10]
+    ]
+    return AccountOperationsDashboard(
+        summary_cards=summary_cards,
+        users_requiring_password_change=password_rows,
+        unlinked_users=unlinked_rows,
+        players_without_self_link_count=players_without_self_link_count,
+        generated_at=timezone.now(),
+    )
+
+
+def get_account_list(filters: AccountListFilters) -> AccountListContext:
+    """Return read-only account list rows for staff account operations."""
+    queryset = account_query_service.filter_account_users(filters)
+    rows = [_list_row(user) for user in queryset]
+    return AccountListContext(
+        filters=filters,
+        rows=rows,
+        role_choices=AccountRole.choices,
+        total_count=len(rows),
+    )
+
+
+def get_account_detail(user_id: int) -> AccountDetailContext:
+    """Return read-only detail context for one account."""
+    user = account_query_service.get_account_user(user_id)
+    links = user.player_links.select_related("player", "import_batch").order_by(
+        "-is_active",
+        "relationship",
+        "player__last_name",
+        "player__first_name",
+        "id",
+    )
+    role = _role_for_user(user)
+    return AccountDetailContext(
+        user=user,
+        role=role,
+        role_label=role_label(role),
+        linked_players=[_linked_player_row(link) for link in links],
+    )
diff --git a/accounts/services/account_query_service.py b/accounts/services/account_query_service.py
new file mode 100644
index 0000000..1d97ab5
--- /dev/null
+++ b/accounts/services/account_query_service.py
@@ -0,0 +1,118 @@
+from __future__ import annotations
+
+from dataclasses import dataclass
+
+from django.contrib.auth import get_user_model
+from django.db.models import Count, Exists, OuterRef, Q
+
+from accounts.models import AccountRole, UserPlayerLink, UserPlayerRelationship
+from players.models import Player
+
+
+User = get_user_model()
+
+
+@dataclass(frozen=True)
+class AccountListFilters:
+    search: str = ""
+    role: str = ""
+    active_status: str = ""
+    staff_status: str = ""
+    superuser_status: str = ""
+    imported_status: str = ""
+    must_change_password: str = ""
+    linked_status: str = ""
+
+
+def parse_account_list_filters(params) -> AccountListFilters:
+    """Parse account list GET parameters into normalized filter values."""
+    return AccountListFilters(
+        search=str(params.get("q", "") or "").strip(),
+        role=str(params.get("role", "") or "").strip(),
+        active_status=str(params.get("active", "") or "").strip(),
+        staff_status=str(params.get("staff", "") or "").strip(),
+        superuser_status=str(params.get("superuser", "") or "").strip(),
+        imported_status=str(params.get("imported", "") or "").strip(),
+        must_change_password=str(params.get("must_change_password", "") or "").strip(),
+        linked_status=str(params.get("linked", "") or "").strip(),
+    )
+
+
+def _truthy_filter_value(value: str) -> bool | None:
+    if value in {"yes", "true", "1"}:
+        return True
+    if value in {"no", "false", "0"}:
+        return False
+    return None
+
+
+def account_user_queryset():
+    """Return the base queryset for account operation user lists."""
+    active_link = UserPlayerLink.objects.filter(user=OuterRef("pk"), is_active=True)
+    return (
+        User.objects.select_related("account_profile", "account_profile__import_batch")
+        .prefetch_related("player_links__player", "player_links__import_batch")
+        .annotate(
+            active_player_link_count=Count("player_links", filter=Q(player_links__is_active=True), distinct=True),
+            has_active_player_link=Exists(active_link),
+        )
+        .order_by("username", "id")
+    )
+
+
+def filter_account_users(filters: AccountListFilters):
+    """Apply account operation search and filters to users."""
+    queryset = account_user_queryset()
+
+    if filters.search:
+        queryset = queryset.filter(
+            Q(username__icontains=filters.search)
+            | Q(email__icontains=filters.search)
+            | Q(first_name__icontains=filters.search)
+            | Q(last_name__icontains=filters.search)
+        )
+
+    if filters.role in {choice.value for choice in AccountRole}:
+        queryset = queryset.filter(account_profile__role=filters.role)
+
+    active = _truthy_filter_value(filters.active_status)
+    if active is not None:
+        queryset = queryset.filter(is_active=active)
+
+    staff = _truthy_filter_value(filters.staff_status)
+    if staff is not None:
+        queryset = queryset.filter(is_staff=staff)
+
+    superuser = _truthy_filter_value(filters.superuser_status)
+    if superuser is not None:
+        queryset = queryset.filter(is_superuser=superuser)
+
+    imported = _truthy_filter_value(filters.imported_status)
+    if imported is not None:
+        queryset = queryset.filter(account_profile__created_from_import=imported)
+
+    must_change = _truthy_filter_value(filters.must_change_password)
+    if must_change is not None:
+        queryset = queryset.filter(account_profile__must_change_password=must_change)
+
+    if filters.linked_status == "linked":
+        queryset = queryset.filter(has_active_player_link=True)
+    elif filters.linked_status == "unlinked":
+        queryset = queryset.filter(has_active_player_link=False)
+
+    return queryset
+
+
+def get_account_user(user_id: int):
+    """Return one user with account-operation related data loaded."""
+    return account_user_queryset().get(pk=user_id)
+
+
+def count_players_without_self_link() -> int:
+    """Return active players without an active primary self-linked user account."""
+    self_link = UserPlayerLink.objects.filter(
+        player=OuterRef("pk"),
+        relationship=UserPlayerRelationship.SELF,
+        is_active=True,
+    )
+    return Player.objects.filter(is_active=True).annotate(has_self_link=Exists(self_link)).filter(has_self_link=False).count()
diff --git a/accounts/services/permissions.py b/accounts/services/permissions.py
index 3ec6cf9..d85ec64 100644
--- a/accounts/services/permissions.py
+++ b/accounts/services/permissions.py
@@ -7,6 +7,26 @@ def can_manage_accounts(user) -> bool:
     return is_staff_or_admin(user)


+def can_access_account_operations(user) -> bool:
+    return is_staff_or_admin(user)
+
+
+def can_view_account_operations_dashboard(user) -> bool:
+    return can_access_account_operations(user)
+
+
+def can_view_account_list(user) -> bool:
+    return can_access_account_operations(user)
+
+
+def can_view_account_detail(user, target_user) -> bool:
+    return bool(target_user and can_access_account_operations(user))
+
+
+def can_manage_privileged_accounts(user) -> bool:
+    return bool(user and user.is_authenticated and user.is_superuser)
+
+
 def can_view_account_profile(user, profile) -> bool:
     if is_staff_or_admin(user):
         return True
diff --git a/accounts/templates/accounts/operations_dashboard.html b/accounts/templates/accounts/operations_dashboard.html
new file mode 100644
index 0000000..93f7de6
--- /dev/null
+++ b/accounts/templates/accounts/operations_dashboard.html
@@ -0,0 +1,70 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Account Operations{% endblock %}
+{% block pdp_subtitle %}Read-only staff dashboard for account health and account lookup.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>Summary</h2>
+        <div class="pdp-grid">
+            {% for card in summary_cards %}
+                <section>
+                    <h3>{{ card.label }}</h3>
+                    <p><strong>{{ card.value }}</strong></p>
+                    <p>{{ card.help_text }}</p>
+                    {% if card.url %}
+                        <a class="button button--ghost" href="{{ card.url }}">Open</a>
+                    {% endif %}
+                </section>
+            {% endfor %}
+        </div>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Accounts Requiring Password Change</h2>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr><th>Username</th><th>Name</th><th>Role</th><th></th></tr>
+                </thead>
+                <tbody>
+                    {% for row in users_requiring_password_change %}
+                        <tr>
+                            <td>{{ row.user.username }}</td>
+                            <td>{{ row.user.get_full_name|default:"-" }}</td>
+                            <td>{{ row.role_label }}</td>
+                            <td><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="4">No accounts currently require password change.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Users Without Player Links</h2>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr><th>Username</th><th>Name</th><th>Role</th><th></th></tr>
+                </thead>
+                <tbody>
+                    {% for row in unlinked_users %}
+                        <tr>
+                            <td>{{ row.user.username }}</td>
+                            <td>{{ row.user.get_full_name|default:"-" }}</td>
+                            <td>{{ row.role_label }}</td>
+                            <td><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="4">No unlinked users found.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    </article>
+</section>
+{% endblock %}
diff --git a/accounts/templates/accounts/profile.html b/accounts/templates/accounts/profile.html
index 006c412..b81b7c9 100644
--- a/accounts/templates/accounts/profile.html
+++ b/accounts/templates/accounts/profile.html
@@ -25,6 +25,9 @@
                 {% endfor %}
             </ul>
         {% endif %}
+        {% if request.user.is_staff or request.user.is_superuser %}
+            <p><a class="button button--ghost" href="{% url 'accounts:operations-dashboard' %}">Account Operations</a></p>
+        {% endif %}
     </article>
 </section>
 {% endblock %}
diff --git a/accounts/templates/accounts/user_detail.html b/accounts/templates/accounts/user_detail.html
new file mode 100644
index 0000000..6633dc8
--- /dev/null
+++ b/accounts/templates/accounts/user_detail.html
@@ -0,0 +1,87 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Account Detail{% endblock %}
+{% block pdp_subtitle %}Read-only account and linked player context.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>{{ target_user.get_full_name|default:target_user.username }}</h2>
+        <dl class="pdp-definition-list">
+            <dt>Username</dt>
+            <dd>{{ target_user.username }}</dd>
+            <dt>Email</dt>
+            <dd>{{ target_user.email|default:"-" }}</dd>
+            <dt>First name</dt>
+            <dd>{{ target_user.first_name|default:"-" }}</dd>
+            <dt>Last name</dt>
+            <dd>{{ target_user.last_name|default:"-" }}</dd>
+            <dt>Role</dt>
+            <dd>{{ account_detail.role_label }}</dd>
+            <dt>Active</dt>
+            <dd>{% if target_user.is_active %}Yes{% else %}No{% endif %}</dd>
+            <dt>Staff</dt>
+            <dd>{% if target_user.is_staff %}Yes{% else %}No{% endif %}</dd>
+            <dt>Superuser</dt>
+            <dd>{% if target_user.is_superuser %}Yes{% else %}No{% endif %}</dd>
+            <dt>Password change required</dt>
+            <dd>
+                {% if target_user.account_profile.must_change_password %}
+                    Yes
+                {% else %}
+                    No
+                {% endif %}
+            </dd>
+            <dt>Created from import</dt>
+            <dd>
+                {% if target_user.account_profile.created_from_import %}
+                    Yes
+                {% else %}
+                    No
+                {% endif %}
+            </dd>
+            {% if target_user.account_profile.import_batch %}
+                <dt>Import batch</dt>
+                <dd>{{ target_user.account_profile.import_batch.original_filename }}</dd>
+            {% endif %}
+            <dt>Date joined</dt>
+            <dd>{{ target_user.date_joined }}</dd>
+            <dt>Last login</dt>
+            <dd>{{ target_user.last_login|default:"-" }}</dd>
+        </dl>
+        <p><a class="button button--ghost" href="{% url 'accounts:user-list' %}">Back to users</a></p>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Linked Players</h2>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr>
+                        <th>Player</th>
+                        <th>Relationship</th>
+                        <th>Primary</th>
+                        <th>Active</th>
+                        <th>Imported</th>
+                        <th>Import Batch</th>
+                    </tr>
+                </thead>
+                <tbody>
+                    {% for row in linked_players %}
+                        <tr>
+                            <td>{{ row.player.display_name }}</td>
+                            <td>{{ row.relationship }}</td>
+                            <td>{% if row.is_primary %}Yes{% else %}No{% endif %}</td>
+                            <td>{% if row.is_active %}Active{% else %}Inactive{% endif %}</td>
+                            <td>{% if row.created_from_import %}Yes{% else %}No{% endif %}</td>
+                            <td>{{ row.import_label|default:"-" }}</td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="6">No linked players found.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    </article>
+</section>
+{% endblock %}
diff --git a/accounts/templates/accounts/user_list.html b/accounts/templates/accounts/user_list.html
new file mode 100644
index 0000000..e78f575
--- /dev/null
+++ b/accounts/templates/accounts/user_list.html
@@ -0,0 +1,132 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Account Users{% endblock %}
+{% block pdp_subtitle %}Search and filter platform accounts.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>Filters</h2>
+        <form method="get" class="pdp-form">
+            <label>
+                Search
+                <input type="text" name="q" value="{{ filters.search }}" placeholder="Username, email, first, or last name">
+            </label>
+            <label>
+                Role
+                <select name="role">
+                    <option value="">Any role</option>
+                    {% for value, label in role_choices %}
+                        <option value="{{ value }}"{% if filters.role == value %} selected{% endif %}>{{ label }}</option>
+                    {% endfor %}
+                </select>
+            </label>
+            <label>
+                Active
+                <select name="active">
+                    <option value="">Any</option>
+                    <option value="yes"{% if filters.active_status == "yes" %} selected{% endif %}>Active</option>
+                    <option value="no"{% if filters.active_status == "no" %} selected{% endif %}>Inactive</option>
+                </select>
+            </label>
+            <label>
+                Staff
+                <select name="staff">
+                    <option value="">Any</option>
+                    <option value="yes"{% if filters.staff_status == "yes" %} selected{% endif %}>Staff</option>
+                    <option value="no"{% if filters.staff_status == "no" %} selected{% endif %}>Not staff</option>
+                </select>
+            </label>
+            <label>
+                Superuser
+                <select name="superuser">
+                    <option value="">Any</option>
+                    <option value="yes"{% if filters.superuser_status == "yes" %} selected{% endif %}>Superuser</option>
+                    <option value="no"{% if filters.superuser_status == "no" %} selected{% endif %}>Not superuser</option>
+                </select>
+            </label>
+            <label>
+                Imported
+                <select name="imported">
+                    <option value="">Any</option>
+                    <option value="yes"{% if filters.imported_status == "yes" %} selected{% endif %}>Imported</option>
+                    <option value="no"{% if filters.imported_status == "no" %} selected{% endif %}>Not imported</option>
+                </select>
+            </label>
+            <label>
+                Password
+                <select name="must_change_password">
+                    <option value="">Any</option>
+                    <option value="yes"{% if filters.must_change_password == "yes" %} selected{% endif %}>Change required</option>
+                    <option value="no"{% if filters.must_change_password == "no" %} selected{% endif %}>No change required</option>
+                </select>
+            </label>
+            <label>
+                Player Links
+                <select name="linked">
+                    <option value="">Any</option>
+                    <option value="linked"{% if filters.linked_status == "linked" %} selected{% endif %}>Linked</option>
+                    <option value="unlinked"{% if filters.linked_status == "unlinked" %} selected{% endif %}>Unlinked</option>
+                </select>
+            </label>
+            <button class="button button--primary" type="submit">Apply</button>
+            <a class="button button--ghost" href="{% url 'accounts:user-list' %}">Reset</a>
+        </form>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Results</h2>
+        <p>{{ total_count }} account{{ total_count|pluralize }} found.</p>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr>
+                        <th>Username</th>
+                        <th>Name</th>
+                        <th>Email</th>
+                        <th>Role</th>
+                        <th>Active</th>
+                        <th>Staff</th>
+                        <th>Superuser</th>
+                        <th>Password Change</th>
+                        <th>Player Links</th>
+                        <th>Imported</th>
+                        <th></th>
+                    </tr>
+                </thead>
+                <tbody>
+                    {% for row in rows %}
+                        <tr>
+                            <td>{{ row.user.username }}</td>
+                            <td>{{ row.user.get_full_name|default:"-" }}</td>
+                            <td>{{ row.user.email|default:"-" }}</td>
+                            <td>{{ row.role_label }}</td>
+                            <td>{% if row.user.is_active %}Active{% else %}Inactive{% endif %}</td>
+                            <td>{% if row.user.is_staff %}Yes{% else %}No{% endif %}</td>
+                            <td>{% if row.user.is_superuser %}Yes{% else %}No{% endif %}</td>
+                            <td>
+                                {% if row.user.account_profile.must_change_password %}
+                                    Required
+                                {% else %}
+                                    No
+                                {% endif %}
+                            </td>
+                            <td>{{ row.linked_player_count }}</td>
+                            <td>
+                                {% if row.user.account_profile.created_from_import %}
+                                    Yes
+                                {% else %}
+                                    No
+                                {% endif %}
+                            </td>
+                            <td><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="11">No accounts match these filters.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    </article>
+</section>
+{% endblock %}
diff --git a/accounts/tests.py b/accounts/tests.py
index 983d746..7640f19 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -4,10 +4,16 @@ from django.conf import settings
 from django.core.exceptions import ValidationError
 from django.db import IntegrityError, transaction
 from django.test import TestCase
-from django.urls import NoReverseMatch, reverse
+from django.urls import reverse
 from django.contrib.auth import SESSION_KEY

 from accounts.models import AccountProfile, AccountRole, UserPlayerLink, UserPlayerRelationship
+from accounts.services.account_operations_service import (
+    get_account_detail,
+    get_account_list,
+    get_account_operations_dashboard,
+)
+from accounts.services.account_query_service import AccountListFilters, count_players_without_self_link, filter_account_users
 from accounts.services.auth_redirect_service import (
     ACCOUNT_LOGIN_PATH,
     ACCOUNT_LOGOUT_PATH,
@@ -20,9 +26,14 @@ from accounts.services.auth_redirect_service import (
 )
 from accounts.services.email_service import emails_equal, find_existing_email_user, normalize_email
 from accounts.services.permissions import (
+    can_access_account_operations,
     can_change_account_role,
     can_manage_accounts,
+    can_manage_privileged_accounts,
     can_submit_evaluations,
+    can_view_account_detail,
+    can_view_account_list,
+    can_view_account_operations_dashboard,
     can_view_account_profile,
 )
 from accounts.services.link_service import (
@@ -111,6 +122,7 @@ class AccountPermissionTests(TestCase):
     def setUp(self):
         self.user = User.objects.create_user(username="user", password="testpass")
         self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
+        self.superuser = User.objects.create_superuser(username="admin", password="testpass")
         self.profile = get_or_create_account_profile(self.user)

     def test_staff_admin_permissions_use_django_flags(self):
@@ -119,6 +131,25 @@ class AccountPermissionTests(TestCase):
         self.assertTrue(can_manage_accounts(self.staff))
         self.assertTrue(can_change_account_role(self.staff))

+    def test_account_operations_permissions_use_django_staff_flags(self):
+        self.profile.role = AccountRole.STAFF
+        self.profile.save(update_fields=["role", "updated_at"])
+
+        self.assertFalse(can_access_account_operations(self.user))
+        self.assertFalse(can_view_account_operations_dashboard(self.user))
+        self.assertFalse(can_view_account_list(self.user))
+        self.assertFalse(can_view_account_detail(self.user, self.staff))
+        self.assertTrue(can_access_account_operations(self.staff))
+        self.assertTrue(can_view_account_operations_dashboard(self.staff))
+        self.assertTrue(can_view_account_list(self.staff))
+        self.assertTrue(can_view_account_detail(self.staff, self.user))
+        self.assertTrue(can_access_account_operations(self.superuser))
+
+    def test_privileged_account_management_is_superuser_only(self):
+        self.assertFalse(can_manage_privileged_accounts(self.user))
+        self.assertFalse(can_manage_privileged_accounts(self.staff))
+        self.assertTrue(can_manage_privileged_accounts(self.superuser))
+
     def test_regular_user_can_view_own_profile_but_not_manage_accounts(self):
         other = User.objects.create_user(username="other", password="testpass")

@@ -147,6 +178,120 @@ class AccountAdminTests(TestCase):
         self.assertIn("updated_at", link_admin.readonly_fields)


+class AccountOperationsServiceTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
+        self.coach = User.objects.create_user(
+            username="coach.one",
+            password="testpass",
+            first_name="Coach",
+            last_name="One",
+            email="coach@example.com",
+        )
+        self.player_user = User.objects.create_user(
+            username="alex.player",
+            password="testpass",
+            first_name="Alex",
+            last_name="Player",
+            email="alex@example.com",
+        )
+        self.inactive_user = User.objects.create_user(username="inactive", password="testpass", is_active=False)
+        self.import_batch = PlayerImportBatch.objects.create(
+            source="manual_staff_csv",
+            original_filename="players.csv",
+            uploaded_by=self.staff,
+        )
+        set_account_role(self.coach, AccountRole.COACH)
+        player_profile = set_account_role(self.player_user, AccountRole.PLAYER)
+        player_profile.created_from_import = True
+        player_profile.import_batch = self.import_batch
+        player_profile.must_change_password = True
+        player_profile.save(
+            update_fields=["created_from_import", "import_batch", "must_change_password", "updated_at"]
+        )
+        get_or_create_account_profile(self.inactive_user)
+        self.player = Player.objects.create(first_name="Alex", last_name="Player", birthdate="2012-05-01")
+        self.unlinked_player = Player.objects.create(first_name="No", last_name="Account")
+        link_user_to_player(
+            self.player_user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            created_from_import=True,
+            import_batch=self.import_batch,
+        )
+
+    def usernames_for_filters(self, **kwargs):
+        return [user.username for user in filter_account_users(AccountListFilters(**kwargs))]
+
+    def test_account_query_filters_by_search_text(self):
+        self.assertEqual(self.usernames_for_filters(search="coach@example.com"), ["coach.one"])
+        self.assertEqual(self.usernames_for_filters(search="Alex"), ["alex.player"])
+
+    def test_account_query_filters_by_role(self):
+        self.assertEqual(self.usernames_for_filters(role=AccountRole.COACH), ["coach.one"])
+        self.assertEqual(self.usernames_for_filters(role=AccountRole.PLAYER), ["alex.player"])
+
+    def test_account_query_filters_by_active_status(self):
+        self.assertEqual(self.usernames_for_filters(active_status="no"), ["inactive"])
+
+    def test_account_query_filters_by_staff_and_superuser_status(self):
+        admin_user = User.objects.create_superuser(username="admin", password="testpass")
+        get_or_create_account_profile(admin_user)
+
+        self.assertEqual(self.usernames_for_filters(staff_status="yes"), ["admin", "staff"])
+        self.assertEqual(self.usernames_for_filters(superuser_status="yes"), ["admin"])
+
+    def test_account_query_filters_by_imported_and_password_status(self):
+        self.assertEqual(self.usernames_for_filters(imported_status="yes"), ["alex.player"])
+        self.assertEqual(self.usernames_for_filters(must_change_password="yes"), ["alex.player"])
+
+    def test_account_query_filters_by_linked_status(self):
+        self.assertEqual(self.usernames_for_filters(linked_status="linked"), ["alex.player"])
+        self.assertCountEqual(
+            self.usernames_for_filters(linked_status="unlinked"),
+            ["coach.one", "inactive", "staff"],
+        )
+
+    def test_dashboard_counts_include_account_health_metrics(self):
+        dashboard = get_account_operations_dashboard()
+        cards = {card.label: card.value for card in dashboard.summary_cards}
+
+        self.assertEqual(cards["Total accounts"], 4)
+        self.assertEqual(cards["Active accounts"], 3)
+        self.assertEqual(cards["Inactive accounts"], 1)
+        self.assertEqual(cards["Imported accounts"], 1)
+        self.assertEqual(cards["Password change required"], 1)
+        self.assertEqual(cards["Users without player links"], 3)
+        self.assertEqual(cards["Players without self-linked accounts"], 1)
+        self.assertEqual(dashboard.users_requiring_password_change[0].user, self.player_user)
+
+    def test_account_list_context_returns_rows_and_choices(self):
+        context = get_account_list(AccountListFilters(role=AccountRole.COACH))
+
+        self.assertEqual(context.total_count, 1)
+        self.assertEqual(context.rows[0].user, self.coach)
+        self.assertEqual(context.rows[0].role_label, "Coach")
+        self.assertIn((AccountRole.COACH, "Coach"), context.role_choices)
+
+    def test_account_detail_context_includes_profile_and_linked_players(self):
+        context = get_account_detail(self.player_user.id)
+
+        self.assertEqual(context.user, self.player_user)
+        self.assertEqual(context.role, AccountRole.PLAYER)
+        self.assertEqual(context.role_label, "Player")
+        self.assertEqual(len(context.linked_players), 1)
+        linked = context.linked_players[0]
+        self.assertEqual(linked.player, self.player)
+        self.assertEqual(linked.relationship, "Self")
+        self.assertTrue(linked.is_primary)
+        self.assertTrue(linked.is_active)
+        self.assertTrue(linked.created_from_import)
+        self.assertEqual(linked.import_label, "players.csv")
+
+    def test_players_without_self_link_count(self):
+        self.assertEqual(count_players_without_self_link(), 1)
+
+
 class UserPlayerLinkModelTests(TestCase):
     def setUp(self):
         self.user = User.objects.create_user(username="player", password="testpass")
@@ -862,6 +1007,106 @@ class AccountAuthViewTests(TestCase):
         self.assertContains(response, "Guest Evaluator")


+class AccountOperationsViewTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
+        self.superuser = User.objects.create_superuser(username="admin", password="testpass")
+        self.regular = User.objects.create_user(username="regular", password="testpass")
+        self.coach = User.objects.create_user(
+            username="coach.one",
+            password="testpass",
+            first_name="Coach",
+            last_name="One",
+            email="coach@example.com",
+        )
+        set_account_role(self.coach, AccountRole.COACH)
+        profile = get_or_create_account_profile(self.regular)
+        profile.role = AccountRole.STAFF
+        profile.save(update_fields=["role", "updated_at"])
+        self.player = Player.objects.create(first_name="Alex", last_name="Player")
+        link_user_to_player(self.coach, self.player, relationship=UserPlayerRelationship.COACH, is_primary=False)
+
+    def test_dashboard_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:operations-dashboard"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_superuser_can_access_dashboard(self):
+        self.client.force_login(self.superuser)
+
+        response = self.client.get(reverse("accounts:operations-dashboard"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account Operations")
+
+    def test_dashboard_renders_expected_summary_cards(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:operations-dashboard"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Total accounts")
+        self.assertContains(response, "Active accounts")
+        self.assertContains(response, "Inactive accounts")
+        self.assertContains(response, "Password change required")
+        self.assertContains(response, "Users without player links")
+        self.assertContains(response, "Players without self-linked accounts")
+
+    def test_user_list_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:user-list"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_user_list_renders_users_and_filters(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:user-list"), {"q": "coach", "role": AccountRole.COACH})
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account Users")
+        self.assertContains(response, "coach.one")
+        self.assertContains(response, "Coach")
+        self.assertNotContains(response, "regular")
+
+    def test_user_detail_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_user_detail_renders_profile_and_linked_players(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "coach.one")
+        self.assertContains(response, "coach@example.com")
+        self.assertContains(response, "Coach")
+        self.assertContains(response, "Alex Player")
+
+    def test_profile_page_links_staff_to_account_operations(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:profile"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, reverse("accounts:operations-dashboard"))
+
+    def test_profile_page_does_not_link_regular_user_to_account_operations(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:profile"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertNotContains(response, reverse("accounts:operations-dashboard"))
+
+
 class AccountPasswordMiddlewareTests(TestCase):
     def setUp(self):
         self.user = User.objects.create_user(username="user", password="testpass")
@@ -967,6 +1212,6 @@ class AccountPdpCoexistenceTests(TestCase):
         self.assertEqual(settings.LOGIN_URL, ACCOUNT_LOGIN_PATH)
         self.assertEqual(settings.LOGIN_REDIRECT_URL, ACCOUNT_PROFILE_PATH)

-    def test_no_staff_account_management_routes_exist_yet(self):
-        with self.assertRaises(NoReverseMatch):
-            reverse("accounts:account-list")
+    def test_account_operations_routes_are_platform_account_routes(self):
+        self.assertEqual(reverse("accounts:operations-dashboard"), "/accounts/")
+        self.assertEqual(reverse("accounts:user-list"), "/accounts/users/")
diff --git a/accounts/urls.py b/accounts/urls.py
index af8980c..535afe5 100644
--- a/accounts/urls.py
+++ b/accounts/urls.py
@@ -1,13 +1,24 @@
 from django.urls import path

-from accounts.views import AccountLoginView, AccountLogoutView, AccountPasswordChangeView, AccountProfileView
+from accounts.views import (
+    AccountLoginView,
+    AccountLogoutView,
+    AccountOperationsDashboardView,
+    AccountPasswordChangeView,
+    AccountProfileView,
+    AccountUserDetailView,
+    AccountUserListView,
+)


 app_name = "accounts"

 urlpatterns = [
+    path("", AccountOperationsDashboardView.as_view(), name="operations-dashboard"),
     path("login/", AccountLoginView.as_view(), name="login"),
     path("logout/", AccountLogoutView.as_view(), name="logout"),
     path("password/", AccountPasswordChangeView.as_view(), name="password-change"),
     path("profile/", AccountProfileView.as_view(), name="profile"),
+    path("users/", AccountUserListView.as_view(), name="user-list"),
+    path("users/<int:user_id>/", AccountUserDetailView.as_view(), name="user-detail"),
 ]
diff --git a/accounts/views.py b/accounts/views.py
index 2cd00f4..b74e5e9 100644
--- a/accounts/views.py
+++ b/accounts/views.py
@@ -1,10 +1,17 @@
 from django.contrib import messages
 from django.contrib.auth import update_session_auth_hash
-from django.contrib.auth.mixins import LoginRequiredMixin
+from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
 from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
+from django.core.exceptions import PermissionDenied
 from django.shortcuts import redirect
 from django.views.generic import TemplateView

+from accounts.services.account_operations_service import (
+    get_account_detail,
+    get_account_list,
+    get_account_operations_dashboard,
+)
+from accounts.services.account_query_service import parse_account_list_filters
 from accounts.services.auth_redirect_service import (
     ACCOUNT_LOGIN_PATH,
     ACCOUNT_PASSWORD_PATH,
@@ -13,10 +20,20 @@ from accounts.services.auth_redirect_service import (
 )
 from accounts.services.link_service import get_players_for_user
 from accounts.services.password_service import clear_password_change_required
+from accounts.services.permissions import (
+    can_view_account_detail,
+    can_view_account_list,
+    can_view_account_operations_dashboard,
+)
 from accounts.services.profile_service import get_account_role
 from accounts.services.role_service import role_label


+class AccountOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
+    def test_func(self):
+        return can_view_account_operations_dashboard(self.request.user)
+
+
 class AccountLoginView(LoginView):
     template_name = "accounts/login.html"

@@ -59,3 +76,61 @@ class AccountProfileView(LoginRequiredMixin, TemplateView):
             }
         )
         return context
+
+
+class AccountOperationsDashboardView(AccountOperationsStaffRequiredMixin, TemplateView):
+    template_name = "accounts/operations_dashboard.html"
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        dashboard = get_account_operations_dashboard()
+        context.update(
+            {
+                "dashboard": dashboard,
+                "summary_cards": dashboard.summary_cards,
+                "users_requiring_password_change": dashboard.users_requiring_password_change,
+                "unlinked_users": dashboard.unlinked_users,
+            }
+        )
+        return context
+
+
+class AccountUserListView(AccountOperationsStaffRequiredMixin, TemplateView):
+    template_name = "accounts/user_list.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        if not can_view_account_list(request.user):
+            raise PermissionDenied
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        filters = parse_account_list_filters(self.request.GET)
+        account_list = get_account_list(filters)
+        context.update(
+            {
+                "account_list": account_list,
+                "filters": account_list.filters,
+                "rows": account_list.rows,
+                "role_choices": account_list.role_choices,
+                "total_count": account_list.total_count,
+            }
+        )
+        return context
+
+
+class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
+    template_name = "accounts/user_detail.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        self.account_detail = get_account_detail(kwargs["user_id"])
+        if not can_view_account_detail(request.user, self.account_detail.user):
+            raise PermissionDenied
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["account_detail"] = self.account_detail
+        context["target_user"] = self.account_detail.user
+        context["linked_players"] = self.account_detail.linked_players
+        return context
diff --git a/analytics/services/reporting_service.py b/analytics/services/reporting_service.py
index 6f22e90..43a7c4f 100644
--- a/analytics/services/reporting_service.py
+++ b/analytics/services/reporting_service.py
@@ -85,6 +85,7 @@ def _navigation_links() -> list[NavigationLink]:
         NavigationLink("Import Players", reverse("analytics:import-list"), "Review player import batches."),
         NavigationLink("Coach Assessments", reverse("analytics:assessment-list"), "Open the coach assessment workflow."),
         NavigationLink("Observation Review", reverse("analytics:observation-review-list"), "Review submitted and draft observations."),
+        NavigationLink("Account Operations", reverse("accounts:operations-dashboard"), "Review account status and player links."),
     ]


diff --git a/project_flat_file.txt b/project_flat_file.txt
index 5cc8651..af0cbf7 100644
--- a/project_flat_file.txt
+++ b/project_flat_file.txt
@@ -1,6 +1,6 @@
 # Project Flat File Snapshot
 # Root: /Users/eugenelin/dev/vmba0
-# File count: 336
+# File count: 341
 # Excluded directories: .git, .venv, __pycache__, node_modules, dist, build
 # Excluded unrelated untracked scratch files.
 # Text files are included as UTF-8/decoded text. Binary files are described, not embedded.
@@ -757,6 +757,329 @@ CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------


+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/accounts/services/account_operations_service.py
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+from __future__ import annotations
+
+from dataclasses import dataclass
+
+from django.contrib.auth import get_user_model
+from django.urls import reverse
+from django.utils import timezone
+
+from accounts.models import AccountRole, UserPlayerLink
+from accounts.services import account_query_service
+from accounts.services.account_query_service import AccountListFilters
+from accounts.services.role_service import role_label
+
+
+User = get_user_model()
+
+
+@dataclass(frozen=True)
+class AccountSummaryCard:
+    label: str
+    value: int
+    help_text: str = ""
+    url: str = ""
+
+
+@dataclass(frozen=True)
+class AccountListRow:
+    user: User
+    role: str
+    role_label: str
+    linked_player_count: int
+    detail_url: str
+
+
+@dataclass(frozen=True)
+class LinkedPlayerRow:
+    link: UserPlayerLink
+    player: object
+    relationship: str
+    is_primary: bool
+    is_active: bool
+    created_from_import: bool
+    import_label: str
+
+
+@dataclass(frozen=True)
+class AccountOperationsDashboard:
+    summary_cards: list[AccountSummaryCard]
+    users_requiring_password_change: list[AccountListRow]
+    unlinked_users: list[AccountListRow]
+    players_without_self_link_count: int
+    generated_at: object
+
+
+@dataclass(frozen=True)
+class AccountListContext:
+    filters: AccountListFilters
+    rows: list[AccountListRow]
+    role_choices: tuple
+    total_count: int
+
+
+@dataclass(frozen=True)
+class AccountDetailContext:
+    user: User
+    role: str
+    role_label: str
+    linked_players: list[LinkedPlayerRow]
+
+
+def _role_for_user(user: User) -> str:
+    profile = getattr(user, "account_profile", None)
+    if profile:
+        return profile.role
+    if user.is_superuser:
+        return AccountRole.ADMIN
+    if user.is_staff:
+        return AccountRole.STAFF
+    return AccountRole.GUEST_EVALUATOR
+
+
+def _list_row(user: User) -> AccountListRow:
+    role = _role_for_user(user)
+    linked_count = getattr(user, "active_player_link_count", None)
+    if linked_count is None:
+        linked_count = user.player_links.filter(is_active=True).count()
+    return AccountListRow(
+        user=user,
+        role=role,
+        role_label=role_label(role),
+        linked_player_count=linked_count,
+        detail_url=reverse("accounts:user-detail", kwargs={"user_id": user.id}),
+    )
+
+
+def _linked_player_row(link: UserPlayerLink) -> LinkedPlayerRow:
+    import_label = ""
+    if link.import_batch_id:
+        import_label = link.import_batch.original_filename
+    return LinkedPlayerRow(
+        link=link,
+        player=link.player,
+        relationship=link.get_relationship_display(),
+        is_primary=link.is_primary,
+        is_active=link.is_active,
+        created_from_import=link.created_from_import,
+        import_label=import_label,
+    )
+
+
+def get_account_operations_dashboard() -> AccountOperationsDashboard:
+    """Return the read-only Account Operations dashboard context."""
+    users = User.objects.select_related("account_profile")
+    total_accounts = users.count()
+    active_accounts = users.filter(is_active=True).count()
+    inactive_accounts = users.filter(is_active=False).count()
+    imported_accounts = users.filter(account_profile__created_from_import=True).count()
+    password_change_accounts = users.filter(account_profile__must_change_password=True).count()
+    unlinked_users_count = account_query_service.filter_account_users(
+        AccountListFilters(linked_status="unlinked")
+    ).count()
+    players_without_self_link_count = account_query_service.count_players_without_self_link()
+
+    summary_cards = [
+        AccountSummaryCard("Total accounts", total_accounts, "All Django user accounts.", reverse("accounts:user-list")),
+        AccountSummaryCard("Active accounts", active_accounts, "Accounts that can authenticate.", reverse("accounts:user-list") + "?active=yes"),
+        AccountSummaryCard("Inactive accounts", inactive_accounts, "Accounts blocked from login.", reverse("accounts:user-list") + "?active=no"),
+        AccountSummaryCard("Imported accounts", imported_accounts, "Accounts created from player imports.", reverse("accounts:user-list") + "?imported=yes"),
+        AccountSummaryCard(
+            "Password change required",
+            password_change_accounts,
+            "Users who must change a temporary password.",
+            reverse("accounts:user-list") + "?must_change_password=yes",
+        ),
+        AccountSummaryCard(
+            "Users without player links",
+            unlinked_users_count,
+            "Accounts with no active player links.",
+            reverse("accounts:user-list") + "?linked=unlinked",
+        ),
+        AccountSummaryCard(
+            "Players without self-linked accounts",
+            players_without_self_link_count,
+            "Active players without an active self-linked user account.",
+        ),
+    ]
+
+    password_rows = [
+        _list_row(user)
+        for user in account_query_service.filter_account_users(AccountListFilters(must_change_password="yes"))[:10]
+    ]
+    unlinked_rows = [
+        _list_row(user)
+        for user in account_query_service.filter_account_users(AccountListFilters(linked_status="unlinked"))[:10]
+    ]
+    return AccountOperationsDashboard(
+        summary_cards=summary_cards,
+        users_requiring_password_change=password_rows,
+        unlinked_users=unlinked_rows,
+        players_without_self_link_count=players_without_self_link_count,
+        generated_at=timezone.now(),
+    )
+
+
+def get_account_list(filters: AccountListFilters) -> AccountListContext:
+    """Return read-only account list rows for staff account operations."""
+    queryset = account_query_service.filter_account_users(filters)
+    rows = [_list_row(user) for user in queryset]
+    return AccountListContext(
+        filters=filters,
+        rows=rows,
+        role_choices=AccountRole.choices,
+        total_count=len(rows),
+    )
+
+
+def get_account_detail(user_id: int) -> AccountDetailContext:
+    """Return read-only detail context for one account."""
+    user = account_query_service.get_account_user(user_id)
+    links = user.player_links.select_related("player", "import_batch").order_by(
+        "-is_active",
+        "relationship",
+        "player__last_name",
+        "player__first_name",
+        "id",
+    )
+    role = _role_for_user(user)
+    return AccountDetailContext(
+        user=user,
+        role=role,
+        role_label=role_label(role),
+        linked_players=[_linked_player_row(link) for link in links],
+    )
+
+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/accounts/services/account_query_service.py
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+from __future__ import annotations
+
+from dataclasses import dataclass
+
+from django.contrib.auth import get_user_model
+from django.db.models import Count, Exists, OuterRef, Q
+
+from accounts.models import AccountRole, UserPlayerLink, UserPlayerRelationship
+from players.models import Player
+
+
+User = get_user_model()
+
+
+@dataclass(frozen=True)
+class AccountListFilters:
+    search: str = ""
+    role: str = ""
+    active_status: str = ""
+    staff_status: str = ""
+    superuser_status: str = ""
+    imported_status: str = ""
+    must_change_password: str = ""
+    linked_status: str = ""
+
+
+def parse_account_list_filters(params) -> AccountListFilters:
+    """Parse account list GET parameters into normalized filter values."""
+    return AccountListFilters(
+        search=str(params.get("q", "") or "").strip(),
+        role=str(params.get("role", "") or "").strip(),
+        active_status=str(params.get("active", "") or "").strip(),
+        staff_status=str(params.get("staff", "") or "").strip(),
+        superuser_status=str(params.get("superuser", "") or "").strip(),
+        imported_status=str(params.get("imported", "") or "").strip(),
+        must_change_password=str(params.get("must_change_password", "") or "").strip(),
+        linked_status=str(params.get("linked", "") or "").strip(),
+    )
+
+
+def _truthy_filter_value(value: str) -> bool | None:
+    if value in {"yes", "true", "1"}:
+        return True
+    if value in {"no", "false", "0"}:
+        return False
+    return None
+
+
+def account_user_queryset():
+    """Return the base queryset for account operation user lists."""
+    active_link = UserPlayerLink.objects.filter(user=OuterRef("pk"), is_active=True)
+    return (
+        User.objects.select_related("account_profile", "account_profile__import_batch")
+        .prefetch_related("player_links__player", "player_links__import_batch")
+        .annotate(
+            active_player_link_count=Count("player_links", filter=Q(player_links__is_active=True), distinct=True),
+            has_active_player_link=Exists(active_link),
+        )
+        .order_by("username", "id")
+    )
+
+
+def filter_account_users(filters: AccountListFilters):
+    """Apply account operation search and filters to users."""
+    queryset = account_user_queryset()
+
+    if filters.search:
+        queryset = queryset.filter(
+            Q(username__icontains=filters.search)
+            | Q(email__icontains=filters.search)
+            | Q(first_name__icontains=filters.search)
+            | Q(last_name__icontains=filters.search)
+        )
+
+    if filters.role in {choice.value for choice in AccountRole}:
+        queryset = queryset.filter(account_profile__role=filters.role)
+
+    active = _truthy_filter_value(filters.active_status)
+    if active is not None:
+        queryset = queryset.filter(is_active=active)
+
+    staff = _truthy_filter_value(filters.staff_status)
+    if staff is not None:
+        queryset = queryset.filter(is_staff=staff)
+
+    superuser = _truthy_filter_value(filters.superuser_status)
+    if superuser is not None:
+        queryset = queryset.filter(is_superuser=superuser)
+
+    imported = _truthy_filter_value(filters.imported_status)
+    if imported is not None:
+        queryset = queryset.filter(account_profile__created_from_import=imported)
+
+    must_change = _truthy_filter_value(filters.must_change_password)
+    if must_change is not None:
+        queryset = queryset.filter(account_profile__must_change_password=must_change)
+
+    if filters.linked_status == "linked":
+        queryset = queryset.filter(has_active_player_link=True)
+    elif filters.linked_status == "unlinked":
+        queryset = queryset.filter(has_active_player_link=False)
+
+    return queryset
+
+
+def get_account_user(user_id: int):
+    """Return one user with account-operation related data loaded."""
+    return account_user_queryset().get(pk=user_id)
+
+
+def count_players_without_self_link() -> int:
+    """Return active players without an active primary self-linked user account."""
+    self_link = UserPlayerLink.objects.filter(
+        player=OuterRef("pk"),
+        relationship=UserPlayerRelationship.SELF,
+        is_active=True,
+    )
+    return Player.objects.filter(is_active=True).annotate(has_self_link=Exists(self_link)).filter(has_self_link=False).count()
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/accounts/services/auth_redirect_service.py
 ====================================================================================================
@@ -1147,6 +1470,26 @@ def can_manage_accounts(user) -> bool:
     return is_staff_or_admin(user)


+def can_access_account_operations(user) -> bool:
+    return is_staff_or_admin(user)
+
+
+def can_view_account_operations_dashboard(user) -> bool:
+    return can_access_account_operations(user)
+
+
+def can_view_account_list(user) -> bool:
+    return can_access_account_operations(user)
+
+
+def can_view_account_detail(user, target_user) -> bool:
+    return bool(target_user and can_access_account_operations(user))
+
+
+def can_manage_privileged_accounts(user) -> bool:
+    return bool(user and user.is_authenticated and user.is_superuser)
+
+
 def can_view_account_profile(user, profile) -> bool:
     if is_staff_or_admin(user):
         return True
@@ -1632,6 +1975,82 @@ CONTENT-TYPE: text/plain; charset=utf-8
 </section>
 {% endblock %}

+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/operations_dashboard.html
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Account Operations{% endblock %}
+{% block pdp_subtitle %}Read-only staff dashboard for account health and account lookup.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>Summary</h2>
+        <div class="pdp-grid">
+            {% for card in summary_cards %}
+                <section>
+                    <h3>{{ card.label }}</h3>
+                    <p><strong>{{ card.value }}</strong></p>
+                    <p>{{ card.help_text }}</p>
+                    {% if card.url %}
+                        <a class="button button--ghost" href="{{ card.url }}">Open</a>
+                    {% endif %}
+                </section>
+            {% endfor %}
+        </div>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Accounts Requiring Password Change</h2>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr><th>Username</th><th>Name</th><th>Role</th><th></th></tr>
+                </thead>
+                <tbody>
+                    {% for row in users_requiring_password_change %}
+                        <tr>
+                            <td>{{ row.user.username }}</td>
+                            <td>{{ row.user.get_full_name|default:"-" }}</td>
+                            <td>{{ row.role_label }}</td>
+                            <td><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="4">No accounts currently require password change.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Users Without Player Links</h2>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr><th>Username</th><th>Name</th><th>Role</th><th></th></tr>
+                </thead>
+                <tbody>
+                    {% for row in unlinked_users %}
+                        <tr>
+                            <td>{{ row.user.username }}</td>
+                            <td>{{ row.user.get_full_name|default:"-" }}</td>
+                            <td>{{ row.role_label }}</td>
+                            <td><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="4">No unlinked users found.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    </article>
+</section>
+{% endblock %}
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/password_change.html
 ====================================================================================================
@@ -1687,6 +2106,240 @@ CONTENT-TYPE: text/plain; charset=utf-8
                 {% endfor %}
             </ul>
         {% endif %}
+        {% if request.user.is_staff or request.user.is_superuser %}
+            <p><a class="button button--ghost" href="{% url 'accounts:operations-dashboard' %}">Account Operations</a></p>
+        {% endif %}
+    </article>
+</section>
+{% endblock %}
+
+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/user_detail.html
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Account Detail{% endblock %}
+{% block pdp_subtitle %}Read-only account and linked player context.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>{{ target_user.get_full_name|default:target_user.username }}</h2>
+        <dl class="pdp-definition-list">
+            <dt>Username</dt>
+            <dd>{{ target_user.username }}</dd>
+            <dt>Email</dt>
+            <dd>{{ target_user.email|default:"-" }}</dd>
+            <dt>First name</dt>
+            <dd>{{ target_user.first_name|default:"-" }}</dd>
+            <dt>Last name</dt>
+            <dd>{{ target_user.last_name|default:"-" }}</dd>
+            <dt>Role</dt>
+            <dd>{{ account_detail.role_label }}</dd>
+            <dt>Active</dt>
+            <dd>{% if target_user.is_active %}Yes{% else %}No{% endif %}</dd>
+            <dt>Staff</dt>
+            <dd>{% if target_user.is_staff %}Yes{% else %}No{% endif %}</dd>
+            <dt>Superuser</dt>
+            <dd>{% if target_user.is_superuser %}Yes{% else %}No{% endif %}</dd>
+            <dt>Password change required</dt>
+            <dd>
+                {% if target_user.account_profile.must_change_password %}
+                    Yes
+                {% else %}
+                    No
+                {% endif %}
+            </dd>
+            <dt>Created from import</dt>
+            <dd>
+                {% if target_user.account_profile.created_from_import %}
+                    Yes
+                {% else %}
+                    No
+                {% endif %}
+            </dd>
+            {% if target_user.account_profile.import_batch %}
+                <dt>Import batch</dt>
+                <dd>{{ target_user.account_profile.import_batch.original_filename }}</dd>
+            {% endif %}
+            <dt>Date joined</dt>
+            <dd>{{ target_user.date_joined }}</dd>
+            <dt>Last login</dt>
+            <dd>{{ target_user.last_login|default:"-" }}</dd>
+        </dl>
+        <p><a class="button button--ghost" href="{% url 'accounts:user-list' %}">Back to users</a></p>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Linked Players</h2>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr>
+                        <th>Player</th>
+                        <th>Relationship</th>
+                        <th>Primary</th>
+                        <th>Active</th>
+                        <th>Imported</th>
+                        <th>Import Batch</th>
+                    </tr>
+                </thead>
+                <tbody>
+                    {% for row in linked_players %}
+                        <tr>
+                            <td>{{ row.player.display_name }}</td>
+                            <td>{{ row.relationship }}</td>
+                            <td>{% if row.is_primary %}Yes{% else %}No{% endif %}</td>
+                            <td>{% if row.is_active %}Active{% else %}Inactive{% endif %}</td>
+                            <td>{% if row.created_from_import %}Yes{% else %}No{% endif %}</td>
+                            <td>{{ row.import_label|default:"-" }}</td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="6">No linked players found.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    </article>
+</section>
+{% endblock %}
+
+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/user_list.html
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Account Users{% endblock %}
+{% block pdp_subtitle %}Search and filter platform accounts.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>Filters</h2>
+        <form method="get" class="pdp-form">
+            <label>
+                Search
+                <input type="text" name="q" value="{{ filters.search }}" placeholder="Username, email, first, or last name">
+            </label>
+            <label>
+                Role
+                <select name="role">
+                    <option value="">Any role</option>
+                    {% for value, label in role_choices %}
+                        <option value="{{ value }}"{% if filters.role == value %} selected{% endif %}>{{ label }}</option>
+                    {% endfor %}
+                </select>
+            </label>
+            <label>
+                Active
+                <select name="active">
+                    <option value="">Any</option>
+                    <option value="yes"{% if filters.active_status == "yes" %} selected{% endif %}>Active</option>
+                    <option value="no"{% if filters.active_status == "no" %} selected{% endif %}>Inactive</option>
+                </select>
+            </label>
+            <label>
+                Staff
+                <select name="staff">
+                    <option value="">Any</option>
+                    <option value="yes"{% if filters.staff_status == "yes" %} selected{% endif %}>Staff</option>
+                    <option value="no"{% if filters.staff_status == "no" %} selected{% endif %}>Not staff</option>
+                </select>
+            </label>
+            <label>
+                Superuser
+                <select name="superuser">
+                    <option value="">Any</option>
+                    <option value="yes"{% if filters.superuser_status == "yes" %} selected{% endif %}>Superuser</option>
+                    <option value="no"{% if filters.superuser_status == "no" %} selected{% endif %}>Not superuser</option>
+                </select>
+            </label>
+            <label>
+                Imported
+                <select name="imported">
+                    <option value="">Any</option>
+                    <option value="yes"{% if filters.imported_status == "yes" %} selected{% endif %}>Imported</option>
+                    <option value="no"{% if filters.imported_status == "no" %} selected{% endif %}>Not imported</option>
+                </select>
+            </label>
+            <label>
+                Password
+                <select name="must_change_password">
+                    <option value="">Any</option>
+                    <option value="yes"{% if filters.must_change_password == "yes" %} selected{% endif %}>Change required</option>
+                    <option value="no"{% if filters.must_change_password == "no" %} selected{% endif %}>No change required</option>
+                </select>
+            </label>
+            <label>
+                Player Links
+                <select name="linked">
+                    <option value="">Any</option>
+                    <option value="linked"{% if filters.linked_status == "linked" %} selected{% endif %}>Linked</option>
+                    <option value="unlinked"{% if filters.linked_status == "unlinked" %} selected{% endif %}>Unlinked</option>
+                </select>
+            </label>
+            <button class="button button--primary" type="submit">Apply</button>
+            <a class="button button--ghost" href="{% url 'accounts:user-list' %}">Reset</a>
+        </form>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Results</h2>
+        <p>{{ total_count }} account{{ total_count|pluralize }} found.</p>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr>
+                        <th>Username</th>
+                        <th>Name</th>
+                        <th>Email</th>
+                        <th>Role</th>
+                        <th>Active</th>
+                        <th>Staff</th>
+                        <th>Superuser</th>
+                        <th>Password Change</th>
+                        <th>Player Links</th>
+                        <th>Imported</th>
+                        <th></th>
+                    </tr>
+                </thead>
+                <tbody>
+                    {% for row in rows %}
+                        <tr>
+                            <td>{{ row.user.username }}</td>
+                            <td>{{ row.user.get_full_name|default:"-" }}</td>
+                            <td>{{ row.user.email|default:"-" }}</td>
+                            <td>{{ row.role_label }}</td>
+                            <td>{% if row.user.is_active %}Active{% else %}Inactive{% endif %}</td>
+                            <td>{% if row.user.is_staff %}Yes{% else %}No{% endif %}</td>
+                            <td>{% if row.user.is_superuser %}Yes{% else %}No{% endif %}</td>
+                            <td>
+                                {% if row.user.account_profile.must_change_password %}
+                                    Required
+                                {% else %}
+                                    No
+                                {% endif %}
+                            </td>
+                            <td>{{ row.linked_player_count }}</td>
+                            <td>
+                                {% if row.user.account_profile.created_from_import %}
+                                    Yes
+                                {% else %}
+                                    No
+                                {% endif %}
+                            </td>
+                            <td><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="11">No accounts match these filters.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
     </article>
 </section>
 {% endblock %}
@@ -1702,10 +2355,16 @@ from django.conf import settings
 from django.core.exceptions import ValidationError
 from django.db import IntegrityError, transaction
 from django.test import TestCase
-from django.urls import NoReverseMatch, reverse
+from django.urls import reverse
 from django.contrib.auth import SESSION_KEY

 from accounts.models import AccountProfile, AccountRole, UserPlayerLink, UserPlayerRelationship
+from accounts.services.account_operations_service import (
+    get_account_detail,
+    get_account_list,
+    get_account_operations_dashboard,
+)
+from accounts.services.account_query_service import AccountListFilters, count_players_without_self_link, filter_account_users
 from accounts.services.auth_redirect_service import (
     ACCOUNT_LOGIN_PATH,
     ACCOUNT_LOGOUT_PATH,
@@ -1718,9 +2377,14 @@ from accounts.services.auth_redirect_service import (
 )
 from accounts.services.email_service import emails_equal, find_existing_email_user, normalize_email
 from accounts.services.permissions import (
+    can_access_account_operations,
     can_change_account_role,
     can_manage_accounts,
+    can_manage_privileged_accounts,
     can_submit_evaluations,
+    can_view_account_detail,
+    can_view_account_list,
+    can_view_account_operations_dashboard,
     can_view_account_profile,
 )
 from accounts.services.link_service import (
@@ -1809,6 +2473,7 @@ class AccountPermissionTests(TestCase):
     def setUp(self):
         self.user = User.objects.create_user(username="user", password="testpass")
         self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
+        self.superuser = User.objects.create_superuser(username="admin", password="testpass")
         self.profile = get_or_create_account_profile(self.user)

     def test_staff_admin_permissions_use_django_flags(self):
@@ -1817,6 +2482,25 @@ class AccountPermissionTests(TestCase):
         self.assertTrue(can_manage_accounts(self.staff))
         self.assertTrue(can_change_account_role(self.staff))

+    def test_account_operations_permissions_use_django_staff_flags(self):
+        self.profile.role = AccountRole.STAFF
+        self.profile.save(update_fields=["role", "updated_at"])
+
+        self.assertFalse(can_access_account_operations(self.user))
+        self.assertFalse(can_view_account_operations_dashboard(self.user))
+        self.assertFalse(can_view_account_list(self.user))
+        self.assertFalse(can_view_account_detail(self.user, self.staff))
+        self.assertTrue(can_access_account_operations(self.staff))
+        self.assertTrue(can_view_account_operations_dashboard(self.staff))
+        self.assertTrue(can_view_account_list(self.staff))
+        self.assertTrue(can_view_account_detail(self.staff, self.user))
+        self.assertTrue(can_access_account_operations(self.superuser))
+
+    def test_privileged_account_management_is_superuser_only(self):
+        self.assertFalse(can_manage_privileged_accounts(self.user))
+        self.assertFalse(can_manage_privileged_accounts(self.staff))
+        self.assertTrue(can_manage_privileged_accounts(self.superuser))
+
     def test_regular_user_can_view_own_profile_but_not_manage_accounts(self):
         other = User.objects.create_user(username="other", password="testpass")

@@ -1845,6 +2529,120 @@ class AccountAdminTests(TestCase):
         self.assertIn("updated_at", link_admin.readonly_fields)


+class AccountOperationsServiceTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
+        self.coach = User.objects.create_user(
+            username="coach.one",
+            password="testpass",
+            first_name="Coach",
+            last_name="One",
+            email="coach@example.com",
+        )
+        self.player_user = User.objects.create_user(
+            username="alex.player",
+            password="testpass",
+            first_name="Alex",
+            last_name="Player",
+            email="alex@example.com",
+        )
+        self.inactive_user = User.objects.create_user(username="inactive", password="testpass", is_active=False)
+        self.import_batch = PlayerImportBatch.objects.create(
+            source="manual_staff_csv",
+            original_filename="players.csv",
+            uploaded_by=self.staff,
+        )
+        set_account_role(self.coach, AccountRole.COACH)
+        player_profile = set_account_role(self.player_user, AccountRole.PLAYER)
+        player_profile.created_from_import = True
+        player_profile.import_batch = self.import_batch
+        player_profile.must_change_password = True
+        player_profile.save(
+            update_fields=["created_from_import", "import_batch", "must_change_password", "updated_at"]
+        )
+        get_or_create_account_profile(self.inactive_user)
+        self.player = Player.objects.create(first_name="Alex", last_name="Player", birthdate="2012-05-01")
+        self.unlinked_player = Player.objects.create(first_name="No", last_name="Account")
+        link_user_to_player(
+            self.player_user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            created_from_import=True,
+            import_batch=self.import_batch,
+        )
+
+    def usernames_for_filters(self, **kwargs):
+        return [user.username for user in filter_account_users(AccountListFilters(**kwargs))]
+
+    def test_account_query_filters_by_search_text(self):
+        self.assertEqual(self.usernames_for_filters(search="coach@example.com"), ["coach.one"])
+        self.assertEqual(self.usernames_for_filters(search="Alex"), ["alex.player"])
+
+    def test_account_query_filters_by_role(self):
+        self.assertEqual(self.usernames_for_filters(role=AccountRole.COACH), ["coach.one"])
+        self.assertEqual(self.usernames_for_filters(role=AccountRole.PLAYER), ["alex.player"])
+
+    def test_account_query_filters_by_active_status(self):
+        self.assertEqual(self.usernames_for_filters(active_status="no"), ["inactive"])
+
+    def test_account_query_filters_by_staff_and_superuser_status(self):
+        admin_user = User.objects.create_superuser(username="admin", password="testpass")
+        get_or_create_account_profile(admin_user)
+
+        self.assertEqual(self.usernames_for_filters(staff_status="yes"), ["admin", "staff"])
+        self.assertEqual(self.usernames_for_filters(superuser_status="yes"), ["admin"])
+
+    def test_account_query_filters_by_imported_and_password_status(self):
+        self.assertEqual(self.usernames_for_filters(imported_status="yes"), ["alex.player"])
+        self.assertEqual(self.usernames_for_filters(must_change_password="yes"), ["alex.player"])
+
+    def test_account_query_filters_by_linked_status(self):
+        self.assertEqual(self.usernames_for_filters(linked_status="linked"), ["alex.player"])
+        self.assertCountEqual(
+            self.usernames_for_filters(linked_status="unlinked"),
+            ["coach.one", "inactive", "staff"],
+        )
+
+    def test_dashboard_counts_include_account_health_metrics(self):
+        dashboard = get_account_operations_dashboard()
+        cards = {card.label: card.value for card in dashboard.summary_cards}
+
+        self.assertEqual(cards["Total accounts"], 4)
+        self.assertEqual(cards["Active accounts"], 3)
+        self.assertEqual(cards["Inactive accounts"], 1)
+        self.assertEqual(cards["Imported accounts"], 1)
+        self.assertEqual(cards["Password change required"], 1)
+        self.assertEqual(cards["Users without player links"], 3)
+        self.assertEqual(cards["Players without self-linked accounts"], 1)
+        self.assertEqual(dashboard.users_requiring_password_change[0].user, self.player_user)
+
+    def test_account_list_context_returns_rows_and_choices(self):
+        context = get_account_list(AccountListFilters(role=AccountRole.COACH))
+
+        self.assertEqual(context.total_count, 1)
+        self.assertEqual(context.rows[0].user, self.coach)
+        self.assertEqual(context.rows[0].role_label, "Coach")
+        self.assertIn((AccountRole.COACH, "Coach"), context.role_choices)
+
+    def test_account_detail_context_includes_profile_and_linked_players(self):
+        context = get_account_detail(self.player_user.id)
+
+        self.assertEqual(context.user, self.player_user)
+        self.assertEqual(context.role, AccountRole.PLAYER)
+        self.assertEqual(context.role_label, "Player")
+        self.assertEqual(len(context.linked_players), 1)
+        linked = context.linked_players[0]
+        self.assertEqual(linked.player, self.player)
+        self.assertEqual(linked.relationship, "Self")
+        self.assertTrue(linked.is_primary)
+        self.assertTrue(linked.is_active)
+        self.assertTrue(linked.created_from_import)
+        self.assertEqual(linked.import_label, "players.csv")
+
+    def test_players_without_self_link_count(self):
+        self.assertEqual(count_players_without_self_link(), 1)
+
+
 class UserPlayerLinkModelTests(TestCase):
     def setUp(self):
         self.user = User.objects.create_user(username="player", password="testpass")
@@ -2560,6 +3358,106 @@ class AccountAuthViewTests(TestCase):
         self.assertContains(response, "Guest Evaluator")


+class AccountOperationsViewTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
+        self.superuser = User.objects.create_superuser(username="admin", password="testpass")
+        self.regular = User.objects.create_user(username="regular", password="testpass")
+        self.coach = User.objects.create_user(
+            username="coach.one",
+            password="testpass",
+            first_name="Coach",
+            last_name="One",
+            email="coach@example.com",
+        )
+        set_account_role(self.coach, AccountRole.COACH)
+        profile = get_or_create_account_profile(self.regular)
+        profile.role = AccountRole.STAFF
+        profile.save(update_fields=["role", "updated_at"])
+        self.player = Player.objects.create(first_name="Alex", last_name="Player")
+        link_user_to_player(self.coach, self.player, relationship=UserPlayerRelationship.COACH, is_primary=False)
+
+    def test_dashboard_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:operations-dashboard"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_superuser_can_access_dashboard(self):
+        self.client.force_login(self.superuser)
+
+        response = self.client.get(reverse("accounts:operations-dashboard"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account Operations")
+
+    def test_dashboard_renders_expected_summary_cards(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:operations-dashboard"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Total accounts")
+        self.assertContains(response, "Active accounts")
+        self.assertContains(response, "Inactive accounts")
+        self.assertContains(response, "Password change required")
+        self.assertContains(response, "Users without player links")
+        self.assertContains(response, "Players without self-linked accounts")
+
+    def test_user_list_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:user-list"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_user_list_renders_users_and_filters(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:user-list"), {"q": "coach", "role": AccountRole.COACH})
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account Users")
+        self.assertContains(response, "coach.one")
+        self.assertContains(response, "Coach")
+        self.assertNotContains(response, "regular")
+
+    def test_user_detail_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_user_detail_renders_profile_and_linked_players(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "coach.one")
+        self.assertContains(response, "coach@example.com")
+        self.assertContains(response, "Coach")
+        self.assertContains(response, "Alex Player")
+
+    def test_profile_page_links_staff_to_account_operations(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:profile"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, reverse("accounts:operations-dashboard"))
+
+    def test_profile_page_does_not_link_regular_user_to_account_operations(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:profile"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertNotContains(response, reverse("accounts:operations-dashboard"))
+
+
 class AccountPasswordMiddlewareTests(TestCase):
     def setUp(self):
         self.user = User.objects.create_user(username="user", password="testpass")
@@ -2665,9 +3563,9 @@ class AccountPdpCoexistenceTests(TestCase):
         self.assertEqual(settings.LOGIN_URL, ACCOUNT_LOGIN_PATH)
         self.assertEqual(settings.LOGIN_REDIRECT_URL, ACCOUNT_PROFILE_PATH)

-    def test_no_staff_account_management_routes_exist_yet(self):
-        with self.assertRaises(NoReverseMatch):
-            reverse("accounts:account-list")
+    def test_account_operations_routes_are_platform_account_routes(self):
+        self.assertEqual(reverse("accounts:operations-dashboard"), "/accounts/")
+        self.assertEqual(reverse("accounts:user-list"), "/accounts/users/")

 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/accounts/urls.py
@@ -2676,16 +3574,27 @@ CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 from django.urls import path

-from accounts.views import AccountLoginView, AccountLogoutView, AccountPasswordChangeView, AccountProfileView
+from accounts.views import (
+    AccountLoginView,
+    AccountLogoutView,
+    AccountOperationsDashboardView,
+    AccountPasswordChangeView,
+    AccountProfileView,
+    AccountUserDetailView,
+    AccountUserListView,
+)


 app_name = "accounts"

 urlpatterns = [
+    path("", AccountOperationsDashboardView.as_view(), name="operations-dashboard"),
     path("login/", AccountLoginView.as_view(), name="login"),
     path("logout/", AccountLogoutView.as_view(), name="logout"),
     path("password/", AccountPasswordChangeView.as_view(), name="password-change"),
     path("profile/", AccountProfileView.as_view(), name="profile"),
+    path("users/", AccountUserListView.as_view(), name="user-list"),
+    path("users/<int:user_id>/", AccountUserDetailView.as_view(), name="user-detail"),
 ]

 ====================================================================================================
@@ -2695,11 +3604,18 @@ CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 from django.contrib import messages
 from django.contrib.auth import update_session_auth_hash
-from django.contrib.auth.mixins import LoginRequiredMixin
+from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
 from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
+from django.core.exceptions import PermissionDenied
 from django.shortcuts import redirect
 from django.views.generic import TemplateView

+from accounts.services.account_operations_service import (
+    get_account_detail,
+    get_account_list,
+    get_account_operations_dashboard,
+)
+from accounts.services.account_query_service import parse_account_list_filters
 from accounts.services.auth_redirect_service import (
     ACCOUNT_LOGIN_PATH,
     ACCOUNT_PASSWORD_PATH,
@@ -2708,10 +3624,20 @@ from accounts.services.auth_redirect_service import (
 )
 from accounts.services.link_service import get_players_for_user
 from accounts.services.password_service import clear_password_change_required
+from accounts.services.permissions import (
+    can_view_account_detail,
+    can_view_account_list,
+    can_view_account_operations_dashboard,
+)
 from accounts.services.profile_service import get_account_role
 from accounts.services.role_service import role_label


+class AccountOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
+    def test_func(self):
+        return can_view_account_operations_dashboard(self.request.user)
+
+
 class AccountLoginView(LoginView):
     template_name = "accounts/login.html"

@@ -2755,6 +3681,64 @@ class AccountProfileView(LoginRequiredMixin, TemplateView):
         )
         return context

+
+class AccountOperationsDashboardView(AccountOperationsStaffRequiredMixin, TemplateView):
+    template_name = "accounts/operations_dashboard.html"
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        dashboard = get_account_operations_dashboard()
+        context.update(
+            {
+                "dashboard": dashboard,
+                "summary_cards": dashboard.summary_cards,
+                "users_requiring_password_change": dashboard.users_requiring_password_change,
+                "unlinked_users": dashboard.unlinked_users,
+            }
+        )
+        return context
+
+
+class AccountUserListView(AccountOperationsStaffRequiredMixin, TemplateView):
+    template_name = "accounts/user_list.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        if not can_view_account_list(request.user):
+            raise PermissionDenied
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        filters = parse_account_list_filters(self.request.GET)
+        account_list = get_account_list(filters)
+        context.update(
+            {
+                "account_list": account_list,
+                "filters": account_list.filters,
+                "rows": account_list.rows,
+                "role_choices": account_list.role_choices,
+                "total_count": account_list.total_count,
+            }
+        )
+        return context
+
+
+class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
+    template_name = "accounts/user_detail.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        self.account_detail = get_account_detail(kwargs["user_id"])
+        if not can_view_account_detail(request.user, self.account_detail.user):
+            raise PermissionDenied
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["account_detail"] = self.account_detail
+        context["target_user"] = self.account_detail.user
+        context["linked_players"] = self.account_detail.linked_players
+        return context
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/analytics/__init__.py
 ====================================================================================================
@@ -5621,6 +6605,7 @@ def _navigation_links() -> list[NavigationLink]:
         NavigationLink("Import Players", reverse("analytics:import-list"), "Review player import batches."),
         NavigationLink("Coach Assessments", reverse("analytics:assessment-list"), "Open the coach assessment workflow."),
         NavigationLink("Observation Review", reverse("analytics:observation-review-list"), "Review submitted and draft observations."),
+        NavigationLink("Account Operations", reverse("accounts:operations-dashboard"), "Review account status and player links."),
     ]
```

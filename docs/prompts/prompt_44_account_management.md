# Prompt 44 - Account Management

## User Prompt

```text
You are implementing Platform V1 Account Operations.

Implement Phase C only.

Do NOT implement Phase D, E, or F.

==================================================
Before Coding
==================================================

Read:

- docs/ARCHITECTURE.md
- docs/account_management/V1_SUMMARY.md
- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/platform_v1_account_operations.md
- AGENTS.md

Review:

accounts/
players/
analytics/
drafts/

Pay particular attention to:

accounts/services/account_operations_service.py
accounts/services/account_query_service.py
accounts/services/link_service.py
accounts/services/profile_service.py
accounts/services/permissions.py
accounts/views.py
accounts/forms.py
accounts/templates/

==================================================
Scope
==================================================

Implement ONLY Phase C.

Goal:

Staff can manage the lifecycle of existing accounts and their player links.

This phase is intentionally limited to existing accounts.

NO account creation improvements.

NO password reset.

NO bulk operations.

==================================================
Architecture
==================================================

Views remain thin.

Business rules belong in services.

accounts owns:

- account lifecycle
- UserPlayerLink
- AccountProfile
- username changes
- link management

players owns:

- Player identity
- Player search

Analytics remains unchanged.

==================================================
Service Ownership
==================================================

Expand:

accounts/services/account_operations_service.py

It becomes the orchestration layer.

Reuse:

link_service

profile_service

username_service

Do NOT duplicate link logic.

==================================================
Account Lifecycle
==================================================

Allow staff to:

Activate account

Deactivate account

Change account role

Change username

Do NOT allow deleting users.

Deletion remains unsupported.

==================================================
Activation Rules
==================================================

Activation:

User.is_active=True

Deactivation:

User.is_active=False

Must preserve:

User

AccountProfile

UserPlayerLink

History

Nothing is deleted.

==================================================
Username Editing
==================================================

Allow changing usernames.

Reuse username_service.

Rules:

trim

casefold

validate uniqueness

no duplicates

Views know nothing about validation rules.

==================================================
Role Editing
==================================================

Allow staff to change roles.

Restrictions:

Only superuser may assign Admin.

Changing AccountProfile.role must never modify:

User.is_staff

User.is_superuser

==================================================
Link Management
==================================================

Allow staff to:

Create new link

Deactivate existing link

Reactivate inactive link

Set primary self link

Supported relationships:

self

parent

coach

guardian

future relationships remain supported by enum.

==================================================
Primary Rules
==================================================

Exactly one active primary SELF link per player.

Exactly one active primary SELF link per user.

Primary applies ONLY to SELF.

Parent/coach/guardian links are never primary.

Reuse existing link_service constraints.

==================================================
Player Search
==================================================

Reuse existing player query/search helpers.

Do NOT duplicate search logic.

==================================================
Views
==================================================

Add staff pages:

/accounts/users/<id>/edit/

/accounts/users/<id>/links/

These become operational pages.

==================================================
Templates
==================================================

Create:

user_edit.html

user_links.html

Keep server rendered.

No JavaScript required.

==================================================
Permissions
==================================================

Staff:

may activate/deactivate

may edit usernames

may edit roles except Admin

may manage links

Superuser:

may assign Admin

Regular users:

no access

==================================================
Validation
==================================================

Prevent:

duplicate usernames

multiple primary self links

invalid relationship transitions

duplicate active links

role escalation

self-link inconsistencies

==================================================
Engineering Recommendations
==================================================

1.

Reuse link_service for everything.

Do not manipulate UserPlayerLink directly in views.

2.

Introduce reusable dataclasses:

UpdatedAccountResult

UpdatedLinkResult

similar to CreatedAccountResult.

3.

Username changes must use username_service.

There should be exactly one normalization implementation.

4.

Prefer deactivation over deletion.

5.

Never lose historical links.

Deactivate instead.

6.

Keep account_operations_service as the orchestration boundary.

Views should call only this service.

7.

Do not expose database integrity errors to users.

Convert ValidationErrors into friendly messages.

8.

Preserve provenance.

Changing links or usernames must never modify import provenance.

==================================================
Do NOT Implement
==================================================

NO password reset

NO temporary password regeneration

NO account invitations

NO emails

NO bulk operations

NO coach import

NO parent import

NO merge

NO duplicate resolution

NO audit logging

NO player editing

NO new player creation

==================================================
Testing
==================================================

Add tests for:

activate account

deactivate account

role changes

admin restrictions

username changes

duplicate username

link creation

link reactivation

link deactivation

primary link switching

duplicate active links

permissions

views

service orchestration

regressions

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

Verify:

Phase C only

No Phase D work

Views remain thin

No duplicated link logic

No duplicated username logic

No duplicated permission logic

No provenance regression

No architecture violations

project_flat_file.txt updated

==================================================
Final Report
==================================================

Report:

implementation summary

files created

files modified

services expanded

views/templates/forms added

tests added

test results

implementation decisions

technical debt

self-review

confirmation that only Phase C was implemented.
```

## Implementation Commit Diff

```diff
diff --git a/accounts/forms.py b/accounts/forms.py
index 3c12be6..8cd49fc 100644
--- a/accounts/forms.py
+++ b/accounts/forms.py
@@ -1,6 +1,6 @@
 from django import forms
 
-from accounts.models import AccountRole
+from accounts.models import AccountRole, UserPlayerRelationship
 from players.models import Player
 
 
@@ -32,3 +32,22 @@ class PlayerAccountCreateForm(forms.Form):
     def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)
         self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")
+
+
+class AccountEditForm(forms.Form):
+    username = forms.CharField(max_length=150)
+    first_name = forms.CharField(max_length=150, required=False)
+    last_name = forms.CharField(max_length=150, required=False)
+    email = forms.EmailField(required=False)
+    role = forms.ChoiceField(choices=AccountRole.choices)
+    is_active = forms.BooleanField(required=False, label="Account is active")
+
+
+class UserPlayerLinkForm(forms.Form):
+    player = forms.ModelChoiceField(queryset=Player.objects.none())
+    relationship = forms.ChoiceField(choices=UserPlayerRelationship.choices)
+    is_primary = forms.BooleanField(required=False, label="Primary self link")
+
+    def __init__(self, *args, **kwargs):
+        super().__init__(*args, **kwargs)
+        self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")
diff --git a/accounts/services/account_operations_service.py b/accounts/services/account_operations_service.py
index 6fca77c..e9361e5 100644
--- a/accounts/services/account_operations_service.py
+++ b/accounts/services/account_operations_service.py
@@ -12,6 +12,12 @@ from accounts.models import AccountRole, UserPlayerLink
 from accounts.services import account_query_service
 from accounts.services.account_query_service import AccountListFilters
 from accounts.services.email_service import find_existing_email_user, normalize_email
+from accounts.services.link_service import (
+    activate_link,
+    deactivate_link,
+    link_user_to_player,
+    set_primary_self_link,
+)
 from accounts.services.password_service import (
     generate_birthdate_password,
     mark_password_change_required,
@@ -20,7 +26,7 @@ from accounts.services.password_service import (
 from accounts.services.profile_service import get_or_create_account_profile, set_account_role
 from accounts.services.provisioning_service import STATUS_CREATED, provision_player_account
 from accounts.services.role_service import role_label
-from accounts.services.username_service import validate_available_username
+from accounts.services.username_service import validate_available_username, validate_available_username_for_user
 from players.models import Player
 
 
@@ -90,11 +96,35 @@ class CreatedAccountResult:
     player: Player | None = None
 
 
+@dataclass(frozen=True)
+class UpdatedAccountResult:
+    user: User
+    username: str
+    role: str
+    role_label: str
+    is_active: bool
+
+
+@dataclass(frozen=True)
+class UpdatedLinkResult:
+    link: UserPlayerLink
+    user: User
+    player: Player
+    relationship: str
+    is_primary: bool
+    is_active: bool
+
+
 def _validate_actor_can_create_role(actor, role: str) -> None:
     if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
         raise ValidationError("Only superusers can create admin accounts.")
 
 
+def _validate_actor_can_assign_role(actor, role: str) -> None:
+    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
+        raise ValidationError("Only superusers can assign admin role.")
+
+
 def _validate_email_available(email: str) -> str:
     normalized = normalize_email(email)
     if normalized and find_existing_email_user(normalized):
@@ -102,6 +132,15 @@ def _validate_email_available(email: str) -> str:
     return normalized
 
 
+def _validate_email_available_for_user(user: User, email: str) -> str:
+    normalized = normalize_email(email)
+    if normalized:
+        existing_user = find_existing_email_user(normalized)
+        if existing_user and existing_user.pk != user.pk:
+            raise ValidationError("Email is already in use.")
+    return normalized
+
+
 def _role_for_user(user: User) -> str:
     profile = getattr(user, "account_profile", None)
     if profile:
@@ -142,6 +181,36 @@ def _linked_player_row(link: UserPlayerLink) -> LinkedPlayerRow:
     )
 
 
+def _updated_account_result(user: User) -> UpdatedAccountResult:
+    role = _role_for_user(user)
+    return UpdatedAccountResult(
+        user=user,
+        username=user.username,
+        role=role,
+        role_label=role_label(role),
+        is_active=user.is_active,
+    )
+
+
+def _updated_link_result(link: UserPlayerLink) -> UpdatedLinkResult:
+    return UpdatedLinkResult(
+        link=link,
+        user=link.user,
+        player=link.player,
+        relationship=link.relationship,
+        is_primary=link.is_primary,
+        is_active=link.is_active,
+    )
+
+
+def _get_user_for_update(user_id: int) -> User:
+    return User.objects.select_for_update().select_related("account_profile").get(pk=user_id)
+
+
+def _get_link_for_user(user: User, link_id: int) -> UserPlayerLink:
+    return UserPlayerLink.objects.select_for_update().select_related("user", "player").get(pk=link_id, user=user)
+
+
 def get_account_operations_dashboard() -> AccountOperationsDashboard:
     """Return the read-only Account Operations dashboard context."""
     users = User.objects.select_related("account_profile")
@@ -227,6 +296,93 @@ def get_account_detail(user_id: int) -> AccountDetailContext:
     )
 
 
+@transaction.atomic
+def update_account(
+    *,
+    actor,
+    user_id: int,
+    username: str,
+    first_name: str = "",
+    last_name: str = "",
+    email: str = "",
+    role: str = AccountRole.GUEST_EVALUATOR,
+    is_active: bool = True,
+) -> UpdatedAccountResult:
+    """Update lifecycle and profile fields for an existing account."""
+    _validate_actor_can_assign_role(actor, role)
+    user = _get_user_for_update(user_id)
+    user.username = validate_available_username_for_user(user, username)
+    user.first_name = str(first_name or "").strip()
+    user.last_name = str(last_name or "").strip()
+    user.email = _validate_email_available_for_user(user, email)
+    user.is_active = bool(is_active)
+    user.save(update_fields=["username", "first_name", "last_name", "email", "is_active"])
+    set_account_role(user, role, actor=actor)
+    user.refresh_from_db()
+    return _updated_account_result(user)
+
+
+@transaction.atomic
+def activate_account(*, actor, user_id: int) -> UpdatedAccountResult:
+    """Activate an existing account without changing profile or link history."""
+    user = _get_user_for_update(user_id)
+    if not user.is_active:
+        user.is_active = True
+        user.save(update_fields=["is_active"])
+    return _updated_account_result(user)
+
+
+@transaction.atomic
+def deactivate_account(*, actor, user_id: int) -> UpdatedAccountResult:
+    """Deactivate an existing account without deleting account data or links."""
+    user = _get_user_for_update(user_id)
+    if user.is_active:
+        user.is_active = False
+        user.save(update_fields=["is_active"])
+    return _updated_account_result(user)
+
+
+@transaction.atomic
+def create_user_player_link(
+    *,
+    actor,
+    user_id: int,
+    player: Player,
+    relationship: str,
+    is_primary: bool = False,
+) -> UpdatedLinkResult:
+    """Create an active user/player link through the account operations workflow."""
+    user = _get_user_for_update(user_id)
+    if UserPlayerLink.objects.filter(user=user, player=player, relationship=relationship, is_active=True).exists():
+        raise ValidationError("An active link already exists for this user, player, and relationship.")
+    link = link_user_to_player(user, player, relationship=relationship, is_primary=is_primary)
+    return _updated_link_result(link)
+
+
+@transaction.atomic
+def deactivate_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
+    """Deactivate a user/player link without deleting its history."""
+    user = _get_user_for_update(user_id)
+    link = _get_link_for_user(user, link_id)
+    return _updated_link_result(deactivate_link(link, actor=actor))
+
+
+@transaction.atomic
+def reactivate_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
+    """Reactivate an existing inactive user/player link when constraints allow it."""
+    user = _get_user_for_update(user_id)
+    link = _get_link_for_user(user, link_id)
+    return _updated_link_result(activate_link(link, actor=actor))
+
+
+@transaction.atomic
+def set_primary_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
+    """Set an existing self link as the active primary player link."""
+    user = _get_user_for_update(user_id)
+    link = _get_link_for_user(user, link_id)
+    return _updated_link_result(set_primary_self_link(link, actor=actor))
+
+
 @transaction.atomic
 def create_account_only(
     *,
diff --git a/accounts/services/link_service.py b/accounts/services/link_service.py
index 23cc437..a03f13f 100644
--- a/accounts/services/link_service.py
+++ b/accounts/services/link_service.py
@@ -1,6 +1,7 @@
 from django.contrib.auth import get_user_model
 from django.core.exceptions import ValidationError
 from django.db import IntegrityError, transaction
+from django.db.models import Q
 
 from accounts.models import UserPlayerLink, UserPlayerRelationship
 from players.models import Player, PlayerImportBatch
@@ -165,6 +166,30 @@ def activate_link(link, actor=None) -> UserPlayerLink:
     return link
 
 
+@transaction.atomic
+def set_primary_self_link(link, actor=None) -> UserPlayerLink:
+    """Make a self link the active primary link for its user and player."""
+    if not isinstance(link, UserPlayerLink):
+        raise ValidationError("A valid user/player link is required.")
+    if link.relationship != UserPlayerRelationship.SELF:
+        raise ValidationError("Only self links can be primary.")
+
+    UserPlayerLink.objects.select_for_update().filter(
+        Q(user=link.user) | Q(player=link.player),
+        relationship=UserPlayerRelationship.SELF,
+        is_active=True,
+        is_primary=True,
+    ).exclude(pk=link.pk).update(is_primary=False)
+
+    link.is_active = True
+    link.is_primary = True
+    try:
+        link.save(update_fields=["is_active", "is_primary", "updated_at"])
+    except IntegrityError as exc:
+        raise ValidationError("This primary self link conflicts with an existing active link.") from exc
+    return link
+
+
 @transaction.atomic
 def unlink_user_from_player(user, player, relationship=None, actor=None) -> int:
     """Deactivate active links between a user and player, optionally for one relationship."""
diff --git a/accounts/services/username_service.py b/accounts/services/username_service.py
index e17615c..a2199e9 100644
--- a/accounts/services/username_service.py
+++ b/accounts/services/username_service.py
@@ -38,13 +38,29 @@ def username_for_player(player) -> str:
     return username
 
 
-def validate_available_username(username: str) -> str:
-    """Validate an explicitly supplied username and return the normalized value."""
+def _normalize_explicit_username(username: str) -> str:
     cleaned = str(username or "").strip().casefold()
     if not cleaned:
         raise ValidationError("Username is required.")
     if USERNAME_ALLOWED_PATTERN.search(cleaned):
         raise ValidationError("Username may contain only letters, numbers, dots, underscores, and hyphens.")
+    return cleaned
+
+
+def validate_available_username(username: str) -> str:
+    """Validate an explicitly supplied username and return the normalized value."""
+    cleaned = _normalize_explicit_username(username)
     if User.objects.filter(username__iexact=cleaned).exists():
         raise ValidationError("Username is already in use.")
     return cleaned
+
+
+def validate_available_username_for_user(user, username: str) -> str:
+    """Validate a username change while allowing the current user's username."""
+    if not isinstance(user, User):
+        raise ValidationError("A valid user is required.")
+    cleaned = _normalize_explicit_username(username)
+    existing_user = User.objects.filter(username__iexact=cleaned).first()
+    if existing_user and existing_user.pk != user.pk:
+        raise ValidationError("Username is already in use.")
+    return cleaned
diff --git a/accounts/templates/accounts/user_detail.html b/accounts/templates/accounts/user_detail.html
index 6633dc8..2eeebc1 100644
--- a/accounts/templates/accounts/user_detail.html
+++ b/accounts/templates/accounts/user_detail.html
@@ -1,7 +1,7 @@
 {% extends "pdp/base.html" %}
 
 {% block pdp_title %}Account Detail{% endblock %}
-{% block pdp_subtitle %}Read-only account and linked player context.{% endblock %}
+{% block pdp_subtitle %}Account and linked player context.{% endblock %}
 
 {% block pdp_content %}
 <section class="pdp-grid pdp-grid--single">
@@ -49,7 +49,11 @@
             <dt>Last login</dt>
             <dd>{{ target_user.last_login|default:"-" }}</dd>
         </dl>
-        <p><a class="button button--ghost" href="{% url 'accounts:user-list' %}">Back to users</a></p>
+        <div class="pdp-actions">
+            <a class="button button--primary" href="{% url 'accounts:user-edit' target_user.id %}">Edit Account</a>
+            <a class="button button--ghost" href="{% url 'accounts:user-links' target_user.id %}">Manage Links</a>
+            <a class="button button--ghost" href="{% url 'accounts:user-list' %}">Back to users</a>
+        </div>
     </article>
 
     <article class="pdp-card">
diff --git a/accounts/templates/accounts/user_edit.html b/accounts/templates/accounts/user_edit.html
new file mode 100644
index 0000000..68c2c07
--- /dev/null
+++ b/accounts/templates/accounts/user_edit.html
@@ -0,0 +1,50 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Edit Account{% endblock %}
+{% block pdp_subtitle %}Manage account lifecycle, username, and role.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>{{ target_user.get_full_name|default:target_user.username }}</h2>
+        <form method="post" class="pdp-form">
+            {% csrf_token %}
+            {{ form.non_field_errors }}
+            <label>
+                Username
+                {{ form.username }}
+                {{ form.username.errors }}
+            </label>
+            <label>
+                First name
+                {{ form.first_name }}
+                {{ form.first_name.errors }}
+            </label>
+            <label>
+                Last name
+                {{ form.last_name }}
+                {{ form.last_name.errors }}
+            </label>
+            <label>
+                Email
+                {{ form.email }}
+                {{ form.email.errors }}
+            </label>
+            <label>
+                Role
+                {{ form.role }}
+                {{ form.role.errors }}
+            </label>
+            <label>
+                {{ form.is_active }}
+                {{ form.is_active.label }}
+                {{ form.is_active.errors }}
+            </label>
+            <div class="pdp-actions">
+                <button class="button button--primary" type="submit">Save Account</button>
+                <a class="button button--ghost" href="{% url 'accounts:user-detail' target_user.id %}">Cancel</a>
+            </div>
+        </form>
+    </article>
+</section>
+{% endblock %}
diff --git a/accounts/templates/accounts/user_links.html b/accounts/templates/accounts/user_links.html
new file mode 100644
index 0000000..35a1a7f
--- /dev/null
+++ b/accounts/templates/accounts/user_links.html
@@ -0,0 +1,94 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Manage Player Links{% endblock %}
+{% block pdp_subtitle %}Create, deactivate, reactivate, and manage primary self links.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>{{ target_user.get_full_name|default:target_user.username }}</h2>
+        <form method="post" class="pdp-form">
+            {% csrf_token %}
+            <input type="hidden" name="action" value="create">
+            {{ form.non_field_errors }}
+            <label>
+                Player
+                {{ form.player }}
+                {{ form.player.errors }}
+            </label>
+            <label>
+                Relationship
+                {{ form.relationship }}
+                {{ form.relationship.errors }}
+            </label>
+            <label>
+                {{ form.is_primary }}
+                {{ form.is_primary.label }}
+                {{ form.is_primary.errors }}
+            </label>
+            <div class="pdp-actions">
+                <button class="button button--primary" type="submit">Create Link</button>
+                <a class="button button--ghost" href="{% url 'accounts:user-detail' target_user.id %}">Back to account</a>
+            </div>
+        </form>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Existing Links</h2>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr>
+                        <th>Player</th>
+                        <th>Relationship</th>
+                        <th>Primary</th>
+                        <th>Status</th>
+                        <th>Imported</th>
+                        <th></th>
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
+                            <td>
+                                <div class="pdp-actions">
+                                    {% if row.is_active %}
+                                        <form method="post">
+                                            {% csrf_token %}
+                                            <input type="hidden" name="action" value="deactivate">
+                                            <input type="hidden" name="link_id" value="{{ row.link.id }}">
+                                            <button class="button button--ghost" type="submit">Deactivate</button>
+                                        </form>
+                                    {% else %}
+                                        <form method="post">
+                                            {% csrf_token %}
+                                            <input type="hidden" name="action" value="reactivate">
+                                            <input type="hidden" name="link_id" value="{{ row.link.id }}">
+                                            <button class="button button--ghost" type="submit">Reactivate</button>
+                                        </form>
+                                    {% endif %}
+                                    {% if row.link.relationship == "self" and not row.is_primary %}
+                                        <form method="post">
+                                            {% csrf_token %}
+                                            <input type="hidden" name="action" value="set_primary">
+                                            <input type="hidden" name="link_id" value="{{ row.link.id }}">
+                                            <button class="button button--ghost" type="submit">Set Primary</button>
+                                        </form>
+                                    {% endif %}
+                                </div>
+                            </td>
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
diff --git a/accounts/tests.py b/accounts/tests.py
index 24f97df..ee63b08 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -10,11 +10,18 @@ from django.contrib.auth import SESSION_KEY
 
 from accounts.models import AccountProfile, AccountRole, UserPlayerLink, UserPlayerRelationship
 from accounts.services.account_operations_service import (
+    activate_account,
     create_account_only,
     create_player_account,
+    create_user_player_link,
+    deactivate_account,
+    deactivate_user_player_link,
     get_account_detail,
     get_account_list,
     get_account_operations_dashboard,
+    reactivate_user_player_link,
+    set_primary_user_player_link,
+    update_account,
 )
 from accounts.services.account_query_service import AccountListFilters, count_players_without_self_link, filter_account_users
 from accounts.services.auth_redirect_service import (
@@ -48,6 +55,7 @@ from accounts.services.link_service import (
     get_users_for_player,
     is_player_self,
     link_user_to_player,
+    set_primary_self_link,
     unlink_user_from_player,
 )
 from accounts.services.password_service import (
@@ -72,6 +80,7 @@ from accounts.services.username_service import (
     base_username_for_player,
     normalize_username_part,
     validate_available_username,
+    validate_available_username_for_user,
     username_for_player,
 )
 from analytics.services.permissions import can_submit_coach_assessment
@@ -421,6 +430,147 @@ class AccountOperationsServiceTests(TestCase):
         with self.assertRaises(ValidationError):
             create_player_account(actor=self.staff, player=self.player, role=AccountRole.COACH)
 
+    def test_update_account_changes_lifecycle_username_email_and_role(self):
+        result = update_account(
+            actor=self.staff,
+            user_id=self.coach.id,
+            username=" Coach.Updated ",
+            first_name="Updated",
+            last_name="Coach",
+            email="UPDATED@example.com",
+            role=AccountRole.GUEST_EVALUATOR,
+            is_active=False,
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(result.username, "coach.updated")
+        self.assertEqual(result.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(result.is_active)
+        self.assertEqual(self.coach.username, "coach.updated")
+        self.assertEqual(self.coach.email, "updated@example.com")
+        self.assertEqual(self.coach.account_profile.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(self.coach.is_staff)
+        self.assertFalse(self.coach.is_superuser)
+
+    def test_update_account_rejects_duplicate_username_and_email(self):
+        User.objects.create_user(username="taken", email="taken@example.com")
+
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.coach.id,
+                username="TAKEN",
+                email="coach@example.com",
+                role=AccountRole.COACH,
+            )
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.coach.id,
+                username="coach.one",
+                email="Taken@Example.com",
+                role=AccountRole.COACH,
+            )
+
+    def test_update_account_admin_role_requires_superuser(self):
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.coach.id,
+                username="coach.one",
+                role=AccountRole.ADMIN,
+            )
+
+        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
+        result = update_account(
+            actor=superuser,
+            user_id=self.coach.id,
+            username="coach.one",
+            role=AccountRole.ADMIN,
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(result.role, AccountRole.ADMIN)
+        self.assertEqual(self.coach.account_profile.role, AccountRole.ADMIN)
+        self.assertFalse(self.coach.is_staff)
+        self.assertFalse(self.coach.is_superuser)
+
+    def test_activate_and_deactivate_account_preserve_profile_and_links(self):
+        deactivate_result = deactivate_account(actor=self.staff, user_id=self.player_user.id)
+        self.player_user.refresh_from_db()
+        link = UserPlayerLink.objects.get(user=self.player_user, player=self.player)
+
+        self.assertFalse(deactivate_result.is_active)
+        self.assertFalse(self.player_user.is_active)
+        self.assertEqual(self.player_user.account_profile.role, AccountRole.PLAYER)
+        self.assertTrue(link.is_active)
+
+        activate_result = activate_account(actor=self.staff, user_id=self.player_user.id)
+        self.player_user.refresh_from_db()
+
+        self.assertTrue(activate_result.is_active)
+        self.assertTrue(self.player_user.is_active)
+        self.assertTrue(UserPlayerLink.objects.get(pk=link.pk).is_active)
+
+    def test_account_operations_manage_player_links_through_services(self):
+        link_result = create_user_player_link(
+            actor=self.staff,
+            user_id=self.coach.id,
+            player=self.player,
+            relationship=UserPlayerRelationship.COACH,
+            is_primary=False,
+        )
+
+        self.assertTrue(link_result.is_active)
+        self.assertFalse(link_result.is_primary)
+        with self.assertRaises(ValidationError):
+            create_user_player_link(
+                actor=self.staff,
+                user_id=self.coach.id,
+                player=self.player,
+                relationship=UserPlayerRelationship.COACH,
+                is_primary=False,
+            )
+
+        deactivated = deactivate_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id)
+        self.assertFalse(deactivated.is_active)
+        self.assertFalse(UserPlayerLink.objects.get(pk=link_result.link.id).is_primary)
+
+        reactivated = reactivate_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id)
+        self.assertTrue(reactivated.is_active)
+
+    def test_account_operations_set_primary_self_link_switches_existing_primary(self):
+        other_player = Player.objects.create(first_name="Second", last_name="Player")
+        first_link = UserPlayerLink.objects.get(user=self.player_user, player=self.player)
+        second_link = create_user_player_link(
+            actor=self.staff,
+            user_id=self.player_user.id,
+            player=other_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        ).link
+
+        result = set_primary_user_player_link(actor=self.staff, user_id=self.player_user.id, link_id=second_link.id)
+        first_link.refresh_from_db()
+        second_link.refresh_from_db()
+
+        self.assertTrue(result.is_primary)
+        self.assertFalse(first_link.is_primary)
+        self.assertTrue(second_link.is_primary)
+        self.assertEqual(UserPlayerLink.objects.filter(user=self.player_user, is_primary=True, is_active=True).count(), 1)
+
+    def test_account_operations_reject_primary_non_self_link(self):
+        link = create_user_player_link(
+            actor=self.staff,
+            user_id=self.coach.id,
+            player=self.player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        ).link
+
+        with self.assertRaises(ValidationError):
+            set_primary_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link.id)
+
 
 class UserPlayerLinkModelTests(TestCase):
     def setUp(self):
@@ -712,6 +862,35 @@ class UserPlayerLinkServiceTests(TestCase):
         self.assertTrue(is_player_self(self.user, self.player))
         self.assertFalse(is_player_self(self.user, self.other_player))
 
+    def test_set_primary_self_link_switches_primary_link(self):
+        first_link = link_user_to_player(self.user, self.player)
+        second_link = link_user_to_player(
+            self.user,
+            self.other_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        )
+
+        set_primary_self_link(second_link)
+        first_link.refresh_from_db()
+        second_link.refresh_from_db()
+
+        self.assertFalse(first_link.is_primary)
+        self.assertTrue(second_link.is_primary)
+        self.assertTrue(second_link.is_active)
+        self.assertEqual(get_primary_player(self.user), self.other_player)
+
+    def test_set_primary_self_link_rejects_non_self_link(self):
+        parent_link = link_user_to_player(
+            self.user,
+            self.player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        )
+
+        with self.assertRaises(ValidationError):
+            set_primary_self_link(parent_link)
+
     def test_is_player_self_ignores_inactive_or_non_self_links(self):
         parent_link = link_user_to_player(
             self.user,
@@ -752,6 +931,14 @@ class AccountUsernameServiceTests(TestCase):
         with self.assertRaises(ValidationError):
             validate_available_username("bad username")
 
+    def test_validate_available_username_for_user_allows_current_user(self):
+        user = User.objects.create_user(username="coach.one")
+        User.objects.create_user(username="other")
+
+        self.assertEqual(validate_available_username_for_user(user, " Coach.One "), "coach.one")
+        with self.assertRaises(ValidationError):
+            validate_available_username_for_user(user, "OTHER")
+
 
 class AccountEmailServiceTests(TestCase):
     def test_email_normalization_and_comparison(self):
@@ -1237,6 +1424,147 @@ class AccountOperationsViewTests(TestCase):
         self.assertContains(response, "coach@example.com")
         self.assertContains(response, "Coach")
         self.assertContains(response, "Alex Player")
+        self.assertContains(response, reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}))
+        self.assertContains(response, reverse("accounts:user-links", kwargs={"user_id": self.coach.id}))
+
+    def test_user_edit_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_edit_account_lifecycle_username_and_role(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
+            {
+                "username": " Coach.Updated ",
+                "first_name": "Updated",
+                "last_name": "Coach",
+                "email": "updated@example.com",
+                "role": AccountRole.GUEST_EVALUATOR,
+            },
+        )
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
+        self.coach.refresh_from_db()
+        self.assertEqual(self.coach.username, "coach.updated")
+        self.assertFalse(self.coach.is_active)
+        self.assertEqual(self.coach.account_profile.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(self.coach.is_staff)
+        self.assertFalse(self.coach.is_superuser)
+
+    def test_staff_user_edit_rejects_duplicate_username_and_admin_role(self):
+        User.objects.create_user(username="taken")
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
+            {
+                "username": "taken",
+                "role": AccountRole.COACH,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Username is already in use")
+
+        response = self.client.post(
+            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
+            {
+                "username": "coach.one",
+                "role": AccountRole.ADMIN,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Only superusers can assign admin role")
+        self.coach.refresh_from_db()
+        self.assertEqual(self.coach.account_profile.role, AccountRole.COACH)
+
+    def test_user_links_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:user-links", kwargs={"user_id": self.coach.id}))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_create_deactivate_and_reactivate_link(self):
+        other_player = Player.objects.create(first_name="Blake", last_name="Player")
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {
+                "action": "create",
+                "player": other_player.id,
+                "relationship": UserPlayerRelationship.PARENT,
+            },
+        )
+
+        self.assertEqual(response.status_code, 302)
+        link = UserPlayerLink.objects.get(user=self.coach, player=other_player, relationship=UserPlayerRelationship.PARENT)
+        self.assertTrue(link.is_active)
+        self.assertFalse(link.is_primary)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "deactivate", "link_id": link.id},
+        )
+        self.assertEqual(response.status_code, 302)
+        link.refresh_from_db()
+        self.assertFalse(link.is_active)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "reactivate", "link_id": link.id},
+        )
+        self.assertEqual(response.status_code, 302)
+        link.refresh_from_db()
+        self.assertTrue(link.is_active)
+
+    def test_staff_can_set_primary_self_link_from_links_page(self):
+        first_player = Player.objects.create(first_name="Self", last_name="One")
+        second_player = Player.objects.create(first_name="Self", last_name="Two")
+        first_link = link_user_to_player(self.coach, first_player, relationship=UserPlayerRelationship.SELF)
+        second_link = link_user_to_player(
+            self.coach,
+            second_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        )
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "set_primary", "link_id": second_link.id},
+        )
+
+        self.assertEqual(response.status_code, 302)
+        first_link.refresh_from_db()
+        second_link.refresh_from_db()
+        self.assertFalse(first_link.is_primary)
+        self.assertTrue(second_link.is_primary)
+
+    def test_links_page_rejects_duplicate_active_link(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {
+                "action": "create",
+                "player": self.player.id,
+                "relationship": UserPlayerRelationship.COACH,
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "An active link already exists")
 
     def test_profile_page_links_staff_to_account_operations(self):
         self.client.force_login(self.staff)
diff --git a/accounts/urls.py b/accounts/urls.py
index 809a033..b618b47 100644
--- a/accounts/urls.py
+++ b/accounts/urls.py
@@ -8,6 +8,8 @@ from accounts.views import (
     AccountPasswordChangeView,
     AccountProfileView,
     AccountUserDetailView,
+    AccountUserEditView,
+    AccountUserLinksView,
     AccountUserListView,
     PlayerAccountCreateView,
 )
@@ -25,4 +27,6 @@ urlpatterns = [
     path("profile/", AccountProfileView.as_view(), name="profile"),
     path("users/", AccountUserListView.as_view(), name="user-list"),
     path("users/<int:user_id>/", AccountUserDetailView.as_view(), name="user-detail"),
+    path("users/<int:user_id>/edit/", AccountUserEditView.as_view(), name="user-edit"),
+    path("users/<int:user_id>/links/", AccountUserLinksView.as_view(), name="user-links"),
 ]
diff --git a/accounts/views.py b/accounts/views.py
index c8fa005..ae34d9d 100644
--- a/accounts/views.py
+++ b/accounts/views.py
@@ -6,13 +6,18 @@ from django.core.exceptions import PermissionDenied, ValidationError
 from django.shortcuts import redirect
 from django.views.generic import FormView, TemplateView
 
-from accounts.forms import AccountOnlyCreateForm, PlayerAccountCreateForm
+from accounts.forms import AccountEditForm, AccountOnlyCreateForm, PlayerAccountCreateForm, UserPlayerLinkForm
 from accounts.services.account_operations_service import (
     create_account_only,
     create_player_account,
+    create_user_player_link,
+    deactivate_user_player_link,
     get_account_detail,
     get_account_list,
     get_account_operations_dashboard,
+    reactivate_user_player_link,
+    set_primary_user_player_link,
+    update_account,
 )
 from accounts.services.account_query_service import parse_account_list_filters
 from accounts.services.auth_redirect_service import (
@@ -139,6 +144,113 @@ class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
         return context
 
 
+class AccountUserEditView(AccountOperationsStaffRequiredMixin, FormView):
+    template_name = "accounts/user_edit.html"
+    form_class = AccountEditForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.account_detail = get_account_detail(kwargs["user_id"])
+        if not can_view_account_detail(request.user, self.account_detail.user):
+            raise PermissionDenied
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_initial(self):
+        user = self.account_detail.user
+        return {
+            "username": user.username,
+            "first_name": user.first_name,
+            "last_name": user.last_name,
+            "email": user.email,
+            "role": self.account_detail.role,
+            "is_active": user.is_active,
+        }
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["account_detail"] = self.account_detail
+        context["target_user"] = self.account_detail.user
+        return context
+
+    def form_valid(self, form):
+        try:
+            update_account(
+                actor=self.request.user,
+                user_id=self.account_detail.user.id,
+                username=form.cleaned_data["username"],
+                first_name=form.cleaned_data.get("first_name", ""),
+                last_name=form.cleaned_data.get("last_name", ""),
+                email=form.cleaned_data.get("email", ""),
+                role=form.cleaned_data["role"],
+                is_active=form.cleaned_data.get("is_active", False),
+            )
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Account updated.")
+        return redirect("accounts:user-detail", user_id=self.account_detail.user.id)
+
+
+class AccountUserLinksView(AccountOperationsStaffRequiredMixin, FormView):
+    template_name = "accounts/user_links.html"
+    form_class = UserPlayerLinkForm
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
+    def form_valid(self, form):
+        action = self.request.POST.get("action", "create")
+        try:
+            if action == "create":
+                create_user_player_link(
+                    actor=self.request.user,
+                    user_id=self.account_detail.user.id,
+                    player=form.cleaned_data["player"],
+                    relationship=form.cleaned_data["relationship"],
+                    is_primary=form.cleaned_data.get("is_primary", False),
+                )
+                messages.success(self.request, "Player link created.")
+            else:
+                raise ValidationError("Unsupported link action.")
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        return redirect("accounts:user-links", user_id=self.account_detail.user.id)
+
+    def post(self, request, *args, **kwargs):
+        action = request.POST.get("action", "create")
+        if action == "create":
+            return super().post(request, *args, **kwargs)
+
+        form = self.form_class()
+        try:
+            link_id = int(request.POST.get("link_id", ""))
+            if action == "deactivate":
+                deactivate_user_player_link(actor=request.user, user_id=self.account_detail.user.id, link_id=link_id)
+                messages.success(request, "Player link deactivated.")
+            elif action == "reactivate":
+                reactivate_user_player_link(actor=request.user, user_id=self.account_detail.user.id, link_id=link_id)
+                messages.success(request, "Player link reactivated.")
+            elif action == "set_primary":
+                set_primary_user_player_link(actor=request.user, user_id=self.account_detail.user.id, link_id=link_id)
+                messages.success(request, "Primary self link updated.")
+            else:
+                raise ValidationError("Unsupported link action.")
+        except (TypeError, ValueError, ValidationError) as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        return redirect("accounts:user-links", user_id=self.account_detail.user.id)
+
+
 class AccountOnlyCreateView(AccountOperationsStaffRequiredMixin, FormView):
     template_name = "accounts/account_create.html"
     form_class = AccountOnlyCreateForm
diff --git a/project_flat_file.txt b/project_flat_file.txt
index be36c9f..3894c97 100644
--- a/project_flat_file.txt
+++ b/project_flat_file.txt
@@ -1,6 +1,6 @@
 # Project Flat File Snapshot
 # Root: /Users/eugenelin/dev/vmba0
-# File count: 347
+# File count: 351
 # Excluded directories: .git, .venv, __pycache__, node_modules, dist, build
 # Excluded unrelated untracked scratch files.
 # Text files are included as UTF-8/decoded text. Binary files are described, not embedded.
@@ -501,7 +501,7 @@ CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 from django import forms
 
-from accounts.models import AccountRole
+from accounts.models import AccountRole, UserPlayerRelationship
 from players.models import Player
 
 
@@ -534,6 +534,25 @@ class PlayerAccountCreateForm(forms.Form):
         super().__init__(*args, **kwargs)
         self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")
 
+
+class AccountEditForm(forms.Form):
+    username = forms.CharField(max_length=150)
+    first_name = forms.CharField(max_length=150, required=False)
+    last_name = forms.CharField(max_length=150, required=False)
+    email = forms.EmailField(required=False)
+    role = forms.ChoiceField(choices=AccountRole.choices)
+    is_active = forms.BooleanField(required=False, label="Account is active")
+
+
+class UserPlayerLinkForm(forms.Form):
+    player = forms.ModelChoiceField(queryset=Player.objects.none())
+    relationship = forms.ChoiceField(choices=UserPlayerRelationship.choices)
+    is_primary = forms.BooleanField(required=False, label="Primary self link")
+
+    def __init__(self, *args, **kwargs):
+        super().__init__(*args, **kwargs)
+        self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/accounts/middleware.py
 ====================================================================================================
@@ -667,6 +686,7 @@ FILE: /Users/eugenelin/dev/vmba0/accounts/migrations/__init__.py
 CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/accounts/models.py
 ====================================================================================================
@@ -817,6 +837,12 @@ from accounts.models import AccountRole, UserPlayerLink
 from accounts.services import account_query_service
 from accounts.services.account_query_service import AccountListFilters
 from accounts.services.email_service import find_existing_email_user, normalize_email
+from accounts.services.link_service import (
+    activate_link,
+    deactivate_link,
+    link_user_to_player,
+    set_primary_self_link,
+)
 from accounts.services.password_service import (
     generate_birthdate_password,
     mark_password_change_required,
@@ -825,7 +851,7 @@ from accounts.services.password_service import (
 from accounts.services.profile_service import get_or_create_account_profile, set_account_role
 from accounts.services.provisioning_service import STATUS_CREATED, provision_player_account
 from accounts.services.role_service import role_label
-from accounts.services.username_service import validate_available_username
+from accounts.services.username_service import validate_available_username, validate_available_username_for_user
 from players.models import Player
 
 
@@ -895,11 +921,35 @@ class CreatedAccountResult:
     player: Player | None = None
 
 
+@dataclass(frozen=True)
+class UpdatedAccountResult:
+    user: User
+    username: str
+    role: str
+    role_label: str
+    is_active: bool
+
+
+@dataclass(frozen=True)
+class UpdatedLinkResult:
+    link: UserPlayerLink
+    user: User
+    player: Player
+    relationship: str
+    is_primary: bool
+    is_active: bool
+
+
 def _validate_actor_can_create_role(actor, role: str) -> None:
     if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
         raise ValidationError("Only superusers can create admin accounts.")
 
 
+def _validate_actor_can_assign_role(actor, role: str) -> None:
+    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
+        raise ValidationError("Only superusers can assign admin role.")
+
+
 def _validate_email_available(email: str) -> str:
     normalized = normalize_email(email)
     if normalized and find_existing_email_user(normalized):
@@ -907,6 +957,15 @@ def _validate_email_available(email: str) -> str:
     return normalized
 
 
+def _validate_email_available_for_user(user: User, email: str) -> str:
+    normalized = normalize_email(email)
+    if normalized:
+        existing_user = find_existing_email_user(normalized)
+        if existing_user and existing_user.pk != user.pk:
+            raise ValidationError("Email is already in use.")
+    return normalized
+
+
 def _role_for_user(user: User) -> str:
     profile = getattr(user, "account_profile", None)
     if profile:
@@ -947,6 +1006,36 @@ def _linked_player_row(link: UserPlayerLink) -> LinkedPlayerRow:
     )
 
 
+def _updated_account_result(user: User) -> UpdatedAccountResult:
+    role = _role_for_user(user)
+    return UpdatedAccountResult(
+        user=user,
+        username=user.username,
+        role=role,
+        role_label=role_label(role),
+        is_active=user.is_active,
+    )
+
+
+def _updated_link_result(link: UserPlayerLink) -> UpdatedLinkResult:
+    return UpdatedLinkResult(
+        link=link,
+        user=link.user,
+        player=link.player,
+        relationship=link.relationship,
+        is_primary=link.is_primary,
+        is_active=link.is_active,
+    )
+
+
+def _get_user_for_update(user_id: int) -> User:
+    return User.objects.select_for_update().select_related("account_profile").get(pk=user_id)
+
+
+def _get_link_for_user(user: User, link_id: int) -> UserPlayerLink:
+    return UserPlayerLink.objects.select_for_update().select_related("user", "player").get(pk=link_id, user=user)
+
+
 def get_account_operations_dashboard() -> AccountOperationsDashboard:
     """Return the read-only Account Operations dashboard context."""
     users = User.objects.select_related("account_profile")
@@ -1032,6 +1121,93 @@ def get_account_detail(user_id: int) -> AccountDetailContext:
     )
 
 
+@transaction.atomic
+def update_account(
+    *,
+    actor,
+    user_id: int,
+    username: str,
+    first_name: str = "",
+    last_name: str = "",
+    email: str = "",
+    role: str = AccountRole.GUEST_EVALUATOR,
+    is_active: bool = True,
+) -> UpdatedAccountResult:
+    """Update lifecycle and profile fields for an existing account."""
+    _validate_actor_can_assign_role(actor, role)
+    user = _get_user_for_update(user_id)
+    user.username = validate_available_username_for_user(user, username)
+    user.first_name = str(first_name or "").strip()
+    user.last_name = str(last_name or "").strip()
+    user.email = _validate_email_available_for_user(user, email)
+    user.is_active = bool(is_active)
+    user.save(update_fields=["username", "first_name", "last_name", "email", "is_active"])
+    set_account_role(user, role, actor=actor)
+    user.refresh_from_db()
+    return _updated_account_result(user)
+
+
+@transaction.atomic
+def activate_account(*, actor, user_id: int) -> UpdatedAccountResult:
+    """Activate an existing account without changing profile or link history."""
+    user = _get_user_for_update(user_id)
+    if not user.is_active:
+        user.is_active = True
+        user.save(update_fields=["is_active"])
+    return _updated_account_result(user)
+
+
+@transaction.atomic
+def deactivate_account(*, actor, user_id: int) -> UpdatedAccountResult:
+    """Deactivate an existing account without deleting account data or links."""
+    user = _get_user_for_update(user_id)
+    if user.is_active:
+        user.is_active = False
+        user.save(update_fields=["is_active"])
+    return _updated_account_result(user)
+
+
+@transaction.atomic
+def create_user_player_link(
+    *,
+    actor,
+    user_id: int,
+    player: Player,
+    relationship: str,
+    is_primary: bool = False,
+) -> UpdatedLinkResult:
+    """Create an active user/player link through the account operations workflow."""
+    user = _get_user_for_update(user_id)
+    if UserPlayerLink.objects.filter(user=user, player=player, relationship=relationship, is_active=True).exists():
+        raise ValidationError("An active link already exists for this user, player, and relationship.")
+    link = link_user_to_player(user, player, relationship=relationship, is_primary=is_primary)
+    return _updated_link_result(link)
+
+
+@transaction.atomic
+def deactivate_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
+    """Deactivate a user/player link without deleting its history."""
+    user = _get_user_for_update(user_id)
+    link = _get_link_for_user(user, link_id)
+    return _updated_link_result(deactivate_link(link, actor=actor))
+
+
+@transaction.atomic
+def reactivate_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
+    """Reactivate an existing inactive user/player link when constraints allow it."""
+    user = _get_user_for_update(user_id)
+    link = _get_link_for_user(user, link_id)
+    return _updated_link_result(activate_link(link, actor=actor))
+
+
+@transaction.atomic
+def set_primary_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
+    """Set an existing self link as the active primary player link."""
+    user = _get_user_for_update(user_id)
+    link = _get_link_for_user(user, link_id)
+    return _updated_link_result(set_primary_self_link(link, actor=actor))
+
+
 @transaction.atomic
 def create_account_only(
     *,
@@ -1320,6 +1496,7 @@ CONTENT-TYPE: text/plain; charset=utf-8
 from django.contrib.auth import get_user_model
 from django.core.exceptions import ValidationError
 from django.db import IntegrityError, transaction
+from django.db.models import Q
 
 from accounts.models import UserPlayerLink, UserPlayerRelationship
 from players.models import Player, PlayerImportBatch
@@ -1484,6 +1661,30 @@ def activate_link(link, actor=None) -> UserPlayerLink:
     return link
 
 
+@transaction.atomic
+def set_primary_self_link(link, actor=None) -> UserPlayerLink:
+    """Make a self link the active primary link for its user and player."""
+    if not isinstance(link, UserPlayerLink):
+        raise ValidationError("A valid user/player link is required.")
+    if link.relationship != UserPlayerRelationship.SELF:
+        raise ValidationError("Only self links can be primary.")
+
+    UserPlayerLink.objects.select_for_update().filter(
+        Q(user=link.user) | Q(player=link.player),
+        relationship=UserPlayerRelationship.SELF,
+        is_active=True,
+        is_primary=True,
+    ).exclude(pk=link.pk).update(is_primary=False)
+
+    link.is_active = True
+    link.is_primary = True
+    try:
+        link.save(update_fields=["is_active", "is_primary", "updated_at"])
+    except IntegrityError as exc:
+        raise ValidationError("This primary self link conflicts with an existing active link.") from exc
+    return link
+
+
 @transaction.atomic
 def unlink_user_from_player(user, player, relationship=None, actor=None) -> int:
     """Deactivate active links between a user and player, optionally for one relationship."""
@@ -2123,17 +2324,33 @@ def username_for_player(player) -> str:
     return username
 
 
-def validate_available_username(username: str) -> str:
-    """Validate an explicitly supplied username and return the normalized value."""
+def _normalize_explicit_username(username: str) -> str:
     cleaned = str(username or "").strip().casefold()
     if not cleaned:
         raise ValidationError("Username is required.")
     if USERNAME_ALLOWED_PATTERN.search(cleaned):
         raise ValidationError("Username may contain only letters, numbers, dots, underscores, and hyphens.")
+    return cleaned
+
+
+def validate_available_username(username: str) -> str:
+    """Validate an explicitly supplied username and return the normalized value."""
+    cleaned = _normalize_explicit_username(username)
     if User.objects.filter(username__iexact=cleaned).exists():
         raise ValidationError("Username is already in use.")
     return cleaned
 
+
+def validate_available_username_for_user(user, username: str) -> str:
+    """Validate a username change while allowing the current user's username."""
+    if not isinstance(user, User):
+        raise ValidationError("A valid user is required.")
+    cleaned = _normalize_explicit_username(username)
+    existing_user = User.objects.filter(username__iexact=cleaned).first()
+    if existing_user and existing_user.pk != user.pk:
+        raise ValidationError("Username is already in use.")
+    return cleaned
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/account_create.html
 ====================================================================================================
@@ -2449,7 +2666,7 @@ CONTENT-TYPE: text/plain; charset=utf-8
 {% extends "pdp/base.html" %}
 
 {% block pdp_title %}Account Detail{% endblock %}
-{% block pdp_subtitle %}Read-only account and linked player context.{% endblock %}
+{% block pdp_subtitle %}Account and linked player context.{% endblock %}
 
 {% block pdp_content %}
 <section class="pdp-grid pdp-grid--single">
@@ -2497,7 +2714,11 @@ CONTENT-TYPE: text/plain; charset=utf-8
             <dt>Last login</dt>
             <dd>{{ target_user.last_login|default:"-" }}</dd>
         </dl>
-        <p><a class="button button--ghost" href="{% url 'accounts:user-list' %}">Back to users</a></p>
+        <div class="pdp-actions">
+            <a class="button button--primary" href="{% url 'accounts:user-edit' target_user.id %}">Edit Account</a>
+            <a class="button button--ghost" href="{% url 'accounts:user-links' target_user.id %}">Manage Links</a>
+            <a class="button button--ghost" href="{% url 'accounts:user-list' %}">Back to users</a>
+        </div>
     </article>
 
     <article class="pdp-card">
@@ -2534,6 +2755,162 @@ CONTENT-TYPE: text/plain; charset=utf-8
 </section>
 {% endblock %}
 
+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/user_edit.html
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Edit Account{% endblock %}
+{% block pdp_subtitle %}Manage account lifecycle, username, and role.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>{{ target_user.get_full_name|default:target_user.username }}</h2>
+        <form method="post" class="pdp-form">
+            {% csrf_token %}
+            {{ form.non_field_errors }}
+            <label>
+                Username
+                {{ form.username }}
+                {{ form.username.errors }}
+            </label>
+            <label>
+                First name
+                {{ form.first_name }}
+                {{ form.first_name.errors }}
+            </label>
+            <label>
+                Last name
+                {{ form.last_name }}
+                {{ form.last_name.errors }}
+            </label>
+            <label>
+                Email
+                {{ form.email }}
+                {{ form.email.errors }}
+            </label>
+            <label>
+                Role
+                {{ form.role }}
+                {{ form.role.errors }}
+            </label>
+            <label>
+                {{ form.is_active }}
+                {{ form.is_active.label }}
+                {{ form.is_active.errors }}
+            </label>
+            <div class="pdp-actions">
+                <button class="button button--primary" type="submit">Save Account</button>
+                <a class="button button--ghost" href="{% url 'accounts:user-detail' target_user.id %}">Cancel</a>
+            </div>
+        </form>
+    </article>
+</section>
+{% endblock %}
+
+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/user_links.html
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Manage Player Links{% endblock %}
+{% block pdp_subtitle %}Create, deactivate, reactivate, and manage primary self links.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>{{ target_user.get_full_name|default:target_user.username }}</h2>
+        <form method="post" class="pdp-form">
+            {% csrf_token %}
+            <input type="hidden" name="action" value="create">
+            {{ form.non_field_errors }}
+            <label>
+                Player
+                {{ form.player }}
+                {{ form.player.errors }}
+            </label>
+            <label>
+                Relationship
+                {{ form.relationship }}
+                {{ form.relationship.errors }}
+            </label>
+            <label>
+                {{ form.is_primary }}
+                {{ form.is_primary.label }}
+                {{ form.is_primary.errors }}
+            </label>
+            <div class="pdp-actions">
+                <button class="button button--primary" type="submit">Create Link</button>
+                <a class="button button--ghost" href="{% url 'accounts:user-detail' target_user.id %}">Back to account</a>
+            </div>
+        </form>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Existing Links</h2>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr>
+                        <th>Player</th>
+                        <th>Relationship</th>
+                        <th>Primary</th>
+                        <th>Status</th>
+                        <th>Imported</th>
+                        <th></th>
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
+                            <td>
+                                <div class="pdp-actions">
+                                    {% if row.is_active %}
+                                        <form method="post">
+                                            {% csrf_token %}
+                                            <input type="hidden" name="action" value="deactivate">
+                                            <input type="hidden" name="link_id" value="{{ row.link.id }}">
+                                            <button class="button button--ghost" type="submit">Deactivate</button>
+                                        </form>
+                                    {% else %}
+                                        <form method="post">
+                                            {% csrf_token %}
+                                            <input type="hidden" name="action" value="reactivate">
+                                            <input type="hidden" name="link_id" value="{{ row.link.id }}">
+                                            <button class="button button--ghost" type="submit">Reactivate</button>
+                                        </form>
+                                    {% endif %}
+                                    {% if row.link.relationship == "self" and not row.is_primary %}
+                                        <form method="post">
+                                            {% csrf_token %}
+                                            <input type="hidden" name="action" value="set_primary">
+                                            <input type="hidden" name="link_id" value="{{ row.link.id }}">
+                                            <button class="button button--ghost" type="submit">Set Primary</button>
+                                        </form>
+                                    {% endif %}
+                                </div>
+                            </td>
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
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/user_list.html
 ====================================================================================================
@@ -2689,11 +3066,18 @@ from django.contrib.auth import SESSION_KEY
 
 from accounts.models import AccountProfile, AccountRole, UserPlayerLink, UserPlayerRelationship
 from accounts.services.account_operations_service import (
+    activate_account,
     create_account_only,
     create_player_account,
+    create_user_player_link,
+    deactivate_account,
+    deactivate_user_player_link,
     get_account_detail,
     get_account_list,
     get_account_operations_dashboard,
+    reactivate_user_player_link,
+    set_primary_user_player_link,
+    update_account,
 )
 from accounts.services.account_query_service import AccountListFilters, count_players_without_self_link, filter_account_users
 from accounts.services.auth_redirect_service import (
@@ -2727,6 +3111,7 @@ from accounts.services.link_service import (
     get_users_for_player,
     is_player_self,
     link_user_to_player,
+    set_primary_self_link,
     unlink_user_from_player,
 )
 from accounts.services.password_service import (
@@ -2751,6 +3136,7 @@ from accounts.services.username_service import (
     base_username_for_player,
     normalize_username_part,
     validate_available_username,
+    validate_available_username_for_user,
     username_for_player,
 )
 from analytics.services.permissions import can_submit_coach_assessment
@@ -3100,6 +3486,147 @@ class AccountOperationsServiceTests(TestCase):
         with self.assertRaises(ValidationError):
             create_player_account(actor=self.staff, player=self.player, role=AccountRole.COACH)
 
+    def test_update_account_changes_lifecycle_username_email_and_role(self):
+        result = update_account(
+            actor=self.staff,
+            user_id=self.coach.id,
+            username=" Coach.Updated ",
+            first_name="Updated",
+            last_name="Coach",
+            email="UPDATED@example.com",
+            role=AccountRole.GUEST_EVALUATOR,
+            is_active=False,
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(result.username, "coach.updated")
+        self.assertEqual(result.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(result.is_active)
+        self.assertEqual(self.coach.username, "coach.updated")
+        self.assertEqual(self.coach.email, "updated@example.com")
+        self.assertEqual(self.coach.account_profile.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(self.coach.is_staff)
+        self.assertFalse(self.coach.is_superuser)
+
+    def test_update_account_rejects_duplicate_username_and_email(self):
+        User.objects.create_user(username="taken", email="taken@example.com")
+
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.coach.id,
+                username="TAKEN",
+                email="coach@example.com",
+                role=AccountRole.COACH,
+            )
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.coach.id,
+                username="coach.one",
+                email="Taken@Example.com",
+                role=AccountRole.COACH,
+            )
+
+    def test_update_account_admin_role_requires_superuser(self):
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.coach.id,
+                username="coach.one",
+                role=AccountRole.ADMIN,
+            )
+
+        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
+        result = update_account(
+            actor=superuser,
+            user_id=self.coach.id,
+            username="coach.one",
+            role=AccountRole.ADMIN,
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(result.role, AccountRole.ADMIN)
+        self.assertEqual(self.coach.account_profile.role, AccountRole.ADMIN)
+        self.assertFalse(self.coach.is_staff)
+        self.assertFalse(self.coach.is_superuser)
+
+    def test_activate_and_deactivate_account_preserve_profile_and_links(self):
+        deactivate_result = deactivate_account(actor=self.staff, user_id=self.player_user.id)
+        self.player_user.refresh_from_db()
+        link = UserPlayerLink.objects.get(user=self.player_user, player=self.player)
+
+        self.assertFalse(deactivate_result.is_active)
+        self.assertFalse(self.player_user.is_active)
+        self.assertEqual(self.player_user.account_profile.role, AccountRole.PLAYER)
+        self.assertTrue(link.is_active)
+
+        activate_result = activate_account(actor=self.staff, user_id=self.player_user.id)
+        self.player_user.refresh_from_db()
+
+        self.assertTrue(activate_result.is_active)
+        self.assertTrue(self.player_user.is_active)
+        self.assertTrue(UserPlayerLink.objects.get(pk=link.pk).is_active)
+
+    def test_account_operations_manage_player_links_through_services(self):
+        link_result = create_user_player_link(
+            actor=self.staff,
+            user_id=self.coach.id,
+            player=self.player,
+            relationship=UserPlayerRelationship.COACH,
+            is_primary=False,
+        )
+
+        self.assertTrue(link_result.is_active)
+        self.assertFalse(link_result.is_primary)
+        with self.assertRaises(ValidationError):
+            create_user_player_link(
+                actor=self.staff,
+                user_id=self.coach.id,
+                player=self.player,
+                relationship=UserPlayerRelationship.COACH,
+                is_primary=False,
+            )
+
+        deactivated = deactivate_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id)
+        self.assertFalse(deactivated.is_active)
+        self.assertFalse(UserPlayerLink.objects.get(pk=link_result.link.id).is_primary)
+
+        reactivated = reactivate_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id)
+        self.assertTrue(reactivated.is_active)
+
+    def test_account_operations_set_primary_self_link_switches_existing_primary(self):
+        other_player = Player.objects.create(first_name="Second", last_name="Player")
+        first_link = UserPlayerLink.objects.get(user=self.player_user, player=self.player)
+        second_link = create_user_player_link(
+            actor=self.staff,
+            user_id=self.player_user.id,
+            player=other_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        ).link
+
+        result = set_primary_user_player_link(actor=self.staff, user_id=self.player_user.id, link_id=second_link.id)
+        first_link.refresh_from_db()
+        second_link.refresh_from_db()
+
+        self.assertTrue(result.is_primary)
+        self.assertFalse(first_link.is_primary)
+        self.assertTrue(second_link.is_primary)
+        self.assertEqual(UserPlayerLink.objects.filter(user=self.player_user, is_primary=True, is_active=True).count(), 1)
+
+    def test_account_operations_reject_primary_non_self_link(self):
+        link = create_user_player_link(
+            actor=self.staff,
+            user_id=self.coach.id,
+            player=self.player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        ).link
+
+        with self.assertRaises(ValidationError):
+            set_primary_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link.id)
+
 
 class UserPlayerLinkModelTests(TestCase):
     def setUp(self):
@@ -3391,6 +3918,35 @@ class UserPlayerLinkServiceTests(TestCase):
         self.assertTrue(is_player_self(self.user, self.player))
         self.assertFalse(is_player_self(self.user, self.other_player))
 
+    def test_set_primary_self_link_switches_primary_link(self):
+        first_link = link_user_to_player(self.user, self.player)
+        second_link = link_user_to_player(
+            self.user,
+            self.other_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        )
+
+        set_primary_self_link(second_link)
+        first_link.refresh_from_db()
+        second_link.refresh_from_db()
+
+        self.assertFalse(first_link.is_primary)
+        self.assertTrue(second_link.is_primary)
+        self.assertTrue(second_link.is_active)
+        self.assertEqual(get_primary_player(self.user), self.other_player)
+
+    def test_set_primary_self_link_rejects_non_self_link(self):
+        parent_link = link_user_to_player(
+            self.user,
+            self.player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        )
+
+        with self.assertRaises(ValidationError):
+            set_primary_self_link(parent_link)
+
     def test_is_player_self_ignores_inactive_or_non_self_links(self):
         parent_link = link_user_to_player(
             self.user,
@@ -3431,6 +3987,14 @@ class AccountUsernameServiceTests(TestCase):
         with self.assertRaises(ValidationError):
             validate_available_username("bad username")
 
+    def test_validate_available_username_for_user_allows_current_user(self):
+        user = User.objects.create_user(username="coach.one")
+        User.objects.create_user(username="other")
+
+        self.assertEqual(validate_available_username_for_user(user, " Coach.One "), "coach.one")
+        with self.assertRaises(ValidationError):
+            validate_available_username_for_user(user, "OTHER")
+
 
 class AccountEmailServiceTests(TestCase):
     def test_email_normalization_and_comparison(self):
@@ -3916,6 +4480,147 @@ class AccountOperationsViewTests(TestCase):
         self.assertContains(response, "coach@example.com")
         self.assertContains(response, "Coach")
         self.assertContains(response, "Alex Player")
+        self.assertContains(response, reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}))
+        self.assertContains(response, reverse("accounts:user-links", kwargs={"user_id": self.coach.id}))
+
+    def test_user_edit_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_edit_account_lifecycle_username_and_role(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
+            {
+                "username": " Coach.Updated ",
+                "first_name": "Updated",
+                "last_name": "Coach",
+                "email": "updated@example.com",
+                "role": AccountRole.GUEST_EVALUATOR,
+            },
+        )
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
+        self.coach.refresh_from_db()
+        self.assertEqual(self.coach.username, "coach.updated")
+        self.assertFalse(self.coach.is_active)
+        self.assertEqual(self.coach.account_profile.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(self.coach.is_staff)
+        self.assertFalse(self.coach.is_superuser)
+
+    def test_staff_user_edit_rejects_duplicate_username_and_admin_role(self):
+        User.objects.create_user(username="taken")
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
+            {
+                "username": "taken",
+                "role": AccountRole.COACH,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Username is already in use")
+
+        response = self.client.post(
+            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
+            {
+                "username": "coach.one",
+                "role": AccountRole.ADMIN,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Only superusers can assign admin role")
+        self.coach.refresh_from_db()
+        self.assertEqual(self.coach.account_profile.role, AccountRole.COACH)
+
+    def test_user_links_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:user-links", kwargs={"user_id": self.coach.id}))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_create_deactivate_and_reactivate_link(self):
+        other_player = Player.objects.create(first_name="Blake", last_name="Player")
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {
+                "action": "create",
+                "player": other_player.id,
+                "relationship": UserPlayerRelationship.PARENT,
+            },
+        )
+
+        self.assertEqual(response.status_code, 302)
+        link = UserPlayerLink.objects.get(user=self.coach, player=other_player, relationship=UserPlayerRelationship.PARENT)
+        self.assertTrue(link.is_active)
+        self.assertFalse(link.is_primary)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "deactivate", "link_id": link.id},
+        )
+        self.assertEqual(response.status_code, 302)
+        link.refresh_from_db()
+        self.assertFalse(link.is_active)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "reactivate", "link_id": link.id},
+        )
+        self.assertEqual(response.status_code, 302)
+        link.refresh_from_db()
+        self.assertTrue(link.is_active)
+
+    def test_staff_can_set_primary_self_link_from_links_page(self):
+        first_player = Player.objects.create(first_name="Self", last_name="One")
+        second_player = Player.objects.create(first_name="Self", last_name="Two")
+        first_link = link_user_to_player(self.coach, first_player, relationship=UserPlayerRelationship.SELF)
+        second_link = link_user_to_player(
+            self.coach,
+            second_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        )
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "set_primary", "link_id": second_link.id},
+        )
+
+        self.assertEqual(response.status_code, 302)
+        first_link.refresh_from_db()
+        second_link.refresh_from_db()
+        self.assertFalse(first_link.is_primary)
+        self.assertTrue(second_link.is_primary)
+
+    def test_links_page_rejects_duplicate_active_link(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {
+                "action": "create",
+                "player": self.player.id,
+                "relationship": UserPlayerRelationship.COACH,
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "An active link already exists")
 
     def test_profile_page_links_staff_to_account_operations(self):
         self.client.force_login(self.staff)
@@ -4166,6 +4871,8 @@ from accounts.views import (
     AccountPasswordChangeView,
     AccountProfileView,
     AccountUserDetailView,
+    AccountUserEditView,
+    AccountUserLinksView,
     AccountUserListView,
     PlayerAccountCreateView,
 )
@@ -4183,6 +4890,8 @@ urlpatterns = [
     path("profile/", AccountProfileView.as_view(), name="profile"),
     path("users/", AccountUserListView.as_view(), name="user-list"),
     path("users/<int:user_id>/", AccountUserDetailView.as_view(), name="user-detail"),
+    path("users/<int:user_id>/edit/", AccountUserEditView.as_view(), name="user-edit"),
+    path("users/<int:user_id>/links/", AccountUserLinksView.as_view(), name="user-links"),
 ]
 
 ====================================================================================================
@@ -4198,13 +4907,18 @@ from django.core.exceptions import PermissionDenied, ValidationError
 from django.shortcuts import redirect
 from django.views.generic import FormView, TemplateView
 
-from accounts.forms import AccountOnlyCreateForm, PlayerAccountCreateForm
+from accounts.forms import AccountEditForm, AccountOnlyCreateForm, PlayerAccountCreateForm, UserPlayerLinkForm
 from accounts.services.account_operations_service import (
     create_account_only,
     create_player_account,
+    create_user_player_link,
+    deactivate_user_player_link,
     get_account_detail,
     get_account_list,
     get_account_operations_dashboard,
+    reactivate_user_player_link,
+    set_primary_user_player_link,
+    update_account,
 )
 from accounts.services.account_query_service import parse_account_list_filters
 from accounts.services.auth_redirect_service import (
@@ -4331,6 +5045,113 @@ class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
         return context
 
 
+class AccountUserEditView(AccountOperationsStaffRequiredMixin, FormView):
+    template_name = "accounts/user_edit.html"
+    form_class = AccountEditForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.account_detail = get_account_detail(kwargs["user_id"])
+        if not can_view_account_detail(request.user, self.account_detail.user):
+            raise PermissionDenied
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_initial(self):
+        user = self.account_detail.user
+        return {
+            "username": user.username,
+            "first_name": user.first_name,
+            "last_name": user.last_name,
+            "email": user.email,
+            "role": self.account_detail.role,
+            "is_active": user.is_active,
+        }
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["account_detail"] = self.account_detail
+        context["target_user"] = self.account_detail.user
+        return context
+
+    def form_valid(self, form):
+        try:
+            update_account(
+                actor=self.request.user,
+                user_id=self.account_detail.user.id,
+                username=form.cleaned_data["username"],
+                first_name=form.cleaned_data.get("first_name", ""),
+                last_name=form.cleaned_data.get("last_name", ""),
+                email=form.cleaned_data.get("email", ""),
+                role=form.cleaned_data["role"],
+                is_active=form.cleaned_data.get("is_active", False),
+            )
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Account updated.")
+        return redirect("accounts:user-detail", user_id=self.account_detail.user.id)
+
+
+class AccountUserLinksView(AccountOperationsStaffRequiredMixin, FormView):
+    template_name = "accounts/user_links.html"
+    form_class = UserPlayerLinkForm
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
+    def form_valid(self, form):
+        action = self.request.POST.get("action", "create")
+        try:
+            if action == "create":
+                create_user_player_link(
+                    actor=self.request.user,
+                    user_id=self.account_detail.user.id,
+                    player=form.cleaned_data["player"],
+                    relationship=form.cleaned_data["relationship"],
+                    is_primary=form.cleaned_data.get("is_primary", False),
+                )
+                messages.success(self.request, "Player link created.")
+            else:
+                raise ValidationError("Unsupported link action.")
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        return redirect("accounts:user-links", user_id=self.account_detail.user.id)
+
+    def post(self, request, *args, **kwargs):
+        action = request.POST.get("action", "create")
+        if action == "create":
+            return super().post(request, *args, **kwargs)
+
+        form = self.form_class()
+        try:
+            link_id = int(request.POST.get("link_id", ""))
+            if action == "deactivate":
+                deactivate_user_player_link(actor=request.user, user_id=self.account_detail.user.id, link_id=link_id)
+                messages.success(request, "Player link deactivated.")
+            elif action == "reactivate":
+                reactivate_user_player_link(actor=request.user, user_id=self.account_detail.user.id, link_id=link_id)
+                messages.success(request, "Player link reactivated.")
+            elif action == "set_primary":
+                set_primary_user_player_link(actor=request.user, user_id=self.account_detail.user.id, link_id=link_id)
+                messages.success(request, "Primary self link updated.")
+            else:
+                raise ValidationError("Unsupported link action.")
+        except (TypeError, ValueError, ValidationError) as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        return redirect("accounts:user-links", user_id=self.account_detail.user.id)
+
+
 class AccountOnlyCreateView(AccountOperationsStaffRequiredMixin, FormView):
     template_name = "accounts/account_create.html"
     form_class = AccountOnlyCreateForm
@@ -5123,6 +5944,7 @@ FILE: /Users/eugenelin/dev/vmba0/analytics/migrations/__init__.py
 CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/analytics/models.py
 ====================================================================================================
@@ -10824,6 +11646,13 @@ class StaffObservationReviewDetailView(AnalyticsStaffRequiredMixin, CoachAssessm
             messages.success(request, "Assessment reopened for editing.")
         return redirect("analytics:observation-review-detail", observation_id=self.observation.pk)
 
+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/db.sqlite3
+====================================================================================================
+CONTENT-TYPE: application/octet-stream
+----------------------------------------------------------------------------------------------------
+[Binary file omitted. Size: 1429504 bytes.]
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/docs/ARCHITECTURE.md
 ====================================================================================================
@@ -23409,7 +24238,6 @@ Current guidance lives in:
 - [Analytics Documentation](../../analytics/README.md)
 - [Account Management V1 Summary](../../account_management/V1_SUMMARY.md)
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/docs/archive/prompts/espn.md
 ====================================================================================================
@@ -41221,6 +42049,7 @@ FILE: /Users/eugenelin/dev/vmba0/home/__init__.py
 CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/home/admin.py
 ====================================================================================================
@@ -41764,6 +42593,7 @@ FILE: /Users/eugenelin/dev/vmba0/home/migrations/__init__.py
 CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/home/models.py
 ====================================================================================================
@@ -41974,6 +42804,7 @@ FILE: /Users/eugenelin/dev/vmba0/leaguehub/__init__.py
 CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/leaguehub/admin.py
 ====================================================================================================
@@ -42539,6 +43370,7 @@ FILE: /Users/eugenelin/dev/vmba0/leaguehub/migrations/__init__.py
 CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/leaguehub/models.py
 ====================================================================================================
@@ -45336,9 +46168,8 @@ if __name__ == '__main__':
 FILE: /Users/eugenelin/dev/vmba0/media/scholarships/transcripts/IMG_7327.jpg
 ====================================================================================================
 CONTENT-TYPE: image/jpeg
-BINARY-SIZE-BYTES: 468766
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 468766 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/pdp/__init__.py
@@ -45346,6 +46177,7 @@ FILE: /Users/eugenelin/dev/vmba0/pdp/__init__.py
 CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/pdp/admin.py
 ====================================================================================================
@@ -46351,6 +47183,7 @@ FILE: /Users/eugenelin/dev/vmba0/pdp/migrations/__init__.py
 CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/pdp/models.py
 ====================================================================================================
@@ -52861,7 +53694,6 @@ class ScholarshipReferenceAdmin(admin.ModelAdmin):
     list_display = ("application", "display_order", "name", "email")
     search_fields = ("name", "email", "application__player_full_name")
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/apps.py
 ====================================================================================================
@@ -52874,7 +53706,6 @@ class ScholarshipsConfig(AppConfig):
     default_auto_field = "django.db.models.BigAutoField"
     name = "scholarships"
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/forms.py
 ====================================================================================================
@@ -53446,7 +54277,6 @@ class ScholarshipReference(TimeStampedModel):
     def __str__(self):
         return f"{self.application.player_full_name} reference {self.display_order}"
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/templates/scholarships/application_detail.html
 ====================================================================================================
@@ -53474,7 +54304,6 @@ CONTENT-TYPE: text/plain; charset=utf-8
 {% include "scholarships/partials/application_readonly.html" with application=object staff_view=False %}
 {% endblock %}
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/templates/scholarships/application_form.html
 ====================================================================================================
@@ -53627,7 +54456,6 @@ CONTENT-TYPE: text/plain; charset=utf-8
 </form>
 {% endblock %}
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/templates/scholarships/base.html
 ====================================================================================================
@@ -53664,7 +54492,6 @@ CONTENT-TYPE: text/plain; charset=utf-8
 {% include "home/includes/nav_script.html" %}
 {% endblock %}
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/templates/scholarships/dashboard.html
 ====================================================================================================
@@ -53751,7 +54578,6 @@ CONTENT-TYPE: text/plain; charset=utf-8
 </section>
 {% endblock %}
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/templates/scholarships/download_application.html
 ====================================================================================================
@@ -53783,7 +54609,6 @@ CONTENT-TYPE: text/plain; charset=utf-8
 </body>
 </html>
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/templates/scholarships/download_cycle.html
 ====================================================================================================
@@ -53821,7 +54646,6 @@ CONTENT-TYPE: text/plain; charset=utf-8
 </body>
 </html>
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/templates/scholarships/login.html
 ====================================================================================================
@@ -54069,7 +54893,6 @@ CONTENT-TYPE: text/plain; charset=utf-8
     </article>
 </section>
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/templates/scholarships/partials/download_application_content.html
 ====================================================================================================
@@ -54149,7 +54972,6 @@ CONTENT-TYPE: text/plain; charset=utf-8
     </div>
 {% endif %}
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/templates/scholarships/signup.html
 ====================================================================================================
@@ -54211,7 +55033,6 @@ CONTENT-TYPE: text/plain; charset=utf-8
 </section>
 {% endblock %}
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/templates/scholarships/staff_application_detail.html
 ====================================================================================================
@@ -54238,7 +55059,6 @@ CONTENT-TYPE: text/plain; charset=utf-8
 {% include "scholarships/partials/application_readonly.html" with application=object staff_view=True %}
 {% endblock %}
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/templates/scholarships/staff_application_list.html
 ====================================================================================================
@@ -54336,7 +55156,6 @@ CONTENT-TYPE: text/plain; charset=utf-8
 </section>
 {% endblock %}
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/tests.py
 ====================================================================================================
@@ -54498,7 +55317,6 @@ urlpatterns = [
     path("staff/cycles/<slug:slug>/download/", StaffCycleDownloadView.as_view(), name="staff-cycle-download"),
 ]
 
-
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/scholarships/views.py
 ====================================================================================================
@@ -58770,161 +59588,141 @@ CONTENT-TYPE: text/plain; charset=utf-8
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-01.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 558139
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 558139 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-02.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 1792127
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 1792127 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-03.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 349003
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 349003 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-04.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 6472
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 6472 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-05.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 269376
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 269376 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-06.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 6670
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 6670 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-07.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 866301
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 866301 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-08.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 6524
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 6524 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-09.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 6910
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 6910 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-10.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 6574
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 6574 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-11.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 1088438
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 1088438 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-12.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 1334355
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 1334355 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/achievement-13.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 6855
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 6855 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/hero-banner.jpg
 ====================================================================================================
 CONTENT-TYPE: image/jpeg
-BINARY-SIZE-BYTES: 304687
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 304687 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/logo.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 2669
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 2669 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/north-fraser-nationals-18u-cp-tryouts.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 1369750
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 1369750 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/programs-hero.jpg
 ====================================================================================================
 CONTENT-TYPE: image/jpeg
-BINARY-SIZE-BYTES: 587570
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 587570 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/registration-hero.jpg
 ====================================================================================================
 CONTENT-TYPE: image/jpeg
-BINARY-SIZE-BYTES: 304687
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 304687 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/vmb_hero-banner.jpg
 ====================================================================================================
 CONTENT-TYPE: image/jpeg
-BINARY-SIZE-BYTES: 304687
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 304687 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/static/images/vmb_logo.png
 ====================================================================================================
 CONTENT-TYPE: image/png
-BINARY-SIZE-BYTES: 386568
 ----------------------------------------------------------------------------------------------------
-Binary file omitted from flat snapshot to save space.
+[Binary file omitted. Size: 386568 bytes.]
 
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/templates/base.html
@@ -59963,6 +60761,7 @@ FILE: /Users/eugenelin/dev/vmba0/vancouverminor/__init__.py
 CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/vancouverminor/asgi.py
 ====================================================================================================
@@ -60192,3 +60991,16 @@ os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vancouverminor.settings')
 
 application = get_wsgi_application()
 
+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/vmba0.code-workspace
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+{
+	"folders": [
+		{
+			"path": "."
+		}
+	],
+	"settings": {}
+}
```

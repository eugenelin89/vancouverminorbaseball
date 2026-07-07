# Prompt 42: Account Management

## User Prompt

```text
You are implementing Platform V1 Account Operations.

Implement Phase B only.

Manual Account Creation

Do NOT implement Phase C, D, E, or F.

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
pdp/

Pay particular attention to:

accounts/services/account_operations_service.py
accounts/services/account_query_service.py
accounts/services/profile_service.py
accounts/services/link_service.py
accounts/services/provisioning_service.py
accounts/services/password_service.py
accounts/services/username_service.py
accounts/views.py
accounts/templates/

==================================================
Scope
==================================================

Implement ONLY Phase B.

Goal:

Allow staff to manually create platform accounts.

Support TWO completely separate workflows.

Workflow 1

Account Only

Creates a Django User + AccountProfile.

Does NOT create or link a Player.

Typical uses:

- staff
- admin
- coach
- evaluator
- volunteer
- commissioner

Workflow 2

Player Account

Creates an account ONLY for an EXISTING players.Player.

It must NEVER create a Player.

Player identity always comes from players.

==================================================
Architecture Rules
==================================================

accounts owns:

- account creation
- usernames
- passwords
- AccountProfile
- UserPlayerLink
- validation

players owns:

- Player creation
- Player identity
- Player search
- imports

Analytics owns nothing here.

Views remain thin.

Business logic belongs in services.

==================================================
Service Ownership
==================================================

Expand:

accounts/services/account_operations_service.py

It becomes the public orchestration layer.

Implement ONLY:

create_account_only(...)

create_player_account(...)

Both should return typed dataclass result objects.

Views should never manipulate User or AccountProfile directly.

==================================================
Create Account Only
==================================================

Inputs:

username
first_name
last_name
email
role
active checkbox

Behavior:

validate username

validate email uniqueness

create User

create AccountProfile

set role

set is_active

set temporary password

must_change_password=True

NO player link

Return success dataclass.

==================================================
Create Player Account
==================================================

Inputs:

existing Player

optional username

optional email

role (default player)

activate account checkbox

Behavior:

Player MUST already exist.

Reuse existing provisioning logic whenever possible.

DO NOT duplicate provisioning logic.

Expected flow:

account_operations_service

↓

provisioning_service

↓

username/password/link services

This should reuse the same safety guarantees as import provisioning.

==================================================
Username Policy
==================================================

username_service remains authoritative.

Default username:

firstname.lastname

Collision handling stays inside username_service.

Views know nothing about collision resolution.

==================================================
Temporary Password
==================================================

Player accounts

Use existing birthdate password rules.

Non-player accounts

Generate secure random temporary password.

DO NOT invent weak passwords.

Passwords must NEVER be displayed again after creation.

Instead:

Display one-time temporary password immediately after successful creation.

Never store it.

Never serialize it.

Never log it.

If browser refreshes,

password is gone.

==================================================
Forms
==================================================

Create forms.

Keep validation inside forms/services.

==================================================
Views
==================================================

Add:

/accounts/create/

/accounts/create/player/

Staff only.

Thin views.

==================================================
Templates
==================================================

Create:

account_create.html

player_account_create.html

Reuse existing layout.

Keep server rendered.

No JavaScript required.

==================================================
Navigation
==================================================

Account Operations dashboard should now include:

Create Account

Create Player Account

==================================================
Player Selection
==================================================

Do NOT implement autocomplete.

Simple searchable dropdown or existing player search helper is sufficient.

Reuse player query services whenever practical.

==================================================
Permissions
==================================================

Staff:

may create normal accounts

Superuser:

may create admin accounts

Regular staff cannot create admins.

Role escalation must remain impossible.

==================================================
Validation
==================================================

Prevent:

duplicate usernames

duplicate active self links

duplicate emails

duplicate player accounts

inactive player linked twice

All validation belongs in services.

==================================================
Do NOT Implement
==================================================

NO activation/deactivation

NO username editing

NO password reset

NO link management UI

NO bulk creation

NO coach import

NO parent import

NO merge

NO audit logging

NO email

NO invitations

==================================================
Testing
==================================================

Add tests for:

services

account-only creation

player account creation

duplicate username

duplicate email

duplicate player account

admin creation permissions

temporary password generation

must_change_password

inactive creation

views

permissions

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
Engineering Recommendations
==================================================

1.

Do NOT duplicate provisioning logic.

Player account creation should become another caller of provisioning_service.

Import provisioning and manual provisioning should share the same implementation.

2.

Introduce a reusable dataclass:

CreatedAccountResult

that can be returned by both import provisioning and manual creation.

3.

Generate random temporary passwords through password_service.

Password generation should have exactly one implementation.

4.

Keep account_operations_service as the only orchestration boundary.

Views should never directly call provisioning_service.

5.

Keep username generation entirely inside username_service.

6.

Do not expose plaintext passwords anywhere except the immediate success page.

7.

Continue to preserve provenance.

Manual accounts must never become "created_from_import".

Imported accounts must retain import provenance.

8.

No models or migrations unless absolutely necessary.

==================================================
Self Review
==================================================

Verify:

Phase B only

No Phase C work

No activation workflows

No password reset

No username changes

No link management UI

No audit logging

No architecture violations

Views remain thin

No duplicated provisioning logic

Working tree clean

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

deviations

technical debt

self-review

confirmation that only Phase B was implemented.
```

## App / Subsystem

account_management

## Work Commit

`574e1a1`

## Work Commit Diff

```diff
diff --git a/accounts/forms.py b/accounts/forms.py
new file mode 100644
index 0000000..3c12be6
--- /dev/null
+++ b/accounts/forms.py
@@ -0,0 +1,34 @@
+from django import forms
+
+from accounts.models import AccountRole
+from players.models import Player
+
+
+ACCOUNT_ONLY_ROLE_CHOICES = (
+    (AccountRole.STAFF, "Staff"),
+    (AccountRole.COACH, "Coach"),
+    (AccountRole.PARENT, "Parent"),
+    (AccountRole.GUEST_EVALUATOR, "Guest Evaluator"),
+    (AccountRole.ADMIN, "Admin"),
+)
+
+
+class AccountOnlyCreateForm(forms.Form):
+    username = forms.CharField(max_length=150)
+    first_name = forms.CharField(max_length=150, required=False)
+    last_name = forms.CharField(max_length=150, required=False)
+    email = forms.EmailField(required=False)
+    role = forms.ChoiceField(choices=ACCOUNT_ONLY_ROLE_CHOICES)
+    is_active = forms.BooleanField(required=False, initial=True, label="Activate account immediately")
+
+
+class PlayerAccountCreateForm(forms.Form):
+    player = forms.ModelChoiceField(queryset=Player.objects.none())
+    username = forms.CharField(max_length=150, required=False, help_text="Leave blank to use firstname.lastname.")
+    email = forms.EmailField(required=False)
+    role = forms.ChoiceField(choices=((AccountRole.PLAYER, "Player"),), initial=AccountRole.PLAYER)
+    is_active = forms.BooleanField(required=False, initial=True, label="Activate account immediately")
+
+    def __init__(self, *args, **kwargs):
+        super().__init__(*args, **kwargs)
+        self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")
diff --git a/accounts/services/account_operations_service.py b/accounts/services/account_operations_service.py
index a1c4c69..4b38248 100644
--- a/accounts/services/account_operations_service.py
+++ b/accounts/services/account_operations_service.py
@@ -3,13 +3,25 @@ from __future__ import annotations
 from dataclasses import dataclass

 from django.contrib.auth import get_user_model
+from django.core.exceptions import ValidationError
+from django.db import transaction
 from django.urls import reverse
 from django.utils import timezone

 from accounts.models import AccountRole, UserPlayerLink
 from accounts.services import account_query_service
 from accounts.services.account_query_service import AccountListFilters
+from accounts.services.email_service import find_existing_email_user, normalize_email
+from accounts.services.password_service import (
+    generate_birthdate_password,
+    mark_password_change_required,
+    set_random_temporary_password,
+)
+from accounts.services.profile_service import get_or_create_account_profile, set_account_role
+from accounts.services.provisioning_service import STATUS_CREATED, provision_player_account
 from accounts.services.role_service import role_label
+from accounts.services.username_service import validate_available_username
+from players.models import Player


 User = get_user_model()
@@ -68,6 +80,28 @@ class AccountDetailContext:
     linked_players: list[LinkedPlayerRow]


+@dataclass(frozen=True)
+class CreatedAccountResult:
+    user: User
+    username: str
+    temporary_password: str
+    role: str
+    role_label: str
+    player: Player | None = None
+
+
+def _validate_actor_can_create_role(actor, role: str) -> None:
+    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
+        raise ValidationError("Only superusers can create admin accounts.")
+
+
+def _validate_email_available(email: str) -> str:
+    normalized = normalize_email(email)
+    if normalized and find_existing_email_user(normalized):
+        raise ValidationError("Email is already in use.")
+    return normalized
+
+
 def _role_for_user(user: User) -> str:
     profile = getattr(user, "account_profile", None)
     if profile:
@@ -191,3 +225,80 @@ def get_account_detail(user_id: int) -> AccountDetailContext:
         role_label=role_label(role),
         linked_players=[_linked_player_row(link) for link in links],
     )
+
+
+@transaction.atomic
+def create_account_only(
+    *,
+    actor,
+    username: str,
+    first_name: str = "",
+    last_name: str = "",
+    email: str = "",
+    role: str = AccountRole.GUEST_EVALUATOR,
+    is_active: bool = True,
+) -> CreatedAccountResult:
+    """Create a login account without creating or linking a player."""
+    _validate_actor_can_create_role(actor, role)
+    username = validate_available_username(username)
+    normalized_email = _validate_email_available(email)
+    user = User.objects.create(
+        username=username,
+        first_name=str(first_name or "").strip(),
+        last_name=str(last_name or "").strip(),
+        email=normalized_email,
+        is_active=bool(is_active),
+    )
+    temporary_password = set_random_temporary_password(user)
+    profile = get_or_create_account_profile(user)
+    if profile.created_from_import or profile.import_batch_id:
+        raise ValidationError("Manual accounts cannot use import provenance.")
+    set_account_role(user, role, actor=actor)
+    mark_password_change_required(user, True)
+    user.refresh_from_db()
+    return CreatedAccountResult(
+        user=user,
+        username=user.username,
+        temporary_password=temporary_password,
+        role=role,
+        role_label=role_label(role),
+    )
+
+
+@transaction.atomic
+def create_player_account(
+    *,
+    actor,
+    player,
+    username: str = "",
+    email: str = "",
+    role: str = AccountRole.PLAYER,
+    is_active: bool = True,
+) -> CreatedAccountResult:
+    """Create a login account for an existing canonical player."""
+    if not isinstance(player, Player):
+        raise ValidationError("A valid existing player is required.")
+    _validate_actor_can_create_role(actor, role)
+    if role != AccountRole.PLAYER:
+        raise ValidationError("Player account creation must use the player role in Phase B.")
+    normalized_email = _validate_email_available(email)
+    result = provision_player_account(
+        player,
+        actor=actor,
+        email=normalized_email,
+        activate_user=bool(is_active),
+        username=username,
+    )
+    if result.status != STATUS_CREATED or not result.user_id:
+        message = "; ".join(result.messages) if result.messages else "Player account could not be created."
+        raise ValidationError(message)
+    user = User.objects.get(pk=result.user_id)
+    temporary_password = generate_birthdate_password(player)
+    return CreatedAccountResult(
+        user=user,
+        username=user.username,
+        temporary_password=temporary_password,
+        role=role,
+        role_label=role_label(role),
+        player=player,
+    )
diff --git a/accounts/services/password_service.py b/accounts/services/password_service.py
index 78b2133..38b03ba 100644
--- a/accounts/services/password_service.py
+++ b/accounts/services/password_service.py
@@ -1,4 +1,5 @@
 from datetime import date
+import secrets

 from django.core.exceptions import ValidationError
 from django.db import transaction
@@ -25,6 +26,21 @@ def set_temporary_password(user, player) -> None:
     user.save(update_fields=["password"])


+def generate_random_temporary_password(length: int = 18) -> str:
+    """Return a secure random temporary password for non-player accounts."""
+    if length < 12:
+        raise ValidationError("Temporary password length must be at least 12 characters.")
+    return secrets.token_urlsafe(length)[:length]
+
+
+def set_random_temporary_password(user, length: int = 18) -> str:
+    """Set and return a one-time random temporary password."""
+    password = generate_random_temporary_password(length=length)
+    user.set_password(password)
+    user.save(update_fields=["password"])
+    return password
+
+
 @transaction.atomic
 def mark_password_change_required(user, value=True):
     """Set the account profile password-change requirement."""
diff --git a/accounts/services/provisioning_service.py b/accounts/services/provisioning_service.py
index 2f68fa6..f899f50 100644
--- a/accounts/services/provisioning_service.py
+++ b/accounts/services/provisioning_service.py
@@ -12,7 +12,7 @@ from accounts.services.email_service import find_existing_email_user, normalize_
 from accounts.services.link_service import activate_link, link_user_to_player
 from accounts.services.password_service import mark_password_change_required, set_temporary_password
 from accounts.services.profile_service import get_or_create_account_profile
-from accounts.services.username_service import username_for_player
+from accounts.services.username_service import validate_available_username, username_for_player
 from players.models import Player, PlayerImportBatch


@@ -195,6 +195,7 @@ def provision_player_account(
     email="",
     activate_user=True,
     row_number=None,
+    username="",
 ) -> ProvisioningResult:
     """Create or reuse an imported player login account without exposing passwords."""
     _validate_player(player)
@@ -246,7 +247,7 @@ def provision_player_account(
         )

     try:
-        username = username_for_player(player)
+        username = validate_available_username(username) if username else username_for_player(player)
     except ValidationError as exc:
         return ProvisioningResult(
             player_id=player.id,
@@ -257,7 +258,8 @@ def provision_player_account(

     user = User.objects.create(username=username, email=normalized_email, is_active=activate_user)
     set_temporary_password(user, player)
-    profile = _apply_import_profile_state(user, import_batch, set_player_role=True, created_from_import=True)
+    created_from_import = bool(import_batch)
+    profile = _apply_import_profile_state(user, import_batch, set_player_role=True, created_from_import=created_from_import)
     if not profile.must_change_password:
         mark_password_change_required(user, True)
     link_user_to_player(
@@ -265,7 +267,7 @@ def provision_player_account(
         player,
         relationship=UserPlayerRelationship.SELF,
         is_primary=True,
-        created_from_import=True,
+        created_from_import=created_from_import,
         import_batch=import_batch,
     )
     return ProvisioningResult(
diff --git a/accounts/services/username_service.py b/accounts/services/username_service.py
index c18ce3e..9d1792b 100644
--- a/accounts/services/username_service.py
+++ b/accounts/services/username_service.py
@@ -36,3 +36,15 @@ def username_for_player(player) -> str:
         username = f"{base_username}{suffix}"
         suffix += 1
     return username
+
+
+def validate_available_username(username: str) -> str:
+    """Validate an explicitly supplied username and return the normalized value."""
+    cleaned = str(username or "").strip()
+    if not cleaned:
+        raise ValidationError("Username is required.")
+    if USERNAME_ALLOWED_PATTERN.search(cleaned.casefold()):
+        raise ValidationError("Username may contain only letters, numbers, dots, underscores, and hyphens.")
+    if User.objects.filter(username__iexact=cleaned).exists():
+        raise ValidationError("Username is already in use.")
+    return cleaned
diff --git a/accounts/templates/accounts/account_create.html b/accounts/templates/accounts/account_create.html
new file mode 100644
index 0000000..5bd3909
--- /dev/null
+++ b/accounts/templates/accounts/account_create.html
@@ -0,0 +1,64 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Create Account{% endblock %}
+{% block pdp_subtitle %}Create a login account without creating or linking a player.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    {% if created_account %}
+        <article class="pdp-card">
+            <h2>Account Created</h2>
+            <dl class="pdp-definition-list">
+                <dt>Username</dt>
+                <dd>{{ created_account.username }}</dd>
+                <dt>Role</dt>
+                <dd>{{ created_account.role_label }}</dd>
+                <dt>Temporary password</dt>
+                <dd><strong>{{ created_account.temporary_password }}</strong></dd>
+            </dl>
+            <p>This password is shown once. The user must change it after signing in.</p>
+            <p><a class="button button--ghost" href="{% url 'accounts:user-detail' user_id=created_account.user.id %}">Open account</a></p>
+        </article>
+    {% endif %}
+
+    <article class="pdp-card">
+        <h2>Account Details</h2>
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
+            <button class="button button--primary" type="submit">Create Account</button>
+            <a class="button button--ghost" href="{% url 'accounts:operations-dashboard' %}">Cancel</a>
+        </form>
+    </article>
+</section>
+{% endblock %}
diff --git a/accounts/templates/accounts/operations_dashboard.html b/accounts/templates/accounts/operations_dashboard.html
index 93f7de6..514a518 100644
--- a/accounts/templates/accounts/operations_dashboard.html
+++ b/accounts/templates/accounts/operations_dashboard.html
@@ -5,6 +5,14 @@

 {% block pdp_content %}
 <section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>Actions</h2>
+        <div class="pdp-actions">
+            <a class="button button--primary" href="{% url 'accounts:account-create' %}">Create Account</a>
+            <a class="button button--ghost" href="{% url 'accounts:player-account-create' %}">Create Player Account</a>
+        </div>
+    </article>
+
     <article class="pdp-card">
         <h2>Summary</h2>
         <div class="pdp-grid">
diff --git a/accounts/templates/accounts/player_account_create.html b/accounts/templates/accounts/player_account_create.html
new file mode 100644
index 0000000..cdadec6
--- /dev/null
+++ b/accounts/templates/accounts/player_account_create.html
@@ -0,0 +1,62 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Create Player Account{% endblock %}
+{% block pdp_subtitle %}Create a login account for an existing player record.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    {% if created_account %}
+        <article class="pdp-card">
+            <h2>Player Account Created</h2>
+            <dl class="pdp-definition-list">
+                <dt>Player</dt>
+                <dd>{{ created_account.player.display_name }}</dd>
+                <dt>Username</dt>
+                <dd>{{ created_account.username }}</dd>
+                <dt>Role</dt>
+                <dd>{{ created_account.role_label }}</dd>
+                <dt>Temporary password</dt>
+                <dd><strong>{{ created_account.temporary_password }}</strong></dd>
+            </dl>
+            <p>This password is shown once. The user must change it after signing in.</p>
+            <p><a class="button button--ghost" href="{% url 'accounts:user-detail' user_id=created_account.user.id %}">Open account</a></p>
+        </article>
+    {% endif %}
+
+    <article class="pdp-card">
+        <h2>Player Account Details</h2>
+        <form method="post" class="pdp-form">
+            {% csrf_token %}
+            {{ form.non_field_errors }}
+            <label>
+                Existing player
+                {{ form.player }}
+                {{ form.player.errors }}
+            </label>
+            <label>
+                Username
+                {{ form.username }}
+                {{ form.username.help_text }}
+                {{ form.username.errors }}
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
+            <button class="button button--primary" type="submit">Create Player Account</button>
+            <a class="button button--ghost" href="{% url 'accounts:operations-dashboard' %}">Cancel</a>
+        </form>
+    </article>
+</section>
+{% endblock %}
diff --git a/accounts/tests.py b/accounts/tests.py
index 7640f19..7cf9c73 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -9,6 +9,8 @@ from django.contrib.auth import SESSION_KEY

 from accounts.models import AccountProfile, AccountRole, UserPlayerLink, UserPlayerRelationship
 from accounts.services.account_operations_service import (
+    create_account_only,
+    create_player_account,
     get_account_detail,
     get_account_list,
     get_account_operations_dashboard,
@@ -47,7 +49,12 @@ from accounts.services.link_service import (
     link_user_to_player,
     unlink_user_from_player,
 )
-from accounts.services.password_service import generate_birthdate_password, mark_password_change_required, set_temporary_password
+from accounts.services.password_service import (
+    generate_birthdate_password,
+    generate_random_temporary_password,
+    mark_password_change_required,
+    set_temporary_password,
+)
 from accounts.services.provisioning_service import (
     STATUS_ALREADY_LINKED,
     STATUS_CONFLICT,
@@ -60,7 +67,12 @@ from accounts.services.provisioning_service import (
 )
 from accounts.services.profile_service import get_account_role, get_or_create_account_profile, set_account_role
 from accounts.services.role_service import default_role_for_user, role_for_user, role_label, validate_role
-from accounts.services.username_service import base_username_for_player, normalize_username_part, username_for_player
+from accounts.services.username_service import (
+    base_username_for_player,
+    normalize_username_part,
+    validate_available_username,
+    username_for_player,
+)
 from analytics.services.permissions import can_submit_coach_assessment
 from players.models import Player, PlayerImportBatch

@@ -291,6 +303,118 @@ class AccountOperationsServiceTests(TestCase):
     def test_players_without_self_link_count(self):
         self.assertEqual(count_players_without_self_link(), 1)

+    def test_create_account_only_creates_user_profile_and_temporary_password(self):
+        result = create_account_only(
+            actor=self.staff,
+            username="new.coach",
+            first_name="New",
+            last_name="Coach",
+            email="New.Coach@example.com",
+            role=AccountRole.COACH,
+            is_active=True,
+        )
+
+        user = User.objects.get(username="new.coach")
+        profile = user.account_profile
+        self.assertEqual(result.user, user)
+        self.assertEqual(result.username, "new.coach")
+        self.assertEqual(result.role, AccountRole.COACH)
+        self.assertEqual(result.role_label, "Coach")
+        self.assertTrue(result.temporary_password)
+        self.assertTrue(user.check_password(result.temporary_password))
+        self.assertEqual(user.email, "new.coach@example.com")
+        self.assertEqual(profile.role, AccountRole.COACH)
+        self.assertTrue(profile.must_change_password)
+        self.assertFalse(profile.created_from_import)
+        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
+
+    def test_create_account_only_can_create_inactive_account(self):
+        result = create_account_only(
+            actor=self.staff,
+            username="inactive.coach",
+            role=AccountRole.COACH,
+            is_active=False,
+        )
+
+        self.assertFalse(User.objects.get(pk=result.user.id).is_active)
+        self.assertTrue(result.user.account_profile.must_change_password)
+
+    def test_create_account_only_rejects_duplicate_username_and_email(self):
+        User.objects.create_user(username="duplicate", email="duplicate@example.com")
+
+        with self.assertRaises(ValidationError):
+            create_account_only(actor=self.staff, username="DUPLICATE", role=AccountRole.COACH)
+        with self.assertRaises(ValidationError):
+            create_account_only(
+                actor=self.staff,
+                username="unique",
+                email="Duplicate@Example.com",
+                role=AccountRole.COACH,
+            )
+
+    def test_create_account_only_admin_requires_superuser(self):
+        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
+
+        with self.assertRaises(ValidationError):
+            create_account_only(actor=self.staff, username="admin.account", role=AccountRole.ADMIN)
+
+        result = create_account_only(actor=superuser, username="admin.account", role=AccountRole.ADMIN)
+
+        self.assertEqual(result.role, AccountRole.ADMIN)
+        self.assertFalse(result.user.is_staff)
+        self.assertFalse(result.user.is_superuser)
+
+    def test_create_player_account_uses_existing_player_and_provisioning_logic(self):
+        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
+
+        result = create_player_account(actor=self.staff, player=player, email="Blake@example.com")
+
+        user = User.objects.get(username="blake.player")
+        profile = user.account_profile
+        link = UserPlayerLink.objects.get(user=user, player=player)
+        self.assertEqual(result.user, user)
+        self.assertEqual(result.player, player)
+        self.assertEqual(result.temporary_password, "20130602")
+        self.assertTrue(user.check_password(result.temporary_password))
+        self.assertEqual(user.email, "blake@example.com")
+        self.assertEqual(profile.role, AccountRole.PLAYER)
+        self.assertTrue(profile.must_change_password)
+        self.assertTrue(user.is_active)
+        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
+        self.assertTrue(link.is_primary)
+        self.assertFalse(profile.created_from_import)
+
+    def test_create_player_account_accepts_optional_username_and_inactive_flag(self):
+        player = Player.objects.create(first_name="Casey", last_name="Player", birthdate="2014-07-03")
+
+        result = create_player_account(actor=self.staff, player=player, username="custom.player", is_active=False)
+
+        self.assertEqual(result.username, "custom.player")
+        self.assertFalse(User.objects.get(username="custom.player").is_active)
+
+    def test_create_player_account_rejects_duplicate_email_username_and_player_account(self):
+        player = Player.objects.create(first_name="Dana", last_name="Player", birthdate="2015-08-04")
+        User.objects.create_user(username="taken", email="taken@example.com")
+
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=player, username="taken")
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=player, email="taken@example.com")
+
+        create_player_account(actor=self.staff, player=player, username="dana.player")
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=player, username="dana.player2")
+
+        self.assertEqual(UserPlayerLink.objects.filter(player=player, relationship=UserPlayerRelationship.SELF).count(), 1)
+
+    def test_create_player_account_requires_existing_player_birthdate_and_player_role(self):
+        player = Player.objects.create(first_name="No", last_name="Birthdate")
+
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=player)
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=self.player, role=AccountRole.COACH)
+

 class UserPlayerLinkModelTests(TestCase):
     def setUp(self):
@@ -612,6 +736,15 @@ class AccountUsernameServiceTests(TestCase):

         self.assertEqual(username_for_player(player), "alex.player3")

+    def test_validate_available_username_rejects_duplicates_and_unsafe_values(self):
+        User.objects.create_user(username="coach.one")
+
+        self.assertEqual(validate_available_username("new.user"), "new.user")
+        with self.assertRaises(ValidationError):
+            validate_available_username("coach.ONE")
+        with self.assertRaises(ValidationError):
+            validate_available_username("bad username")
+

 class AccountEmailServiceTests(TestCase):
     def test_email_normalization_and_comparison(self):
@@ -648,6 +781,12 @@ class AccountPasswordServiceTests(TestCase):
         self.assertTrue(user.check_password("20120501"))
         self.assertTrue(user.account_profile.must_change_password)

+    def test_generate_random_temporary_password_is_secure_length(self):
+        password = generate_random_temporary_password()
+
+        self.assertGreaterEqual(len(password), 12)
+        self.assertNotEqual(password, generate_random_temporary_password())
+

 class AccountProvisioningServiceTests(TestCase):
     def setUp(self):
@@ -1053,6 +1192,8 @@ class AccountOperationsViewTests(TestCase):
         self.assertContains(response, "Password change required")
         self.assertContains(response, "Users without player links")
         self.assertContains(response, "Players without self-linked accounts")
+        self.assertContains(response, reverse("accounts:account-create"))
+        self.assertContains(response, reverse("accounts:player-account-create"))

     def test_user_list_requires_staff(self):
         self.client.force_login(self.regular)
@@ -1106,6 +1247,99 @@ class AccountOperationsViewTests(TestCase):
         self.assertEqual(response.status_code, 200)
         self.assertNotContains(response, reverse("accounts:operations-dashboard"))

+    def test_account_create_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:account-create"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_create_account_only_and_see_one_time_password(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:account-create"),
+            {
+                "username": "new.evaluator",
+                "first_name": "New",
+                "last_name": "Evaluator",
+                "email": "new@example.com",
+                "role": AccountRole.GUEST_EVALUATOR,
+                "is_active": "on",
+            },
+        )
+
+        user = User.objects.get(username="new.evaluator")
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account Created")
+        self.assertContains(response, "Temporary password")
+        self.assertTrue(user.account_profile.must_change_password)
+        self.assertEqual(user.account_profile.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
+
+    def test_staff_cannot_create_admin_account(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:account-create"),
+            {
+                "username": "admin.try",
+                "role": AccountRole.ADMIN,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Only superusers can create admin accounts")
+        self.assertFalse(User.objects.filter(username="admin.try").exists())
+
+    def test_player_account_create_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:player-account-create"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_create_player_account_for_existing_player(self):
+        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:player-account-create"),
+            {
+                "player": player.id,
+                "email": "blake@example.com",
+                "role": AccountRole.PLAYER,
+                "is_active": "on",
+            },
+        )
+
+        user = User.objects.get(username="blake.player")
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Player Account Created")
+        self.assertContains(response, "20130602")
+        self.assertTrue(user.check_password("20130602"))
+        self.assertTrue(user.account_profile.must_change_password)
+        self.assertEqual(UserPlayerLink.objects.get(user=user).player, player)
+
+    def test_player_account_create_rejects_duplicate_player_account(self):
+        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
+        create_player_account(actor=self.staff, player=player)
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:player-account-create"),
+            {
+                "player": player.id,
+                "role": AccountRole.PLAYER,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Player already has a linked user account")
+        self.assertEqual(UserPlayerLink.objects.filter(player=player, relationship=UserPlayerRelationship.SELF).count(), 1)
+

 class AccountPasswordMiddlewareTests(TestCase):
     def setUp(self):
diff --git a/accounts/urls.py b/accounts/urls.py
index 535afe5..809a033 100644
--- a/accounts/urls.py
+++ b/accounts/urls.py
@@ -1,6 +1,7 @@
 from django.urls import path

 from accounts.views import (
+    AccountOnlyCreateView,
     AccountLoginView,
     AccountLogoutView,
     AccountOperationsDashboardView,
@@ -8,6 +9,7 @@ from accounts.views import (
     AccountProfileView,
     AccountUserDetailView,
     AccountUserListView,
+    PlayerAccountCreateView,
 )


@@ -15,6 +17,8 @@ app_name = "accounts"

 urlpatterns = [
     path("", AccountOperationsDashboardView.as_view(), name="operations-dashboard"),
+    path("create/", AccountOnlyCreateView.as_view(), name="account-create"),
+    path("create/player/", PlayerAccountCreateView.as_view(), name="player-account-create"),
     path("login/", AccountLoginView.as_view(), name="login"),
     path("logout/", AccountLogoutView.as_view(), name="logout"),
     path("password/", AccountPasswordChangeView.as_view(), name="password-change"),
diff --git a/accounts/views.py b/accounts/views.py
index b74e5e9..c8fa005 100644
--- a/accounts/views.py
+++ b/accounts/views.py
@@ -2,11 +2,14 @@ from django.contrib import messages
 from django.contrib.auth import update_session_auth_hash
 from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
 from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
-from django.core.exceptions import PermissionDenied
+from django.core.exceptions import PermissionDenied, ValidationError
 from django.shortcuts import redirect
-from django.views.generic import TemplateView
+from django.views.generic import FormView, TemplateView

+from accounts.forms import AccountOnlyCreateForm, PlayerAccountCreateForm
 from accounts.services.account_operations_service import (
+    create_account_only,
+    create_player_account,
     get_account_detail,
     get_account_list,
     get_account_operations_dashboard,
@@ -134,3 +137,46 @@ class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
         context["target_user"] = self.account_detail.user
         context["linked_players"] = self.account_detail.linked_players
         return context
+
+
+class AccountOnlyCreateView(AccountOperationsStaffRequiredMixin, FormView):
+    template_name = "accounts/account_create.html"
+    form_class = AccountOnlyCreateForm
+
+    def form_valid(self, form):
+        try:
+            result = create_account_only(
+                actor=self.request.user,
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
+        messages.success(self.request, "Account created. Copy the temporary password now; it will not be shown again.")
+        return self.render_to_response(self.get_context_data(form=form, created_account=result))
+
+
+class PlayerAccountCreateView(AccountOperationsStaffRequiredMixin, FormView):
+    template_name = "accounts/player_account_create.html"
+    form_class = PlayerAccountCreateForm
+
+    def form_valid(self, form):
+        try:
+            result = create_player_account(
+                actor=self.request.user,
+                player=form.cleaned_data["player"],
+                username=form.cleaned_data.get("username", ""),
+                email=form.cleaned_data.get("email", ""),
+                role=form.cleaned_data["role"],
+                is_active=form.cleaned_data.get("is_active", False),
+            )
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Player account created. Copy the temporary password now; it will not be shown again.")
+        return self.render_to_response(self.get_context_data(form=form, created_account=result))
diff --git a/project_flat_file.txt b/project_flat_file.txt
index ffff794..c2adf07 100644
--- a/project_flat_file.txt
+++ b/project_flat_file.txt
@@ -1,6 +1,6 @@
 # Project Flat File Snapshot
 # Root: /Users/eugenelin/dev/vmba0
-# File count: 342
+# File count: 345
 # Excluded directories: .git, .venv, __pycache__, node_modules, dist, build
 # Excluded unrelated untracked scratch files.
 # Text files are included as UTF-8/decoded text. Binary files are described, not embedded.
@@ -493,6 +493,46 @@ class AccountsConfig(AppConfig):
     default_auto_field = "django.db.models.BigAutoField"
     name = "accounts"

+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/accounts/forms.py
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+from django import forms
+
+from accounts.models import AccountRole
+from players.models import Player
+
+
+ACCOUNT_ONLY_ROLE_CHOICES = (
+    (AccountRole.STAFF, "Staff"),
+    (AccountRole.COACH, "Coach"),
+    (AccountRole.PARENT, "Parent"),
+    (AccountRole.GUEST_EVALUATOR, "Guest Evaluator"),
+    (AccountRole.ADMIN, "Admin"),
+)
+
+
+class AccountOnlyCreateForm(forms.Form):
+    username = forms.CharField(max_length=150)
+    first_name = forms.CharField(max_length=150, required=False)
+    last_name = forms.CharField(max_length=150, required=False)
+    email = forms.EmailField(required=False)
+    role = forms.ChoiceField(choices=ACCOUNT_ONLY_ROLE_CHOICES)
+    is_active = forms.BooleanField(required=False, initial=True, label="Activate account immediately")
+
+
+class PlayerAccountCreateForm(forms.Form):
+    player = forms.ModelChoiceField(queryset=Player.objects.none())
+    username = forms.CharField(max_length=150, required=False, help_text="Leave blank to use firstname.lastname.")
+    email = forms.EmailField(required=False)
+    role = forms.ChoiceField(choices=((AccountRole.PLAYER, "Player"),), initial=AccountRole.PLAYER)
+    is_active = forms.BooleanField(required=False, initial=True, label="Activate account immediately")
+
+    def __init__(self, *args, **kwargs):
+        super().__init__(*args, **kwargs)
+        self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/accounts/middleware.py
 ====================================================================================================
@@ -767,13 +807,25 @@ from __future__ import annotations
 from dataclasses import dataclass

 from django.contrib.auth import get_user_model
+from django.core.exceptions import ValidationError
+from django.db import transaction
 from django.urls import reverse
 from django.utils import timezone

 from accounts.models import AccountRole, UserPlayerLink
 from accounts.services import account_query_service
 from accounts.services.account_query_service import AccountListFilters
+from accounts.services.email_service import find_existing_email_user, normalize_email
+from accounts.services.password_service import (
+    generate_birthdate_password,
+    mark_password_change_required,
+    set_random_temporary_password,
+)
+from accounts.services.profile_service import get_or_create_account_profile, set_account_role
+from accounts.services.provisioning_service import STATUS_CREATED, provision_player_account
 from accounts.services.role_service import role_label
+from accounts.services.username_service import validate_available_username
+from players.models import Player


 User = get_user_model()
@@ -832,6 +884,28 @@ class AccountDetailContext:
     linked_players: list[LinkedPlayerRow]


+@dataclass(frozen=True)
+class CreatedAccountResult:
+    user: User
+    username: str
+    temporary_password: str
+    role: str
+    role_label: str
+    player: Player | None = None
+
+
+def _validate_actor_can_create_role(actor, role: str) -> None:
+    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
+        raise ValidationError("Only superusers can create admin accounts.")
+
+
+def _validate_email_available(email: str) -> str:
+    normalized = normalize_email(email)
+    if normalized and find_existing_email_user(normalized):
+        raise ValidationError("Email is already in use.")
+    return normalized
+
+
 def _role_for_user(user: User) -> str:
     profile = getattr(user, "account_profile", None)
     if profile:
@@ -956,6 +1030,83 @@ def get_account_detail(user_id: int) -> AccountDetailContext:
         linked_players=[_linked_player_row(link) for link in links],
     )

+
+@transaction.atomic
+def create_account_only(
+    *,
+    actor,
+    username: str,
+    first_name: str = "",
+    last_name: str = "",
+    email: str = "",
+    role: str = AccountRole.GUEST_EVALUATOR,
+    is_active: bool = True,
+) -> CreatedAccountResult:
+    """Create a login account without creating or linking a player."""
+    _validate_actor_can_create_role(actor, role)
+    username = validate_available_username(username)
+    normalized_email = _validate_email_available(email)
+    user = User.objects.create(
+        username=username,
+        first_name=str(first_name or "").strip(),
+        last_name=str(last_name or "").strip(),
+        email=normalized_email,
+        is_active=bool(is_active),
+    )
+    temporary_password = set_random_temporary_password(user)
+    profile = get_or_create_account_profile(user)
+    if profile.created_from_import or profile.import_batch_id:
+        raise ValidationError("Manual accounts cannot use import provenance.")
+    set_account_role(user, role, actor=actor)
+    mark_password_change_required(user, True)
+    user.refresh_from_db()
+    return CreatedAccountResult(
+        user=user,
+        username=user.username,
+        temporary_password=temporary_password,
+        role=role,
+        role_label=role_label(role),
+    )
+
+
+@transaction.atomic
+def create_player_account(
+    *,
+    actor,
+    player,
+    username: str = "",
+    email: str = "",
+    role: str = AccountRole.PLAYER,
+    is_active: bool = True,
+) -> CreatedAccountResult:
+    """Create a login account for an existing canonical player."""
+    if not isinstance(player, Player):
+        raise ValidationError("A valid existing player is required.")
+    _validate_actor_can_create_role(actor, role)
+    if role != AccountRole.PLAYER:
+        raise ValidationError("Player account creation must use the player role in Phase B.")
+    normalized_email = _validate_email_available(email)
+    result = provision_player_account(
+        player,
+        actor=actor,
+        email=normalized_email,
+        activate_user=bool(is_active),
+        username=username,
+    )
+    if result.status != STATUS_CREATED or not result.user_id:
+        message = "; ".join(result.messages) if result.messages else "Player account could not be created."
+        raise ValidationError(message)
+    user = User.objects.get(pk=result.user_id)
+    temporary_password = generate_birthdate_password(player)
+    return CreatedAccountResult(
+        user=user,
+        username=user.username,
+        temporary_password=temporary_password,
+        role=role,
+        role_label=role_label(role),
+        player=player,
+    )
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/accounts/services/account_query_service.py
 ====================================================================================================
@@ -1417,6 +1568,7 @@ FILE: /Users/eugenelin/dev/vmba0/accounts/services/password_service.py
 CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 from datetime import date
+import secrets

 from django.core.exceptions import ValidationError
 from django.db import transaction
@@ -1443,6 +1595,21 @@ def set_temporary_password(user, player) -> None:
     user.save(update_fields=["password"])


+def generate_random_temporary_password(length: int = 18) -> str:
+    """Return a secure random temporary password for non-player accounts."""
+    if length < 12:
+        raise ValidationError("Temporary password length must be at least 12 characters.")
+    return secrets.token_urlsafe(length)[:length]
+
+
+def set_random_temporary_password(user, length: int = 18) -> str:
+    """Set and return a one-time random temporary password."""
+    password = generate_random_temporary_password(length=length)
+    user.set_password(password)
+    user.save(update_fields=["password"])
+    return password
+
+
 @transaction.atomic
 def mark_password_change_required(user, value=True):
     """Set the account profile password-change requirement."""
@@ -1567,7 +1734,7 @@ from accounts.services.email_service import find_existing_email_user, normalize_
 from accounts.services.link_service import activate_link, link_user_to_player
 from accounts.services.password_service import mark_password_change_required, set_temporary_password
 from accounts.services.profile_service import get_or_create_account_profile
-from accounts.services.username_service import username_for_player
+from accounts.services.username_service import validate_available_username, username_for_player
 from players.models import Player, PlayerImportBatch


@@ -1750,6 +1917,7 @@ def provision_player_account(
     email="",
     activate_user=True,
     row_number=None,
+    username="",
 ) -> ProvisioningResult:
     """Create or reuse an imported player login account without exposing passwords."""
     _validate_player(player)
@@ -1801,7 +1969,7 @@ def provision_player_account(
         )

     try:
-        username = username_for_player(player)
+        username = validate_available_username(username) if username else username_for_player(player)
     except ValidationError as exc:
         return ProvisioningResult(
             player_id=player.id,
@@ -1812,7 +1980,8 @@ def provision_player_account(

     user = User.objects.create(username=username, email=normalized_email, is_active=activate_user)
     set_temporary_password(user, player)
-    profile = _apply_import_profile_state(user, import_batch, set_player_role=True, created_from_import=True)
+    created_from_import = bool(import_batch)
+    profile = _apply_import_profile_state(user, import_batch, set_player_role=True, created_from_import=created_from_import)
     if not profile.must_change_password:
         mark_password_change_required(user, True)
     link_user_to_player(
@@ -1820,7 +1989,7 @@ def provision_player_account(
         player,
         relationship=UserPlayerRelationship.SELF,
         is_primary=True,
-        created_from_import=True,
+        created_from_import=created_from_import,
         import_batch=import_batch,
     )
     return ProvisioningResult(
@@ -1952,6 +2121,88 @@ def username_for_player(player) -> str:
         suffix += 1
     return username

+
+def validate_available_username(username: str) -> str:
+    """Validate an explicitly supplied username and return the normalized value."""
+    cleaned = str(username or "").strip()
+    if not cleaned:
+        raise ValidationError("Username is required.")
+    if USERNAME_ALLOWED_PATTERN.search(cleaned.casefold()):
+        raise ValidationError("Username may contain only letters, numbers, dots, underscores, and hyphens.")
+    if User.objects.filter(username__iexact=cleaned).exists():
+        raise ValidationError("Username is already in use.")
+    return cleaned
+
+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/account_create.html
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Create Account{% endblock %}
+{% block pdp_subtitle %}Create a login account without creating or linking a player.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    {% if created_account %}
+        <article class="pdp-card">
+            <h2>Account Created</h2>
+            <dl class="pdp-definition-list">
+                <dt>Username</dt>
+                <dd>{{ created_account.username }}</dd>
+                <dt>Role</dt>
+                <dd>{{ created_account.role_label }}</dd>
+                <dt>Temporary password</dt>
+                <dd><strong>{{ created_account.temporary_password }}</strong></dd>
+            </dl>
+            <p>This password is shown once. The user must change it after signing in.</p>
+            <p><a class="button button--ghost" href="{% url 'accounts:user-detail' user_id=created_account.user.id %}">Open account</a></p>
+        </article>
+    {% endif %}
+
+    <article class="pdp-card">
+        <h2>Account Details</h2>
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
+            <button class="button button--primary" type="submit">Create Account</button>
+            <a class="button button--ghost" href="{% url 'accounts:operations-dashboard' %}">Cancel</a>
+        </form>
+    </article>
+</section>
+{% endblock %}
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/login.html
 ====================================================================================================
@@ -1987,6 +2238,14 @@ CONTENT-TYPE: text/plain; charset=utf-8

 {% block pdp_content %}
 <section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>Actions</h2>
+        <div class="pdp-actions">
+            <a class="button button--primary" href="{% url 'accounts:account-create' %}">Create Account</a>
+            <a class="button button--ghost" href="{% url 'accounts:player-account-create' %}">Create Player Account</a>
+        </div>
+    </article>
+
     <article class="pdp-card">
         <h2>Summary</h2>
         <div class="pdp-grid">
@@ -2074,6 +2333,74 @@ CONTENT-TYPE: text/plain; charset=utf-8
 </section>
 {% endblock %}

+====================================================================================================
+FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/player_account_create.html
+====================================================================================================
+CONTENT-TYPE: text/plain; charset=utf-8
+----------------------------------------------------------------------------------------------------
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Create Player Account{% endblock %}
+{% block pdp_subtitle %}Create a login account for an existing player record.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    {% if created_account %}
+        <article class="pdp-card">
+            <h2>Player Account Created</h2>
+            <dl class="pdp-definition-list">
+                <dt>Player</dt>
+                <dd>{{ created_account.player.display_name }}</dd>
+                <dt>Username</dt>
+                <dd>{{ created_account.username }}</dd>
+                <dt>Role</dt>
+                <dd>{{ created_account.role_label }}</dd>
+                <dt>Temporary password</dt>
+                <dd><strong>{{ created_account.temporary_password }}</strong></dd>
+            </dl>
+            <p>This password is shown once. The user must change it after signing in.</p>
+            <p><a class="button button--ghost" href="{% url 'accounts:user-detail' user_id=created_account.user.id %}">Open account</a></p>
+        </article>
+    {% endif %}
+
+    <article class="pdp-card">
+        <h2>Player Account Details</h2>
+        <form method="post" class="pdp-form">
+            {% csrf_token %}
+            {{ form.non_field_errors }}
+            <label>
+                Existing player
+                {{ form.player }}
+                {{ form.player.errors }}
+            </label>
+            <label>
+                Username
+                {{ form.username }}
+                {{ form.username.help_text }}
+                {{ form.username.errors }}
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
+            <button class="button button--primary" type="submit">Create Player Account</button>
+            <a class="button button--ghost" href="{% url 'accounts:operations-dashboard' %}">Cancel</a>
+        </form>
+    </article>
+</section>
+{% endblock %}
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/accounts/templates/accounts/profile.html
 ====================================================================================================
@@ -2360,6 +2687,8 @@ from django.contrib.auth import SESSION_KEY

 from accounts.models import AccountProfile, AccountRole, UserPlayerLink, UserPlayerRelationship
 from accounts.services.account_operations_service import (
+    create_account_only,
+    create_player_account,
     get_account_detail,
     get_account_list,
     get_account_operations_dashboard,
@@ -2398,7 +2727,12 @@ from accounts.services.link_service import (
     link_user_to_player,
     unlink_user_from_player,
 )
-from accounts.services.password_service import generate_birthdate_password, mark_password_change_required, set_temporary_password
+from accounts.services.password_service import (
+    generate_birthdate_password,
+    generate_random_temporary_password,
+    mark_password_change_required,
+    set_temporary_password,
+)
 from accounts.services.provisioning_service import (
     STATUS_ALREADY_LINKED,
     STATUS_CONFLICT,
@@ -2411,7 +2745,12 @@ from accounts.services.provisioning_service import (
 )
 from accounts.services.profile_service import get_account_role, get_or_create_account_profile, set_account_role
 from accounts.services.role_service import default_role_for_user, role_for_user, role_label, validate_role
-from accounts.services.username_service import base_username_for_player, normalize_username_part, username_for_player
+from accounts.services.username_service import (
+    base_username_for_player,
+    normalize_username_part,
+    validate_available_username,
+    username_for_player,
+)
 from analytics.services.permissions import can_submit_coach_assessment
 from players.models import Player, PlayerImportBatch

@@ -2642,6 +2981,118 @@ class AccountOperationsServiceTests(TestCase):
     def test_players_without_self_link_count(self):
         self.assertEqual(count_players_without_self_link(), 1)

+    def test_create_account_only_creates_user_profile_and_temporary_password(self):
+        result = create_account_only(
+            actor=self.staff,
+            username="new.coach",
+            first_name="New",
+            last_name="Coach",
+            email="New.Coach@example.com",
+            role=AccountRole.COACH,
+            is_active=True,
+        )
+
+        user = User.objects.get(username="new.coach")
+        profile = user.account_profile
+        self.assertEqual(result.user, user)
+        self.assertEqual(result.username, "new.coach")
+        self.assertEqual(result.role, AccountRole.COACH)
+        self.assertEqual(result.role_label, "Coach")
+        self.assertTrue(result.temporary_password)
+        self.assertTrue(user.check_password(result.temporary_password))
+        self.assertEqual(user.email, "new.coach@example.com")
+        self.assertEqual(profile.role, AccountRole.COACH)
+        self.assertTrue(profile.must_change_password)
+        self.assertFalse(profile.created_from_import)
+        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
+
+    def test_create_account_only_can_create_inactive_account(self):
+        result = create_account_only(
+            actor=self.staff,
+            username="inactive.coach",
+            role=AccountRole.COACH,
+            is_active=False,
+        )
+
+        self.assertFalse(User.objects.get(pk=result.user.id).is_active)
+        self.assertTrue(result.user.account_profile.must_change_password)
+
+    def test_create_account_only_rejects_duplicate_username_and_email(self):
+        User.objects.create_user(username="duplicate", email="duplicate@example.com")
+
+        with self.assertRaises(ValidationError):
+            create_account_only(actor=self.staff, username="DUPLICATE", role=AccountRole.COACH)
+        with self.assertRaises(ValidationError):
+            create_account_only(
+                actor=self.staff,
+                username="unique",
+                email="Duplicate@Example.com",
+                role=AccountRole.COACH,
+            )
+
+    def test_create_account_only_admin_requires_superuser(self):
+        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
+
+        with self.assertRaises(ValidationError):
+            create_account_only(actor=self.staff, username="admin.account", role=AccountRole.ADMIN)
+
+        result = create_account_only(actor=superuser, username="admin.account", role=AccountRole.ADMIN)
+
+        self.assertEqual(result.role, AccountRole.ADMIN)
+        self.assertFalse(result.user.is_staff)
+        self.assertFalse(result.user.is_superuser)
+
+    def test_create_player_account_uses_existing_player_and_provisioning_logic(self):
+        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
+
+        result = create_player_account(actor=self.staff, player=player, email="Blake@example.com")
+
+        user = User.objects.get(username="blake.player")
+        profile = user.account_profile
+        link = UserPlayerLink.objects.get(user=user, player=player)
+        self.assertEqual(result.user, user)
+        self.assertEqual(result.player, player)
+        self.assertEqual(result.temporary_password, "20130602")
+        self.assertTrue(user.check_password(result.temporary_password))
+        self.assertEqual(user.email, "blake@example.com")
+        self.assertEqual(profile.role, AccountRole.PLAYER)
+        self.assertTrue(profile.must_change_password)
+        self.assertTrue(user.is_active)
+        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
+        self.assertTrue(link.is_primary)
+        self.assertFalse(profile.created_from_import)
+
+    def test_create_player_account_accepts_optional_username_and_inactive_flag(self):
+        player = Player.objects.create(first_name="Casey", last_name="Player", birthdate="2014-07-03")
+
+        result = create_player_account(actor=self.staff, player=player, username="custom.player", is_active=False)
+
+        self.assertEqual(result.username, "custom.player")
+        self.assertFalse(User.objects.get(username="custom.player").is_active)
+
+    def test_create_player_account_rejects_duplicate_email_username_and_player_account(self):
+        player = Player.objects.create(first_name="Dana", last_name="Player", birthdate="2015-08-04")
+        User.objects.create_user(username="taken", email="taken@example.com")
+
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=player, username="taken")
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=player, email="taken@example.com")
+
+        create_player_account(actor=self.staff, player=player, username="dana.player")
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=player, username="dana.player2")
+
+        self.assertEqual(UserPlayerLink.objects.filter(player=player, relationship=UserPlayerRelationship.SELF).count(), 1)
+
+    def test_create_player_account_requires_existing_player_birthdate_and_player_role(self):
+        player = Player.objects.create(first_name="No", last_name="Birthdate")
+
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=player)
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=self.player, role=AccountRole.COACH)
+

 class UserPlayerLinkModelTests(TestCase):
     def setUp(self):
@@ -2963,6 +3414,15 @@ class AccountUsernameServiceTests(TestCase):

         self.assertEqual(username_for_player(player), "alex.player3")

+    def test_validate_available_username_rejects_duplicates_and_unsafe_values(self):
+        User.objects.create_user(username="coach.one")
+
+        self.assertEqual(validate_available_username("new.user"), "new.user")
+        with self.assertRaises(ValidationError):
+            validate_available_username("coach.ONE")
+        with self.assertRaises(ValidationError):
+            validate_available_username("bad username")
+

 class AccountEmailServiceTests(TestCase):
     def test_email_normalization_and_comparison(self):
@@ -2999,6 +3459,12 @@ class AccountPasswordServiceTests(TestCase):
         self.assertTrue(user.check_password("20120501"))
         self.assertTrue(user.account_profile.must_change_password)

+    def test_generate_random_temporary_password_is_secure_length(self):
+        password = generate_random_temporary_password()
+
+        self.assertGreaterEqual(len(password), 12)
+        self.assertNotEqual(password, generate_random_temporary_password())
+

 class AccountProvisioningServiceTests(TestCase):
     def setUp(self):
@@ -3404,6 +3870,8 @@ class AccountOperationsViewTests(TestCase):
         self.assertContains(response, "Password change required")
         self.assertContains(response, "Users without player links")
         self.assertContains(response, "Players without self-linked accounts")
+        self.assertContains(response, reverse("accounts:account-create"))
+        self.assertContains(response, reverse("accounts:player-account-create"))

     def test_user_list_requires_staff(self):
         self.client.force_login(self.regular)
@@ -3457,6 +3925,99 @@ class AccountOperationsViewTests(TestCase):
         self.assertEqual(response.status_code, 200)
         self.assertNotContains(response, reverse("accounts:operations-dashboard"))

+    def test_account_create_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:account-create"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_create_account_only_and_see_one_time_password(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:account-create"),
+            {
+                "username": "new.evaluator",
+                "first_name": "New",
+                "last_name": "Evaluator",
+                "email": "new@example.com",
+                "role": AccountRole.GUEST_EVALUATOR,
+                "is_active": "on",
+            },
+        )
+
+        user = User.objects.get(username="new.evaluator")
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account Created")
+        self.assertContains(response, "Temporary password")
+        self.assertTrue(user.account_profile.must_change_password)
+        self.assertEqual(user.account_profile.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
+
+    def test_staff_cannot_create_admin_account(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:account-create"),
+            {
+                "username": "admin.try",
+                "role": AccountRole.ADMIN,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Only superusers can create admin accounts")
+        self.assertFalse(User.objects.filter(username="admin.try").exists())
+
+    def test_player_account_create_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:player-account-create"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_create_player_account_for_existing_player(self):
+        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:player-account-create"),
+            {
+                "player": player.id,
+                "email": "blake@example.com",
+                "role": AccountRole.PLAYER,
+                "is_active": "on",
+            },
+        )
+
+        user = User.objects.get(username="blake.player")
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Player Account Created")
+        self.assertContains(response, "20130602")
+        self.assertTrue(user.check_password("20130602"))
+        self.assertTrue(user.account_profile.must_change_password)
+        self.assertEqual(UserPlayerLink.objects.get(user=user).player, player)
+
+    def test_player_account_create_rejects_duplicate_player_account(self):
+        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
+        create_player_account(actor=self.staff, player=player)
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:player-account-create"),
+            {
+                "player": player.id,
+                "role": AccountRole.PLAYER,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Player already has a linked user account")
+        self.assertEqual(UserPlayerLink.objects.filter(player=player, relationship=UserPlayerRelationship.SELF).count(), 1)
+

 class AccountPasswordMiddlewareTests(TestCase):
     def setUp(self):
@@ -3575,6 +4136,7 @@ CONTENT-TYPE: text/plain; charset=utf-8
 from django.urls import path

 from accounts.views import (
+    AccountOnlyCreateView,
     AccountLoginView,
     AccountLogoutView,
     AccountOperationsDashboardView,
@@ -3582,6 +4144,7 @@ from accounts.views import (
     AccountProfileView,
     AccountUserDetailView,
     AccountUserListView,
+    PlayerAccountCreateView,
 )


@@ -3589,6 +4152,8 @@ app_name = "accounts"

 urlpatterns = [
     path("", AccountOperationsDashboardView.as_view(), name="operations-dashboard"),
+    path("create/", AccountOnlyCreateView.as_view(), name="account-create"),
+    path("create/player/", PlayerAccountCreateView.as_view(), name="player-account-create"),
     path("login/", AccountLoginView.as_view(), name="login"),
     path("logout/", AccountLogoutView.as_view(), name="logout"),
     path("password/", AccountPasswordChangeView.as_view(), name="password-change"),
@@ -3606,11 +4171,14 @@ from django.contrib import messages
 from django.contrib.auth import update_session_auth_hash
 from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
 from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
-from django.core.exceptions import PermissionDenied
+from django.core.exceptions import PermissionDenied, ValidationError
 from django.shortcuts import redirect
-from django.views.generic import TemplateView
+from django.views.generic import FormView, TemplateView

+from accounts.forms import AccountOnlyCreateForm, PlayerAccountCreateForm
 from accounts.services.account_operations_service import (
+    create_account_only,
+    create_player_account,
     get_account_detail,
     get_account_list,
     get_account_operations_dashboard,
@@ -3739,6 +4307,49 @@ class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
         context["linked_players"] = self.account_detail.linked_players
         return context

+
+class AccountOnlyCreateView(AccountOperationsStaffRequiredMixin, FormView):
+    template_name = "accounts/account_create.html"
+    form_class = AccountOnlyCreateForm
+
+    def form_valid(self, form):
+        try:
+            result = create_account_only(
+                actor=self.request.user,
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
+        messages.success(self.request, "Account created. Copy the temporary password now; it will not be shown again.")
+        return self.render_to_response(self.get_context_data(form=form, created_account=result))
+
+
+class PlayerAccountCreateView(AccountOperationsStaffRequiredMixin, FormView):
+    template_name = "accounts/player_account_create.html"
+    form_class = PlayerAccountCreateForm
+
+    def form_valid(self, form):
+        try:
+            result = create_player_account(
+                actor=self.request.user,
+                player=form.cleaned_data["player"],
+                username=form.cleaned_data.get("username", ""),
+                email=form.cleaned_data.get("email", ""),
+                role=form.cleaned_data["role"],
+                is_active=form.cleaned_data.get("is_active", False),
+            )
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Player account created. Copy the temporary password now; it will not be shown again.")
+        return self.render_to_response(self.get_context_data(form=form, created_account=result))
+
 ====================================================================================================
 FILE: /Users/eugenelin/dev/vmba0/analytics/__init__.py
 ====================================================================================================
```

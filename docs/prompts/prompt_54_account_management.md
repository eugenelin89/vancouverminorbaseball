# Prompt 54 - Account Management

## User Prompt

```text
Implement Evaluation Access V1 Phase 1 only: Coach Import.

Do NOT implement Phase 2, 3, 4, 5, or 6.

Do NOT change Analytics evaluation permissions yet.

Goal:
Staff can import coach accounts from CSV.

Read:
- docs/ARCHITECTURE.md
- docs/USER_MANUAL.md
- docs/evaluations/implementation/engineering/evaluation_access_v1.md
- docs/account_management/V1_SUMMARY.md
- AGENTS.md

Review:
- accounts/
- players/
- analytics/

Scope:
Implement coach import in `accounts`.

Coach import should:
- create or reuse Django `User`
- create or reuse `AccountProfile`
- set `AccountProfile.role = coach`
- default imported coach accounts to active
- set `must_change_password=True`
- use secure random temporary passwords
- display temporary passwords only once in the immediate import result
- never store plaintext passwords
- never create `players.Player`
- never create `UserPlayerLink` rows in Phase 1
- never grant Django `is_staff` or `is_superuser`

CSV:
Required:
- first_name
- last_name
- email

Optional:
- username
- team
- division
- is_active
- notes
- source_id

Implementation:
Create:
- `accounts/services/coach_import_service.py`

Likely add:
- forms for upload/preview/confirm
- staff-only routes:
  - `/accounts/imports/coaches/`
  - `/accounts/imports/coaches/new/`
  - `/accounts/imports/coaches/preview/`
  - `/accounts/imports/coaches/confirm/`
- templates for coach import upload/preview/result

No persistent coach import batch model unless absolutely necessary.

If a model/migration seems necessary, stop and report why instead of adding it.

Service rules:
- username rules belong in `username_service`
- email normalization belongs in `email_service`
- password generation belongs in `password_service`
- profile role updates belong in `profile_service`
- coach import orchestration belongs in `coach_import_service`
- views stay thin

Duplicate handling:
- duplicate email with existing coach: reuse existing account safely
- duplicate email with non-coach: conflict
- explicit duplicate username: conflict
- generated username collision: resolve with suffix
- invalid rows: row error
- continue processing valid rows where safe

Import result should report:
- rows processed
- users created
- existing coaches reused
- conflicts
- errors
- skipped rows
- active accounts
- inactive accounts
- password-change-required count

Security:
- temporary passwords shown only once in confirmation/result response
- temporary passwords not stored in messages, metadata, summaries, logs, or account detail pages
- imported coaches must change password on first login
- only Django staff/superusers can access coach import

Tests:
Add tests for:
- valid CSV creates coach account
- imported coach role is coach
- imported coach is active by default
- imported coach must change password
- random temporary password is hashed and shown once
- temporary password not shown on later pages
- explicit username normalized/validated
- generated username collision suffixes
- duplicate email with existing coach reused
- duplicate email with non-coach conflicts
- invalid/missing required fields produce row errors
- `is_active=false` creates inactive coach
- no `UserPlayerLink` is created
- no `players.Player` is created
- coach import pages require staff
- regular users denied
- Account Operations still works
- existing player import provisioning still works

Do NOT implement:
- coach-to-player links
- Coach model
- persistent coach import batch model
- player import changes
- Analytics permission changes
- evaluation submission changes
- player “My Evaluations”
- coach evaluation review
- audit logging
- invitations
- email verification
- APIs
- JavaScript

Verification:
Run:
- python manage.py check
- python manage.py makemigrations accounts --check
- python manage.py test accounts
- python manage.py test analytics
- python manage.py test players
- python manage.py test drafts
- python manage.py test pdp
- python manage.py test
- git diff --check

Prompt archive:
Create the next prompt record in `docs/prompts/` according to AGENTS.md.

Commit implementation first.
Then commit prompt archive separately.
Push both commits.

Final report:
- implementation summary
- files created
- files modified
- routes added
- services added
- templates/forms added
- tests added
- test results
- implementation decisions
- deviations
- technical debt
- confirmation that only Phase 1 Coach Import was implemented
```

## App / Subsystem

account_management

## Work Commit

```text
5e2b196cf3106f2a2a94c7ac4106ddeb2d842bff Implement coach account import workflow
```

## Commit Diff

```diff
commit 5e2b196cf3106f2a2a94c7ac4106ddeb2d842bff
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 8 13:21:38 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 8 13:21:38 2026 -0700

    Implement coach account import workflow
---
 accounts/forms.py                                  |   8 +
 accounts/services/coach_import_service.py          | 447 +++++++++++++++++++++
 accounts/services/username_service.py              |  19 +-
 accounts/templates/accounts/coach_import_list.html |  18 +
 .../templates/accounts/coach_import_preview.html   |  81 ++++
 .../templates/accounts/coach_import_result.html    |  65 +++
 .../templates/accounts/coach_import_upload.html    |  23 ++
 .../templates/accounts/operations_dashboard.html   |   1 +
 accounts/tests.py                                  | 217 ++++++++++
 accounts/urls.py                                   |   8 +
 accounts/views.py                                  |  76 ++++
 11 files changed, 962 insertions(+), 1 deletion(-)

diff --git a/accounts/forms.py b/accounts/forms.py
index 3568389..9e77ab9 100644
--- a/accounts/forms.py
+++ b/accounts/forms.py
@@ -86,3 +86,11 @@ class BulkAccountOperationForm(forms.Form):
         if self.cleaned_data.get("select_all"):
             return self.cleaned_data.get("visible_user_ids", [])
         return self.cleaned_data.get("user_ids", [])
+
+
+class CoachImportUploadForm(forms.Form):
+    csv_file = forms.FileField(label="Coach CSV")
+
+
+class CoachImportConfirmForm(forms.Form):
+    confirm = forms.BooleanField(required=True, label="Create or reuse the valid coach accounts shown in the preview.")
diff --git a/accounts/services/coach_import_service.py b/accounts/services/coach_import_service.py
new file mode 100644
index 0000000..bc536ed
--- /dev/null
+++ b/accounts/services/coach_import_service.py
@@ -0,0 +1,447 @@
+from __future__ import annotations
+
+import csv
+from dataclasses import dataclass, field, replace
+from io import StringIO
+
+from django.contrib.auth import get_user_model
+from django.core.exceptions import ValidationError
+from django.db import transaction
+
+from accounts.models import AccountRole
+from accounts.services.email_service import find_existing_email_user, normalize_email
+from accounts.services.password_service import set_random_temporary_password
+from accounts.services.permissions import can_manage_accounts
+from accounts.services.profile_service import get_or_create_account_profile, set_account_role
+from accounts.services.username_service import validate_available_username, username_for_person
+
+
+User = get_user_model()
+
+REQUIRED_COLUMNS = {"first_name", "last_name", "email"}
+OPTIONAL_COLUMNS = {"username", "team", "division", "is_active", "notes", "source_id"}
+SUPPORTED_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS
+
+STATUS_READY = "ready"
+STATUS_REUSE = "reuse"
+STATUS_CONFLICT = "conflict"
+STATUS_ERROR = "error"
+
+RESULT_CREATED = "created"
+RESULT_REUSED = "reused"
+RESULT_CONFLICT = "conflict"
+RESULT_ERROR = "error"
+RESULT_SKIPPED = "skipped"
+
+
+@dataclass(frozen=True)
+class CoachImportRowPreview:
+    row_number: int
+    first_name: str = ""
+    last_name: str = ""
+    email: str = ""
+    username: str = ""
+    generated_username: str = ""
+    team: str = ""
+    division: str = ""
+    is_active: bool = True
+    notes: str = ""
+    source_id: str = ""
+    status: str = STATUS_READY
+    messages: list[str] = field(default_factory=list)
+    existing_user_id: int | None = None
+
+    @property
+    def final_username(self) -> str:
+        return self.username or self.generated_username
+
+    @property
+    def can_commit(self) -> bool:
+        return self.status in {STATUS_READY, STATUS_REUSE}
+
+
+@dataclass(frozen=True)
+class CoachImportPreview:
+    rows: list[CoachImportRowPreview]
+    headers: list[str]
+    row_errors: list[str]
+
+    @property
+    def rows_processed(self) -> int:
+        return len(self.rows)
+
+    @property
+    def ready_count(self) -> int:
+        return sum(1 for row in self.rows if row.status == STATUS_READY)
+
+    @property
+    def reuse_count(self) -> int:
+        return sum(1 for row in self.rows if row.status == STATUS_REUSE)
+
+    @property
+    def conflict_count(self) -> int:
+        return sum(1 for row in self.rows if row.status == STATUS_CONFLICT)
+
+    @property
+    def error_count(self) -> int:
+        return len(self.row_errors) + sum(1 for row in self.rows if row.status == STATUS_ERROR)
+
+    @property
+    def can_confirm(self) -> bool:
+        return any(row.can_commit for row in self.rows)
+
+
+@dataclass(frozen=True)
+class CoachImportResultRow:
+    row_number: int
+    status: str
+    username: str = ""
+    user_id: int | None = None
+    temporary_password: str = field(default="", repr=False)
+    messages: list[str] = field(default_factory=list)
+
+
+@dataclass(frozen=True)
+class CoachImportResult:
+    rows: list[CoachImportResultRow]
+
+    @property
+    def rows_processed(self) -> int:
+        return len(self.rows)
+
+    @property
+    def users_created(self) -> int:
+        return sum(1 for row in self.rows if row.status == RESULT_CREATED)
+
+    @property
+    def existing_coaches_reused(self) -> int:
+        return sum(1 for row in self.rows if row.status == RESULT_REUSED)
+
+    @property
+    def conflicts(self) -> int:
+        return sum(1 for row in self.rows if row.status == RESULT_CONFLICT)
+
+    @property
+    def errors(self) -> int:
+        return sum(1 for row in self.rows if row.status == RESULT_ERROR)
+
+    @property
+    def skipped_rows(self) -> int:
+        return sum(1 for row in self.rows if row.status == RESULT_SKIPPED)
+
+    @property
+    def active_accounts(self) -> int:
+        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and "inactive" not in row.messages)
+
+    @property
+    def inactive_accounts(self) -> int:
+        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and "inactive" in row.messages)
+
+    @property
+    def password_change_required(self) -> int:
+        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED})
+
+
+def _validate_actor(actor) -> None:
+    if not can_manage_accounts(actor):
+        raise ValidationError("Only staff users can import coaches.")
+
+
+def _parse_bool(value, default=True) -> bool:
+    text = str(value or "").strip().casefold()
+    if not text:
+        return default
+    if text in {"1", "true", "yes", "y", "active"}:
+        return True
+    if text in {"0", "false", "no", "n", "inactive"}:
+        return False
+    raise ValidationError("is_active must be true or false.")
+
+
+def _decode_csv_file(uploaded_file) -> str:
+    uploaded_file.seek(0)
+    raw = uploaded_file.read()
+    if isinstance(raw, str):
+        return raw
+    try:
+        return raw.decode("utf-8-sig")
+    except UnicodeDecodeError as exc:
+        raise ValidationError("Coach import CSV must be UTF-8 encoded.") from exc
+
+
+def _normalize_header(header: str) -> str:
+    return str(header or "").strip().casefold().replace(" ", "_")
+
+
+def _read_csv(csv_text: str) -> tuple[list[str], list[dict[str, str]]]:
+    reader = csv.DictReader(StringIO(csv_text))
+    headers = [_normalize_header(header) for header in (reader.fieldnames or [])]
+    missing = sorted(REQUIRED_COLUMNS - set(headers))
+    if missing:
+        raise ValidationError(f"Missing required column(s): {', '.join(missing)}.")
+
+    rows = []
+    for raw_row in reader:
+        normalized_row = {}
+        for header, value in raw_row.items():
+            normalized_header = _normalize_header(header)
+            if normalized_header in SUPPORTED_COLUMNS:
+                normalized_row[normalized_header] = str(value or "").strip()
+        rows.append(normalized_row)
+    return headers, rows
+
+
+def _role_for_user(user) -> str:
+    profile = getattr(user, "account_profile", None)
+    if profile:
+        return profile.role
+    return get_or_create_account_profile(user).role
+
+
+def _preview_row(row_number: int, row: dict[str, str]) -> CoachImportRowPreview:
+    messages = []
+    first_name = row.get("first_name", "").strip()
+    last_name = row.get("last_name", "").strip()
+    email = normalize_email(row.get("email", ""))
+    explicit_username = row.get("username", "").strip()
+    team = row.get("team", "").strip()
+    division = row.get("division", "").strip()
+    notes = row.get("notes", "").strip()
+    source_id = row.get("source_id", "").strip()
+
+    try:
+        is_active = _parse_bool(row.get("is_active", ""), default=True)
+    except ValidationError as exc:
+        return CoachImportRowPreview(row_number=row_number, status=STATUS_ERROR, messages=list(exc.messages))
+
+    missing_fields = [label for label, value in [("first_name", first_name), ("last_name", last_name), ("email", email)] if not value]
+    if missing_fields:
+        return CoachImportRowPreview(
+            row_number=row_number,
+            first_name=first_name,
+            last_name=last_name,
+            email=email,
+            username=explicit_username,
+            team=team,
+            division=division,
+            is_active=is_active,
+            notes=notes,
+            source_id=source_id,
+            status=STATUS_ERROR,
+            messages=[f"Missing required field(s): {', '.join(missing_fields)}."],
+        )
+
+    existing_email_user = find_existing_email_user(email)
+    if existing_email_user:
+        existing_role = _role_for_user(existing_email_user)
+        if existing_role == AccountRole.COACH:
+            return CoachImportRowPreview(
+                row_number=row_number,
+                first_name=first_name,
+                last_name=last_name,
+                email=email,
+                username=existing_email_user.username,
+                team=team,
+                division=division,
+                is_active=is_active,
+                notes=notes,
+                source_id=source_id,
+                status=STATUS_REUSE,
+                messages=["Existing coach account will be reused."],
+                existing_user_id=existing_email_user.id,
+            )
+        return CoachImportRowPreview(
+            row_number=row_number,
+            first_name=first_name,
+            last_name=last_name,
+            email=email,
+            username=existing_email_user.username,
+            team=team,
+            division=division,
+            is_active=is_active,
+            notes=notes,
+            source_id=source_id,
+            status=STATUS_CONFLICT,
+            messages=["Email belongs to an existing non-coach account."],
+            existing_user_id=existing_email_user.id,
+        )
+
+    try:
+        username = validate_available_username(explicit_username) if explicit_username else ""
+        generated_username = "" if username else username_for_person(first_name, last_name)
+    except ValidationError as exc:
+        return CoachImportRowPreview(
+            row_number=row_number,
+            first_name=first_name,
+            last_name=last_name,
+            email=email,
+            username=explicit_username,
+            team=team,
+            division=division,
+            is_active=is_active,
+            notes=notes,
+            source_id=source_id,
+            status=STATUS_CONFLICT,
+            messages=list(exc.messages),
+        )
+
+    return CoachImportRowPreview(
+        row_number=row_number,
+        first_name=first_name,
+        last_name=last_name,
+        email=email,
+        username=username,
+        generated_username=generated_username,
+        team=team,
+        division=division,
+        is_active=is_active,
+        notes=notes,
+        source_id=source_id,
+        status=STATUS_READY,
+        messages=messages,
+    )
+
+
+def preview_coach_import(csv_text: str) -> CoachImportPreview:
+    """Return a non-persistent preview for a coach CSV import."""
+    try:
+        headers, rows = _read_csv(csv_text)
+    except ValidationError as exc:
+        return CoachImportPreview(rows=[], headers=[], row_errors=list(exc.messages))
+
+    preview_rows = []
+    seen_emails = set()
+    seen_usernames = set()
+    for index, row in enumerate(rows, start=2):
+        preview_row = _preview_row(index, row)
+        if preview_row.email:
+            if preview_row.email in seen_emails:
+                preview_row = replace(
+                    preview_row,
+                    status=STATUS_CONFLICT,
+                    messages=[*preview_row.messages, "Email appears more than once in this CSV."],
+                )
+            seen_emails.add(preview_row.email)
+        final_username = preview_row.final_username
+        if preview_row.status == STATUS_READY and final_username:
+            if final_username in seen_usernames:
+                preview_row = replace(
+                    preview_row,
+                    status=STATUS_CONFLICT,
+                    messages=[*preview_row.messages, "Username appears more than once in this CSV."],
+                )
+            seen_usernames.add(final_username)
+        preview_rows.append(preview_row)
+    return CoachImportPreview(rows=preview_rows, headers=headers, row_errors=[])
+
+
+def preview_coach_import_file(uploaded_file) -> CoachImportPreview:
+    """Read an uploaded CSV file and return a coach import preview."""
+    return preview_coach_import(_decode_csv_file(uploaded_file))
+
+
+def _metadata_for_row(row: CoachImportRowPreview) -> dict[str, str]:
+    return {
+        key: value
+        for key, value in {
+            "team": row.team,
+            "division": row.division,
+            "notes": row.notes,
+            "source_id": row.source_id,
+            "source": "coach_roster",
+        }.items()
+        if value
+    }
+
+
+@transaction.atomic
+def _reuse_existing_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
+    user = User.objects.select_for_update().select_related("account_profile").get(pk=row.existing_user_id)
+    profile = set_account_role(user, AccountRole.COACH)
+    metadata = {**profile.metadata, **_metadata_for_row(row)}
+    profile.metadata = metadata
+    profile.must_change_password = True
+    profile.save(update_fields=["metadata", "must_change_password", "updated_at"])
+    user.first_name = user.first_name or row.first_name
+    user.last_name = user.last_name or row.last_name
+    user.email = user.email or row.email
+    user.is_active = row.is_active
+    user.save(update_fields=["first_name", "last_name", "email", "is_active"])
+    temporary_password = set_random_temporary_password(user)
+    status_message = "inactive" if not user.is_active else "active"
+    return CoachImportResultRow(
+        row_number=row.row_number,
+        status=RESULT_REUSED,
+        username=user.username,
+        user_id=user.id,
+        temporary_password=temporary_password,
+        messages=[status_message],
+    )
+
+
+@transaction.atomic
+def _create_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
+    user = User.objects.create(
+        username=row.final_username,
+        first_name=row.first_name,
+        last_name=row.last_name,
+        email=row.email,
+        is_active=row.is_active,
+    )
+    temporary_password = set_random_temporary_password(user)
+    profile = set_account_role(user, AccountRole.COACH)
+    profile.must_change_password = True
+    profile.metadata = {**profile.metadata, **_metadata_for_row(row)}
+    profile.save(update_fields=["must_change_password", "metadata", "updated_at"])
+    status_message = "inactive" if not user.is_active else "active"
+    return CoachImportResultRow(
+        row_number=row.row_number,
+        status=RESULT_CREATED,
+        username=user.username,
+        user_id=user.id,
+        temporary_password=temporary_password,
+        messages=[status_message],
+    )
+
+
+def commit_coach_import(actor, csv_text: str) -> CoachImportResult:
+    """Create or reuse coach accounts from CSV text and return one-time passwords."""
+    _validate_actor(actor)
+    preview = preview_coach_import(csv_text)
+    result_rows = []
+
+    for error in preview.row_errors:
+        result_rows.append(CoachImportResultRow(row_number=0, status=RESULT_ERROR, messages=[error]))
+
+    for row in preview.rows:
+        if row.status == STATUS_READY:
+            try:
+                result_rows.append(_create_coach(row))
+            except ValidationError as exc:
+                result_rows.append(CoachImportResultRow(row_number=row.row_number, status=RESULT_ERROR, messages=list(exc.messages)))
+        elif row.status == STATUS_REUSE:
+            try:
+                result_rows.append(_reuse_existing_coach(row))
+            except ValidationError as exc:
+                result_rows.append(CoachImportResultRow(row_number=row.row_number, status=RESULT_ERROR, messages=list(exc.messages)))
+        elif row.status == STATUS_CONFLICT:
+            result_rows.append(
+                CoachImportResultRow(
+                    row_number=row.row_number,
+                    status=RESULT_CONFLICT,
+                    username=row.final_username,
+                    user_id=row.existing_user_id,
+                    messages=row.messages,
+                )
+            )
+        else:
+            result_rows.append(
+                CoachImportResultRow(
+                    row_number=row.row_number,
+                    status=RESULT_ERROR,
+                    username=row.final_username,
+                    messages=row.messages,
+                )
+            )
+
+    return CoachImportResult(rows=result_rows)
diff --git a/accounts/services/username_service.py b/accounts/services/username_service.py
index a2199e9..bab9f9f 100644
--- a/accounts/services/username_service.py
+++ b/accounts/services/username_service.py
@@ -22,14 +22,31 @@ def base_username_for_player(player) -> str:
     """Return firstname.lastname username base for a player."""
     first = normalize_username_part(getattr(player, "first_name", ""))
     last = normalize_username_part(getattr(player, "last_name", ""))
+    return base_username_for_person(first, last)
+
+
+def base_username_for_person(first_name: str, last_name: str) -> str:
+    """Return firstname.lastname username base for a person."""
+    first = normalize_username_part(first_name)
+    last = normalize_username_part(last_name)
     if not first or not last:
-        raise ValidationError("Player first and last name are required to generate a username.")
+        raise ValidationError("First and last name are required to generate a username.")
     return f"{first}.{last}"
 
 
 def username_for_player(player) -> str:
     """Return a unique deterministic username for a player."""
     base_username = base_username_for_player(player)
+    return unique_username_from_base(base_username)
+
+
+def username_for_person(first_name: str, last_name: str) -> str:
+    """Return a unique deterministic firstname.lastname username for a person."""
+    return unique_username_from_base(base_username_for_person(first_name, last_name))
+
+
+def unique_username_from_base(base_username: str) -> str:
+    """Return an available username by suffixing a normalized base when needed."""
     username = base_username
     suffix = 2
     while User.objects.filter(username__iexact=username).exists():
diff --git a/accounts/templates/accounts/coach_import_list.html b/accounts/templates/accounts/coach_import_list.html
new file mode 100644
index 0000000..0a5c3ed
--- /dev/null
+++ b/accounts/templates/accounts/coach_import_list.html
@@ -0,0 +1,18 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Import Coaches{% endblock %}
+{% block pdp_subtitle %}Create or reuse coach accounts from a CSV file.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>Coach CSV</h2>
+        <p>Required columns: first_name, last_name, email.</p>
+        <p>Optional columns: username, team, division, is_active, notes, source_id.</p>
+        <div class="pdp-actions">
+            <a class="button button--primary" href="{% url 'accounts:coach-import-new' %}">Upload Coach CSV</a>
+            <a class="button button--ghost" href="{% url 'accounts:operations-dashboard' %}">Account Operations</a>
+        </div>
+    </article>
+</section>
+{% endblock %}
diff --git a/accounts/templates/accounts/coach_import_preview.html b/accounts/templates/accounts/coach_import_preview.html
new file mode 100644
index 0000000..c908df5
--- /dev/null
+++ b/accounts/templates/accounts/coach_import_preview.html
@@ -0,0 +1,81 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Preview Coach Import{% endblock %}
+{% block pdp_subtitle %}Review rows before creating or reusing coach accounts.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>Summary</h2>
+        <dl class="pdp-definition-list">
+            <dt>Rows processed</dt><dd>{{ preview.rows_processed }}</dd>
+            <dt>Ready to create</dt><dd>{{ preview.ready_count }}</dd>
+            <dt>Existing coaches to reuse</dt><dd>{{ preview.reuse_count }}</dd>
+            <dt>Conflicts</dt><dd>{{ preview.conflict_count }}</dd>
+            <dt>Errors</dt><dd>{{ preview.error_count }}</dd>
+        </dl>
+        {% if preview.row_errors %}
+            <ul>
+                {% for error in preview.row_errors %}
+                    <li>{{ error }}</li>
+                {% endfor %}
+            </ul>
+        {% endif %}
+    </article>
+
+    <article class="pdp-card">
+        <h2>Rows</h2>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr>
+                        <th>Row</th>
+                        <th>Name</th>
+                        <th>Email</th>
+                        <th>Username</th>
+                        <th>Active</th>
+                        <th>Status</th>
+                        <th>Messages</th>
+                    </tr>
+                </thead>
+                <tbody>
+                    {% for row in preview.rows %}
+                        <tr>
+                            <td>{{ row.row_number }}</td>
+                            <td>{{ row.first_name }} {{ row.last_name }}</td>
+                            <td>{{ row.email }}</td>
+                            <td>{{ row.final_username|default:"-" }}</td>
+                            <td>{{ row.is_active|yesno:"Yes,No" }}</td>
+                            <td>{{ row.status }}</td>
+                            <td>
+                                {% for message in row.messages %}
+                                    <div>{{ message }}</div>
+                                {% empty %}
+                                    -
+                                {% endfor %}
+                            </td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="7">No rows found.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Confirm</h2>
+        <p>Only rows marked ready or reuse will be processed. Temporary passwords are shown once on the result page.</p>
+        <form method="post" action="{% url 'accounts:coach-import-confirm' %}" class="pdp-form">
+            {% csrf_token %}
+            <label>
+                {{ form.confirm }}
+                {{ form.confirm.label }}
+                {{ form.confirm.errors }}
+            </label>
+            <button class="button button--primary" type="submit" {% if not preview.can_confirm %}disabled{% endif %}>Confirm Import</button>
+            <a class="button button--ghost" href="{% url 'accounts:coach-import-new' %}">Upload Different CSV</a>
+        </form>
+    </article>
+</section>
+{% endblock %}
diff --git a/accounts/templates/accounts/coach_import_result.html b/accounts/templates/accounts/coach_import_result.html
new file mode 100644
index 0000000..db9e86d
--- /dev/null
+++ b/accounts/templates/accounts/coach_import_result.html
@@ -0,0 +1,65 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Coach Import Result{% endblock %}
+{% block pdp_subtitle %}Copy temporary passwords now. They will not be shown again.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>Summary</h2>
+        <dl class="pdp-definition-list">
+            <dt>Rows processed</dt><dd>{{ result.rows_processed }}</dd>
+            <dt>Users created</dt><dd>{{ result.users_created }}</dd>
+            <dt>Existing coaches reused</dt><dd>{{ result.existing_coaches_reused }}</dd>
+            <dt>Conflicts</dt><dd>{{ result.conflicts }}</dd>
+            <dt>Errors</dt><dd>{{ result.errors }}</dd>
+            <dt>Skipped rows</dt><dd>{{ result.skipped_rows }}</dd>
+            <dt>Active accounts</dt><dd>{{ result.active_accounts }}</dd>
+            <dt>Inactive accounts</dt><dd>{{ result.inactive_accounts }}</dd>
+            <dt>Password change required</dt><dd>{{ result.password_change_required }}</dd>
+        </dl>
+    </article>
+
+    <article class="pdp-card">
+        <h2>Rows</h2>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr>
+                        <th>Row</th>
+                        <th>Status</th>
+                        <th>Username</th>
+                        <th>Temporary password</th>
+                        <th>Messages</th>
+                    </tr>
+                </thead>
+                <tbody>
+                    {% for row in result.rows %}
+                        <tr>
+                            <td>{{ row.row_number|default:"-" }}</td>
+                            <td>{{ row.status }}</td>
+                            <td>
+                                {% if row.user_id %}
+                                    <a href="{% url 'accounts:user-detail' user_id=row.user_id %}">{{ row.username }}</a>
+                                {% else %}
+                                    {{ row.username|default:"-" }}
+                                {% endif %}
+                            </td>
+                            <td><strong>{{ row.temporary_password|default:"-" }}</strong></td>
+                            <td>
+                                {% for message in row.messages %}
+                                    <div>{{ message }}</div>
+                                {% empty %}
+                                    -
+                                {% endfor %}
+                            </td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="5">No rows processed.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    </article>
+</section>
+{% endblock %}
diff --git a/accounts/templates/accounts/coach_import_upload.html b/accounts/templates/accounts/coach_import_upload.html
new file mode 100644
index 0000000..7874464
--- /dev/null
+++ b/accounts/templates/accounts/coach_import_upload.html
@@ -0,0 +1,23 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Upload Coach CSV{% endblock %}
+{% block pdp_subtitle %}Preview coach accounts before creating or reusing them.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>Upload</h2>
+        <form method="post" enctype="multipart/form-data" class="pdp-form">
+            {% csrf_token %}
+            {{ form.non_field_errors }}
+            <label>
+                Coach CSV
+                {{ form.csv_file }}
+                {{ form.csv_file.errors }}
+            </label>
+            <button class="button button--primary" type="submit">Preview Import</button>
+            <a class="button button--ghost" href="{% url 'accounts:coach-import-list' %}">Cancel</a>
+        </form>
+    </article>
+</section>
+{% endblock %}
diff --git a/accounts/templates/accounts/operations_dashboard.html b/accounts/templates/accounts/operations_dashboard.html
index 514a518..76d6ba2 100644
--- a/accounts/templates/accounts/operations_dashboard.html
+++ b/accounts/templates/accounts/operations_dashboard.html
@@ -10,6 +10,7 @@
         <div class="pdp-actions">
             <a class="button button--primary" href="{% url 'accounts:account-create' %}">Create Account</a>
             <a class="button button--ghost" href="{% url 'accounts:player-account-create' %}">Create Player Account</a>
+            <a class="button button--ghost" href="{% url 'accounts:coach-import-list' %}">Import Coaches</a>
         </div>
     </article>
 
diff --git a/accounts/tests.py b/accounts/tests.py
index bba2ce8..96eec66 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -3,6 +3,7 @@ from django.contrib.messages import get_messages
 from django.contrib.auth import get_user_model
 from django.conf import settings
 from django.core.exceptions import ValidationError
+from django.core.files.uploadedfile import SimpleUploadedFile
 from django.db import IntegrityError, transaction
 from django.test import TestCase
 from django.urls import reverse
@@ -36,6 +37,13 @@ from accounts.services.auth_redirect_service import (
     landing_url_for_user,
     should_force_password_change,
 )
+from accounts.services.coach_import_service import (
+    RESULT_CONFLICT,
+    RESULT_CREATED,
+    RESULT_REUSED,
+    commit_coach_import,
+    preview_coach_import,
+)
 from accounts.services.email_service import emails_equal, find_existing_email_user, normalize_email
 from accounts.services.permissions import (
     can_access_account_operations,
@@ -80,10 +88,12 @@ from accounts.services.profile_service import get_account_role, get_or_create_ac
 from accounts.services.role_service import default_role_for_user, role_for_user, role_label, validate_role
 from accounts.services.username_service import (
     base_username_for_player,
+    base_username_for_person,
     normalize_username_part,
     validate_available_username,
     validate_available_username_for_user,
     username_for_player,
+    username_for_person,
 )
 from analytics.services.permissions import can_submit_coach_assessment
 from players.models import Player, PlayerImportBatch
@@ -1569,6 +1579,137 @@ class AccountAuthViewTests(TestCase):
         self.assertContains(response, "Guest Evaluator")
 
 
+class CoachImportServiceTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
+
+    def csv_text(self, rows):
+        return "first_name,last_name,email,username,team,division,is_active,notes,source_id\n" + "\n".join(rows)
+
+    def test_valid_csv_creates_active_coach_with_one_time_password(self):
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,Lead coach,C001"]),
+        )
+
+        user = User.objects.get(email="casey@example.com")
+        profile = user.account_profile
+        result_row = result.rows[0]
+        self.assertEqual(result_row.status, RESULT_CREATED)
+        self.assertEqual(user.username, "casey.coach")
+        self.assertEqual(user.first_name, "Casey")
+        self.assertEqual(user.last_name, "Coach")
+        self.assertTrue(user.is_active)
+        self.assertEqual(profile.role, AccountRole.COACH)
+        self.assertTrue(profile.must_change_password)
+        self.assertEqual(profile.metadata["team"], "Reds")
+        self.assertEqual(profile.metadata["division"], "13U")
+        self.assertTrue(result_row.temporary_password)
+        self.assertTrue(user.check_password(result_row.temporary_password))
+        self.assertNotIn(result_row.temporary_password, repr(result_row))
+        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
+        self.assertEqual(Player.objects.count(), 0)
+        self.assertEqual(result.users_created, 1)
+        self.assertEqual(result.active_accounts, 1)
+        self.assertEqual(result.inactive_accounts, 0)
+        self.assertEqual(result.password_change_required, 1)
+
+    def test_imported_coach_can_be_inactive(self):
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Inactive,Coach,inactive.coach@example.com,,,,false,,"]),
+        )
+
+        user = User.objects.get(username="inactive.coach")
+        self.assertFalse(user.is_active)
+        self.assertEqual(result.inactive_accounts, 1)
+
+    def test_explicit_username_is_normalized_and_validated(self):
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["User,Name,user.name@example.com,Explicit.User,,,,,"]),
+        )
+
+        self.assertEqual(result.rows[0].username, "explicit.user")
+        self.assertTrue(User.objects.filter(username="explicit.user").exists())
+
+    def test_generated_username_collision_uses_suffix(self):
+        User.objects.create_user(username="casey.coach", email="other@example.com")
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Casey,Coach,casey2@example.com,,,,,,"]),
+        )
+
+        self.assertEqual(result.rows[0].username, "casey.coach2")
+        self.assertTrue(User.objects.filter(username="casey.coach2").exists())
+
+    def test_duplicate_email_with_existing_coach_reuses_account(self):
+        existing = User.objects.create_user(username="existing.coach", email="coach@example.com", password="oldpass")
+        set_account_role(existing, AccountRole.COACH)
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Existing,Coach,COACH@example.com,,,,,,"]),
+        )
+
+        existing.refresh_from_db()
+        self.assertEqual(result.rows[0].status, RESULT_REUSED)
+        self.assertEqual(result.existing_coaches_reused, 1)
+        self.assertEqual(User.objects.filter(email__iexact="coach@example.com").count(), 1)
+        self.assertTrue(existing.account_profile.must_change_password)
+        self.assertTrue(existing.check_password(result.rows[0].temporary_password))
+
+    def test_duplicate_email_with_non_coach_conflicts(self):
+        existing = User.objects.create_user(username="player.user", email="shared@example.com")
+        set_account_role(existing, AccountRole.PLAYER)
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Shared,Coach,shared@example.com,,,,,,"]),
+        )
+
+        self.assertEqual(result.rows[0].status, RESULT_CONFLICT)
+        self.assertEqual(result.conflicts, 1)
+        self.assertEqual(User.objects.count(), 2)
+
+    def test_explicit_duplicate_username_conflicts(self):
+        User.objects.create_user(username="taken.name")
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Taken,Name,taken@example.com,taken.name,,,,,"]),
+        )
+
+        self.assertEqual(result.rows[0].status, RESULT_CONFLICT)
+        self.assertFalse(User.objects.filter(email="taken@example.com").exists())
+
+    def test_missing_required_fields_produce_row_errors(self):
+        preview = preview_coach_import("first_name,last_name,email\nMissing,Email,\n")
+        result = commit_coach_import(self.staff, "first_name,last_name,email\nMissing,Email,\n")
+
+        self.assertEqual(preview.rows[0].status, "error")
+        self.assertIn("Missing required field", preview.rows[0].messages[0])
+        self.assertEqual(result.errors, 1)
+        self.assertEqual(User.objects.count(), 1)
+
+    def test_missing_required_columns_produce_import_error(self):
+        result = commit_coach_import(self.staff, "first_name,last_name\nNo,Email\n")
+
+        self.assertEqual(result.errors, 1)
+        self.assertIn("Missing required column", result.rows[0].messages[0])
+
+    def test_regular_user_cannot_commit_coach_import(self):
+        regular = User.objects.create_user(username="regular", password="testpass")
+
+        with self.assertRaisesMessage(ValidationError, "Only staff users can import coaches"):
+            commit_coach_import(regular, self.csv_text(["Casey,Coach,casey@example.com,,,,,,"]))
+
+    def test_username_for_person_uses_same_normalization_style(self):
+        self.assertEqual(base_username_for_person("Jos\u00e9", "Van Horne"), "jose.vanhorne")
+        self.assertEqual(username_for_person("Jos\u00e9", "Van Horne"), "jose.vanhorne")
+
+
 class AccountOperationsViewTests(TestCase):
     def setUp(self):
         self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
@@ -1617,6 +1758,7 @@ class AccountOperationsViewTests(TestCase):
         self.assertContains(response, "Players without self-linked accounts")
         self.assertContains(response, reverse("accounts:account-create"))
         self.assertContains(response, reverse("accounts:player-account-create"))
+        self.assertContains(response, reverse("accounts:coach-import-list"))
 
     def test_user_list_requires_staff(self):
         self.client.force_login(self.regular)
@@ -2153,6 +2295,81 @@ class AccountOperationsViewTests(TestCase):
         self.assertContains(response, "Player already has a linked user account")
         self.assertEqual(UserPlayerLink.objects.filter(player=player, relationship=UserPlayerRelationship.SELF).count(), 1)
 
+    def test_coach_import_pages_require_staff(self):
+        self.client.force_login(self.regular)
+
+        urls = [
+            reverse("accounts:coach-import-list"),
+            reverse("accounts:coach-import-new"),
+            reverse("accounts:coach-import-preview"),
+            reverse("accounts:coach-import-confirm"),
+        ]
+
+        for url in urls:
+            response = self.client.get(url)
+            self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_preview_and_confirm_coach_import(self):
+        self.client.force_login(self.staff)
+        csv_file = SimpleUploadedFile(
+            "coaches.csv",
+            b"first_name,last_name,email,team,division\nNew,Coach,new.coach@example.com,Reds,13U\n",
+            content_type="text/csv",
+        )
+
+        upload_response = self.client.post(reverse("accounts:coach-import-new"), {"csv_file": csv_file})
+        self.assertEqual(upload_response.status_code, 302)
+        self.assertEqual(upload_response["Location"], reverse("accounts:coach-import-preview"))
+
+        preview_response = self.client.get(reverse("accounts:coach-import-preview"))
+        self.assertEqual(preview_response.status_code, 200)
+        self.assertContains(preview_response, "Ready to create")
+        self.assertContains(preview_response, "new.coach@example.com")
+
+        confirm_response = self.client.post(reverse("accounts:coach-import-confirm"), {"confirm": "on"})
+        self.assertEqual(confirm_response.status_code, 200)
+        self.assertContains(confirm_response, "Coach Import Result")
+        self.assertContains(confirm_response, "Temporary password")
+        user = User.objects.get(username="new.coach")
+        temporary_password = confirm_response.context["result"].rows[0].temporary_password
+        self.assertTrue(user.check_password(temporary_password))
+        self.assertTrue(user.is_active)
+        self.assertEqual(user.account_profile.role, AccountRole.COACH)
+        self.assertTrue(user.account_profile.must_change_password)
+        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
+        self.assertEqual(Player.objects.count(), 1)
+
+        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": user.id}))
+        self.assertNotContains(detail_response, temporary_password)
+        confirm_again = self.client.get(reverse("accounts:coach-import-confirm"))
+        self.assertEqual(confirm_again.status_code, 302)
+
+    def test_coach_import_reuses_existing_coach_and_blocks_non_coach_email(self):
+        existing_coach = User.objects.create_user(username="existing.coach", email="existing@example.com")
+        set_account_role(existing_coach, AccountRole.COACH)
+        existing_player = User.objects.create_user(username="existing.player", email="player@example.com")
+        set_account_role(existing_player, AccountRole.PLAYER)
+        self.client.force_login(self.staff)
+        csv_file = SimpleUploadedFile(
+            "coaches.csv",
+            (
+                "first_name,last_name,email\n"
+                "Existing,Coach,existing@example.com\n"
+                "Existing,Player,player@example.com\n"
+            ).encode(),
+            content_type="text/csv",
+        )
+
+        self.client.post(reverse("accounts:coach-import-new"), {"csv_file": csv_file})
+        response = self.client.post(reverse("accounts:coach-import-confirm"), {"confirm": "on"})
+
+        self.assertEqual(response.status_code, 200)
+        result = response.context["result"]
+        self.assertEqual(result.existing_coaches_reused, 1)
+        self.assertEqual(result.conflicts, 1)
+        self.assertEqual(User.objects.filter(email__iexact="existing@example.com").count(), 1)
+        self.assertEqual(User.objects.filter(email__iexact="player@example.com").count(), 1)
+
 
 class AccountPasswordMiddlewareTests(TestCase):
     def setUp(self):
diff --git a/accounts/urls.py b/accounts/urls.py
index f4fad92..7deccc6 100644
--- a/accounts/urls.py
+++ b/accounts/urls.py
@@ -12,6 +12,10 @@ from accounts.views import (
     AccountUserLinksView,
     AccountUserListView,
     AccountUserPasswordResetView,
+    CoachImportConfirmView,
+    CoachImportListView,
+    CoachImportPreviewView,
+    CoachImportUploadView,
     PlayerAccountCreateView,
 )
 
@@ -22,6 +26,10 @@ urlpatterns = [
     path("", AccountOperationsDashboardView.as_view(), name="operations-dashboard"),
     path("create/", AccountOnlyCreateView.as_view(), name="account-create"),
     path("create/player/", PlayerAccountCreateView.as_view(), name="player-account-create"),
+    path("imports/coaches/", CoachImportListView.as_view(), name="coach-import-list"),
+    path("imports/coaches/new/", CoachImportUploadView.as_view(), name="coach-import-new"),
+    path("imports/coaches/preview/", CoachImportPreviewView.as_view(), name="coach-import-preview"),
+    path("imports/coaches/confirm/", CoachImportConfirmView.as_view(), name="coach-import-confirm"),
     path("login/", AccountLoginView.as_view(), name="login"),
     path("logout/", AccountLogoutView.as_view(), name="logout"),
     path("password/", AccountPasswordChangeView.as_view(), name="password-change"),
diff --git a/accounts/views.py b/accounts/views.py
index 8b4a483..801a46e 100644
--- a/accounts/views.py
+++ b/accounts/views.py
@@ -11,6 +11,8 @@ from accounts.forms import (
     AccountEditForm,
     AccountOnlyCreateForm,
     BulkAccountOperationForm,
+    CoachImportConfirmForm,
+    CoachImportUploadForm,
     PasswordResetConfirmForm,
     PlayerAccountCreateForm,
     UserPlayerLinkForm,
@@ -36,6 +38,7 @@ from accounts.services.auth_redirect_service import (
     landing_url_for_user,
     should_force_password_change,
 )
+from accounts.services.coach_import_service import commit_coach_import, preview_coach_import, preview_coach_import_file
 from accounts.services.link_service import get_players_for_user
 from accounts.services.password_service import clear_password_change_required
 from accounts.services.permissions import (
@@ -172,6 +175,79 @@ class AccountUserListView(AccountOperationsStaffRequiredMixin, TemplateView):
         return self.render_to_response(self.get_context_data(bulk_form=form, bulk_result=bulk_result))
 
 
+class CoachImportListView(AccountOperationsStaffRequiredMixin, TemplateView):
+    template_name = "accounts/coach_import_list.html"
+
+
+class CoachImportUploadView(AccountOperationsStaffRequiredMixin, FormView):
+    template_name = "accounts/coach_import_upload.html"
+    form_class = CoachImportUploadForm
+
+    def form_valid(self, form):
+        try:
+            csv_file = form.cleaned_data["csv_file"]
+            preview_coach_import_file(csv_file)
+            csv_file.seek(0)
+            raw = csv_file.read()
+            csv_text = raw if isinstance(raw, str) else raw.decode("utf-8-sig")
+        except (UnicodeDecodeError, ValidationError) as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        self.request.session["coach_import_csv"] = csv_text
+        self.request.session.modified = True
+        return redirect("accounts:coach-import-preview")
+
+
+class CoachImportPreviewView(AccountOperationsStaffRequiredMixin, FormView):
+    template_name = "accounts/coach_import_preview.html"
+    form_class = CoachImportConfirmForm
+
+    def dispatch(self, request, *args, **kwargs):
+        if not request.user.is_authenticated or not self.test_func():
+            return super().dispatch(request, *args, **kwargs)
+        self.csv_text = request.session.get("coach_import_csv", "")
+        if not self.csv_text:
+            messages.error(request, "Upload a coach CSV before previewing an import.")
+            return redirect("accounts:coach-import-new")
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_preview(self):
+        return preview_coach_import(self.csv_text)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["preview"] = self.get_preview()
+        return context
+
+    def form_valid(self, form):
+        return redirect("accounts:coach-import-confirm")
+
+
+class CoachImportConfirmView(AccountOperationsStaffRequiredMixin, TemplateView):
+    template_name = "accounts/coach_import_result.html"
+
+    def get(self, request, *args, **kwargs):
+        return redirect("accounts:coach-import-preview")
+
+    def post(self, request, *args, **kwargs):
+        form = CoachImportConfirmForm(request.POST)
+        if not form.is_valid():
+            messages.error(request, "Confirm the coach import before continuing.")
+            return redirect("accounts:coach-import-preview")
+        csv_text = request.session.get("coach_import_csv", "")
+        if not csv_text:
+            messages.error(request, "Upload a coach CSV before confirming an import.")
+            return redirect("accounts:coach-import-new")
+        try:
+            result = commit_coach_import(request.user, csv_text)
+        except ValidationError as exc:
+            messages.error(request, "; ".join(exc.messages))
+            return redirect("accounts:coach-import-preview")
+        request.session.pop("coach_import_csv", None)
+        request.session.modified = True
+        return self.render_to_response(self.get_context_data(result=result))
+
+
 class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
     template_name = "accounts/user_detail.html"
 
```

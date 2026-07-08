from django import forms

from accounts.models import AccountRole, UserPlayerRelationship
from accounts.services.account_operations_service import (
    BULK_ACTION_ACTIVATE,
    BULK_ACTION_CLEAR_PASSWORD_CHANGE,
    BULK_ACTION_DEACTIVATE,
    BULK_ACTION_REQUIRE_PASSWORD_CHANGE,
)
from players.models import Player


ACCOUNT_ONLY_ROLE_CHOICES = (
    (AccountRole.STAFF, "Staff"),
    (AccountRole.COACH, "Coach"),
    (AccountRole.PARENT, "Parent"),
    (AccountRole.GUEST_EVALUATOR, "Guest Evaluator"),
    (AccountRole.ADMIN, "Admin"),
)

BULK_ACTION_CHOICES = (
    (BULK_ACTION_ACTIVATE, "Activate"),
    (BULK_ACTION_DEACTIVATE, "Deactivate"),
    (BULK_ACTION_REQUIRE_PASSWORD_CHANGE, "Require password change"),
    (BULK_ACTION_CLEAR_PASSWORD_CHANGE, "Clear password change"),
)


class AccountOnlyCreateForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    role = forms.ChoiceField(choices=ACCOUNT_ONLY_ROLE_CHOICES)
    is_active = forms.BooleanField(required=False, initial=True, label="Activate account immediately")


class PlayerAccountCreateForm(forms.Form):
    player = forms.ModelChoiceField(queryset=Player.objects.none())
    username = forms.CharField(max_length=150, required=False, help_text="Leave blank to use firstname.lastname.")
    email = forms.EmailField(required=False)
    role = forms.ChoiceField(choices=((AccountRole.PLAYER, "Player"),), initial=AccountRole.PLAYER)
    is_active = forms.BooleanField(required=False, initial=True, label="Activate account immediately")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")


class AccountEditForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    role = forms.ChoiceField(choices=AccountRole.choices)
    is_active = forms.BooleanField(required=False, label="Account is active")


class UserPlayerLinkForm(forms.Form):
    player = forms.ModelChoiceField(queryset=Player.objects.none())
    relationship = forms.ChoiceField(choices=UserPlayerRelationship.choices)
    is_primary = forms.BooleanField(required=False, label="Primary self link")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")


class PasswordResetConfirmForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="I understand this temporary password will be shown once.")


class BulkAccountOperationForm(forms.Form):
    action = forms.ChoiceField(choices=BULK_ACTION_CHOICES)
    user_ids = forms.MultipleChoiceField(required=False)
    visible_user_ids = forms.MultipleChoiceField(required=False)
    select_all = forms.BooleanField(required=False, label="Select all accounts shown")

    def __init__(self, *args, visible_user_ids=None, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(str(user_id), str(user_id)) for user_id in visible_user_ids or []]
        self.fields["user_ids"].choices = choices
        self.fields["visible_user_ids"].choices = choices

    def selected_user_ids(self):
        if self.cleaned_data.get("select_all"):
            return self.cleaned_data.get("visible_user_ids", [])
        return self.cleaned_data.get("user_ids", [])


class CoachImportUploadForm(forms.Form):
    csv_file = forms.FileField(label="Coach CSV")


class CoachImportConfirmForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Create or reuse the valid coach accounts shown in the preview.")

from django import forms

from accounts.models import AccountRole, UserPlayerRelationship
from players.models import Player


ACCOUNT_ONLY_ROLE_CHOICES = (
    (AccountRole.STAFF, "Staff"),
    (AccountRole.COACH, "Coach"),
    (AccountRole.PARENT, "Parent"),
    (AccountRole.GUEST_EVALUATOR, "Guest Evaluator"),
    (AccountRole.ADMIN, "Admin"),
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

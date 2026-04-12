from django import forms
from django.contrib.auth import get_user_model

from leaguehub.models import Game, GamePhoto, GameStory, League, LeagueSeason, Team, TeamCoachAssignment
from pdp.models import Season


User = get_user_model()


def apply_form_control_styling(fields):
    for field in fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            continue
        existing = widget.attrs.get("class", "")
        widget.attrs["class"] = f"{existing} pdp-input".strip()


class UrlChoiceForm(forms.Form):
    destination = forms.ChoiceField(choices=(), required=False)

    def __init__(self, *args, choices=None, label="", field_name="destination", **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["destination"].choices = choices or []
        self.fields["destination"].label = label
        self.fields["destination"].widget.attrs.update(
            {
                "class": "leaguehub-select",
                "onchange": "if (this.value) { window.location.href = this.value; }",
            }
        )
        if field_name != "destination":
            self.fields[field_name] = self.fields.pop("destination")


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ["name", "slug", "year", "start_date", "end_date", "is_active"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control_styling(self.fields)


class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ["name", "slug", "description", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control_styling(self.fields)


class LeagueSeasonForm(forms.ModelForm):
    class Meta:
        model = LeagueSeason
        fields = ["league", "season", "slug", "title", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control_styling(self.fields)


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["league_season", "name", "slug", "short_name", "color", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control_styling(self.fields)


class CoachUserForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password", "is_staff"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control_styling(self.fields)
        self.fields["username"].required = False
        self.fields["is_staff"].help_text = "Leave off for regular coach accounts."

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        email = self.cleaned_data.get("email", "").strip().lower()
        if username:
            return username
        if email:
            return email
        raise forms.ValidationError("Provide either a username or an email.")

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user


class TeamCoachAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeamCoachAssignment
        fields = ["team", "user", "role", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control_styling(self.fields)


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["league_season", "game_date", "scheduled_start_time", "location", "home_team", "away_team", "status"]
        widgets = {
            "game_date": forms.DateInput(attrs={"type": "date"}),
            "scheduled_start_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control_styling(self.fields)


class ScoreSubmissionForm(forms.Form):
    home_score = forms.IntegerField(min_value=0)
    away_score = forms.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control_styling(self.fields)


class AdminScoreOverrideForm(ScoreSubmissionForm):
    require_reverification = forms.BooleanField(
        required=False,
        initial=False,
        label="Require away-team re-verification after this admin edit",
    )
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))


class ScoreVerificationForm(forms.Form):
    confirm = forms.BooleanField(initial=True, required=True, widget=forms.HiddenInput())


class GameStoryForm(forms.ModelForm):
    class Meta:
        model = GameStory
        fields = ["headline", "story"]
        widgets = {
            "story": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control_styling(self.fields)


class GamePhotoForm(forms.ModelForm):
    class Meta:
        model = GamePhoto
        fields = ["image", "caption"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_control_styling(self.fields)

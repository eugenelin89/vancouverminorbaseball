from django import forms
from django.contrib.auth import get_user_model

from accounts.models import AccountProfile, AccountRole
from players.models import Player
from seasons.models import (
    CoachAssignmentRole,
    CoachSeasonAssignment,
    PlayerRosterMembership,
    RosterStatus,
    Season,
    SeasonTeam,
)


class DateInput(forms.DateInput):
    input_type = "date"


class SeasonForm(forms.Form):
    key = forms.SlugField(max_length=80)
    name = forms.CharField(max_length=120)
    starts_on = forms.DateField(required=False, widget=DateInput)
    ends_on = forms.DateField(required=False, widget=DateInput)
    is_active = forms.BooleanField(required=False, initial=True)


class ConfirmCurrentSeasonForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="I understand this will make this the current season.")


class SeasonTeamForm(forms.Form):
    season = forms.ModelChoiceField(queryset=Season.objects.none())
    name = forms.CharField(max_length=120)
    division = forms.CharField(max_length=80)
    external_source = forms.CharField(max_length=80, required=False)
    external_identifier = forms.CharField(max_length=160, required=False)
    is_active = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        fixed_season = kwargs.pop("fixed_season", None)
        super().__init__(*args, **kwargs)
        self.fields["season"].queryset = Season.objects.filter(is_active=True).order_by("-is_current", "-starts_on", "name")
        if fixed_season:
            self.fields["season"].initial = fixed_season
            self.fields["season"].disabled = True


class PlayerRosterMembershipForm(forms.Form):
    player = forms.ModelChoiceField(queryset=Player.objects.none())
    season_team = forms.ModelChoiceField(queryset=SeasonTeam.objects.none())
    status = forms.ChoiceField(choices=RosterStatus.choices, initial=RosterStatus.ACTIVE)
    jersey_number = forms.CharField(max_length=20, required=False)
    is_primary = forms.BooleanField(required=False)
    is_active = forms.BooleanField(required=False, initial=True)
    starts_on = forms.DateField(required=False, widget=DateInput)
    ends_on = forms.DateField(required=False, widget=DateInput)
    source = forms.CharField(max_length=80, required=False)
    source_identifier = forms.CharField(max_length=160, required=False)

    def __init__(self, *args, **kwargs):
        fixed_season = kwargs.pop("fixed_season", None)
        editing = kwargs.pop("editing", False)
        super().__init__(*args, **kwargs)
        self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")
        teams = SeasonTeam.objects.select_related("season").filter(is_active=True).order_by("-season__is_current", "season__name", "division", "name")
        if fixed_season:
            teams = teams.filter(season=fixed_season)
        self.fields["season_team"].queryset = teams
        if editing:
            self.fields["player"].disabled = True
            self.fields["season_team"].disabled = True


class PlayerMembershipEndForm(forms.Form):
    status = forms.ChoiceField(
        choices=(
            (RosterStatus.INACTIVE, "Inactive"),
            (RosterStatus.REMOVED, "Removed"),
            (RosterStatus.TRANSFERRED, "Transferred"),
        ),
        initial=RosterStatus.INACTIVE,
    )
    ends_on = forms.DateField(required=False, widget=DateInput)
    confirm = forms.BooleanField(required=True, label="I understand this preserves history and ends the active membership.")


class PlayerMembershipTransferForm(forms.Form):
    ACTION_TRANSFER = "transfer"
    ACTION_ADDITIONAL = "additional"
    ACTION_CHOICES = (
        (ACTION_TRANSFER, "Transfer and make destination primary"),
        (ACTION_ADDITIONAL, "Add additional non-primary membership"),
    )

    action = forms.ChoiceField(choices=ACTION_CHOICES, initial=ACTION_TRANSFER)
    season_team = forms.ModelChoiceField(queryset=SeasonTeam.objects.none(), label="Destination team")
    transfer_date = forms.DateField(required=False, widget=DateInput)
    jersey_number = forms.CharField(max_length=20, required=False)
    source = forms.CharField(max_length=80, required=False)
    source_identifier = forms.CharField(max_length=160, required=False)

    def __init__(self, *args, source_membership: PlayerRosterMembership, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_membership = source_membership
        self.fields["season_team"].queryset = (
            SeasonTeam.objects.filter(season=source_membership.season, is_active=True)
            .exclude(pk=source_membership.season_team_id)
            .order_by("division", "name", "id")
        )

    def clean_season_team(self):
        season_team = self.cleaned_data["season_team"]
        duplicate = (
            PlayerRosterMembership.objects.filter(
                player=self.source_membership.player,
                season_team=season_team,
                is_active=True,
            )
            .exclude(pk=self.source_membership.pk)
            .exists()
        )
        if duplicate:
            raise forms.ValidationError("This player already has an active membership on the destination team.")
        return season_team


class CoachSeasonAssignmentForm(forms.Form):
    user = forms.ModelChoiceField(queryset=get_user_model().objects.none(), label="Coach account")
    season_team = forms.ModelChoiceField(queryset=SeasonTeam.objects.none())
    assignment_role = forms.ChoiceField(choices=CoachAssignmentRole.choices, initial=CoachAssignmentRole.ASSISTANT_COACH)
    is_primary = forms.BooleanField(required=False)
    is_active = forms.BooleanField(required=False, initial=True)
    starts_on = forms.DateField(required=False, widget=DateInput)
    ends_on = forms.DateField(required=False, widget=DateInput)
    source = forms.CharField(max_length=80, required=False)
    source_identifier = forms.CharField(max_length=160, required=False)

    def __init__(self, *args, **kwargs):
        fixed_season = kwargs.pop("fixed_season", None)
        editing = kwargs.pop("editing", False)
        super().__init__(*args, **kwargs)
        coach_user_ids = AccountProfile.objects.filter(role=AccountRole.COACH).values("user_id")
        self.fields["user"].queryset = (
            get_user_model().objects.filter(id__in=coach_user_ids).order_by("last_name", "first_name", "username", "id")
        )
        teams = SeasonTeam.objects.select_related("season").filter(is_active=True).order_by("-season__is_current", "season__name", "division", "name")
        if fixed_season:
            teams = teams.filter(season=fixed_season)
        self.fields["season_team"].queryset = teams
        if editing:
            self.fields["user"].disabled = True
            self.fields["season_team"].disabled = True


class CoachAssignmentEndForm(forms.Form):
    ends_on = forms.DateField(required=False, widget=DateInput)
    confirm = forms.BooleanField(required=True, label="I understand this preserves history and ends the active assignment.")

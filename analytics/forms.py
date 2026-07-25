from django import forms

from players.services.import_service import SOURCE_CHOICES, build_column_choices
from seasons.models import Season
from seasons.services.season_service import get_current_season


class PlayerImportUploadForm(forms.Form):
    season = forms.ModelChoiceField(
        queryset=Season.objects.none(),
        help_text="Choose the season for this roster import.",
    )
    csv_file = forms.FileField(
        help_text="Upload a player member-list or roster-detail CSV."
    )
    source = forms.ChoiceField(choices=SOURCE_CHOICES)
    provision_player_accounts = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["season"].queryset = Season.objects.filter(is_active=True).order_by(
            "-is_current", "-starts_on", "name"
        )
        current = get_current_season()
        if current and current.is_active:
            self.fields["season"].initial = current

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        if not csv_file.name.lower().endswith(".csv"):
            raise forms.ValidationError("Upload a .csv file.")
        return csv_file


class PlayerImportMappingForm(forms.Form):
    first_name = forms.ChoiceField(required=False)
    last_name = forms.ChoiceField(required=False)
    full_name = forms.ChoiceField(required=False)
    preferred_name = forms.ChoiceField(required=False)
    birthdate = forms.ChoiceField(required=False)
    birth_year = forms.ChoiceField(required=False)
    gender = forms.ChoiceField(required=False)
    division = forms.ChoiceField(required=False)
    team_name = forms.ChoiceField(required=False)
    primary_positions = forms.ChoiceField(required=False)
    bats = forms.ChoiceField(required=False)
    throws = forms.ChoiceField(required=False)
    school = forms.ChoiceField(required=False)
    graduation_year = forms.ChoiceField(required=False)
    registration_id = forms.ChoiceField(required=False)
    registrant_id = forms.ChoiceField(required=False)
    team_id = forms.ChoiceField(required=False)
    source_player_id = forms.ChoiceField(required=False)
    account_email = forms.ChoiceField(
        required=False,
        label="Player login email",
        help_text=(
            "Optional. Map only when the email belongs to the player's own login "
            "account. Leave blank for registration, parent, guardian, or family "
            "contact emails."
        ),
    )
    roster_status = forms.ChoiceField(required=False)
    jersey_number = forms.ChoiceField(required=False)
    membership_start_date = forms.ChoiceField(required=False)
    membership_end_date = forms.ChoiceField(required=False)
    roster_source_id = forms.ChoiceField(required=False)

    def __init__(self, *args, parsed=None, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [("", "---------")]
        if parsed:
            choices += build_column_choices(parsed)
        for field in self.fields.values():
            field.choices = choices

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("full_name") and not (
            cleaned_data.get("first_name") and cleaned_data.get("last_name")
        ):
            raise forms.ValidationError(
                "Map either full name or both first and last name."
            )
        return cleaned_data

    def mapping_config(self):
        return {key: value for key, value in self.cleaned_data.items() if value}


def parse_conflict_resolutions(post_data):
    resolutions = {}
    for key, value in post_data.items():
        if key.startswith("row_") and key.endswith("_action"):
            row_number = key.removeprefix("row_").removesuffix("_action")
            resolutions.setdefault(row_number, {"fields": {}})["action"] = value
        elif key.startswith("row_") and key.endswith("_candidate"):
            row_number = key.removeprefix("row_").removesuffix("_candidate")
            resolutions.setdefault(row_number, {"action": "commit", "fields": {}})[
                "candidate_id"
            ] = value
        elif key.startswith("row_") and "_field_" in key:
            row_part, field_name = key.removeprefix("row_").split("_field_", 1)
            resolutions.setdefault(row_part, {"action": "commit", "fields": {}})[
                "fields"
            ][field_name] = value
    return resolutions

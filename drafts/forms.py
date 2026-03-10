from django import forms

from .models import Draft, DraftAction, DraftPlayer, DraftStatus, DraftTeam
from .services import deserialize_import_preview, parse_player_csv, serialize_import_preview


class DraftForm(forms.ModelForm):
    teams = forms.CharField(
        help_text="Enter one team per line. Use Team Name|#RRGGBB for optional colors.",
        widget=forms.Textarea(attrs={"rows": 8, "placeholder": "Expos Navy|#102a43\nExpos Gold|#f7b733"}),
    )

    class Meta:
        model = Draft
        fields = ["name", "year", "division", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_teams(self):
        lines = [line.strip() for line in self.cleaned_data["teams"].splitlines() if line.strip()]
        if len(lines) < 2:
            raise forms.ValidationError("Enter at least two teams.")

        parsed = []
        names = set()
        for line in lines:
            name, _, color = line.partition("|")
            team_name = name.strip()
            if not team_name:
                raise forms.ValidationError("Each team line must include a team name.")
            if team_name.casefold() in names:
                raise forms.ValidationError(f"Duplicate team name: {team_name}")
            names.add(team_name.casefold())
            parsed.append({"name": team_name, "color": color.strip()})
        return parsed


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(help_text="Upload the draft-eligible player list as CSV.", required=False)
    preview_payload = forms.CharField(widget=forms.HiddenInput(), required=False)
    confirm_import = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("confirm_import"):
            if not cleaned_data.get("preview_payload"):
                raise forms.ValidationError("Import preview data is missing. Upload the CSV again.")
            cleaned_data["parsed_preview"] = deserialize_import_preview(cleaned_data["preview_payload"])
            return cleaned_data

        csv_file = cleaned_data.get("csv_file")
        if not csv_file:
            raise forms.ValidationError("Upload a CSV file to preview the import.")

        preview = parse_player_csv(csv_file)
        cleaned_data["parsed_preview"] = preview
        cleaned_data["preview_payload"] = serialize_import_preview(preview)
        return cleaned_data


class AssignPlayerForm(forms.Form):
    player_id = forms.IntegerField(widget=forms.HiddenInput())
    team_id = forms.ModelChoiceField(queryset=DraftTeam.objects.none())

    def __init__(self, *args, draft=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["team_id"].queryset = DraftTeam.objects.filter(draft=draft).order_by("display_order", "name")


class MovePlayerForm(forms.Form):
    player_id = forms.IntegerField(widget=forms.HiddenInput())
    to_team_id = forms.ModelChoiceField(queryset=DraftTeam.objects.none(), label="Move to")

    def __init__(self, *args, draft=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["to_team_id"].queryset = DraftTeam.objects.filter(draft=draft).order_by("display_order", "name")


class RemovePlayerForm(forms.Form):
    player_id = forms.IntegerField(widget=forms.HiddenInput())


class UndoActionForm(forms.Form):
    action_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean_action_id(self):
        action_id = self.cleaned_data["action_id"]
        if not DraftAction.objects.filter(pk=action_id).exists():
            raise forms.ValidationError("Unknown action.")
        return action_id


class DraftStatusForm(forms.Form):
    status = forms.ChoiceField(choices=DraftStatus.choices)


class TradeForm(forms.Form):
    team_one = forms.ModelChoiceField(queryset=DraftTeam.objects.none(), label="Team A")
    team_two = forms.ModelChoiceField(queryset=DraftTeam.objects.none(), label="Team B")
    team_one_players = forms.ModelMultipleChoiceField(
        queryset=DraftPlayer.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Team A players",
    )
    team_two_players = forms.ModelMultipleChoiceField(
        queryset=DraftPlayer.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Team B players",
    )

    def __init__(self, *args, draft=None, **kwargs):
        super().__init__(*args, **kwargs)
        teams = DraftTeam.objects.filter(draft=draft).order_by("display_order", "name")
        players = DraftPlayer.objects.filter(draft=draft, current_team__isnull=False).select_related("current_team")
        self.fields["team_one"].queryset = teams
        self.fields["team_two"].queryset = teams
        self.fields["team_one_players"].queryset = players
        self.fields["team_two_players"].queryset = players

        selected_team_one = None
        selected_team_two = None
        if self.is_bound:
            try:
                selected_team_one = int(self.data.get("team_one") or 0)
            except (TypeError, ValueError):
                selected_team_one = None
            try:
                selected_team_two = int(self.data.get("team_two") or 0)
            except (TypeError, ValueError):
                selected_team_two = None
        else:
            initial_team_one = self.initial.get("team_one")
            initial_team_two = self.initial.get("team_two")
            selected_team_one = getattr(initial_team_one, "id", initial_team_one)
            selected_team_two = getattr(initial_team_two, "id", initial_team_two)

        if selected_team_one:
            self.fields["team_one_players"].queryset = players.filter(current_team_id=selected_team_one)
        else:
            self.fields["team_one_players"].queryset = players.none()

        if selected_team_two:
            self.fields["team_two_players"].queryset = players.filter(current_team_id=selected_team_two)
        else:
            self.fields["team_two_players"].queryset = players.none()

    def clean(self):
        cleaned_data = super().clean()
        team_one = cleaned_data.get("team_one")
        team_two = cleaned_data.get("team_two")
        team_one_players = cleaned_data.get("team_one_players")
        team_two_players = cleaned_data.get("team_two_players")

        if team_one and team_two and team_one == team_two:
            raise forms.ValidationError("Choose two different teams.")

        if team_one and team_one_players:
            invalid = [player.full_name for player in team_one_players if player.current_team_id != team_one.id]
            if invalid:
                raise forms.ValidationError("Some Team A selections are no longer on that roster.")

        if team_two and team_two_players:
            invalid = [player.full_name for player in team_two_players if player.current_team_id != team_two.id]
            if invalid:
                raise forms.ValidationError("Some Team B selections are no longer on that roster.")

        if not team_one_players or not team_two_players:
            raise forms.ValidationError("Select at least one player from each team.")

        return cleaned_data

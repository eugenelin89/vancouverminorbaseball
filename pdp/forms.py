from django import forms
from django.forms import inlineformset_factory

from pdp.models import (
    AssignmentSourceType,
    DevelopmentGoal,
    DevelopmentLogType,
    DrillResource,
    EndOfSeasonReport,
    EndOfSeasonReportItem,
    EvaluationEventType,
    EvaluationImportTemplate,
    GoalStatus,
    PlayerDevelopmentLog,
    PlayerDrillAssignment,
    Season,
)
from pdp.services.imports import build_column_choices, deserialize_preview, serialize_preview


class WorkbookUploadForm(forms.Form):
    workbook = forms.FileField(help_text="Upload a CSV or XLSX workbook.")
    season = forms.ModelChoiceField(queryset=Season.objects.order_by("-year", "name"))
    event_name = forms.CharField(max_length=140)
    evaluated_on = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    event_type = forms.ChoiceField(choices=EvaluationEventType.choices)
    template = forms.ModelChoiceField(
        queryset=EvaluationImportTemplate.objects.filter(is_active=True).order_by("name"),
        required=False,
    )
    create_missing_players = forms.BooleanField(required=False, initial=True)
    provision_accounts = forms.BooleanField(required=False, initial=False)


class WorkbookMappingForm(forms.Form):
    preview_payload = forms.CharField(widget=forms.HiddenInput())
    season_id = forms.IntegerField(widget=forms.HiddenInput())
    event_name = forms.CharField(widget=forms.HiddenInput())
    evaluated_on = forms.CharField(widget=forms.HiddenInput())
    event_type = forms.CharField(widget=forms.HiddenInput())
    template_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    create_missing_players = forms.BooleanField(required=False)
    provision_accounts = forms.BooleanField(required=False)

    full_name_column = forms.ChoiceField(required=False)
    first_name_column = forms.ChoiceField(required=False)
    last_name_column = forms.ChoiceField(required=False)
    email_column = forms.ChoiceField(required=False)
    external_id_column = forms.ChoiceField(required=False)
    category_column = forms.ChoiceField(required=False)
    metric_columns = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    summary_columns = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    ranking_columns = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    save_as_template = forms.BooleanField(required=False)
    template_name = forms.CharField(max_length=140, required=False)

    def __init__(self, *args, **kwargs):
        preview_payload = kwargs.pop("preview_payload", "")
        super().__init__(*args, **kwargs)
        empty_choices = [("", "---------")]
        if preview_payload:
            preview = deserialize_preview(preview_payload)
            column_choices = build_column_choices(preview)
            self.fields["preview_payload"].initial = preview_payload
            for field_name in [
                "full_name_column",
                "first_name_column",
                "last_name_column",
                "email_column",
                "external_id_column",
                "category_column",
            ]:
                self.fields[field_name].choices = empty_choices + column_choices
            for field_name in ["metric_columns", "summary_columns", "ranking_columns"]:
                self.fields[field_name].choices = column_choices
            if not self.is_bound:
                recommended_metrics = []
                for key, label in column_choices:
                    lowered = label.lower()
                    if not any(term in lowered for term in ["name", "email", "category", "summary", "comment"]):
                        recommended_metrics.append(key)
                self.initial.setdefault("metric_columns", recommended_metrics[:12])
        else:
            for field_name in self.fields:
                if hasattr(self.fields[field_name], "choices"):
                    self.fields[field_name].choices = empty_choices

    def clean(self):
        cleaned_data = super().clean()
        full_name = cleaned_data.get("full_name_column")
        first_name = cleaned_data.get("first_name_column")
        last_name = cleaned_data.get("last_name_column")
        if not full_name and not (first_name and last_name):
            raise forms.ValidationError("Map either a full-name column or both first and last name columns.")
        if cleaned_data.get("save_as_template") and not cleaned_data.get("template_name"):
            raise forms.ValidationError("Enter a template name to save this mapping.")
        return cleaned_data

    def build_mapping_config(self):
        return {
            "season_id": self.cleaned_data["season_id"],
            "event_name": self.cleaned_data["event_name"],
            "evaluated_on": self.cleaned_data["evaluated_on"],
            "event_type": self.cleaned_data["event_type"],
            "template_id": self.cleaned_data.get("template_id") or "",
            "create_missing_players": self.cleaned_data.get("create_missing_players", False),
            "identity": {
                "full_name_column": self.cleaned_data.get("full_name_column", ""),
                "first_name_column": self.cleaned_data.get("first_name_column", ""),
                "last_name_column": self.cleaned_data.get("last_name_column", ""),
                "email_column": self.cleaned_data.get("email_column", ""),
                "external_id_column": self.cleaned_data.get("external_id_column", ""),
            },
            "category_column": self.cleaned_data.get("category_column", ""),
            "metric_columns": self.cleaned_data.get("metric_columns", []),
            "summary_columns": self.cleaned_data.get("summary_columns", []),
            "ranking_columns": self.cleaned_data.get("ranking_columns", []),
        }


class DevelopmentLogForm(forms.ModelForm):
    occurred_at = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))

    class Meta:
        model = PlayerDevelopmentLog
        fields = ["log_type", "title", "note", "skill_tags", "visibility", "occurred_at"]
        widgets = {
            "note": forms.Textarea(attrs={"rows": 4}),
            "skill_tags": forms.TextInput(attrs={"placeholder": "hitting, balance, command"}),
        }


class GoalForm(forms.ModelForm):
    class Meta:
        model = DevelopmentGoal
        fields = [
            "title",
            "category",
            "description",
            "status",
            "target_metric_key",
            "target_value",
            "target_unit",
            "due_date",
            "progress_notes",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "progress_notes": forms.Textarea(attrs={"rows": 3}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class DrillAssignmentForm(forms.ModelForm):
    class Meta:
        model = PlayerDrillAssignment
        fields = ["drill_resource", "source_type", "notes", "due_date"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = EndOfSeasonReport
        fields = [
            "summary",
            "strengths",
            "development_opportunities",
            "offseason_focus",
            "overall_rating",
            "overall_comments",
            "is_final",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "strengths": forms.Textarea(attrs={"rows": 3}),
            "development_opportunities": forms.Textarea(attrs={"rows": 3}),
            "offseason_focus": forms.Textarea(attrs={"rows": 3}),
            "overall_comments": forms.Textarea(attrs={"rows": 4}),
        }


ReportItemFormSet = inlineformset_factory(
    EndOfSeasonReport,
    EndOfSeasonReportItem,
    fields=["category", "rating_value", "rubric_rating", "text_feedback", "display_order"],
    extra=0,
    can_delete=False,
    widgets={
        "text_feedback": forms.Textarea(attrs={"rows": 2}),
    },
)

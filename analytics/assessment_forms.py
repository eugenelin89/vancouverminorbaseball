from django import forms

from analytics.models import RESPONSE_TYPE_RATING_1_5, RESPONSE_TYPE_TEXT
from analytics.services.coach_assessment_service import responses_by_question
from analytics.services.question_service import get_active_questions


class CoachAssessmentForm(forms.Form):
    def __init__(
        self, *args, question_set, observation=None, require_required=False, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.question_set = question_set
        self.observation = observation
        self.require_required = require_required
        self.questions = list(get_active_questions(question_set))
        existing_responses = responses_by_question(observation) if observation else {}
        rubric_labels = question_set.rubric.get("labels", {})

        for question in self.questions:
            field_name = self.field_name(question)
            required = question.is_required if require_required else False
            field_label = (
                question.prompt
                if question.is_required
                else f"{question.prompt} (Optional)"
            )
            initial = self.initial_for_question(
                question, existing_responses.get(question.id)
            )
            if question.response_type == RESPONSE_TYPE_RATING_1_5:
                choices = [("", "---------")]
                for value in range(1, 6):
                    choice_label = rubric_labels.get(str(value), str(value))
                    choices.append((value, f"{value} - {choice_label}"))
                self.fields[field_name] = forms.TypedChoiceField(
                    choices=choices,
                    coerce=int,
                    empty_value=None,
                    required=required,
                    label=field_label,
                    help_text=question.help_text,
                )
            elif question.response_type == RESPONSE_TYPE_TEXT:
                self.fields[field_name] = forms.CharField(
                    required=required,
                    label=field_label,
                    help_text=question.help_text,
                    widget=forms.Textarea(attrs={"rows": 4}),
                )
            else:
                self.fields[field_name] = forms.CharField(
                    required=False,
                    label=field_label,
                    disabled=True,
                )
            self.fields[field_name].initial = initial

    @staticmethod
    def field_name(question):
        return f"question_{question.id}"

    @staticmethod
    def initial_for_question(question, response):
        if not response:
            return None
        if question.response_type == RESPONSE_TYPE_RATING_1_5:
            return (
                int(response.numeric_value)
                if response.numeric_value is not None
                else None
            )
        if question.response_type == RESPONSE_TYPE_TEXT:
            return response.text_value
        return response.raw_value

    def response_payload(self):
        payload = []
        for question in self.questions:
            value = self.cleaned_data.get(self.field_name(question))
            payload.append({"question": question, "value": value})
        return payload

    def question_groups(self):
        groups = []
        group_lookup = {}
        for question in self.questions:
            category = question.category or "Questions"
            if category not in group_lookup:
                group = {"category": category, "questions": []}
                group_lookup[category] = group
                groups.append(group)
            group_lookup[category]["questions"].append(
                {
                    "question": question,
                    "field": self[self.field_name(question)],
                }
            )
        return groups

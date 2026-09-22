"""CSV export of submitted evaluations for Django staff."""

import csv

from django.core.exceptions import PermissionDenied
from django.utils import timezone

from analytics.services.evaluation_review_service import (
    parse_evaluation_review_filters,
    submitted_evaluation_queryset,
)
from analytics.services.permissions import can_export_submitted_evaluations

EXPORT_HEADERS = (
    "observation_id",
    "submitted_at",
    "player_id",
    "player_name",
    "season",
    "team",
    "division",
    "cycle_id",
    "cycle",
    "evaluation_type",
    "evaluator_id",
    "evaluator_name",
    "evaluator_role",
    "question_set",
    "question_set_version",
    "question_key",
    "question_category",
    "question_prompt",
    "response_type",
    "numeric_value",
    "text_value",
    "boolean_value",
    "selected_choice",
    "unit",
    "observation_notes",
)


class _Echo:
    def write(self, value):
        return value


def _safe_csv_cell(value):
    text = "" if value is None else str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def _observation_fields(observation):
    evaluator = observation.evaluator
    return (
        observation.id,
        (
            timezone.localtime(observation.submitted_at).isoformat()
            if observation.submitted_at
            else ""
        ),
        observation.player_id,
        observation.player.display_name,
        observation.season_name_snapshot
        or (observation.season.name if observation.season_id else "Legacy / No Season"),
        observation.player_team_name_snapshot or observation.player.team_name,
        observation.player_division_snapshot or observation.player.division,
        observation.evaluation_cycle_id,
        observation.evaluation_cycle.name,
        observation.evaluation_perspective_label,
        evaluator.id if evaluator else "",
        (evaluator.get_full_name() or evaluator.username) if evaluator else "",
        observation.evaluator_role_name or "Evaluator",
        observation.question_set.name,
        observation.question_set.version,
    )


def _export_rows(queryset):
    yield EXPORT_HEADERS
    for observation in queryset.iterator(chunk_size=200):
        fields = _observation_fields(observation)
        responses = observation.responses.all()
        if not responses:
            yield (*fields, *(("",) * 9), observation.notes)
            continue
        for response in responses:
            question = response.question
            yield (
                *fields,
                question.key,
                question.category,
                question.prompt,
                response.response_type,
                response.numeric_value,
                response.text_value,
                response.boolean_value,
                response.selected_choice,
                response.unit,
                observation.notes,
            )


def _csv_lines(queryset):
    writer = csv.writer(_Echo(), lineterminator="\r\n")
    yield "\ufeff"
    for row in _export_rows(queryset):
        yield writer.writerow([_safe_csv_cell(value) for value in row])


def export_submitted_evaluations_csv(user, params):
    """Return UTF-8 CSV lines using the same filters as the review page."""
    if not can_export_submitted_evaluations(user):
        raise PermissionDenied("You cannot export submitted evaluations.")
    filters = parse_evaluation_review_filters(params)
    queryset = (
        submitted_evaluation_queryset(filters)
        .select_related("question_set")
        .prefetch_related("responses__question")
    )
    return _csv_lines(queryset)

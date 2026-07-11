from __future__ import annotations

from dataclasses import dataclass

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.dateparse import parse_date

from analytics.models import (
    EVALUATION_PERSPECTIVE_CHOICES,
    OBSERVATION_STATUS_SUBMITTED,
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    EvaluationCycle,
    EvaluatorRole,
    Observation,
)
from analytics.services.permissions import can_review_submitted_evaluations, can_view_evaluation_review_detail


@dataclass(frozen=True)
class EvaluationReviewFilters:
    q: str = ""
    player: str = ""
    evaluator: str = ""
    evaluator_role: str = ""
    perspective: str = ""
    team: str = ""
    division: str = ""
    cycle: str = ""
    submitted_from: str = ""
    submitted_to: str = ""


@dataclass(frozen=True)
class EvaluationReviewRow:
    observation_id: int
    player_name: str
    player_team: str
    player_division: str
    evaluator_name: str
    evaluator_role_name: str
    evaluation_perspective_label: str
    cycle_name: str
    submitted_at: object


@dataclass(frozen=True)
class EvaluationReviewQuestionResponse:
    question_prompt: str
    category: str
    numeric_value: object = None
    text_value: str = ""


@dataclass(frozen=True)
class EvaluationReviewDetail:
    observation_id: int
    player_name: str
    player_team: str
    player_division: str
    evaluator_name: str
    evaluator_role_name: str
    evaluation_perspective_label: str
    cycle_name: str
    submitted_at: object
    responses: list[EvaluationReviewQuestionResponse]


@dataclass(frozen=True)
class EvaluationReviewList:
    filters: EvaluationReviewFilters
    rows: list[EvaluationReviewRow]
    total_count: int
    cycles: object
    evaluator_roles: object
    perspective_choices: object


def parse_evaluation_review_filters(params) -> EvaluationReviewFilters:
    return EvaluationReviewFilters(
        q=(params.get("q") or "").strip(),
        player=(params.get("player") or "").strip(),
        evaluator=(params.get("evaluator") or "").strip(),
        evaluator_role=(params.get("evaluator_role") or "").strip(),
        perspective=(params.get("perspective") or "").strip(),
        team=(params.get("team") or "").strip(),
        division=(params.get("division") or "").strip(),
        cycle=(params.get("cycle") or "").strip(),
        submitted_from=(params.get("submitted_from") or "").strip(),
        submitted_to=(params.get("submitted_to") or "").strip(),
    )


def _display_user(user) -> str:
    if not user:
        return "Unknown evaluator"
    return user.get_full_name() or user.username


def submitted_evaluation_queryset(filters: EvaluationReviewFilters | None = None):
    queryset = (
        Observation.objects.select_related("player", "evaluation_cycle", "evaluator", "evaluator_role")
        .filter(
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
            status=OBSERVATION_STATUS_SUBMITTED,
        )
        .order_by("-submitted_at", "-created_at", "-id")
    )
    if filters is None:
        return queryset

    if filters.q:
        queryset = queryset.filter(
            Q(player__first_name__icontains=filters.q)
            | Q(player__last_name__icontains=filters.q)
            | Q(player__preferred_name__icontains=filters.q)
        )
    if filters.player.isdigit():
        queryset = queryset.filter(player_id=int(filters.player))
    if filters.evaluator:
        if filters.evaluator.isdigit():
            queryset = queryset.filter(evaluator_id=int(filters.evaluator))
        else:
            queryset = queryset.filter(evaluator__username__icontains=filters.evaluator)
    if filters.evaluator_role:
        queryset = queryset.filter(evaluator_role_key=filters.evaluator_role)
    if filters.perspective:
        queryset = queryset.filter(evaluation_perspective=filters.perspective)
    if filters.team:
        queryset = queryset.filter(player__team_name__icontains=filters.team)
    if filters.division:
        queryset = queryset.filter(player__division__icontains=filters.division)
    if filters.cycle.isdigit():
        queryset = queryset.filter(evaluation_cycle_id=int(filters.cycle))

    submitted_from = parse_date(filters.submitted_from)
    if submitted_from:
        queryset = queryset.filter(submitted_at__date__gte=submitted_from)
    submitted_to = parse_date(filters.submitted_to)
    if submitted_to:
        queryset = queryset.filter(submitted_at__date__lte=submitted_to)

    return queryset


def get_evaluation_review_list(user, params) -> EvaluationReviewList:
    if not can_review_submitted_evaluations(user):
        raise PermissionDenied("You cannot review submitted evaluations.")
    filters = parse_evaluation_review_filters(params)
    queryset = submitted_evaluation_queryset(filters)
    rows = [
        EvaluationReviewRow(
            observation_id=observation.id,
            player_name=observation.player.display_name,
            player_team=observation.player.team_name,
            player_division=observation.player.division,
            evaluator_name=_display_user(observation.evaluator),
            evaluator_role_name=observation.evaluator_role_name or "Evaluator",
            evaluation_perspective_label=observation.evaluation_perspective_label,
            cycle_name=observation.evaluation_cycle.name,
            submitted_at=observation.submitted_at,
        )
        for observation in queryset
    ]
    return EvaluationReviewList(
        filters=filters,
        rows=rows,
        total_count=len(rows),
        cycles=EvaluationCycle.objects.filter(is_active=True).order_by("-starts_on", "-created_at", "name"),
        evaluator_roles=EvaluatorRole.objects.filter(is_active=True).order_by("name"),
        perspective_choices=EVALUATION_PERSPECTIVE_CHOICES,
    )


def get_evaluation_review_detail(user, observation_id: int) -> EvaluationReviewDetail:
    observation = submitted_evaluation_queryset().get(pk=observation_id)
    if not can_view_evaluation_review_detail(user, observation):
        raise PermissionDenied("You cannot review this evaluation.")
    responses = [
        EvaluationReviewQuestionResponse(
            question_prompt=response.question.prompt,
            category=response.question.category or "Questions",
            numeric_value=response.numeric_value,
            text_value=response.text_value,
        )
        for response in observation.responses.select_related("question").order_by(
            "question__display_order",
            "question_id",
            "id",
        )
    ]
    return EvaluationReviewDetail(
        observation_id=observation.id,
        player_name=observation.player.display_name,
        player_team=observation.player.team_name,
        player_division=observation.player.division,
        evaluator_name=_display_user(observation.evaluator),
        evaluator_role_name=observation.evaluator_role_name or "Evaluator",
        evaluation_perspective_label=observation.evaluation_perspective_label,
        cycle_name=observation.evaluation_cycle.name,
        submitted_at=observation.submitted_at,
        responses=responses,
    )

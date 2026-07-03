from __future__ import annotations

from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from analytics.models import (
    OBSERVATION_STATUS_DRAFT,
    OBSERVATION_STATUS_REOPENED,
    OBSERVATION_STATUS_SUBMITTED,
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    EvaluationCycle,
    Observation,
    ObservationQuestionSet,
)
from analytics.services.observation_service import create_coach_assessment_observation
from analytics.services.question_service import get_active_questions, get_coach_assessment_type, get_question_set_for_cycle
from players.models import Player


@dataclass
class PlayerAssessmentStatus:
    player: Player
    observation: Observation | None
    status: str


def get_active_coach_assessment_cycle(cycle_id: int | None = None) -> EvaluationCycle | None:
    queryset = EvaluationCycle.objects.filter(is_active=True).order_by("-starts_on", "-created_at", "name")
    if cycle_id:
        return queryset.filter(pk=cycle_id).first()
    return queryset.filter(coach_assessment_question_set__observation_type__key=OBSERVATION_TYPE_COACH_ASSESSMENT).first()


def list_players_for_assessment(query: str = "", division: str = "", team: str = ""):
    players = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")
    if query:
        players = players.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(preferred_name__icontains=query))
    if division:
        players = players.filter(division__iexact=division)
    if team:
        players = players.filter(team_name__iexact=team)
    return players


def get_existing_coach_assessment(player: Player, cycle: EvaluationCycle, evaluator) -> Observation | None:
    return (
        Observation.objects.select_related("player", "evaluation_cycle", "question_set", "evaluator", "evaluator_role")
        .filter(
            player=player,
            evaluation_cycle=cycle,
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
            evaluator=evaluator,
        )
        .first()
    )


@transaction.atomic
def get_or_create_draft_coach_assessment(player: Player, cycle: EvaluationCycle, evaluator) -> Observation:
    existing = get_existing_coach_assessment(player, cycle, evaluator)
    if existing:
        return existing
    result = create_coach_assessment_observation(
        player=player,
        evaluation_cycle=cycle,
        evaluator=evaluator,
        question_set=get_question_set_for_cycle(cycle, get_coach_assessment_type()),
        status=OBSERVATION_STATUS_DRAFT,
    )
    return result.observation


def assessment_status_for_players(players, cycle: EvaluationCycle, evaluator) -> list[PlayerAssessmentStatus]:
    observations = {
        observation.player_id: observation
        for observation in Observation.objects.filter(
            player__in=players,
            evaluation_cycle=cycle,
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
            evaluator=evaluator,
        )
    }
    statuses = []
    for player in players:
        observation = observations.get(player.id)
        statuses.append(PlayerAssessmentStatus(player=player, observation=observation, status=observation.status if observation else "not_started"))
    return statuses


def responses_by_question(observation: Observation) -> dict[int, object]:
    return {response.question_id: response for response in observation.responses.select_related("question")}


def group_questions_for_display(question_set: ObservationQuestionSet):
    groups = []
    group_lookup = {}
    for question in get_active_questions(question_set):
        category = question.category or "Questions"
        if category not in group_lookup:
            group = {"category": category, "questions": []}
            group_lookup[category] = group
            groups.append(group)
        group_lookup[category]["questions"].append(question)
    return groups


@transaction.atomic
def reopen_observation(observation: Observation, actor) -> Observation:
    if observation.status != OBSERVATION_STATUS_SUBMITTED:
        raise ValidationError("Only submitted observations can be reopened.")
    locked_observation = Observation.objects.select_for_update().get(pk=observation.pk)
    locked_observation.status = OBSERVATION_STATUS_REOPENED
    locked_observation.save(update_fields=["status", "updated_at"])
    return locked_observation

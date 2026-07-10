from __future__ import annotations

from dataclasses import dataclass

from django.core.exceptions import PermissionDenied
from django.db import transaction

from accounts.services.link_service import get_self_linked_players
from analytics.models import (
    OBSERVATION_STATUS_SUBMITTED,
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    EvaluationCycle,
    Observation,
)
from analytics.services.coach_assessment_service import (
    assessment_status_for_players,
    get_active_coach_assessment_cycle,
    get_existing_coach_assessment,
    get_or_create_draft_coach_assessment,
    list_players_for_assessment,
)
from analytics.services.permissions import (
    can_evaluate_player,
    can_submit_evaluation,
    can_view_my_evaluation_detail,
    can_view_my_evaluations,
)
from players.models import Player


@dataclass(frozen=True)
class EvaluationTargetStatus:
    player: Player
    observation: Observation | None
    status: str
    can_evaluate: bool


@dataclass(frozen=True)
class EvaluationTargetList:
    cycle: EvaluationCycle | None
    player_statuses: list[EvaluationTargetStatus]
    query: str = ""
    division: str = ""
    team: str = ""


@dataclass(frozen=True)
class MyEvaluationSummary:
    observation_id: int
    player: Player
    evaluator_role_name: str
    submitted_at: object
    cycle_name: str


@dataclass(frozen=True)
class MyEvaluationQuestionResponse:
    question_prompt: str
    category: str
    numeric_value: object = None
    text_value: str = ""


@dataclass(frozen=True)
class MyEvaluationDetail:
    observation_id: int
    player: Player
    evaluator_role_name: str
    submitted_at: object
    cycle_name: str
    responses: list[MyEvaluationQuestionResponse]


def get_evaluation_target_list(user, params) -> EvaluationTargetList:
    """Return active player evaluation targets for an authenticated evaluator."""
    if not can_submit_evaluation(user):
        raise PermissionDenied("You cannot submit evaluations.")

    cycle = get_active_coach_assessment_cycle()
    query = (params.get("q") or "").strip()
    division = (params.get("division") or "").strip()
    team = (params.get("team") or "").strip()
    if not cycle:
        return EvaluationTargetList(cycle=None, player_statuses=[], query=query, division=division, team=team)

    players = list(list_players_for_assessment(query=query, division=division, team=team))
    statuses_by_player_id = {
        item.player.id: item for item in assessment_status_for_players(players, cycle, user)
    }
    player_statuses = [
        EvaluationTargetStatus(
            player=player,
            observation=statuses_by_player_id[player.id].observation,
            status=statuses_by_player_id[player.id].status,
            can_evaluate=can_evaluate_player(user, player),
        )
        for player in players
    ]
    return EvaluationTargetList(
        cycle=cycle,
        player_statuses=player_statuses,
        query=query,
        division=division,
        team=team,
    )


def get_existing_evaluation_for_player(user, player: Player, cycle: EvaluationCycle) -> Observation | None:
    """Return the evaluator's existing coach-assessment observation for a target player and cycle."""
    return get_existing_coach_assessment(player, cycle, user)


@transaction.atomic
def get_or_create_evaluation_for_player(user, player: Player, cycle: EvaluationCycle) -> Observation:
    """Return or create the evaluator's draft evaluation for a target player."""
    if not can_evaluate_player(user, player):
        raise PermissionDenied("You cannot evaluate this player.")
    existing = get_existing_evaluation_for_player(user, player, cycle)
    if existing and existing.status == OBSERVATION_STATUS_SUBMITTED:
        return existing
    return get_or_create_draft_coach_assessment(player, cycle, user)


def active_evaluation_cycle() -> EvaluationCycle | None:
    """Return the active evaluation cycle for player-facing evaluation submission."""
    return get_active_coach_assessment_cycle()


def self_linked_players_for_user(user) -> list[Player]:
    """Return active self-linked players for My Evaluations."""
    return list(get_self_linked_players(user).filter(is_active=True))


def get_my_evaluations(user, player: Player | None = None) -> tuple[list[Player], list[MyEvaluationSummary]]:
    """Return submitted evaluations about the current user's self-linked player records."""
    if player is not None and not can_view_my_evaluations(user, player=player):
        raise PermissionDenied("You cannot view evaluations for this player.")
    players = [player] if player is not None else self_linked_players_for_user(user)
    if not players:
        return [], []
    observations = (
        Observation.objects.select_related("player", "evaluation_cycle", "evaluator_role")
        .filter(
            player__in=players,
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
            status=OBSERVATION_STATUS_SUBMITTED,
        )
        .order_by("-submitted_at", "-created_at", "-id")
    )
    summaries = [
        MyEvaluationSummary(
            observation_id=observation.id,
            player=observation.player,
            evaluator_role_name=observation.evaluator_role_name or "Evaluator",
            submitted_at=observation.submitted_at,
            cycle_name=observation.evaluation_cycle.name,
        )
        for observation in observations
    ]
    return players, summaries


def get_my_evaluation_detail(user, observation_id: int) -> MyEvaluationDetail:
    """Return a player-safe submitted evaluation detail view."""
    observation = (
        Observation.objects.select_related("player", "evaluation_cycle", "evaluator_role")
        .get(pk=observation_id)
    )
    if not can_view_my_evaluation_detail(user, observation):
        raise PermissionDenied("You cannot view this evaluation.")
    responses = [
        MyEvaluationQuestionResponse(
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
    return MyEvaluationDetail(
        observation_id=observation.id,
        player=observation.player,
        evaluator_role_name=observation.evaluator_role_name or "Evaluator",
        submitted_at=observation.submitted_at,
        cycle_name=observation.evaluation_cycle.name,
        responses=responses,
    )

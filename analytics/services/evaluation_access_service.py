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
    list_memberships_for_assessment,
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
    player_roster_membership: object = None
    player_team: str = ""
    player_division: str = ""
    evaluation_perspective_label: str = ""


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
    evaluation_perspective_label: str
    evaluator_role_name: str
    submitted_at: object
    cycle_name: str


@dataclass(frozen=True)
class MyEvaluationQuestionResponse:
    question_prompt: str
    category: str
    is_required: bool
    numeric_value: object = None
    text_value: str = ""


@dataclass(frozen=True)
class MyEvaluationDetail:
    observation_id: int
    player: Player
    evaluation_perspective_label: str
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
        return EvaluationTargetList(
            cycle=None, player_statuses=[], query=query, division=division, team=team
        )

    targets = list(
        list_memberships_for_assessment(
            cycle, query=query, division=division, team=team
        )
    )
    player_statuses = [
        EvaluationTargetStatus(
            player=item.player,
            observation=item.observation,
            status=item.status,
            can_evaluate=item.status != "unavailable"
            and can_evaluate_player(user, item.player),
            player_roster_membership=item.player_roster_membership,
            player_team=item.player_team,
            player_division=item.player_division,
            evaluation_perspective_label=item.evaluation_perspective_label,
        )
        for item in assessment_status_for_players(targets, cycle, user)
    ]
    return EvaluationTargetList(
        cycle=cycle,
        player_statuses=player_statuses,
        query=query,
        division=division,
        team=team,
    )


def get_existing_evaluation_for_player(
    user, player: Player, cycle: EvaluationCycle
) -> Observation | None:
    """Return the evaluator's existing coach-assessment observation for a target player and cycle."""
    return get_existing_coach_assessment(player, cycle, user)


@transaction.atomic
def get_or_create_evaluation_for_player(
    user, player: Player, cycle: EvaluationCycle, player_roster_membership=None
) -> Observation:
    """Return or create the evaluator's draft evaluation for a target player."""
    if not can_evaluate_player(user, player):
        raise PermissionDenied("You cannot evaluate this player.")
    existing = get_existing_evaluation_for_player(user, player, cycle)
    if existing and existing.status == OBSERVATION_STATUS_SUBMITTED:
        return existing
    return get_or_create_draft_coach_assessment(
        player, cycle, user, player_roster_membership=player_roster_membership
    )


def active_evaluation_cycle() -> EvaluationCycle | None:
    """Return the active evaluation cycle for player-facing evaluation submission."""
    return get_active_coach_assessment_cycle()


def self_linked_players_for_user(user) -> list[Player]:
    """Return active self-linked players for My Evaluations."""
    return list(get_self_linked_players(user).filter(is_active=True))


def get_my_evaluations(
    user, player: Player | None = None
) -> tuple[list[Player], list[MyEvaluationSummary]]:
    """Return submitted evaluations about the current user's self-linked player records."""
    if player is not None and not can_view_my_evaluations(user, player=player):
        raise PermissionDenied("You cannot view evaluations for this player.")
    players = [player] if player is not None else self_linked_players_for_user(user)
    if not players:
        return [], []
    observations = (
        Observation.objects.select_related(
            "player", "evaluation_cycle", "evaluator_role"
        )
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
            evaluation_perspective_label=observation.evaluation_perspective_label,
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
        Observation.objects.select_related(
            "player", "evaluation_cycle", "evaluator_role", "question_set"
        )
        .prefetch_related("responses__question")
        .get(pk=observation_id)
    )
    if not can_view_my_evaluation_detail(user, observation):
        raise PermissionDenied("You cannot view this evaluation.")
    responses_by_question = {
        response.question_id: response for response in observation.responses.all()
    }
    responses = [
        MyEvaluationQuestionResponse(
            question_prompt=question.prompt,
            category=question.category or "Questions",
            is_required=question.is_required,
            numeric_value=(
                responses_by_question[question.id].numeric_value
                if question.id in responses_by_question
                else None
            ),
            text_value=(
                responses_by_question[question.id].text_value
                if question.id in responses_by_question
                else ""
            ),
        )
        for question in observation.question_set.questions.filter(
            is_active=True
        ).order_by("display_order", "id")
    ]
    return MyEvaluationDetail(
        observation_id=observation.id,
        player=observation.player,
        evaluation_perspective_label=observation.evaluation_perspective_label,
        evaluator_role_name=observation.evaluator_role_name or "Evaluator",
        submitted_at=observation.submitted_at,
        cycle_name=observation.evaluation_cycle.name,
        responses=responses,
    )

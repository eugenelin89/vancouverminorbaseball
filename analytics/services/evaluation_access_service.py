from __future__ import annotations

from dataclasses import dataclass

from django.core.exceptions import PermissionDenied
from django.db import transaction

from analytics.models import OBSERVATION_STATUS_SUBMITTED, EvaluationCycle, Observation
from analytics.services.coach_assessment_service import (
    assessment_status_for_players,
    get_active_coach_assessment_cycle,
    get_existing_coach_assessment,
    get_or_create_draft_coach_assessment,
    list_players_for_assessment,
)
from analytics.services.permissions import can_evaluate_player, can_submit_evaluation
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

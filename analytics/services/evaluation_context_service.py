from __future__ import annotations

from dataclasses import dataclass

from django.core.exceptions import ValidationError

from accounts.models import AccountRole
from accounts.services.role_service import role_for_user
from analytics.models import EVALUATION_PERSPECTIVE_COACH, OBSERVATION_STATUS_SUBMITTED, EvaluationCycle, Observation
from players.models import Player
from seasons.models import CoachSeasonAssignment, PlayerRosterMembership, Season


@dataclass(frozen=True)
class EvaluationSeasonContext:
    season: Season | None
    player_roster_membership: PlayerRosterMembership | None = None
    evaluator_coach_assignment: CoachSeasonAssignment | None = None
    season_name_snapshot: str = ""
    season_key_snapshot: str = ""
    player_team_name_snapshot: str = ""
    player_division_snapshot: str = ""
    evaluator_team_name_snapshot: str = ""
    evaluator_division_snapshot: str = ""
    evaluator_assignment_role_snapshot: str = ""


def _active_player_memberships(player: Player, season: Season):
    return (
        PlayerRosterMembership.objects.select_related("season_team", "season_team__season")
        .filter(player=player, season_team__season=season, is_active=True)
        .order_by("-is_primary", "-starts_on", "-created_at", "-id")
    )


def resolve_player_membership(
    *,
    player: Player,
    season: Season,
    player_roster_membership: PlayerRosterMembership | None = None,
) -> PlayerRosterMembership:
    """Resolve a target player's membership for an evaluation season without guessing ambiguous cases."""
    if player_roster_membership is not None:
        membership = PlayerRosterMembership.objects.select_related("season_team", "season_team__season").get(
            pk=player_roster_membership.pk
        )
        if membership.player_id != player.id:
            raise ValidationError("Selected player membership does not belong to this player.")
        if membership.season.id != season.id:
            raise ValidationError("Selected player membership does not belong to this evaluation season.")
        if not membership.is_active:
            raise ValidationError("Selected player membership is inactive.")
        return membership

    memberships = list(_active_player_memberships(player, season))
    if not memberships:
        raise ValidationError("This player is not on an active roster for the evaluation season.")
    primary_memberships = [membership for membership in memberships if membership.is_primary]
    if len(primary_memberships) == 1:
        return primary_memberships[0]
    if len(primary_memberships) > 1:
        raise ValidationError("This player has multiple primary memberships for the evaluation season.")
    if len(memberships) == 1:
        return memberships[0]
    raise ValidationError("This player has multiple active memberships for the evaluation season. Select a roster team.")


def resolve_evaluator_assignment(
    *,
    evaluator,
    season: Season,
    player_roster_membership: PlayerRosterMembership | None,
    evaluation_perspective: str,
    evaluator_coach_assignment: CoachSeasonAssignment | None = None,
) -> CoachSeasonAssignment | None:
    """Resolve a coach assignment snapshot for coach evaluations only."""
    if evaluator_coach_assignment is not None:
        assignment = CoachSeasonAssignment.objects.select_related("season_team", "season_team__season").get(
            pk=evaluator_coach_assignment.pk
        )
        if assignment.user_id != evaluator.id:
            raise ValidationError("Selected coach assignment does not belong to this evaluator.")
        if assignment.season.id != season.id:
            raise ValidationError("Selected coach assignment does not belong to this evaluation season.")
        if not assignment.is_active:
            raise ValidationError("Selected coach assignment is inactive.")
        return assignment

    if not evaluator or evaluation_perspective != EVALUATION_PERSPECTIVE_COACH:
        return None
    if role_for_user(evaluator) != AccountRole.COACH:
        return None

    assignments = list(
        CoachSeasonAssignment.objects.select_related("season_team", "season_team__season")
        .filter(user=evaluator, season_team__season=season, is_active=True)
        .order_by("-is_primary", "season_team__division", "season_team__name", "id")
    )
    if not assignments:
        return None
    if player_roster_membership:
        team_matches = [
            assignment
            for assignment in assignments
            if assignment.season_team_id == player_roster_membership.season_team_id
        ]
        if len(team_matches) == 1:
            return team_matches[0]
        if len(team_matches) > 1:
            raise ValidationError("This coach has multiple assignments for the player's team. Select a coach assignment.")
    if len(assignments) == 1:
        return assignments[0]
    primary_assignments = [assignment for assignment in assignments if assignment.is_primary]
    if len(primary_assignments) == 1:
        return primary_assignments[0]
    raise ValidationError("This coach has multiple active assignments for the evaluation season. Select a coach assignment.")


def resolve_evaluation_context(
    *,
    player: Player,
    evaluation_cycle: EvaluationCycle,
    evaluator=None,
    evaluation_perspective: str = "",
    player_roster_membership: PlayerRosterMembership | None = None,
    evaluator_coach_assignment: CoachSeasonAssignment | None = None,
    require_season: bool = True,
) -> EvaluationSeasonContext:
    """Resolve the season, roster membership, assignment, and display snapshots for an observation."""
    season = evaluation_cycle.season
    if season is None:
        if require_season:
            raise ValidationError("Evaluation cycle must have a season before this evaluation can be submitted.")
        return EvaluationSeasonContext(season=None)

    membership = resolve_player_membership(
        player=player,
        season=season,
        player_roster_membership=player_roster_membership,
    )
    assignment = resolve_evaluator_assignment(
        evaluator=evaluator,
        season=season,
        player_roster_membership=membership,
        evaluation_perspective=evaluation_perspective,
        evaluator_coach_assignment=evaluator_coach_assignment,
    )
    return EvaluationSeasonContext(
        season=season,
        player_roster_membership=membership,
        evaluator_coach_assignment=assignment,
        season_name_snapshot=season.name,
        season_key_snapshot=season.key,
        player_team_name_snapshot=membership.season_team.name,
        player_division_snapshot=membership.season_team.division,
        evaluator_team_name_snapshot=assignment.season_team.name if assignment else "",
        evaluator_division_snapshot=assignment.season_team.division if assignment else "",
        evaluator_assignment_role_snapshot=assignment.get_assignment_role_display() if assignment else "",
    )


def apply_evaluation_context(
    observation: Observation,
    context: EvaluationSeasonContext,
    *,
    refresh_snapshots: bool = False,
) -> Observation:
    """Apply resolved context to an observation, preserving submitted snapshots unless explicitly refreshed."""
    observation.season = context.season
    observation.player_roster_membership = context.player_roster_membership
    observation.evaluator_coach_assignment = context.evaluator_coach_assignment
    if observation.status != OBSERVATION_STATUS_SUBMITTED or refresh_snapshots:
        observation.season_name_snapshot = context.season_name_snapshot
        observation.season_key_snapshot = context.season_key_snapshot
        observation.player_team_name_snapshot = context.player_team_name_snapshot
        observation.player_division_snapshot = context.player_division_snapshot
        observation.evaluator_team_name_snapshot = context.evaluator_team_name_snapshot
        observation.evaluator_division_snapshot = context.evaluator_division_snapshot
        observation.evaluator_assignment_role_snapshot = context.evaluator_assignment_role_snapshot
    return observation


def observation_display_season(observation: Observation) -> str:
    return observation.season_name_snapshot or (observation.season.name if observation.season_id else "Legacy / No Season")


def observation_display_player_team(observation: Observation) -> str:
    return observation.player_team_name_snapshot or observation.player.team_name


def observation_display_player_division(observation: Observation) -> str:
    return observation.player_division_snapshot or observation.player.division

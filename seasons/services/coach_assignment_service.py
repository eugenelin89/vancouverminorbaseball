from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from seasons.models import CoachAssignmentRole, CoachSeasonAssignment, Season, SeasonTeam


def assignments_for_user(user, season: Season | None = None):
    queryset = CoachSeasonAssignment.objects.select_related("season_team", "season_team__season").filter(user=user)
    if season:
        queryset = queryset.filter(season_team__season=season)
    return queryset.order_by("-is_primary", "-is_active", "season_team__division", "season_team__name", "id")


def assignments_for_team(season_team: SeasonTeam):
    return (
        CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season")
        .filter(season_team=season_team)
        .order_by("-is_primary", "assignment_role", "user__last_name", "user__first_name", "id")
    )


def get_primary_assignment(user, season: Season) -> CoachSeasonAssignment | None:
    return (
        CoachSeasonAssignment.objects.select_related("season_team", "season_team__season")
        .filter(user=user, season_team__season=season, is_active=True, is_primary=True)
        .order_by("id")
        .first()
    )


@transaction.atomic
def create_assignment(
    *,
    user,
    season_team: SeasonTeam,
    assignment_role: str = CoachAssignmentRole.ASSISTANT_COACH,
    is_primary: bool = False,
    is_active: bool = True,
    starts_on=None,
    ends_on=None,
    source: str = "",
    source_identifier: str = "",
    metadata: dict | None = None,
) -> CoachSeasonAssignment:
    assignment = CoachSeasonAssignment(
        user=user,
        season_team=season_team,
        assignment_role=assignment_role,
        is_primary=False,
        is_active=is_active,
        starts_on=starts_on,
        ends_on=ends_on,
        source=source,
        source_identifier=source_identifier,
        metadata=metadata or {},
    )
    assignment.save()
    if is_primary:
        assignment = set_primary_assignment(assignment)
    return assignment


@transaction.atomic
def update_assignment(assignment: CoachSeasonAssignment, **updates) -> CoachSeasonAssignment:
    requested_primary = updates.pop("is_primary", None)
    for field, value in updates.items():
        setattr(assignment, field, value)
    if requested_primary is False:
        assignment.is_primary = False
    assignment.save()
    if requested_primary is True and not assignment.is_primary:
        assignment = set_primary_assignment(assignment)
    return assignment


@transaction.atomic
def set_primary_assignment(assignment: CoachSeasonAssignment) -> CoachSeasonAssignment:
    if not assignment.is_active:
        raise ValidationError("Only active assignments can be primary.")
    locked = CoachSeasonAssignment.objects.select_for_update().filter(
        user=assignment.user,
        season_team__season=assignment.season,
        is_active=True,
    )
    locked.exclude(pk=assignment.pk).filter(is_primary=True).update(is_primary=False)
    assignment = CoachSeasonAssignment.objects.select_for_update().get(pk=assignment.pk)
    assignment.is_primary = True
    assignment.save(update_fields=["is_primary", "updated_at"])
    return assignment


@transaction.atomic
def deactivate_assignment(
    assignment: CoachSeasonAssignment,
    *,
    ends_on=None,
) -> CoachSeasonAssignment:
    assignment.is_active = False
    assignment.is_primary = False
    if ends_on is not None:
        assignment.ends_on = ends_on
    assignment.save()
    return assignment

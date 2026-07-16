from __future__ import annotations

from django.db.models import Count, Q

from seasons.models import (
    CoachSeasonAssignment,
    PlayerRosterMembership,
    Season,
    SeasonTeam,
)


def clean_int(value: str | None) -> str | None:
    value = str(value or "").strip()
    return value if value.isdigit() else None


def season_list_queryset():
    return Season.objects.annotate(
        team_count=Count("teams", distinct=True),
        membership_count=Count("teams__player_memberships", distinct=True),
        assignment_count=Count("teams__coach_assignments", distinct=True),
    ).order_by("-starts_on", "name", "id")


def season_detail_team_queryset(season: Season):
    return season.teams.annotate(
        membership_count=Count("player_memberships", distinct=True),
        assignment_count=Count("coach_assignments", distinct=True),
    ).order_by("division", "name", "id")


def season_options_queryset():
    return Season.objects.order_by("-is_current", "-starts_on", "name")


def team_options_queryset():
    return SeasonTeam.objects.select_related("season").order_by(
        "-season__is_current",
        "season__name",
        "division",
        "name",
    )


def team_list_queryset(*, season_id: str | None = None):
    queryset = SeasonTeam.objects.select_related("season").annotate(
        membership_count=Count("player_memberships", distinct=True),
        assignment_count=Count("coach_assignments", distinct=True),
    )
    season_id = clean_int(season_id)
    if season_id:
        queryset = queryset.filter(season_id=season_id)
    return queryset.order_by(
        "-season__is_current", "season__name", "division", "name", "id"
    )


def membership_list_queryset(params):
    queryset = PlayerRosterMembership.objects.select_related(
        "player", "season_team", "season_team__season"
    )
    season_id = clean_int(params.get("season"))
    team_id = clean_int(params.get("team"))
    active = params.get("active")
    search = params.get("q", "").strip()
    if season_id:
        queryset = queryset.filter(season_team__season_id=season_id)
    if team_id:
        queryset = queryset.filter(season_team_id=team_id)
    if active == "yes":
        queryset = queryset.filter(is_active=True)
    elif active == "no":
        queryset = queryset.filter(is_active=False)
    if search:
        queryset = queryset.filter(
            Q(player__first_name__icontains=search)
            | Q(player__last_name__icontains=search)
        )
    return queryset.order_by(
        "-season_team__season__is_current",
        "season_team__season__name",
        "player__last_name",
        "player__first_name",
        "id",
    )


def player_history_membership_queryset(player):
    return (
        PlayerRosterMembership.objects.select_related(
            "season_team", "season_team__season"
        )
        .filter(player=player)
        .order_by(
            "-season_team__season__starts_on",
            "-season_team__season__is_current",
            "season_team__division",
            "season_team__name",
            "-starts_on",
            "id",
        )
    )


def assignment_list_queryset(params):
    queryset = CoachSeasonAssignment.objects.select_related(
        "user",
        "season_team",
        "season_team__season",
        "user__account_profile",
    )
    season_id = clean_int(params.get("season"))
    team_id = clean_int(params.get("team"))
    active = params.get("active")
    search = params.get("q", "").strip()
    if season_id:
        queryset = queryset.filter(season_team__season_id=season_id)
    if team_id:
        queryset = queryset.filter(season_team_id=team_id)
    if active == "yes":
        queryset = queryset.filter(is_active=True)
    elif active == "no":
        queryset = queryset.filter(is_active=False)
    if search:
        queryset = queryset.filter(
            Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__username__icontains=search)
        )
    return queryset.order_by(
        "-season_team__season__is_current",
        "season_team__season__name",
        "user__last_name",
        "user__first_name",
        "id",
    )


def coach_history_assignment_queryset(coach):
    return (
        CoachSeasonAssignment.objects.select_related(
            "season_team", "season_team__season"
        )
        .filter(user=coach)
        .order_by(
            "-season_team__season__starts_on",
            "-season_team__season__is_current",
            "season_team__division",
            "season_team__name",
            "-starts_on",
            "id",
        )
    )

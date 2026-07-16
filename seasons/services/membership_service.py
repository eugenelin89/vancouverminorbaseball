from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from players.models import Player
from seasons.models import PlayerRosterMembership, RosterStatus, Season, SeasonTeam


def memberships_for_player(player: Player, season: Season | None = None):
    queryset = PlayerRosterMembership.objects.select_related("season_team", "season_team__season").filter(player=player)
    if season:
        queryset = queryset.filter(season_team__season=season)
    return queryset.order_by("-is_primary", "-is_active", "season_team__division", "season_team__name", "id")


def get_primary_membership(player: Player, season: Season) -> PlayerRosterMembership | None:
    return (
        PlayerRosterMembership.objects.select_related("season_team", "season_team__season")
        .filter(player=player, season_team__season=season, is_active=True, is_primary=True)
        .order_by("id")
        .first()
    )


def get_current_membership(player: Player, season: Season) -> PlayerRosterMembership | None:
    primary = get_primary_membership(player, season)
    if primary:
        return primary
    return (
        PlayerRosterMembership.objects.select_related("season_team", "season_team__season")
        .filter(player=player, season_team__season=season, is_active=True)
        .order_by("-starts_on", "-created_at", "-id")
        .first()
    )


def current_team_division(player: Player, season: Season) -> tuple[str, str]:
    membership = get_current_membership(player, season)
    if not membership:
        return "", ""
    return membership.season_team.name, membership.season_team.division


@transaction.atomic
def create_membership(
    *,
    player: Player,
    season_team: SeasonTeam,
    status: str = RosterStatus.ACTIVE,
    jersey_number: str = "",
    is_primary: bool = False,
    is_active: bool = True,
    starts_on=None,
    ends_on=None,
    source: str = "",
    source_identifier: str = "",
    import_batch=None,
    metadata: dict | None = None,
    sync_player_fields: bool = False,
) -> PlayerRosterMembership:
    membership = PlayerRosterMembership(
        player=player,
        season_team=season_team,
        status=status,
        jersey_number=jersey_number,
        is_primary=False,
        is_active=is_active,
        starts_on=starts_on,
        ends_on=ends_on,
        source=source,
        source_identifier=source_identifier,
        import_batch=import_batch,
        metadata=metadata or {},
    )
    membership.save()
    if is_primary:
        membership = set_primary_membership(membership, sync_player_fields=sync_player_fields)
    elif sync_player_fields:
        sync_player_current_team_fields(player, season_team.season)
    return membership


@transaction.atomic
def update_membership(membership: PlayerRosterMembership, *, sync_player_fields: bool = False, **updates) -> PlayerRosterMembership:
    requested_primary = updates.pop("is_primary", None)
    for field, value in updates.items():
        setattr(membership, field, value)
    if requested_primary is False:
        membership.is_primary = False
    membership.save()
    if requested_primary is True and not membership.is_primary:
        membership = set_primary_membership(membership, sync_player_fields=sync_player_fields)
    elif sync_player_fields:
        sync_player_current_team_fields(membership.player, membership.season)
    return membership


@transaction.atomic
def set_primary_membership(
    membership: PlayerRosterMembership,
    *,
    sync_player_fields: bool = True,
) -> PlayerRosterMembership:
    if not membership.is_active:
        raise ValidationError("Only active memberships can be primary.")
    locked = PlayerRosterMembership.objects.select_for_update().filter(
        player=membership.player,
        season_team__season=membership.season,
        is_active=True,
    )
    locked.exclude(pk=membership.pk).filter(is_primary=True).update(is_primary=False)
    membership = PlayerRosterMembership.objects.select_for_update().get(pk=membership.pk)
    membership.is_primary = True
    membership.save(update_fields=["is_primary", "updated_at"])
    if sync_player_fields:
        sync_player_current_team_fields(membership.player, membership.season)
    return membership


@transaction.atomic
def deactivate_membership(
    membership: PlayerRosterMembership,
    *,
    status: str = RosterStatus.INACTIVE,
    ends_on=None,
    sync_player_fields: bool = False,
) -> PlayerRosterMembership:
    membership.is_active = False
    membership.is_primary = False
    membership.status = status
    if ends_on is not None:
        membership.ends_on = ends_on
    membership.save()
    if sync_player_fields:
        sync_player_current_team_fields(membership.player, membership.season)
    return membership


@transaction.atomic
def transfer_player(
    *,
    player: Player,
    to_season_team: SeasonTeam,
    from_membership: PlayerRosterMembership | None = None,
    transfer_date=None,
    source: str = "",
    source_identifier: str = "",
    metadata: dict | None = None,
) -> PlayerRosterMembership:
    season = to_season_team.season
    if from_membership is None:
        from_membership = get_primary_membership(player, season)
    if from_membership:
        deactivate_membership(
            from_membership,
            status=RosterStatus.TRANSFERRED,
            ends_on=transfer_date,
            sync_player_fields=False,
        )
    return create_membership(
        player=player,
        season_team=to_season_team,
        status=RosterStatus.ACTIVE,
        is_primary=True,
        is_active=True,
        starts_on=transfer_date,
        source=source,
        source_identifier=source_identifier,
        metadata=metadata,
        sync_player_fields=True,
    )


def sync_player_current_team_fields(player: Player, season: Season | None = None, *, clear_when_missing: bool = False) -> Player:
    """Explicitly sync temporary Player team/division fields from the active primary membership."""
    if season is None:
        primary = (
            PlayerRosterMembership.objects.select_related("season_team", "season_team__season")
            .filter(player=player, is_active=True, is_primary=True, season_team__season__is_current=True)
            .order_by("-season_team__season__starts_on", "-created_at", "-id")
            .first()
        )
    else:
        primary = get_primary_membership(player, season)

    if primary:
        player.team_name = primary.season_team.name
        player.division = primary.season_team.division
        player.save(update_fields=["team_name", "division", "updated_at"])
    elif clear_when_missing:
        player.team_name = ""
        player.division = ""
        player.save(update_fields=["team_name", "division", "updated_at"])
    return player

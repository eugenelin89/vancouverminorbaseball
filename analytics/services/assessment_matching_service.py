from __future__ import annotations

from dataclasses import dataclass

from players.models import Player, PlayerAlias, PlayerSourceIdentifier
from players.models import normalize_lookup_value as normalize_player_lookup_value
from seasons.models import PlayerRosterMembership

MATCH_EXACT_IDENTIFIER = "exact_identifier"
MATCH_EXACT_NAME = "exact_name"
MATCH_ALIAS = "alias"
MATCH_UNMATCHED = "unmatched"
MATCH_AMBIGUOUS = "ambiguous"


@dataclass(frozen=True)
class AssessmentMatchResult:
    status: str
    player: Player | None = None
    roster_membership: PlayerRosterMembership | None = None
    candidates: tuple[Player, ...] = ()
    reason: str = ""

    @property
    def is_committable(self) -> bool:
        return self.player is not None and self.status != MATCH_AMBIGUOUS


def normalize_assessment_name(value: str) -> str:
    """Normalize workbook player names for exact and alias matching."""
    return normalize_player_lookup_value(
        str(value or "").replace("“", '"').replace("”", '"').replace("’", "'")
    )


def _primary_roster_membership(player: Player, event) -> PlayerRosterMembership | None:
    return (
        player.roster_memberships.select_related("season_team", "season_team__season")
        .filter(season_team__season=event.season, is_active=True)
        .order_by("-is_primary", "season_team__name", "id")
        .first()
    )


def _result_for_players(
    players: list[Player], *, event, status: str, reason: str
) -> AssessmentMatchResult:
    unique_players = list({player.pk: player for player in players}.values())
    if len(unique_players) == 1:
        player = unique_players[0]
        return AssessmentMatchResult(
            status=status,
            player=player,
            roster_membership=_primary_roster_membership(player, event),
            candidates=(player,),
            reason=reason,
        )
    if len(unique_players) > 1:
        return AssessmentMatchResult(
            status=MATCH_AMBIGUOUS,
            candidates=tuple(unique_players),
            reason="Multiple players matched the workbook identity.",
        )
    return AssessmentMatchResult(status=MATCH_UNMATCHED, reason=reason)


def match_player_for_assessment(
    *,
    raw_name: str,
    event,
    source_identifiers: dict[str, str] | None = None,
) -> AssessmentMatchResult:
    """Match a workbook row to an existing canonical player without fuzzy commits."""
    source_identifiers = source_identifiers or {}
    identifier_players = []
    for identifier_type, identifier_value in source_identifiers.items():
        if not identifier_value:
            continue
        identifiers = PlayerSourceIdentifier.objects.select_related("player").filter(
            identifier_type=normalize_player_lookup_value(identifier_type),
            identifier_value=normalize_player_lookup_value(identifier_value),
        )
        identifier_players.extend(identifier.player for identifier in identifiers)
    if identifier_players:
        return _result_for_players(
            identifier_players,
            event=event,
            status=MATCH_EXACT_IDENTIFIER,
            reason="Matched by source identifier.",
        )

    normalized_name = normalize_assessment_name(raw_name)
    if not normalized_name:
        return AssessmentMatchResult(
            status=MATCH_UNMATCHED, reason="Missing player name."
        )

    name_players = [
        player
        for player in Player.objects.filter(is_active=True)
        if normalize_assessment_name(player.display_name) == normalized_name
        or normalize_assessment_name(player.full_name) == normalized_name
    ]
    if name_players:
        return _result_for_players(
            name_players,
            event=event,
            status=MATCH_EXACT_NAME,
            reason="Matched by exact player name.",
        )

    aliases = PlayerAlias.objects.select_related("player").filter(
        normalized_alias=normalized_name,
        player__is_active=True,
    )
    return _result_for_players(
        [alias.player for alias in aliases],
        event=event,
        status=MATCH_ALIAS,
        reason="Matched by player alias." if aliases else "No exact player match.",
    )

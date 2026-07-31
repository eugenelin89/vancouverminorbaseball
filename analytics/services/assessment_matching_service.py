from __future__ import annotations

from dataclasses import dataclass

from django.db.models import CharField, F, Q, Value
from django.db.models.functions import Coalesce, Concat, Lower, Trim

from players.models import Player, PlayerAlias, PlayerSourceIdentifier
from players.models import normalize_lookup_value as normalize_player_lookup_value
from seasons.models import PlayerRosterMembership, normalize_lookup_value

MATCH_EXACT_IDENTIFIER = "exact_identifier"
MATCH_EXACT_ROSTER_NAME = "exact_roster_name"
MATCH_EXACT_ROSTER_ALIAS = "exact_roster_alias"
MATCH_EXACT_GLOBAL_NAME = "exact_global_name"
MATCH_EXACT_GLOBAL_ALIAS = "exact_global_alias"
MATCH_UNMATCHED = "unmatched"
MATCH_AMBIGUOUS = "ambiguous"


@dataclass(frozen=True)
class AssessmentMatchCandidate:
    player: Player
    birth_year: int | None
    team: str
    division: str


@dataclass(frozen=True)
class AssessmentMatchResult:
    status: str
    player: Player | None = None
    roster_membership: PlayerRosterMembership | None = None
    candidates: tuple[Player, ...] = ()
    candidate_contexts: tuple[AssessmentMatchCandidate, ...] = ()
    reason: str = ""

    @property
    def is_committable(self) -> bool:
        return self.player is not None and self.status != MATCH_AMBIGUOUS


def normalize_assessment_name(value: str) -> str:
    """Normalize workbook player names for exact and alias matching."""
    return normalize_player_lookup_value(
        str(value or "").replace("“", '"').replace("”", '"').replace("’", "'")
    )


def _roster_memberships(event, *, player_ids=None):
    memberships = PlayerRosterMembership.objects.select_related(
        "player", "season_team", "season_team__season"
    ).filter(
        season_team__season=event.season,
        player__is_active=True,
        is_active=True,
    )
    if event.division:
        memberships = memberships.filter(
            season_team__normalized_division=normalize_lookup_value(event.division)
        )
    if player_ids is not None:
        memberships = memberships.filter(player_id__in=player_ids)
    return memberships.order_by("-is_primary", "season_team__name", "id")


def _primary_roster_membership(player: Player, event) -> PlayerRosterMembership | None:
    return _roster_memberships(event, player_ids=[player.pk]).first()


def _candidate_context(player: Player, event) -> AssessmentMatchCandidate:
    membership = _primary_roster_membership(player, event)
    return AssessmentMatchCandidate(
        player=player,
        birth_year=player.birth_year,
        team=membership.season_team.name if membership else player.team_name,
        division=(membership.season_team.division if membership else player.division),
    )


def _result_for_players(
    players, *, event, status: str, reason: str
) -> AssessmentMatchResult:
    unique_players = list({player.pk: player for player in players}.values())
    contexts = tuple(_candidate_context(player, event) for player in unique_players)
    if len(unique_players) == 1:
        player = unique_players[0]
        return AssessmentMatchResult(
            status=status,
            player=player,
            roster_membership=_primary_roster_membership(player, event),
            candidates=(player,),
            candidate_contexts=contexts,
            reason=reason,
        )
    if len(unique_players) > 1:
        return AssessmentMatchResult(
            status=MATCH_AMBIGUOUS,
            candidates=tuple(unique_players),
            candidate_contexts=contexts,
            reason="Multiple exact player matches require staff selection.",
        )
    return AssessmentMatchResult(status=MATCH_UNMATCHED, reason=reason)


def _players_with_exact_name(normalized_name: str, *, player_ids=None):
    queryset = Player.objects.filter(is_active=True)
    if player_ids is not None:
        queryset = queryset.filter(pk__in=player_ids)
    full_name = Lower(
        Trim(
            Concat(
                F("first_name"),
                Value(" "),
                F("last_name"),
                output_field=CharField(),
            )
        )
    )
    display_name = Lower(
        Trim(
            Concat(
                Coalesce("preferred_name", "first_name"),
                Value(" "),
                F("last_name"),
                output_field=CharField(),
            )
        )
    )
    return queryset.annotate(
        assessment_full_name=full_name,
        assessment_display_name=display_name,
    ).filter(
        Q(assessment_full_name=normalized_name)
        | Q(assessment_display_name=normalized_name)
    )


def _roster_player_ids(event) -> list[int]:
    return list(
        _roster_memberships(event).values_list("player_id", flat=True).distinct()
    )


def _identifier_players(source_identifiers: list[dict]) -> list[Player]:
    players = []
    for source_identifier in source_identifiers:
        source = normalize_player_lookup_value(source_identifier.get("source", ""))
        identifier_type = normalize_player_lookup_value(
            source_identifier.get("identifier_type", "")
        )
        identifier_value = normalize_player_lookup_value(
            source_identifier.get("identifier_value", "")
        )
        if not source or not identifier_type or not identifier_value:
            continue
        identifiers = PlayerSourceIdentifier.objects.select_related("player").filter(
            source=source,
            identifier_type=identifier_type,
            identifier_value=identifier_value,
            player__is_active=True,
        )
        players.extend(identifier.player for identifier in identifiers)
    return players


def match_player_for_assessment(
    *,
    raw_name: str,
    event,
    source_identifiers: list[dict] | None = None,
) -> AssessmentMatchResult:
    """Match a row conservatively without creating players or using fuzzy matches."""
    identifier_players = _identifier_players(source_identifiers or [])
    if identifier_players:
        return _result_for_players(
            identifier_players,
            event=event,
            status=MATCH_EXACT_IDENTIFIER,
            reason="Matched by exact namespaced source identifier.",
        )

    normalized_name = normalize_assessment_name(raw_name)
    if not normalized_name:
        return AssessmentMatchResult(
            status=MATCH_UNMATCHED, reason="Missing player identity."
        )

    roster_ids = _roster_player_ids(event)
    roster_name_players = list(
        _players_with_exact_name(normalized_name, player_ids=roster_ids)
    )
    if roster_name_players:
        return _result_for_players(
            roster_name_players,
            event=event,
            status=MATCH_EXACT_ROSTER_NAME,
            reason="Matched by exact name in the event season and division roster.",
        )

    roster_alias_players = [
        alias.player
        for alias in PlayerAlias.objects.select_related("player").filter(
            normalized_alias=normalized_name,
            player_id__in=roster_ids,
            player__is_active=True,
        )
    ]
    if roster_alias_players:
        return _result_for_players(
            roster_alias_players,
            event=event,
            status=MATCH_EXACT_ROSTER_ALIAS,
            reason="Matched by exact alias in the event season and division roster.",
        )

    global_name_players = list(_players_with_exact_name(normalized_name))
    if global_name_players:
        return _result_for_players(
            global_name_players,
            event=event,
            status=MATCH_EXACT_GLOBAL_NAME,
            reason="Matched by a unique exact canonical name outside the event roster.",
        )

    global_alias_players = [
        alias.player
        for alias in PlayerAlias.objects.select_related("player").filter(
            normalized_alias=normalized_name,
            player__is_active=True,
        )
    ]
    return _result_for_players(
        global_alias_players,
        event=event,
        status=MATCH_EXACT_GLOBAL_ALIAS,
        reason=(
            "Matched by a unique exact alias outside the event roster."
            if global_alias_players
            else "No exact player match; manual resolution is required."
        ),
    )

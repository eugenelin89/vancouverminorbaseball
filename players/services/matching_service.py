from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from players.models import Player, PlayerSourceIdentifier
from players.services.identity_service import normalize_identifier, normalize_name


MATCH_EXACT = "exact"
MATCH_HIGH_CONFIDENCE = "high_confidence"
MATCH_AMBIGUOUS = "ambiguous"
MATCH_NO_MATCH = "no_match"


@dataclass
class PlayerMatchResult:
    status: str
    player: Player | None = None
    candidates: list[Player] = field(default_factory=list)
    reason: str = ""
    score: Decimal | None = None


def _result_for_candidates(candidates: list[Player], *, reason: str, score: Decimal) -> PlayerMatchResult:
    if not candidates:
        return PlayerMatchResult(status=MATCH_NO_MATCH, reason=reason, score=Decimal("0"))
    if len(candidates) == 1:
        return PlayerMatchResult(
            status=MATCH_HIGH_CONFIDENCE,
            player=candidates[0],
            candidates=candidates,
            reason=reason,
            score=score,
        )
    return PlayerMatchResult(status=MATCH_AMBIGUOUS, candidates=candidates, reason=reason, score=score)


def match_by_identifier(source: str, identifier_type: str, identifier_value: str) -> PlayerMatchResult:
    """Find a player by exact normalized source identifier."""
    normalized_source = normalize_identifier(source)
    normalized_type = normalize_identifier(identifier_type)
    normalized_value = normalize_identifier(identifier_value)
    if not normalized_source or not normalized_type or not normalized_value:
        return PlayerMatchResult(status=MATCH_NO_MATCH, reason="Source identifier is incomplete.", score=Decimal("0"))

    identifier = (
        PlayerSourceIdentifier.objects.select_related("player")
        .filter(source=normalized_source, identifier_type=normalized_type, identifier_value=normalized_value)
        .first()
    )
    if not identifier:
        return PlayerMatchResult(status=MATCH_NO_MATCH, reason="No player matched the source identifier.", score=Decimal("0"))
    return PlayerMatchResult(
        status=MATCH_EXACT,
        player=identifier.player,
        candidates=[identifier.player],
        reason="Matched by source identifier.",
        score=Decimal("1.0"),
    )


def match_by_name_and_birthdate(first_name: str, last_name: str, birthdate) -> PlayerMatchResult:
    """Find a high-confidence player match by exact name and birthdate."""
    normalized_first = normalize_name(first_name)
    normalized_last = normalize_name(last_name)
    if not normalized_first or not normalized_last or not birthdate:
        return PlayerMatchResult(status=MATCH_NO_MATCH, reason="Name and birthdate are required.", score=Decimal("0"))

    candidates = list(
        Player.objects.filter(first_name__iexact=normalized_first, last_name__iexact=normalized_last, birthdate=birthdate)
    )
    return _result_for_candidates(
        candidates,
        reason="Matched by exact name and birthdate.",
        score=Decimal("0.95"),
    )


def match_by_name_birth_year_division(
    first_name: str,
    last_name: str,
    birth_year: int | None = None,
    division: str = "",
) -> PlayerMatchResult:
    """Find a conservative player match by name with optional birth year and division context."""
    normalized_first = normalize_name(first_name)
    normalized_last = normalize_name(last_name)
    if not normalized_first or not normalized_last:
        return PlayerMatchResult(status=MATCH_NO_MATCH, reason="First and last name are required.", score=Decimal("0"))

    queryset = Player.objects.filter(first_name__iexact=normalized_first, last_name__iexact=normalized_last)
    if birth_year:
        queryset = queryset.filter(birth_year=birth_year)
    if division:
        queryset = queryset.filter(division__iexact=division.strip())

    candidates = list(queryset)
    return _result_for_candidates(
        candidates,
        reason="Matched by name with birth year and division context.",
        score=Decimal("0.85"),
    )


def find_player_match(identity_data: dict) -> PlayerMatchResult:
    """Find the best conservative player match for imported or entered identity data."""
    source = identity_data.get("source", "")
    identifier_type = identity_data.get("identifier_type", "")
    identifier_value = identity_data.get("identifier_value", "")
    if source and identifier_type and identifier_value:
        identifier_result = match_by_identifier(source, identifier_type, identifier_value)
        if identifier_result.status == MATCH_EXACT:
            return identifier_result

    birthdate = identity_data.get("birthdate")
    if birthdate:
        birthdate_result = match_by_name_and_birthdate(
            identity_data.get("first_name", ""),
            identity_data.get("last_name", ""),
            birthdate,
        )
        if birthdate_result.status != MATCH_NO_MATCH:
            return birthdate_result

    return match_by_name_birth_year_division(
        identity_data.get("first_name", ""),
        identity_data.get("last_name", ""),
        birth_year=identity_data.get("birth_year"),
        division=identity_data.get("division", ""),
    )

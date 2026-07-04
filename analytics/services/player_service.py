from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from django.db.models import Q

from analytics.models import (
    OBSERVATION_STATUS_SUBMITTED,
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    Observation,
)
from analytics.services.draft_service import DraftContext, get_draft_contexts_for_players
from players.models import Player, PlayerSourceRow, PlayerTag
from players.services.tag_service import active_tags


EVALUATION_HAS_SUBMITTED = "has_submitted"
EVALUATION_NO_SUBMITTED = "no_submitted"
EVALUATION_HAS_ANY = "has_any"
EVALUATION_NOT_STARTED = "not_started"

DRAFT_STATUS_DRAFTED = "drafted"
DRAFT_STATUS_AVAILABLE = "available"
DRAFT_STATUS_NO_CONTEXT = "no_draft_context"

MAX_COMPARE_PLAYERS = 6


@dataclass(frozen=True)
class PlayerSearchFilters:
    q: str = ""
    team: str = ""
    division: str = ""
    birth_year: int | None = None
    birth_year_raw: str = ""
    tag: str = ""
    source: str = ""
    evaluation: str = ""
    draft_status: str = ""
    include_inactive: bool = False


@dataclass(frozen=True)
class PlayerSearchResult:
    players: list[Player]
    filters: PlayerSearchFilters
    result_count: int
    active_tags: list[PlayerTag]
    source_choices: list[str]


def parse_player_search_filters(params) -> PlayerSearchFilters:
    """Normalize GET parameters for staff-facing player search/report filters."""
    birth_year_raw = (params.get("birth_year") or "").strip()
    birth_year = None
    if birth_year_raw:
        try:
            birth_year = int(birth_year_raw)
        except (TypeError, ValueError):
            birth_year = None
    return PlayerSearchFilters(
        q=(params.get("q") or "").strip(),
        team=(params.get("team") or "").strip(),
        division=(params.get("division") or "").strip(),
        birth_year=birth_year,
        birth_year_raw=birth_year_raw,
        tag=(params.get("tag") or "").strip(),
        source=(params.get("source") or "").strip(),
        evaluation=(params.get("evaluation") or "").strip(),
        draft_status=(params.get("draft_status") or "").strip(),
        include_inactive=params.get("include_inactive") == "1",
    )


def active_player_queryset(division: str = "", team: str = ""):
    """Return the canonical active player queryset for Analytics metrics."""
    queryset = Player.objects.filter(is_active=True).prefetch_related("tags").order_by("last_name", "first_name", "id")
    if division:
        queryset = queryset.filter(division__iexact=division)
    if team:
        queryset = queryset.filter(team_name__iexact=team)
    return queryset


def active_player_ids(division: str = "", team: str = "") -> set[int]:
    """Return active canonical player IDs for reusable metrics filters."""
    return set(active_player_queryset(division=division, team=team).values_list("id", flat=True))


def staff_player_queryset():
    """Return the reusable player queryset for staff profile-style pages."""
    return Player.objects.prefetch_related("tags", "source_rows").order_by("last_name", "first_name", "id")


def selected_player_queryset():
    """Return the reusable queryset for selected player lists and comparisons."""
    return Player.objects.prefetch_related("tags")


def _evaluation_filtered_player_ids(evaluation: str) -> set[int] | None:
    if not evaluation:
        return None
    any_ids = set(
        Observation.objects.filter(observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT).values_list("player_id", flat=True)
    )
    submitted_ids = set(
        Observation.objects.filter(
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
            status=OBSERVATION_STATUS_SUBMITTED,
        ).values_list("player_id", flat=True)
    )
    all_ids = set(Player.objects.values_list("id", flat=True))
    if evaluation == EVALUATION_HAS_SUBMITTED:
        return submitted_ids
    if evaluation == EVALUATION_NO_SUBMITTED:
        return all_ids - submitted_ids
    if evaluation == EVALUATION_HAS_ANY:
        return any_ids
    if evaluation == EVALUATION_NOT_STARTED:
        return all_ids - any_ids
    return None


def draft_status_for_contexts(contexts: list[DraftContext]) -> str:
    """Classify draft status from existing draft context read models."""
    if not contexts:
        return DRAFT_STATUS_NO_CONTEXT
    if any(context.pick_number or context.selected_team or context.current_team for context in contexts):
        return DRAFT_STATUS_DRAFTED
    return DRAFT_STATUS_AVAILABLE


def _apply_draft_status_filter(players: list[Player], draft_status: str) -> list[Player]:
    if not draft_status:
        return players
    if draft_status not in {DRAFT_STATUS_DRAFTED, DRAFT_STATUS_AVAILABLE, DRAFT_STATUS_NO_CONTEXT, "unmatched"}:
        return players
    contexts_by_player = get_draft_contexts_for_players(players)
    wanted = DRAFT_STATUS_NO_CONTEXT if draft_status == "unmatched" else draft_status
    return [
        player
        for player in players
        if draft_status_for_contexts(contexts_by_player.get(player.id, [])) == wanted
    ]


def source_choices() -> list[str]:
    """Return distinct import source choices for player search."""
    return list(
        PlayerSourceRow.objects.exclude(source="")
        .order_by("source")
        .values_list("source", flat=True)
        .distinct()
    )


def search_players(filters: PlayerSearchFilters) -> PlayerSearchResult:
    """Search canonical players for staff-facing Analytics pages."""
    queryset = Player.objects.all().prefetch_related("tags").order_by("last_name", "first_name", "id")
    if not filters.include_inactive:
        queryset = queryset.filter(is_active=True)
    if filters.q:
        queryset = queryset.filter(
            Q(first_name__icontains=filters.q)
            | Q(last_name__icontains=filters.q)
            | Q(preferred_name__icontains=filters.q)
        )
    if filters.team:
        queryset = queryset.filter(team_name__iexact=filters.team)
    if filters.division:
        queryset = queryset.filter(division__iexact=filters.division)
    if filters.birth_year is not None:
        queryset = queryset.filter(birth_year=filters.birth_year)
    if filters.tag:
        queryset = queryset.filter(tags__slug=filters.tag, tags__is_active=True)
    if filters.source:
        queryset = queryset.filter(source_rows__source=filters.source)

    evaluation_player_ids = _evaluation_filtered_player_ids(filters.evaluation)
    if evaluation_player_ids is not None:
        queryset = queryset.filter(id__in=evaluation_player_ids)

    players = list(queryset.distinct())
    players = _apply_draft_status_filter(players, filters.draft_status)
    return PlayerSearchResult(
        players=players,
        filters=filters,
        result_count=len(players),
        active_tags=list(active_tags()),
        source_choices=source_choices(),
    )


def selected_players_from_ids(player_ids: Iterable[int]) -> list[Player]:
    """Return selected players in the requested order, capped for comparison."""
    clean_ids = []
    for player_id in player_ids:
        try:
            player_id = int(player_id)
        except (TypeError, ValueError):
            continue
        if player_id not in clean_ids:
            clean_ids.append(player_id)
        if len(clean_ids) >= MAX_COMPARE_PLAYERS:
            break
    players_by_id = selected_player_queryset().in_bulk(clean_ids)
    return [players_by_id[player_id] for player_id in clean_ids if player_id in players_by_id]

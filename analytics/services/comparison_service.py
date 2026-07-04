from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Iterable

from analytics.models import (
    OBSERVATION_STATUS_SUBMITTED,
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    Observation,
)
from analytics.services.draft_service import DraftContext, get_draft_contexts_for_player
from analytics.services.player_service import MAX_COMPARE_PLAYERS
from players.models import Player, PlayerTag


@dataclass(frozen=True)
class CategoryScoreSummary:
    category: str
    average_rating: Decimal | None = None
    rating_count: int = 0


@dataclass(frozen=True)
class PlayerScoreSummary:
    player: Player
    average_rating: Decimal | None = None
    rating_count: int = 0
    submitted_observation_count: int = 0
    evaluator_count: int = 0
    category_scores: list[CategoryScoreSummary] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    tags: list[PlayerTag] = field(default_factory=list)
    draft_contexts: list[DraftContext] = field(default_factory=list)

    @property
    def category_score_map(self) -> dict[str, CategoryScoreSummary]:
        return {summary.category: summary for summary in self.category_scores}


@dataclass(frozen=True)
class PlayerComparison:
    players: list[Player]
    summaries: list[PlayerScoreSummary]
    category_names: list[str]
    empty: bool = False


def _average(values: list[Decimal]) -> Decimal | None:
    if not values:
        return None
    return sum(values, Decimal("0")) / Decimal(len(values))


def _submitted_observations(player: Player):
    return (
        Observation.objects.filter(
            player=player,
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
            status=OBSERVATION_STATUS_SUBMITTED,
        )
        .select_related("evaluator")
        .prefetch_related("responses__question")
        .order_by("-submitted_at", "-id")
    )


def _active_tags_for_player(player: Player) -> list[PlayerTag]:
    prefetched = getattr(player, "_prefetched_objects_cache", {})
    if "tags" in prefetched:
        return sorted(
            [tag for tag in prefetched["tags"] if tag.is_active],
            key=lambda tag: tag.name,
        )
    return list(player.tags.filter(is_active=True).order_by("name"))


def get_player_score_summary(player: Player) -> PlayerScoreSummary:
    """Return a read-only score summary for one player using submitted coach assessments."""
    observations = list(_submitted_observations(player))
    rating_values = []
    category_values: dict[str, list[Decimal]] = {}
    notes = []
    evaluator_ids = set()

    for observation in observations:
        if observation.evaluator_id:
            evaluator_ids.add(observation.evaluator_id)
        for response in observation.responses.all():
            if response.response_type == RESPONSE_TYPE_RATING_1_5 and response.numeric_value is not None:
                rating_values.append(response.numeric_value)
                category = response.question.category or "Questions"
                category_values.setdefault(category, []).append(response.numeric_value)
            elif response.response_type == RESPONSE_TYPE_TEXT and response.text_value.strip():
                notes.append(response.text_value.strip())

    category_scores = [
        CategoryScoreSummary(category=category, average_rating=_average(values), rating_count=len(values))
        for category, values in sorted(category_values.items())
    ]
    return PlayerScoreSummary(
        player=player,
        average_rating=_average(rating_values),
        rating_count=len(rating_values),
        submitted_observation_count=len(observations),
        evaluator_count=len(evaluator_ids),
        category_scores=category_scores,
        notes=notes,
        tags=_active_tags_for_player(player),
        draft_contexts=get_draft_contexts_for_player(player),
    )


def get_player_comparison(players: Iterable[Player]) -> PlayerComparison:
    """Return a simple read-only comparison for selected players."""
    selected_players = list(players)[:MAX_COMPARE_PLAYERS]
    summaries = [get_player_score_summary(player) for player in selected_players]
    category_names = sorted(
        {
            category.category
            for summary in summaries
            for category in summary.category_scores
        }
    )
    return PlayerComparison(
        players=selected_players,
        summaries=summaries,
        category_names=category_names,
        empty=not selected_players,
    )

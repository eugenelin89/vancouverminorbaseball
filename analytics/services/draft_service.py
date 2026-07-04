from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Iterable

from django.db.models import Prefetch

from analytics.models import (
    OBSERVATION_STATUS_SUBMITTED,
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    Observation,
    ObservationResponse,
)
from drafts.models import Draft, DraftAction, DraftActionType, DraftPlayer, DraftTeam
from players.models import Player
from players.services.matching_service import MATCH_AMBIGUOUS, MATCH_EXACT, MATCH_HIGH_CONFIDENCE, find_player_match


EXPECTED_DRAFT_ROUND_KEYS = {
    "expected_draft_round",
    "projected_draft_round",
    "should_be_drafted_round",
}


@dataclass(frozen=True)
class DraftObservationSummary:
    observation: Observation
    evaluator_name: str
    submitted_at: object
    average_rating: Decimal | None = None
    rating_count: int = 0
    notes: list[str] = field(default_factory=list)
    expected_draft_round: str = ""


@dataclass(frozen=True)
class DraftContext:
    draft_player: DraftPlayer
    matched_player: Player | None
    match_status: str
    match_reason: str
    birth_year: int | None = None
    selected_team: DraftTeam | None = None
    current_team: DraftTeam | None = None
    pick_number: int | None = None
    selected_round: int | None = None
    selection_order: int | None = None
    selected_at: object | None = None
    observations: list[DraftObservationSummary] = field(default_factory=list)

    @property
    def is_matched(self) -> bool:
        return self.matched_player is not None

    @property
    def has_submitted_observations(self) -> bool:
        return bool(self.observations)

    @property
    def submitted_observation_count(self) -> int:
        return len(self.observations)

    @property
    def latest_observation(self) -> DraftObservationSummary | None:
        return self.observations[0] if self.observations else None

    @property
    def average_rating(self) -> Decimal | None:
        ratings = [
            summary.average_rating
            for summary in self.observations
            if summary.average_rating is not None and summary.rating_count
        ]
        if not ratings:
            return None
        return sum(ratings, Decimal("0")) / Decimal(len(ratings))


def _normalized_extra_value(draft_player: DraftPlayer, *candidate_keys: str) -> str:
    candidate_lookup = {key.casefold().replace("_", " ").strip() for key in candidate_keys}
    for source in [draft_player.extra_data, draft_player.imported_row]:
        for key, value in source.items():
            normalized_key = str(key).casefold().replace("_", " ").strip()
            if normalized_key in candidate_lookup and value not in (None, ""):
                return str(value).strip()
    return ""


def _birth_year_for_draft_player(draft_player: DraftPlayer) -> int | None:
    value = _normalized_extra_value(draft_player, "birth year", "birth_year", "year of birth")
    if not value:
        birthdate_value = _normalized_extra_value(draft_player, "birthdate", "birth date", "dob")
        value = birthdate_value[:4] if len(birthdate_value) >= 4 else ""
    try:
        year = int(value)
    except (TypeError, ValueError):
        return None
    if 1900 <= year <= 2100:
        return year
    return None


def match_draft_player_to_player(draft_player: DraftPlayer):
    """Return a conservative canonical player match for a draft player."""
    return find_player_match(
        {
            "first_name": draft_player.first_name,
            "last_name": draft_player.last_name,
            "birth_year": _birth_year_for_draft_player(draft_player),
            "division": draft_player.draft.division,
        }
    )


def _selection_round(pick_number: int | None, team_count: int) -> int | None:
    if not pick_number or team_count <= 0:
        return None
    return ((pick_number - 1) // team_count) + 1


def _expected_round_from_response(response) -> str:
    field_name = response.question.metadata.get("draft_context_field") or response.payload.get("draft_context_field")
    if field_name != "expected_draft_round" and response.question.key not in EXPECTED_DRAFT_ROUND_KEYS:
        return ""
    if response.numeric_value is not None:
        return str(response.numeric_value.normalize())
    if response.text_value:
        return response.text_value
    if response.selected_choice:
        return response.selected_choice
    return response.raw_value


def _summarize_observation(observation: Observation) -> DraftObservationSummary:
    rating_values = []
    notes = []
    expected_round = ""
    for response in observation.responses.all():
        if response.response_type == RESPONSE_TYPE_RATING_1_5 and response.numeric_value is not None:
            rating_values.append(response.numeric_value)
        elif response.response_type == RESPONSE_TYPE_TEXT and response.text_value.strip():
            notes.append(response.text_value.strip())
        expected_round = expected_round or _expected_round_from_response(response)

    average_rating = None
    if rating_values:
        average_rating = sum(rating_values, Decimal("0")) / Decimal(len(rating_values))

    return DraftObservationSummary(
        observation=observation,
        evaluator_name=observation.evaluator.get_username() if observation.evaluator_id else "Unknown evaluator",
        submitted_at=observation.submitted_at,
        average_rating=average_rating,
        rating_count=len(rating_values),
        notes=notes,
        expected_draft_round=expected_round,
    )


def _submitted_observations_by_player(player_ids: set[int]) -> dict[int, list[DraftObservationSummary]]:
    if not player_ids:
        return {}
    responses = Prefetch("responses", queryset=ObservationResponse.objects.select_related("question"))
    observations = (
        Observation.objects.filter(
            player_id__in=player_ids,
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
            status=OBSERVATION_STATUS_SUBMITTED,
        )
        .select_related("player", "evaluator", "evaluation_cycle", "question_set")
        .prefetch_related(responses)
        .order_by("player_id", "-submitted_at", "-id")
    )
    grouped: dict[int, list[DraftObservationSummary]] = {}
    for observation in observations:
        grouped.setdefault(observation.player_id, []).append(_summarize_observation(observation))
    return grouped


def get_draft_contexts_for_draft(draft: Draft) -> dict[int, DraftContext]:
    """Return read-only analytics draft context keyed by DraftPlayer id."""
    draft_players = list(draft.players.select_related("current_team", "draft").order_by("last_name", "first_name", "id"))
    team_count = draft.teams.count()

    matches = {}
    matched_player_ids = set()
    for draft_player in draft_players:
        match = match_draft_player_to_player(draft_player)
        matches[draft_player.id] = match
        if match.status in {MATCH_EXACT, MATCH_HIGH_CONFIDENCE} and match.player:
            matched_player_ids.add(match.player.id)

    observations_by_player = _submitted_observations_by_player(matched_player_ids)

    selected_actions = {}
    for action in (
        DraftAction.objects.filter(
            draft=draft,
            player_id__in=[draft_player.id for draft_player in draft_players],
            action_type=DraftActionType.PLAYER_DRAFTED,
            is_reverted=False,
        )
        .select_related("to_team")
        .order_by("pick_number", "created_at", "id")
    ):
        selected_actions.setdefault(action.player_id, action)

    contexts = {}
    for draft_player in draft_players:
        match = matches[draft_player.id]
        matched_player = match.player if match.status in {MATCH_EXACT, MATCH_HIGH_CONFIDENCE} else None
        selected_action = selected_actions.get(draft_player.id)
        pick_number = selected_action.pick_number if selected_action else None
        contexts[draft_player.id] = DraftContext(
            draft_player=draft_player,
            matched_player=matched_player,
            match_status=MATCH_AMBIGUOUS if match.status == MATCH_AMBIGUOUS else match.status,
            match_reason=match.reason,
            birth_year=matched_player.birth_year if matched_player else _birth_year_for_draft_player(draft_player),
            selected_team=selected_action.to_team if selected_action else None,
            current_team=draft_player.current_team,
            pick_number=pick_number,
            selected_round=_selection_round(pick_number, team_count),
            selection_order=pick_number,
            selected_at=selected_action.created_at if selected_action else None,
            observations=observations_by_player.get(matched_player.id, []) if matched_player else [],
        )
    return contexts


def get_draft_context_for_draft_player(draft_player: DraftPlayer) -> DraftContext:
    """Return read-only analytics draft context for one draft player."""
    return get_draft_contexts_for_draft(draft_player.draft).get(draft_player.id)


def get_draft_contexts_for_players(players: Iterable[Player]) -> dict[int, list[DraftContext]]:
    """Return read-only draft contexts keyed by canonical Player id."""
    player_ids = {player.id for player in players}
    contexts_by_player = {player_id: [] for player_id in player_ids}
    if not player_ids:
        return contexts_by_player

    for draft in Draft.objects.all():
        for context in get_draft_contexts_for_draft(draft).values():
            matched_player_id = getattr(context.matched_player, "id", None)
            if matched_player_id in contexts_by_player:
                contexts_by_player[matched_player_id].append(context)
    return contexts_by_player


def get_draft_contexts_for_player(player: Player) -> list[DraftContext]:
    """Return read-only draft contexts confidently matched to a canonical Player."""
    return get_draft_contexts_for_players([player]).get(player.id, [])

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from django.db.models import Avg, Count, Sum

from analytics.models import (
    OBSERVATION_STATUS_DRAFT,
    OBSERVATION_STATUS_REOPENED,
    OBSERVATION_STATUS_SUBMITTED,
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    RESPONSE_TYPE_RATING_1_5,
    EvaluationCycle,
    Observation,
    ObservationResponse,
)
from analytics.services.coach_assessment_service import get_active_coach_assessment_cycle
from analytics.services.draft_service import get_draft_contexts_for_draft, get_draft_contexts_for_players
from analytics.services.player_service import active_player_queryset, draft_status_for_contexts
from drafts.models import Draft
from players.models import Player, PlayerImportBatch, PlayerImportStatus


@dataclass(frozen=True)
class RoleCount:
    role: str
    count: int


@dataclass(frozen=True)
class AverageMetric:
    label: str
    average: Decimal | None
    count: int


@dataclass(frozen=True)
class VarianceRow:
    player: Player
    category: str
    min_average: Decimal
    max_average: Decimal
    spread: Decimal
    evaluator_count: int


@dataclass(frozen=True)
class CompletionMetrics:
    active_cycle: EvaluationCycle | None
    total_active_players: int = 0
    players_with_submitted_assessment: int = 0
    players_without_submitted_assessment: int = 0
    submitted_observation_count: int = 0
    draft_observation_count: int = 0
    reopened_observation_count: int = 0
    completion_rate: Decimal = Decimal("0")


@dataclass(frozen=True)
class ObservationMetrics:
    total_observations: int = 0
    submitted_count: int = 0
    draft_count: int = 0
    reopened_count: int = 0
    archived_count: int = 0
    by_evaluator_role: list[RoleCount] = field(default_factory=list)
    by_category_average: list[AverageMetric] = field(default_factory=list)
    by_role_average: list[AverageMetric] = field(default_factory=list)
    variance_rows: list[VarianceRow] = field(default_factory=list)


@dataclass(frozen=True)
class ImportMetrics:
    total_batches: int = 0
    uploaded_count: int = 0
    previewed_count: int = 0
    needs_review_count: int = 0
    committed_count: int = 0
    failed_count: int = 0
    cancelled_count: int = 0
    recent_batches: list[PlayerImportBatch] = field(default_factory=list)
    rows_created: int = 0
    rows_updated: int = 0
    rows_skipped: int = 0
    rows_conflicted: int = 0


@dataclass(frozen=True)
class DraftMismatchRow:
    player: Player
    expected_round: str
    actual_round: str
    pick_number: int | None
    draft_name: str


@dataclass(frozen=True)
class DraftMatchingMetrics:
    matched_player_count: int = 0
    drafted_player_count: int = 0
    available_player_count: int = 0
    no_context_player_count: int = 0
    unmatched_draft_player_count: int = 0
    expected_round_mismatch_count: int = 0
    mismatches: list[DraftMismatchRow] = field(default_factory=list)
    players_without_draft_context: list[Player] = field(default_factory=list)


def normalize_cycle_id(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def selected_cycle(cycle_id: int | None = None) -> EvaluationCycle | None:
    """Return the requested active cycle or the default active coach-assessment cycle."""
    return get_active_coach_assessment_cycle(cycle_id)


def _observation_queryset(cycle: EvaluationCycle | None = None, division: str = "", team: str = ""):
    queryset = Observation.objects.filter(observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT).select_related(
        "player", "evaluation_cycle", "evaluator", "evaluator_role"
    )
    if cycle:
        queryset = queryset.filter(evaluation_cycle=cycle)
    if division:
        queryset = queryset.filter(player__division__iexact=division)
    if team:
        queryset = queryset.filter(player__team_name__iexact=team)
    return queryset


def completion_metrics(cycle: EvaluationCycle | None = None, division: str = "", team: str = "") -> CompletionMetrics:
    """Return coach-assessment completion metrics for active players."""
    cycle = cycle or get_active_coach_assessment_cycle()
    players = active_player_queryset(division=division, team=team)
    total_players = players.count()
    if not cycle:
        return CompletionMetrics(active_cycle=None, total_active_players=total_players)

    player_ids = set(players.values_list("id", flat=True))
    observations = _observation_queryset(cycle=cycle, division=division, team=team)
    submitted_player_ids = set(observations.filter(status=OBSERVATION_STATUS_SUBMITTED).values_list("player_id", flat=True))
    completed = len(player_ids & submitted_player_ids)
    rate = Decimal("0")
    if total_players:
        rate = (Decimal(completed) / Decimal(total_players)) * Decimal("100")
    return CompletionMetrics(
        active_cycle=cycle,
        total_active_players=total_players,
        players_with_submitted_assessment=completed,
        players_without_submitted_assessment=max(total_players - completed, 0),
        submitted_observation_count=observations.filter(status=OBSERVATION_STATUS_SUBMITTED).count(),
        draft_observation_count=observations.filter(status=OBSERVATION_STATUS_DRAFT).count(),
        reopened_observation_count=observations.filter(status=OBSERVATION_STATUS_REOPENED).count(),
        completion_rate=rate,
    )


def _average_metrics(rows, label_key: str, empty_label: str = "Unknown") -> list[AverageMetric]:
    metrics = []
    for row in rows:
        label = row.get(label_key) or empty_label
        metrics.append(AverageMetric(label=label, average=row["average"], count=row["count"]))
    return metrics


def coach_to_coach_variance_rows(cycle: EvaluationCycle | None = None, division: str = "", team: str = "", limit: int = 10) -> list[VarianceRow]:
    """Return simple max-minus-min coach spread rows by player/category."""
    responses = ObservationResponse.objects.filter(
        response_type=RESPONSE_TYPE_RATING_1_5,
        numeric_value__isnull=False,
        observation__observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
        observation__status=OBSERVATION_STATUS_SUBMITTED,
    )
    if cycle:
        responses = responses.filter(observation__evaluation_cycle=cycle)
    if division:
        responses = responses.filter(observation__player__division__iexact=division)
    if team:
        responses = responses.filter(observation__player__team_name__iexact=team)

    evaluator_rows = (
        responses.values(
            "observation__player_id",
            "observation__player__first_name",
            "observation__player__last_name",
            "question__category",
            "observation__evaluator_id",
        )
        .annotate(evaluator_average=Avg("numeric_value"))
        .filter(observation__evaluator_id__isnull=False)
    )
    grouped = {}
    for row in evaluator_rows:
        key = (row["observation__player_id"], row["question__category"] or "Questions")
        grouped.setdefault(
            key,
            {
                "player_id": row["observation__player_id"],
                "category": row["question__category"] or "Questions",
                "averages": [],
            },
        )["averages"].append(row["evaluator_average"])

    player_ids = [value["player_id"] for value in grouped.values() if len(value["averages"]) >= 2]
    players_by_id = Player.objects.in_bulk(player_ids)
    variance_rows = []
    for value in grouped.values():
        averages = value["averages"]
        if len(averages) < 2:
            continue
        min_average = min(averages)
        max_average = max(averages)
        player = players_by_id.get(value["player_id"])
        if not player:
            continue
        variance_rows.append(
            VarianceRow(
                player=player,
                category=value["category"],
                min_average=min_average,
                max_average=max_average,
                spread=max_average - min_average,
                evaluator_count=len(averages),
            )
        )
    return sorted(variance_rows, key=lambda row: (-row.spread, row.player.last_name, row.player.first_name))[:limit]


def observation_metrics(cycle: EvaluationCycle | None = None, division: str = "", team: str = "") -> ObservationMetrics:
    """Return counts and rating summaries for submitted coach assessments."""
    observations = _observation_queryset(cycle=cycle, division=division, team=team)
    status_counts = observations.values("status").annotate(count=Count("id"))
    counts_by_status = {row["status"]: row["count"] for row in status_counts}
    role_counts = [
        RoleCount(role=row["evaluator_role_name"] or row["evaluator_role_key"] or "Unknown role", count=row["count"])
        for row in observations.values("evaluator_role_name", "evaluator_role_key").annotate(count=Count("id")).order_by("evaluator_role_name", "evaluator_role_key")
    ]

    rating_responses = ObservationResponse.objects.filter(
        response_type=RESPONSE_TYPE_RATING_1_5,
        numeric_value__isnull=False,
        observation__observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
        observation__status=OBSERVATION_STATUS_SUBMITTED,
    )
    if cycle:
        rating_responses = rating_responses.filter(observation__evaluation_cycle=cycle)
    if division:
        rating_responses = rating_responses.filter(observation__player__division__iexact=division)
    if team:
        rating_responses = rating_responses.filter(observation__player__team_name__iexact=team)

    category_rows = (
        rating_responses.values("question__category")
        .annotate(average=Avg("numeric_value"), count=Count("id"))
        .order_by("question__category")
    )
    role_average_rows = (
        rating_responses.values("observation__evaluator_role_name", "observation__evaluator_role_key")
        .annotate(average=Avg("numeric_value"), count=Count("id"))
        .order_by("observation__evaluator_role_name", "observation__evaluator_role_key")
    )
    return ObservationMetrics(
        total_observations=observations.count(),
        submitted_count=counts_by_status.get(OBSERVATION_STATUS_SUBMITTED, 0),
        draft_count=counts_by_status.get(OBSERVATION_STATUS_DRAFT, 0),
        reopened_count=counts_by_status.get(OBSERVATION_STATUS_REOPENED, 0),
        archived_count=counts_by_status.get("archived", 0),
        by_evaluator_role=role_counts,
        by_category_average=_average_metrics(category_rows, "question__category", "Questions"),
        by_role_average=[
            AverageMetric(
                label=row["observation__evaluator_role_name"] or row["observation__evaluator_role_key"] or "Unknown role",
                average=row["average"],
                count=row["count"],
            )
            for row in role_average_rows
        ],
        variance_rows=coach_to_coach_variance_rows(cycle=cycle, division=division, team=team),
    )


def import_metrics(limit: int = 5) -> ImportMetrics:
    """Return import batch status counts and row totals."""
    status_counts = PlayerImportBatch.objects.values("status").annotate(count=Count("id"))
    counts_by_status = {row["status"]: row["count"] for row in status_counts}
    totals = PlayerImportBatch.objects.aggregate(
        rows_created=Sum("rows_created"),
        rows_updated=Sum("rows_updated"),
        rows_skipped=Sum("rows_skipped"),
        rows_conflicted=Sum("rows_conflicted"),
    )
    return ImportMetrics(
        total_batches=PlayerImportBatch.objects.count(),
        uploaded_count=counts_by_status.get(PlayerImportStatus.UPLOADED, 0),
        previewed_count=counts_by_status.get(PlayerImportStatus.PREVIEWED, 0),
        needs_review_count=counts_by_status.get(PlayerImportStatus.NEEDS_REVIEW, 0),
        committed_count=counts_by_status.get(PlayerImportStatus.COMMITTED, 0),
        failed_count=counts_by_status.get(PlayerImportStatus.FAILED, 0),
        cancelled_count=counts_by_status.get(PlayerImportStatus.CANCELLED, 0),
        recent_batches=list(PlayerImportBatch.objects.select_related("uploaded_by").order_by("-created_at", "-id")[:limit]),
        rows_created=totals["rows_created"] or 0,
        rows_updated=totals["rows_updated"] or 0,
        rows_skipped=totals["rows_skipped"] or 0,
        rows_conflicted=totals["rows_conflicted"] or 0,
    )


def _normalize_round(value: object) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    try:
        return str(int(Decimal(value)))
    except Exception:
        return value.casefold()


def draft_matching_metrics(division: str = "", team: str = "", mismatch_limit: int = 10, no_context_limit: int = 10) -> DraftMatchingMetrics:
    """Return draft matching summaries using draft_service read models."""
    players = list(active_player_queryset(division=division, team=team))
    contexts_by_player = get_draft_contexts_for_players(players)
    matched_count = drafted_count = available_count = no_context_count = 0
    mismatches = []
    players_without_context = []

    for player in players:
        contexts = contexts_by_player.get(player.id, [])
        if not contexts:
            no_context_count += 1
            players_without_context.append(player)
            continue
        matched_count += 1
        status = draft_status_for_contexts(contexts)
        if status == "drafted":
            drafted_count += 1
        elif status == "available":
            available_count += 1
        for context in contexts:
            if not context.selected_round:
                continue
            for observation_summary in context.observations:
                expected_round = observation_summary.expected_draft_round
                if expected_round and _normalize_round(expected_round) != _normalize_round(context.selected_round):
                    mismatches.append(
                        DraftMismatchRow(
                            player=player,
                            expected_round=expected_round,
                            actual_round=str(context.selected_round),
                            pick_number=context.pick_number,
                            draft_name=context.draft_player.draft.name,
                        )
                    )
                    break

    unmatched_draft_players = 0
    for draft in Draft.objects.all():
        for context in get_draft_contexts_for_draft(draft).values():
            if not context.is_matched:
                unmatched_draft_players += 1

    mismatches = sorted(
        mismatches,
        key=lambda row: (
            int(row.actual_round) if row.actual_round.isdigit() else 999,
            row.pick_number or 999999,
            row.player.last_name,
            row.player.first_name,
        ),
    )
    return DraftMatchingMetrics(
        matched_player_count=matched_count,
        drafted_player_count=drafted_count,
        available_player_count=available_count,
        no_context_player_count=no_context_count,
        unmatched_draft_player_count=unmatched_draft_players,
        expected_round_mismatch_count=len(mismatches),
        mismatches=mismatches[:mismatch_limit],
        players_without_draft_context=players_without_context[:no_context_limit],
    )


def recent_submitted_observations(cycle: EvaluationCycle | None = None, division: str = "", team: str = "", limit: int = 10) -> list[Observation]:
    """Return recent submitted coach assessments for command center display."""
    return list(
        _observation_queryset(cycle=cycle, division=division, team=team)
        .filter(status=OBSERVATION_STATUS_SUBMITTED)
        .select_related("player", "evaluation_cycle", "evaluator", "evaluator_role")
        .order_by("-submitted_at", "-id")[:limit]
    )

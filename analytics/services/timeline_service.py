from __future__ import annotations

from dataclasses import dataclass, field

from django.urls import reverse

from analytics.models import OBSERVATION_STATUS_SUBMITTED, OBSERVATION_TYPE_COACH_ASSESSMENT, Observation
from analytics.services.draft_service import DraftContext, get_draft_contexts_for_player
from players.models import Player, PlayerSourceRow


KIND_COACH_ASSESSMENT = "coach_assessment"
KIND_DRAFT_CONTEXT = "draft_context"
KIND_IMPORT = "import"

KIND_PRIORITY = {
    KIND_COACH_ASSESSMENT: 0,
    KIND_DRAFT_CONTEXT: 1,
    KIND_IMPORT: 2,
}


@dataclass(frozen=True)
class PlayerTimelineItem:
    occurred_at: object | None
    sort_key: tuple
    kind: str
    title: str
    subtitle: str = ""
    description: str = ""
    metadata: dict = field(default_factory=dict)
    url: str = ""


@dataclass(frozen=True)
class PlayerTimeline:
    player: Player
    items: list[PlayerTimelineItem]
    coach_assessment_count: int = 0
    import_count: int = 0
    draft_context_count: int = 0


def _sort_key(kind: str, occurred_at, stable_id: int | None = None) -> tuple:
    # Newer dated entries first; undated entries last. Python sorts ascending.
    has_no_timestamp = occurred_at is None
    timestamp = occurred_at.timestamp() if hasattr(occurred_at, "timestamp") else 0
    return (has_no_timestamp, -timestamp, KIND_PRIORITY.get(kind, 99), -(stable_id or 0))


def coach_assessment_timeline_items(player: Player) -> list[PlayerTimelineItem]:
    """Return submitted coach assessment timeline items for a player."""
    observations = (
        Observation.objects.filter(
            player=player,
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
            status=OBSERVATION_STATUS_SUBMITTED,
        )
        .select_related("evaluation_cycle", "evaluator", "evaluator_role")
        .order_by("-submitted_at", "-id")
    )
    items = []
    for observation in observations:
        evaluator = observation.evaluator.get_username() if observation.evaluator_id else "Unknown evaluator"
        role = observation.evaluator_role_name or "Evaluator"
        items.append(
            PlayerTimelineItem(
                occurred_at=observation.submitted_at,
                sort_key=_sort_key(KIND_COACH_ASSESSMENT, observation.submitted_at, observation.id),
                kind=KIND_COACH_ASSESSMENT,
                title="Coach assessment submitted",
                subtitle=observation.evaluation_cycle.name,
                description=f"{role}: {evaluator}",
                metadata={
                    "status": observation.status,
                    "evaluator": evaluator,
                    "role": role,
                    "cycle": observation.evaluation_cycle.name,
                },
                url=reverse("analytics:observation-review-detail", kwargs={"observation_id": observation.id}),
            )
        )
    return items


def import_timeline_items(player: Player) -> list[PlayerTimelineItem]:
    """Return imported source-row timeline items for a player without exposing raw row JSON."""
    source_rows = (
        PlayerSourceRow.objects.filter(player=player)
        .select_related("import_batch", "imported_by")
        .order_by("-imported_at", "-id")
    )
    items = []
    for source_row in source_rows:
        filename = source_row.source_filename or getattr(source_row.import_batch, "original_filename", "")
        row_label = f" row {source_row.row_number}" if source_row.row_number else ""
        items.append(
            PlayerTimelineItem(
                occurred_at=source_row.imported_at,
                sort_key=_sort_key(KIND_IMPORT, source_row.imported_at, source_row.id),
                kind=KIND_IMPORT,
                title="Player context imported",
                subtitle=source_row.source,
                description=f"{filename}{row_label}".strip(),
                metadata={
                    "source": source_row.source,
                    "filename": filename,
                    "row_number": source_row.row_number,
                },
            )
        )
    return items


def _draft_context_title(context: DraftContext) -> str:
    if context.pick_number:
        return "Draft selection recorded"
    if context.current_team:
        return "Draft roster assignment"
    return "Draft context matched"


def draft_context_timeline_items(player: Player) -> list[PlayerTimelineItem]:
    """Return draft context timeline items confidently matched to a canonical player."""
    items = []
    for context in get_draft_contexts_for_player(player):
        occurred_at = context.selected_at or context.draft_player.updated_at or context.draft_player.created_at
        draft = context.draft_player.draft
        details = []
        if context.selected_team:
            details.append(f"Selected by {context.selected_team.name}")
        elif context.current_team:
            details.append(f"Assigned to {context.current_team.name}")
        if context.pick_number:
            details.append(f"Pick #{context.pick_number}")
        if context.selected_round:
            details.append(f"Round {context.selected_round}")
        items.append(
            PlayerTimelineItem(
                occurred_at=occurred_at,
                sort_key=_sort_key(KIND_DRAFT_CONTEXT, occurred_at, context.draft_player.id),
                kind=KIND_DRAFT_CONTEXT,
                title=_draft_context_title(context),
                subtitle=draft.name,
                description=" · ".join(details) or "Matched to draft room.",
                metadata={
                    "draft": draft.name,
                    "pick_number": context.pick_number,
                    "selected_round": context.selected_round,
                    "selected_team": context.selected_team.name if context.selected_team else "",
                    "match_status": context.match_status,
                },
            )
        )
    return items


def get_player_timeline(player: Player) -> PlayerTimeline:
    """Assemble the Version 1 read-only player timeline."""
    coach_items = coach_assessment_timeline_items(player)
    import_items = import_timeline_items(player)
    draft_items = draft_context_timeline_items(player)
    items = sorted([*coach_items, *draft_items, *import_items], key=lambda item: item.sort_key)
    return PlayerTimeline(
        player=player,
        items=items,
        coach_assessment_count=len(coach_items),
        import_count=len(import_items),
        draft_context_count=len(draft_items),
    )

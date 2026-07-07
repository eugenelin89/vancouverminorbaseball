from __future__ import annotations

from dataclasses import dataclass, field
from django.urls import reverse
from django.utils import timezone

from analytics.models import EvaluationCycle, Observation
from analytics.services import metrics_service
from analytics.services.metrics_service import (
    CompletionMetrics,
    DraftMatchingMetrics,
    ImportMetrics,
    ObservationMetrics,
)


@dataclass(frozen=True)
class MetricCard:
    label: str
    value: str
    help_text: str = ""
    url: str = ""
    status: str = "neutral"


@dataclass(frozen=True)
class NavigationLink:
    label: str
    url: str
    help_text: str = ""


@dataclass(frozen=True)
class RecentObservationRow:
    observation: Observation
    player: object
    evaluator_name: str
    evaluator_role: str
    cycle_name: str
    submitted_at: object
    detail_url: str
    player_profile_url: str


@dataclass(frozen=True)
class CommandCenterContext:
    summary_cards: list[MetricCard]
    completion_summary: CompletionMetrics
    observation_summary: ObservationMetrics
    import_summary: ImportMetrics
    draft_summary: DraftMatchingMetrics
    recent_observations: list[RecentObservationRow]
    navigation_links: list[NavigationLink]
    generated_at: object
    selected_cycle: EvaluationCycle | None = None
    filters: dict = field(default_factory=dict)


def _percent(value) -> str:
    return f"{value:.0f}%"


def _recent_observation_rows(observations: list[Observation]) -> list[RecentObservationRow]:
    rows = []
    for observation in observations:
        rows.append(
            RecentObservationRow(
                observation=observation,
                player=observation.player,
                evaluator_name=observation.evaluator.get_username() if observation.evaluator_id else "Unknown evaluator",
                evaluator_role=observation.evaluator_role_name or observation.evaluator_role_key or "Unknown role",
                cycle_name=observation.evaluation_cycle.name,
                submitted_at=observation.submitted_at,
                detail_url=reverse("analytics:observation-review-detail", kwargs={"observation_id": observation.id}),
                player_profile_url=reverse("analytics:player-profile", kwargs={"player_id": observation.player_id}),
            )
        )
    return rows


def _navigation_links() -> list[NavigationLink]:
    return [
        NavigationLink("Player Search", reverse("analytics:player-search"), "Find players and open profiles."),
        NavigationLink("Compare Players", reverse("analytics:player-compare"), "Compare submitted assessment summaries."),
        NavigationLink("Import Players", reverse("analytics:import-list"), "Review player import batches."),
        NavigationLink("Coach Assessments", reverse("analytics:assessment-list"), "Open the coach assessment workflow."),
        NavigationLink("Observation Review", reverse("analytics:observation-review-list"), "Review submitted and draft observations."),
        NavigationLink("Account Operations", reverse("accounts:operations-dashboard"), "Review account status and player links."),
    ]


def _summary_cards(
    completion: CompletionMetrics,
    observations: ObservationMetrics,
    imports: ImportMetrics,
    draft: DraftMatchingMetrics,
    recent_count: int,
) -> list[MetricCard]:
    return [
        MetricCard(
            label="Active players",
            value=str(completion.total_active_players),
            help_text="Canonical active player records.",
            url=reverse("analytics:player-search"),
        ),
        MetricCard(
            label="Submitted assessments",
            value=str(observations.submitted_count),
            help_text="Submitted coach assessment observations.",
            url=reverse("analytics:observation-review-list"),
            status="success" if observations.submitted_count else "neutral",
        ),
        MetricCard(
            label="Completion rate",
            value=_percent(completion.completion_rate),
            help_text="Active players with at least one submitted assessment in the selected cycle.",
            url=reverse("analytics:assessment-list"),
        ),
        MetricCard(
            label="Imports needing review",
            value=str(imports.needs_review_count),
            help_text="Player import batches waiting for staff review.",
            url=reverse("analytics:import-list"),
            status="warning" if imports.needs_review_count else "success",
        ),
        MetricCard(
            label="Drafted / matched",
            value=f"{draft.drafted_player_count} / {draft.matched_player_count}",
            help_text="Active players with draft context.",
        ),
        MetricCard(
            label="Recent observations",
            value=str(recent_count),
            help_text="Latest submitted coach assessments shown below.",
            url=reverse("analytics:observation-review-list"),
        ),
    ]


def get_command_center_context(cycle_id: int | None = None, division: str = "", team: str = "") -> CommandCenterContext:
    """Assemble the Analytics Command Center read model from metric services."""
    cycle = metrics_service.selected_cycle(cycle_id)
    completion = metrics_service.completion_metrics(cycle=cycle, division=division, team=team)
    observations = metrics_service.observation_metrics(cycle=cycle, division=division, team=team)
    imports = metrics_service.import_metrics()
    draft = metrics_service.draft_matching_metrics(division=division, team=team)
    recent = _recent_observation_rows(
        metrics_service.recent_submitted_observations(cycle=cycle, division=division, team=team)
    )
    return CommandCenterContext(
        summary_cards=_summary_cards(completion, observations, imports, draft, len(recent)),
        completion_summary=completion,
        observation_summary=observations,
        import_summary=imports,
        draft_summary=draft,
        recent_observations=recent,
        navigation_links=_navigation_links(),
        generated_at=timezone.now(),
        selected_cycle=cycle,
        filters={"cycle": cycle_id or "", "division": division, "team": team},
    )

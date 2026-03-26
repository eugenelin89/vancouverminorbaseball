from collections import defaultdict
from decimal import Decimal

from django.db import transaction

from pdp.models import (
    AssignmentSourceType,
    DevelopmentGoal,
    DevelopmentRoadmap,
    DevelopmentRoadmapItem,
    DrillResource,
    EndOfSeasonReport,
    EndOfSeasonReportItem,
    GoalStatus,
    PlayerDevelopmentLog,
    PlayerDrillAssignment,
    PlayerMetric,
    ProgressSnapshot,
    RoadmapTimeframe,
    SnapshotType,
)


def metric_trends_for_player(player, *, season=None):
    queryset = PlayerMetric.objects.filter(player=player).select_related("evaluation_event", "season")
    if season:
        queryset = queryset.filter(season=season)
    grouped = defaultdict(list)
    for metric in queryset.order_by("metric_key", "evaluation_event__evaluated_on", "id"):
        grouped[metric.metric_key].append(metric)
    trends = []
    for metric_key, entries in grouped.items():
        latest = entries[-1]
        previous = entries[-2] if len(entries) > 1 else None
        best = None
        numeric_entries = [entry.numeric_value for entry in entries if entry.numeric_value is not None]
        if numeric_entries:
            best = max(numeric_entries)
        change = None
        if previous and latest.numeric_value is not None and previous.numeric_value is not None:
            change = latest.numeric_value - previous.numeric_value
        trends.append(
            {
                "metric_key": metric_key,
                "display_name": latest.display_name,
                "category": latest.category,
                "latest": latest.numeric_value or latest.text_value or latest.raw_value,
                "previous": previous.numeric_value if previous else None,
                "change": change,
                "best": best,
                "unit": latest.unit,
                "direction": "up" if change and change > 0 else "down" if change and change < 0 else "flat",
            }
        )
    return sorted(trends, key=lambda item: (item["category"], item["display_name"]))


@transaction.atomic
def generate_progress_snapshot(player, *, season=None, evaluation_event=None, snapshot_type=SnapshotType.CUSTOM):
    trends = metric_trends_for_player(player, season=season)
    biggest_gains = [trend for trend in trends if trend["change"] not in (None, Decimal("0"))]
    biggest_gains.sort(key=lambda item: item["change"], reverse=True)
    strengths = []
    development_opportunities = []
    metric_summary = {}
    for trend in trends[:8]:
        metric_summary[trend["metric_key"]] = {
            "latest": str(trend["latest"]),
            "previous": str(trend["previous"]) if trend["previous"] is not None else "",
            "best": str(trend["best"]) if trend["best"] is not None else "",
            "direction": trend["direction"],
            "display_name": trend["display_name"],
        }
        if trend["direction"] == "up":
            strengths.append(f"{trend['display_name']} is trending upward.")
        else:
            development_opportunities.append(f"Keep building {trend['display_name']} with focused reps.")

    latest_logs = PlayerDevelopmentLog.objects.filter(player=player, season=season).order_by("-occurred_at")[:3]
    summary_parts = []
    if biggest_gains:
        top = biggest_gains[0]
        summary_parts.append(f"Best recent gain: {top['display_name']}.")
    if latest_logs:
        summary_parts.append(f"Recent coaching emphasis: {latest_logs[0].title}.")
    summary_parts.append("Next step: build consistency around the highest-impact development area.")

    return ProgressSnapshot.objects.create(
        player=player,
        season=season,
        evaluation_event=evaluation_event,
        snapshot_type=snapshot_type,
        title=f"{player.full_name} Progress Snapshot",
        summary=" ".join(summary_parts),
        strengths="\n".join(strengths[:3]),
        improvement_areas="\n".join(development_opportunities[:3]),
        next_priorities="\n".join(item["display_name"] for item in trends[:3]),
        metric_summary_data=metric_summary,
        source_data_snapshot={"trend_count": len(trends)},
    )


@transaction.atomic
def generate_development_roadmap(player, *, season=None):
    trends = metric_trends_for_player(player, season=season)
    active_goals = list(DevelopmentGoal.objects.filter(player=player, season=season, status=GoalStatus.ACTIVE)[:3])
    drills = list(DrillResource.objects.filter(is_active=True)[:5])
    roadmap = DevelopmentRoadmap.objects.create(
        player=player,
        season=season,
        title=f"{player.full_name} Development Roadmap",
        summary="A constructive, season-aware growth plan built from evaluations, goals, and coach notes.",
        strengths="\n".join(f"Asset to build on: {trend['display_name']}" for trend in trends if trend["direction"] == "up")[:1000],
        short_term_focus="\n".join(trend["display_name"] for trend in trends[:3]),
        medium_term_focus="Convert recent gains into repeatable game-ready habits.",
        offseason_focus="Protect movement quality, add athletic capacity, and keep foundational skill work consistent.",
        source_snapshot={"metric_count": len(trends), "goal_count": len(active_goals)},
        is_current=True,
    )
    DevelopmentRoadmap.objects.exclude(pk=roadmap.pk).filter(player=player, season=season).update(is_current=False)

    candidates = trends[:3] or [
        {"display_name": goal.title, "category": goal.category or "General"} for goal in active_goals
    ]
    for index, candidate in enumerate(candidates, start=1):
        linked_goal = active_goals[index - 1] if index - 1 < len(active_goals) else None
        linked_drill = drills[index - 1] if index - 1 < len(drills) else None
        DevelopmentRoadmapItem.objects.create(
            roadmap=roadmap,
            priority_level=index,
            display_order=index,
            category=candidate.get("category") or "General",
            title=f"Priority {index}: {candidate['display_name']}",
            description=f"Turn {candidate['display_name']} into a repeatable advantage with weekly focused work and coach check-ins.",
            target_metric_key=candidate.get("metric_key", ""),
            linked_goal=linked_goal,
            linked_drill_resource=linked_drill,
            timeframe=RoadmapTimeframe.SHORT_TERM if index == 1 else RoadmapTimeframe.MID_TERM,
        )
    return roadmap


@transaction.atomic
def draft_end_of_season_report(player, *, season, coach=None):
    report, _ = EndOfSeasonReport.objects.get_or_create(
        player=player,
        season=season,
        defaults={
            "coach": coach,
            "summary": "This report highlights assets to build on, meaningful gains, and the next development priorities.",
            "strengths": "Shows encouraging habits and transferable strengths across core baseball skills.",
            "development_opportunities": "Focus on high-upside areas with specific offseason targets.",
            "offseason_focus": "Build movement quality, strength, and skill consistency.",
        },
    )
    if report.items.exists():
        return report
    categories = [
        "Hitting",
        "Fielding",
        "Throwing",
        "Pitching",
        "Athleticism",
        "Baseball IQ",
        "Teamwork",
        "Coachability",
        "Effort",
        "Attitude",
        "Leadership",
        "Overall Development",
    ]
    for index, category in enumerate(categories, start=1):
        EndOfSeasonReportItem.objects.create(
            report=report,
            category=category,
            rating_value=3,
            text_feedback="Showing positive growth; the next step is turning flashes into repeatable results.",
            display_order=index,
        )
    return report


@transaction.atomic
def assign_drill_to_player(*, player, drill_resource, assigned_by=None, season=None, source_type=AssignmentSourceType.COACH, notes="", goal=None, roadmap_item=None, report=None):
    return PlayerDrillAssignment.objects.create(
        player=player,
        season=season,
        drill_resource=drill_resource,
        assigned_by=assigned_by,
        source_type=source_type,
        notes=notes,
        goal=goal,
        roadmap_item=roadmap_item,
        report=report,
    )

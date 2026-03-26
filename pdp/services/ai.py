from django.db import transaction

from pdp.models import AIAnalysisRun, AnalysisRunStatus, GeneratedByType, InsightAudience, InsightType, PlayerInsight
from pdp.services.development import metric_trends_for_player


def collect_player_analysis_context(player, *, season=None):
    trends = metric_trends_for_player(player, season=season)
    return {
        "player": {
            "id": player.id,
            "name": player.full_name,
            "level": player.level,
            "primary_position": player.primary_position,
        },
        "trends": trends[:10],
    }


def generate_player_summary(context: dict):
    player_name = context["player"]["name"]
    top_trend = context["trends"][0]["display_name"] if context["trends"] else "foundational skill work"
    return {
        "title": f"{player_name} Development Summary",
        "summary": f"{player_name} is building momentum. The clearest current opportunity is {top_trend}, with emphasis on consistent, game-ready execution.",
        "strengths": "Bring forward the athlete's best habits and confidence-building gains.",
        "development_opportunities": "Frame the next growth target as a specific training opportunity with clear feedback loops.",
        "recommended_actions": "Focus on one primary skill priority, pair it with one supporting drill, and review progress after the next evaluation.",
    }


@transaction.atomic
def persist_generated_insight(*, player, season=None, evaluation_event=None, analysis_run=None, payload=None):
    payload = payload or {}
    return PlayerInsight.objects.create(
        player=player,
        season=season,
        evaluation_event=evaluation_event,
        analysis_run=analysis_run,
        title=payload.get("title", f"{player.full_name} Insight"),
        summary=payload.get("summary", ""),
        strengths=payload.get("strengths", ""),
        development_opportunities=payload.get("development_opportunities", ""),
        recommended_actions=payload.get("recommended_actions", ""),
        generated_by_type=GeneratedByType.AI,
        insight_type=InsightType.SUMMARY,
        audience=InsightAudience.PLAYER,
    )


@transaction.atomic
def run_player_ai_analysis(*, player, season=None, evaluation_event=None, triggered_by=None):
    context = collect_player_analysis_context(player, season=season)
    run = AIAnalysisRun.objects.create(
        player=player,
        season=season,
        evaluation_event=evaluation_event,
        triggered_by=triggered_by,
        analysis_type="player_summary",
        provider="scaffold",
        model_name="offline-template",
        input_snapshot=context,
    )
    payload = generate_player_summary(context)
    insight = persist_generated_insight(
        player=player,
        season=season,
        evaluation_event=evaluation_event,
        analysis_run=run,
        payload=payload,
    )
    run.status = AnalysisRunStatus.COMPLETED
    run.summary = payload["summary"]
    run.output_payload = payload
    run.save(update_fields=["status", "summary", "output_payload", "updated_at"])
    return run, insight

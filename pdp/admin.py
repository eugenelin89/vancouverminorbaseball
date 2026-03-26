from django.contrib import admin

from pdp.models import (
    AIAnalysisRun,
    CoachAssignment,
    DevelopmentGoal,
    DevelopmentRoadmap,
    DevelopmentRoadmapItem,
    DrillResource,
    EndOfSeasonReport,
    EndOfSeasonReportItem,
    EvaluationEvent,
    EvaluationImport,
    EvaluationImportTemplate,
    ExternalPerformanceSource,
    ParentChildAccess,
    PlayerDevelopmentLog,
    PlayerDrillAssignment,
    PlayerEvaluation,
    PlayerInsight,
    PlayerMetric,
    PlayerProfile,
    ProgressSnapshot,
    ReportTemplate,
    Season,
)


class TimeStampedAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


@admin.register(Season)
class SeasonAdmin(TimeStampedAdmin):
    list_display = ("name", "year", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PlayerProfile)
class PlayerProfileAdmin(TimeStampedAdmin):
    list_display = ("full_name", "email", "level", "user", "must_change_password", "is_active")
    list_filter = ("is_active", "must_change_password", "level")
    search_fields = ("first_name", "last_name", "email", "external_player_id")


@admin.register(CoachAssignment)
class CoachAssignmentAdmin(TimeStampedAdmin):
    list_display = ("coach", "player", "season", "is_active")
    list_filter = ("season", "is_active")


@admin.register(ParentChildAccess)
class ParentChildAccessAdmin(TimeStampedAdmin):
    list_display = ("parent", "player", "relationship_label", "can_view_private_notes", "is_active")
    list_filter = ("can_view_private_notes", "is_active")


@admin.register(EvaluationImportTemplate)
class EvaluationImportTemplateAdmin(TimeStampedAdmin):
    list_display = ("name", "is_active", "created_by")


@admin.register(EvaluationImport)
class EvaluationImportAdmin(TimeStampedAdmin):
    list_display = ("file_name", "season", "status", "uploaded_by", "created_at")
    list_filter = ("status", "season")


@admin.register(EvaluationEvent)
class EvaluationEventAdmin(TimeStampedAdmin):
    list_display = ("name", "season", "event_type", "evaluated_on", "is_published")
    list_filter = ("event_type", "season", "is_published")


@admin.register(PlayerEvaluation)
class PlayerEvaluationAdmin(TimeStampedAdmin):
    list_display = ("player", "evaluation_event", "season", "source_sheet")
    search_fields = ("player__full_name", "evaluation_event__name")


@admin.register(PlayerMetric)
class PlayerMetricAdmin(TimeStampedAdmin):
    list_display = ("player", "display_name", "category", "numeric_value", "evaluation_event")
    list_filter = ("category", "season")
    search_fields = ("player__full_name", "display_name", "metric_key")


@admin.register(PlayerDevelopmentLog)
class PlayerDevelopmentLogAdmin(TimeStampedAdmin):
    list_display = ("player", "log_type", "title", "visibility", "occurred_at")
    list_filter = ("log_type", "visibility", "season")


@admin.register(DevelopmentGoal)
class DevelopmentGoalAdmin(TimeStampedAdmin):
    list_display = ("player", "title", "status", "due_date", "target_metric_key")
    list_filter = ("status", "season", "category")


class EndOfSeasonReportItemInline(admin.TabularInline):
    model = EndOfSeasonReportItem
    extra = 0


@admin.register(EndOfSeasonReport)
class EndOfSeasonReportAdmin(TimeStampedAdmin):
    list_display = ("player", "season", "coach", "overall_rating", "is_final")
    list_filter = ("season", "is_final")
    inlines = [EndOfSeasonReportItemInline]


@admin.register(ProgressSnapshot)
class ProgressSnapshotAdmin(TimeStampedAdmin):
    list_display = ("player", "season", "snapshot_type", "generated_by_type")
    list_filter = ("snapshot_type", "generated_by_type")


class DevelopmentRoadmapItemInline(admin.TabularInline):
    model = DevelopmentRoadmapItem
    extra = 0


@admin.register(DevelopmentRoadmap)
class DevelopmentRoadmapAdmin(TimeStampedAdmin):
    list_display = ("player", "season", "title", "generated_by_type", "is_current")
    list_filter = ("generated_by_type", "is_current")
    inlines = [DevelopmentRoadmapItemInline]


@admin.register(DrillResource)
class DrillResourceAdmin(TimeStampedAdmin):
    list_display = ("title", "category", "difficulty_level", "is_active")
    list_filter = ("category", "difficulty_level", "is_active")


@admin.register(PlayerDrillAssignment)
class PlayerDrillAssignmentAdmin(TimeStampedAdmin):
    list_display = ("player", "drill_resource", "status", "source_type", "due_date")
    list_filter = ("status", "source_type", "season")


@admin.register(AIAnalysisRun)
class AIAnalysisRunAdmin(TimeStampedAdmin):
    list_display = ("analysis_type", "player", "season", "status", "provider", "created_at")
    list_filter = ("status", "provider")


@admin.register(PlayerInsight)
class PlayerInsightAdmin(TimeStampedAdmin):
    list_display = ("player", "title", "generated_by_type", "audience", "is_current")
    list_filter = ("generated_by_type", "audience", "is_current")


@admin.register(ReportTemplate)
class ReportTemplateAdmin(TimeStampedAdmin):
    list_display = ("name", "season", "division", "is_default")


@admin.register(ExternalPerformanceSource)
class ExternalPerformanceSourceAdmin(TimeStampedAdmin):
    list_display = ("player", "provider_name", "source_type", "external_identifier", "last_synced_at")

# Register your models here.

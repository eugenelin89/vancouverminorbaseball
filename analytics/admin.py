from django.contrib import admin

from analytics.models import (
    EvaluationCycle,
    EvaluatorRole,
    Observation,
    ObservationQuestion,
    ObservationQuestionSet,
    ObservationResponse,
    ObservationSource,
    ObservationType,
)


class TimeStampedAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


@admin.register(EvaluationCycle)
class EvaluationCycleAdmin(TimeStampedAdmin):
    list_display = ("name", "cycle_type", "season", "is_active", "starts_on", "ends_on", "coach_assessment_question_set")
    list_filter = ("is_active", "cycle_type", "season")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ObservationType)
class ObservationTypeAdmin(TimeStampedAdmin):
    list_display = ("key", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("key", "name")


@admin.register(ObservationSource)
class ObservationSourceAdmin(TimeStampedAdmin):
    list_display = ("key", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("key", "name")


@admin.register(EvaluatorRole)
class EvaluatorRoleAdmin(TimeStampedAdmin):
    list_display = ("key", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("key", "name")


class ObservationQuestionInline(admin.TabularInline):
    model = ObservationQuestion
    extra = 0
    fields = ("display_order", "category", "key", "prompt", "response_type", "is_required", "is_active")


@admin.register(ObservationQuestion)
class ObservationQuestionAdmin(TimeStampedAdmin):
    list_display = ("prompt", "question_set", "category", "response_type", "display_order", "is_active")
    list_filter = ("question_set", "category", "response_type", "is_active")
    search_fields = ("prompt", "key", "question_set__name")


@admin.register(ObservationQuestionSet)
class ObservationQuestionSetAdmin(TimeStampedAdmin):
    list_display = ("name", "observation_type", "version", "is_active", "effective_from", "retired_on")
    list_filter = ("observation_type", "is_active")
    search_fields = ("name", "observation_type__key")
    inlines = [ObservationQuestionInline]


class ObservationResponseInline(admin.TabularInline):
    model = ObservationResponse
    extra = 0
    can_delete = False
    readonly_fields = (
        "question",
        "response_type",
        "numeric_value",
        "text_value",
        "boolean_value",
        "selected_choice",
        "raw_value",
        "unit",
        "payload",
        "metadata",
        "created_at",
        "updated_at",
    )
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Observation)
class ObservationAdmin(TimeStampedAdmin):
    list_display = (
        "player",
        "evaluation_cycle",
        "season",
        "observation_type",
        "status",
        "evaluator",
        "evaluator_role_name",
        "evaluation_perspective",
        "submitted_at",
    )
    list_filter = ("status", "season", "observation_type", "evaluation_cycle", "evaluator_role_key", "evaluation_perspective", "source")
    search_fields = ("player__first_name", "player__last_name", "evaluator__username", "evaluator__email")
    readonly_fields = TimeStampedAdmin.readonly_fields + (
        "submitted_at",
        "observation_type_key",
        "evaluator_role_key",
        "evaluator_role_name",
        "evaluation_perspective",
        "season_name_snapshot",
        "season_key_snapshot",
        "player_team_name_snapshot",
        "player_division_snapshot",
        "evaluator_team_name_snapshot",
        "evaluator_division_snapshot",
        "evaluator_assignment_role_snapshot",
    )
    inlines = [ObservationResponseInline]


@admin.register(ObservationResponse)
class ObservationResponseAdmin(TimeStampedAdmin):
    list_display = ("observation", "question", "response_type", "numeric_value", "text_preview")
    list_filter = ("response_type", "question__category")
    search_fields = ("observation__player__first_name", "observation__player__last_name", "question__prompt", "text_value")

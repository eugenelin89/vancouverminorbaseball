from django.contrib import admin

from analytics.models import (
    AssessmentEvent,
    AssessmentImportBatch,
    AssessmentImportRow,
    AssessmentImportTemplate,
    AssessmentMetricDefinition,
    AssessmentScoringProfile,
    AssessmentTemplate,
    AssessmentTemplateMetric,
    AssessmentValue,
    AssessmentValueCorrection,
    EvaluationCycle,
    EvaluatorRole,
    Observation,
    ObservationQuestion,
    ObservationQuestionSet,
    ObservationResponse,
    ObservationSource,
    ObservationType,
    PlayerAssessment,
)
from analytics.services.assessment_feature import assessments_enabled


class TimeStampedAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


class AssessmentFeatureAdminMixin:
    def get_model_perms(self, request):
        if not assessments_enabled():
            return {}
        return super().get_model_perms(request)


@admin.register(EvaluationCycle)
class EvaluationCycleAdmin(TimeStampedAdmin):
    list_display = (
        "name",
        "cycle_type",
        "season",
        "is_active",
        "starts_on",
        "ends_on",
        "coach_assessment_question_set",
    )
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
    fields = (
        "display_order",
        "category",
        "key",
        "prompt",
        "response_type",
        "is_required",
        "is_active",
    )


@admin.register(ObservationQuestion)
class ObservationQuestionAdmin(TimeStampedAdmin):
    list_display = (
        "prompt",
        "question_set",
        "category",
        "response_type",
        "display_order",
        "is_required",
        "is_active",
    )
    list_filter = (
        "question_set",
        "category",
        "response_type",
        "is_required",
        "is_active",
    )
    search_fields = ("prompt", "key", "question_set__name")


@admin.register(ObservationQuestionSet)
class ObservationQuestionSetAdmin(TimeStampedAdmin):
    list_display = (
        "name",
        "observation_type",
        "version",
        "is_active",
        "effective_from",
        "retired_on",
    )
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
    list_filter = (
        "status",
        "season",
        "observation_type",
        "evaluation_cycle",
        "evaluator_role_key",
        "evaluation_perspective",
        "source",
    )
    search_fields = (
        "player__first_name",
        "player__last_name",
        "evaluator__username",
        "evaluator__email",
    )
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
    list_display = (
        "observation",
        "question",
        "response_type",
        "numeric_value",
        "text_preview",
    )
    list_filter = ("response_type", "question__category")
    search_fields = (
        "observation__player__first_name",
        "observation__player__last_name",
        "question__prompt",
        "text_value",
    )


@admin.register(AssessmentMetricDefinition)
class AssessmentMetricDefinitionAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
    list_display = ("key", "name", "default_value_type", "default_unit", "is_active")
    list_filter = ("default_value_type", "is_active")
    search_fields = ("key", "name")

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.has_historical_use():
            fields.extend(
                [
                    "key",
                    "name",
                    "description",
                    "default_value_type",
                    "default_unit",
                    "metadata",
                ]
            )
        return fields

    def has_delete_permission(self, request, obj=None):
        return bool(
            super().has_delete_permission(request, obj)
            and not (obj and obj.has_historical_use())
        )


class AssessmentTemplateMetricInline(admin.TabularInline):
    model = AssessmentTemplateMetric
    extra = 0
    autocomplete_fields = ("metric",)
    fields = (
        "display_order",
        "category",
        "metric",
        "display_name",
        "value_type",
        "unit",
        "is_required",
        "direction",
    )

    def has_add_permission(self, request, obj=None):
        return bool(obj and not obj.is_locked and not obj.has_historical_use())

    def has_delete_permission(self, request, obj=None):
        return bool(obj and not obj.is_locked and not obj.has_historical_use())

    def get_readonly_fields(self, request, obj=None):
        if obj and (obj.is_locked or obj.has_historical_use()):
            return self.fields
        return ()


@admin.register(AssessmentTemplate)
class AssessmentTemplateAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
    list_display = ("name", "key", "version", "is_active", "is_locked")
    list_filter = ("is_active", "is_locked")
    search_fields = ("key", "name")
    inlines = [AssessmentTemplateMetricInline]

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and (obj.is_locked or obj.has_historical_use()):
            fields.extend(
                [
                    "key",
                    "name",
                    "version",
                    "description",
                    "effective_from",
                    "metadata",
                    "is_locked",
                ]
            )
        return fields

    def has_delete_permission(self, request, obj=None):
        return bool(
            super().has_delete_permission(request, obj)
            and not (obj and (obj.is_locked or obj.has_historical_use()))
        )


@admin.register(AssessmentTemplateMetric)
class AssessmentTemplateMetricAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
    list_display = (
        "display_name",
        "template",
        "category",
        "display_order",
        "value_type",
        "unit",
        "direction",
    )
    list_filter = ("template", "category", "value_type", "direction", "is_required")
    search_fields = ("display_name", "metric__key", "metric__name", "template__name")
    autocomplete_fields = ("template", "metric")

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and (obj.template.is_locked or obj.template.has_historical_use()):
            fields.extend(
                field.name for field in obj._meta.fields if field.name not in fields
            )
        return fields

    def has_delete_permission(self, request, obj=None):
        return bool(
            super().has_delete_permission(request, obj)
            and not (
                obj and (obj.template.is_locked or obj.template.has_historical_use())
            )
        )


@admin.register(AssessmentScoringProfile)
class AssessmentScoringProfileAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
    list_display = ("name", "key", "version", "is_active", "is_locked")
    list_filter = ("is_active", "is_locked")
    search_fields = ("key", "name")
    autocomplete_fields = ("assessment_template",)

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and (obj.is_locked or obj.has_committed_assessments()):
            fields.extend(
                [
                    "key",
                    "name",
                    "version",
                    "description",
                    "assessment_template",
                    "config",
                    "metadata",
                    "is_locked",
                ]
            )
        return fields

    def has_delete_permission(self, request, obj=None):
        return bool(
            super().has_delete_permission(request, obj)
            and not (obj and (obj.is_locked or obj.has_committed_assessments()))
        )


@admin.register(AssessmentImportTemplate)
class AssessmentImportTemplateAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
    list_display = ("name", "key", "version", "is_active", "is_locked")
    list_filter = ("is_active", "is_locked")
    search_fields = ("key", "name")
    autocomplete_fields = ("assessment_template",)

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and (obj.is_locked or obj.has_committed_imports()):
            fields.extend(
                [
                    "key",
                    "name",
                    "version",
                    "description",
                    "assessment_template",
                    "config",
                    "metadata",
                    "is_locked",
                ]
            )
        return fields

    def has_delete_permission(self, request, obj=None):
        return bool(
            super().has_delete_permission(request, obj)
            and not (obj and (obj.is_locked or obj.has_committed_imports()))
        )


@admin.register(AssessmentEvent)
class AssessmentEventAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
    list_display = ("name", "season", "division", "template", "is_active")
    list_filter = ("season", "division", "is_active", "template")
    search_fields = ("name", "slug", "season__name", "division")
    autocomplete_fields = ("template", "scoring_profile")
    prepopulated_fields = {"slug": ("name",)}

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.has_historical_use():
            fields.extend(
                [
                    "name",
                    "slug",
                    "season",
                    "division",
                    "starts_on",
                    "ends_on",
                    "template",
                    "scoring_profile",
                    "metadata",
                ]
            )
        return fields

    def has_delete_permission(self, request, obj=None):
        return bool(
            super().has_delete_permission(request, obj)
            and not (obj and obj.has_historical_use())
        )


class AssessmentValueInline(admin.TabularInline):
    model = AssessmentValue
    extra = 0
    can_delete = False
    readonly_fields = (
        "template_metric",
        "numeric_value",
        "rating_value",
        "text_value",
        "choice_value",
        "raw_value",
        "unit",
        "source_sheet",
        "source_row",
        "source_header",
        "source_kind",
        "is_manual_override",
        "metadata",
        "created_at",
        "updated_at",
    )
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PlayerAssessment)
class PlayerAssessmentAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
    list_display = ("player", "event", "status", "roster_membership", "import_batch")
    list_filter = ("event", "status", "event__season")
    search_fields = ("player__first_name", "player__last_name", "event__name")
    autocomplete_fields = ("player", "event", "roster_membership", "import_batch")
    inlines = [AssessmentValueInline]

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.status == "committed":
            fields.extend(
                [
                    "player",
                    "event",
                    "roster_membership",
                    "import_batch",
                    "source_row_key",
                    "status",
                    "metadata",
                ]
            )
        return fields

    def has_delete_permission(self, request, obj=None):
        return bool(
            super().has_delete_permission(request, obj)
            and not (obj and obj.status == "committed")
        )


@admin.register(AssessmentValue)
class AssessmentValueAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
    list_display = (
        "player_assessment",
        "template_metric",
        "numeric_value",
        "rating_value",
        "source_kind",
        "is_manual_override",
    )
    list_filter = ("template_metric__category", "source_kind", "is_manual_override")
    search_fields = (
        "player_assessment__player__first_name",
        "player_assessment__player__last_name",
        "template_metric__display_name",
    )
    autocomplete_fields = ("player_assessment", "template_metric", "import_row")

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.player_assessment.status == "committed":
            fields.extend(
                field.name for field in obj._meta.fields if field.name not in fields
            )
        return fields

    def has_delete_permission(self, request, obj=None):
        return bool(
            super().has_delete_permission(request, obj)
            and not (obj and obj.player_assessment.status == "committed")
        )


class AssessmentImportRowInline(admin.TabularInline):
    model = AssessmentImportRow
    extra = 0
    can_delete = False
    readonly_fields = (
        "row_key",
        "source_sheet",
        "source_row",
        "raw_identity",
        "player",
        "roster_membership",
        "action",
        "status",
        "match_status",
        "validation_status",
        "conflict_status",
        "errors",
        "warnings",
        "values_snapshot",
        "metric_changes",
        "raw_row",
        "metadata",
        "created_at",
        "updated_at",
    )
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AssessmentImportBatch)
class AssessmentImportBatchAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
    list_display = (
        "original_filename",
        "event",
        "status",
        "uploaded_by",
        "created_at",
        "committed_at",
    )
    list_filter = ("status", "event", "event__season")
    search_fields = ("original_filename", "workbook_sha256", "event__name")
    readonly_fields = TimeStampedAdmin.readonly_fields + (
        "event",
        "import_template",
        "uploaded_by",
        "original_filename",
        "status",
        "workbook_sha256",
        "preview_snapshot",
        "config_snapshot",
        "config_checksum",
        "validation_errors",
        "validation_warnings",
        "required_warning_codes",
        "preview_version",
        "acknowledgement_token",
        "warnings_acknowledged_at",
        "warnings_acknowledged_by",
        "import_summary",
        "committed_at",
        "metadata",
    )
    inlines = [AssessmentImportRowInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return bool(
            super().has_delete_permission(request, obj)
            and not (obj and obj.status == "committed")
        )


@admin.register(AssessmentImportRow)
class AssessmentImportRowAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
    list_display = ("batch", "source_sheet", "source_row", "raw_identity", "status")
    list_filter = ("status", "source_sheet", "batch__event")
    search_fields = ("raw_identity", "batch__original_filename", "batch__event__name")
    readonly_fields = TimeStampedAdmin.readonly_fields + (
        "batch",
        "row_key",
        "source_sheet",
        "source_row",
        "raw_identity",
        "player",
        "roster_membership",
        "action",
        "status",
        "match_status",
        "validation_status",
        "conflict_status",
        "raw_row",
        "values_snapshot",
        "metric_changes",
        "errors",
        "warnings",
        "metadata",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AssessmentValueCorrection)
class AssessmentValueCorrectionAdmin(AssessmentFeatureAdminMixin, TimeStampedAdmin):
    list_display = ("assessment_value", "actor", "created_at")
    search_fields = (
        "assessment_value__player_assessment__player__first_name",
        "assessment_value__player_assessment__player__last_name",
        "reason",
    )
    readonly_fields = tuple(
        field.name for field in AssessmentValueCorrection._meta.fields
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

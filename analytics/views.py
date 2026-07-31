from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, ListView, TemplateView, View

from analytics.assessment_forms import CoachAssessmentForm
from analytics.forms import (
    AssessmentImportRowResolutionForm,
    AssessmentImportUploadForm,
    PlayerImportMappingForm,
    PlayerImportUploadForm,
    parse_conflict_resolutions,
)
from analytics.models import (
    ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
    ASSESSMENT_IMPORT_ROW_INVALID,
    ASSESSMENT_IMPORT_ROW_UNMATCHED,
    EVALUATION_PERSPECTIVE_CHOICES,
    OBSERVATION_STATUS_SUBMITTED,
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    AssessmentEvent,
    AssessmentImportBatch,
    EvaluationCycle,
    Observation,
    PlayerAssessment,
)
from analytics.services.assessment_feature import assessments_enabled
from analytics.services.assessment_import_service import (
    assessment_records_for_player,
    commit_assessment_import_batch,
    create_assessment_import_batch,
    resolve_assessment_import_row,
    summarize_import_batch,
)
from analytics.services.coach_assessment_service import (
    assessment_status_for_players,
    get_active_coach_assessment_cycle,
    get_existing_coach_assessment,
    get_or_create_draft_coach_assessment,
    group_questions_for_display,
    list_memberships_for_assessment,
    reopen_observation,
)
from analytics.services.comparison_service import (
    get_player_comparison,
    get_player_score_summary,
)
from analytics.services.draft_service import get_draft_contexts_for_player
from analytics.services.evaluation_access_service import (
    active_evaluation_cycle,
    get_evaluation_target_list,
    get_my_evaluation_detail,
    get_my_evaluations,
    get_or_create_evaluation_for_player,
)
from analytics.services.evaluation_review_service import (
    get_evaluation_review_detail,
    get_evaluation_review_list,
)
from analytics.services.metrics_service import normalize_cycle_id
from analytics.services.observation_service import (
    get_observation_detail,
    save_observation_responses,
    submit_observation,
)
from analytics.services.permissions import (
    can_edit_observation,
    can_evaluate_player,
    can_reopen_observation,
    can_review_submitted_evaluations,
    can_submit_coach_assessment,
    can_submit_evaluation,
    can_view_my_evaluations,
    can_view_observation,
)
from analytics.services.player_service import (
    parse_player_search_filters,
    search_players,
    selected_players_from_ids,
    staff_player_queryset,
)
from analytics.services.reporting_service import get_command_center_context
from analytics.services.timeline_service import get_player_timeline
from players.models import Player, PlayerImportBatch
from players.services.import_service import (
    MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS,
    MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS,
    build_import_preview,
    commit_import_batch,
    create_import_batch,
    current_preview,
)
from seasons.models import PlayerRosterMembership


class AnalyticsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AssessmentFeatureRequiredMixin(AnalyticsStaffRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not assessments_enabled():
            raise Http404("Assessment events are not enabled.")
        return super().dispatch(request, *args, **kwargs)


class AnalyticsCommandCenterView(AnalyticsStaffRequiredMixin, TemplateView):
    template_name = "analytics/command_center.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cycle_id = normalize_cycle_id(self.request.GET.get("cycle"))
        division = self.request.GET.get("division", "").strip()
        team = self.request.GET.get("team", "").strip()
        command_center = get_command_center_context(
            cycle_id=cycle_id, division=division, team=team
        )
        context.update(
            {
                "command_center": command_center,
                "summary_cards": command_center.summary_cards,
                "completion_summary": command_center.completion_summary,
                "observation_summary": command_center.observation_summary,
                "import_summary": command_center.import_summary,
                "draft_summary": command_center.draft_summary,
                "recent_observations": command_center.recent_observations,
                "navigation_links": command_center.navigation_links,
                "filters": command_center.filters,
            }
        )
        return context


class PlayerImportListView(AnalyticsStaffRequiredMixin, ListView):
    model = PlayerImportBatch
    template_name = "analytics/import_list.html"
    context_object_name = "import_batches"
    paginate_by = 25

    def get_queryset(self):
        return PlayerImportBatch.objects.select_related("season", "uploaded_by")


class PlayerImportUploadView(AnalyticsStaffRequiredMixin, FormView):
    template_name = "analytics/import_upload.html"
    form_class = PlayerImportUploadForm

    def form_valid(self, form):
        batch = create_import_batch(
            file_obj=form.cleaned_data["csv_file"],
            source=form.cleaned_data["source"],
            uploaded_by=self.request.user,
            season=form.cleaned_data["season"],
            provision_player_accounts=form.cleaned_data.get(
                "provision_player_accounts", False
            ),
        )
        messages.success(
            self.request, "CSV uploaded. Review the import preview before committing."
        )
        return redirect("analytics:import-preview", pk=batch.pk)


class ImportBatchMixin(AnalyticsStaffRequiredMixin):
    import_batch = None

    def dispatch(self, request, *args, **kwargs):
        self.import_batch = get_object_or_404(PlayerImportBatch, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["import_batch"] = self.import_batch
        context["preview"] = current_preview(self.import_batch)
        return context


class PlayerImportPreviewView(ImportBatchMixin, TemplateView):
    template_name = "analytics/import_preview.html"

    def get_mapping_form(self, data=None):
        parsed = self.import_batch.preview_snapshot.get("parsed_csv", {})
        initial = self.import_batch.mapping_config
        return PlayerImportMappingForm(data=data, parsed=parsed, initial=initial)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mapping_form"] = kwargs.get("mapping_form") or self.get_mapping_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_mapping_form(data=request.POST)
        if form.is_valid():
            mapping_config = form.mapping_config()
            for key in [
                MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS,
                MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS,
            ]:
                mapping_config[key] = bool(self.import_batch.mapping_config.get(key))
            build_import_preview(
                import_batch=self.import_batch, mapping_config=mapping_config
            )
            messages.success(request, "Import preview refreshed.")
            return redirect("analytics:import-preview", pk=self.import_batch.pk)
        return self.render_to_response(self.get_context_data(mapping_form=form))


class PlayerImportConflictView(ImportBatchMixin, TemplateView):
    template_name = "analytics/import_conflicts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        preview = context.get("preview") or {}
        context["review_rows"] = [
            row
            for row in preview.get("rows", [])
            if row.get("action") == "needs_review" or row.get("errors")
        ]
        return context


class PlayerImportConfirmView(ImportBatchMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            result = commit_import_batch(
                import_batch=self.import_batch,
                actor=request.user,
                resolutions=parse_conflict_resolutions(request.POST),
            )
        except (PermissionDenied, ValidationError) as exc:
            messages.error(request, str(exc))
            return redirect("analytics:import-preview", pk=self.import_batch.pk)

        messages.success(
            request,
            f"Import committed. Created {result.created}, updated {result.updated}, skipped {result.skipped}.",
        )
        if result.errors:
            messages.warning(
                request, f"{len(result.errors)} row issue(s) were recorded."
            )
        return redirect("analytics:import-detail", pk=self.import_batch.pk)


class PlayerImportDetailView(ImportBatchMixin, TemplateView):
    template_name = "analytics/import_detail.html"


class PlayerSearchView(AnalyticsStaffRequiredMixin, TemplateView):
    template_name = "analytics/player_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filters = parse_player_search_filters(self.request.GET)
        search_result = search_players(filters)
        context.update(
            {
                "search_result": search_result,
                "players": search_result.players,
                "filters": filters,
                "active_tags": search_result.active_tags,
                "source_choices": search_result.source_choices,
                "result_count": search_result.result_count,
            }
        )
        return context


class PlayerProfileView(AnalyticsStaffRequiredMixin, TemplateView):
    template_name = "analytics/player_profile.html"

    def dispatch(self, request, *args, **kwargs):
        self.player = get_object_or_404(staff_player_queryset(), pk=kwargs["player_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        timeline = get_player_timeline(self.player)
        score_summary = get_player_score_summary(self.player)
        context.update(
            {
                "player": self.player,
                "tags": self.player.tags.filter(is_active=True).order_by("name"),
                "source_rows": self.player.source_rows.select_related(
                    "import_batch"
                ).order_by("-imported_at", "-id"),
                "draft_contexts": get_draft_contexts_for_player(self.player),
                "score_summary": score_summary,
                "timeline": timeline,
                "assessments_enabled": assessments_enabled(),
                "assessment_records": (
                    assessment_records_for_player(self.player)
                    if assessments_enabled()
                    else []
                ),
            }
        )
        return context


class AssessmentEventListView(AssessmentFeatureRequiredMixin, ListView):
    model = AssessmentEvent
    template_name = "analytics/assessment_event_list.html"
    context_object_name = "assessment_events"
    paginate_by = 25

    def get_queryset(self):
        return AssessmentEvent.objects.select_related(
            "season", "template", "scoring_profile"
        )


class AssessmentEventDetailView(AssessmentFeatureRequiredMixin, TemplateView):
    template_name = "analytics/assessment_event_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.assessment_event = get_object_or_404(
            AssessmentEvent.objects.select_related("season", "template"),
            pk=kwargs["event_id"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assessments = (
            PlayerAssessment.objects.filter(event=self.assessment_event)
            .select_related(
                "player", "roster_membership", "roster_membership__season_team"
            )
            .prefetch_related("values__template_metric")
        )
        context.update(
            {
                "assessment_event": self.assessment_event,
                "player_assessments": assessments,
            }
        )
        return context


class PlayerAssessmentDetailView(AssessmentFeatureRequiredMixin, TemplateView):
    template_name = "analytics/player_assessment_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.player_assessment = get_object_or_404(
            PlayerAssessment.objects.select_related(
                "player", "event", "event__season"
            ).prefetch_related(
                "values__template_metric", "values__template_metric__metric"
            ),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["player_assessment"] = self.player_assessment
        context["values"] = self.player_assessment.values.all()
        return context


class AssessmentImportListView(AssessmentFeatureRequiredMixin, ListView):
    model = AssessmentImportBatch
    template_name = "analytics/assessment_import_list.html"
    context_object_name = "import_batches"
    paginate_by = 25

    def get_queryset(self):
        return AssessmentImportBatch.objects.select_related(
            "event", "event__season", "uploaded_by"
        )


class AssessmentImportUploadView(AssessmentFeatureRequiredMixin, FormView):
    template_name = "analytics/assessment_import_upload.html"
    form_class = AssessmentImportUploadForm

    def form_valid(self, form):
        try:
            batch = create_assessment_import_batch(
                file_obj=form.cleaned_data["workbook"],
                event=form.cleaned_data["event"],
                import_template=form.cleaned_data["import_template"],
                uploaded_by=self.request.user,
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.render_to_response(self.get_context_data(form=form))
        messages.success(
            self.request,
            "Assessment workbook uploaded. Review matches before committing.",
        )
        return redirect("analytics:assessment-import-preview", pk=batch.pk)


class AssessmentImportBatchMixin(AssessmentFeatureRequiredMixin):
    assessment_import_batch = None

    def dispatch(self, request, *args, **kwargs):
        self.assessment_import_batch = get_object_or_404(
            AssessmentImportBatch.objects.select_related(
                "event", "event__season", "import_template"
            ),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["import_batch"] = self.assessment_import_batch
        context["summary"] = summarize_import_batch(self.assessment_import_batch)
        return context


class AssessmentImportPreviewView(AssessmentImportBatchMixin, TemplateView):
    template_name = "analytics/assessment_import_preview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rows"] = self.assessment_import_batch.rows.select_related(
            "player", "roster_membership"
        )
        return context


class AssessmentImportResolveView(AssessmentImportBatchMixin, TemplateView):
    template_name = "analytics/assessment_import_resolve.html"

    def _review_rows(self):
        return self.assessment_import_batch.rows.select_related("player").filter(
            status__in=[
                ASSESSMENT_IMPORT_ROW_UNMATCHED,
                ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
                ASSESSMENT_IMPORT_ROW_INVALID,
            ]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["forms"] = [
            (row, AssessmentImportRowResolutionForm(row=row))
            for row in self._review_rows()
        ]
        return context

    def post(self, request, *args, **kwargs):
        for row in self._review_rows():
            form = AssessmentImportRowResolutionForm(
                data={
                    "player": request.POST.get(f"row_{row.pk}_player", ""),
                    "skip": request.POST.get(f"row_{row.pk}_skip", ""),
                },
                row=row,
            )
            if form.is_valid():
                resolve_assessment_import_row(
                    row=row,
                    player=form.cleaned_data.get("player"),
                    skip=form.cleaned_data.get("skip"),
                )
        messages.success(request, "Assessment import resolutions updated.")
        return redirect(
            "analytics:assessment-import-preview",
            pk=self.assessment_import_batch.pk,
        )


class AssessmentImportConfirmView(AssessmentImportBatchMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            result = commit_assessment_import_batch(
                batch=self.assessment_import_batch,
                actor=request.user,
            )
        except (PermissionDenied, ValidationError) as exc:
            messages.error(request, str(exc))
            return redirect(
                "analytics:assessment-import-preview",
                pk=self.assessment_import_batch.pk,
            )
        messages.success(
            request,
            f"Assessment import committed. Created {result.created}, updated {result.updated}, skipped {result.skipped}.",
        )
        return redirect(
            "analytics:assessment-import-detail", pk=self.assessment_import_batch.pk
        )


class AssessmentImportDetailView(AssessmentImportBatchMixin, TemplateView):
    template_name = "analytics/assessment_import_detail.html"


class PlayerComparisonView(AnalyticsStaffRequiredMixin, TemplateView):
    template_name = "analytics/player_compare.html"

    def selected_player_ids(self):
        ids = list(self.request.GET.getlist("players"))
        player_ids = (self.request.GET.get("player_ids") or "").strip()
        if player_ids:
            ids.extend(
                [value.strip() for value in player_ids.split(",") if value.strip()]
            )
        return ids

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        players = selected_players_from_ids(self.selected_player_ids())
        comparison = get_player_comparison(players)
        search_result = search_players(parse_player_search_filters(self.request.GET))
        context.update(
            {
                "comparison": comparison,
                "selected_players": players,
                "players": search_result.players,
                "filters": search_result.filters,
                "active_tags": search_result.active_tags,
                "source_choices": search_result.source_choices,
            }
        )
        return context


class EvaluationSubmitterRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not can_submit_evaluation(request.user):
            raise PermissionDenied("You cannot submit evaluations.")
        return super().dispatch(request, *args, **kwargs)


class EvaluationListView(EvaluationSubmitterRequiredMixin, TemplateView):
    template_name = "analytics/evaluation_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_list = get_evaluation_target_list(self.request.user, self.request.GET)
        context.update(
            {
                "target_list": target_list,
                "cycle": target_list.cycle,
                "player_statuses": target_list.player_statuses,
                "query": target_list.query,
                "division": target_list.division,
                "team": target_list.team,
            }
        )
        return context


class EvaluationPlayerView(EvaluationSubmitterRequiredMixin, TemplateView):
    template_name = "analytics/evaluation_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.observation = None
        cycle = active_evaluation_cycle()
        if not cycle:
            messages.error(request, "No active evaluation cycle is available.")
            return redirect("analytics:evaluation-list")
        player = get_object_or_404(Player, pk=kwargs["player_id"], is_active=True)
        if not can_evaluate_player(request.user, player):
            raise PermissionDenied("You cannot evaluate this player.")
        membership = None
        membership_id = request.GET.get("membership") or request.POST.get("membership")
        if membership_id:
            membership = get_object_or_404(PlayerRosterMembership, pk=membership_id)
        self.observation = get_or_create_evaluation_for_player(
            request.user, player, cycle, player_roster_membership=membership
        )
        if self.observation.status == OBSERVATION_STATUS_SUBMITTED:
            return redirect(
                "analytics:assessment-detail", observation_id=self.observation.pk
            )
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, data=None, require_required=False):
        return CoachAssessmentForm(
            data=data,
            question_set=self.observation.question_set,
            observation=self.observation,
            require_required=require_required,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get("form") or self.get_form()
        context.update(
            {
                "observation": self.observation,
                "player": self.observation.player,
                "cycle": self.observation.evaluation_cycle,
                "question_set": self.observation.question_set,
                "form": form,
                "question_groups": form.question_groups(),
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action", "save_draft")
        form = self.get_form(data=request.POST, require_required=action == "submit")
        if form.is_valid():
            try:
                save_observation_responses(self.observation, form.response_payload())
                if action == "submit":
                    submit_observation(self.observation, actor=request.user)
                    messages.success(request, "Evaluation submitted.")
                    return redirect(
                        "analytics:assessment-detail",
                        observation_id=self.observation.pk,
                    )
                messages.success(request, "Evaluation draft saved.")
                return redirect(
                    "analytics:evaluation-player", player_id=self.observation.player_id
                )
            except ValidationError as exc:
                form.add_error(None, exc)
        return self.render_to_response(self.get_context_data(form=form))


class MyEvaluationsView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/my_evaluations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        players, evaluations = get_my_evaluations(self.request.user)
        context.update(
            {
                "players": players,
                "evaluations": evaluations,
                "has_self_link": bool(players),
                "selected_player": None,
            }
        )
        return context


class MyEvaluationsPlayerView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/my_evaluations.html"

    def dispatch(self, request, *args, **kwargs):
        self.player = get_object_or_404(Player, pk=kwargs["player_id"])
        if not can_view_my_evaluations(request.user, player=self.player):
            raise PermissionDenied("You cannot view evaluations for this player.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        players, evaluations = get_my_evaluations(self.request.user, player=self.player)
        context.update(
            {
                "players": players,
                "evaluations": evaluations,
                "has_self_link": bool(players),
                "selected_player": self.player,
            }
        )
        return context


class MyEvaluationDetailView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/my_evaluation_detail.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            self.detail = get_my_evaluation_detail(
                request.user, kwargs["observation_id"]
            )
        except Observation.DoesNotExist as exc:
            raise Http404("Evaluation not found.") from exc
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detail"] = self.detail
        return context


class EvaluationReviewRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not can_review_submitted_evaluations(
            request.user
        ):
            raise PermissionDenied("You cannot review submitted evaluations.")
        return super().dispatch(request, *args, **kwargs)


class EvaluationReviewListView(EvaluationReviewRequiredMixin, TemplateView):
    template_name = "analytics/evaluation_review_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review_list = get_evaluation_review_list(self.request.user, self.request.GET)
        context.update(
            {
                "review_list": review_list,
                "rows": review_list.rows,
                "filters": review_list.filters,
                "seasons": review_list.seasons,
                "cycles": review_list.cycles,
                "evaluator_roles": review_list.evaluator_roles,
                "perspective_choices": review_list.perspective_choices,
                "total_count": review_list.total_count,
            }
        )
        return context


class EvaluationReviewDetailView(EvaluationReviewRequiredMixin, TemplateView):
    template_name = "analytics/evaluation_review_detail.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            self.detail = get_evaluation_review_detail(
                request.user, kwargs["observation_id"]
            )
        except Observation.DoesNotExist as exc:
            raise Http404("Evaluation not found.") from exc
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detail"] = self.detail
        return context


class CoachAssessmentListView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/assessment_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cycle = get_active_coach_assessment_cycle(
            normalize_cycle_id(self.request.GET.get("cycle"))
        )
        query = self.request.GET.get("q", "").strip()
        division = self.request.GET.get("division", "").strip()
        team = self.request.GET.get("team", "").strip()
        players = Player.objects.none()
        player_statuses = []
        if cycle:
            players = list_memberships_for_assessment(
                cycle, query=query, division=division, team=team
            )
            player_statuses = assessment_status_for_players(
                list(players), cycle, self.request.user
            )
        context.update(
            {
                "cycle": cycle,
                "cycles": EvaluationCycle.objects.filter(
                    is_active=True,
                    coach_assessment_question_set__observation_type__key=OBSERVATION_TYPE_COACH_ASSESSMENT,
                ),
                "player_statuses": player_statuses,
                "query": query,
                "division": division,
                "team": team,
            }
        )
        return context


class CoachAssessmentEditView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/assessment_form.html"
    observation = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not can_submit_coach_assessment(
            request.user
        ):
            raise PermissionDenied("You cannot submit coach assessments.")
        if "observation_id" in kwargs:
            self.observation = get_object_or_404(
                Observation.objects.select_related(
                    "player", "evaluation_cycle", "question_set", "evaluator"
                ),
                pk=kwargs["observation_id"],
                observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
            )
            if not can_edit_observation(request.user, self.observation):
                if can_view_observation(request.user, self.observation):
                    return redirect(
                        "analytics:assessment-detail",
                        observation_id=self.observation.pk,
                    )
                raise PermissionDenied("You cannot edit this assessment.")
        else:
            cycle = get_active_coach_assessment_cycle(
                normalize_cycle_id(request.GET.get("cycle"))
            )
            if not cycle:
                messages.error(
                    request, "No active coach assessment cycle is available."
                )
                return redirect("analytics:assessment-list")
            player = get_object_or_404(Player, pk=kwargs["player_id"], is_active=True)
            if not can_evaluate_player(request.user, player):
                raise PermissionDenied("You cannot evaluate this player.")
            existing = get_existing_coach_assessment(player, cycle, request.user)
            if existing and existing.status == OBSERVATION_STATUS_SUBMITTED:
                return redirect(
                    "analytics:assessment-detail", observation_id=existing.pk
                )
            membership = None
            membership_id = request.GET.get("membership") or request.POST.get(
                "membership"
            )
            if membership_id:
                membership = get_object_or_404(PlayerRosterMembership, pk=membership_id)
            self.observation = get_or_create_draft_coach_assessment(
                player,
                cycle,
                request.user,
                player_roster_membership=membership,
            )
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, data=None, require_required=False):
        return CoachAssessmentForm(
            data=data,
            question_set=self.observation.question_set,
            observation=self.observation,
            require_required=require_required,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get("form") or self.get_form()
        context.update(
            {
                "observation": self.observation,
                "player": self.observation.player,
                "cycle": self.observation.evaluation_cycle,
                "question_set": self.observation.question_set,
                "form": form,
                "question_groups": form.question_groups(),
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action", "save_draft")
        form = self.get_form(data=request.POST, require_required=action == "submit")
        if form.is_valid():
            try:
                save_observation_responses(self.observation, form.response_payload())
                if action == "submit":
                    submit_observation(self.observation, actor=request.user)
                    messages.success(request, "Assessment submitted.")
                    return redirect(
                        "analytics:assessment-detail",
                        observation_id=self.observation.pk,
                    )
                messages.success(request, "Assessment draft saved.")
                return redirect(
                    "analytics:assessment-edit", observation_id=self.observation.pk
                )
            except ValidationError as exc:
                form.add_error(None, exc)
        return self.render_to_response(self.get_context_data(form=form))


class CoachAssessmentDetailView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/assessment_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.observation = get_object_or_404(
            Observation.objects.select_related(
                "player",
                "evaluation_cycle",
                "question_set",
                "evaluator",
                "evaluator_role",
            ),
            pk=kwargs["observation_id"],
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
        )
        if not can_view_observation(request.user, self.observation):
            raise PermissionDenied("You cannot view this assessment.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        observation = get_observation_detail(self.observation.pk)
        responses = {
            response.question_id: response for response in observation.responses.all()
        }
        question_groups = []
        for group in group_questions_for_display(observation.question_set):
            question_groups.append(
                {
                    "category": group["category"],
                    "questions": [
                        {"question": question, "response": responses.get(question.id)}
                        for question in group["questions"]
                    ],
                }
            )
        context.update(
            {
                "observation": observation,
                "question_groups": question_groups,
                "can_edit": can_edit_observation(self.request.user, observation),
                "back_url": reverse("analytics:assessment-list"),
            }
        )
        return context


class StaffObservationReviewListView(AnalyticsStaffRequiredMixin, ListView):
    template_name = "analytics/observation_review_list.html"
    context_object_name = "observations"
    paginate_by = 25

    def get_queryset(self):
        queryset = Observation.objects.select_related(
            "player",
            "evaluation_cycle",
            "season",
            "observation_type",
            "evaluator",
            "evaluator_role",
            "source",
        ).filter(observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT)
        status = self.request.GET.get("status", "").strip()
        cycle = normalize_cycle_id(self.request.GET.get("cycle"))
        q = self.request.GET.get("q", "").strip()
        if status:
            queryset = queryset.filter(status=status)
        if cycle:
            queryset = queryset.filter(evaluation_cycle_id=cycle)
        if q:
            queryset = queryset.filter(
                Q(player__first_name__icontains=q)
                | Q(player__last_name__icontains=q)
                | Q(evaluator__username__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cycles"] = EvaluationCycle.objects.filter(is_active=True)
        context["perspective_choices"] = EVALUATION_PERSPECTIVE_CHOICES
        return context


class StaffObservationReviewDetailView(
    AnalyticsStaffRequiredMixin, CoachAssessmentDetailView
):
    template_name = "analytics/assessment_review.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = reverse("analytics:observation-review-list")
        return context

    def post(self, request, *args, **kwargs):
        self.observation = get_object_or_404(
            Observation,
            pk=kwargs["observation_id"],
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
        )
        if request.POST.get("action") == "reopen" and can_reopen_observation(
            request.user, self.observation
        ):
            reopen_observation(self.observation, request.user)
            messages.success(request, "Assessment reopened for editing.")
        return redirect(
            "analytics:observation-review-detail", observation_id=self.observation.pk
        )

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, ListView, TemplateView, View

from analytics.assessment_forms import CoachAssessmentForm
from analytics.forms import PlayerImportMappingForm, PlayerImportUploadForm, parse_conflict_resolutions
from analytics.models import OBSERVATION_STATUS_SUBMITTED, OBSERVATION_TYPE_COACH_ASSESSMENT, EvaluationCycle, Observation
from analytics.services.coach_assessment_service import (
    assessment_status_for_players,
    get_active_coach_assessment_cycle,
    get_existing_coach_assessment,
    get_or_create_draft_coach_assessment,
    group_questions_for_display,
    list_players_for_assessment,
    reopen_observation,
)
from analytics.services.comparison_service import (
    get_player_comparison,
    get_player_score_summary,
)
from analytics.services.player_service import (
    parse_player_search_filters,
    search_players,
    selected_players_from_ids,
    staff_player_queryset,
)
from analytics.services.draft_service import get_draft_contexts_for_player
from analytics.services.observation_service import get_observation_detail, save_observation_responses, submit_observation
from analytics.services.permissions import (
    can_edit_observation,
    can_evaluate_player,
    can_reopen_observation,
    can_submit_coach_assessment,
    can_view_observation,
)
from analytics.services.metrics_service import normalize_cycle_id
from analytics.services.reporting_service import get_command_center_context
from analytics.services.timeline_service import get_player_timeline
from players.models import PlayerImportBatch
from players.models import Player
from players.services.import_service import (
    MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS,
    MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS,
    build_import_preview,
    commit_import_batch,
    create_import_batch,
    current_preview,
)


class AnalyticsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AnalyticsCommandCenterView(AnalyticsStaffRequiredMixin, TemplateView):
    template_name = "analytics/command_center.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cycle_id = normalize_cycle_id(self.request.GET.get("cycle"))
        division = self.request.GET.get("division", "").strip()
        team = self.request.GET.get("team", "").strip()
        command_center = get_command_center_context(cycle_id=cycle_id, division=division, team=team)
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


class PlayerImportUploadView(AnalyticsStaffRequiredMixin, FormView):
    template_name = "analytics/import_upload.html"
    form_class = PlayerImportUploadForm

    def form_valid(self, form):
        batch = create_import_batch(
            file_obj=form.cleaned_data["csv_file"],
            source=form.cleaned_data["source"],
            uploaded_by=self.request.user,
            provision_player_accounts=form.cleaned_data.get("provision_player_accounts", False),
        )
        messages.success(self.request, "CSV uploaded. Review the import preview before committing.")
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
            for key in [MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS, MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS]:
                mapping_config[key] = bool(self.import_batch.mapping_config.get(key))
            build_import_preview(import_batch=self.import_batch, mapping_config=mapping_config)
            messages.success(request, "Import preview refreshed.")
            return redirect("analytics:import-preview", pk=self.import_batch.pk)
        return self.render_to_response(self.get_context_data(mapping_form=form))


class PlayerImportConflictView(ImportBatchMixin, TemplateView):
    template_name = "analytics/import_conflicts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        preview = context.get("preview") or {}
        context["review_rows"] = [
            row for row in preview.get("rows", []) if row.get("action") == "needs_review" or row.get("errors")
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
            messages.warning(request, f"{len(result.errors)} row issue(s) were recorded.")
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
                "source_rows": self.player.source_rows.select_related("import_batch").order_by("-imported_at", "-id"),
                "draft_contexts": get_draft_contexts_for_player(self.player),
                "score_summary": score_summary,
                "timeline": timeline,
            }
        )
        return context


class PlayerComparisonView(AnalyticsStaffRequiredMixin, TemplateView):
    template_name = "analytics/player_compare.html"

    def selected_player_ids(self):
        ids = list(self.request.GET.getlist("players"))
        player_ids = (self.request.GET.get("player_ids") or "").strip()
        if player_ids:
            ids.extend([value.strip() for value in player_ids.split(",") if value.strip()])
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


class CoachAssessmentListView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/assessment_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cycle = get_active_coach_assessment_cycle(normalize_cycle_id(self.request.GET.get("cycle")))
        query = self.request.GET.get("q", "").strip()
        division = self.request.GET.get("division", "").strip()
        team = self.request.GET.get("team", "").strip()
        players = Player.objects.none()
        player_statuses = []
        if cycle:
            players = list_players_for_assessment(query=query, division=division, team=team)
            player_statuses = assessment_status_for_players(list(players), cycle, self.request.user)
        context.update(
            {
                "cycle": cycle,
                "cycles": EvaluationCycle.objects.filter(is_active=True, coach_assessment_question_set__observation_type__key=OBSERVATION_TYPE_COACH_ASSESSMENT),
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
        if request.user.is_authenticated and not can_submit_coach_assessment(request.user):
            raise PermissionDenied("You cannot submit coach assessments.")
        if "observation_id" in kwargs:
            self.observation = get_object_or_404(
                Observation.objects.select_related("player", "evaluation_cycle", "question_set", "evaluator"),
                pk=kwargs["observation_id"],
                observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
            )
            if not can_edit_observation(request.user, self.observation):
                if can_view_observation(request.user, self.observation):
                    return redirect("analytics:assessment-detail", observation_id=self.observation.pk)
                raise PermissionDenied("You cannot edit this assessment.")
        else:
            cycle = get_active_coach_assessment_cycle(normalize_cycle_id(request.GET.get("cycle")))
            if not cycle:
                messages.error(request, "No active coach assessment cycle is available.")
                return redirect("analytics:assessment-list")
            player = get_object_or_404(Player, pk=kwargs["player_id"], is_active=True)
            if not can_evaluate_player(request.user, player):
                raise PermissionDenied("You cannot evaluate this player.")
            existing = get_existing_coach_assessment(player, cycle, request.user)
            if existing and existing.status == OBSERVATION_STATUS_SUBMITTED:
                return redirect("analytics:assessment-detail", observation_id=existing.pk)
            self.observation = get_or_create_draft_coach_assessment(player, cycle, request.user)
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
                    return redirect("analytics:assessment-detail", observation_id=self.observation.pk)
                messages.success(request, "Assessment draft saved.")
                return redirect("analytics:assessment-edit", observation_id=self.observation.pk)
            except ValidationError as exc:
                form.add_error(None, exc)
        return self.render_to_response(self.get_context_data(form=form))


class CoachAssessmentDetailView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/assessment_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.observation = get_object_or_404(
            Observation.objects.select_related("player", "evaluation_cycle", "question_set", "evaluator", "evaluator_role"),
            pk=kwargs["observation_id"],
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
        )
        if not can_view_observation(request.user, self.observation):
            raise PermissionDenied("You cannot view this assessment.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        observation = get_observation_detail(self.observation.pk)
        responses = {response.question_id: response for response in observation.responses.all()}
        question_groups = []
        for group in group_questions_for_display(observation.question_set):
            question_groups.append(
                {
                    "category": group["category"],
                    "questions": [{"question": question, "response": responses.get(question.id)} for question in group["questions"]],
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
        queryset = Observation.objects.select_related("player", "evaluation_cycle", "observation_type", "evaluator", "source").filter(
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT
        )
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
        return context


class StaffObservationReviewDetailView(AnalyticsStaffRequiredMixin, CoachAssessmentDetailView):
    template_name = "analytics/assessment_review.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = reverse("analytics:observation-review-list")
        return context

    def post(self, request, *args, **kwargs):
        self.observation = get_object_or_404(Observation, pk=kwargs["observation_id"], observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT)
        if request.POST.get("action") == "reopen" and can_reopen_observation(request.user, self.observation):
            reopen_observation(self.observation, request.user)
            messages.success(request, "Assessment reopened for editing.")
        return redirect("analytics:observation-review-detail", observation_id=self.observation.pk)

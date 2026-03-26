from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, View

from pdp.forms import (
    DevelopmentLogForm,
    DrillAssignmentForm,
    GoalForm,
    ReportForm,
    ReportItemFormSet,
    WorkbookMappingForm,
    WorkbookUploadForm,
)
from pdp.models import (
    DevelopmentGoal,
    DrillResource,
    EndOfSeasonReport,
    EvaluationImport,
    EvaluationImportTemplate,
    ParentChildAccess,
    PlayerDevelopmentLog,
    PlayerProfile,
    ProgressSnapshot,
    Season,
)
from pdp.services.ai import run_player_ai_analysis
from pdp.services.development import (
    assign_drill_to_player,
    draft_end_of_season_report,
    generate_development_roadmap,
    generate_progress_snapshot,
    metric_trends_for_player,
)
from pdp.services.imports import deserialize_preview, execute_import, parse_workbook, serialize_preview
from pdp.services.permissions import (
    can_manage_imports,
    can_manage_player,
    can_view_player,
    get_accessible_players,
    visible_logs_for_user,
)


class PDPLoginView(LoginView):
    template_name = "pdp/login.html"


class PDPLogoutView(LogoutView):
    next_page = reverse_lazy("pdp:login")


class PDPPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "pdp/password_change.html"
    success_url = reverse_lazy("pdp:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        if hasattr(self.request.user, "player_profile"):
            profile = self.request.user.player_profile
            if profile.must_change_password:
                profile.must_change_password = False
                profile.save(update_fields=["must_change_password", "updated_at"])
        update_session_auth_hash(self.request, self.request.user)
        messages.success(self.request, "Password updated.")
        return response


class PDPHomeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if hasattr(request.user, "player_profile"):
            return redirect("pdp:player-dashboard", player_id=request.user.player_profile_id)
        if ParentChildAccess.objects.filter(parent=request.user, is_active=True).exists():
            return redirect("pdp:parent-dashboard")
        return redirect("pdp:coach-dashboard")


class StaffOrCoachRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser or self.request.user.coached_players.exists()


class PlayerAccessMixin(LoginRequiredMixin):
    player = None

    def dispatch(self, request, *args, **kwargs):
        self.player = get_object_or_404(
            PlayerProfile.objects.select_related("user"),
            pk=kwargs["player_id"],
        )
        if not can_view_player(request.user, self.player):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def _current_season():
    return Season.objects.filter(is_active=True).order_by("-year").first() or Season.objects.order_by("-year").first()


class PlayerDashboardView(PlayerAccessMixin, TemplateView):
    template_name = "pdp/player_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        season = _current_season()
        context.update(
            {
                "player": self.player,
                "season": season,
                "trends": metric_trends_for_player(self.player, season=season)[:8],
                "active_goals": self.player.goals.filter(season=season).exclude(status="archived")[:5],
                "recent_logs": visible_logs_for_user(
                    self.request.user,
                    self.player.development_logs.filter(season=season),
                )[:5],
                "insights": self.player.insights.filter(season=season)[:4],
                "roadmap": self.player.roadmaps.filter(season=season, is_current=True).prefetch_related("items").first(),
                "snapshots": self.player.snapshots.filter(season=season)[:4],
                "drill_assignments": self.player.drill_assignments.filter(season=season).select_related("drill_resource")[:5],
                "report": self.player.season_reports.filter(season=season).first(),
                "can_manage_player": can_manage_player(self.request.user, self.player),
            }
        )
        return context


class EvaluationHistoryView(PlayerAccessMixin, TemplateView):
    template_name = "pdp/evaluation_history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        season = _current_season()
        metrics = (
            self.player.metrics.filter(season=season)
            .select_related("evaluation_event")
            .order_by("category", "display_name", "evaluation_event__evaluated_on")
        )
        grouped = {}
        for metric in metrics:
            grouped.setdefault(metric.category or "General", []).append(metric)
        context.update(
            {
                "player": self.player,
                "season": season,
                "metric_groups": grouped,
                "trends": metric_trends_for_player(self.player, season=season),
            }
        )
        return context


class DevelopmentLogView(PlayerAccessMixin, TemplateView):
    template_name = "pdp/development_logs.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not can_manage_player(request.user, self.player):
            raise PermissionDenied
        form = DevelopmentLogForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.player = self.player
            entry.season = _current_season()
            entry.author = request.user
            entry.save()
            messages.success(request, "Development log added.")
            return redirect("pdp:development-logs", player_id=self.player.id)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        season = _current_season()
        context.update(
            {
                "player": self.player,
                "season": season,
                "logs": visible_logs_for_user(
                    self.request.user,
                    self.player.development_logs.filter(season=season),
                ),
                "form": kwargs.get("form") or DevelopmentLogForm(),
                "can_manage_player": can_manage_player(self.request.user, self.player),
            }
        )
        return context


class GoalView(PlayerAccessMixin, TemplateView):
    template_name = "pdp/goals.html"

    def post(self, request, *args, **kwargs):
        if not can_manage_player(request.user, self.player):
            raise PermissionDenied
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.player = self.player
            goal.season = _current_season()
            goal.created_by = request.user
            goal.save()
            messages.success(request, "Goal saved.")
            return redirect("pdp:goals", player_id=self.player.id)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        season = _current_season()
        context.update(
            {
                "player": self.player,
                "season": season,
                "active_goals": self.player.goals.filter(season=season).exclude(status="archived"),
                "completed_goals": self.player.goals.filter(season=season, status="completed"),
                "form": kwargs.get("form") or GoalForm(),
                "can_manage_player": can_manage_player(self.request.user, self.player),
            }
        )
        return context


class CoachDashboardView(StaffOrCoachRequiredMixin, TemplateView):
    template_name = "pdp/coach_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        season = _current_season()
        players = get_accessible_players(self.request.user).prefetch_related("goals", "snapshots", "season_reports")
        context.update(
            {
                "season": season,
                "players": players,
                "follow_up_players": players.annotate(goal_count=Count("goals")).order_by("goal_count", "last_name")[:6],
                "missing_reports": players.exclude(season_reports__season=season)[:6],
                "recent_imports": EvaluationImport.objects.filter(season=season)[:5],
            }
        )
        return context


class ParentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "pdp/parent_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        children = get_accessible_players(self.request.user)
        context["children"] = children
        context["season"] = _current_season()
        return context


class ImportWorkbenchView(LoginRequiredMixin, TemplateView):
    template_name = "pdp/import_workbench.html"

    def dispatch(self, request, *args, **kwargs):
        if not can_manage_imports(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "confirm_import" in request.POST:
            preview_payload = request.POST.get("preview_payload", "")
            mapping_form = WorkbookMappingForm(request.POST, preview_payload=preview_payload)
            if mapping_form.is_valid():
                preview = deserialize_preview(preview_payload)
                template = None
                template_id = mapping_form.cleaned_data.get("template_id")
                if template_id:
                    template = EvaluationImportTemplate.objects.filter(pk=template_id).first()
                import_record = EvaluationImport.objects.create(
                    template=template,
                    uploaded_by=request.user,
                    file_name=preview.get("file_name", "workbook"),
                    status="previewed",
                )
                mapping_config = mapping_form.build_mapping_config()
                if mapping_form.cleaned_data.get("save_as_template"):
                    EvaluationImportTemplate.objects.update_or_create(
                        name=mapping_form.cleaned_data["template_name"],
                        defaults={
                            "description": "Saved from import workbench.",
                            "configuration": mapping_config,
                            "created_by": request.user,
                            "is_active": True,
                        },
                    )
                results, event = execute_import(
                    import_record=import_record,
                    preview=preview,
                    mapping_config=mapping_config,
                    provision_accounts=mapping_form.cleaned_data.get("provision_accounts", False),
                )
                messages.success(request, f"Imported evaluation data for {event.name}.")
                if results["errors"]:
                    messages.warning(request, f"{len(results['errors'])} row(s) need review.")
                request.session["pdp_onboarding_report"] = [
                    result.__dict__ for result in results["onboarding_report"]
                ]
                return redirect("pdp:import-workbench")
            context = self.get_context_data(mapping_form=mapping_form)
            return self.render_to_response(context)

        upload_form = WorkbookUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            preview = parse_workbook(upload_form.cleaned_data["workbook"])
            preview_payload = serialize_preview(preview)
            mapping_form = WorkbookMappingForm(
                preview_payload=preview_payload,
                initial={
                    "preview_payload": preview_payload,
                    "season_id": upload_form.cleaned_data["season"].id,
                    "event_name": upload_form.cleaned_data["event_name"],
                    "evaluated_on": upload_form.cleaned_data["evaluated_on"].isoformat(),
                    "event_type": upload_form.cleaned_data["event_type"],
                    "template_id": getattr(upload_form.cleaned_data.get("template"), "id", ""),
                    "create_missing_players": upload_form.cleaned_data["create_missing_players"],
                    "provision_accounts": upload_form.cleaned_data["provision_accounts"],
                },
            )
            context = self.get_context_data(
                upload_form=upload_form,
                mapping_form=mapping_form,
                preview=preview,
            )
            return self.render_to_response(context)
        return self.render_to_response(self.get_context_data(upload_form=upload_form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("upload_form", WorkbookUploadForm())
        context.setdefault("mapping_form", None)
        context["preview"] = kwargs.get("preview")
        context["recent_imports"] = EvaluationImport.objects.select_related("season", "uploaded_by")[:8]
        context["onboarding_report"] = self.request.session.pop("pdp_onboarding_report", [])
        return context


class AIInsightsView(PlayerAccessMixin, TemplateView):
    template_name = "pdp/ai_insights.html"

    def post(self, request, *args, **kwargs):
        if not can_manage_player(request.user, self.player):
            raise PermissionDenied
        run_player_ai_analysis(player=self.player, season=_current_season(), triggered_by=request.user)
        messages.success(request, "AI insight scaffold generated.")
        return redirect("pdp:ai-insights", player_id=self.player.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["player"] = self.player
        context["season"] = _current_season()
        context["insights"] = self.player.insights.all()
        context["analysis_runs"] = self.player.analysis_runs.all()
        context["can_manage_player"] = can_manage_player(self.request.user, self.player)
        return context


class ReportCardView(PlayerAccessMixin, TemplateView):
    template_name = "pdp/report_card.html"

    def post(self, request, *args, **kwargs):
        if not can_manage_player(request.user, self.player):
            raise PermissionDenied
        report = draft_end_of_season_report(self.player, season=_current_season(), coach=request.user)
        form = ReportForm(request.POST, instance=report)
        formset = ReportItemFormSet(request.POST, instance=report)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Report card updated.")
            return redirect("pdp:report-card", player_id=self.player.id)
        context = self.get_context_data(form=form, formset=formset)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = draft_end_of_season_report(self.player, season=_current_season(), coach=self.request.user)
        context.update(
            {
                "player": self.player,
                "season": _current_season(),
                "report": report,
                "form": kwargs.get("form") or ReportForm(instance=report),
                "formset": kwargs.get("formset") or ReportItemFormSet(instance=report),
                "can_manage_player": can_manage_player(self.request.user, self.player),
            }
        )
        return context


class SnapshotView(PlayerAccessMixin, TemplateView):
    template_name = "pdp/snapshots.html"

    def post(self, request, *args, **kwargs):
        if not can_manage_player(request.user, self.player):
            raise PermissionDenied
        generate_progress_snapshot(self.player, season=_current_season())
        messages.success(request, "Progress snapshot generated.")
        return redirect("pdp:snapshots", player_id=self.player.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["player"] = self.player
        context["season"] = _current_season()
        context["snapshots"] = self.player.snapshots.filter(season=_current_season())
        context["can_manage_player"] = can_manage_player(self.request.user, self.player)
        return context


class RoadmapView(PlayerAccessMixin, TemplateView):
    template_name = "pdp/roadmap.html"

    def post(self, request, *args, **kwargs):
        if not can_manage_player(request.user, self.player):
            raise PermissionDenied
        generate_development_roadmap(self.player, season=_current_season())
        messages.success(request, "Development roadmap refreshed.")
        return redirect("pdp:roadmap", player_id=self.player.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        roadmap = self.player.roadmaps.filter(season=_current_season(), is_current=True).prefetch_related("items").first()
        context.update(
            {
                "player": self.player,
                "season": _current_season(),
                "roadmap": roadmap,
                "previous_roadmaps": self.player.roadmaps.exclude(pk=getattr(roadmap, "pk", None))[:5],
                "can_manage_player": can_manage_player(self.request.user, self.player),
            }
        )
        return context


class DrillLibraryView(LoginRequiredMixin, TemplateView):
    template_name = "pdp/drill_library.html"

    def post(self, request, *args, **kwargs):
        player = get_object_or_404(PlayerProfile, pk=request.POST.get("player_id"))
        if not can_manage_player(request.user, player):
            raise PermissionDenied
        form = DrillAssignmentForm(request.POST)
        if form.is_valid():
            assign_drill_to_player(
                player=player,
                drill_resource=form.cleaned_data["drill_resource"],
                assigned_by=request.user,
                season=_current_season(),
                source_type=form.cleaned_data["source_type"],
                notes=form.cleaned_data["notes"],
            )
            messages.success(request, "Drill assigned.")
            return redirect("pdp:drill-library")
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.request.GET.get("category", "").strip()
        drills = DrillResource.objects.filter(is_active=True)
        if category:
            drills = drills.filter(category__iexact=category)
        context["drills"] = drills
        context["categories"] = DrillResource.objects.filter(is_active=True).values_list("category", flat=True).distinct()
        context["form"] = kwargs.get("form") or DrillAssignmentForm()
        context["players"] = get_accessible_players(self.request.user)
        context["selected_category"] = category
        return context

# Create your views here.

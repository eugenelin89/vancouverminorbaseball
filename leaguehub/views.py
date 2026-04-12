from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView, View

from leaguehub.forms import (
    AdminScoreOverrideForm,
    CoachUserForm,
    GamePhotoForm,
    GameForm,
    GameStoryForm,
    LeagueForm,
    LeagueSeasonForm,
    SeasonForm,
    ScoreSubmissionForm,
    ScoreVerificationForm,
    TeamCoachAssignmentForm,
    TeamForm,
)
from leaguehub.models import Game, LeagueSeason, Team
from leaguehub.services.content import save_game_photo, save_game_story
from leaguehub.services.permissions import can_submit_score, can_verify_score, is_league_admin
from leaguehub.services.presentation import (
    get_dashboard_context,
    get_index_context,
    get_navigation_context,
    get_results_context,
    get_team_context,
    serialize_game_for_display,
    serialize_standings_for_display,
)
from leaguehub.services.score_workflow import admin_override_score, submit_home_score, verify_game_score

class LeagueSeasonMixin:
    league_season = None

    def dispatch(self, request, *args, **kwargs):
        self.league_season = get_object_or_404(
            LeagueSeason.objects.select_related("league", "season"),
            league__slug=kwargs["league_slug"],
            season__slug=kwargs["season_slug"],
        )
        return super().dispatch(request, *args, **kwargs)


class LeagueHubAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_league_admin(self.request.user)


class LeagueHubIndexView(TemplateView):
    template_name = "leaguehub/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_index_context(user=self.request.user))
        context.update(get_navigation_context())
        return context


class LeagueHubManageView(LeagueHubAdminRequiredMixin, TemplateView):
    template_name = "leaguehub/manage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_navigation_context())
        context["season_form"] = kwargs.get("season_form") or SeasonForm()
        context["league_form"] = kwargs.get("league_form") or LeagueForm()
        context["league_season_form"] = kwargs.get("league_season_form") or LeagueSeasonForm()
        context["team_form"] = kwargs.get("team_form") or TeamForm()
        context["coach_user_form"] = kwargs.get("coach_user_form") or CoachUserForm()
        context["coach_assignment_form"] = kwargs.get("coach_assignment_form") or TeamCoachAssignmentForm()
        context["game_form"] = kwargs.get("game_form") or GameForm()
        context["recent_seasons"] = LeagueSeason.objects.select_related("league", "season").order_by("-created_at")[:8]
        context["recent_teams"] = Team.objects.select_related("league_season", "league_season__league").order_by("-created_at")[:10]
        context["recent_games"] = Game.objects.select_related("league_season", "home_team", "away_team").order_by("-created_at")[:10]
        return context


class LeagueHubManagementCreateView(LeagueHubAdminRequiredMixin, FormView):
    template_name = "leaguehub/manage.html"
    success_anchor = "operations"
    form_context_key = None

    def get_success_url(self):
        return f"{reverse('leaguehub:manage')}#{self.success_anchor}"

    def get_context_data(self, **kwargs):
        context = LeagueHubManageView().get_context_data(**kwargs)
        context.update(kwargs)
        return context

    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, self.get_success_message(obj))
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        context = LeagueHubManageView().get_context_data(**{self.form_context_key: form})
        return self.render_to_response(context)

    def get_success_message(self, obj):
        return f"Created {obj}."


class SeasonCreateView(LeagueHubManagementCreateView):
    form_class = SeasonForm
    form_context_key = "season_form"
    success_anchor = "season"

    def get_success_message(self, obj):
        return f"Season '{obj.name}' created."


class LeagueCreateView(LeagueHubManagementCreateView):
    form_class = LeagueForm
    form_context_key = "league_form"
    success_anchor = "league"

    def get_success_message(self, obj):
        return f"League '{obj.name}' created."


class LeagueSeasonCreateView(LeagueHubManagementCreateView):
    form_class = LeagueSeasonForm
    form_context_key = "league_season_form"
    success_anchor = "league-season"

    def get_success_message(self, obj):
        return f"League season '{obj.title}' created."


class TeamCreateView(LeagueHubManagementCreateView):
    form_class = TeamForm
    form_context_key = "team_form"
    success_anchor = "team"

    def get_success_message(self, obj):
        return f"Team '{obj.name}' created."


class CoachUserCreateView(LeagueHubManagementCreateView):
    form_class = CoachUserForm
    form_context_key = "coach_user_form"
    success_anchor = "coach"

    def get_success_message(self, obj):
        return f"Coach user '{obj.get_full_name() or obj.username}' created."


class CoachAssignmentCreateView(LeagueHubManagementCreateView):
    form_class = TeamCoachAssignmentForm
    form_context_key = "coach_assignment_form"
    success_anchor = "assignment"

    def get_success_message(self, obj):
        return f"Assigned {obj.user.get_full_name() or obj.user.username} to {obj.team.name}."


class GameCreateView(LeagueHubManagementCreateView):
    form_class = GameForm
    form_context_key = "game_form"
    success_anchor = "game"

    def get_success_message(self, obj):
        return f"Game '{obj}' created."


class GameMixin:
    game = None

    def dispatch(self, request, *args, **kwargs):
        self.game = get_object_or_404(
            Game.objects.select_related("league_season", "league_season__league", "league_season__season", "home_team", "away_team")
            .prefetch_related("stories", "photos"),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("leaguehub:game-detail", kwargs={"pk": self.game.pk})


class LeagueSeasonDashboardView(LeagueSeasonMixin, TemplateView):
    template_name = "leaguehub/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_dashboard_context(league_season=self.league_season, user=self.request.user))
        context.update(get_navigation_context(current_league_season=self.league_season))
        return context


class StandingsView(LeagueSeasonMixin, TemplateView):
    template_name = "leaguehub/standings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["league_season"] = self.league_season
        context["standings"] = serialize_standings_for_display(league_season=self.league_season)
        context.update(get_navigation_context(current_league_season=self.league_season))
        return context


class ResultsListView(LeagueSeasonMixin, TemplateView):
    template_name = "leaguehub/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_results_context(league_season=self.league_season, user=self.request.user))
        context.update(get_navigation_context(current_league_season=self.league_season))
        return context


class TeamDetailView(LeagueSeasonMixin, TemplateView):
    template_name = "leaguehub/team_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = get_object_or_404(
            Team.objects.select_related("league_season", "league_season__league", "league_season__season"),
            league_season=self.league_season,
            slug=self.kwargs["team_slug"],
        )
        context.update(get_team_context(team=team, user=self.request.user))
        context.update(get_navigation_context(current_league_season=self.league_season, current_team=team))
        return context


class GameDetailView(GameMixin, TemplateView):
    template_name = "leaguehub/game_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game_display"] = serialize_game_for_display(self.game, user=self.request.user)
        context["league_season"] = self.game.league_season
        context.update(get_navigation_context(current_league_season=self.game.league_season))
        context["score_form"] = kwargs.get("score_form") or ScoreSubmissionForm(
            initial={"home_score": self.game.home_score, "away_score": self.game.away_score}
        )
        context["admin_score_form"] = kwargs.get("admin_score_form") or AdminScoreOverrideForm(
            initial={"home_score": self.game.home_score, "away_score": self.game.away_score, "require_reverification": False}
        )
        context["verify_form"] = kwargs.get("verify_form") or ScoreVerificationForm(initial={"confirm": True})
        context["home_story_form"] = kwargs.get("home_story_form") or GameStoryForm(
            initial={
                "headline": getattr(context["game_display"]["home_story"], "headline", ""),
                "story": getattr(context["game_display"]["home_story"], "story", ""),
            }
        )
        context["away_story_form"] = kwargs.get("away_story_form") or GameStoryForm(
            initial={
                "headline": getattr(context["game_display"]["away_story"], "headline", ""),
                "story": getattr(context["game_display"]["away_story"], "story", ""),
            }
        )
        context["home_photo_form"] = kwargs.get("home_photo_form") or GamePhotoForm()
        context["away_photo_form"] = kwargs.get("away_photo_form") or GamePhotoForm()
        return context


class GameScoreSubmitView(LoginRequiredMixin, GameMixin, View):
    def post(self, request, *args, **kwargs):
        if is_league_admin(request.user):
            form = AdminScoreOverrideForm(request.POST)
            if form.is_valid():
                try:
                    result = admin_override_score(
                        game=self.game,
                        actor=request.user,
                        home_score=form.cleaned_data["home_score"],
                        away_score=form.cleaned_data["away_score"],
                        note=form.cleaned_data["note"],
                        require_reverification=form.cleaned_data["require_reverification"],
                    )
                except ValidationError as exc:
                    form.add_error(None, exc.message)
                else:
                    if result.audit_entry:
                        if result.game.verification_status == "verified_final":
                            messages.success(request, "Admin score saved, audited, and verified as final.")
                        else:
                            messages.success(request, "Admin score override saved with audit entry.")
                    return redirect(self.get_success_url())
        else:
            if not can_submit_score(request.user, self.game):
                raise PermissionDenied
            form = ScoreSubmissionForm(request.POST)
            if form.is_valid():
                try:
                    submit_home_score(
                        game=self.game,
                        actor=request.user,
                        home_score=form.cleaned_data["home_score"],
                        away_score=form.cleaned_data["away_score"],
                    )
                except ValidationError as exc:
                    form.add_error(None, exc.message)
                else:
                    messages.success(request, "Score submitted and awaiting away-team verification.")
                    return redirect(self.get_success_url())

        detail_view = GameDetailView()
        detail_view.setup(request, *args, **kwargs)
        detail_view.game = self.game
        return detail_view.render_to_response(
            detail_view.get_context_data(
                score_form=form if not is_league_admin(request.user) else None,
                admin_score_form=form if is_league_admin(request.user) else None,
            )
        )


class GameScoreVerifyView(LoginRequiredMixin, GameMixin, View):
    def post(self, request, *args, **kwargs):
        if not can_verify_score(request.user, self.game):
            raise PermissionDenied
        form = ScoreVerificationForm(request.POST)
        if form.is_valid():
            try:
                verify_game_score(game=self.game, actor=request.user)
            except ValidationError as exc:
                form.add_error(None, exc.message)
            else:
                messages.success(request, "Score verified as final.")
                return redirect(self.get_success_url())
        detail_view = GameDetailView()
        detail_view.setup(request, *args, **kwargs)
        detail_view.game = self.game
        return detail_view.render_to_response(detail_view.get_context_data(verify_form=form))


class TeamContentMixin(LoginRequiredMixin, GameMixin):
    team = None

    def dispatch(self, request, *args, **kwargs):
        self.team = get_object_or_404(Team, pk=kwargs["team_id"])
        return super().dispatch(request, *args, **kwargs)


class GameStorySubmitView(TeamContentMixin, View):
    def post(self, request, *args, **kwargs):
        form = GameStoryForm(request.POST)
        if form.is_valid():
            try:
                save_game_story(
                    game=self.game,
                    team=self.team,
                    actor=request.user,
                    headline=form.cleaned_data["headline"],
                    story_text=form.cleaned_data["story"],
                )
            except ValidationError as exc:
                form.add_error(None, exc.message)
            else:
                messages.success(request, "Game story saved.")
                return redirect(self.get_success_url())

        detail_view = GameDetailView()
        detail_view.setup(request, *args, **kwargs)
        detail_view.game = self.game
        key = "home_story_form" if self.team.pk == self.game.home_team_id else "away_story_form"
        return detail_view.render_to_response(detail_view.get_context_data(**{key: form}))


class GamePhotoSubmitView(TeamContentMixin, View):
    def post(self, request, *args, **kwargs):
        form = GamePhotoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                save_game_photo(
                    game=self.game,
                    team=self.team,
                    actor=request.user,
                    image=form.cleaned_data["image"],
                    caption=form.cleaned_data["caption"],
                )
            except ValidationError as exc:
                form.add_error(None, exc.message)
            else:
                messages.success(request, "Game photo uploaded.")
                return redirect(self.get_success_url())

        detail_view = GameDetailView()
        detail_view.setup(request, *args, **kwargs)
        detail_view.game = self.game
        key = "home_photo_form" if self.team.pk == self.game.home_team_id else "away_photo_form"
        return detail_view.render_to_response(detail_view.get_context_data(**{key: form}))

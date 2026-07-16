from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, ListView

from seasons.forms import SeasonTeamForm
from seasons.models import Season, SeasonTeam
from seasons.services.season_query_service import (
    season_options_queryset,
    team_list_queryset,
)
from seasons.services.team_service import get_or_create_season_team, update_season_team
from seasons.views.mixins import (
    SeasonOperationsStaffRequiredMixin,
    SeasonPaginationMixin,
)


class SeasonTeamListView(
    SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView
):
    model = SeasonTeam
    template_name = "seasons/team_list.html"
    context_object_name = "teams"
    paginate_by = 50

    def get_queryset(self):
        return team_list_queryset(season_id=self.request.GET.get("season"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["seasons"] = season_options_queryset()
        context["selected_season_id"] = self.request.GET.get("season", "")
        return context


class SeasonTeamCreateView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/team_form.html"
    form_class = SeasonTeamForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        season_id = self.kwargs.get("season_id")
        if season_id:
            kwargs["fixed_season"] = get_object_or_404(
                Season, pk=season_id, is_active=True
            )
        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            team, created = get_or_create_season_team(
                season=data["season"],
                name=data["name"],
                division=data["division"],
                external_source=data.get("external_source", ""),
                external_identifier=data.get("external_identifier", ""),
            )
            if not created:
                update_season_team(team, is_active=data.get("is_active", False))
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(
            self.request,
            "Season team created." if created else "Existing season team reused.",
        )
        return redirect("seasons:team-list")


class SeasonTeamEditView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/team_form.html"
    form_class = SeasonTeamForm

    def dispatch(self, request, *args, **kwargs):
        self.team = get_object_or_404(
            SeasonTeam.objects.select_related("season"), pk=kwargs["team_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["fixed_season"] = self.team.season
        return kwargs

    def get_initial(self):
        return {
            "season": self.team.season,
            "name": self.team.name,
            "division": self.team.division,
            "external_source": self.team.external_source,
            "external_identifier": self.team.external_identifier,
            "is_active": self.team.is_active,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["team"] = self.team
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            update_season_team(
                self.team,
                name=data["name"],
                division=data["division"],
                external_source=data.get("external_source", ""),
                external_identifier=data.get("external_identifier", ""),
                is_active=data.get("is_active", False),
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Season team updated.")
        return redirect("seasons:team-list")

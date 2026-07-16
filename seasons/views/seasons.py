from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, ListView, TemplateView

from seasons.forms import ConfirmCurrentSeasonForm, SeasonForm
from seasons.models import Season
from seasons.services.season_query_service import (
    season_detail_team_queryset,
    season_list_queryset,
)
from seasons.services.season_service import (
    create_season,
    set_current_season,
    update_season,
)
from seasons.views.mixins import (
    SeasonOperationsStaffRequiredMixin,
    SeasonPaginationMixin,
)


class SeasonListView(
    SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView
):
    model = Season
    template_name = "seasons/season_list.html"
    context_object_name = "seasons"
    paginate_by = 50

    def get_queryset(self):
        return season_list_queryset()


class SeasonDetailView(SeasonOperationsStaffRequiredMixin, TemplateView):
    template_name = "seasons/season_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.season = get_object_or_404(Season, pk=kwargs["season_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {"season": self.season, "teams": season_detail_team_queryset(self.season)}
        )
        return context


class SeasonCreateView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/season_form.html"
    form_class = SeasonForm

    def form_valid(self, form):
        try:
            season = create_season(**form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Season created.")
        return redirect("seasons:season-detail", season_id=season.id)


class SeasonEditView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/season_form.html"
    form_class = SeasonForm

    def dispatch(self, request, *args, **kwargs):
        self.season = get_object_or_404(Season, pk=kwargs["season_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            "key": self.season.key,
            "name": self.season.name,
            "starts_on": self.season.starts_on,
            "ends_on": self.season.ends_on,
            "is_active": self.season.is_active,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["season"] = self.season
        return context

    def form_valid(self, form):
        try:
            update_season(self.season, **form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Season updated.")
        return redirect("seasons:season-detail", season_id=self.season.id)


class SeasonSetCurrentView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/season_set_current.html"
    form_class = ConfirmCurrentSeasonForm

    def dispatch(self, request, *args, **kwargs):
        self.season = get_object_or_404(Season, pk=kwargs["season_id"])
        if not self.season.is_active:
            raise PermissionDenied("Inactive seasons cannot be made current.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["season"] = self.season
        return context

    def form_valid(self, form):
        set_current_season(self.season)
        messages.success(self.request, f"{self.season.name} is now the current season.")
        return redirect("seasons:season-detail", season_id=self.season.id)

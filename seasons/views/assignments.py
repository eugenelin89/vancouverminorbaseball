from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, ListView, TemplateView

from seasons.forms import CoachAssignmentEndForm, CoachSeasonAssignmentForm
from seasons.models import CoachSeasonAssignment
from seasons.services.coach_assignment_service import (
    create_assignment,
    deactivate_assignment,
    update_assignment,
)
from seasons.services.season_query_service import (
    assignment_list_queryset,
    coach_history_assignment_queryset,
    season_options_queryset,
    team_options_queryset,
)
from seasons.views.mixins import (
    SeasonOperationsStaffRequiredMixin,
    SeasonPaginationMixin,
)


class CoachAssignmentListView(
    SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView
):
    model = CoachSeasonAssignment
    template_name = "seasons/assignment_list.html"
    context_object_name = "assignments"
    paginate_by = 50

    def get_queryset(self):
        return assignment_list_queryset(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "seasons": season_options_queryset(),
                "teams": team_options_queryset(),
                "filters": {
                    "season": self.request.GET.get("season", ""),
                    "team": self.request.GET.get("team", ""),
                    "active": self.request.GET.get("active", ""),
                    "q": self.request.GET.get("q", ""),
                },
            }
        )
        return context


class CoachAssignmentCreateView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/assignment_form.html"
    form_class = CoachSeasonAssignmentForm

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            assignment = create_assignment(
                user=data["user"],
                season_team=data["season_team"],
                assignment_role=data["assignment_role"],
                is_primary=data.get("is_primary", False),
                is_active=data.get("is_active", False),
                starts_on=data.get("starts_on"),
                ends_on=data.get("ends_on"),
                source=data.get("source", ""),
                source_identifier=data.get("source_identifier", ""),
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Coach assignment created.")
        return redirect("seasons:coach-history", user_id=assignment.user_id)


class CoachAssignmentEditView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/assignment_form.html"
    form_class = CoachSeasonAssignmentForm

    def dispatch(self, request, *args, **kwargs):
        self.assignment = get_object_or_404(
            CoachSeasonAssignment.objects.select_related(
                "user", "season_team", "season_team__season"
            ),
            pk=kwargs["assignment_id"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["fixed_season"] = self.assignment.season
        kwargs["editing"] = True
        return kwargs

    def get_initial(self):
        return {
            "user": self.assignment.user,
            "season_team": self.assignment.season_team,
            "assignment_role": self.assignment.assignment_role,
            "is_primary": self.assignment.is_primary,
            "is_active": self.assignment.is_active,
            "starts_on": self.assignment.starts_on,
            "ends_on": self.assignment.ends_on,
            "source": self.assignment.source,
            "source_identifier": self.assignment.source_identifier,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assignment"] = self.assignment
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        original_flags = (
            self.assignment.user.is_staff,
            self.assignment.user.is_superuser,
            self.assignment.user.password,
        )
        try:
            update_assignment(
                self.assignment,
                assignment_role=data["assignment_role"],
                is_primary=data.get("is_primary", False),
                is_active=data.get("is_active", False),
                starts_on=data.get("starts_on"),
                ends_on=data.get("ends_on"),
                source=data.get("source", ""),
                source_identifier=data.get("source_identifier", ""),
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        self.assignment.user.refresh_from_db()
        if original_flags != (
            self.assignment.user.is_staff,
            self.assignment.user.is_superuser,
            self.assignment.user.password,
        ):
            raise ValidationError(
                "Coach assignment updates must not change account privileges or password state."
            )
        messages.success(self.request, "Coach assignment updated.")
        return redirect("seasons:coach-history", user_id=self.assignment.user_id)


class CoachAssignmentEndView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/assignment_end.html"
    form_class = CoachAssignmentEndForm

    def dispatch(self, request, *args, **kwargs):
        self.assignment = get_object_or_404(
            CoachSeasonAssignment.objects.select_related(
                "user", "season_team", "season_team__season"
            ),
            pk=kwargs["assignment_id"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assignment"] = self.assignment
        return context

    def form_valid(self, form):
        try:
            deactivate_assignment(
                self.assignment, ends_on=form.cleaned_data.get("ends_on")
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Coach assignment ended.")
        return redirect("seasons:coach-history", user_id=self.assignment.user_id)


class CoachSeasonHistoryView(SeasonOperationsStaffRequiredMixin, TemplateView):
    template_name = "seasons/coach_history.html"

    def dispatch(self, request, *args, **kwargs):
        User = CoachSeasonAssignment._meta.get_field("user").remote_field.model
        self.coach = get_object_or_404(User, pk=kwargs["user_id"])
        if (
            not hasattr(self.coach, "account_profile")
            or self.coach.account_profile.role != "coach"
        ):
            raise Http404("Coach not found.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignments = coach_history_assignment_queryset(self.coach)
        context.update({"coach": self.coach, "assignments": assignments})
        return context

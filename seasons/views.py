from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, ListView, TemplateView

from accounts.services.permissions import is_staff_or_admin
from players.models import Player
from seasons.forms import (
    CoachAssignmentEndForm,
    CoachSeasonAssignmentForm,
    ConfirmCurrentSeasonForm,
    PlayerMembershipEndForm,
    PlayerMembershipTransferForm,
    PlayerRosterMembershipForm,
    SeasonForm,
    SeasonTeamForm,
)
from seasons.models import CoachSeasonAssignment, PlayerRosterMembership, RosterStatus, Season, SeasonTeam
from seasons.services.coach_assignment_service import create_assignment, deactivate_assignment, update_assignment
from seasons.services.membership_service import create_membership, deactivate_membership, transfer_player, update_membership
from seasons.services.season_service import create_season, set_current_season, update_season
from seasons.services.team_service import get_or_create_season_team, update_season_team


class SeasonOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_staff_or_admin(self.request.user)


class SeasonPaginationMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        query.pop("page", None)
        encoded = query.urlencode()
        context["pagination_query"] = f"{encoded}&" if encoded else ""
        return context


def _clean_int(value: str) -> str | None:
    value = str(value or "").strip()
    return value if value.isdigit() else None


class SeasonListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
    model = Season
    template_name = "seasons/season_list.html"
    context_object_name = "seasons"
    paginate_by = 50

    def get_queryset(self):
        return Season.objects.annotate(
            team_count=Count("teams", distinct=True),
            membership_count=Count("teams__player_memberships", distinct=True),
            assignment_count=Count("teams__coach_assignments", distinct=True),
        ).order_by("-starts_on", "name", "id")


class SeasonDetailView(SeasonOperationsStaffRequiredMixin, TemplateView):
    template_name = "seasons/season_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.season = get_object_or_404(Season, pk=kwargs["season_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teams = (
            self.season.teams.annotate(
                membership_count=Count("player_memberships", distinct=True),
                assignment_count=Count("coach_assignments", distinct=True),
            )
            .order_by("division", "name", "id")
        )
        context.update({"season": self.season, "teams": teams})
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


class SeasonTeamListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
    model = SeasonTeam
    template_name = "seasons/team_list.html"
    context_object_name = "teams"
    paginate_by = 50

    def get_queryset(self):
        queryset = SeasonTeam.objects.select_related("season").annotate(
            membership_count=Count("player_memberships", distinct=True),
            assignment_count=Count("coach_assignments", distinct=True),
        )
        season_id = _clean_int(self.request.GET.get("season"))
        if season_id:
            queryset = queryset.filter(season_id=season_id)
        return queryset.order_by("-season__is_current", "season__name", "division", "name", "id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["seasons"] = Season.objects.order_by("-is_current", "-starts_on", "name")
        context["selected_season_id"] = self.request.GET.get("season", "")
        return context


class SeasonTeamCreateView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/team_form.html"
    form_class = SeasonTeamForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        season_id = self.kwargs.get("season_id")
        if season_id:
            kwargs["fixed_season"] = get_object_or_404(Season, pk=season_id, is_active=True)
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
        messages.success(self.request, "Season team created." if created else "Existing season team reused.")
        return redirect("seasons:team-list")


class SeasonTeamEditView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/team_form.html"
    form_class = SeasonTeamForm

    def dispatch(self, request, *args, **kwargs):
        self.team = get_object_or_404(SeasonTeam.objects.select_related("season"), pk=kwargs["team_id"])
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


class PlayerMembershipListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
    model = PlayerRosterMembership
    template_name = "seasons/membership_list.html"
    context_object_name = "memberships"
    paginate_by = 50

    def get_queryset(self):
        queryset = PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season")
        season_id = _clean_int(self.request.GET.get("season"))
        team_id = _clean_int(self.request.GET.get("team"))
        active = self.request.GET.get("active")
        search = self.request.GET.get("q", "").strip()
        if season_id:
            queryset = queryset.filter(season_team__season_id=season_id)
        if team_id:
            queryset = queryset.filter(season_team_id=team_id)
        if active == "yes":
            queryset = queryset.filter(is_active=True)
        elif active == "no":
            queryset = queryset.filter(is_active=False)
        if search:
            queryset = queryset.filter(Q(player__first_name__icontains=search) | Q(player__last_name__icontains=search))
        return queryset.order_by("-season_team__season__is_current", "season_team__season__name", "player__last_name", "player__first_name", "id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "seasons": Season.objects.order_by("-is_current", "-starts_on", "name"),
                "teams": SeasonTeam.objects.select_related("season").order_by("-season__is_current", "season__name", "division", "name"),
                "filters": {
                    "season": self.request.GET.get("season", ""),
                    "team": self.request.GET.get("team", ""),
                    "active": self.request.GET.get("active", ""),
                    "q": self.request.GET.get("q", ""),
                },
            }
        )
        return context


class PlayerMembershipCreateView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/membership_form.html"
    form_class = PlayerRosterMembershipForm

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            membership = create_membership(
                player=data["player"],
                season_team=data["season_team"],
                status=data["status"],
                jersey_number=data.get("jersey_number", ""),
                is_primary=data.get("is_primary", False),
                is_active=data.get("is_active", False),
                starts_on=data.get("starts_on"),
                ends_on=data.get("ends_on"),
                source=data.get("source", ""),
                source_identifier=data.get("source_identifier", ""),
                sync_player_fields=True,
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Player membership created.")
        return redirect("seasons:player-history", player_id=membership.player_id)


class PlayerMembershipEditView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/membership_form.html"
    form_class = PlayerRosterMembershipForm

    def dispatch(self, request, *args, **kwargs):
        self.membership = get_object_or_404(
            PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season"),
            pk=kwargs["membership_id"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["fixed_season"] = self.membership.season
        kwargs["editing"] = True
        return kwargs

    def get_initial(self):
        return {
            "player": self.membership.player,
            "season_team": self.membership.season_team,
            "status": self.membership.status,
            "jersey_number": self.membership.jersey_number,
            "is_primary": self.membership.is_primary,
            "is_active": self.membership.is_active,
            "starts_on": self.membership.starts_on,
            "ends_on": self.membership.ends_on,
            "source": self.membership.source,
            "source_identifier": self.membership.source_identifier,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["membership"] = self.membership
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            update_membership(
                self.membership,
                status=data["status"],
                jersey_number=data.get("jersey_number", ""),
                is_primary=data.get("is_primary", False),
                is_active=data.get("is_active", False),
                starts_on=data.get("starts_on"),
                ends_on=data.get("ends_on"),
                source=data.get("source", ""),
                source_identifier=data.get("source_identifier", ""),
                sync_player_fields=True,
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Player membership updated.")
        return redirect("seasons:player-history", player_id=self.membership.player_id)


class PlayerMembershipEndView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/membership_end.html"
    form_class = PlayerMembershipEndForm

    def dispatch(self, request, *args, **kwargs):
        self.membership = get_object_or_404(
            PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season"),
            pk=kwargs["membership_id"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["membership"] = self.membership
        return context

    def form_valid(self, form):
        try:
            deactivate_membership(
                self.membership,
                status=form.cleaned_data["status"],
                ends_on=form.cleaned_data.get("ends_on"),
                sync_player_fields=True,
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Player membership ended.")
        return redirect("seasons:player-history", player_id=self.membership.player_id)


class PlayerMembershipTransferView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/membership_transfer.html"
    form_class = PlayerMembershipTransferForm

    def dispatch(self, request, *args, **kwargs):
        self.membership = get_object_or_404(
            PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season"),
            pk=kwargs["membership_id"],
        )
        if not self.membership.is_active:
            raise PermissionDenied("Only active memberships can be transferred or extended.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["source_membership"] = self.membership
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["membership"] = self.membership
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            if data["action"] == PlayerMembershipTransferForm.ACTION_TRANSFER:
                transfer_player(
                    player=self.membership.player,
                    to_season_team=data["season_team"],
                    from_membership=self.membership,
                    transfer_date=data.get("transfer_date"),
                    source=data.get("source", ""),
                    source_identifier=data.get("source_identifier", ""),
                    metadata={"created_by": "season_operations_ui"},
                )
                messages.success(self.request, "Player transferred.")
            elif data["action"] == PlayerMembershipTransferForm.ACTION_ADDITIONAL:
                create_membership(
                    player=self.membership.player,
                    season_team=data["season_team"],
                    status=RosterStatus.GUEST,
                    jersey_number=data.get("jersey_number", ""),
                    is_primary=False,
                    is_active=True,
                    starts_on=data.get("transfer_date"),
                    source=data.get("source", ""),
                    source_identifier=data.get("source_identifier", ""),
                    sync_player_fields=True,
                )
                messages.success(self.request, "Additional membership created.")
            else:
                raise ValidationError("Unsupported membership action.")
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        return redirect("seasons:player-history", player_id=self.membership.player_id)


class PlayerSeasonHistoryView(SeasonOperationsStaffRequiredMixin, TemplateView):
    template_name = "seasons/player_history.html"

    def dispatch(self, request, *args, **kwargs):
        self.player = get_object_or_404(Player, pk=kwargs["player_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        memberships = (
            PlayerRosterMembership.objects.select_related("season_team", "season_team__season")
            .filter(player=self.player)
            .order_by("-season_team__season__starts_on", "-season_team__season__is_current", "season_team__division", "season_team__name", "-starts_on", "id")
        )
        context.update({"player": self.player, "memberships": memberships})
        return context


class CoachAssignmentListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
    model = CoachSeasonAssignment
    template_name = "seasons/assignment_list.html"
    context_object_name = "assignments"
    paginate_by = 50

    def get_queryset(self):
        queryset = CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season", "user__account_profile")
        season_id = _clean_int(self.request.GET.get("season"))
        team_id = _clean_int(self.request.GET.get("team"))
        active = self.request.GET.get("active")
        search = self.request.GET.get("q", "").strip()
        if season_id:
            queryset = queryset.filter(season_team__season_id=season_id)
        if team_id:
            queryset = queryset.filter(season_team_id=team_id)
        if active == "yes":
            queryset = queryset.filter(is_active=True)
        elif active == "no":
            queryset = queryset.filter(is_active=False)
        if search:
            queryset = queryset.filter(Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search) | Q(user__username__icontains=search))
        return queryset.order_by("-season_team__season__is_current", "season_team__season__name", "user__last_name", "user__first_name", "id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "seasons": Season.objects.order_by("-is_current", "-starts_on", "name"),
                "teams": SeasonTeam.objects.select_related("season").order_by("-season__is_current", "season__name", "division", "name"),
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
            CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season"),
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
        original_flags = (self.assignment.user.is_staff, self.assignment.user.is_superuser, self.assignment.user.password)
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
        if original_flags != (self.assignment.user.is_staff, self.assignment.user.is_superuser, self.assignment.user.password):
            raise ValidationError("Coach assignment updates must not change account privileges or password state.")
        messages.success(self.request, "Coach assignment updated.")
        return redirect("seasons:coach-history", user_id=self.assignment.user_id)


class CoachAssignmentEndView(SeasonOperationsStaffRequiredMixin, FormView):
    template_name = "seasons/assignment_end.html"
    form_class = CoachAssignmentEndForm

    def dispatch(self, request, *args, **kwargs):
        self.assignment = get_object_or_404(
            CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season"),
            pk=kwargs["assignment_id"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assignment"] = self.assignment
        return context

    def form_valid(self, form):
        try:
            deactivate_assignment(self.assignment, ends_on=form.cleaned_data.get("ends_on"))
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
        if not hasattr(self.coach, "account_profile") or self.coach.account_profile.role != "coach":
            raise Http404("Coach not found.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignments = (
            CoachSeasonAssignment.objects.select_related("season_team", "season_team__season")
            .filter(user=self.coach)
            .order_by("-season_team__season__starts_on", "-season_team__season__is_current", "season_team__division", "season_team__name", "-starts_on", "id")
        )
        context.update({"coach": self.coach, "assignments": assignments})
        return context

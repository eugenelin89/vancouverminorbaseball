from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, ListView, TemplateView

from players.models import Player
from seasons.forms import (
    PlayerMembershipEndForm,
    PlayerMembershipTransferForm,
    PlayerRosterMembershipForm,
)
from seasons.models import PlayerRosterMembership, RosterStatus
from seasons.services.membership_service import (
    create_membership,
    deactivate_membership,
    transfer_player,
    update_membership,
)
from seasons.services.season_query_service import (
    membership_list_queryset,
    player_history_membership_queryset,
    season_options_queryset,
    team_options_queryset,
)
from seasons.views.mixins import (
    SeasonOperationsStaffRequiredMixin,
    SeasonPaginationMixin,
)


class PlayerMembershipListView(
    SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView
):
    model = PlayerRosterMembership
    template_name = "seasons/membership_list.html"
    context_object_name = "memberships"
    paginate_by = 50

    def get_queryset(self):
        return membership_list_queryset(self.request.GET)

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
            PlayerRosterMembership.objects.select_related(
                "player", "season_team", "season_team__season"
            ),
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
            PlayerRosterMembership.objects.select_related(
                "player", "season_team", "season_team__season"
            ),
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
            PlayerRosterMembership.objects.select_related(
                "player", "season_team", "season_team__season"
            ),
            pk=kwargs["membership_id"],
        )
        if not self.membership.is_active:
            raise PermissionDenied(
                "Only active memberships can be transferred or extended."
            )
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
        memberships = player_history_membership_queryset(self.player)
        context.update({"player": self.player, "memberships": memberships})
        return context

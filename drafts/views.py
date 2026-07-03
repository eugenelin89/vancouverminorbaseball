import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, ListView, TemplateView, View

from analytics.services.draft_service import get_draft_contexts_for_draft

from .forms import (
    AssignPlayerForm,
    CSVUploadForm,
    DraftForm,
    DraftStatusForm,
    MovePlayerForm,
    RemovePlayerForm,
    TradeForm,
    UndoActionForm,
)
from .models import Draft, DraftAction, DraftStatus
from .services import (
    change_draft_status,
    create_draft,
    draft_player,
    get_command_center_data,
    import_players,
    move_player,
    remove_player_from_team,
    revert_action,
    trade_players,
)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class DraftListView(StaffRequiredMixin, ListView):
    model = Draft
    template_name = "drafts/draft_list.html"
    context_object_name = "drafts"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["open_draft_count"] = self.object_list.filter(status=DraftStatus.OPEN).count()
        return context


class DraftCreateView(StaffRequiredMixin, FormView):
    template_name = "drafts/draft_form.html"
    form_class = DraftForm

    def form_valid(self, form):
        draft = create_draft(
            name=form.cleaned_data["name"],
            year=form.cleaned_data["year"],
            division=form.cleaned_data["division"],
            description=form.cleaned_data["description"],
            created_by=self.request.user,
            teams=form.cleaned_data["teams"],
        )
        messages.success(self.request, "Draft created. Import players before opening the room.")
        return redirect("drafts:import", slug=draft.slug)


class DraftBaseMixin(StaffRequiredMixin):
    draft = None

    def dispatch(self, request, *args, **kwargs):
        self.draft = get_object_or_404(Draft, slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)


class DraftImportView(DraftBaseMixin, FormView):
    template_name = "drafts/draft_import.html"
    form_class = CSVUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["draft"] = self.draft
        return context

    def form_valid(self, form):
        preview = form.cleaned_data["parsed_preview"]
        if form.cleaned_data.get("confirm_import"):
            result = import_players(
                draft=self.draft,
                rows=preview["rows"],
                actor=self.request.user,
            )
            if result["rows_imported"]:
                messages.success(
                    self.request,
                    f"Imported {result['rows_imported']} players. Rejected {result['rows_rejected']} rows.",
                )
            else:
                messages.warning(self.request, "No players were imported.")
            for error in result["errors"][:10]:
                messages.error(self.request, error)
            return redirect("drafts:command-center", slug=self.draft.slug)

        context = self.get_context_data(form=form)
        context["preview"] = preview
        context["preview_payload"] = form.cleaned_data["preview_payload"]
        context["preview_summary"] = {
            "rows_processed": len(preview["rows"]),
            "rows_importable": sum(1 for row in preview["rows"] if row.imported),
            "rows_rejected": sum(1 for row in preview["rows"] if not row.imported),
        }
        return self.render_to_response(context)


class DraftCommandCenterView(DraftBaseMixin, TemplateView):
    template_name = "drafts/command_center.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "").strip()
        sort = self.request.GET.get("sort", "name")
        extra_columns = [value.strip() for value in self.request.GET.getlist("columns") if value.strip()]
        command_data = get_command_center_data(
            draft=self.draft,
            search=search,
            sort=sort,
            extra_columns=extra_columns,
        )
        context.update(command_data)
        context["draft"] = self.draft
        context["assign_form"] = AssignPlayerForm(draft=self.draft)
        context["move_form"] = MovePlayerForm(draft=self.draft)
        context["remove_form"] = RemovePlayerForm()
        context["status_form"] = DraftStatusForm(initial={"status": self.draft.status})
        context["undo_action"] = next(
            (action for action in self.draft.actions.filter(is_reverted=False)[:10] if action.can_revert),
            None,
        )
        context["search"] = search
        context["sort"] = sort
        context["status_choices"] = DraftStatus.choices
        context["draft_contexts_by_player_id"] = get_draft_contexts_for_draft(self.draft)
        return context


class PublicDraftLiveView(TemplateView):
    template_name = "drafts/public_live.html"

    def dispatch(self, request, *args, **kwargs):
        self.draft = get_object_or_404(Draft, slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_columns = [value.strip() for value in self.request.GET.getlist("columns") if value.strip()]
        command_data = get_command_center_data(
            draft=self.draft,
            sort="name",
            extra_columns=extra_columns,
        )
        context.update(command_data)
        context["draft"] = self.draft
        context["public_live"] = True
        return context


class DraftActionView(DraftBaseMixin, View):
    form_class = None
    success_view_name = "drafts:command-center"

    def post(self, request, *args, **kwargs):
        try:
            form = self.form_class(request.POST, draft=self.draft)
        except TypeError:
            form = self.form_class(request.POST)
        if not form.is_valid():
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
            return redirect(self.get_success_url())
        try:
            self.handle_valid_form(form)
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, self.success_message)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(self.success_view_name, kwargs={"slug": self.draft.slug})


class DraftAssignPlayerView(DraftActionView):
    form_class = AssignPlayerForm
    success_message = "Player assigned."

    def handle_valid_form(self, form):
        draft_player(
            draft=self.draft,
            player_id=form.cleaned_data["player_id"],
            team_id=form.cleaned_data["team_id"].id,
            actor=self.request.user,
        )


class DraftMovePlayerView(DraftActionView):
    form_class = MovePlayerForm
    success_message = "Player moved."

    def handle_valid_form(self, form):
        move_player(
            draft=self.draft,
            player_id=form.cleaned_data["player_id"],
            to_team_id=form.cleaned_data["to_team_id"].id,
            actor=self.request.user,
        )


class DraftRemovePlayerView(DraftActionView):
    form_class = RemovePlayerForm
    success_message = "Player returned to the available pool."

    def handle_valid_form(self, form):
        remove_player_from_team(
            draft=self.draft,
            player_id=form.cleaned_data["player_id"],
            actor=self.request.user,
        )


class DraftUndoView(DraftActionView):
    form_class = UndoActionForm
    success_message = "Last action reverted."

    def handle_valid_form(self, form):
        action = get_object_or_404(DraftAction, pk=form.cleaned_data["action_id"], draft=self.draft)
        revert_action(action=action, actor=self.request.user)


class DraftStatusUpdateView(DraftActionView):
    form_class = DraftStatusForm
    success_message = "Draft status updated."

    def handle_valid_form(self, form):
        change_draft_status(
            draft=self.draft,
            new_status=form.cleaned_data["status"],
            actor=self.request.user,
        )


class DraftTradeView(DraftBaseMixin, FormView):
    template_name = "drafts/trade_form.html"
    form_class = TradeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["draft"] = self.draft
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        team_one_id = self.request.GET.get("team_one")
        team_two_id = self.request.GET.get("team_two")
        teams = list(self.draft.teams.all()[:2])
        if team_one_id:
            initial["team_one"] = self.draft.teams.filter(pk=team_one_id).first()
        if team_two_id:
            initial["team_two"] = self.draft.teams.filter(pk=team_two_id).first()
        if len(teams) == 2:
            initial.setdefault("team_one", teams[0])
            initial.setdefault("team_two", teams[1])
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["draft"] = self.draft
        return context

    def form_valid(self, form):
        trade_players(
            draft=self.draft,
            team_one_id=form.cleaned_data["team_one"].id,
            team_two_id=form.cleaned_data["team_two"].id,
            team_one_player_ids=list(form.cleaned_data["team_one_players"].values_list("id", flat=True)),
            team_two_player_ids=list(form.cleaned_data["team_two_players"].values_list("id", flat=True)),
            actor=self.request.user,
        )
        messages.success(self.request, "Trade completed.")
        return redirect("drafts:command-center", slug=self.draft.slug)


class DraftExportView(DraftBaseMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{self.draft.slug}-rosters.csv"'
        writer = csv.writer(response)
        writer.writerow(["Team", "First", "Last", "Full Name"])
        for team in self.draft.teams.prefetch_related("players"):
            for player in team.players.all().order_by("last_name", "first_name"):
                writer.writerow([team.name, player.first_name, player.last_name, player.full_name])
        return response

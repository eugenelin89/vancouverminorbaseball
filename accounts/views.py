from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from accounts.forms import (
    AccountEditForm,
    AccountOnlyCreateForm,
    BulkAccountOperationForm,
    CoachImportConfirmForm,
    CoachImportUploadForm,
    PasswordResetConfirmForm,
    PlayerAccountCreateForm,
    UserPlayerLinkForm,
)
from accounts.services.account_operations_service import (
    bulk_account_operation,
    create_account_only,
    create_player_account,
    create_user_player_link,
    deactivate_user_player_link,
    get_account_detail,
    get_account_list,
    get_account_operations_dashboard,
    reactivate_user_player_link,
    reset_account_password,
    set_primary_user_player_link,
    update_account,
)
from accounts.services.account_query_service import parse_account_list_filters
from accounts.services.auth_redirect_service import (
    ACCOUNT_LOGIN_PATH,
    ACCOUNT_PASSWORD_PATH,
    landing_url_for_user,
    should_force_password_change,
)
from accounts.services.coach_import_service import commit_coach_import, preview_coach_import, preview_coach_import_file
from accounts.services.link_service import get_players_for_user
from accounts.services.password_service import clear_password_change_required
from accounts.services.permissions import (
    can_view_account_detail,
    can_view_account_list,
    can_view_account_operations_dashboard,
)
from accounts.services.profile_service import get_account_role
from accounts.services.role_service import role_label


class AccountOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return can_view_account_operations_dashboard(self.request.user)


def _account_detail_or_404(user_id):
    try:
        return get_account_detail(user_id)
    except ObjectDoesNotExist as exc:
        raise Http404("Account not found.") from exc


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        if should_force_password_change(self.request.user):
            return ACCOUNT_PASSWORD_PATH
        return super().get_success_url() or landing_url_for_user(self.request.user)

    def get_default_redirect_url(self):
        return landing_url_for_user(self.request.user)


class AccountLogoutView(LogoutView):
    next_page = ACCOUNT_LOGIN_PATH


class AccountPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/password_change.html"

    def form_valid(self, form):
        # Keep the forced-password flow explicit: save, clear flag, preserve session, then redirect.
        user = form.save()
        clear_password_change_required(user)
        update_session_auth_hash(self.request, user)
        messages.success(self.request, "Password updated.")
        return redirect(landing_url_for_user(user))


class AccountProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = get_account_role(self.request.user)
        context.update(
            {
                "account_role": role,
                "account_role_label": role_label(role),
                "linked_players": get_players_for_user(self.request.user),
            }
        )
        return context


class AccountOperationsDashboardView(AccountOperationsStaffRequiredMixin, TemplateView):
    template_name = "accounts/operations_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dashboard = get_account_operations_dashboard()
        context.update(
            {
                "dashboard": dashboard,
                "summary_cards": dashboard.summary_cards,
                "users_requiring_password_change": dashboard.users_requiring_password_change,
                "unlinked_users": dashboard.unlinked_users,
            }
        )
        return context


class AccountUserListView(AccountOperationsStaffRequiredMixin, TemplateView):
    template_name = "accounts/user_list.html"

    def dispatch(self, request, *args, **kwargs):
        if not can_view_account_list(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filters = parse_account_list_filters(self.request.GET)
        account_list = get_account_list(filters)
        visible_user_ids = [row.user.id for row in account_list.rows]
        bulk_form = kwargs.get("bulk_form") or BulkAccountOperationForm(visible_user_ids=visible_user_ids)
        context.update(
            {
                "account_list": account_list,
                "bulk_form": bulk_form,
                "bulk_result": kwargs.get("bulk_result"),
                "current_path": self.request.get_full_path(),
                "filters": account_list.filters,
                "rows": account_list.rows,
                "role_choices": account_list.role_choices,
                "total_count": account_list.total_count,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        if not can_view_account_list(request.user):
            raise PermissionDenied
        visible_user_ids = request.POST.getlist("visible_user_ids")
        form = BulkAccountOperationForm(request.POST, visible_user_ids=visible_user_ids)
        bulk_result = None
        if form.is_valid():
            try:
                bulk_result = bulk_account_operation(
                    actor=request.user,
                    action=form.cleaned_data["action"],
                    user_ids=form.selected_user_ids(),
                )
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    f"Bulk operation complete: {bulk_result.successful} succeeded, {bulk_result.failed} failed.",
                )
                form = BulkAccountOperationForm(visible_user_ids=visible_user_ids)
        return self.render_to_response(self.get_context_data(bulk_form=form, bulk_result=bulk_result))


class CoachImportListView(AccountOperationsStaffRequiredMixin, TemplateView):
    template_name = "accounts/coach_import_list.html"


class CoachImportUploadView(AccountOperationsStaffRequiredMixin, FormView):
    template_name = "accounts/coach_import_upload.html"
    form_class = CoachImportUploadForm

    def form_valid(self, form):
        try:
            csv_file = form.cleaned_data["csv_file"]
            preview_coach_import_file(csv_file)
            csv_file.seek(0)
            raw = csv_file.read()
            csv_text = raw if isinstance(raw, str) else raw.decode("utf-8-sig")
        except (UnicodeDecodeError, ValidationError) as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        self.request.session["coach_import_csv"] = csv_text
        self.request.session.modified = True
        return redirect("accounts:coach-import-preview")


class CoachImportPreviewView(AccountOperationsStaffRequiredMixin, FormView):
    template_name = "accounts/coach_import_preview.html"
    form_class = CoachImportConfirmForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not self.test_func():
            return super().dispatch(request, *args, **kwargs)
        self.csv_text = request.session.get("coach_import_csv", "")
        if not self.csv_text:
            messages.error(request, "Upload a coach CSV before previewing an import.")
            return redirect("accounts:coach-import-new")
        return super().dispatch(request, *args, **kwargs)

    def get_preview(self):
        return preview_coach_import(self.csv_text)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["preview"] = self.get_preview()
        return context

    def form_valid(self, form):
        return redirect("accounts:coach-import-confirm")


class CoachImportConfirmView(AccountOperationsStaffRequiredMixin, TemplateView):
    template_name = "accounts/coach_import_result.html"

    def get(self, request, *args, **kwargs):
        return redirect("accounts:coach-import-preview")

    def post(self, request, *args, **kwargs):
        form = CoachImportConfirmForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Confirm the coach import before continuing.")
            return redirect("accounts:coach-import-preview")
        csv_text = request.session.get("coach_import_csv", "")
        if not csv_text:
            messages.error(request, "Upload a coach CSV before confirming an import.")
            return redirect("accounts:coach-import-new")
        try:
            result = commit_coach_import(request.user, csv_text)
        except ValidationError as exc:
            messages.error(request, "; ".join(exc.messages))
            return redirect("accounts:coach-import-preview")
        request.session.pop("coach_import_csv", None)
        request.session.modified = True
        return self.render_to_response(self.get_context_data(result=result))


class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
    template_name = "accounts/user_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.account_detail = _account_detail_or_404(kwargs["user_id"])
        if not can_view_account_detail(request.user, self.account_detail.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account_detail"] = self.account_detail
        context["target_user"] = self.account_detail.user
        context["linked_players"] = self.account_detail.linked_players
        return context


class AccountUserEditView(AccountOperationsStaffRequiredMixin, FormView):
    template_name = "accounts/user_edit.html"
    form_class = AccountEditForm

    def dispatch(self, request, *args, **kwargs):
        self.account_detail = _account_detail_or_404(kwargs["user_id"])
        if not can_view_account_detail(request.user, self.account_detail.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        user = self.account_detail.user
        return {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": self.account_detail.role,
            "is_active": user.is_active,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account_detail"] = self.account_detail
        context["target_user"] = self.account_detail.user
        return context

    def form_valid(self, form):
        try:
            update_account(
                actor=self.request.user,
                user_id=self.account_detail.user.id,
                username=form.cleaned_data["username"],
                first_name=form.cleaned_data.get("first_name", ""),
                last_name=form.cleaned_data.get("last_name", ""),
                email=form.cleaned_data.get("email", ""),
                role=form.cleaned_data["role"],
                is_active=form.cleaned_data.get("is_active", False),
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Account updated.")
        return redirect("accounts:user-detail", user_id=self.account_detail.user.id)


class AccountUserLinksView(AccountOperationsStaffRequiredMixin, FormView):
    template_name = "accounts/user_links.html"
    form_class = UserPlayerLinkForm

    def dispatch(self, request, *args, **kwargs):
        self.account_detail = _account_detail_or_404(kwargs["user_id"])
        if not can_view_account_detail(request.user, self.account_detail.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account_detail"] = self.account_detail
        context["target_user"] = self.account_detail.user
        context["linked_players"] = self.account_detail.linked_players
        return context

    def form_valid(self, form):
        action = self.request.POST.get("action", "create")
        try:
            if action == "create":
                create_user_player_link(
                    actor=self.request.user,
                    user_id=self.account_detail.user.id,
                    player=form.cleaned_data["player"],
                    relationship=form.cleaned_data["relationship"],
                    is_primary=form.cleaned_data.get("is_primary", False),
                )
                messages.success(self.request, "Player link created.")
            else:
                raise ValidationError("Unsupported link action.")
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        return redirect("accounts:user-links", user_id=self.account_detail.user.id)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action", "create")
        if action == "create":
            return super().post(request, *args, **kwargs)

        form = self.form_class(request.POST)
        form.is_valid()
        try:
            link_id = int(request.POST.get("link_id", ""))
            if action == "deactivate":
                deactivate_user_player_link(actor=request.user, user_id=self.account_detail.user.id, link_id=link_id)
                messages.success(request, "Player link deactivated.")
            elif action == "reactivate":
                reactivate_user_player_link(actor=request.user, user_id=self.account_detail.user.id, link_id=link_id)
                messages.success(request, "Player link reactivated.")
            elif action == "set_primary":
                set_primary_user_player_link(actor=request.user, user_id=self.account_detail.user.id, link_id=link_id)
                messages.success(request, "Primary self link updated.")
            else:
                raise ValidationError("Unsupported link action.")
        except ObjectDoesNotExist:
            form.add_error(None, "Player link not found.")
            return self.form_invalid(form)
        except (TypeError, ValueError, ValidationError) as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        return redirect("accounts:user-links", user_id=self.account_detail.user.id)


class AccountUserPasswordResetView(AccountOperationsStaffRequiredMixin, FormView):
    template_name = "accounts/user_password_reset.html"
    form_class = PasswordResetConfirmForm

    def dispatch(self, request, *args, **kwargs):
        self.account_detail = _account_detail_or_404(kwargs["user_id"])
        if not can_view_account_detail(request.user, self.account_detail.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account_detail"] = self.account_detail
        context["target_user"] = self.account_detail.user
        return context

    def form_valid(self, form):
        try:
            result = reset_account_password(actor=self.request.user, user_id=self.account_detail.user.id)
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Password reset successfully.")
        return self.render_to_response(
            self.get_context_data(form=self.form_class(), password_reset_result=result)
        )


class AccountOnlyCreateView(AccountOperationsStaffRequiredMixin, FormView):
    template_name = "accounts/account_create.html"
    form_class = AccountOnlyCreateForm

    def form_valid(self, form):
        try:
            result = create_account_only(
                actor=self.request.user,
                username=form.cleaned_data["username"],
                first_name=form.cleaned_data.get("first_name", ""),
                last_name=form.cleaned_data.get("last_name", ""),
                email=form.cleaned_data.get("email", ""),
                role=form.cleaned_data["role"],
                is_active=form.cleaned_data.get("is_active", False),
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Account created. Copy the temporary password now; it will not be shown again.")
        return self.render_to_response(self.get_context_data(form=form, created_account=result))


class PlayerAccountCreateView(AccountOperationsStaffRequiredMixin, FormView):
    template_name = "accounts/player_account_create.html"
    form_class = PlayerAccountCreateForm

    def form_valid(self, form):
        try:
            result = create_player_account(
                actor=self.request.user,
                player=form.cleaned_data["player"],
                username=form.cleaned_data.get("username", ""),
                email=form.cleaned_data.get("email", ""),
                role=form.cleaned_data["role"],
                is_active=form.cleaned_data.get("is_active", False),
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Player account created. Copy the temporary password now; it will not be shown again.")
        return self.render_to_response(self.get_context_data(form=form, created_account=result))

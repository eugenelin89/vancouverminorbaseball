from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from accounts.forms import AccountOnlyCreateForm, PlayerAccountCreateForm
from accounts.services.account_operations_service import (
    create_account_only,
    create_player_account,
    get_account_detail,
    get_account_list,
    get_account_operations_dashboard,
)
from accounts.services.account_query_service import parse_account_list_filters
from accounts.services.auth_redirect_service import (
    ACCOUNT_LOGIN_PATH,
    ACCOUNT_PASSWORD_PATH,
    landing_url_for_user,
    should_force_password_change,
)
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
        context.update(
            {
                "account_list": account_list,
                "filters": account_list.filters,
                "rows": account_list.rows,
                "role_choices": account_list.role_choices,
                "total_count": account_list.total_count,
            }
        )
        return context


class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
    template_name = "accounts/user_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.account_detail = get_account_detail(kwargs["user_id"])
        if not can_view_account_detail(request.user, self.account_detail.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account_detail"] = self.account_detail
        context["target_user"] = self.account_detail.user
        context["linked_players"] = self.account_detail.linked_players
        return context


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

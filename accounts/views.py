from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from accounts.services.auth_redirect_service import ACCOUNT_PASSWORD_PATH, landing_url_for_user, should_force_password_change
from accounts.services.link_service import get_players_for_user
from accounts.services.password_service import clear_password_change_required
from accounts.services.profile_service import get_account_role
from accounts.services.role_service import role_label


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        if should_force_password_change(self.request.user):
            return ACCOUNT_PASSWORD_PATH
        return super().get_success_url() or landing_url_for_user(self.request.user)

    def get_default_redirect_url(self):
        return landing_url_for_user(self.request.user)


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class AccountPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/password_change.html"

    def get_success_url(self):
        return landing_url_for_user(self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        clear_password_change_required(self.request.user)
        update_session_auth_hash(self.request, self.request.user)
        messages.success(self.request, "Password updated.")
        return response


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

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from accounts.services.permissions import is_staff_or_admin


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

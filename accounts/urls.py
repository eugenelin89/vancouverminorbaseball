from django.urls import path

from accounts.views import (
    AccountLoginView,
    AccountLogoutView,
    AccountOperationsDashboardView,
    AccountPasswordChangeView,
    AccountProfileView,
    AccountUserDetailView,
    AccountUserListView,
)


app_name = "accounts"

urlpatterns = [
    path("", AccountOperationsDashboardView.as_view(), name="operations-dashboard"),
    path("login/", AccountLoginView.as_view(), name="login"),
    path("logout/", AccountLogoutView.as_view(), name="logout"),
    path("password/", AccountPasswordChangeView.as_view(), name="password-change"),
    path("profile/", AccountProfileView.as_view(), name="profile"),
    path("users/", AccountUserListView.as_view(), name="user-list"),
    path("users/<int:user_id>/", AccountUserDetailView.as_view(), name="user-detail"),
]

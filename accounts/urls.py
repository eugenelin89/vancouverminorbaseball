from django.urls import path

from accounts.views import (
    AccountOnlyCreateView,
    AccountLoginView,
    AccountLogoutView,
    AccountOperationsDashboardView,
    AccountPasswordChangeView,
    AccountProfileView,
    AccountUserDetailView,
    AccountUserEditView,
    AccountUserLinksView,
    AccountUserListView,
    AccountUserPasswordResetView,
    CoachImportConfirmView,
    CoachImportListView,
    CoachImportPreviewView,
    CoachImportUploadView,
    PlayerAccountCreateView,
)


app_name = "accounts"

urlpatterns = [
    path("", AccountOperationsDashboardView.as_view(), name="operations-dashboard"),
    path("create/", AccountOnlyCreateView.as_view(), name="account-create"),
    path("create/player/", PlayerAccountCreateView.as_view(), name="player-account-create"),
    path("imports/coaches/", CoachImportListView.as_view(), name="coach-import-list"),
    path("imports/coaches/new/", CoachImportUploadView.as_view(), name="coach-import-new"),
    path("imports/coaches/preview/", CoachImportPreviewView.as_view(), name="coach-import-preview"),
    path("imports/coaches/confirm/", CoachImportConfirmView.as_view(), name="coach-import-confirm"),
    path("login/", AccountLoginView.as_view(), name="login"),
    path("logout/", AccountLogoutView.as_view(), name="logout"),
    path("password/", AccountPasswordChangeView.as_view(), name="password-change"),
    path("profile/", AccountProfileView.as_view(), name="profile"),
    path("users/", AccountUserListView.as_view(), name="user-list"),
    path("users/<int:user_id>/", AccountUserDetailView.as_view(), name="user-detail"),
    path("users/<int:user_id>/edit/", AccountUserEditView.as_view(), name="user-edit"),
    path("users/<int:user_id>/links/", AccountUserLinksView.as_view(), name="user-links"),
    path("users/<int:user_id>/password/", AccountUserPasswordResetView.as_view(), name="user-password-reset"),
]

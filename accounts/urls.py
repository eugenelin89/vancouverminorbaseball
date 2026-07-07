from django.urls import path

from accounts.views import AccountLoginView, AccountLogoutView, AccountPasswordChangeView, AccountProfileView


app_name = "accounts"

urlpatterns = [
    path("login/", AccountLoginView.as_view(), name="login"),
    path("logout/", AccountLogoutView.as_view(), name="logout"),
    path("password/", AccountPasswordChangeView.as_view(), name="password-change"),
    path("profile/", AccountProfileView.as_view(), name="profile"),
]

from django.shortcuts import redirect

from accounts.services.auth_redirect_service import ACCOUNT_PASSWORD_PATH, is_password_change_allowed_path, should_force_password_change


class AccountPasswordChangeRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            user
            and user.is_authenticated
            and should_force_password_change(user)
            and not is_password_change_allowed_path(request.path, user)
        ):
            return redirect(ACCOUNT_PASSWORD_PATH)
        return self.get_response(request)

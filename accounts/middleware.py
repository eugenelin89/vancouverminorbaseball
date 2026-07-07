from django.shortcuts import redirect

from accounts.services.auth_redirect_service import ACCOUNT_PASSWORD_PATH, is_password_change_allowed_path, should_force_password_change


class AccountPasswordChangeRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_redirect(request):
            return redirect(ACCOUNT_PASSWORD_PATH)
        return self.get_response(request)

    def _should_redirect(self, request) -> bool:
        user = getattr(request, "user", None)
        return bool(
            user
            and user.is_authenticated
            and should_force_password_change(user)
            and not is_password_change_allowed_path(request.path, user)
        )

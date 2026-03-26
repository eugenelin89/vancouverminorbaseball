from django.shortcuts import redirect
from django.urls import reverse


class FirstLoginPasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            user
            and user.is_authenticated
            and hasattr(user, "player_profile")
            and user.player_profile.must_change_password
        ):
            allowed_paths = {
                reverse("pdp:password-change"),
                reverse("pdp:logout"),
                reverse("pdp:login"),
            }
            if not request.path.startswith("/admin/") and request.path not in allowed_paths:
                return redirect("pdp:password-change")
        return self.get_response(request)

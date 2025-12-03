from django.urls import path

from .views import (
    HomePageView,
    PAGE_REGISTRY,
    PlaceholderPageView,
    ProgramsPageView,
    RegistrationPageView,
    TryoutsPageView,
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("programs/", ProgramsPageView.as_view(), name="programs"),
    path("registration/", RegistrationPageView.as_view(), name="registration"),
    path("tryouts/", TryoutsPageView.as_view(), name="tryouts"),
]

for slug in PAGE_REGISTRY:
    if not slug or slug in {"programs", "registration", "tryouts"}:
        continue

    route = f"{slug}/"
    urlpatterns.append(
        path(route, PlaceholderPageView.as_view(), {"page_slug": slug}, name=f"page-{slug.replace('/', '-')}")
    )

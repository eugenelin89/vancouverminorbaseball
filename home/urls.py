from django.urls import path

from .views import HomePageView, PAGE_REGISTRY, PlaceholderPageView, ProgramsPageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("programs/", ProgramsPageView.as_view(), name="programs"),
]

for slug in PAGE_REGISTRY:
    if not slug or slug == "programs":
        continue

    route = f"{slug}/"
    urlpatterns.append(
        path(route, PlaceholderPageView.as_view(), {"page_slug": slug}, name=f"page-{slug.replace('/', '-')}")
    )

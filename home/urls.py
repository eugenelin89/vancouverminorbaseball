from django.urls import path

from .views import HomePageView, PAGE_REGISTRY, PlaceholderPageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
]

for slug in PAGE_REGISTRY:
    if not slug:
        continue

    route = f"{slug}/"
    urlpatterns.append(
        path(route, PlaceholderPageView.as_view(), {"page_slug": slug}, name=f"page-{slug.replace('/', '-')}")
    )

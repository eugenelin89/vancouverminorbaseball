from collections import OrderedDict

from django.http import Http404
from django.views.generic import TemplateView

from .content import (
    ACHIEVEMENTS,
    FOOTER_TEXT,
    HERO,
    NAVIGATION,
    SOCIAL_LINKS,
)


def build_page_registry():
    pages = OrderedDict()
    pages[""] = "Home"

    def walk(items):
        for item in items:
            url = item.get("url", "")
            label = item.get("label", "Page")
            if url and url != "#":
                slug = url.strip("/")
                if slug not in pages:
                    pages[slug] = label
            walk(item.get("children", []))

    walk(NAVIGATION)
    return pages


def base_context():
    return {
        "navigation": NAVIGATION,
        "footer_text": FOOTER_TEXT,
        "social_links": SOCIAL_LINKS,
    }


PAGE_REGISTRY = build_page_registry()


class HomePageView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        context["hero"] = HERO
        context["achievements"] = [
            {**achievement, "lines": achievement["title"].split("\n")}
            for achievement in ACHIEVEMENTS
        ]
        return context


class PlaceholderPageView(TemplateView):
    template_name = "home/page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())

        slug = kwargs.get("page_slug", "")
        page_title = PAGE_REGISTRY.get(slug)
        if page_title is None:
            raise Http404()

        asset_stub = (slug or "home").replace("/", "-")

        context["page_title"] = page_title
        context["page_slug"] = slug or "home"
        context["page_asset_stub"] = asset_stub
        return context

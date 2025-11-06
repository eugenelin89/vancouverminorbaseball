from collections import OrderedDict

from django.http import Http404
from django.views.generic import TemplateView

from .content import (
    ABOUT,
    ACHIEVEMENTS,
    CONTACT_INFO,
    DIVISION_SUMMARIES,
    FAQ_ITEMS,
    FOOTER_TEXT,
    GALLERY,
    HERO,
    KEY_DATES,
    NAVIGATION,
    PROGRAMS_PAGE,
    REGISTRATION_PAGE,
    SOCIAL_LINKS,
    TESTIMONIALS,
    VALUE_PROPS,
)


def build_page_registry():
    pages = OrderedDict()
    pages[""] = "Home"

    def walk(items):
        for item in items:
            url = item.get("url", "")
            label = item.get("label", "Page")
            if not url or url == "#" or "#" in url or url.startswith("http"):
                continue

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
        "contact": CONTACT_INFO,
    }


PAGE_REGISTRY = build_page_registry()


class HomePageView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        context["hero"] = HERO
        context["about"] = ABOUT
        context["value_props"] = VALUE_PROPS
        context["divisions"] = DIVISION_SUMMARIES
        context["key_dates"] = KEY_DATES
        context["testimonials"] = TESTIMONIALS
        context["gallery"] = GALLERY
        context["faqs"] = FAQ_ITEMS
        context["achievements"] = [
            {**achievement, "lines": achievement["title"].split("\n")}
            for achievement in ACHIEVEMENTS
        ]
        return context


class ProgramsPageView(TemplateView):
    template_name = "home/programs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        context["programs"] = PROGRAMS_PAGE
        return context


class RegistrationPageView(TemplateView):
    template_name = "home/registration.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        context["registration"] = REGISTRATION_PAGE
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

from collections import OrderedDict

from django.http import Http404
from django.views.generic import TemplateView

from .content import (
    ACHIEVEMENTS,
    CONTACT_INFO,
    DIVISION_SUMMARIES,
    FOOTER_TEXT,
    GALLERY,
    HERO,
    KEY_DATES,
    LEAD_CAPTURE,
    NAVIGATION,
    PROGRAMS_PAGE,
    REGISTRATION_PAGE,
    SOCIAL_LINKS,
    TESTIMONIALS,
    VALUE_PROPOSITIONS,
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
        "contact_info": CONTACT_INFO,
    }


PAGE_REGISTRY = build_page_registry()


class HomePageView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        context["hero"] = HERO
        context["value_props"] = VALUE_PROPOSITIONS
        context["divisions"] = DIVISION_SUMMARIES
        context["testimonials"] = TESTIMONIALS
        context["gallery"] = GALLERY
        context["key_dates"] = KEY_DATES
        context["lead_capture"] = LEAD_CAPTURE
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

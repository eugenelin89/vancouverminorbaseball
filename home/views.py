from collections import OrderedDict

from django.http import Http404
from django.views.generic import TemplateView

from .content import (
    ACHIEVEMENTS,
    CONTACT_INFO,
    DIVISION_SUMMARIES,
    FAQS,
    FOOTER_LINKS,
    FOOTER_TEXT,
    EXPECTATIONS,
    GALLERY_ITEMS,
    HERO,
    LEAD_CAPTURE,
    NAVIGATION,
    PROGRAMS_PAGE,
    REGISTRATION_PAGE,
    SCHEDULE_EVENTS,
    SOCIAL_LINKS,
    TRYOUTS_PAGE,
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
        "footer_contact": CONTACT_INFO,
        "footer_links": FOOTER_LINKS,
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
        context["value_props"] = VALUE_PROPS
        context["divisions"] = DIVISION_SUMMARIES
        context["testimonials"] = TESTIMONIALS
        context["gallery_items"] = GALLERY_ITEMS
        context["schedule_events"] = SCHEDULE_EVENTS
        context["faqs"] = FAQS
        context["lead_capture"] = LEAD_CAPTURE
        context["contact_info"] = CONTACT_INFO
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
        context["contact_info"] = CONTACT_INFO
        return context


class ExpectationsPageView(TemplateView):
    template_name = "home/expectations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        context["expectations"] = EXPECTATIONS
        return context


class TryoutsPageView(TemplateView):
    template_name = "home/tryouts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        context["page"] = TRYOUTS_PAGE
        context["tryouts"] = TRYOUTS_PAGE["tryouts"]
        context["contact_info"] = CONTACT_INFO
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

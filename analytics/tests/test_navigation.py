from html.parser import HTMLParser
from urllib.parse import urlsplit

from django.urls import Resolver404, resolve, reverse

from accounts.models import AccountRole
from accounts.services.profile_service import set_account_role
from analytics.tests.helpers import TestCase, User


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attr_map = dict(attrs)
        href = attr_map.get("href")
        if href:
            self.links.append(href)


def rendered_links(response):
    parser = LinkParser()
    parser.feed(response.content.decode())
    return parser.links


class PlatformNavigationTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        set_account_role(self.staff, AccountRole.STAFF)
        self.coach = User.objects.create_user(username="coach", password="testpass")
        set_account_role(self.coach, AccountRole.COACH)
        self.player_user = User.objects.create_user(
            username="player", password="testpass"
        )
        set_account_role(self.player_user, AccountRole.PLAYER)

    def assert_local_links_resolve(self, response):
        for href in rendered_links(response):
            if href.startswith(("#", "mailto:", "tel:", "http://", "https://")):
                continue
            path = urlsplit(href).path
            if not path:
                continue
            try:
                resolve(path)
            except Resolver404 as exc:
                raise AssertionError(f"Rendered link does not resolve: {href}") from exc

    def test_analytics_import_navigation_uses_current_route(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:command-center"))
        links = rendered_links(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn(reverse("analytics:import-list"), links)
        self.assertNotIn(reverse("pdp:import-workbench"), links)
        self.assertNotIn("/pdp/import/", links)

    def test_analytics_pages_do_not_expose_pdp_links_or_text(self):
        self.client.force_login(self.staff)

        for route_name in (
            "analytics:command-center",
            "analytics:import-list",
            "analytics:evaluation-list",
            "analytics:evaluation-review-list",
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, "PDP")
                self.assertFalse(
                    any(
                        urlsplit(href).path.startswith("/pdp/")
                        for href in rendered_links(response)
                    ),
                    f"{route_name} rendered a PDP link.",
                )
                self.assert_local_links_resolve(response)

    def test_staff_navigation_links_resolve(self):
        self.client.force_login(self.staff)

        for route_name in (
            "analytics:command-center",
            "accounts:operations-dashboard",
            "accounts:profile",
            "seasons:season-list",
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assert_local_links_resolve(response)

    def test_non_staff_profile_hides_staff_only_navigation(self):
        self.client.force_login(self.player_user)

        response = self.client.get(reverse("accounts:profile"))
        links = rendered_links(response)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(reverse("analytics:command-center"), links)
        self.assertNotIn(reverse("accounts:operations-dashboard"), links)
        self.assertNotIn(reverse("analytics:import-list"), links)
        self.assertNotIn(reverse("seasons:season-list"), links)
        self.assertNotIn(reverse("analytics:evaluation-review-list"), links)
        self.assertFalse(
            any(urlsplit(href).path.startswith("/pdp/") for href in links),
            "Non-staff profile rendered a PDP link.",
        )

    def test_coach_navigation_hides_staff_only_links_but_keeps_review_access(self):
        self.client.force_login(self.coach)

        response = self.client.get(reverse("accounts:profile"))
        links = rendered_links(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn(reverse("analytics:evaluation-list"), links)
        self.assertIn(reverse("analytics:evaluation-review-list"), links)
        self.assertNotIn(reverse("analytics:command-center"), links)
        self.assertNotIn(reverse("accounts:operations-dashboard"), links)
        self.assertNotIn(reverse("analytics:import-list"), links)
        self.assertNotIn(reverse("seasons:season-list"), links)

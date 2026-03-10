from django.test import TestCase


class HomeNavigationTests(TestCase):
    def test_home_page_includes_draft_navigation_link(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/drafts/live/2026-vcb-13u/')

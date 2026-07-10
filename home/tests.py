import os
import subprocess
import sys

from django.test import TestCase


class HomeNavigationTests(TestCase):
    def test_home_page_includes_draft_navigation_link(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/drafts/live/2026-vcb-13u/')


class SettingsConfigurationTests(TestCase):
    def test_settings_require_django_secret_key(self):
        env = os.environ.copy()
        env.pop("DJANGO_SECRET_KEY", None)

        result = subprocess.run(
            [sys.executable, "-c", "import vancouverminor.settings"],
            cwd=os.getcwd(),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY", result.stderr)

    def test_settings_load_with_django_secret_key(self):
        env = os.environ.copy()
        env["DJANGO_SECRET_KEY"] = "test-only-not-production"

        result = subprocess.run(
            [sys.executable, "-c", "import vancouverminor.settings"],
            cwd=os.getcwd(),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

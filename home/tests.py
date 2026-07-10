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

    def test_settings_default_environment_configuration(self):
        env = os.environ.copy()
        env["DJANGO_SECRET_KEY"] = "test-only-not-production"
        env.pop("DJANGO_DEBUG", None)
        env.pop("DJANGO_ALLOWED_HOSTS", None)
        env.pop("DJANGO_STATIC_ROOT", None)
        env.pop("DJANGO_MEDIA_ROOT", None)

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import vancouverminor.settings as settings; "
                    "print(settings.DEBUG); "
                    "print(','.join(settings.ALLOWED_HOSTS)); "
                    "print(settings.STATIC_ROOT); "
                    "print(settings.MEDIA_ROOT)"
                ),
            ],
            cwd=os.getcwd(),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.strip().splitlines()
        self.assertEqual(lines[0], "False")
        self.assertEqual(lines[1], "localhost,127.0.0.1")
        self.assertTrue(lines[2].endswith("/staticfiles"))
        self.assertTrue(lines[3].endswith("/media"))

    def test_settings_read_environment_overrides(self):
        env = os.environ.copy()
        env["DJANGO_SECRET_KEY"] = "test-only-not-production"
        env["DJANGO_DEBUG"] = "yes"
        env["DJANGO_ALLOWED_HOSTS"] = " vancouverminor.com, www.vancouverminor.com, "
        env["DJANGO_STATIC_ROOT"] = "/srv/vcb/staticfiles"
        env["DJANGO_MEDIA_ROOT"] = "/srv/vcb/media"

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import vancouverminor.settings as settings; "
                    "print(settings.DEBUG); "
                    "print(','.join(settings.ALLOWED_HOSTS)); "
                    "print(settings.STATIC_ROOT); "
                    "print(settings.MEDIA_ROOT)"
                ),
            ],
            cwd=os.getcwd(),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.strip().splitlines()
        self.assertEqual(lines[0], "True")
        self.assertEqual(lines[1], "vancouverminor.com,www.vancouverminor.com")
        self.assertEqual(lines[2], "/srv/vcb/staticfiles")
        self.assertEqual(lines[3], "/srv/vcb/media")

    def test_settings_false_debug_values_remain_false(self):
        for value in ["", "false", "0", "no", "off", "anything"]:
            with self.subTest(value=value):
                env = os.environ.copy()
                env["DJANGO_SECRET_KEY"] = "test-only-not-production"
                env["DJANGO_DEBUG"] = value

                result = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        "import vancouverminor.settings as settings; print(settings.DEBUG)",
                    ],
                    cwd=os.getcwd(),
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), "False")

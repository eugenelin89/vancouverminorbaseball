from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from players.models import Player, PlayerImportBatch
from players.services.import_service import SOURCE_MEMBER_LIST


User = get_user_model()


class AnalyticsImportViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.user = User.objects.create_user(username="user", password="testpass")

    def upload(self):
        return SimpleUploadedFile(
            "member list for 13u house.csv",
            b"First,Last,Gender,Team\nEugene,Lin,M,Expos\n",
            content_type="text/csv",
        )

    def test_import_views_require_staff(self):
        response = self.client.get(reverse("analytics:import-list"))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(reverse("analytics:import-list"))
        self.assertEqual(response.status_code, 403)

    def test_staff_can_open_import_list(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:import-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Player Imports")

    def test_upload_redirects_to_preview(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("analytics:import-new"),
            {"source": SOURCE_MEMBER_LIST, "csv_file": self.upload()},
        )

        self.assertEqual(response.status_code, 302)
        batch = PlayerImportBatch.objects.get()
        self.assertEqual(response["Location"], reverse("analytics:import-preview", kwargs={"pk": batch.pk}))

    def test_preview_refresh_and_confirm_import(self):
        self.client.force_login(self.staff)
        batch = PlayerImportBatch.objects.create(
            source=SOURCE_MEMBER_LIST,
            original_filename="member.csv",
            uploaded_by=self.staff,
            preview_snapshot={
                "parsed_csv": {
                    "file_name": "member.csv",
                    "headers": ["First", "Last", "Team"],
                    "normalized_headers": {"first": "First", "last": "Last", "team": "Team"},
                    "rows": [
                        {
                            "row_number": 2,
                            "original_row": {"First": "Eugene", "Last": "Lin", "Team": "Expos"},
                            "cleaned_row": {"First": "Eugene", "Last": "Lin", "Team": "Expos"},
                        }
                    ],
                }
            },
        )

        preview_response = self.client.post(
            reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
            {"first_name": "First", "last_name": "Last", "team_name": "Team"},
        )
        self.assertEqual(preview_response.status_code, 302)

        confirm_response = self.client.post(reverse("analytics:import-confirm", kwargs={"pk": batch.pk}), follow=True)

        self.assertEqual(confirm_response.status_code, 200)
        self.assertTrue(Player.objects.filter(first_name="Eugene", last_name="Lin").exists())
        self.assertContains(confirm_response, "Import Result")

    def test_conflict_page_displays_review_rows(self):
        self.client.force_login(self.staff)
        Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", team_name="Old")
        upload_response = self.client.post(
            reverse("analytics:import-new"),
            {
                "source": SOURCE_MEMBER_LIST,
                "csv_file": SimpleUploadedFile(
                    "member.csv",
                    b"First,Last,DOB,Team\nEugene,Lin,2012-05-01,New\n",
                    content_type="text/csv",
                ),
            },
        )
        batch = PlayerImportBatch.objects.get()

        response = self.client.get(reverse("analytics:import-conflicts", kwargs={"pk": batch.pk}))

        self.assertEqual(upload_response.status_code, 302)
        self.assertContains(response, "Row 2")
        self.assertContains(response, "team_name")

from analytics.tests.helpers import (
    SOURCE_MEMBER_LIST,
    Player,
    PlayerImportBatch,
    PlayerSourceRow,
    SimpleUploadedFile,
    TestCase,
    User,
    create_season,
    reverse,
)


class AnalyticsImportViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        self.user = User.objects.create_user(username="user", password="testpass")
        self.season = create_season(
            key="2026-spring", name="2026 Spring", is_current=True
        )

    def upload(self):
        return SimpleUploadedFile(
            "member list for 13u house.csv",
            b"First,Last,Gender,Division,Team\nEugene,Lin,M,13U,Expos\n",
            content_type="text/csv",
        )

    def test_import_views_require_staff(self):
        response = self.client.get(reverse("analytics:import-list"))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(reverse("analytics:import-list"))
        self.assertEqual(response.status_code, 403)

    def test_staff_can_open_import_list(self):
        PlayerImportBatch.objects.create(
            source=SOURCE_MEMBER_LIST,
            original_filename="member.csv",
            uploaded_by=self.staff,
            season=self.season,
        )
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:import-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Player Imports")
        self.assertContains(response, 'data-responsive="cards"')
        self.assertContains(response, 'data-label="File"')

    def test_upload_redirects_to_preview(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("analytics:import-new"),
            {
                "season": str(self.season.pk),
                "source": SOURCE_MEMBER_LIST,
                "csv_file": self.upload(),
            },
        )

        self.assertEqual(response.status_code, 302)
        batch = PlayerImportBatch.objects.get()
        self.assertEqual(
            response["Location"],
            reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
        )

    def test_upload_can_enable_account_provisioning_options(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("analytics:import-new"),
            {
                "source": SOURCE_MEMBER_LIST,
                "season": str(self.season.pk),
                "csv_file": SimpleUploadedFile(
                    "member.csv",
                    b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n",
                    content_type="text/csv",
                ),
                "provision_player_accounts": "on",
            },
        )

        batch = PlayerImportBatch.objects.get()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(batch.mapping_config["_provision_player_accounts"])
        self.assertTrue(batch.mapping_config["_activate_player_accounts"])

    def test_preview_can_map_account_email_and_preserves_provisioning_options(self):
        self.client.force_login(self.staff)
        batch = PlayerImportBatch.objects.create(
            source=SOURCE_MEMBER_LIST,
            original_filename="member.csv",
            uploaded_by=self.staff,
            season=self.season,
            mapping_config={
                "_provision_player_accounts": True,
                "_activate_player_accounts": False,
            },
            preview_snapshot={
                "parsed_csv": {
                    "file_name": "member.csv",
                    "headers": ["First", "Last", "DOB", "Email", "Division", "Team"],
                    "normalized_headers": {
                        "first": "First",
                        "last": "Last",
                        "dob": "DOB",
                        "email": "Email",
                        "division": "Division",
                        "team": "Team",
                    },
                    "rows": [
                        {
                            "row_number": 2,
                            "original_row": {
                                "First": "Eugene",
                                "Last": "Lin",
                                "DOB": "2012-05-01",
                                "Email": "eugene@example.com",
                                "Division": "13U",
                                "Team": "Expos",
                            },
                            "cleaned_row": {
                                "First": "Eugene",
                                "Last": "Lin",
                                "DOB": "2012-05-01",
                                "Email": "eugene@example.com",
                                "Division": "13U",
                                "Team": "Expos",
                            },
                        }
                    ],
                }
            },
        )

        response = self.client.post(
            reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
            {
                "first_name": "First",
                "last_name": "Last",
                "birthdate": "DOB",
                "account_email": "Email",
                "division": "Division",
                "team_name": "Team",
            },
        )

        batch.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(batch.mapping_config["_provision_player_accounts"])
        self.assertEqual(batch.mapping_config["account_email"], "Email")
        self.assertTrue(
            batch.preview_snapshot["preview"]["account_provisioning"]["enabled"]
        )
        self.assertTrue(
            batch.preview_snapshot["preview"]["account_provisioning"]["activate_users"]
        )

    def test_preview_refresh_and_confirm_import(self):
        self.client.force_login(self.staff)
        batch = PlayerImportBatch.objects.create(
            source=SOURCE_MEMBER_LIST,
            original_filename="member.csv",
            uploaded_by=self.staff,
            season=self.season,
            preview_snapshot={
                "parsed_csv": {
                    "file_name": "member.csv",
                    "headers": ["First", "Last", "Division", "Team"],
                    "normalized_headers": {
                        "first": "First",
                        "last": "Last",
                        "division": "Division",
                        "team": "Team",
                    },
                    "rows": [
                        {
                            "row_number": 2,
                            "original_row": {
                                "First": "Eugene",
                                "Last": "Lin",
                                "Division": "13U",
                                "Team": "Expos",
                            },
                            "cleaned_row": {
                                "First": "Eugene",
                                "Last": "Lin",
                                "Division": "13U",
                                "Team": "Expos",
                            },
                        }
                    ],
                }
            },
        )

        preview_response = self.client.post(
            reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
            {
                "first_name": "First",
                "last_name": "Last",
                "division": "Division",
                "team_name": "Team",
            },
        )
        self.assertEqual(preview_response.status_code, 302)

        confirm_response = self.client.post(
            reverse("analytics:import-confirm", kwargs={"pk": batch.pk}), follow=True
        )

        self.assertEqual(confirm_response.status_code, 200)
        self.assertTrue(
            Player.objects.filter(first_name="Eugene", last_name="Lin").exists()
        )
        self.assertContains(confirm_response, "Import Result")

    def test_import_detail_shows_safe_account_provisioning_summary(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("analytics:import-new"),
            {
                "source": SOURCE_MEMBER_LIST,
                "season": str(self.season.pk),
                "csv_file": SimpleUploadedFile(
                    "member.csv",
                    b"First,Last,DOB,Division,Team\nEugene,Lin,2012-05-01,13U,Expos\n",
                    content_type="text/csv",
                ),
                "provision_player_accounts": "on",
            },
        )
        batch = PlayerImportBatch.objects.get()

        response = self.client.post(
            reverse("analytics:import-confirm", kwargs={"pk": batch.pk}), follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account provisioning")
        self.assertContains(response, "Users Created")
        self.assertNotContains(response, "20120501")

    def test_import_detail_displays_persisted_provisioning_warnings(self):
        self.client.force_login(self.staff)
        warning = (
            'Row 2: Player account was created, but the login email "family@example.com" '
            "was already assigned to another account and was not added. The new account "
            "has a blank email."
        )
        batch = PlayerImportBatch.objects.create(
            source=SOURCE_MEMBER_LIST,
            original_filename="member.csv",
            uploaded_by=self.staff,
            season=self.season,
            status="committed",
            import_summary={
                "warnings": [warning],
                "account_provisioning": {
                    "enabled": True,
                    "users_created": 1,
                    "users_linked": 0,
                    "already_linked": 0,
                    "skipped": 0,
                    "conflicts": 0,
                    "messages": [],
                    "warnings": [warning],
                },
            },
            row_errors=[],
        )

        response = self.client.get(
            reverse("analytics:import-detail", kwargs={"pk": batch.pk})
        )

        self.assertContains(response, "Warnings")
        self.assertContains(response, "family@example.com")
        self.assertContains(response, "new account has a blank email")
        self.assertNotContains(response, "Issues")

    def test_conflict_page_displays_review_rows(self):
        self.client.force_login(self.staff)
        Player.objects.create(
            first_name="Eugene",
            last_name="Lin",
            birthdate="2012-05-01",
            preferred_name="Old",
        )
        upload_response = self.client.post(
            reverse("analytics:import-new"),
            {
                "source": SOURCE_MEMBER_LIST,
                "season": str(self.season.pk),
                "csv_file": SimpleUploadedFile(
                    "member.csv",
                    b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n",
                    content_type="text/csv",
                ),
            },
        )
        batch = PlayerImportBatch.objects.get()

        response = self.client.get(
            reverse("analytics:import-conflicts", kwargs={"pk": batch.pk})
        )

        self.assertEqual(upload_response.status_code, 302)
        self.assertContains(response, "Row 2")
        self.assertContains(response, "preferred_name")

    def test_preview_routes_review_rows_through_conflict_review(self):
        self.client.force_login(self.staff)
        Player.objects.create(
            first_name="Eugene",
            last_name="Lin",
            birthdate="2012-05-01",
            preferred_name="Old",
        )
        self.client.post(
            reverse("analytics:import-new"),
            {
                "source": SOURCE_MEMBER_LIST,
                "season": str(self.season.pk),
                "csv_file": SimpleUploadedFile(
                    "member.csv",
                    b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n",
                    content_type="text/csv",
                ),
            },
        )
        batch = PlayerImportBatch.objects.get()

        response = self.client.get(
            reverse("analytics:import-preview", kwargs={"pk": batch.pk})
        )

        self.assertContains(response, "Review Rows")
        self.assertNotContains(response, "Confirm Import")

    def test_conflict_page_can_commit_ambiguous_row_to_selected_candidate(self):
        self.client.force_login(self.staff)
        Player.objects.create(
            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
        )
        selected = Player.objects.create(
            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
        )
        self.client.post(
            reverse("analytics:import-new"),
            {
                "source": SOURCE_MEMBER_LIST,
                "season": str(self.season.pk),
                "csv_file": SimpleUploadedFile(
                    "member.csv",
                    b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n",
                    content_type="text/csv",
                ),
            },
        )
        batch = PlayerImportBatch.objects.get()

        response = self.client.post(
            reverse("analytics:import-confirm", kwargs={"pk": batch.pk}),
            {"row_2_action": "use_candidate", "row_2_candidate": str(selected.id)},
            follow=True,
        )

        selected.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(selected.team_name, "Expos")
        self.assertEqual(PlayerSourceRow.objects.get().player, selected)

from accounts.tests.helpers import (
    RESULT_CONFLICT,
    RESULT_CREATED,
    RESULT_REUSED,
    AccountRole,
    CoachAssignmentRole,
    CoachSeasonAssignment,
    Player,
    SeasonTeam,
    TestCase,
    User,
    UserPlayerLink,
    ValidationError,
    base_username_for_person,
    commit_coach_import,
    create_season,
    preview_coach_import,
    set_account_role,
    username_for_person,
)


class CoachImportServiceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        self.season = create_season(
            key="2026-spring", name="2026 Spring", is_current=True
        )
        self.next_season = create_season(key="2027-spring", name="2027 Spring")

    def csv_text(self, rows):
        return (
            "first_name,last_name,email,username,team,division,is_active,notes,source_id,assignment_role,assignment_start_date,assignment_end_date,assignment_source_id\n"
            + "\n".join(rows)
        )

    def test_valid_csv_creates_active_coach_with_one_time_password(self):
        result = commit_coach_import(
            self.staff,
            self.csv_text(
                ["Casey,Coach,casey@example.com,,Reds,13U,true,Lead coach,C001"]
            ),
            season=self.season,
        )

        user = User.objects.get(email="casey@example.com")
        profile = user.account_profile
        result_row = result.rows[0]
        self.assertEqual(result_row.status, RESULT_CREATED)
        self.assertEqual(user.username, "casey.coach")
        self.assertEqual(user.first_name, "Casey")
        self.assertEqual(user.last_name, "Coach")
        self.assertTrue(user.is_active)
        self.assertEqual(profile.role, AccountRole.COACH)
        self.assertTrue(profile.must_change_password)
        self.assertEqual(profile.metadata["team"], "Reds")
        self.assertEqual(profile.metadata["division"], "13U")
        self.assertTrue(result_row.temporary_password)
        self.assertTrue(user.check_password(result_row.temporary_password))
        self.assertNotIn(result_row.temporary_password, repr(result_row))
        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
        self.assertEqual(Player.objects.count(), 0)
        self.assertEqual(result.users_created, 1)
        self.assertEqual(result.active_accounts, 1)
        self.assertEqual(result.inactive_accounts, 0)
        self.assertEqual(result.password_change_required, 1)
        assignment = CoachSeasonAssignment.objects.select_related("season_team").get(
            user=user
        )
        self.assertEqual(assignment.season_team.season, self.season)
        self.assertEqual(assignment.season_team.name, "Reds")
        self.assertEqual(
            assignment.assignment_role, CoachAssignmentRole.ASSISTANT_COACH
        )
        self.assertTrue(assignment.is_primary)
        self.assertEqual(result.season_teams_created, 1)
        self.assertEqual(result.assignments_created, 1)

    def test_coach_import_requires_active_season(self):
        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)

        preview = preview_coach_import(
            self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,,"])
        )
        inactive_preview = preview_coach_import(
            self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,,"]),
            season=inactive,
        )

        self.assertEqual(preview.error_count, 1)
        self.assertIn("Select an active season", preview.row_errors[0])
        self.assertEqual(inactive_preview.error_count, 1)
        self.assertIn("Select an active season", inactive_preview.row_errors[0])

    def test_assignment_role_aliases_and_dates_are_persisted(self):
        result = commit_coach_import(
            self.staff,
            self.csv_text(
                [
                    "Head,Coach,head@example.com,,Reds,13U,true,,C001,head,2026-04-01,2026-08-31,A001"
                ]
            ),
            season=self.season,
        )

        assignment = CoachSeasonAssignment.objects.get(user__email="head@example.com")
        self.assertEqual(result.rows[0].assignment_role_label, "Head Coach")
        self.assertEqual(assignment.assignment_role, CoachAssignmentRole.HEAD_COACH)
        self.assertEqual(assignment.starts_on.isoformat(), "2026-04-01")
        self.assertEqual(assignment.ends_on.isoformat(), "2026-08-31")
        self.assertEqual(assignment.source_identifier, "a001")

    def test_invalid_assignment_role_and_date_range_are_row_errors(self):
        preview = preview_coach_import(
            self.csv_text(
                [
                    "Bad,Role,bad.role@example.com,,Reds,13U,true,,C001,owner,,,",
                    "Bad,Dates,bad.dates@example.com,,Reds,13U,true,,C002,assistant,2026-08-31,2026-04-01,",
                ]
            ),
            season=self.season,
        )

        self.assertEqual(preview.error_count, 2)
        self.assertIn("Unknown assignment role", preview.rows[0].messages[0])
        self.assertIn("end date", preview.rows[1].messages[0])

    def test_missing_team_or_division_blocks_row(self):
        result = commit_coach_import(
            self.staff,
            self.csv_text(
                [
                    "No,Team,no.team@example.com,,,13U,true,,",
                    "No,Division,no.division@example.com,,Reds,,true,,",
                ]
            ),
            season=self.season,
        )

        self.assertEqual(result.errors, 2)
        self.assertFalse(
            User.objects.filter(
                email__in=["no.team@example.com", "no.division@example.com"]
            ).exists()
        )
        self.assertFalse(SeasonTeam.objects.exists())

    def test_imported_coach_can_be_inactive(self):
        result = commit_coach_import(
            self.staff,
            self.csv_text(
                ["Inactive,Coach,inactive.coach@example.com,,Reds,13U,false,,"]
            ),
            season=self.season,
        )

        user = User.objects.get(username="inactive.coach")
        self.assertFalse(user.is_active)
        self.assertFalse(result.rows[0].is_active)
        self.assertEqual(result.inactive_accounts, 1)

    def test_explicit_username_is_normalized_and_validated(self):
        result = commit_coach_import(
            self.staff,
            self.csv_text(
                ["User,Name,user.name@example.com,Explicit.User,Reds,13U,true,,"]
            ),
            season=self.season,
        )

        self.assertEqual(result.rows[0].username, "explicit.user")
        self.assertTrue(User.objects.filter(username="explicit.user").exists())

    def test_generated_username_collision_uses_suffix(self):
        User.objects.create_user(username="casey.coach", email="other@example.com")

        result = commit_coach_import(
            self.staff,
            self.csv_text(["Casey,Coach,casey2@example.com,,Reds,13U,true,,"]),
            season=self.season,
        )

        self.assertEqual(result.rows[0].username, "casey.coach2")
        self.assertTrue(User.objects.filter(username="casey.coach2").exists())

    def test_duplicate_email_with_existing_coach_reuses_account(self):
        existing = User.objects.create_user(
            username="existing.coach", email="coach@example.com", password="oldpass"
        )
        set_account_role(existing, AccountRole.COACH)
        original_password_hash = existing.password

        result = commit_coach_import(
            self.staff,
            self.csv_text(["Existing,Coach,COACH@example.com,,Reds,13U,true,,"]),
            season=self.season,
        )

        existing.refresh_from_db()
        existing.account_profile.refresh_from_db()
        self.assertEqual(result.rows[0].status, RESULT_REUSED)
        self.assertEqual(result.existing_coaches_reused, 1)
        self.assertEqual(
            User.objects.filter(email__iexact="coach@example.com").count(), 1
        )
        self.assertFalse(existing.account_profile.must_change_password)
        self.assertFalse(result.rows[0].temporary_password)
        self.assertEqual(existing.password, original_password_hash)
        self.assertEqual(existing.account_profile.role, AccountRole.COACH)
        self.assertEqual(CoachSeasonAssignment.objects.filter(user=existing).count(), 1)

    def test_existing_inactive_coach_is_not_activated_or_reset(self):
        existing = User.objects.create_user(
            username="inactive.existing",
            email="inactive-existing@example.com",
            password="oldpass",
            is_active=False,
        )
        profile = set_account_role(existing, AccountRole.COACH)
        profile.must_change_password = False
        profile.save(update_fields=["must_change_password", "updated_at"])
        original_password_hash = existing.password

        result = commit_coach_import(
            self.staff,
            self.csv_text(
                ["Inactive,Existing,inactive-existing@example.com,,Reds,13U,true,,"]
            ),
            season=self.season,
        )

        existing.refresh_from_db()
        profile.refresh_from_db()
        self.assertEqual(result.rows[0].status, RESULT_REUSED)
        self.assertFalse(existing.is_active)
        self.assertEqual(existing.password, original_password_hash)
        self.assertFalse(result.rows[0].temporary_password)
        self.assertFalse(profile.must_change_password)
        self.assertEqual(CoachSeasonAssignment.objects.filter(user=existing).count(), 1)

    def test_reimport_same_assignment_updates_without_duplicate_or_password_reset(self):
        first = commit_coach_import(
            self.staff,
            self.csv_text(
                [
                    "Return,Coach,return@example.com,,Reds,13U,true,,C001,assistant,,,A001"
                ]
            ),
            season=self.season,
        )
        user = User.objects.get(email="return@example.com")
        original_password_hash = user.password

        second = commit_coach_import(
            self.staff,
            self.csv_text(
                [
                    "Return,Coach,return@example.com,,Reds,13U,true,Updated notes,C001,assistant,2026-04-01,,A001"
                ]
            ),
            season=self.season,
        )

        user.refresh_from_db()
        assignment = CoachSeasonAssignment.objects.get(user=user)
        self.assertEqual(first.users_created, 1)
        self.assertEqual(second.existing_coaches_reused, 1)
        self.assertEqual(second.assignments_updated, 1)
        self.assertEqual(CoachSeasonAssignment.objects.filter(user=user).count(), 1)
        self.assertEqual(assignment.starts_on.isoformat(), "2026-04-01")
        self.assertEqual(user.password, original_password_hash)
        self.assertFalse(second.rows[0].temporary_password)

    def test_new_season_creates_new_assignment_and_distinct_team(self):
        commit_coach_import(
            self.staff,
            self.csv_text(["Season,Coach,season@example.com,,Reds,13U,true,,"]),
            season=self.season,
        )
        user = User.objects.get(email="season@example.com")

        commit_coach_import(
            self.staff,
            self.csv_text(["Season,Coach,season@example.com,,Reds,13U,true,,"]),
            season=self.next_season,
        )

        self.assertEqual(CoachSeasonAssignment.objects.filter(user=user).count(), 2)
        self.assertEqual(
            SeasonTeam.objects.filter(name="Reds", division="13U").count(), 2
        )

    def test_same_coach_can_have_multiple_teams_and_roles_without_replacing_primary(
        self,
    ):
        commit_coach_import(
            self.staff,
            self.csv_text(
                [
                    "Multi,Coach,multi@example.com,,Reds,13U,true,,C001,head,,,",
                    "Multi,Coach,multi@example.com,,Blues,13U,true,,C002,assistant,,,",
                    "Multi,Coach,multi@example.com,,Reds,13U,true,,C003,evaluator,,,",
                ]
            ),
            season=self.season,
        )
        user = User.objects.get(email="multi@example.com")
        assignments = CoachSeasonAssignment.objects.filter(
            user=user, season_team__season=self.season
        )

        self.assertEqual(assignments.count(), 3)
        self.assertEqual(assignments.filter(is_primary=True).count(), 1)
        self.assertEqual(
            assignments.get(is_primary=True).assignment_role,
            CoachAssignmentRole.HEAD_COACH,
        )

    def test_csv_season_mismatch_is_rejected(self):
        preview = preview_coach_import(
            "first_name,last_name,email,team,division,season\nMismatch,Coach,mismatch@example.com,Reds,13U,2027 Spring\n",
            season=self.season,
        )

        self.assertEqual(preview.rows[0].status, "error")
        self.assertIn("season does not match", preview.rows[0].messages[0])

    def test_duplicate_email_with_non_coach_conflicts(self):
        existing = User.objects.create_user(
            username="player.user", email="shared@example.com"
        )
        set_account_role(existing, AccountRole.PLAYER)

        result = commit_coach_import(
            self.staff,
            self.csv_text(["Shared,Coach,shared@example.com,,Reds,13U,true,,"]),
            season=self.season,
        )

        self.assertEqual(result.rows[0].status, RESULT_CONFLICT)
        self.assertEqual(result.conflicts, 1)
        self.assertEqual(User.objects.count(), 2)
        self.assertFalse(CoachSeasonAssignment.objects.exists())

    def test_explicit_duplicate_username_conflicts(self):
        User.objects.create_user(username="taken.name")

        result = commit_coach_import(
            self.staff,
            self.csv_text(["Taken,Name,taken@example.com,taken.name,Reds,13U,true,,"]),
            season=self.season,
        )

        self.assertEqual(result.rows[0].status, RESULT_CONFLICT)
        self.assertFalse(User.objects.filter(email="taken@example.com").exists())

    def test_duplicate_email_reuses_created_coach_but_duplicate_username_conflicts(
        self,
    ):
        result = commit_coach_import(
            self.staff,
            self.csv_text(
                [
                    "First,Coach,first@example.com,same.username,Reds,13U,true,,",
                    "Second,Coach,first@example.com,other.username,Reds,13U,true,,",
                    "Third,Coach,third@example.com,same.username,Reds,13U,true,,",
                ]
            ),
            season=self.season,
        )

        self.assertEqual(result.users_created, 1)
        self.assertEqual(result.existing_coaches_reused, 1)
        self.assertEqual(result.conflicts, 1)
        self.assertTrue(User.objects.filter(email="first@example.com").exists())
        self.assertFalse(User.objects.filter(email="third@example.com").exists())
        self.assertEqual(
            CoachSeasonAssignment.objects.filter(
                user__email="first@example.com"
            ).count(),
            1,
        )

    def test_blank_csv_fields_do_not_wipe_existing_metadata(self):
        existing = User.objects.create_user(
            username="metadata.coach", email="metadata@example.com"
        )
        profile = set_account_role(existing, AccountRole.COACH)
        profile.metadata = {
            "team": "Reds",
            "division": "13U",
            "notes": "Keep this",
            "custom": "value",
        }
        profile.save(update_fields=["metadata", "updated_at"])

        result = commit_coach_import(
            self.staff,
            self.csv_text(["Metadata,Coach,metadata@example.com,,Reds,13U,true,,"]),
            season=self.season,
        )

        profile.refresh_from_db()
        self.assertEqual(result.rows[0].status, RESULT_REUSED)
        self.assertEqual(profile.metadata["team"], "Reds")
        self.assertEqual(profile.metadata["division"], "13U")
        self.assertEqual(profile.metadata["notes"], "Keep this")
        self.assertEqual(profile.metadata["custom"], "value")
        self.assertFalse(result.rows[0].temporary_password)
        self.assertFalse(profile.created_from_import)
        self.assertIsNone(profile.import_batch)

    def test_missing_required_fields_produce_row_errors(self):
        preview = preview_coach_import(
            "first_name,last_name,email,team,division\nMissing,Email,,Reds,13U\n",
            season=self.season,
        )
        result = commit_coach_import(
            self.staff,
            "first_name,last_name,email,team,division\nMissing,Email,,Reds,13U\n",
            season=self.season,
        )

        self.assertEqual(preview.rows[0].status, "error")
        self.assertIn("Missing required field", preview.rows[0].messages[0])
        self.assertEqual(result.errors, 1)
        self.assertEqual(User.objects.count(), 1)

    def test_missing_required_columns_produce_import_error(self):
        result = commit_coach_import(
            self.staff, "first_name,last_name\nNo,Email\n", season=self.season
        )

        self.assertEqual(result.errors, 1)
        self.assertIn("Missing required column", result.rows[0].messages[0])

    def test_regular_user_cannot_commit_coach_import(self):
        regular = User.objects.create_user(username="regular", password="testpass")

        with self.assertRaisesMessage(
            ValidationError, "Only staff users can import coaches"
        ):
            commit_coach_import(
                regular,
                self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,,"]),
                season=self.season,
            )

    def test_username_for_person_uses_same_normalization_style(self):
        self.assertEqual(
            base_username_for_person("Jos\u00e9", "Van Horne"), "jose.vanhorne"
        )
        self.assertEqual(username_for_person("Jos\u00e9", "Van Horne"), "jose.vanhorne")

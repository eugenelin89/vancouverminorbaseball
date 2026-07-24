from django.test import override_settings

from accounts.services.password_service import (
    set_coach_import_default_password,
    validate_coach_import_default_password,
)
from accounts.tests.helpers import (
    STATUS_ALREADY_LINKED,
    STATUS_CONFLICT,
    STATUS_CREATED,
    STATUS_SKIPPED,
    AccountProfile,
    AccountRole,
    Player,
    PlayerImportBatch,
    ProvisioningOptions,
    ProvisioningSummary,
    TestCase,
    User,
    UserPlayerLink,
    UserPlayerRelationship,
    ValidationError,
    base_username_for_player,
    can_submit_coach_assessment,
    deactivate_link,
    emails_equal,
    find_existing_email_user,
    generate_birthdate_password,
    generate_random_temporary_password,
    get_or_create_account_profile,
    link_user_to_player,
    mark_password_change_required,
    normalize_email,
    normalize_username_part,
    provision_accounts_for_import,
    provision_player_account,
    set_temporary_password,
    username_for_player,
    validate_available_username,
    validate_available_username_for_user,
)


class AccountUsernameServiceTests(TestCase):
    def test_username_parts_normalize_unicode_and_unsafe_characters(self):
        self.assertEqual(normalize_username_part("  José   García!  "), "josegarcia")

    def test_base_username_for_player_uses_first_dot_last(self):
        player = Player.objects.create(
            first_name="José", last_name="García", birthdate="2012-05-01"
        )

        self.assertEqual(base_username_for_player(player), "jose.garcia")

    def test_username_for_player_uses_deterministic_suffixes(self):
        player = Player.objects.create(
            first_name="Alex", last_name="Player", birthdate="2012-05-01"
        )
        User.objects.create_user(username="alex.player")
        User.objects.create_user(username="alex.player2")

        self.assertEqual(username_for_player(player), "alex.player3")

    def test_validate_available_username_rejects_duplicates_and_unsafe_values(self):
        User.objects.create_user(username="coach.one")

        self.assertEqual(validate_available_username("new.user"), "new.user")
        self.assertEqual(validate_available_username("  Coach.Two  "), "coach.two")
        with self.assertRaises(ValidationError):
            validate_available_username("coach.ONE")
        with self.assertRaises(ValidationError):
            validate_available_username("bad username")

    def test_validate_available_username_for_user_allows_current_user(self):
        user = User.objects.create_user(username="coach.one")
        User.objects.create_user(username="other")

        self.assertEqual(
            validate_available_username_for_user(user, " Coach.One "), "coach.one"
        )
        with self.assertRaises(ValidationError):
            validate_available_username_for_user(user, "OTHER")


class AccountEmailServiceTests(TestCase):
    def test_email_normalization_and_comparison(self):
        self.assertEqual(normalize_email("  PLAYER@Example.COM "), "player@example.com")
        self.assertTrue(emails_equal("PLAYER@example.com", "player@EXAMPLE.com"))

    def test_find_existing_email_user_is_case_insensitive(self):
        user = User.objects.create_user(username="user", email="Player@Example.com")

        self.assertEqual(find_existing_email_user("player@example.COM"), user)


class AccountPasswordServiceTests(TestCase):
    def test_generate_birthdate_password_uses_yyyymmdd(self):
        player = Player.objects.create(
            first_name="Alex", last_name="Player", birthdate="2012-05-01"
        )

        self.assertEqual(generate_birthdate_password(player), "20120501")

    def test_generate_birthdate_password_requires_birthdate(self):
        player = Player.objects.create(first_name="Alex", last_name="Player")

        with self.assertRaises(ValidationError):
            generate_birthdate_password(player)

    def test_set_temporary_password_hashes_password_and_marks_profile(self):
        user = User.objects.create_user(username="player")
        player = Player.objects.create(
            first_name="Alex", last_name="Player", birthdate="2012-05-01"
        )

        set_temporary_password(user, player)
        mark_password_change_required(user)
        user.refresh_from_db()

        self.assertNotEqual(user.password, "20120501")
        self.assertTrue(user.check_password("20120501"))
        self.assertTrue(user.account_profile.must_change_password)

    def test_generate_random_temporary_password_is_secure_length(self):
        password = generate_random_temporary_password()

        self.assertGreaterEqual(len(password), 12)
        self.assertNotEqual(password, generate_random_temporary_password())

    @override_settings(COACH_IMPORT_DEFAULT_PASSWORD="CoachImportDefault123!")
    def test_set_coach_import_default_password_hashes_configured_password(self):
        user = User.objects.create_user(
            username="coach.import",
            first_name="Coach",
            last_name="Import",
            email="coach@example.com",
        )

        set_coach_import_default_password(user)
        user.refresh_from_db()

        self.assertNotEqual(user.password, "CoachImportDefault123!")
        self.assertTrue(user.check_password("CoachImportDefault123!"))

    @override_settings(COACH_IMPORT_DEFAULT_PASSWORD="")
    def test_coach_import_default_password_requires_setting(self):
        with self.assertRaisesMessage(
            ValidationError,
            "COACH_IMPORT_DEFAULT_PASSWORD must be configured",
        ):
            validate_coach_import_default_password()


class AccountProvisioningServiceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        self.player = Player.objects.create(
            first_name="José", last_name="García", birthdate="2012-05-01"
        )
        self.import_batch = PlayerImportBatch.objects.create(
            source="manual_staff_csv",
            original_filename="players.csv",
            uploaded_by=self.staff,
        )

    def test_provision_player_account_creates_active_player_account_profile_and_link(
        self,
    ):
        result = provision_player_account(
            self.player,
            import_batch=self.import_batch,
            actor=self.staff,
            email="Player@Example.com",
            row_number=2,
        )

        user = User.objects.get(username="jose.garcia")
        profile = user.account_profile
        link = UserPlayerLink.objects.get(user=user, player=self.player)
        self.assertEqual(result.status, STATUS_CREATED)
        self.assertEqual(result.username, "jose.garcia")
        self.assertTrue(user.is_active)
        self.assertEqual(user.email, "player@example.com")
        self.assertTrue(user.check_password("20120501"))
        self.assertEqual(profile.role, AccountRole.PLAYER)
        self.assertTrue(profile.must_change_password)
        self.assertTrue(profile.created_from_import)
        self.assertEqual(profile.import_batch, self.import_batch)
        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
        self.assertTrue(link.created_from_import)
        self.assertEqual(link.import_batch, self.import_batch)

    def test_provision_player_account_can_activate_user_when_explicit(self):
        result = provision_player_account(
            self.player, import_batch=self.import_batch, activate_user=True
        )

        self.assertEqual(result.status, STATUS_CREATED)
        self.assertTrue(User.objects.get(pk=result.user_id).is_active)

    def test_provision_player_account_skips_missing_birthdate(self):
        player = Player.objects.create(first_name="No", last_name="Birthdate")

        result = provision_player_account(
            player, import_batch=self.import_batch, row_number=3
        )

        self.assertEqual(result.status, STATUS_SKIPPED)
        self.assertFalse(User.objects.filter(username="no.birthdate").exists())

    def test_provision_player_account_is_idempotent_for_existing_link(self):
        first = provision_player_account(
            self.player, import_batch=self.import_batch, row_number=2
        )
        second = provision_player_account(
            self.player, import_batch=self.import_batch, row_number=2
        )

        self.assertEqual(first.status, STATUS_CREATED)
        self.assertEqual(second.status, STATUS_ALREADY_LINKED)
        self.assertEqual(User.objects.filter(username="jose.garcia").count(), 1)
        self.assertEqual(UserPlayerLink.objects.filter(player=self.player).count(), 1)
        self.assertEqual(
            AccountProfile.objects.filter(user_id=first.user_id).count(), 1
        )

    def test_provision_player_account_reuses_inactive_self_link_without_duplicates(
        self,
    ):
        user = User.objects.create_user(
            username="existing.player", email="existing@example.com"
        )
        profile = get_or_create_account_profile(user)
        link = link_user_to_player(
            user,
            self.player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
            created_from_import=True,
            import_batch=self.import_batch,
        )
        deactivate_link(link)

        result = provision_player_account(
            self.player,
            import_batch=self.import_batch,
            email="existing@example.com",
            row_number=2,
        )
        link.refresh_from_db()
        profile.refresh_from_db()

        self.assertEqual(result.status, STATUS_ALREADY_LINKED)
        self.assertEqual(result.user_id, user.id)
        self.assertTrue(link.is_active)
        self.assertTrue(link.is_primary)
        self.assertEqual(User.objects.filter(username="existing.player").count(), 1)
        self.assertEqual(AccountProfile.objects.filter(user=user).count(), 1)
        self.assertEqual(
            UserPlayerLink.objects.filter(user=user, player=self.player).count(), 1
        )

    def test_provision_player_account_preserves_manual_link_provenance(self):
        user = User.objects.create_user(
            username="manual.player", email="manual@example.com"
        )
        profile = get_or_create_account_profile(user)
        link = link_user_to_player(user, self.player)
        deactivate_link(link)

        result = provision_player_account(
            self.player,
            import_batch=self.import_batch,
            email="manual@example.com",
            row_number=2,
        )
        profile.refresh_from_db()
        link.refresh_from_db()

        self.assertEqual(result.status, STATUS_ALREADY_LINKED)
        self.assertFalse(profile.created_from_import)
        self.assertIsNone(profile.import_batch)
        self.assertFalse(link.created_from_import)
        self.assertIsNone(link.import_batch)

    def test_provision_player_account_remains_idempotent_after_link_deactivation_and_reactivation(
        self,
    ):
        first = provision_player_account(
            self.player, import_batch=self.import_batch, row_number=2
        )
        link = UserPlayerLink.objects.get(player=self.player, user_id=first.user_id)
        deactivate_link(link)

        second = provision_player_account(
            self.player, import_batch=self.import_batch, row_number=2
        )
        third = provision_player_account(
            self.player, import_batch=self.import_batch, row_number=2
        )

        link.refresh_from_db()
        self.assertEqual(second.status, STATUS_ALREADY_LINKED)
        self.assertEqual(third.status, STATUS_ALREADY_LINKED)
        self.assertTrue(link.is_active)
        self.assertEqual(User.objects.filter(username="jose.garcia").count(), 1)
        self.assertEqual(
            AccountProfile.objects.filter(user_id=first.user_id).count(), 1
        )
        self.assertEqual(
            UserPlayerLink.objects.filter(
                player=self.player, user_id=first.user_id
            ).count(),
            1,
        )

    def test_provision_player_account_conflicts_on_unrelated_email(self):
        User.objects.create_user(username="other", email="player@example.com")

        result = provision_player_account(
            self.player, import_batch=self.import_batch, email="PLAYER@example.com"
        )

        self.assertEqual(result.status, STATUS_CONFLICT)
        self.assertFalse(UserPlayerLink.objects.filter(player=self.player).exists())

    def test_provision_player_account_does_not_downgrade_existing_staff_link(self):
        staff_profile = get_or_create_account_profile(self.staff)
        staff_profile.role = AccountRole.STAFF
        staff_profile.save(update_fields=["role", "updated_at"])
        link_user_to_player(self.staff, self.player)

        result = provision_player_account(self.player, import_batch=self.import_batch)
        staff_profile.refresh_from_db()

        self.assertEqual(result.status, STATUS_ALREADY_LINKED)
        self.assertEqual(staff_profile.role, AccountRole.STAFF)
        self.assertFalse(staff_profile.created_from_import)
        self.assertIsNone(staff_profile.import_batch)

    def test_provisioning_summary_serializes_safe_counts_without_plaintext_passwords(
        self,
    ):
        summary = provision_accounts_for_import(
            self.import_batch,
            [
                {
                    "player": self.player,
                    "row_number": 2,
                    "original_row": {"Email": "player@example.com"},
                }
            ],
            actor=self.staff,
            options=ProvisioningOptions(
                enabled=True, activate_users=False, email_column="Email"
            ),
        )

        serialized = summary.to_dict()
        self.assertIsInstance(summary, ProvisioningSummary)
        self.assertEqual(serialized["users_created"], 1)
        self.assertEqual(serialized["already_linked"], 0)
        self.assertNotIn("20120501", str(serialized))
        self.assertNotIn("password", str(serialized).casefold())


class AccountRegressionTests(TestCase):
    def test_phase_two_creates_user_player_link_but_no_provisioning_models(self):
        model_names = {
            model.__name__ for model in AccountProfile._meta.apps.get_models()
        }

        self.assertIn("AccountProfile", model_names)
        self.assertIn("UserPlayerLink", model_names)
        self.assertNotIn("AccountProvisioningBatch", model_names)

    def test_players_player_does_not_gain_direct_user_field(self):
        self.assertNotIn("user", {field.name for field in Player._meta.fields})

    def test_analytics_evaluation_permission_remains_any_authenticated_user(self):
        user = User.objects.create_user(username="evaluator", password="testpass")

        self.assertTrue(can_submit_coach_assessment(user))
        self.assertFalse(can_submit_coach_assessment(None))

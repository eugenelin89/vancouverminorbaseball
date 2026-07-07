from django.contrib import admin
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from django.contrib.auth import SESSION_KEY

from accounts.models import AccountProfile, AccountRole, UserPlayerLink, UserPlayerRelationship
from accounts.services.auth_redirect_service import (
    ACCOUNT_LOGIN_PATH,
    ACCOUNT_LOGOUT_PATH,
    ACCOUNT_PASSWORD_PATH,
    ACCOUNT_PROFILE_PATH,
    ANALYTICS_HOME_PATH,
    is_password_change_allowed_path,
    landing_url_for_user,
    should_force_password_change,
)
from accounts.services.email_service import emails_equal, find_existing_email_user, normalize_email
from accounts.services.permissions import (
    can_change_account_role,
    can_manage_accounts,
    can_submit_evaluations,
    can_view_account_profile,
)
from accounts.services.link_service import (
    activate_link,
    deactivate_link,
    get_players_for_user,
    get_primary_player,
    get_primary_user,
    get_users_for_player,
    is_player_self,
    link_user_to_player,
    unlink_user_from_player,
)
from accounts.services.password_service import generate_birthdate_password, mark_password_change_required, set_temporary_password
from accounts.services.provisioning_service import (
    STATUS_ALREADY_LINKED,
    STATUS_CONFLICT,
    STATUS_CREATED,
    STATUS_SKIPPED,
    ProvisioningOptions,
    ProvisioningSummary,
    provision_accounts_for_import,
    provision_player_account,
)
from accounts.services.profile_service import get_account_role, get_or_create_account_profile, set_account_role
from accounts.services.role_service import default_role_for_user, role_for_user, role_label, validate_role
from accounts.services.username_service import base_username_for_player, normalize_username_part, username_for_player
from analytics.services.permissions import can_submit_coach_assessment
from players.models import Player, PlayerImportBatch


User = get_user_model()


class AccountProfileServiceTests(TestCase):
    def test_get_or_create_account_profile_creates_guest_profile_for_regular_user(self):
        user = User.objects.create_user(username="player", password="testpass")

        profile = get_or_create_account_profile(user)
        second = get_or_create_account_profile(user)

        self.assertEqual(profile, second)
        self.assertEqual(profile.role, AccountRole.GUEST_EVALUATOR)
        self.assertFalse(profile.must_change_password)
        self.assertFalse(profile.created_from_import)
        self.assertIsNone(profile.import_batch)

    def test_default_role_uses_django_admin_flags_for_new_profiles(self):
        staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        admin_user = User.objects.create_superuser(username="admin", password="testpass")

        self.assertEqual(get_or_create_account_profile(staff).role, AccountRole.STAFF)
        self.assertEqual(get_or_create_account_profile(admin_user).role, AccountRole.ADMIN)

    def test_role_for_user_falls_back_without_profile(self):
        staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        regular = User.objects.create_user(username="regular", password="testpass")

        self.assertEqual(role_for_user(staff), AccountRole.STAFF)
        self.assertEqual(role_for_user(regular), AccountRole.GUEST_EVALUATOR)

    def test_set_account_role_changes_only_profile_role(self):
        user = User.objects.create_user(username="coach", password="testpass")

        profile = set_account_role(user, AccountRole.COACH)
        user.refresh_from_db()

        self.assertEqual(profile.role, AccountRole.COACH)
        self.assertEqual(get_account_role(user), AccountRole.COACH)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_role_validation_and_labels(self):
        self.assertEqual(validate_role(AccountRole.PLAYER), AccountRole.PLAYER)
        self.assertEqual(role_label(AccountRole.PARENT), "Parent")

        with self.assertRaises(ValidationError):
            validate_role("unsupported")

    def test_profile_creation_requires_authenticated_user(self):
        with self.assertRaises(ValidationError):
            get_or_create_account_profile(None)


class AccountPermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass")
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.profile = get_or_create_account_profile(self.user)

    def test_staff_admin_permissions_use_django_flags(self):
        self.assertFalse(can_manage_accounts(self.user))
        self.assertFalse(can_change_account_role(self.user))
        self.assertTrue(can_manage_accounts(self.staff))
        self.assertTrue(can_change_account_role(self.staff))

    def test_regular_user_can_view_own_profile_but_not_manage_accounts(self):
        other = User.objects.create_user(username="other", password="testpass")

        self.assertTrue(can_view_account_profile(self.user, self.profile))
        self.assertFalse(can_view_account_profile(other, self.profile))
        self.assertTrue(can_view_account_profile(self.staff, self.profile))

    def test_any_authenticated_user_can_submit_evaluations(self):
        self.assertTrue(can_submit_evaluations(self.user))
        self.assertFalse(can_submit_evaluations(None))


class AccountAdminTests(TestCase):
    def test_account_profile_registered_in_admin(self):
        self.assertIn(AccountProfile, admin.site._registry)

    def test_user_player_link_registered_in_admin(self):
        self.assertIn(UserPlayerLink, admin.site._registry)
        link_admin = admin.site._registry[UserPlayerLink]

        self.assertEqual(link_admin.exclude, ("metadata",))
        self.assertIn("user", link_admin.list_display)
        self.assertIn("player", link_admin.list_display)
        self.assertIn("relationship", link_admin.list_display)
        self.assertIn("created_at", link_admin.readonly_fields)
        self.assertIn("updated_at", link_admin.readonly_fields)


class UserPlayerLinkModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player", password="testpass")
        self.other_user = User.objects.create_user(username="other", password="testpass")
        self.player = Player.objects.create(first_name="Alex", last_name="Player")
        self.other_player = Player.objects.create(first_name="Blake", last_name="Player")

    def test_user_player_link_can_link_user_to_player(self):
        link = UserPlayerLink.objects.create(
            user=self.user,
            player=self.player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )

        self.assertEqual(link.user, self.user)
        self.assertEqual(link.player, self.player)
        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
        self.assertTrue(link.is_active)
        self.assertTrue(link.is_primary)

    def test_user_can_link_to_multiple_players(self):
        UserPlayerLink.objects.create(
            user=self.user,
            player=self.player,
            relationship=UserPlayerRelationship.PARENT,
        )
        UserPlayerLink.objects.create(
            user=self.user,
            player=self.other_player,
            relationship=UserPlayerRelationship.PARENT,
        )

        self.assertEqual(UserPlayerLink.objects.filter(user=self.user, is_active=True).count(), 2)

    def test_player_can_link_to_multiple_users(self):
        UserPlayerLink.objects.create(
            user=self.user,
            player=self.player,
            relationship=UserPlayerRelationship.PARENT,
        )
        UserPlayerLink.objects.create(
            user=self.other_user,
            player=self.player,
            relationship=UserPlayerRelationship.GUARDIAN,
        )

        self.assertEqual(UserPlayerLink.objects.filter(player=self.player, is_active=True).count(), 2)

    def test_duplicate_active_relationship_is_blocked_but_inactive_history_is_allowed(self):
        UserPlayerLink.objects.create(
            user=self.user,
            player=self.player,
            relationship=UserPlayerRelationship.PARENT,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserPlayerLink.objects.create(
                    user=self.user,
                    player=self.player,
                    relationship=UserPlayerRelationship.PARENT,
                )

        UserPlayerLink.objects.filter(
            user=self.user,
            player=self.player,
            relationship=UserPlayerRelationship.PARENT,
        ).update(is_active=False)
        UserPlayerLink.objects.create(
            user=self.user,
            player=self.player,
            relationship=UserPlayerRelationship.PARENT,
        )

        self.assertEqual(
            UserPlayerLink.objects.filter(
                user=self.user,
                player=self.player,
                relationship=UserPlayerRelationship.PARENT,
            ).count(),
            2,
        )

    def test_only_one_active_primary_self_link_per_user(self):
        UserPlayerLink.objects.create(
            user=self.user,
            player=self.player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserPlayerLink.objects.create(
                    user=self.user,
                    player=self.other_player,
                    relationship=UserPlayerRelationship.SELF,
                    is_primary=True,
                )

    def test_only_one_active_primary_self_link_per_player(self):
        UserPlayerLink.objects.create(
            user=self.user,
            player=self.player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserPlayerLink.objects.create(
                    user=self.other_user,
                    player=self.player,
                    relationship=UserPlayerRelationship.SELF,
                    is_primary=True,
                )

    def test_import_provenance_fields_persist(self):
        import_batch = PlayerImportBatch.objects.create(
            source="manual_staff_csv",
            original_filename="players.csv",
            uploaded_by=self.other_user,
        )

        link = UserPlayerLink.objects.create(
            user=self.user,
            player=self.player,
            relationship=UserPlayerRelationship.SELF,
            created_from_import=True,
            import_batch=import_batch,
            metadata={"row": 2},
        )

        self.assertTrue(link.created_from_import)
        self.assertEqual(link.import_batch, import_batch)
        self.assertEqual(link.metadata, {"row": 2})


class UserPlayerLinkServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player", password="testpass")
        self.other_user = User.objects.create_user(username="other", password="testpass")
        self.player = Player.objects.create(first_name="Alex", last_name="Player")
        self.other_player = Player.objects.create(first_name="Blake", last_name="Player")

    def test_link_user_to_player_creates_active_link(self):
        link = link_user_to_player(self.user, self.player)

        self.assertEqual(link.user, self.user)
        self.assertEqual(link.player, self.player)
        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
        self.assertTrue(link.is_primary)
        self.assertTrue(link.is_active)

    def test_link_user_to_player_reuses_existing_active_link(self):
        link = link_user_to_player(self.user, self.player, metadata={"source": "initial"})
        same_link = link_user_to_player(self.user, self.player, created_from_import=True, metadata={"source": "updated"})

        self.assertEqual(link.pk, same_link.pk)
        self.assertTrue(same_link.created_from_import)
        self.assertEqual(same_link.metadata, {"source": "updated"})
        self.assertEqual(UserPlayerLink.objects.count(), 1)

    def test_link_user_to_player_rejects_invalid_inputs(self):
        with self.assertRaises(ValidationError):
            link_user_to_player(None, self.player)
        with self.assertRaises(ValidationError):
            link_user_to_player(self.user, None)
        with self.assertRaises(ValidationError):
            link_user_to_player(self.user, self.player, relationship="unsupported")
        with self.assertRaises(ValidationError):
            link_user_to_player(self.user, self.player, metadata=["not", "dict"])

    def test_link_user_to_player_rejects_primary_non_self_link(self):
        with self.assertRaises(ValidationError):
            link_user_to_player(
                self.user,
                self.player,
                relationship=UserPlayerRelationship.PARENT,
                is_primary=True,
            )

    def test_link_user_to_player_rejects_primary_self_conflicts(self):
        link_user_to_player(self.user, self.player)

        with self.assertRaises(ValidationError):
            link_user_to_player(self.user, self.other_player)
        with self.assertRaises(ValidationError):
            link_user_to_player(self.other_user, self.player)

    def test_deactivate_link_marks_inactive_and_clears_primary(self):
        link = link_user_to_player(self.user, self.player)

        deactivate_link(link)
        link.refresh_from_db()

        self.assertFalse(link.is_active)
        self.assertFalse(link.is_primary)

    def test_activate_link_reactivates_valid_inactive_link(self):
        link = link_user_to_player(self.user, self.player)
        deactivate_link(link)

        activate_link(link)
        link.refresh_from_db()

        self.assertTrue(link.is_active)
        self.assertFalse(link.is_primary)

    def test_activate_link_rejects_duplicate_active_relationship(self):
        link = link_user_to_player(
            self.user,
            self.player,
            relationship=UserPlayerRelationship.PARENT,
            is_primary=False,
        )
        deactivate_link(link)
        link_user_to_player(
            self.user,
            self.player,
            relationship=UserPlayerRelationship.PARENT,
            is_primary=False,
        )

        with self.assertRaises(ValidationError):
            activate_link(link)

    def test_unlink_user_from_player_deactivates_matching_links(self):
        link_user_to_player(
            self.user,
            self.player,
            relationship=UserPlayerRelationship.PARENT,
            is_primary=False,
        )
        link_user_to_player(
            self.user,
            self.player,
            relationship=UserPlayerRelationship.COACH,
            is_primary=False,
        )

        count = unlink_user_from_player(self.user, self.player, relationship=UserPlayerRelationship.PARENT)

        self.assertEqual(count, 1)
        self.assertFalse(
            UserPlayerLink.objects.get(
                user=self.user,
                player=self.player,
                relationship=UserPlayerRelationship.PARENT,
            ).is_active
        )
        self.assertTrue(
            UserPlayerLink.objects.get(
                user=self.user,
                player=self.player,
                relationship=UserPlayerRelationship.COACH,
            ).is_active
        )

    def test_lookup_helpers_default_to_active_links(self):
        active_link = link_user_to_player(
            self.user,
            self.player,
            relationship=UserPlayerRelationship.PARENT,
            is_primary=False,
        )
        inactive_link = link_user_to_player(
            self.user,
            self.other_player,
            relationship=UserPlayerRelationship.PARENT,
            is_primary=False,
        )
        deactivate_link(inactive_link)

        self.assertEqual(list(get_players_for_user(self.user)), [self.player])
        self.assertCountEqual(list(get_players_for_user(self.user, active_only=False)), [self.player, self.other_player])
        self.assertEqual(list(get_users_for_player(self.player)), [self.user])
        self.assertEqual(list(get_users_for_player(self.other_player)), [])
        self.assertEqual(list(get_users_for_player(self.other_player, active_only=False)), [self.user])
        self.assertTrue(active_link.is_active)

    def test_primary_and_self_helpers(self):
        link_user_to_player(self.user, self.player)

        self.assertEqual(get_primary_player(self.user), self.player)
        self.assertEqual(get_primary_user(self.player), self.user)
        self.assertTrue(is_player_self(self.user, self.player))
        self.assertFalse(is_player_self(self.user, self.other_player))

    def test_is_player_self_ignores_inactive_or_non_self_links(self):
        parent_link = link_user_to_player(
            self.user,
            self.player,
            relationship=UserPlayerRelationship.PARENT,
            is_primary=False,
        )

        self.assertFalse(is_player_self(self.user, self.player))

        deactivate_link(parent_link)
        self.assertFalse(is_player_self(self.user, self.player))


class AccountUsernameServiceTests(TestCase):
    def test_username_parts_normalize_unicode_and_unsafe_characters(self):
        self.assertEqual(normalize_username_part("  José   García!  "), "josegarcia")

    def test_base_username_for_player_uses_first_dot_last(self):
        player = Player.objects.create(first_name="José", last_name="García", birthdate="2012-05-01")

        self.assertEqual(base_username_for_player(player), "jose.garcia")

    def test_username_for_player_uses_deterministic_suffixes(self):
        player = Player.objects.create(first_name="Alex", last_name="Player", birthdate="2012-05-01")
        User.objects.create_user(username="alex.player")
        User.objects.create_user(username="alex.player2")

        self.assertEqual(username_for_player(player), "alex.player3")


class AccountEmailServiceTests(TestCase):
    def test_email_normalization_and_comparison(self):
        self.assertEqual(normalize_email("  PLAYER@Example.COM "), "player@example.com")
        self.assertTrue(emails_equal("PLAYER@example.com", "player@EXAMPLE.com"))

    def test_find_existing_email_user_is_case_insensitive(self):
        user = User.objects.create_user(username="user", email="Player@Example.com")

        self.assertEqual(find_existing_email_user("player@example.COM"), user)


class AccountPasswordServiceTests(TestCase):
    def test_generate_birthdate_password_uses_yyyymmdd(self):
        player = Player.objects.create(first_name="Alex", last_name="Player", birthdate="2012-05-01")

        self.assertEqual(generate_birthdate_password(player), "20120501")

    def test_generate_birthdate_password_requires_birthdate(self):
        player = Player.objects.create(first_name="Alex", last_name="Player")

        with self.assertRaises(ValidationError):
            generate_birthdate_password(player)

    def test_set_temporary_password_hashes_password_and_marks_profile(self):
        user = User.objects.create_user(username="player")
        player = Player.objects.create(first_name="Alex", last_name="Player", birthdate="2012-05-01")

        set_temporary_password(user, player)
        mark_password_change_required(user)
        user.refresh_from_db()

        self.assertNotEqual(user.password, "20120501")
        self.assertTrue(user.check_password("20120501"))
        self.assertTrue(user.account_profile.must_change_password)


class AccountProvisioningServiceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.player = Player.objects.create(first_name="José", last_name="García", birthdate="2012-05-01")
        self.import_batch = PlayerImportBatch.objects.create(
            source="manual_staff_csv",
            original_filename="players.csv",
            uploaded_by=self.staff,
        )

    def test_provision_player_account_creates_inactive_player_account_profile_and_link(self):
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
        self.assertFalse(user.is_active)
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
        result = provision_player_account(self.player, import_batch=self.import_batch, activate_user=True)

        self.assertEqual(result.status, STATUS_CREATED)
        self.assertTrue(User.objects.get(pk=result.user_id).is_active)

    def test_provision_player_account_skips_missing_birthdate(self):
        player = Player.objects.create(first_name="No", last_name="Birthdate")

        result = provision_player_account(player, import_batch=self.import_batch, row_number=3)

        self.assertEqual(result.status, STATUS_SKIPPED)
        self.assertFalse(User.objects.filter(username="no.birthdate").exists())

    def test_provision_player_account_is_idempotent_for_existing_link(self):
        first = provision_player_account(self.player, import_batch=self.import_batch, row_number=2)
        second = provision_player_account(self.player, import_batch=self.import_batch, row_number=2)

        self.assertEqual(first.status, STATUS_CREATED)
        self.assertEqual(second.status, STATUS_ALREADY_LINKED)
        self.assertEqual(User.objects.filter(username="jose.garcia").count(), 1)
        self.assertEqual(UserPlayerLink.objects.filter(player=self.player).count(), 1)
        self.assertEqual(AccountProfile.objects.filter(user_id=first.user_id).count(), 1)

    def test_provision_player_account_reuses_inactive_self_link_without_duplicates(self):
        user = User.objects.create_user(username="existing.player", email="existing@example.com")
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
        self.assertEqual(UserPlayerLink.objects.filter(user=user, player=self.player).count(), 1)

    def test_provision_player_account_preserves_manual_link_provenance(self):
        user = User.objects.create_user(username="manual.player", email="manual@example.com")
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

    def test_provision_player_account_remains_idempotent_after_link_deactivation_and_reactivation(self):
        first = provision_player_account(self.player, import_batch=self.import_batch, row_number=2)
        link = UserPlayerLink.objects.get(player=self.player, user_id=first.user_id)
        deactivate_link(link)

        second = provision_player_account(self.player, import_batch=self.import_batch, row_number=2)
        third = provision_player_account(self.player, import_batch=self.import_batch, row_number=2)

        link.refresh_from_db()
        self.assertEqual(second.status, STATUS_ALREADY_LINKED)
        self.assertEqual(third.status, STATUS_ALREADY_LINKED)
        self.assertTrue(link.is_active)
        self.assertEqual(User.objects.filter(username="jose.garcia").count(), 1)
        self.assertEqual(AccountProfile.objects.filter(user_id=first.user_id).count(), 1)
        self.assertEqual(UserPlayerLink.objects.filter(player=self.player, user_id=first.user_id).count(), 1)

    def test_provision_player_account_conflicts_on_unrelated_email(self):
        User.objects.create_user(username="other", email="player@example.com")

        result = provision_player_account(self.player, import_batch=self.import_batch, email="PLAYER@example.com")

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

    def test_provisioning_summary_serializes_safe_counts_without_plaintext_passwords(self):
        summary = provision_accounts_for_import(
            self.import_batch,
            [{"player": self.player, "row_number": 2, "original_row": {"Email": "player@example.com"}}],
            actor=self.staff,
            options=ProvisioningOptions(enabled=True, activate_users=False, email_column="Email"),
        )

        serialized = summary.to_dict()
        self.assertIsInstance(summary, ProvisioningSummary)
        self.assertEqual(serialized["users_created"], 1)
        self.assertEqual(serialized["already_linked"], 0)
        self.assertNotIn("20120501", str(serialized))
        self.assertNotIn("password", str(serialized).casefold())


class AccountRegressionTests(TestCase):
    def test_phase_two_creates_user_player_link_but_no_provisioning_models(self):
        model_names = {model.__name__ for model in AccountProfile._meta.apps.get_models()}

        self.assertIn("AccountProfile", model_names)
        self.assertIn("UserPlayerLink", model_names)
        self.assertNotIn("AccountProvisioningBatch", model_names)

    def test_players_player_does_not_gain_direct_user_field(self):
        self.assertNotIn("user", {field.name for field in Player._meta.fields})

    def test_analytics_evaluation_permission_remains_any_authenticated_user(self):
        user = User.objects.create_user(username="evaluator", password="testpass")

        self.assertTrue(can_submit_coach_assessment(user))
        self.assertFalse(can_submit_coach_assessment(None))


class AccountAuthRedirectServiceTests(TestCase):
    def test_landing_url_for_user(self):
        anonymous = None
        staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        regular = User.objects.create_user(username="regular", password="testpass")

        self.assertEqual(landing_url_for_user(anonymous), ACCOUNT_LOGIN_PATH)
        self.assertEqual(landing_url_for_user(staff), ANALYTICS_HOME_PATH)
        self.assertEqual(landing_url_for_user(regular), ACCOUNT_PROFILE_PATH)

    def test_should_force_password_change(self):
        user = User.objects.create_user(username="user", password="testpass")
        profile = get_or_create_account_profile(user)

        self.assertFalse(should_force_password_change(user))
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password", "updated_at"])
        self.assertTrue(should_force_password_change(user))

    def test_missing_account_profile_is_safe(self):
        user = User.objects.create_user(username="user", password="testpass")

        self.assertFalse(should_force_password_change(user))

    def test_allowed_paths(self):
        user = User.objects.create_user(username="user", password="testpass")
        superuser = User.objects.create_superuser(username="admin", password="testpass")

        self.assertTrue(is_password_change_allowed_path(ACCOUNT_PASSWORD_PATH, user))
        self.assertTrue(is_password_change_allowed_path(ACCOUNT_LOGOUT_PATH, user))
        self.assertTrue(is_password_change_allowed_path(ACCOUNT_LOGIN_PATH, user))
        self.assertTrue(is_password_change_allowed_path("/static/app.css", user))
        self.assertTrue(is_password_change_allowed_path("/media/avatar.png", user))
        self.assertFalse(is_password_change_allowed_path("/admin/", user))
        self.assertTrue(is_password_change_allowed_path("/admin/", superuser))
        self.assertFalse(is_password_change_allowed_path("/analytics/", user))


class AccountAuthViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass")
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)

    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account Login")

    def test_non_staff_login_lands_at_profile(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "user", "password": "testpass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], landing_url_for_user(self.user))

    def test_staff_login_lands_at_analytics(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "staff", "password": "testpass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], landing_url_for_user(self.staff))

    def test_safe_next_parameter_is_respected_without_forced_password_change(self):
        response = self.client.post(
            f"{reverse('accounts:login')}?next=/analytics/assessments/",
            {"username": "user", "password": "testpass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/analytics/assessments/")

    def test_forced_password_change_overrides_next_parameter(self):
        profile = get_or_create_account_profile(self.user)
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password", "updated_at"])

        response = self.client.post(
            f"{reverse('accounts:login')}?next=/analytics/assessments/",
            {"username": "user", "password": "testpass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], ACCOUNT_PASSWORD_PATH)

    def test_logout_redirects_to_account_login(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], ACCOUNT_LOGIN_PATH)

    def test_password_page_renders_for_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:password-change"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update Password")

    def test_password_change_clears_flag_and_keeps_user_logged_in(self):
        profile = get_or_create_account_profile(self.user)
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password", "updated_at"])
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:password-change"),
            {
                "old_password": "testpass",
                "new_password1": "new-strong-pass-123",
                "new_password2": "new-strong-pass-123",
            },
        )

        profile.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], landing_url_for_user(self.user))
        self.assertFalse(profile.must_change_password)
        self.assertIn(SESSION_KEY, self.client.session)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-strong-pass-123"))

        landing_response = self.client.get(response["Location"])
        self.assertEqual(landing_response.status_code, 200)
        self.assertNotEqual(landing_response.get("Location"), ACCOUNT_PASSWORD_PATH)

    def test_password_change_redirects_staff_to_landing_service_url(self):
        profile = get_or_create_account_profile(self.staff)
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password", "updated_at"])
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:password-change"),
            {
                "old_password": "testpass",
                "new_password1": "new-strong-pass-123",
                "new_password2": "new-strong-pass-123",
            },
        )

        profile.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], landing_url_for_user(self.staff))
        self.assertFalse(profile.must_change_password)
        self.assertIn(SESSION_KEY, self.client.session)

    def test_inactive_user_cannot_login(self):
        inactive = User.objects.create_user(username="inactive", password="testpass", is_active=False)
        get_or_create_account_profile(inactive)

        response = self.client.post(
            reverse("accounts:login"),
            {"username": "inactive", "password": "testpass"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_profile_page_renders_basic_account_info(self):
        get_or_create_account_profile(self.user)
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account Profile")
        self.assertContains(response, "Guest Evaluator")


class AccountPasswordMiddlewareTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass")
        self.profile = get_or_create_account_profile(self.user)

    def require_password_change(self):
        self.profile.must_change_password = True
        self.profile.save(update_fields=["must_change_password", "updated_at"])
        self.client.force_login(self.user)

    def test_forced_password_user_redirected_from_normal_page(self):
        self.require_password_change()

        response = self.client.get(reverse("analytics:assessment-list"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], ACCOUNT_PASSWORD_PATH)

    def test_allowed_paths_do_not_redirect_loop(self):
        self.require_password_change()

        self.assertEqual(self.client.get(reverse("accounts:password-change")).status_code, 200)
        self.assertNotEqual(self.client.get(reverse("accounts:login")).status_code, 302)
        self.assertEqual(self.client.post(reverse("accounts:logout")).status_code, 302)

    def test_password_page_post_is_not_blocked_by_middleware(self):
        self.require_password_change()

        response = self.client.post(
            reverse("accounts:password-change"),
            {
                "old_password": "wrong-password",
                "new_password1": "new-strong-pass-123",
                "new_password2": "new-strong-pass-123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update Password")

    def test_middleware_does_not_redirect_after_successful_password_change(self):
        self.require_password_change()

        response = self.client.post(
            reverse("accounts:password-change"),
            {
                "old_password": "testpass",
                "new_password1": "new-strong-pass-123",
                "new_password2": "new-strong-pass-123",
            },
        )

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.profile.must_change_password)
        profile_response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(profile_response.status_code, 200)

    def test_static_media_and_superuser_admin_paths_are_allowed(self):
        superuser = User.objects.create_superuser(username="admin", password="testpass")
        profile = get_or_create_account_profile(superuser)
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password", "updated_at"])
        self.client.force_login(superuser)

        self.assertNotEqual(self.client.get("/static/app.css").status_code, 302)
        self.assertNotEqual(self.client.get("/media/app.png").status_code, 302)
        self.assertNotEqual(self.client.get("/admin/").status_code, 302)

    def test_user_without_forced_password_change_is_not_redirected(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)

    def test_missing_account_profile_is_safe(self):
        user = User.objects.create_user(username="missing-profile", password="testpass")
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)


class AccountPdpCoexistenceTests(TestCase):
    def test_pdp_login_route_still_renders(self):
        response = self.client.get(reverse("pdp:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Athlete Login")

    def test_pdp_routes_and_middleware_remain_installed(self):
        self.assertEqual(reverse("pdp:login"), "/pdp/login/")
        self.assertIn("pdp.middleware.FirstLoginPasswordChangeMiddleware", settings.MIDDLEWARE)
        self.assertIn("accounts.middleware.AccountPasswordChangeRequiredMiddleware", settings.MIDDLEWARE)
        self.assertLess(
            settings.MIDDLEWARE.index("pdp.middleware.FirstLoginPasswordChangeMiddleware"),
            settings.MIDDLEWARE.index("accounts.middleware.AccountPasswordChangeRequiredMiddleware"),
        )

    def test_global_login_settings_are_account_forward(self):
        self.assertEqual(settings.LOGIN_URL, ACCOUNT_LOGIN_PATH)
        self.assertEqual(settings.LOGIN_REDIRECT_URL, ACCOUNT_PROFILE_PATH)

    def test_no_staff_account_management_routes_exist_yet(self):
        with self.assertRaises(NoReverseMatch):
            reverse("accounts:account-list")

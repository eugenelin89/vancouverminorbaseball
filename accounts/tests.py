from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import AccountProfile, AccountRole, UserPlayerLink, UserPlayerRelationship
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
from accounts.services.profile_service import get_account_role, get_or_create_account_profile, set_account_role
from accounts.services.role_service import default_role_for_user, role_for_user, role_label, validate_role
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

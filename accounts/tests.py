from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import AccountProfile, AccountRole
from accounts.services.permissions import (
    can_change_account_role,
    can_manage_accounts,
    can_submit_evaluations,
    can_view_account_profile,
)
from accounts.services.profile_service import get_account_role, get_or_create_account_profile, set_account_role
from accounts.services.role_service import default_role_for_user, role_for_user, role_label, validate_role


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


class AccountRegressionTests(TestCase):
    def test_phase_one_does_not_create_user_player_link_or_provisioning_models(self):
        model_names = {model.__name__ for model in AccountProfile._meta.apps.get_models()}

        self.assertIn("AccountProfile", model_names)
        self.assertNotIn("UserPlayerLink", model_names)

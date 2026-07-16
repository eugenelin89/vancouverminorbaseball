from accounts.tests.helpers import (
    AccountProfile,
    AccountRole,
    TestCase,
    User,
    UserPlayerLink,
    ValidationError,
    admin,
    can_access_account_operations,
    can_change_account_role,
    can_manage_accounts,
    can_manage_privileged_accounts,
    can_submit_evaluations,
    can_view_account_detail,
    can_view_account_list,
    can_view_account_operations_dashboard,
    can_view_account_profile,
    get_account_role,
    get_or_create_account_profile,
    role_for_user,
    role_label,
    set_account_role,
    validate_role,
)


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
        staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        admin_user = User.objects.create_superuser(
            username="admin", password="testpass"
        )

        self.assertEqual(get_or_create_account_profile(staff).role, AccountRole.STAFF)
        self.assertEqual(
            get_or_create_account_profile(admin_user).role, AccountRole.ADMIN
        )

    def test_role_for_user_falls_back_without_profile(self):
        staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
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
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        self.superuser = User.objects.create_superuser(
            username="admin", password="testpass"
        )
        self.profile = get_or_create_account_profile(self.user)

    def test_staff_admin_permissions_use_django_flags(self):
        self.assertFalse(can_manage_accounts(self.user))
        self.assertFalse(can_change_account_role(self.user))
        self.assertTrue(can_manage_accounts(self.staff))
        self.assertTrue(can_change_account_role(self.staff))

    def test_account_operations_permissions_use_django_staff_flags(self):
        self.profile.role = AccountRole.STAFF
        self.profile.save(update_fields=["role", "updated_at"])

        self.assertFalse(can_access_account_operations(self.user))
        self.assertFalse(can_view_account_operations_dashboard(self.user))
        self.assertFalse(can_view_account_list(self.user))
        self.assertFalse(can_view_account_detail(self.user, self.staff))
        self.assertTrue(can_access_account_operations(self.staff))
        self.assertTrue(can_view_account_operations_dashboard(self.staff))
        self.assertTrue(can_view_account_list(self.staff))
        self.assertTrue(can_view_account_detail(self.staff, self.user))
        self.assertTrue(can_access_account_operations(self.superuser))

    def test_coach_role_does_not_grant_account_operations_access(self):
        self.profile.role = AccountRole.COACH
        self.profile.save(update_fields=["role", "updated_at"])

        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertFalse(can_access_account_operations(self.user))

    def test_privileged_account_management_is_superuser_only(self):
        self.assertFalse(can_manage_privileged_accounts(self.user))
        self.assertFalse(can_manage_privileged_accounts(self.staff))
        self.assertTrue(can_manage_privileged_accounts(self.superuser))

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

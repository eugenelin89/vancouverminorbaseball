from django.contrib import admin
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import SESSION_KEY

from accounts.models import AccountProfile, AccountRole, UserPlayerLink, UserPlayerRelationship
from accounts.services.account_operations_service import (
    activate_account,
    create_account_only,
    create_player_account,
    create_user_player_link,
    deactivate_account,
    deactivate_user_player_link,
    get_account_detail,
    get_account_list,
    get_account_operations_dashboard,
    reactivate_user_player_link,
    set_primary_user_player_link,
    update_account,
)
from accounts.services.account_query_service import AccountListFilters, count_players_without_self_link, filter_account_users
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
    can_access_account_operations,
    can_change_account_role,
    can_manage_accounts,
    can_manage_privileged_accounts,
    can_submit_evaluations,
    can_view_account_detail,
    can_view_account_list,
    can_view_account_operations_dashboard,
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
    set_primary_self_link,
    unlink_user_from_player,
)
from accounts.services.password_service import (
    generate_birthdate_password,
    generate_random_temporary_password,
    mark_password_change_required,
    set_temporary_password,
)
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
from accounts.services.username_service import (
    base_username_for_player,
    normalize_username_part,
    validate_available_username,
    validate_available_username_for_user,
    username_for_player,
)
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
        self.superuser = User.objects.create_superuser(username="admin", password="testpass")
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


class AccountOperationsServiceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.coach = User.objects.create_user(
            username="coach.one",
            password="testpass",
            first_name="Coach",
            last_name="One",
            email="coach@example.com",
        )
        self.player_user = User.objects.create_user(
            username="alex.player",
            password="testpass",
            first_name="Alex",
            last_name="Player",
            email="alex@example.com",
        )
        self.inactive_user = User.objects.create_user(username="inactive", password="testpass", is_active=False)
        self.import_batch = PlayerImportBatch.objects.create(
            source="manual_staff_csv",
            original_filename="players.csv",
            uploaded_by=self.staff,
        )
        set_account_role(self.coach, AccountRole.COACH)
        player_profile = set_account_role(self.player_user, AccountRole.PLAYER)
        player_profile.created_from_import = True
        player_profile.import_batch = self.import_batch
        player_profile.must_change_password = True
        player_profile.save(
            update_fields=["created_from_import", "import_batch", "must_change_password", "updated_at"]
        )
        get_or_create_account_profile(self.inactive_user)
        self.player = Player.objects.create(first_name="Alex", last_name="Player", birthdate="2012-05-01")
        self.unlinked_player = Player.objects.create(first_name="No", last_name="Account")
        link_user_to_player(
            self.player_user,
            self.player,
            relationship=UserPlayerRelationship.SELF,
            created_from_import=True,
            import_batch=self.import_batch,
        )

    def usernames_for_filters(self, **kwargs):
        return [user.username for user in filter_account_users(AccountListFilters(**kwargs))]

    def test_account_query_filters_by_search_text(self):
        self.assertEqual(self.usernames_for_filters(search="coach@example.com"), ["coach.one"])
        self.assertEqual(self.usernames_for_filters(search="Alex"), ["alex.player"])

    def test_account_query_filters_by_role(self):
        self.assertEqual(self.usernames_for_filters(role=AccountRole.COACH), ["coach.one"])
        self.assertEqual(self.usernames_for_filters(role=AccountRole.PLAYER), ["alex.player"])

    def test_account_query_filters_by_active_status(self):
        self.assertEqual(self.usernames_for_filters(active_status="no"), ["inactive"])

    def test_account_query_filters_by_staff_and_superuser_status(self):
        admin_user = User.objects.create_superuser(username="admin", password="testpass")
        get_or_create_account_profile(admin_user)

        self.assertEqual(self.usernames_for_filters(staff_status="yes"), ["admin", "staff"])
        self.assertEqual(self.usernames_for_filters(superuser_status="yes"), ["admin"])

    def test_account_query_filters_by_imported_and_password_status(self):
        self.assertEqual(self.usernames_for_filters(imported_status="yes"), ["alex.player"])
        self.assertEqual(self.usernames_for_filters(must_change_password="yes"), ["alex.player"])

    def test_account_query_filters_by_linked_status(self):
        self.assertEqual(self.usernames_for_filters(linked_status="linked"), ["alex.player"])
        self.assertCountEqual(
            self.usernames_for_filters(linked_status="unlinked"),
            ["coach.one", "inactive", "staff"],
        )

    def test_dashboard_counts_include_account_health_metrics(self):
        dashboard = get_account_operations_dashboard()
        cards = {card.label: card.value for card in dashboard.summary_cards}

        self.assertEqual(cards["Total accounts"], 4)
        self.assertEqual(cards["Active accounts"], 3)
        self.assertEqual(cards["Inactive accounts"], 1)
        self.assertEqual(cards["Imported accounts"], 1)
        self.assertEqual(cards["Password change required"], 1)
        self.assertEqual(cards["Users without player links"], 3)
        self.assertEqual(cards["Players without self-linked accounts"], 1)
        self.assertEqual(dashboard.users_requiring_password_change[0].user, self.player_user)

    def test_account_list_context_returns_rows_and_choices(self):
        context = get_account_list(AccountListFilters(role=AccountRole.COACH))

        self.assertEqual(context.total_count, 1)
        self.assertEqual(context.rows[0].user, self.coach)
        self.assertEqual(context.rows[0].role_label, "Coach")
        self.assertIn((AccountRole.COACH, "Coach"), context.role_choices)

    def test_account_detail_context_includes_profile_and_linked_players(self):
        context = get_account_detail(self.player_user.id)

        self.assertEqual(context.user, self.player_user)
        self.assertEqual(context.role, AccountRole.PLAYER)
        self.assertEqual(context.role_label, "Player")
        self.assertEqual(len(context.linked_players), 1)
        linked = context.linked_players[0]
        self.assertEqual(linked.player, self.player)
        self.assertEqual(linked.relationship, "Self")
        self.assertTrue(linked.is_primary)
        self.assertTrue(linked.is_active)
        self.assertTrue(linked.created_from_import)
        self.assertEqual(linked.import_label, "players.csv")

    def test_players_without_self_link_count(self):
        self.assertEqual(count_players_without_self_link(), 1)

    def test_create_account_only_creates_user_profile_and_temporary_password(self):
        result = create_account_only(
            actor=self.staff,
            username="New.Coach",
            first_name="New",
            last_name="Coach",
            email="New.Coach@example.com",
            role=AccountRole.COACH,
            is_active=True,
        )

        user = User.objects.get(username="new.coach")
        profile = user.account_profile
        self.assertEqual(result.user, user)
        self.assertEqual(result.username, "new.coach")
        self.assertEqual(result.role, AccountRole.COACH)
        self.assertEqual(result.role_label, "Coach")
        self.assertTrue(result.temporary_password)
        self.assertTrue(user.check_password(result.temporary_password))
        self.assertNotIn(result.temporary_password, repr(result))
        self.assertEqual(user.email, "new.coach@example.com")
        self.assertEqual(profile.role, AccountRole.COACH)
        self.assertTrue(profile.must_change_password)
        self.assertFalse(profile.created_from_import)
        self.assertIsNone(profile.import_batch)
        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())

    def test_create_account_only_can_create_inactive_account(self):
        result = create_account_only(
            actor=self.staff,
            username="inactive.coach",
            role=AccountRole.COACH,
            is_active=False,
        )

        self.assertFalse(User.objects.get(pk=result.user.id).is_active)
        self.assertTrue(result.user.account_profile.must_change_password)

    def test_create_account_only_rejects_duplicate_username_and_email(self):
        User.objects.create_user(username="duplicate", email="duplicate@example.com")

        with self.assertRaises(ValidationError):
            create_account_only(actor=self.staff, username="DUPLICATE", role=AccountRole.COACH)
        with self.assertRaises(ValidationError):
            create_account_only(
                actor=self.staff,
                username="unique",
                email="Duplicate@Example.com",
                role=AccountRole.COACH,
            )

    def test_create_account_only_admin_requires_superuser(self):
        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")

        with self.assertRaises(ValidationError):
            create_account_only(actor=self.staff, username="admin.account", role=AccountRole.ADMIN)

        result = create_account_only(actor=superuser, username="admin.account", role=AccountRole.ADMIN)

        self.assertEqual(result.role, AccountRole.ADMIN)
        self.assertFalse(result.user.is_staff)
        self.assertFalse(result.user.is_superuser)

    def test_create_player_account_uses_existing_player_and_provisioning_logic(self):
        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")

        result = create_player_account(actor=self.staff, player=player, email="Blake@example.com")

        user = User.objects.get(username="blake.player")
        profile = user.account_profile
        link = UserPlayerLink.objects.get(user=user, player=player)
        self.assertEqual(result.user, user)
        self.assertEqual(result.player, player)
        self.assertEqual(result.temporary_password, "20130602")
        self.assertTrue(user.check_password(result.temporary_password))
        self.assertEqual(user.email, "blake@example.com")
        self.assertEqual(profile.role, AccountRole.PLAYER)
        self.assertTrue(profile.must_change_password)
        self.assertTrue(user.is_active)
        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
        self.assertTrue(link.is_primary)
        self.assertFalse(profile.created_from_import)
        self.assertIsNone(profile.import_batch)
        self.assertFalse(link.created_from_import)
        self.assertIsNone(link.import_batch)

    def test_create_player_account_accepts_optional_username_and_inactive_flag(self):
        player = Player.objects.create(first_name="Casey", last_name="Player", birthdate="2014-07-03")

        result = create_player_account(actor=self.staff, player=player, username="Custom.Player", is_active=False)

        self.assertEqual(result.username, "custom.player")
        self.assertFalse(User.objects.get(username="custom.player").is_active)

    def test_create_player_account_rejects_duplicate_email_username_and_player_account(self):
        player = Player.objects.create(first_name="Dana", last_name="Player", birthdate="2015-08-04")
        User.objects.create_user(username="taken", email="taken@example.com")

        with self.assertRaises(ValidationError):
            create_player_account(actor=self.staff, player=player, username="taken")
        with self.assertRaises(ValidationError):
            create_player_account(actor=self.staff, player=player, email="taken@example.com")

        create_player_account(actor=self.staff, player=player, username="dana.player")
        with self.assertRaises(ValidationError):
            create_player_account(actor=self.staff, player=player, username="dana.player2")

        self.assertEqual(UserPlayerLink.objects.filter(player=player, relationship=UserPlayerRelationship.SELF).count(), 1)

    def test_create_player_account_requires_existing_player_birthdate_and_player_role(self):
        player = Player.objects.create(first_name="No", last_name="Birthdate")

        with self.assertRaises(ValidationError):
            create_player_account(actor=self.staff, player=player)
        with self.assertRaises(ValidationError):
            create_player_account(actor=self.staff, player=self.player, role=AccountRole.COACH)

    def test_update_account_changes_lifecycle_username_email_and_role(self):
        result = update_account(
            actor=self.staff,
            user_id=self.coach.id,
            username=" Coach.Updated ",
            first_name="Updated",
            last_name="Coach",
            email="UPDATED@example.com",
            role=AccountRole.GUEST_EVALUATOR,
            is_active=False,
        )

        self.coach.refresh_from_db()
        self.assertEqual(result.username, "coach.updated")
        self.assertEqual(result.role, AccountRole.GUEST_EVALUATOR)
        self.assertFalse(result.is_active)
        self.assertEqual(self.coach.username, "coach.updated")
        self.assertEqual(self.coach.email, "updated@example.com")
        self.assertEqual(self.coach.account_profile.role, AccountRole.GUEST_EVALUATOR)
        self.assertFalse(self.coach.is_staff)
        self.assertFalse(self.coach.is_superuser)

    def test_update_account_rejects_duplicate_username_and_email(self):
        User.objects.create_user(username="taken", email="taken@example.com")

        with self.assertRaises(ValidationError):
            update_account(
                actor=self.staff,
                user_id=self.coach.id,
                username="TAKEN",
                email="coach@example.com",
                role=AccountRole.COACH,
            )
        with self.assertRaises(ValidationError):
            update_account(
                actor=self.staff,
                user_id=self.coach.id,
                username="coach.one",
                email="Taken@Example.com",
                role=AccountRole.COACH,
            )

    def test_update_account_admin_role_requires_superuser(self):
        with self.assertRaises(ValidationError):
            update_account(
                actor=self.staff,
                user_id=self.coach.id,
                username="coach.one",
                role=AccountRole.ADMIN,
            )

        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
        result = update_account(
            actor=superuser,
            user_id=self.coach.id,
            username="coach.one",
            role=AccountRole.ADMIN,
        )

        self.coach.refresh_from_db()
        self.assertEqual(result.role, AccountRole.ADMIN)
        self.assertEqual(self.coach.account_profile.role, AccountRole.ADMIN)
        self.assertFalse(self.coach.is_staff)
        self.assertFalse(self.coach.is_superuser)

    def test_activate_and_deactivate_account_preserve_profile_and_links(self):
        deactivate_result = deactivate_account(actor=self.staff, user_id=self.player_user.id)
        self.player_user.refresh_from_db()
        link = UserPlayerLink.objects.get(user=self.player_user, player=self.player)

        self.assertFalse(deactivate_result.is_active)
        self.assertFalse(self.player_user.is_active)
        self.assertEqual(self.player_user.account_profile.role, AccountRole.PLAYER)
        self.assertTrue(link.is_active)

        activate_result = activate_account(actor=self.staff, user_id=self.player_user.id)
        self.player_user.refresh_from_db()

        self.assertTrue(activate_result.is_active)
        self.assertTrue(self.player_user.is_active)
        self.assertTrue(UserPlayerLink.objects.get(pk=link.pk).is_active)

    def test_account_operations_manage_player_links_through_services(self):
        link_result = create_user_player_link(
            actor=self.staff,
            user_id=self.coach.id,
            player=self.player,
            relationship=UserPlayerRelationship.COACH,
            is_primary=False,
        )

        self.assertTrue(link_result.is_active)
        self.assertFalse(link_result.is_primary)
        with self.assertRaises(ValidationError):
            create_user_player_link(
                actor=self.staff,
                user_id=self.coach.id,
                player=self.player,
                relationship=UserPlayerRelationship.COACH,
                is_primary=False,
            )

        deactivated = deactivate_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id)
        self.assertFalse(deactivated.is_active)
        self.assertFalse(UserPlayerLink.objects.get(pk=link_result.link.id).is_primary)

        reactivated = reactivate_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id)
        self.assertTrue(reactivated.is_active)

    def test_account_operations_set_primary_self_link_switches_existing_primary(self):
        other_player = Player.objects.create(first_name="Second", last_name="Player")
        first_link = UserPlayerLink.objects.get(user=self.player_user, player=self.player)
        second_link = create_user_player_link(
            actor=self.staff,
            user_id=self.player_user.id,
            player=other_player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=False,
        ).link

        result = set_primary_user_player_link(actor=self.staff, user_id=self.player_user.id, link_id=second_link.id)
        first_link.refresh_from_db()
        second_link.refresh_from_db()

        self.assertTrue(result.is_primary)
        self.assertFalse(first_link.is_primary)
        self.assertTrue(second_link.is_primary)
        self.assertEqual(UserPlayerLink.objects.filter(user=self.player_user, is_primary=True, is_active=True).count(), 1)

    def test_account_operations_reject_primary_non_self_link(self):
        link = create_user_player_link(
            actor=self.staff,
            user_id=self.coach.id,
            player=self.player,
            relationship=UserPlayerRelationship.PARENT,
            is_primary=False,
        ).link

        with self.assertRaises(ValidationError):
            set_primary_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link.id)


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

    def test_set_primary_self_link_switches_primary_link(self):
        first_link = link_user_to_player(self.user, self.player)
        second_link = link_user_to_player(
            self.user,
            self.other_player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=False,
        )

        set_primary_self_link(second_link)
        first_link.refresh_from_db()
        second_link.refresh_from_db()

        self.assertFalse(first_link.is_primary)
        self.assertTrue(second_link.is_primary)
        self.assertTrue(second_link.is_active)
        self.assertEqual(get_primary_player(self.user), self.other_player)

    def test_set_primary_self_link_rejects_non_self_link(self):
        parent_link = link_user_to_player(
            self.user,
            self.player,
            relationship=UserPlayerRelationship.PARENT,
            is_primary=False,
        )

        with self.assertRaises(ValidationError):
            set_primary_self_link(parent_link)

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

        self.assertEqual(validate_available_username_for_user(user, " Coach.One "), "coach.one")
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

    def test_generate_random_temporary_password_is_secure_length(self):
        password = generate_random_temporary_password()

        self.assertGreaterEqual(len(password), 12)
        self.assertNotEqual(password, generate_random_temporary_password())


class AccountProvisioningServiceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.player = Player.objects.create(first_name="José", last_name="García", birthdate="2012-05-01")
        self.import_batch = PlayerImportBatch.objects.create(
            source="manual_staff_csv",
            original_filename="players.csv",
            uploaded_by=self.staff,
        )

    def test_provision_player_account_creates_active_player_account_profile_and_link(self):
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


class AccountOperationsViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.superuser = User.objects.create_superuser(username="admin", password="testpass")
        self.regular = User.objects.create_user(username="regular", password="testpass")
        self.coach = User.objects.create_user(
            username="coach.one",
            password="testpass",
            first_name="Coach",
            last_name="One",
            email="coach@example.com",
        )
        set_account_role(self.coach, AccountRole.COACH)
        profile = get_or_create_account_profile(self.regular)
        profile.role = AccountRole.STAFF
        profile.save(update_fields=["role", "updated_at"])
        self.player = Player.objects.create(first_name="Alex", last_name="Player")
        link_user_to_player(self.coach, self.player, relationship=UserPlayerRelationship.COACH, is_primary=False)

    def test_dashboard_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(reverse("accounts:operations-dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_access_dashboard(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("accounts:operations-dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account Operations")

    def test_dashboard_renders_expected_summary_cards(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("accounts:operations-dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total accounts")
        self.assertContains(response, "Active accounts")
        self.assertContains(response, "Inactive accounts")
        self.assertContains(response, "Password change required")
        self.assertContains(response, "Users without player links")
        self.assertContains(response, "Players without self-linked accounts")
        self.assertContains(response, reverse("accounts:account-create"))
        self.assertContains(response, reverse("accounts:player-account-create"))

    def test_user_list_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(reverse("accounts:user-list"))

        self.assertEqual(response.status_code, 403)

    def test_user_list_renders_users_and_filters(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("accounts:user-list"), {"q": "coach", "role": AccountRole.COACH})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account Users")
        self.assertContains(response, "coach.one")
        self.assertContains(response, "Coach")
        self.assertNotContains(response, "regular")

    def test_user_detail_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))

        self.assertEqual(response.status_code, 403)

    def test_user_detail_renders_profile_and_linked_players(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "coach.one")
        self.assertContains(response, "coach@example.com")
        self.assertContains(response, "Coach")
        self.assertContains(response, "Alex Player")
        self.assertContains(response, reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}))
        self.assertContains(response, reverse("accounts:user-links", kwargs={"user_id": self.coach.id}))

    def test_user_edit_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}))

        self.assertEqual(response.status_code, 403)

    def test_staff_can_edit_account_lifecycle_username_and_role(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
            {
                "username": " Coach.Updated ",
                "first_name": "Updated",
                "last_name": "Coach",
                "email": "updated@example.com",
                "role": AccountRole.GUEST_EVALUATOR,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
        self.coach.refresh_from_db()
        self.assertEqual(self.coach.username, "coach.updated")
        self.assertFalse(self.coach.is_active)
        self.assertEqual(self.coach.account_profile.role, AccountRole.GUEST_EVALUATOR)
        self.assertFalse(self.coach.is_staff)
        self.assertFalse(self.coach.is_superuser)

    def test_staff_user_edit_rejects_duplicate_username_and_admin_role(self):
        User.objects.create_user(username="taken")
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
            {
                "username": "taken",
                "role": AccountRole.COACH,
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username is already in use")

        response = self.client.post(
            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
            {
                "username": "coach.one",
                "role": AccountRole.ADMIN,
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Only superusers can assign admin role")
        self.coach.refresh_from_db()
        self.assertEqual(self.coach.account_profile.role, AccountRole.COACH)

    def test_user_links_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(reverse("accounts:user-links", kwargs={"user_id": self.coach.id}))

        self.assertEqual(response.status_code, 403)

    def test_staff_can_create_deactivate_and_reactivate_link(self):
        other_player = Player.objects.create(first_name="Blake", last_name="Player")
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
            {
                "action": "create",
                "player": other_player.id,
                "relationship": UserPlayerRelationship.PARENT,
            },
        )

        self.assertEqual(response.status_code, 302)
        link = UserPlayerLink.objects.get(user=self.coach, player=other_player, relationship=UserPlayerRelationship.PARENT)
        self.assertTrue(link.is_active)
        self.assertFalse(link.is_primary)

        response = self.client.post(
            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
            {"action": "deactivate", "link_id": link.id},
        )
        self.assertEqual(response.status_code, 302)
        link.refresh_from_db()
        self.assertFalse(link.is_active)

        response = self.client.post(
            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
            {"action": "reactivate", "link_id": link.id},
        )
        self.assertEqual(response.status_code, 302)
        link.refresh_from_db()
        self.assertTrue(link.is_active)

    def test_staff_can_set_primary_self_link_from_links_page(self):
        first_player = Player.objects.create(first_name="Self", last_name="One")
        second_player = Player.objects.create(first_name="Self", last_name="Two")
        first_link = link_user_to_player(self.coach, first_player, relationship=UserPlayerRelationship.SELF)
        second_link = link_user_to_player(
            self.coach,
            second_player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=False,
        )
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
            {"action": "set_primary", "link_id": second_link.id},
        )

        self.assertEqual(response.status_code, 302)
        first_link.refresh_from_db()
        second_link.refresh_from_db()
        self.assertFalse(first_link.is_primary)
        self.assertTrue(second_link.is_primary)

    def test_links_page_rejects_duplicate_active_link(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
            {
                "action": "create",
                "player": self.player.id,
                "relationship": UserPlayerRelationship.COACH,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An active link already exists")

    def test_profile_page_links_staff_to_account_operations(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("accounts:operations-dashboard"))

    def test_profile_page_does_not_link_regular_user_to_account_operations(self):
        self.client.force_login(self.regular)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("accounts:operations-dashboard"))

    def test_account_create_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(reverse("accounts:account-create"))

        self.assertEqual(response.status_code, 403)

    def test_staff_can_create_account_only_and_see_one_time_password(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:account-create"),
            {
                "username": "new.evaluator",
                "first_name": "New",
                "last_name": "Evaluator",
                "email": "new@example.com",
                "role": AccountRole.GUEST_EVALUATOR,
                "is_active": "on",
            },
        )

        user = User.objects.get(username="new.evaluator")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account Created")
        self.assertContains(response, "Temporary password")
        temporary_password = response.context["created_account"].temporary_password
        self.assertIn(temporary_password, response.content.decode())
        self.assertNotIn(temporary_password, " ".join(str(message) for message in get_messages(response.wsgi_request)))
        self.assertTrue(user.account_profile.must_change_password)
        self.assertEqual(user.account_profile.role, AccountRole.GUEST_EVALUATOR)
        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())

        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": user.id}))
        self.assertNotContains(detail_response, temporary_password)
        get_response = self.client.get(reverse("accounts:account-create"))
        self.assertNotContains(get_response, temporary_password)

    def test_staff_cannot_create_admin_account(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:account-create"),
            {
                "username": "admin.try",
                "role": AccountRole.ADMIN,
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Only superusers can create admin accounts")
        self.assertNotContains(response, "Temporary password")
        self.assertFalse(User.objects.filter(username="admin.try").exists())

    def test_player_account_create_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(reverse("accounts:player-account-create"))

        self.assertEqual(response.status_code, 403)

    def test_staff_can_create_player_account_for_existing_player(self):
        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:player-account-create"),
            {
                "player": player.id,
                "email": "blake@example.com",
                "role": AccountRole.PLAYER,
                "is_active": "on",
            },
        )

        user = User.objects.get(username="blake.player")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Player Account Created")
        self.assertContains(response, "20130602")
        self.assertNotIn("20130602", " ".join(str(message) for message in get_messages(response.wsgi_request)))
        self.assertTrue(user.check_password("20130602"))
        self.assertTrue(user.account_profile.must_change_password)
        self.assertEqual(UserPlayerLink.objects.get(user=user).player, player)

        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": user.id}))
        self.assertNotContains(detail_response, "20130602")
        get_response = self.client.get(reverse("accounts:player-account-create"))
        self.assertNotContains(get_response, "20130602")

    def test_player_account_create_rejects_duplicate_player_account(self):
        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
        create_player_account(actor=self.staff, player=player)
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:player-account-create"),
            {
                "player": player.id,
                "role": AccountRole.PLAYER,
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Player already has a linked user account")
        self.assertEqual(UserPlayerLink.objects.filter(player=player, relationship=UserPlayerRelationship.SELF).count(), 1)


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

    def test_account_operations_routes_are_platform_account_routes(self):
        self.assertEqual(reverse("accounts:operations-dashboard"), "/accounts/")
        self.assertEqual(reverse("accounts:user-list"), "/accounts/users/")

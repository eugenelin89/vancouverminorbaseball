from django.test import override_settings

from accounts.tests.helpers import (
    AccountListFilters,
    AccountRole,
    CoachSeasonAssignment,
    Player,
    PlayerImportBatch,
    SimpleUploadedFile,
    TestCase,
    User,
    UserPlayerLink,
    UserPlayerRelationship,
    ValidationError,
    activate_account,
    bulk_account_operation,
    count_players_without_self_link,
    create_account_only,
    create_player_account,
    create_season,
    create_user_player_link,
    deactivate_account,
    deactivate_user_player_link,
    filter_account_users,
    get_account_detail,
    get_account_list,
    get_account_operations_dashboard,
    get_messages,
    get_or_create_account_profile,
    link_user_to_player,
    mark_password_change_required,
    reactivate_user_player_link,
    reset_account_password,
    reverse,
    set_account_role,
    set_primary_user_player_link,
    update_account,
)

COACH_IMPORT_TEST_PASSWORD = "CoachImportDefault123!"


class AccountOperationsServiceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
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
        self.inactive_user = User.objects.create_user(
            username="inactive", password="testpass", is_active=False
        )
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
            update_fields=[
                "created_from_import",
                "import_batch",
                "must_change_password",
                "updated_at",
            ]
        )
        get_or_create_account_profile(self.inactive_user)
        self.player = Player.objects.create(
            first_name="Alex", last_name="Player", birthdate="2012-05-01"
        )
        self.unlinked_player = Player.objects.create(
            first_name="No", last_name="Account"
        )
        link_user_to_player(
            self.player_user,
            self.player,
            relationship=UserPlayerRelationship.SELF,
            created_from_import=True,
            import_batch=self.import_batch,
        )

    def usernames_for_filters(self, **kwargs):
        return [
            user.username for user in filter_account_users(AccountListFilters(**kwargs))
        ]

    def test_account_query_filters_by_search_text(self):
        self.assertEqual(
            self.usernames_for_filters(search="coach@example.com"), ["coach.one"]
        )
        self.assertEqual(self.usernames_for_filters(search="Alex"), ["alex.player"])

    def test_account_query_filters_by_role(self):
        self.assertEqual(
            self.usernames_for_filters(role=AccountRole.COACH), ["coach.one"]
        )
        self.assertEqual(
            self.usernames_for_filters(role=AccountRole.PLAYER), ["alex.player"]
        )

    def test_account_query_filters_by_active_status(self):
        self.assertEqual(self.usernames_for_filters(active_status="no"), ["inactive"])

    def test_account_query_filters_by_staff_and_superuser_status(self):
        admin_user = User.objects.create_superuser(
            username="admin", password="testpass"
        )
        get_or_create_account_profile(admin_user)

        self.assertEqual(
            self.usernames_for_filters(staff_status="yes"), ["admin", "staff"]
        )
        self.assertEqual(self.usernames_for_filters(superuser_status="yes"), ["admin"])

    def test_account_query_filters_by_imported_and_password_status(self):
        self.assertEqual(
            self.usernames_for_filters(imported_status="yes"), ["alex.player"]
        )
        self.assertEqual(
            self.usernames_for_filters(must_change_password="yes"), ["alex.player"]
        )

    def test_account_query_filters_by_linked_status(self):
        self.assertEqual(
            self.usernames_for_filters(linked_status="linked"), ["alex.player"]
        )
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
        self.assertEqual(
            dashboard.users_requiring_password_change[0].user, self.player_user
        )

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
            create_account_only(
                actor=self.staff, username="DUPLICATE", role=AccountRole.COACH
            )
        with self.assertRaises(ValidationError):
            create_account_only(
                actor=self.staff,
                username="unique",
                email="Duplicate@Example.com",
                role=AccountRole.COACH,
            )

    def test_create_account_only_admin_requires_superuser(self):
        superuser = User.objects.create_superuser(
            username="ops.admin", password="testpass"
        )

        with self.assertRaises(ValidationError):
            create_account_only(
                actor=self.staff, username="admin.account", role=AccountRole.ADMIN
            )

        result = create_account_only(
            actor=superuser, username="admin.account", role=AccountRole.ADMIN
        )

        self.assertEqual(result.role, AccountRole.ADMIN)
        self.assertFalse(result.user.is_staff)
        self.assertFalse(result.user.is_superuser)

    def test_create_player_account_uses_existing_player_and_provisioning_logic(self):
        player = Player.objects.create(
            first_name="Blake", last_name="Player", birthdate="2013-06-02"
        )

        result = create_player_account(
            actor=self.staff, player=player, email="Blake@example.com"
        )

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
        player = Player.objects.create(
            first_name="Casey", last_name="Player", birthdate="2014-07-03"
        )

        result = create_player_account(
            actor=self.staff, player=player, username="Custom.Player", is_active=False
        )

        self.assertEqual(result.username, "custom.player")
        self.assertFalse(User.objects.get(username="custom.player").is_active)

    def test_create_player_account_rejects_duplicate_email_username_and_player_account(
        self,
    ):
        player = Player.objects.create(
            first_name="Dana", last_name="Player", birthdate="2015-08-04"
        )
        User.objects.create_user(username="taken", email="taken@example.com")

        with self.assertRaises(ValidationError):
            create_player_account(actor=self.staff, player=player, username="taken")
        with self.assertRaises(ValidationError):
            create_player_account(
                actor=self.staff, player=player, email="taken@example.com"
            )

        create_player_account(actor=self.staff, player=player, username="dana.player")
        with self.assertRaises(ValidationError):
            create_player_account(
                actor=self.staff, player=player, username="dana.player2"
            )

        self.assertEqual(
            UserPlayerLink.objects.filter(
                player=player, relationship=UserPlayerRelationship.SELF
            ).count(),
            1,
        )

    def test_create_player_account_requires_existing_player_birthdate_and_player_role(
        self,
    ):
        player = Player.objects.create(first_name="No", last_name="Birthdate")

        with self.assertRaises(ValidationError):
            create_player_account(actor=self.staff, player=player)
        with self.assertRaises(ValidationError):
            create_player_account(
                actor=self.staff, player=self.player, role=AccountRole.COACH
            )

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

        superuser = User.objects.create_superuser(
            username="ops.admin", password="testpass"
        )
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

    def test_account_operation_services_require_staff_actor(self):
        with self.assertRaisesMessage(
            ValidationError, "Only staff users can manage accounts"
        ):
            create_account_only(
                actor=self.coach, username="not.allowed", role=AccountRole.COACH
            )
        with self.assertRaisesMessage(
            ValidationError, "Only staff users can manage accounts"
        ):
            create_player_account(actor=self.coach, player=self.player)
        with self.assertRaisesMessage(
            ValidationError, "Only staff users can manage accounts"
        ):
            update_account(
                actor=self.coach,
                user_id=self.player_user.id,
                username="alex.player",
                role=AccountRole.PLAYER,
            )
        with self.assertRaisesMessage(
            ValidationError, "Only staff users can manage accounts"
        ):
            reset_account_password(actor=self.coach, user_id=self.player_user.id)
        with self.assertRaisesMessage(
            ValidationError, "Only staff users can manage accounts"
        ):
            bulk_account_operation(
                actor=self.coach, action="activate", user_ids=[self.player_user.id]
            )

    def test_staff_cannot_mutate_staff_or_superuser_accounts(self):
        other_staff = User.objects.create_user(
            username="other.staff", password="testpass", is_staff=True
        )
        superuser = User.objects.create_superuser(
            username="ops.admin", password="testpass"
        )
        superuser_actor = User.objects.create_superuser(
            username="ops.admin2", password="testpass"
        )

        with self.assertRaisesMessage(
            ValidationError, "Only superusers can manage staff or superuser accounts"
        ):
            update_account(
                actor=self.staff,
                user_id=other_staff.id,
                username="other.staff",
                role=AccountRole.STAFF,
            )
        with self.assertRaisesMessage(
            ValidationError, "Only superusers can manage staff or superuser accounts"
        ):
            activate_account(actor=self.staff, user_id=other_staff.id)
        with self.assertRaisesMessage(
            ValidationError, "Only superusers can manage staff or superuser accounts"
        ):
            deactivate_account(actor=self.staff, user_id=superuser.id)
        with self.assertRaisesMessage(
            ValidationError, "Only superusers can manage staff or superuser accounts"
        ):
            reset_account_password(actor=self.staff, user_id=superuser.id)
        with self.assertRaisesMessage(
            ValidationError, "Only superusers can manage staff or superuser accounts"
        ):
            create_user_player_link(
                actor=self.staff,
                user_id=other_staff.id,
                player=self.player,
                relationship=UserPlayerRelationship.STAFF,
            )

        result = reset_account_password(actor=superuser_actor, user_id=other_staff.id)
        other_staff.refresh_from_db()
        self.assertTrue(other_staff.check_password(result.temporary_password))

    def test_activate_and_deactivate_account_preserve_profile_and_links(self):
        deactivate_result = deactivate_account(
            actor=self.staff, user_id=self.player_user.id
        )
        self.player_user.refresh_from_db()
        link = UserPlayerLink.objects.get(user=self.player_user, player=self.player)

        self.assertFalse(deactivate_result.is_active)
        self.assertFalse(self.player_user.is_active)
        self.assertEqual(self.player_user.account_profile.role, AccountRole.PLAYER)
        self.assertTrue(link.is_active)

        activate_result = activate_account(
            actor=self.staff, user_id=self.player_user.id
        )
        self.player_user.refresh_from_db()

        self.assertTrue(activate_result.is_active)
        self.assertTrue(self.player_user.is_active)
        self.assertTrue(UserPlayerLink.objects.get(pk=link.pk).is_active)

    def test_deactivate_account_rejects_self_deactivation(self):
        with self.assertRaises(ValidationError):
            deactivate_account(actor=self.staff, user_id=self.staff.id)

        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_active)

    def test_update_account_rejects_self_deactivation(self):
        with self.assertRaises(ValidationError):
            update_account(
                actor=self.staff,
                user_id=self.staff.id,
                username="staff",
                role=AccountRole.STAFF,
                is_active=False,
            )

        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_active)

    def test_deactivate_account_rejects_last_active_superuser(self):
        superuser = User.objects.create_superuser(
            username="ops.admin", password="testpass"
        )

        with self.assertRaises(ValidationError):
            deactivate_account(actor=self.staff, user_id=superuser.id)

        superuser.refresh_from_db()
        self.assertTrue(superuser.is_active)

    def test_deactivate_account_allows_superuser_actor_when_another_active_superuser_exists(
        self,
    ):
        superuser = User.objects.create_superuser(
            username="ops.admin", password="testpass"
        )
        actor = User.objects.create_superuser(username="ops.actor", password="testpass")
        User.objects.create_superuser(username="ops.admin2", password="testpass")

        result = deactivate_account(actor=actor, user_id=superuser.id)

        self.assertFalse(result.is_active)

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

        deactivated = deactivate_user_player_link(
            actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id
        )
        self.assertFalse(deactivated.is_active)
        self.assertFalse(UserPlayerLink.objects.get(pk=link_result.link.id).is_primary)

        reactivated = reactivate_user_player_link(
            actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id
        )
        self.assertTrue(reactivated.is_active)

    def test_account_operations_set_primary_self_link_switches_existing_primary(self):
        other_player = Player.objects.create(first_name="Second", last_name="Player")
        first_link = UserPlayerLink.objects.get(
            user=self.player_user, player=self.player
        )
        second_link = create_user_player_link(
            actor=self.staff,
            user_id=self.player_user.id,
            player=other_player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=False,
        ).link

        result = set_primary_user_player_link(
            actor=self.staff, user_id=self.player_user.id, link_id=second_link.id
        )
        first_link.refresh_from_db()
        second_link.refresh_from_db()

        self.assertTrue(result.is_primary)
        self.assertFalse(first_link.is_primary)
        self.assertTrue(second_link.is_primary)
        self.assertEqual(
            UserPlayerLink.objects.filter(
                user=self.player_user, is_primary=True, is_active=True
            ).count(),
            1,
        )

    def test_account_operations_reject_primary_non_self_link(self):
        link = create_user_player_link(
            actor=self.staff,
            user_id=self.coach.id,
            player=self.player,
            relationship=UserPlayerRelationship.PARENT,
            is_primary=False,
        ).link

        with self.assertRaises(ValidationError):
            set_primary_user_player_link(
                actor=self.staff, user_id=self.coach.id, link_id=link.id
            )

    def test_reset_account_password_uses_birthdate_for_player_account(self):
        self.player_user.account_profile.must_change_password = False
        self.player_user.account_profile.save(
            update_fields=["must_change_password", "updated_at"]
        )
        original_link_count = UserPlayerLink.objects.filter(
            user=self.player_user
        ).count()

        result = reset_account_password(actor=self.staff, user_id=self.player_user.id)

        self.player_user.refresh_from_db()
        self.assertEqual(result.user, self.player_user)
        self.assertEqual(result.username, "alex.player")
        self.assertEqual(result.temporary_password, "20120501")
        self.assertTrue(self.player_user.check_password("20120501"))
        self.assertTrue(self.player_user.account_profile.must_change_password)
        self.assertTrue(self.player_user.is_active)
        self.assertEqual(self.player_user.account_profile.role, AccountRole.PLAYER)
        self.assertTrue(self.player_user.account_profile.created_from_import)
        self.assertEqual(
            self.player_user.account_profile.import_batch, self.import_batch
        )
        self.assertEqual(
            UserPlayerLink.objects.filter(user=self.player_user).count(),
            original_link_count,
        )
        self.assertNotIn(result.temporary_password, repr(result))

    def test_reset_account_password_uses_random_password_for_non_player_account(self):
        self.coach.account_profile.must_change_password = False
        self.coach.account_profile.save(
            update_fields=["must_change_password", "updated_at"]
        )

        result = reset_account_password(actor=self.staff, user_id=self.coach.id)

        self.coach.refresh_from_db()
        self.assertTrue(result.temporary_password)
        self.assertNotEqual(result.temporary_password, "20120501")
        self.assertTrue(self.coach.check_password(result.temporary_password))
        self.assertTrue(self.coach.account_profile.must_change_password)
        self.assertTrue(self.coach.is_active)
        self.assertEqual(self.coach.account_profile.role, AccountRole.COACH)
        self.assertFalse(
            UserPlayerLink.objects.filter(
                user=self.coach, relationship=UserPlayerRelationship.SELF
            ).exists()
        )
        self.assertNotIn(result.temporary_password, repr(result))

    def test_reset_account_password_preserves_inactive_account_state(self):
        self.assertFalse(self.inactive_user.is_active)

        result = reset_account_password(actor=self.staff, user_id=self.inactive_user.id)

        self.inactive_user.refresh_from_db()
        self.assertFalse(self.inactive_user.is_active)
        self.assertTrue(self.inactive_user.check_password(result.temporary_password))
        self.assertTrue(self.inactive_user.account_profile.must_change_password)

    def test_reset_account_password_rejects_player_account_missing_birthdate(self):
        player = Player.objects.create(first_name="No", last_name="Birthdate")
        user = User.objects.create_user(username="no.birthdate", password="testpass")
        set_account_role(user, AccountRole.PLAYER)
        link_user_to_player(user, player)

        with self.assertRaises(ValidationError):
            reset_account_password(actor=self.staff, user_id=user.id)

    def test_bulk_account_operation_activates_accounts(self):
        result = bulk_account_operation(
            actor=self.staff, action="activate", user_ids=[self.inactive_user.id]
        )

        self.inactive_user.refresh_from_db()
        self.assertEqual(result.processed, 1)
        self.assertEqual(result.successful, 1)
        self.assertEqual(result.failed, 0)
        self.assertTrue(self.inactive_user.is_active)

    def test_bulk_account_operation_deactivates_accounts(self):
        result = bulk_account_operation(
            actor=self.staff, action="deactivate", user_ids=[self.coach.id]
        )

        self.coach.refresh_from_db()
        self.assertEqual(result.processed, 1)
        self.assertEqual(result.successful, 1)
        self.assertFalse(self.coach.is_active)

    def test_bulk_account_operation_sets_password_change_requirement(self):
        mark_password_change_required(self.coach, False)

        result = bulk_account_operation(
            actor=self.staff,
            action="require_password_change",
            user_ids=[self.coach.id],
        )

        self.coach.refresh_from_db()
        self.assertEqual(result.successful, 1)
        self.assertTrue(self.coach.account_profile.must_change_password)

    def test_bulk_account_operation_clears_password_change_requirement(self):
        mark_password_change_required(self.player_user, True)

        result = bulk_account_operation(
            actor=self.staff,
            action="clear_password_change",
            user_ids=[self.player_user.id],
        )

        self.player_user.refresh_from_db()
        self.assertEqual(result.successful, 1)
        self.assertFalse(self.player_user.account_profile.must_change_password)

    def test_bulk_account_operation_continues_after_failure(self):
        result = bulk_account_operation(
            actor=self.staff,
            action="deactivate",
            user_ids=[self.staff.id, self.coach.id],
        )

        self.staff.refresh_from_db()
        self.coach.refresh_from_db()
        self.assertEqual(result.processed, 2)
        self.assertEqual(result.successful, 1)
        self.assertEqual(result.failed, 1)
        self.assertEqual(result.errors[0].username, "staff")
        self.assertIn("cannot deactivate your own account", result.errors[0].message)
        self.assertTrue(self.staff.is_active)
        self.assertFalse(self.coach.is_active)

    def test_bulk_account_operation_rejects_empty_selection_and_unknown_action(self):
        with self.assertRaises(ValidationError):
            bulk_account_operation(actor=self.staff, action="activate", user_ids=[])
        with self.assertRaises(ValidationError):
            bulk_account_operation(
                actor=self.staff, action="unsupported", user_ids=[self.coach.id]
            )

    def test_bulk_account_operation_reports_missing_users(self):
        result = bulk_account_operation(
            actor=self.staff, action="activate", user_ids=[999999]
        )

        self.assertEqual(result.processed, 1)
        self.assertEqual(result.successful, 0)
        self.assertEqual(result.failed, 1)
        self.assertEqual(result.errors[0].username, "Unknown account")
        self.assertEqual(result.errors[0].message, "Account not found.")

    def test_bulk_account_operation_rejects_last_superuser_deactivation(self):
        superuser = User.objects.create_superuser(
            username="ops.admin", password="testpass"
        )

        result = bulk_account_operation(
            actor=self.staff, action="deactivate", user_ids=[superuser.id]
        )

        superuser.refresh_from_db()
        self.assertEqual(result.successful, 0)
        self.assertEqual(result.failed, 1)
        self.assertEqual(result.errors[0].username, "ops.admin")
        self.assertIn("last active superuser", result.errors[0].message)
        self.assertTrue(superuser.is_active)


@override_settings(COACH_IMPORT_DEFAULT_PASSWORD=COACH_IMPORT_TEST_PASSWORD)
class AccountOperationsViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        self.superuser = User.objects.create_superuser(
            username="admin", password="testpass"
        )
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
        link_user_to_player(
            self.coach,
            self.player,
            relationship=UserPlayerRelationship.COACH,
            is_primary=False,
        )
        self.season = create_season(
            key="2026-spring", name="2026 Spring", is_current=True
        )

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
        self.assertContains(response, reverse("accounts:coach-import-list"))

    def test_user_list_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(reverse("accounts:user-list"))

        self.assertEqual(response.status_code, 403)

    def test_user_list_renders_users_and_filters(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("accounts:user-list"), {"q": "coach", "role": AccountRole.COACH}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account Users")
        self.assertContains(response, "coach.one")
        self.assertContains(response, "Coach")
        self.assertNotContains(response, "regular")
        self.assertContains(response, "Bulk action")
        self.assertContains(response, "Select all accounts shown")

    def test_user_list_bulk_post_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.post(
            reverse("accounts:user-list"),
            {
                "action": "activate",
                "user_ids": [self.coach.id],
                "visible_user_ids": [self.coach.id],
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_can_bulk_activate_from_user_list(self):
        self.coach.is_active = False
        self.coach.save(update_fields=["is_active"])
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-list"),
            {
                "action": "activate",
                "user_ids": [self.coach.id],
                "visible_user_ids": [self.coach.id],
            },
        )

        self.coach.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 succeeded, 0 failed")
        self.assertTrue(self.coach.is_active)

    def test_staff_can_bulk_require_and_clear_password_change_from_user_list(self):
        mark_password_change_required(self.coach, False)
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-list"),
            {
                "action": "require_password_change",
                "user_ids": [self.coach.id],
                "visible_user_ids": [self.coach.id],
            },
        )

        self.coach.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.coach.account_profile.must_change_password)

        response = self.client.post(
            reverse("accounts:user-list"),
            {
                "action": "clear_password_change",
                "user_ids": [self.coach.id],
                "visible_user_ids": [self.coach.id],
            },
        )

        self.coach.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.coach.account_profile.must_change_password)

    def test_staff_bulk_deactivate_reports_self_failure_and_successes(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-list"),
            {
                "action": "deactivate",
                "user_ids": [self.staff.id, self.coach.id],
                "visible_user_ids": [self.staff.id, self.coach.id],
            },
        )

        self.staff.refresh_from_db()
        self.coach.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 succeeded, 1 failed")
        self.assertContains(response, "staff")
        self.assertContains(response, "cannot deactivate your own account")
        self.assertTrue(self.staff.is_active)
        self.assertFalse(self.coach.is_active)

    def test_staff_bulk_action_rejects_empty_selection_and_unknown_action(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-list"),
            {"action": "activate", "visible_user_ids": [self.coach.id]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select at least one account")

        response = self.client.post(
            reverse("accounts:user-list"),
            {
                "action": "unsupported",
                "user_ids": [self.coach.id],
                "visible_user_ids": [self.coach.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice")

    def test_staff_bulk_select_all_uses_visible_user_ids(self):
        self.coach.is_active = False
        self.coach.save(update_fields=["is_active"])
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-list"),
            {
                "action": "activate",
                "select_all": "on",
                "visible_user_ids": [self.coach.id],
            },
        )

        self.coach.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.coach.is_active)

    def test_user_detail_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(
            reverse("accounts:user-detail", kwargs={"user_id": self.coach.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_user_detail_missing_account_returns_404(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("accounts:user-detail", kwargs={"user_id": 999999})
        )

        self.assertEqual(response.status_code, 404)

    def test_user_detail_renders_profile_and_linked_players(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("accounts:user-detail", kwargs={"user_id": self.coach.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "coach.one")
        self.assertContains(response, "coach@example.com")
        self.assertContains(response, "Coach")
        self.assertContains(response, "Alex Player")
        self.assertContains(
            response, reverse("accounts:user-edit", kwargs={"user_id": self.coach.id})
        )
        self.assertContains(
            response, reverse("accounts:user-links", kwargs={"user_id": self.coach.id})
        )
        self.assertContains(
            response,
            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}),
        )

    def test_user_edit_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(
            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id})
        )

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
        self.assertEqual(
            response["Location"],
            reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}),
        )
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

    def test_staff_user_edit_rejects_staff_or_superuser_target(self):
        other_staff = User.objects.create_user(
            username="other.staff", password="testpass", is_staff=True
        )
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-edit", kwargs={"user_id": other_staff.id}),
            {
                "username": "other.staff",
                "role": AccountRole.STAFF,
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Only superusers can manage staff or superuser accounts"
        )

    def test_user_links_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(
            reverse("accounts:user-links", kwargs={"user_id": self.coach.id})
        )

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
        link = UserPlayerLink.objects.get(
            user=self.coach,
            player=other_player,
            relationship=UserPlayerRelationship.PARENT,
        )
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
        first_link = link_user_to_player(
            self.coach, first_player, relationship=UserPlayerRelationship.SELF
        )
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

    def test_links_page_handles_invalid_link_id_as_form_error(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
            {"action": "deactivate", "link_id": "999999"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Player link not found")

    def test_links_page_handles_unknown_action_as_form_error(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
            {"action": "unsupported", "link_id": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unsupported link action")

    def test_password_reset_requires_staff(self):
        self.client.force_login(self.regular)

        response = self.client.get(
            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_can_reset_non_player_password_and_see_password_once(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}),
            {"confirm": "on"},
        )

        self.coach.refresh_from_db()
        temporary_password = response.context[
            "password_reset_result"
        ].temporary_password
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password Reset Complete")
        self.assertContains(response, temporary_password)
        self.assertTrue(self.coach.check_password(temporary_password))
        self.assertTrue(self.coach.account_profile.must_change_password)
        self.assertNotIn(
            temporary_password,
            " ".join(str(message) for message in get_messages(response.wsgi_request)),
        )

        refresh_response = self.client.get(
            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id})
        )
        detail_response = self.client.get(
            reverse("accounts:user-detail", kwargs={"user_id": self.coach.id})
        )
        self.assertNotContains(refresh_response, temporary_password)
        self.assertNotContains(detail_response, temporary_password)

    def test_staff_can_reset_player_password_with_birthdate_password(self):
        player = Player.objects.create(
            first_name="Blake", last_name="Player", birthdate="2013-06-02"
        )
        user = User.objects.create_user(username="blake.player", password="testpass")
        set_account_role(user, AccountRole.PLAYER)
        link_user_to_player(user, player)
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-password-reset", kwargs={"user_id": user.id}),
            {"confirm": "on"},
        )

        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "20130602")
        self.assertTrue(user.check_password("20130602"))
        self.assertTrue(user.account_profile.must_change_password)

    def test_password_reset_does_not_run_without_confirmation(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}),
            {},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        self.coach.refresh_from_db()
        self.assertTrue(self.coach.check_password("testpass"))

    def test_password_reset_missing_account_returns_404(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("accounts:user-password-reset", kwargs={"user_id": 999999})
        )

        self.assertEqual(response.status_code, 404)

    def test_staff_password_reset_rejects_staff_or_superuser_target(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse(
                "accounts:user-password-reset", kwargs={"user_id": self.superuser.id}
            ),
            {"confirm": "on"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Only superusers can manage staff or superuser accounts"
        )
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.check_password("testpass"))

    def test_profile_page_links_staff_to_account_operations(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("accounts:operations-dashboard"))

    def test_profile_page_does_not_link_regular_user_to_account_operations(self):
        self.client.force_login(self.regular)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, f'href="{reverse("accounts:operations-dashboard")}"'
        )
        self.assertNotContains(response, "Account Operations")

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
        self.assertNotIn(
            temporary_password,
            " ".join(str(message) for message in get_messages(response.wsgi_request)),
        )
        self.assertTrue(user.account_profile.must_change_password)
        self.assertEqual(user.account_profile.role, AccountRole.GUEST_EVALUATOR)
        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())

        detail_response = self.client.get(
            reverse("accounts:user-detail", kwargs={"user_id": user.id})
        )
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
        player = Player.objects.create(
            first_name="Blake", last_name="Player", birthdate="2013-06-02"
        )
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
        self.assertNotIn(
            "20130602",
            " ".join(str(message) for message in get_messages(response.wsgi_request)),
        )
        self.assertTrue(user.check_password("20130602"))
        self.assertTrue(user.account_profile.must_change_password)
        self.assertEqual(UserPlayerLink.objects.get(user=user).player, player)

        detail_response = self.client.get(
            reverse("accounts:user-detail", kwargs={"user_id": user.id})
        )
        self.assertNotContains(detail_response, "20130602")
        get_response = self.client.get(reverse("accounts:player-account-create"))
        self.assertNotContains(get_response, "20130602")

    def test_player_account_create_rejects_duplicate_player_account(self):
        player = Player.objects.create(
            first_name="Blake", last_name="Player", birthdate="2013-06-02"
        )
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
        self.assertEqual(
            UserPlayerLink.objects.filter(
                player=player, relationship=UserPlayerRelationship.SELF
            ).count(),
            1,
        )

    def test_coach_import_pages_require_staff(self):
        self.client.force_login(self.regular)

        urls = [
            reverse("accounts:coach-import-list"),
            reverse("accounts:coach-import-new"),
            reverse("accounts:coach-import-preview"),
            reverse("accounts:coach-import-confirm"),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

    def test_staff_can_preview_and_confirm_coach_import(self):
        self.client.force_login(self.staff)
        csv_file = SimpleUploadedFile(
            "coaches.csv",
            b"first_name,last_name,email,team,division\nNew,Coach,new.coach@example.com,Reds,13U\n",
            content_type="text/csv",
        )

        upload_response = self.client.post(
            reverse("accounts:coach-import-new"),
            {"season": str(self.season.id), "csv_file": csv_file},
        )
        self.assertEqual(upload_response.status_code, 302)
        self.assertEqual(
            upload_response["Location"], reverse("accounts:coach-import-preview")
        )

        preview_response = self.client.get(reverse("accounts:coach-import-preview"))
        self.assertEqual(preview_response.status_code, 200)
        self.assertContains(preview_response, "Ready to create")
        self.assertContains(preview_response, "new.coach@example.com")

        confirm_response = self.client.post(
            reverse("accounts:coach-import-confirm"), {"confirm": "on"}
        )
        self.assertEqual(confirm_response.status_code, 200)
        self.assertContains(confirm_response, "Coach Import Result")
        self.assertContains(confirm_response, "configured default password")
        self.assertNotContains(confirm_response, COACH_IMPORT_TEST_PASSWORD)
        user = User.objects.get(username="new.coach")
        result_row = confirm_response.context["result"].rows[0]
        self.assertFalse(hasattr(result_row, "temporary_password"))
        self.assertTrue(user.check_password(COACH_IMPORT_TEST_PASSWORD))
        self.assertTrue(user.is_active)
        self.assertEqual(user.account_profile.role, AccountRole.COACH)
        self.assertTrue(user.account_profile.must_change_password)
        self.assertEqual(
            CoachSeasonAssignment.objects.filter(
                user=user, season_team__season=self.season
            ).count(),
            1,
        )
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
        self.assertEqual(Player.objects.count(), 1)
        self.assertNotIn("coach_import_csv", self.client.session)

        detail_response = self.client.get(
            reverse("accounts:user-detail", kwargs={"user_id": user.id})
        )
        self.assertNotContains(detail_response, COACH_IMPORT_TEST_PASSWORD)
        list_response = self.client.get(reverse("accounts:coach-import-list"))
        self.assertNotContains(list_response, COACH_IMPORT_TEST_PASSWORD)
        preview_again = self.client.get(reverse("accounts:coach-import-preview"))
        self.assertEqual(preview_again.status_code, 302)
        confirm_again = self.client.get(reverse("accounts:coach-import-confirm"))
        self.assertEqual(confirm_again.status_code, 302)

    def test_coach_import_preview_rejects_manipulated_inactive_season(self):
        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
        self.client.force_login(self.staff)
        session = self.client.session
        session["coach_import_csv"] = (
            "first_name,last_name,email,team,division\nBad,Season,bad.season@example.com,Reds,13U\n"
        )
        session["coach_import_season_id"] = inactive.id
        session.save()

        preview_response = self.client.get(reverse("accounts:coach-import-preview"))
        confirm_response = self.client.post(
            reverse("accounts:coach-import-confirm"), {"confirm": "on"}
        )

        self.assertEqual(preview_response.status_code, 302)
        self.assertEqual(
            preview_response["Location"], reverse("accounts:coach-import-new")
        )
        self.assertEqual(confirm_response.status_code, 302)
        self.assertFalse(User.objects.filter(email="bad.season@example.com").exists())

    def test_coach_import_reuses_existing_coach_and_blocks_non_coach_email(self):
        existing_coach = User.objects.create_user(
            username="existing.coach", email="existing@example.com"
        )
        set_account_role(existing_coach, AccountRole.COACH)
        existing_player = User.objects.create_user(
            username="existing.player", email="player@example.com"
        )
        set_account_role(existing_player, AccountRole.PLAYER)
        self.client.force_login(self.staff)
        csv_file = SimpleUploadedFile(
            "coaches.csv",
            (
                "first_name,last_name,email,team,division\n"
                "Existing,Coach,existing@example.com,Reds,13U\n"
                "Existing,Player,player@example.com,Reds,13U\n"
            ).encode(),
            content_type="text/csv",
        )

        self.client.post(
            reverse("accounts:coach-import-new"),
            {"season": str(self.season.id), "csv_file": csv_file},
        )
        response = self.client.post(
            reverse("accounts:coach-import-confirm"), {"confirm": "on"}
        )

        self.assertEqual(response.status_code, 200)
        result = response.context["result"]
        self.assertEqual(result.existing_coaches_reused, 1)
        self.assertEqual(result.conflicts, 1)
        existing_coach.refresh_from_db()
        self.assertFalse(hasattr(result.rows[0], "temporary_password"))
        self.assertFalse(existing_coach.account_profile.must_change_password)
        self.assertEqual(existing_coach.account_profile.role, AccountRole.COACH)
        self.assertEqual(
            CoachSeasonAssignment.objects.filter(
                user=existing_coach, season_team__season=self.season
            ).count(),
            1,
        )
        self.assertEqual(
            User.objects.filter(email__iexact="existing@example.com").count(), 1
        )
        self.assertEqual(
            User.objects.filter(email__iexact="player@example.com").count(), 1
        )

        detail_response = self.client.get(
            reverse("accounts:user-detail", kwargs={"user_id": existing_coach.id})
        )
        self.assertNotContains(detail_response, "Password unchanged")

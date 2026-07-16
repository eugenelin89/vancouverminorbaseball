from accounts.tests.helpers import (
    IntegrityError,
    Player,
    PlayerImportBatch,
    TestCase,
    User,
    UserPlayerLink,
    UserPlayerRelationship,
    ValidationError,
    activate_link,
    deactivate_link,
    get_players_for_user,
    get_primary_player,
    get_primary_user,
    get_users_for_player,
    is_player_self,
    link_user_to_player,
    set_primary_self_link,
    transaction,
    unlink_user_from_player,
)


class UserPlayerLinkModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player", password="testpass")
        self.other_user = User.objects.create_user(
            username="other", password="testpass"
        )
        self.player = Player.objects.create(first_name="Alex", last_name="Player")
        self.other_player = Player.objects.create(
            first_name="Blake", last_name="Player"
        )

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

        self.assertEqual(
            UserPlayerLink.objects.filter(user=self.user, is_active=True).count(), 2
        )

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

        self.assertEqual(
            UserPlayerLink.objects.filter(player=self.player, is_active=True).count(), 2
        )

    def test_duplicate_active_relationship_is_blocked_but_inactive_history_is_allowed(
        self,
    ):
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
        self.other_user = User.objects.create_user(
            username="other", password="testpass"
        )
        self.player = Player.objects.create(first_name="Alex", last_name="Player")
        self.other_player = Player.objects.create(
            first_name="Blake", last_name="Player"
        )

    def test_link_user_to_player_creates_active_link(self):
        link = link_user_to_player(self.user, self.player)

        self.assertEqual(link.user, self.user)
        self.assertEqual(link.player, self.player)
        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
        self.assertTrue(link.is_primary)
        self.assertTrue(link.is_active)

    def test_link_user_to_player_reuses_existing_active_link(self):
        link = link_user_to_player(
            self.user, self.player, metadata={"source": "initial"}
        )
        same_link = link_user_to_player(
            self.user,
            self.player,
            created_from_import=True,
            metadata={"source": "updated"},
        )

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

        count = unlink_user_from_player(
            self.user, self.player, relationship=UserPlayerRelationship.PARENT
        )

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
        self.assertCountEqual(
            list(get_players_for_user(self.user, active_only=False)),
            [self.player, self.other_player],
        )
        self.assertEqual(list(get_users_for_player(self.player)), [self.user])
        self.assertEqual(list(get_users_for_player(self.other_player)), [])
        self.assertEqual(
            list(get_users_for_player(self.other_player, active_only=False)),
            [self.user],
        )
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

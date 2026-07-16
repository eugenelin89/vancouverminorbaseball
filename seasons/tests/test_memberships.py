from seasons.tests.helpers import (
    Player,
    PlayerRosterMembership,
    RosterStatus,
    TestCase,
    ValidationError,
    create_membership,
    create_season,
    current_team_division,
    date,
    deactivate_membership,
    get_current_membership,
    get_or_create_season_team,
    get_primary_membership,
    memberships_for_player,
    sync_player_current_team_fields,
    transfer_player,
    update_membership,
)


class PlayerMembershipTests(TestCase):
    def setUp(self):
        self.spring = create_season(
            key="2026-spring", name="2026 Spring", is_current=True
        )
        self.next_spring = create_season(key="2027-spring", name="2027 Spring")
        self.dodgers, _ = get_or_create_season_team(
            season=self.spring, name="Dodgers", division="13U"
        )
        self.expos, _ = get_or_create_season_team(
            season=self.spring, name="Expos", division="13U"
        )
        self.mounties, _ = get_or_create_season_team(
            season=self.next_spring, name="Mounties", division="15U"
        )
        self.player = Player.objects.create(
            first_name="Alex", last_name="Player", team_name="Legacy", division="Legacy"
        )

    def test_player_may_join_one_team_and_different_seasons(self):
        first = create_membership(
            player=self.player, season_team=self.dodgers, is_primary=True
        )
        second = create_membership(
            player=self.player, season_team=self.mounties, is_primary=True
        )

        self.assertEqual(first.player, self.player)
        self.assertEqual(second.player, self.player)
        self.assertEqual(memberships_for_player(self.player).count(), 2)

    def test_multiple_memberships_in_one_season_and_non_primary_concurrent_allowed(
        self,
    ):
        primary = create_membership(
            player=self.player, season_team=self.dodgers, is_primary=True
        )
        guest = create_membership(
            player=self.player,
            season_team=self.expos,
            status=RosterStatus.GUEST,
            is_primary=False,
        )

        self.assertTrue(primary.is_primary)
        self.assertFalse(guest.is_primary)
        self.assertEqual(memberships_for_player(self.player, self.spring).count(), 2)

    def test_only_one_active_primary_membership_per_player_season(self):
        first = create_membership(
            player=self.player, season_team=self.dodgers, is_primary=True
        )
        second = create_membership(
            player=self.player, season_team=self.expos, is_primary=True
        )

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_primary)
        self.assertTrue(second.is_primary)
        self.assertEqual(get_primary_membership(self.player, self.spring), second)

    def test_update_membership_can_unset_primary(self):
        membership = create_membership(
            player=self.player, season_team=self.dodgers, is_primary=True
        )

        update_membership(membership, is_primary=False)
        membership.refresh_from_db()

        self.assertFalse(membership.is_primary)

    def test_direct_duplicate_primary_membership_is_rejected(self):
        create_membership(player=self.player, season_team=self.dodgers, is_primary=True)

        with self.assertRaises(ValidationError):
            PlayerRosterMembership.objects.create(
                player=self.player, season_team=self.expos, is_primary=True
            )

    def test_transfer_creates_new_membership_and_preserves_history(self):
        old = create_membership(
            player=self.player, season_team=self.dodgers, is_primary=True
        )

        new = transfer_player(
            player=self.player,
            to_season_team=self.expos,
            transfer_date=date(2026, 6, 1),
        )
        old.refresh_from_db()
        self.player.refresh_from_db()

        self.assertFalse(old.is_active)
        self.assertFalse(old.is_primary)
        self.assertEqual(old.status, RosterStatus.TRANSFERRED)
        self.assertEqual(old.ends_on, date(2026, 6, 1))
        self.assertTrue(new.is_primary)
        self.assertEqual(self.player.team_name, "Expos")
        self.assertEqual(self.player.division, "13U")

    def test_date_validation(self):
        with self.assertRaises(ValidationError):
            create_membership(
                player=self.player,
                season_team=self.dodgers,
                starts_on=date(2026, 8, 1),
                ends_on=date(2026, 7, 1),
            )

    def test_current_membership_derivation_and_team_division(self):
        create_membership(
            player=self.player, season_team=self.dodgers, is_primary=False
        )
        primary = create_membership(
            player=self.player, season_team=self.expos, is_primary=True
        )

        self.assertEqual(get_current_membership(self.player, self.spring), primary)
        self.assertEqual(
            current_team_division(self.player, self.spring), ("Expos", "13U")
        )

    def test_compatibility_sync_is_explicit_and_can_clear_when_requested(self):
        create_membership(
            player=self.player,
            season_team=self.dodgers,
            is_primary=True,
            sync_player_fields=False,
        )
        self.player.refresh_from_db()

        self.assertEqual(self.player.team_name, "Legacy")
        sync_player_current_team_fields(self.player, self.spring)
        self.player.refresh_from_db()
        self.assertEqual(self.player.team_name, "Dodgers")
        self.assertEqual(self.player.division, "13U")

        deactivate_membership(
            get_primary_membership(self.player, self.spring), sync_player_fields=False
        )
        sync_player_current_team_fields(
            self.player, self.spring, clear_when_missing=False
        )
        self.player.refresh_from_db()
        self.assertEqual(self.player.team_name, "Dodgers")

        sync_player_current_team_fields(
            self.player, self.spring, clear_when_missing=True
        )
        self.player.refresh_from_db()
        self.assertEqual(self.player.team_name, "")
        self.assertEqual(self.player.division, "")

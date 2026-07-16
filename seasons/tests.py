from datetime import date

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase

from accounts.models import AccountRole
from accounts.services.profile_service import get_or_create_account_profile, set_account_role
from players.models import Player
from seasons.models import (
    CoachAssignmentRole,
    CoachSeasonAssignment,
    PlayerRosterMembership,
    RosterStatus,
    Season,
    SeasonTeam,
)
from seasons.services.coach_assignment_service import (
    assignments_for_team,
    assignments_for_user,
    create_assignment,
    deactivate_assignment,
    get_primary_assignment,
    set_primary_assignment,
    update_assignment,
)
from seasons.services.membership_service import (
    create_membership,
    current_team_division,
    deactivate_membership,
    get_current_membership,
    get_primary_membership,
    memberships_for_player,
    sync_player_current_team_fields,
    transfer_player,
    update_membership,
)
from seasons.services.season_service import create_season, deactivate_season, get_current_season, set_current_season
from seasons.services.team_service import get_or_create_season_team


User = get_user_model()


class SeasonModelServiceTests(TestCase):
    def test_seasons_app_is_installed(self):
        self.assertTrue(apps.is_installed("seasons"))

    def test_create_valid_season_normalizes_key(self):
        season = create_season(key=" 2026 Spring ", name=" 2026 Spring ", starts_on=date(2026, 4, 1))

        self.assertEqual(season.key, "2026-spring")
        self.assertEqual(season.name, "2026 Spring")
        self.assertTrue(season.is_active)
        self.assertFalse(season.is_current)

    def test_season_key_is_unique(self):
        create_season(key="2026-spring", name="2026 Spring")

        with self.assertRaises(ValidationError):
            create_season(key="2026 Spring", name="Duplicate")

    def test_season_requires_key_name_and_valid_dates(self):
        with self.assertRaises(ValidationError):
            create_season(key="", name="2026 Spring")
        with self.assertRaises(ValidationError):
            create_season(key="2026-spring", name="")
        with self.assertRaises(ValidationError):
            create_season(key="2026-spring", name="2026 Spring", starts_on=date(2026, 8, 1), ends_on=date(2026, 4, 1))

    def test_zero_current_seasons_allowed_before_setup(self):
        create_season(key="2026-spring", name="2026 Spring")

        self.assertIsNone(get_current_season())

    def test_set_first_current_season_and_switch_current(self):
        spring = create_season(key="2026-spring", name="2026 Spring")
        summer = create_season(key="2026-summer", name="2026 Summer")

        set_current_season(spring)
        self.assertEqual(get_current_season(), spring)

        set_current_season(summer)
        spring.refresh_from_db()
        summer.refresh_from_db()
        self.assertFalse(spring.is_current)
        self.assertTrue(summer.is_current)
        self.assertEqual(get_current_season(), summer)

    def test_model_validation_prevents_second_current_season(self):
        create_season(key="2026-spring", name="2026 Spring", is_current=True)

        with self.assertRaises(ValidationError):
            with transaction.atomic():
                Season.objects.create(key="2026-summer", name="2026 Summer", is_current=True)

    def test_inactive_historical_season_remains_queryable(self):
        season = create_season(key="2026-spring", name="2026 Spring", is_current=True)

        deactivate_season(season)
        season.refresh_from_db()

        self.assertFalse(season.is_active)
        self.assertFalse(season.is_current)
        self.assertEqual(Season.objects.get(pk=season.pk), season)


class SeasonTeamTests(TestCase):
    def setUp(self):
        self.spring = create_season(key="2026-spring", name="2026 Spring")
        self.next_spring = create_season(key="2027-spring", name="2027 Spring")

    def test_create_team_normalizes_values(self):
        team, created = get_or_create_season_team(season=self.spring, name="  Dodgers  ", division=" 13U   House ")

        self.assertTrue(created)
        self.assertEqual(team.normalized_name, "dodgers")
        self.assertEqual(team.normalized_division, "13u house")

    def test_same_normalized_team_division_reused(self):
        first, created_first = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
        second, created_second = get_or_create_season_team(season=self.spring, name=" dodgers ", division=" 13u ")

        self.assertTrue(created_first)
        self.assertFalse(created_second)
        self.assertEqual(first, second)

    def test_same_team_name_in_different_seasons_allowed(self):
        first, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
        second, _ = get_or_create_season_team(season=self.next_spring, name="Dodgers", division="13U")

        self.assertNotEqual(first, second)

    def test_external_identifier_scoped_to_season_and_blank_does_not_conflict(self):
        first, _ = get_or_create_season_team(
            season=self.spring,
            name="Dodgers",
            division="13U",
            external_source="Roster",
            external_identifier="ABC",
        )
        second, created_second = get_or_create_season_team(
            season=self.next_spring,
            name="Dodgers",
            division="13U",
            external_source="Roster",
            external_identifier="ABC",
        )
        blank_one, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
        blank_two, _ = get_or_create_season_team(season=self.spring, name="Mounties", division="13U")

        self.assertNotEqual(first, second)
        self.assertTrue(created_second)
        self.assertNotEqual(blank_one, blank_two)

    def test_external_identifier_conflict_rejected(self):
        get_or_create_season_team(
            season=self.spring,
            name="Dodgers",
            division="13U",
            external_source="Roster",
            external_identifier="ABC",
        )

        with self.assertRaises(ValidationError):
            get_or_create_season_team(
                season=self.spring,
                name="Expos",
                division="13U",
                external_source="roster",
                external_identifier="abc",
            )


class PlayerMembershipTests(TestCase):
    def setUp(self):
        self.spring = create_season(key="2026-spring", name="2026 Spring", is_current=True)
        self.next_spring = create_season(key="2027-spring", name="2027 Spring")
        self.dodgers, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
        self.expos, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
        self.mounties, _ = get_or_create_season_team(season=self.next_spring, name="Mounties", division="15U")
        self.player = Player.objects.create(first_name="Alex", last_name="Player", team_name="Legacy", division="Legacy")

    def test_player_may_join_one_team_and_different_seasons(self):
        first = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
        second = create_membership(player=self.player, season_team=self.mounties, is_primary=True)

        self.assertEqual(first.player, self.player)
        self.assertEqual(second.player, self.player)
        self.assertEqual(memberships_for_player(self.player).count(), 2)

    def test_multiple_memberships_in_one_season_and_non_primary_concurrent_allowed(self):
        primary = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
        guest = create_membership(player=self.player, season_team=self.expos, status=RosterStatus.GUEST, is_primary=False)

        self.assertTrue(primary.is_primary)
        self.assertFalse(guest.is_primary)
        self.assertEqual(memberships_for_player(self.player, self.spring).count(), 2)

    def test_only_one_active_primary_membership_per_player_season(self):
        first = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
        second = create_membership(player=self.player, season_team=self.expos, is_primary=True)

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_primary)
        self.assertTrue(second.is_primary)
        self.assertEqual(get_primary_membership(self.player, self.spring), second)

    def test_update_membership_can_unset_primary(self):
        membership = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)

        update_membership(membership, is_primary=False)
        membership.refresh_from_db()

        self.assertFalse(membership.is_primary)

    def test_direct_duplicate_primary_membership_is_rejected(self):
        create_membership(player=self.player, season_team=self.dodgers, is_primary=True)

        with self.assertRaises(ValidationError):
            PlayerRosterMembership.objects.create(player=self.player, season_team=self.expos, is_primary=True)

    def test_transfer_creates_new_membership_and_preserves_history(self):
        old = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)

        new = transfer_player(player=self.player, to_season_team=self.expos, transfer_date=date(2026, 6, 1))
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
        create_membership(player=self.player, season_team=self.dodgers, is_primary=False)
        primary = create_membership(player=self.player, season_team=self.expos, is_primary=True)

        self.assertEqual(get_current_membership(self.player, self.spring), primary)
        self.assertEqual(current_team_division(self.player, self.spring), ("Expos", "13U"))

    def test_compatibility_sync_is_explicit_and_can_clear_when_requested(self):
        create_membership(player=self.player, season_team=self.dodgers, is_primary=True, sync_player_fields=False)
        self.player.refresh_from_db()

        self.assertEqual(self.player.team_name, "Legacy")
        sync_player_current_team_fields(self.player, self.spring)
        self.player.refresh_from_db()
        self.assertEqual(self.player.team_name, "Dodgers")
        self.assertEqual(self.player.division, "13U")

        deactivate_membership(get_primary_membership(self.player, self.spring), sync_player_fields=False)
        sync_player_current_team_fields(self.player, self.spring, clear_when_missing=False)
        self.player.refresh_from_db()
        self.assertEqual(self.player.team_name, "Dodgers")

        sync_player_current_team_fields(self.player, self.spring, clear_when_missing=True)
        self.player.refresh_from_db()
        self.assertEqual(self.player.team_name, "")
        self.assertEqual(self.player.division, "")


class CoachAssignmentTests(TestCase):
    def setUp(self):
        self.spring = create_season(key="2026-spring", name="2026 Spring")
        self.dodgers, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
        self.expos, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
        self.coach = User.objects.create_user(
            username="coach",
            password="original-pass",
            first_name="Casey",
            last_name="Coach",
            email="coach@example.com",
        )
        set_account_role(self.coach, AccountRole.COACH)

    def test_create_assignment_and_query_helpers(self):
        assignment = create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
            is_primary=True,
        )

        self.assertEqual(assignments_for_user(self.coach, self.spring).first(), assignment)
        self.assertEqual(assignments_for_team(self.dodgers).first(), assignment)
        self.assertEqual(get_primary_assignment(self.coach, self.spring), assignment)

    def test_multiple_assignments_and_multiple_coaches_allowed(self):
        other = User.objects.create_user(username="other", password="testpass")

        first = create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)
        second = create_assignment(user=self.coach, season_team=self.expos, assignment_role=CoachAssignmentRole.EVALUATOR)
        third = create_assignment(user=other, season_team=self.dodgers, assignment_role=CoachAssignmentRole.ASSISTANT_COACH)

        self.assertEqual({first, second}, set(assignments_for_user(self.coach, self.spring)))
        self.assertIn(third, list(assignments_for_team(self.dodgers)))

    def test_duplicate_active_user_team_role_rejected(self):
        create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)

        with self.assertRaises(ValidationError):
            create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)

    def test_only_one_active_primary_assignment_per_user_season(self):
        first = create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH, is_primary=True)
        second = create_assignment(user=self.coach, season_team=self.expos, assignment_role=CoachAssignmentRole.EVALUATOR, is_primary=True)

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_primary)
        self.assertTrue(second.is_primary)

    def test_update_assignment_can_unset_primary(self):
        assignment = create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
            is_primary=True,
        )

        update_assignment(assignment, is_primary=False)
        assignment.refresh_from_db()

        self.assertFalse(assignment.is_primary)

    def test_direct_duplicate_primary_assignment_is_rejected(self):
        create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH, is_primary=True)

        with self.assertRaises(ValidationError):
            CoachSeasonAssignment.objects.create(
                user=self.coach,
                season_team=self.expos,
                assignment_role=CoachAssignmentRole.EVALUATOR,
                is_primary=True,
            )

    def test_assignment_has_no_account_role_privilege_or_password_side_effects(self):
        original_password = self.coach.password
        create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)
        self.coach.refresh_from_db()
        profile = get_or_create_account_profile(self.coach)

        self.assertEqual(profile.role, AccountRole.COACH)
        self.assertFalse(self.coach.is_staff)
        self.assertFalse(self.coach.is_superuser)
        self.assertEqual(self.coach.password, original_password)

    def test_assignment_date_validation_and_deactivation(self):
        with self.assertRaises(ValidationError):
            create_assignment(
                user=self.coach,
                season_team=self.dodgers,
                assignment_role=CoachAssignmentRole.HEAD_COACH,
                starts_on=date(2026, 8, 1),
                ends_on=date(2026, 7, 1),
            )

        assignment = create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
            is_primary=True,
        )
        deactivate_assignment(assignment, ends_on=date(2026, 8, 1))
        assignment.refresh_from_db()
        self.assertFalse(assignment.is_active)
        self.assertFalse(assignment.is_primary)
        self.assertEqual(assignment.ends_on, date(2026, 8, 1))


class SeasonsAdminTests(TestCase):
    def test_models_registered_in_admin(self):
        for model in [Season, SeasonTeam, PlayerRosterMembership, CoachSeasonAssignment]:
            self.assertIn(model, admin.site._registry)

    def test_admin_configuration_is_searchable_and_readonly_timestamps(self):
        for model in [Season, SeasonTeam, PlayerRosterMembership, CoachSeasonAssignment]:
            model_admin = admin.site._registry[model]
            self.assertIn("created_at", model_admin.readonly_fields)
            self.assertIn("updated_at", model_admin.readonly_fields)
            self.assertTrue(model_admin.search_fields)

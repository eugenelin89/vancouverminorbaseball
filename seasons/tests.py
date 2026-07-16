from datetime import date

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountRole
from accounts.services.profile_service import get_or_create_account_profile, set_account_role
from analytics.models import EvaluationCycle, RESPONSE_TYPE_RATING_1_5, RESPONSE_TYPE_TEXT
from analytics.services.observation_service import create_coach_assessment_observation, submit_observation
from analytics.services.question_service import ensure_default_coach_assessment_setup
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
from seasons.services.team_service import get_or_create_season_team, update_season_team


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


class SeasonOperationsUITests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.regular = User.objects.create_user(username="regular", password="testpass")
        self.coach = User.objects.create_user(
            username="coach",
            password="original-pass",
            first_name="Casey",
            last_name="Coach",
            email="coach@example.com",
        )
        set_account_role(self.coach, AccountRole.COACH)
        self.player = Player.objects.create(first_name="Alex", last_name="Player")
        self.spring = create_season(key="2026-spring", name="2026 Spring", starts_on=date(2026, 4, 1), is_current=True)
        self.summer = create_season(key="2026-summer", name="2026 Summer")
        self.dodgers, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
        self.expos, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
        self.mounties, _ = get_or_create_season_team(season=self.summer, name="Mounties", division="15U")

    def login_staff(self):
        self.client.force_login(self.staff)

    def test_season_operations_require_staff(self):
        url = reverse("seasons:season-list")

        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.regular)
        self.assertEqual(self.client.get(url).status_code, 403)

        self.login_staff()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2026 Spring")

    def test_staff_can_create_edit_and_set_current_season(self):
        self.login_staff()

        response = self.client.post(
            reverse("seasons:season-new"),
            {
                "key": "2027-spring",
                "name": "2027 Spring",
                "starts_on": "2027-04-01",
                "ends_on": "",
                "is_active": "on",
            },
        )
        season = Season.objects.get(key="2027-spring")
        self.assertRedirects(response, reverse("seasons:season-detail", kwargs={"season_id": season.id}))

        response = self.client.post(
            reverse("seasons:season-edit", kwargs={"season_id": season.id}),
            {
                "key": "2027-spring",
                "name": "2027 Spring Updated",
                "starts_on": "2027-04-01",
                "ends_on": "2027-08-31",
                "is_active": "on",
            },
        )
        self.assertRedirects(response, reverse("seasons:season-detail", kwargs={"season_id": season.id}))
        season.refresh_from_db()
        self.assertEqual(season.name, "2027 Spring Updated")

        self.client.post(reverse("seasons:season-set-current", kwargs={"season_id": season.id}), {"confirm": "on"})
        self.spring.refresh_from_db()
        season.refresh_from_db()
        self.assertFalse(self.spring.is_current)
        self.assertTrue(season.is_current)

        self.client.post(
            reverse("seasons:season-edit", kwargs={"season_id": season.id}),
            {
                "key": "2027-spring",
                "name": "2027 Spring Updated",
                "starts_on": "2027-04-01",
                "ends_on": "2027-08-31",
            },
        )
        season.refresh_from_db()
        self.assertFalse(season.is_active)
        self.assertFalse(season.is_current)

    def test_staff_can_create_and_edit_season_team(self):
        self.login_staff()

        response = self.client.post(
            reverse("seasons:season-team-new", kwargs={"season_id": self.spring.id}),
            {
                "season": self.spring.id,
                "name": "Cardinals",
                "division": "13U",
                "external_source": "Roster",
                "external_identifier": "TEAM-1",
                "is_active": "on",
            },
        )
        self.assertRedirects(response, reverse("seasons:team-list"))
        team = SeasonTeam.objects.get(name="Cardinals")

        response = self.client.post(
            reverse("seasons:team-edit", kwargs={"team_id": team.id}),
            {
                "season": self.summer.id,
                "name": "Cardinals Updated",
                "division": "13U",
                "external_source": "Roster",
                "external_identifier": "TEAM-1",
                "is_active": "on",
            },
        )
        self.assertRedirects(response, reverse("seasons:team-list"))
        team.refresh_from_db()
        self.assertEqual(team.name, "Cardinals Updated")
        self.assertEqual(team.season, self.spring)

    def test_cannot_create_team_from_inactive_season_shortcut(self):
        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
        self.login_staff()

        response = self.client.get(reverse("seasons:season-team-new", kwargs={"season_id": inactive.id}))

        self.assertEqual(response.status_code, 404)

    def test_staff_can_manage_membership_history_transfer_and_additional_membership(self):
        self.login_staff()
        create_response = self.client.post(
            reverse("seasons:membership-new"),
            {
                "player": self.player.id,
                "season_team": self.dodgers.id,
                "status": RosterStatus.ACTIVE,
                "jersey_number": "12",
                "is_primary": "on",
                "is_active": "on",
                "starts_on": "2026-04-01",
                "ends_on": "",
                "source": "manual",
                "source_identifier": "",
            },
        )
        membership = PlayerRosterMembership.objects.get(player=self.player, season_team=self.dodgers)
        self.assertRedirects(create_response, reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
        self.assertTrue(membership.is_primary)

        response = self.client.post(
            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
            {
                "action": "additional",
                "season_team": self.expos.id,
                "transfer_date": "2026-05-01",
                "jersey_number": "8",
                "source": "manual",
                "source_identifier": "",
            },
        )
        self.assertRedirects(response, reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
        membership.refresh_from_db()
        additional = PlayerRosterMembership.objects.get(player=self.player, season_team=self.expos)
        self.assertTrue(membership.is_active)
        self.assertTrue(membership.is_primary)
        self.assertEqual(additional.status, RosterStatus.GUEST)
        self.assertFalse(additional.is_primary)

        response = self.client.post(
            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
            {
                "action": "transfer",
                "season_team": self.expos.id,
                "transfer_date": "2026-06-01",
                "jersey_number": "",
                "source": "manual",
                "source_identifier": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already has")

        additional.delete()
        response = self.client.post(
            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
            {
                "action": "transfer",
                "season_team": self.expos.id,
                "transfer_date": "2026-06-01",
                "jersey_number": "",
                "source": "manual",
                "source_identifier": "",
            },
        )
        self.assertRedirects(response, reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
        membership.refresh_from_db()
        transferred = PlayerRosterMembership.objects.get(player=self.player, season_team=self.expos)
        self.assertFalse(membership.is_active)
        self.assertEqual(membership.status, RosterStatus.TRANSFERRED)
        self.assertTrue(transferred.is_primary)

    def test_transfer_rejects_cross_season_destination_tampering(self):
        self.login_staff()
        membership = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)

        response = self.client.post(
            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
            {
                "action": "transfer",
                "season_team": self.mounties.id,
                "transfer_date": "2026-06-01",
                "source": "manual",
                "source_identifier": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        membership.refresh_from_db()
        self.assertTrue(membership.is_active)
        self.assertEqual(PlayerRosterMembership.objects.filter(player=self.player).count(), 1)

    def test_player_history_and_invalid_filter_ids_render(self):
        self.login_staff()
        create_membership(player=self.player, season_team=self.dodgers, is_primary=True)

        response = self.client.get(reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dodgers")

        response = self.client.get(reverse("seasons:membership-list") + "?season=bad&team=bad")
        self.assertEqual(response.status_code, 200)

    def test_membership_list_is_paginated_and_preserves_filters(self):
        self.login_staff()
        for index in range(55):
            player = Player.objects.create(first_name=f"Player{index}", last_name="Paged")
            create_membership(player=player, season_team=self.dodgers, is_primary=True)

        response = self.client.get(reverse("seasons:membership-list") + f"?season={self.spring.id}&active=yes")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page 1 of 2")
        self.assertContains(response, f"?season={self.spring.id}&amp;active=yes&amp;page=2")

    def test_staff_can_create_edit_end_coach_assignment_without_account_side_effects(self):
        original_password = self.coach.password
        self.login_staff()

        response = self.client.post(
            reverse("seasons:coach-assignment-new"),
            {
                "user": self.coach.id,
                "season_team": self.dodgers.id,
                "assignment_role": CoachAssignmentRole.HEAD_COACH,
                "is_primary": "on",
                "is_active": "on",
                "starts_on": "2026-04-01",
                "ends_on": "",
                "source": "manual",
                "source_identifier": "",
            },
        )
        assignment = CoachSeasonAssignment.objects.get(user=self.coach, season_team=self.dodgers)
        self.assertRedirects(response, reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))

        response = self.client.post(
            reverse("seasons:coach-assignment-edit", kwargs={"assignment_id": assignment.id}),
            {
                "user": self.regular.id,
                "season_team": self.mounties.id,
                "assignment_role": CoachAssignmentRole.EVALUATOR,
                "is_primary": "on",
                "is_active": "on",
                "starts_on": "2026-04-01",
                "ends_on": "",
                "source": "manual",
                "source_identifier": "",
            },
        )
        self.assertRedirects(response, reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))
        assignment.refresh_from_db()
        self.coach.refresh_from_db()
        profile = get_or_create_account_profile(self.coach)
        self.assertEqual(assignment.user, self.coach)
        self.assertEqual(assignment.season_team, self.dodgers)
        self.assertEqual(assignment.assignment_role, CoachAssignmentRole.EVALUATOR)
        self.assertEqual(profile.role, AccountRole.COACH)
        self.assertFalse(self.coach.is_staff)
        self.assertFalse(self.coach.is_superuser)
        self.assertEqual(self.coach.password, original_password)

        response = self.client.post(
            reverse("seasons:coach-assignment-end", kwargs={"assignment_id": assignment.id}),
            {"ends_on": "2026-08-01", "confirm": "on"},
        )
        self.assertRedirects(response, reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))
        assignment.refresh_from_db()
        self.assertFalse(assignment.is_active)
        self.assertFalse(assignment.is_primary)
        self.assertEqual(assignment.ends_on, date(2026, 8, 1))

    def test_non_coach_user_cannot_be_assigned_as_coach(self):
        self.login_staff()

        response = self.client.post(
            reverse("seasons:coach-assignment-new"),
            {
                "user": self.regular.id,
                "season_team": self.dodgers.id,
                "assignment_role": CoachAssignmentRole.HEAD_COACH,
                "is_primary": "on",
                "is_active": "on",
                "starts_on": "",
                "ends_on": "",
                "source": "manual",
                "source_identifier": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(CoachSeasonAssignment.objects.filter(user=self.regular).exists())

    def test_coach_history_requires_coach_profile(self):
        self.login_staff()

        response = self.client.get(reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("seasons:coach-history", kwargs={"user_id": self.regular.id}))
        self.assertEqual(response.status_code, 404)

    def test_submitted_evaluation_snapshot_survives_team_edit_and_player_transfer(self):
        setup = ensure_default_coach_assessment_setup()
        membership = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
        create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
            is_primary=True,
        )
        cycle = EvaluationCycle.objects.create(
            name="2026 Spring Evaluation",
            cycle_type="Coach Assessment",
            season=self.spring,
            coach_assessment_question_set=setup.question_set,
        )
        responses = {
            question: 4
            for question in setup.question_set.questions.filter(
                response_type=RESPONSE_TYPE_RATING_1_5,
                is_required=True,
                is_active=True,
            )
        }
        text_question = setup.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
        responses[text_question] = "Snapshot should not move."

        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=cycle,
            evaluator=self.coach,
            player_roster_membership=membership,
            responses=responses,
        )
        observation = submit_observation(result.observation, actor=self.coach)

        update_season_team(self.dodgers, name="Renamed Dodgers", division="Renamed 13U")
        transfer_player(player=self.player, from_membership=membership, to_season_team=self.expos, transfer_date=date(2026, 6, 1))
        observation.refresh_from_db()

        self.assertEqual(observation.season_name_snapshot, "2026 Spring")
        self.assertEqual(observation.player_team_name_snapshot, "Dodgers")
        self.assertEqual(observation.player_division_snapshot, "13U")
        self.assertEqual(observation.evaluator_team_name_snapshot, "Dodgers")

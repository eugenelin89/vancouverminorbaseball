from seasons.tests.helpers import (
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    AccountRole,
    CoachAssignmentRole,
    CoachSeasonAssignment,
    EvaluationCycle,
    Player,
    PlayerRosterMembership,
    RosterStatus,
    Season,
    SeasonTeam,
    TestCase,
    User,
    create_assignment,
    create_coach_assessment_observation,
    create_membership,
    create_season,
    date,
    ensure_default_coach_assessment_setup,
    get_or_create_account_profile,
    get_or_create_season_team,
    reverse,
    set_account_role,
    submit_observation,
    transfer_player,
    update_season_team,
)


class SeasonOperationsUITests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
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
        self.spring = create_season(
            key="2026-spring",
            name="2026 Spring",
            starts_on=date(2026, 4, 1),
            is_current=True,
        )
        self.summer = create_season(key="2026-summer", name="2026 Summer")
        self.dodgers, _ = get_or_create_season_team(
            season=self.spring, name="Dodgers", division="13U"
        )
        self.expos, _ = get_or_create_season_team(
            season=self.spring, name="Expos", division="13U"
        )
        self.mounties, _ = get_or_create_season_team(
            season=self.summer, name="Mounties", division="15U"
        )

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
        self.assertRedirects(
            response, reverse("seasons:season-detail", kwargs={"season_id": season.id})
        )

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
        self.assertRedirects(
            response, reverse("seasons:season-detail", kwargs={"season_id": season.id})
        )
        season.refresh_from_db()
        self.assertEqual(season.name, "2027 Spring Updated")

        self.client.post(
            reverse("seasons:season-set-current", kwargs={"season_id": season.id}),
            {"confirm": "on"},
        )
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

        response = self.client.get(
            reverse("seasons:season-team-new", kwargs={"season_id": inactive.id})
        )

        self.assertEqual(response.status_code, 404)

    def test_staff_can_manage_membership_history_transfer_and_additional_membership(
        self,
    ):
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
        membership = PlayerRosterMembership.objects.get(
            player=self.player, season_team=self.dodgers
        )
        self.assertRedirects(
            create_response,
            reverse("seasons:player-history", kwargs={"player_id": self.player.id}),
        )
        self.assertTrue(membership.is_primary)

        response = self.client.post(
            reverse(
                "seasons:membership-transfer", kwargs={"membership_id": membership.id}
            ),
            {
                "action": "additional",
                "season_team": self.expos.id,
                "transfer_date": "2026-05-01",
                "jersey_number": "8",
                "source": "manual",
                "source_identifier": "",
            },
        )
        self.assertRedirects(
            response,
            reverse("seasons:player-history", kwargs={"player_id": self.player.id}),
        )
        membership.refresh_from_db()
        additional = PlayerRosterMembership.objects.get(
            player=self.player, season_team=self.expos
        )
        self.assertTrue(membership.is_active)
        self.assertTrue(membership.is_primary)
        self.assertEqual(additional.status, RosterStatus.GUEST)
        self.assertFalse(additional.is_primary)

        response = self.client.post(
            reverse(
                "seasons:membership-transfer", kwargs={"membership_id": membership.id}
            ),
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
            reverse(
                "seasons:membership-transfer", kwargs={"membership_id": membership.id}
            ),
            {
                "action": "transfer",
                "season_team": self.expos.id,
                "transfer_date": "2026-06-01",
                "jersey_number": "",
                "source": "manual",
                "source_identifier": "",
            },
        )
        self.assertRedirects(
            response,
            reverse("seasons:player-history", kwargs={"player_id": self.player.id}),
        )
        membership.refresh_from_db()
        transferred = PlayerRosterMembership.objects.get(
            player=self.player, season_team=self.expos
        )
        self.assertFalse(membership.is_active)
        self.assertEqual(membership.status, RosterStatus.TRANSFERRED)
        self.assertTrue(transferred.is_primary)

    def test_transfer_rejects_cross_season_destination_tampering(self):
        self.login_staff()
        membership = create_membership(
            player=self.player, season_team=self.dodgers, is_primary=True
        )

        response = self.client.post(
            reverse(
                "seasons:membership-transfer", kwargs={"membership_id": membership.id}
            ),
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
        self.assertEqual(
            PlayerRosterMembership.objects.filter(player=self.player).count(), 1
        )

    def test_player_history_and_invalid_filter_ids_render(self):
        self.login_staff()
        create_membership(player=self.player, season_team=self.dodgers, is_primary=True)

        response = self.client.get(
            reverse("seasons:player-history", kwargs={"player_id": self.player.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dodgers")

        response = self.client.get(
            reverse("seasons:membership-list") + "?season=bad&team=bad"
        )
        self.assertEqual(response.status_code, 200)

    def test_membership_list_is_paginated_and_preserves_filters(self):
        self.login_staff()
        for index in range(55):
            player = Player.objects.create(
                first_name=f"Player{index}", last_name="Paged"
            )
            create_membership(player=player, season_team=self.dodgers, is_primary=True)

        response = self.client.get(
            reverse("seasons:membership-list") + f"?season={self.spring.id}&active=yes"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page 1 of 2")
        self.assertContains(response, 'data-responsive="cards"')
        self.assertContains(response, 'data-label="Team"')
        self.assertContains(
            response, f"?season={self.spring.id}&amp;active=yes&amp;page=2"
        )

    def test_staff_can_create_edit_end_coach_assignment_without_account_side_effects(
        self,
    ):
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
        assignment = CoachSeasonAssignment.objects.get(
            user=self.coach, season_team=self.dodgers
        )
        self.assertRedirects(
            response,
            reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}),
        )

        response = self.client.post(
            reverse(
                "seasons:coach-assignment-edit", kwargs={"assignment_id": assignment.id}
            ),
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
        self.assertRedirects(
            response,
            reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}),
        )
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
            reverse(
                "seasons:coach-assignment-end", kwargs={"assignment_id": assignment.id}
            ),
            {"ends_on": "2026-08-01", "confirm": "on"},
        )
        self.assertRedirects(
            response,
            reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}),
        )
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
        self.assertFalse(
            CoachSeasonAssignment.objects.filter(user=self.regular).exists()
        )

    def test_coach_history_requires_coach_profile(self):
        self.login_staff()

        response = self.client.get(
            reverse("seasons:coach-history", kwargs={"user_id": self.coach.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("seasons:coach-history", kwargs={"user_id": self.regular.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_submitted_evaluation_snapshot_survives_team_edit_and_player_transfer(self):
        setup = ensure_default_coach_assessment_setup()
        membership = create_membership(
            player=self.player, season_team=self.dodgers, is_primary=True
        )
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
        text_question = setup.question_set.questions.get(
            response_type=RESPONSE_TYPE_TEXT
        )
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
        transfer_player(
            player=self.player,
            from_membership=membership,
            to_season_team=self.expos,
            transfer_date=date(2026, 6, 1),
        )
        observation.refresh_from_db()

        self.assertEqual(observation.season_name_snapshot, "2026 Spring")
        self.assertEqual(observation.player_team_name_snapshot, "Dodgers")
        self.assertEqual(observation.player_division_snapshot, "13U")
        self.assertEqual(observation.evaluator_team_name_snapshot, "Dodgers")

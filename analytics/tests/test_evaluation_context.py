from analytics.tests.helpers import (
    RESPONSE_TYPE_RATING_1_5,
    AccountRole,
    EvaluationCycle,
    Player,
    TestCase,
    User,
    ValidationError,
    attach_player_to_season,
    create_assignment,
    create_coach_assessment_observation,
    create_season,
    ensure_default_coach_assessment_setup,
    set_account_role,
    submit_observation,
)


class SeasonalEvaluationContextTests(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(
            username="season-coach", password="testpass"
        )
        set_account_role(self.coach, AccountRole.COACH)
        self.player = Player.objects.create(
            first_name="Season", last_name="Player", division="13U", team_name="Reds"
        )
        self.season = create_season(
            key="2026-spring", name="2026 Spring", is_current=True
        )
        self.other_season = create_season(key="2027-spring", name="2027 Spring")
        self.membership = attach_player_to_season(
            self.player, self.season, team_name="Reds", division="13U"
        )
        self.setup_result = ensure_default_coach_assessment_setup()
        self.cycle = EvaluationCycle.objects.create(
            name="2026 Spring Evaluations",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
            season=self.season,
        )

    def rating_payload(self, value=4):
        return {
            question: value
            for question in self.setup_result.question_set.questions.filter(
                response_type=RESPONSE_TYPE_RATING_1_5
            )
        }

    def test_submitted_observation_stores_immutable_season_and_roster_snapshots(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses=self.rating_payload(),
        ).observation

        submitted = submit_observation(observation, actor=self.coach)
        self.membership.season_team.name = "Corrected Reds"
        self.membership.season_team.division = "14U"
        self.membership.season_team.save()
        self.player.team_name = "Live Team"
        self.player.division = "Live Division"
        self.player.save(update_fields=["team_name", "division", "updated_at"])
        submitted.refresh_from_db()

        self.assertEqual(submitted.season, self.season)
        self.assertEqual(submitted.player_roster_membership, self.membership)
        self.assertEqual(submitted.season_name_snapshot, "2026 Spring")
        self.assertEqual(submitted.season_key_snapshot, "2026-spring")
        self.assertEqual(submitted.player_team_name_snapshot, "Reds")
        self.assertEqual(submitted.player_division_snapshot, "13U")

    def test_coach_assignment_snapshot_is_stored_when_resolved(self):
        assignment = create_assignment(
            user=self.coach,
            season_team=self.membership.season_team,
            assignment_role="head_coach",
            is_primary=True,
        )

        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses=self.rating_payload(),
        ).observation
        submitted = submit_observation(observation, actor=self.coach)

        self.assertEqual(submitted.evaluator_coach_assignment, assignment)
        self.assertEqual(submitted.evaluator_team_name_snapshot, "Reds")
        self.assertEqual(submitted.evaluator_division_snapshot, "13U")
        self.assertEqual(submitted.evaluator_assignment_role_snapshot, "Head Coach")

    def test_cross_player_or_cross_season_membership_is_rejected(self):
        other_player = Player.objects.create(
            first_name="Other", last_name="Player", division="13U"
        )
        other_membership = attach_player_to_season(other_player, self.season)
        cross_season_membership = attach_player_to_season(
            self.player, self.other_season
        )

        with self.assertRaisesMessage(
            ValidationError, "does not belong to this player"
        ):
            create_coach_assessment_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                evaluator=self.coach,
                player_roster_membership=other_membership,
            )
        with self.assertRaisesMessage(
            ValidationError, "does not belong to this evaluation season"
        ):
            create_coach_assessment_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                evaluator=self.coach,
                player_roster_membership=cross_season_membership,
            )

    def test_ambiguous_multiple_memberships_without_primary_are_blocked(self):
        player = Player.objects.create(
            first_name="Multi", last_name="Member", division="13U"
        )
        attach_player_to_season(
            player, self.season, team_name="Reds", division="13U", is_primary=False
        )
        attach_player_to_season(
            player, self.season, team_name="Blues", division="13U", is_primary=False
        )

        with self.assertRaisesMessage(ValidationError, "multiple active memberships"):
            create_coach_assessment_observation(
                player=player, evaluation_cycle=self.cycle, evaluator=self.coach
            )

    def test_review_uses_snapshot_values_not_live_player_fields(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses=self.rating_payload(),
        ).observation
        submitted = submit_observation(observation, actor=self.coach)
        self.player.team_name = "Changed Live Team"
        self.player.division = "Changed Live Division"
        self.player.save(update_fields=["team_name", "division", "updated_at"])
        set_account_role(self.coach, AccountRole.COACH)

        from analytics.services.evaluation_review_service import (
            get_evaluation_review_detail,
        )

        detail = get_evaluation_review_detail(self.coach, submitted.id)

        self.assertEqual(detail.season_name, "2026 Spring")
        self.assertEqual(detail.player_team, "Reds")
        self.assertEqual(detail.player_division, "13U")

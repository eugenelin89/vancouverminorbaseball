from analytics.tests.helpers import (
    OBSERVATION_STATUS_DRAFT,
    OBSERVATION_STATUS_REOPENED,
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    Decimal,
    Draft,
    DraftAction,
    DraftActionType,
    DraftPlayer,
    DraftTeam,
    EvaluationCycle,
    Observation,
    ObservationQuestion,
    Player,
    TestCase,
    User,
    attach_player_to_season,
    create_coach_assessment_observation,
    create_season,
    ensure_default_coach_assessment_setup,
    get_draft_context_for_draft_player,
    get_draft_contexts_for_draft,
    submit_observation,
    timedelta,
    timezone,
)


class AnalyticsDraftContextServiceTests(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(username="coach", password="testpass")
        self.other_coach = User.objects.create_user(
            username="othercoach", password="testpass"
        )
        self.third_coach = User.objects.create_user(
            username="thirdcoach", password="testpass"
        )
        self.player = Player.objects.create(
            first_name="Eugene",
            last_name="Lin",
            birth_year=2012,
            division="13U",
            team_name="Expos",
        )
        self.season = create_season(
            key="2026-spring", name="2026 Spring", is_current=True
        )
        attach_player_to_season(self.player, self.season)
        self.setup_result = ensure_default_coach_assessment_setup()
        self.cycle = EvaluationCycle.objects.create(
            name="2026 13U Coach Assessment",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
            season=self.season,
        )
        self.draft = Draft.objects.create(
            name="2026 VCB 13U", year=2026, division="13U"
        )
        self.team = DraftTeam.objects.create(
            draft=self.draft, name="Expos Navy", display_order=1
        )
        DraftTeam.objects.create(draft=self.draft, name="Expos Gold", display_order=2)
        self.draft_player = DraftPlayer.objects.create(
            draft=self.draft,
            first_name="Eugene",
            last_name="Lin",
            full_name="Eugene Lin",
            extra_data={"Birth Year": "2012"},
        )

    def submitted_observation(self, evaluator, rating=4):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=evaluator,
            responses={
                question: rating
                for question in self.setup_result.question_set.questions.filter(
                    response_type=RESPONSE_TYPE_RATING_1_5
                )
            },
        )
        return submit_observation(result.observation, actor=evaluator)

    def test_draft_context_retrieves_submitted_observation_and_selection(self):
        expected_round_question = ObservationQuestion.objects.create(
            question_set=self.setup_result.question_set,
            key="expected_draft_round",
            prompt="Expected draft round",
            response_type=RESPONSE_TYPE_TEXT,
            metadata={"draft_context_field": "expected_draft_round"},
            display_order=100,
        )
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={
                **{
                    question: 4
                    for question in self.setup_result.question_set.questions.filter(
                        response_type=RESPONSE_TYPE_RATING_1_5
                    )
                },
                expected_round_question: "2",
            },
        ).observation
        submit_observation(observation, actor=self.coach)
        DraftAction.objects.create(
            draft=self.draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=self.draft_player,
            to_team=self.team,
            pick_number=3,
        )

        context = get_draft_context_for_draft_player(self.draft_player)

        self.assertTrue(context.is_matched)
        self.assertEqual(context.matched_player, self.player)
        self.assertEqual(context.pick_number, 3)
        self.assertEqual(context.selected_round, 2)
        self.assertEqual(context.selected_team, self.team)
        self.assertEqual(context.submitted_observation_count, 1)
        self.assertEqual(context.latest_observation.expected_draft_round, "2")
        self.assertEqual(context.average_rating, Decimal("4"))

    def test_draft_context_is_empty_when_no_submitted_observations_exist(self):
        context = get_draft_context_for_draft_player(self.draft_player)

        self.assertTrue(context.is_matched)
        self.assertEqual(context.submitted_observation_count, 0)
        self.assertIsNone(context.average_rating)

    def test_draft_context_excludes_draft_and_reopened_observations(self):
        self.submitted_observation(self.coach, rating=5)
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_coach,
            status=OBSERVATION_STATUS_DRAFT,
            responses={
                question: 1
                for question in self.setup_result.question_set.questions.filter(
                    response_type=RESPONSE_TYPE_RATING_1_5
                )
            },
        )
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.third_coach,
            status=OBSERVATION_STATUS_REOPENED,
            responses={
                question: 1
                for question in self.setup_result.question_set.questions.filter(
                    response_type=RESPONSE_TYPE_RATING_1_5
                )
            },
        )

        context = get_draft_context_for_draft_player(self.draft_player)

        self.assertEqual(context.submitted_observation_count, 1)
        self.assertEqual(context.latest_observation.evaluator_name, self.coach.username)

    def test_multiple_submitted_observations_are_ordered_newest_first(self):
        older = self.submitted_observation(self.coach, rating=3)
        newer = self.submitted_observation(self.other_coach, rating=5)
        Observation.objects.filter(pk=older.pk).update(
            submitted_at=timezone.now() - timedelta(days=2)
        )
        Observation.objects.filter(pk=newer.pk).update(
            submitted_at=timezone.now() - timedelta(hours=1)
        )

        context = get_draft_context_for_draft_player(self.draft_player)

        self.assertEqual(context.submitted_observation_count, 2)
        self.assertEqual(
            [summary.evaluator_name for summary in context.observations],
            [self.other_coach.username, self.coach.username],
        )
        self.assertEqual(context.average_rating, Decimal("4"))

    def test_draft_context_reports_unmatched_player(self):
        unmatched = DraftPlayer.objects.create(
            draft=self.draft,
            first_name="No",
            last_name="Match",
            full_name="No Match",
        )

        context = get_draft_context_for_draft_player(unmatched)

        self.assertFalse(context.is_matched)
        self.assertEqual(context.submitted_observation_count, 0)

    def test_ambiguous_player_match_does_not_select_observations(self):
        Player.objects.create(
            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
        )

        context = get_draft_contexts_for_draft(self.draft)[self.draft_player.id]

        self.assertFalse(context.is_matched)
        self.assertEqual(context.match_status, "ambiguous")
        self.assertEqual(context.submitted_observation_count, 0)

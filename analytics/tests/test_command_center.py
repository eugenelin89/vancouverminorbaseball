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
    PlayerImportBatch,
    PlayerImportStatus,
    TestCase,
    User,
    active_player_ids,
    attach_player_to_season,
    completion_metrics,
    create_coach_assessment_observation,
    create_season,
    draft_matching_metrics,
    ensure_default_coach_assessment_setup,
    get_command_center_context,
    import_metrics,
    observation_metrics,
    parse_player_search_filters,
    recent_submitted_observations,
    reverse,
    search_players,
    submit_observation,
    timedelta,
    timezone,
)


class AnalyticsCommandCenterServiceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        self.coach = User.objects.create_user(username="coach", password="testpass")
        self.other_coach = User.objects.create_user(
            username="othercoach", password="testpass"
        )
        self.player = Player.objects.create(
            first_name="Eugene",
            last_name="Lin",
            birth_year=2012,
            division="13U",
            team_name="Expos",
        )
        self.other_player = Player.objects.create(
            first_name="Alex",
            last_name="Chen",
            birth_year=2011,
            division="15U",
            team_name="Mounties",
        )
        self.season = create_season(
            key="2026-spring", name="2026 Spring", is_current=True
        )
        attach_player_to_season(self.player, self.season)
        attach_player_to_season(
            self.other_player, self.season, team_name="Mounties", division="15U"
        )
        self.setup_result = ensure_default_coach_assessment_setup()
        self.cycle = EvaluationCycle.objects.create(
            name="2026 13U Coach Assessment",
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

    def submit_assessment(self, evaluator=None, player=None, value=4):
        result = create_coach_assessment_observation(
            player=player or self.player,
            evaluation_cycle=self.cycle,
            evaluator=evaluator or self.coach,
            responses=self.rating_payload(value),
        )
        return submit_observation(result.observation, actor=evaluator or self.coach)

    def test_player_population_helpers_live_in_player_service(self):
        self.assertIn(self.player.id, active_player_ids(division="13U"))
        self.assertNotIn(self.other_player.id, active_player_ids(division="13U"))

        result = search_players(parse_player_search_filters({"q": "Eugene"}))

        self.assertEqual(result.players, [self.player])

    def test_completion_and_observation_metrics_respect_cycle_and_filters(self):
        self.submit_assessment(value=5)
        create_coach_assessment_observation(
            player=self.other_player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_coach,
            status=OBSERVATION_STATUS_DRAFT,
            responses=self.rating_payload(2),
        )

        completion = completion_metrics(cycle=self.cycle, division="13U")
        observations = observation_metrics(cycle=self.cycle, division="13U")

        self.assertEqual(completion.total_active_players, 1)
        self.assertEqual(completion.players_with_submitted_assessment, 1)
        self.assertEqual(completion.players_without_submitted_assessment, 0)
        self.assertEqual(completion.completion_rate, Decimal("100"))
        self.assertEqual(observations.submitted_count, 1)
        self.assertEqual(observations.draft_count, 0)
        self.assertEqual(observations.by_category_average[0].average, Decimal("5"))

    def test_metrics_exclude_draft_and_reopened_from_submitted_rating_summaries(self):
        self.submit_assessment(evaluator=self.coach, value=5)
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_coach,
            status=OBSERVATION_STATUS_REOPENED,
            responses=self.rating_payload(1),
        )

        observations = observation_metrics(cycle=self.cycle)

        averages = {row.label: row.average for row in observations.by_category_average}
        self.assertTrue(averages)
        self.assertEqual(set(averages.values()), {Decimal("5")})

    def test_coach_to_coach_spread_requires_two_evaluators(self):
        self.submit_assessment(evaluator=self.coach, value=2)
        self.submit_assessment(evaluator=self.other_coach, value=5)

        observations = observation_metrics(cycle=self.cycle)

        self.assertTrue(observations.variance_rows)
        self.assertEqual(observations.variance_rows[0].player, self.player)
        self.assertEqual(observations.variance_rows[0].spread, Decimal("3"))

    def test_import_summary_counts_statuses_and_rows(self):
        PlayerImportBatch.objects.create(
            source="member_list",
            original_filename="members.csv",
            status=PlayerImportStatus.NEEDS_REVIEW,
            rows_created=1,
            rows_updated=2,
            rows_skipped=3,
            rows_conflicted=4,
        )
        PlayerImportBatch.objects.create(
            source="member_list",
            original_filename="committed.csv",
            status=PlayerImportStatus.COMMITTED,
        )

        summary = import_metrics()

        self.assertEqual(summary.total_batches, 2)
        self.assertEqual(summary.needs_review_count, 1)
        self.assertEqual(summary.committed_count, 1)
        self.assertEqual(summary.rows_created, 1)
        self.assertEqual(summary.rows_conflicted, 4)
        self.assertEqual(len(summary.recent_batches), 2)

    def test_draft_matching_summary_uses_draft_context_and_detects_mismatch(self):
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
            responses={**self.rating_payload(4), expected_round_question: "1"},
        ).observation
        submit_observation(observation, actor=self.coach)
        draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
        team = DraftTeam.objects.create(draft=draft, name="Expos Navy", display_order=1)
        DraftTeam.objects.create(draft=draft, name="Expos Gold", display_order=2)
        draft_player = DraftPlayer.objects.create(
            draft=draft,
            first_name="Eugene",
            last_name="Lin",
            full_name="Eugene Lin",
            extra_data={"Birth Year": "2012"},
        )
        DraftPlayer.objects.create(
            draft=draft, first_name="No", last_name="Match", full_name="No Match"
        )
        DraftAction.objects.create(
            draft=draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=draft_player,
            to_team=team,
            pick_number=3,
        )

        summary = draft_matching_metrics(division="13U")

        self.assertEqual(summary.matched_player_count, 1)
        self.assertEqual(summary.drafted_player_count, 1)
        self.assertEqual(summary.no_context_player_count, 0)
        self.assertEqual(summary.unmatched_draft_player_count, 1)
        self.assertEqual(summary.expected_round_mismatch_count, 1)
        self.assertEqual(summary.mismatches[0].player, self.player)

    def test_recent_observations_are_ordered_and_limited(self):
        older = self.submit_assessment(evaluator=self.coach, value=3)
        newer = self.submit_assessment(evaluator=self.other_coach, value=4)
        Observation.objects.filter(pk=older.pk).update(
            submitted_at=timezone.now() - timedelta(days=1)
        )
        Observation.objects.filter(pk=newer.pk).update(submitted_at=timezone.now())

        observations = recent_submitted_observations(cycle=self.cycle, limit=1)

        self.assertEqual(observations, [Observation.objects.get(pk=newer.pk)])

    def test_reporting_context_is_grouped_and_template_ready(self):
        self.submit_assessment()

        context = get_command_center_context(cycle_id=self.cycle.id, division="13U")

        self.assertTrue(context.summary_cards)
        self.assertEqual(context.completion_summary.active_cycle, self.cycle)
        self.assertTrue(context.observation_summary.by_category_average)
        self.assertIsNotNone(context.import_summary)
        self.assertIsNotNone(context.draft_summary)
        self.assertTrue(context.recent_observations)
        self.assertTrue(context.navigation_links)
        self.assertFalse(hasattr(context, "total_active_players"))


class AnalyticsCommandCenterViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        self.coach = User.objects.create_user(username="coach", password="testpass")
        self.player = Player.objects.create(
            first_name="Eugene", last_name="Lin", division="13U", team_name="Expos"
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

    def rating_payload(self, value=4):
        return {
            question: value
            for question in self.setup_result.question_set.questions.filter(
                response_type=RESPONSE_TYPE_RATING_1_5
            )
        }

    def test_command_center_requires_staff(self):
        url = reverse("analytics:command-center")
        self.assertEqual(self.client.get(url).status_code, 302)

        self.client.force_login(self.coach)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_staff_can_render_command_center_links_and_empty_states(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("analytics:command-center"), {"cycle": "not-a-number"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Analytics Command Center")
        self.assertContains(response, reverse("analytics:import-list"))
        self.assertContains(response, reverse("analytics:player-search"))
        self.assertContains(response, reverse("analytics:player-compare"))
        self.assertContains(response, reverse("analytics:assessment-list"))
        self.assertContains(response, reverse("analytics:observation-review-list"))
        self.assertContains(response, "No player imports yet.")
        self.assertContains(response, "No submitted observations yet.")

    def test_command_center_renders_populated_summaries_and_filters(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses=self.rating_payload(4),
        ).observation
        submit_observation(observation, actor=self.coach)
        PlayerImportBatch.objects.create(
            source="member_list",
            original_filename="members.csv",
            status=PlayerImportStatus.COMMITTED,
        )
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("analytics:command-center"), {"division": "13U", "team": "Expos"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Submitted assessments")
        self.assertContains(response, "Completion rate")
        self.assertContains(response, "Average Score By Category")
        self.assertContains(response, "members.csv")
        self.assertContains(response, self.player.display_name)
        self.assertEqual(response.context["filters"]["division"], "13U")
        self.assertEqual(response.context["filters"]["team"], "Expos")

    def test_phase_seven_regression_existing_pages_render(self):
        self.client.force_login(self.staff)

        self.assertEqual(
            self.client.get(reverse("analytics:player-search")).status_code, 200
        )
        self.assertEqual(
            self.client.get(
                reverse(
                    "analytics:player-profile", kwargs={"player_id": self.player.id}
                )
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("analytics:player-compare")).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("analytics:import-list")).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("analytics:assessment-list")).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("analytics:observation-review-list")).status_code,
            200,
        )

from analytics.tests.helpers import (
    DRAFT_STATUS_AVAILABLE,
    DRAFT_STATUS_DRAFTED,
    DRAFT_STATUS_NO_CONTEXT,
    EVALUATION_HAS_ANY,
    EVALUATION_HAS_SUBMITTED,
    EVALUATION_NO_SUBMITTED,
    EVALUATION_NOT_STARTED,
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
    Player,
    PlayerSourceRow,
    TestCase,
    User,
    assign_tag,
    attach_player_to_season,
    create_coach_assessment_observation,
    create_season,
    ensure_default_coach_assessment_setup,
    get_player_comparison,
    get_player_score_summary,
    get_player_timeline,
    parse_player_search_filters,
    reverse,
    search_players,
    submit_observation,
)


class PlayerExperienceServiceTests(TestCase):
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
        self.no_context_player = Player.objects.create(
            first_name="No", last_name="Context", division="13U"
        )
        self.season = create_season(
            key="2026-spring", name="2026 Spring", is_current=True
        )
        attach_player_to_season(self.player, self.season)
        attach_player_to_season(self.other_player, self.season)
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

    def test_timeline_includes_submitted_assessment_import_and_draft_context(self):
        observation = self.submit_assessment()
        PlayerSourceRow.objects.create(
            player=self.player,
            source="vcb_member_list_csv",
            source_filename="members.csv",
            row_number=2,
            original_row={"private": "do not render"},
        )
        DraftAction.objects.create(
            draft=self.draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=self.draft_player,
            to_team=self.team,
            pick_number=1,
        )

        timeline = get_player_timeline(self.player)

        self.assertEqual(timeline.coach_assessment_count, 1)
        self.assertEqual(timeline.import_count, 1)
        self.assertEqual(timeline.draft_context_count, 1)
        self.assertEqual(
            {item.kind for item in timeline.items},
            {"coach_assessment", "import", "draft_context"},
        )
        self.assertTrue(
            any(str(observation.id) in item.url for item in timeline.items if item.url)
        )

    def test_timeline_excludes_draft_and_reopened_observations(self):
        submitted = self.submit_assessment(evaluator=self.coach, value=5)
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_coach,
            status=OBSERVATION_STATUS_DRAFT,
            responses=self.rating_payload(1),
        )
        third_coach = User.objects.create_user(
            username="thirdcoach", password="testpass"
        )
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=third_coach,
            status=OBSERVATION_STATUS_REOPENED,
            responses=self.rating_payload(1),
        )

        timeline = get_player_timeline(self.player)

        self.assertEqual(timeline.coach_assessment_count, 1)
        self.assertEqual(
            timeline.items[0].metadata.get("evaluator"), submitted.evaluator.username
        )

    def test_timeline_handles_no_entries(self):
        timeline = get_player_timeline(self.other_player)

        self.assertEqual(timeline.items, [])
        self.assertEqual(timeline.coach_assessment_count, 0)

    def test_comparison_computes_scores_notes_tags_and_draft_context(self):
        text_question = self.setup_result.question_set.questions.get(
            response_type=RESPONSE_TYPE_TEXT
        )
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={**self.rating_payload(4), text_question: "Strong arm."},
        ).observation
        submit_observation(observation, actor=self.coach)
        assign_tag(self.player, "Strong Prospect")
        DraftAction.objects.create(
            draft=self.draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=self.draft_player,
            to_team=self.team,
            pick_number=1,
        )

        summary = get_player_score_summary(self.player)
        comparison = get_player_comparison([self.other_player, self.player])

        self.assertEqual(summary.average_rating, Decimal("4"))
        self.assertEqual(summary.evaluator_count, 1)
        self.assertIn("Strong arm.", summary.notes)
        self.assertEqual([tag.name for tag in summary.tags], ["Strong Prospect"])
        self.assertEqual(len(summary.draft_contexts), 1)
        self.assertEqual(
            [player.id for player in comparison.players],
            [self.other_player.id, self.player.id],
        )
        self.assertIn("Throw", comparison.category_names)

    def test_search_filters_by_name_team_division_birth_year_tag_source_and_evaluation(
        self,
    ):
        assign_tag(self.player, "Future AAA")
        PlayerSourceRow.objects.create(
            player=self.player,
            source="vcb_member_list_csv",
            source_filename="members.csv",
        )
        self.submit_assessment()

        expectations = [
            ({"q": "Eug"}, [self.player]),
            ({"team": "Expos"}, [self.player]),
            ({"division": "13U"}, [self.no_context_player, self.player]),
            ({"birth_year": "2012"}, [self.player]),
            ({"tag": "future-aaa"}, [self.player]),
            ({"source": "vcb_member_list_csv"}, [self.player]),
            ({"evaluation": EVALUATION_HAS_SUBMITTED}, [self.player]),
            (
                {"evaluation": EVALUATION_NO_SUBMITTED},
                [self.other_player, self.no_context_player],
            ),
            ({"evaluation": EVALUATION_HAS_ANY}, [self.player]),
            (
                {"evaluation": EVALUATION_NOT_STARTED},
                [self.other_player, self.no_context_player],
            ),
        ]
        for params, expected_players in expectations:
            with self.subTest(params=params):
                result = search_players(parse_player_search_filters(params))
                self.assertEqual(
                    [player.id for player in result.players],
                    [player.id for player in expected_players],
                )

    def test_search_filters_by_draft_status_and_ignores_invalid_birth_year(self):
        available_player = Player.objects.create(
            first_name="Ava", last_name="Lopez", birth_year=2012, division="13U"
        )
        DraftPlayer.objects.create(
            draft=self.draft,
            first_name="Ava",
            last_name="Lopez",
            full_name="Ava Lopez",
            extra_data={"Birth Year": "2012"},
        )
        DraftAction.objects.create(
            draft=self.draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=self.draft_player,
            to_team=self.team,
            pick_number=1,
        )

        drafted = search_players(
            parse_player_search_filters({"draft_status": DRAFT_STATUS_DRAFTED})
        )
        available = search_players(
            parse_player_search_filters({"draft_status": DRAFT_STATUS_AVAILABLE})
        )
        no_context = search_players(
            parse_player_search_filters({"draft_status": DRAFT_STATUS_NO_CONTEXT})
        )
        invalid = search_players(
            parse_player_search_filters({"birth_year": "not-a-year"})
        )

        self.assertIn(self.player, drafted.players)
        self.assertIn(available_player, available.players)
        self.assertIn(self.no_context_player, no_context.players)
        self.assertIn(self.player, invalid.players)


class PlayerExperienceViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        self.coach = User.objects.create_user(username="coach", password="testpass")
        self.player = Player.objects.create(
            first_name="Eugene",
            last_name="Lin",
            birth_year=2012,
            division="13U",
            team_name="Expos",
            bats="R",
            throws="R",
            primary_positions="SS",
        )
        self.other_player = Player.objects.create(
            first_name="Alex", last_name="Chen", division="15U", team_name="Mounties"
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

    def test_player_experience_views_require_staff(self):
        profile_url = reverse(
            "analytics:player-profile", kwargs={"player_id": self.player.id}
        )
        for url in [
            reverse("analytics:player-search"),
            profile_url,
            reverse("analytics:player-compare"),
        ]:
            with self.subTest(url=url):
                self.client.logout()
                self.assertEqual(self.client.get(url).status_code, 302)
                self.client.force_login(self.coach)
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_player_search_view_renders_filters_and_results(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:player-search"), {"q": "Eugene"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Player Search")
        self.assertContains(response, self.player.display_name)
        self.assertNotContains(response, self.other_player.display_name)

    def test_player_profile_renders_phase_six_context_without_raw_import_json(self):
        assign_tag(self.player, "Strong Prospect")
        PlayerSourceRow.objects.create(
            player=self.player,
            source="vcb_member_list_csv",
            source_filename="members.csv",
            row_number=2,
            original_row={"private": "secret value"},
        )
        text_question = self.setup_result.question_set.questions.get(
            response_type=RESPONSE_TYPE_TEXT
        )
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={**self.rating_payload(4), text_question: "Good teammate."},
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
        DraftAction.objects.create(
            draft=draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=draft_player,
            to_team=team,
            pick_number=1,
        )
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("analytics:player-profile", kwargs={"player_id": self.player.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Strong Prospect")
        self.assertContains(response, "vcb_member_list_csv")
        self.assertContains(response, "Good teammate.")
        self.assertContains(response, "Draft Context")
        self.assertContains(response, "Timeline")
        self.assertNotContains(response, "secret value")

    def test_player_profile_empty_states(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse(
                "analytics:player-profile", kwargs={"player_id": self.other_player.id}
            )
        )

        self.assertContains(response, "No tags assigned.")
        self.assertContains(response, "No imported source rows.")
        self.assertContains(response, "No draft context found.")
        self.assertContains(response, "No submitted coach assessments yet.")
        self.assertContains(response, "No timeline entries yet.")

    def test_player_compare_handles_empty_selected_and_selected_players(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses=self.rating_payload(4),
        ).observation
        submit_observation(observation, actor=self.coach)
        self.client.force_login(self.staff)

        empty_response = self.client.get(reverse("analytics:player-compare"))
        selected_response = self.client.get(
            reverse("analytics:player-compare"),
            {"players": [str(self.player.id), str(self.other_player.id)]},
        )

        self.assertContains(empty_response, "Select players to compare.")
        self.assertContains(selected_response, self.player.display_name)
        self.assertContains(selected_response, "4.0")
        self.assertContains(selected_response, "No submitted assessments")

    def test_player_compare_caps_selected_players(self):
        extra_players = [
            Player.objects.create(
                first_name=f"Player{i}", last_name="Test", division="13U"
            )
            for i in range(10)
        ]
        ids = [str(player.id) for player in extra_players]
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("analytics:player-compare"), {"players": ids}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["selected_players"]), 6)

    def test_phase_six_regression_existing_pages_render(self):
        self.client.force_login(self.staff)

        self.assertEqual(
            self.client.get(reverse("analytics:assessment-list")).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("analytics:observation-review-list")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("analytics:import-list")).status_code, 200
        )

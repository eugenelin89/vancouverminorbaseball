from analytics.tests.helpers import (
    OBSERVATION_STATUS_DRAFT,
    OBSERVATION_STATUS_REOPENED,
    OBSERVATION_STATUS_SUBMITTED,
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    CoachAssessmentForm,
    Decimal,
    EvaluationCycle,
    Observation,
    ObservationResponse,
    Player,
    TestCase,
    User,
    attach_player_to_season,
    create_coach_assessment_observation,
    create_season,
    ensure_default_coach_assessment_setup,
    get_player_score_summary,
    observation_metrics,
    patch,
    reverse,
    submit_observation,
)


class CoachAssessmentWorkflowTests(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(username="coach", password="testpass")
        self.other_coach = User.objects.create_user(
            username="othercoach", password="testpass"
        )
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        self.player = Player.objects.create(
            first_name="Eugene", last_name="Lin", division="13U", team_name="Expos"
        )
        self.other_player = Player.objects.create(
            first_name="Alex", last_name="Chen", division="13U", team_name="Expos"
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

    def response_payload(self, include_required=True):
        data = {}
        for question in self.setup_result.question_set.questions.filter(is_active=True):
            field_name = f"question_{question.id}"
            if question.response_type == RESPONSE_TYPE_RATING_1_5 and include_required:
                data[field_name] = "4"
            elif question.response_type == RESPONSE_TYPE_TEXT:
                data[field_name] = "Good teammate."
        return data

    def test_dynamic_form_uses_configured_questions(self):
        question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        question.prompt = "Edited dynamic question"
        question.save()

        form = CoachAssessmentForm(question_set=self.setup_result.question_set)

        self.assertIn(f"question_{question.id}", form.fields)
        self.assertEqual(
            form.fields[f"question_{question.id}"].label, "Edited dynamic question"
        )

    def test_dynamic_form_marks_optional_questions_not_required(self):
        optional_question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        optional_question.is_required = False
        optional_question.save(update_fields=["is_required", "updated_at"])
        required_question = (
            self.setup_result.question_set.questions.filter(
                response_type=RESPONSE_TYPE_RATING_1_5,
                is_required=True,
            )
            .exclude(id=optional_question.id)
            .first()
        )

        form = CoachAssessmentForm(
            question_set=self.setup_result.question_set, require_required=True
        )

        self.assertFalse(form.fields[f"question_{optional_question.id}"].required)
        self.assertTrue(form.fields[f"question_{required_question.id}"].required)
        self.assertEqual(
            form.fields[f"question_{optional_question.id}"].label,
            f"{optional_question.prompt} (Optional)",
        )

    def test_assessment_list_requires_login_and_lists_players(self):
        response = self.client.get(reverse("analytics:assessment-list"))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.coach)
        response = self.client.get(reverse("analytics:assessment-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)
        self.assertContains(response, "Not started")

    def test_invalid_cycle_parameter_does_not_crash_assessment_list(self):
        self.client.force_login(self.coach)

        response = self.client.get(
            reverse("analytics:assessment-list"), {"cycle": "not-a-number"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)

    def test_coach_can_open_dynamic_assessment_form_for_any_active_player(self):
        prompt = self.setup_result.question_set.questions.first().prompt
        self.client.force_login(self.coach)

        response = self.client.get(
            reverse(
                "analytics:assessment-player",
                kwargs={"player_id": self.other_player.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.other_player.display_name)
        self.assertContains(response, prompt)

    def test_invalid_cycle_parameter_does_not_crash_assessment_form(self):
        self.client.force_login(self.coach)

        response = self.client.get(
            reverse(
                "analytics:assessment-player", kwargs={"player_id": self.player.id}
            ),
            {"cycle": "bad"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)

    def test_assessment_edit_uses_submit_permission_helper(self):
        self.client.force_login(self.coach)

        with patch("analytics.views.can_submit_coach_assessment", return_value=False):
            response = self.client.get(
                reverse(
                    "analytics:assessment-player", kwargs={"player_id": self.player.id}
                )
            )

        self.assertEqual(response.status_code, 403)

    def test_coach_can_save_partial_draft(self):
        question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        self.client.force_login(self.coach)

        response = self.client.post(
            reverse(
                "analytics:assessment-player", kwargs={"player_id": self.player.id}
            ),
            {"action": "save_draft", f"question_{question.id}": "3"},
        )

        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
        self.assertEqual(
            observation.responses.get(question=question).numeric_value, Decimal("3.00")
        )

    def test_submit_missing_required_responses_is_rejected(self):
        self.client.force_login(self.coach)

        response = self.client.post(
            reverse(
                "analytics:assessment-player", kwargs={"player_id": self.player.id}
            ),
            {"action": "submit"},
        )

        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
        self.assertContains(response, "This field is required")

    def test_coach_can_submit_complete_assessment(self):
        self.client.force_login(self.coach)
        data = {"action": "submit"}
        data.update(self.response_payload())

        response = self.client.post(
            reverse(
                "analytics:assessment-player", kwargs={"player_id": self.player.id}
            ),
            data,
        )

        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
        self.assertIsNotNone(observation.submitted_at)
        self.assertEqual(observation.responses.count(), len(self.response_payload()))

    def test_coach_can_submit_with_optional_question_blank(self):
        optional_question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        optional_question.is_required = False
        optional_question.save(update_fields=["is_required", "updated_at"])
        self.client.force_login(self.coach)
        data = {"action": "submit"}
        data.update(self.response_payload())
        data[f"question_{optional_question.id}"] = ""

        response = self.client.post(
            reverse(
                "analytics:assessment-player", kwargs={"player_id": self.player.id}
            ),
            data,
        )

        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
        score_summary = get_player_score_summary(self.player)
        metrics = observation_metrics(cycle=self.cycle)
        expected_rating_count = (
            self.setup_result.question_set.questions.filter(
                response_type=RESPONSE_TYPE_RATING_1_5
            ).count()
            - 1
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
        self.assertFalse(
            ObservationResponse.objects.filter(
                observation=observation, question=optional_question
            ).exists()
        )
        self.assertEqual(score_summary.rating_count, expected_rating_count)
        self.assertEqual(
            sum(row.count for row in metrics.by_category_average),
            expected_rating_count,
        )

    def test_clearing_optional_draft_answer_removes_response(self):
        optional_question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        optional_question.is_required = False
        optional_question.save(update_fields=["is_required", "updated_at"])
        self.client.force_login(self.coach)

        self.client.post(
            reverse(
                "analytics:assessment-player", kwargs={"player_id": self.player.id}
            ),
            {"action": "save_draft", f"question_{optional_question.id}": "3"},
        )
        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
        self.client.post(
            reverse(
                "analytics:assessment-edit", kwargs={"observation_id": observation.id}
            ),
            {"action": "save_draft", f"question_{optional_question.id}": ""},
        )

        self.assertFalse(
            ObservationResponse.objects.filter(
                observation=observation, question=optional_question
            ).exists()
        )

    def test_assessment_detail_shows_unanswered_optional_question(self):
        optional_question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        optional_question.is_required = False
        optional_question.save(update_fields=["is_required", "updated_at"])
        self.client.force_login(self.coach)
        data = {"action": "submit"}
        data.update(self.response_payload())
        data[f"question_{optional_question.id}"] = ""
        self.client.post(
            reverse(
                "analytics:assessment-player", kwargs={"player_id": self.player.id}
            ),
            data,
        )
        observation = Observation.objects.get(player=self.player, evaluator=self.coach)

        response = self.client.get(
            reverse(
                "analytics:assessment-detail",
                kwargs={"observation_id": observation.id},
            )
        )

        self.assertContains(response, optional_question.prompt)
        self.assertContains(response, "Optional")
        self.assertContains(response, "Not answered")

    def test_submitted_assessment_redirects_instead_of_creating_duplicate(self):
        self.client.force_login(self.coach)
        data = {"action": "submit"}
        data.update(self.response_payload())
        self.client.post(
            reverse(
                "analytics:assessment-player", kwargs={"player_id": self.player.id}
            ),
            data,
        )
        observation = Observation.objects.get(player=self.player, evaluator=self.coach)

        response = self.client.get(
            reverse("analytics:assessment-player", kwargs={"player_id": self.player.id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse(
                "analytics:assessment-detail", kwargs={"observation_id": observation.id}
            ),
        )
        self.assertEqual(
            Observation.objects.filter(
                player=self.player, evaluator=self.coach
            ).count(),
            1,
        )

    def test_multiple_evaluators_can_submit_for_same_player(self):
        for user in [self.coach, self.other_coach]:
            self.client.force_login(user)
            data = {"action": "submit"}
            data.update(self.response_payload())
            self.client.post(
                reverse(
                    "analytics:assessment-player", kwargs={"player_id": self.player.id}
                ),
                data,
            )

        self.assertEqual(
            Observation.objects.filter(
                player=self.player, status=OBSERVATION_STATUS_SUBMITTED
            ).count(),
            2,
        )

    def test_coach_cannot_view_or_edit_other_evaluator_observation(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_coach,
            responses={
                question: 4
                for question in self.setup_result.question_set.questions.filter(
                    response_type=RESPONSE_TYPE_RATING_1_5
                )
            },
        )
        submit_observation(result.observation)
        self.client.force_login(self.coach)

        detail_response = self.client.get(
            reverse(
                "analytics:assessment-detail",
                kwargs={"observation_id": result.observation.id},
            )
        )
        edit_response = self.client.get(
            reverse(
                "analytics:assessment-edit",
                kwargs={"observation_id": result.observation.id},
            )
        )

        self.assertEqual(detail_response.status_code, 403)
        self.assertEqual(edit_response.status_code, 403)

    def test_coach_detail_context_controls_edit_and_back_link(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
        )
        self.client.force_login(self.coach)

        response = self.client.get(
            reverse(
                "analytics:assessment-detail",
                kwargs={"observation_id": result.observation.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "analytics:assessment-edit",
                kwargs={"observation_id": result.observation.id},
            ),
        )
        self.assertContains(response, f'href="{reverse("analytics:assessment-list")}"')

    def test_staff_review_requires_staff_and_displays_observation(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={
                question: 4
                for question in self.setup_result.question_set.questions.filter(
                    response_type=RESPONSE_TYPE_RATING_1_5
                )
            },
        )
        submit_observation(result.observation)

        self.client.force_login(self.coach)
        self.assertEqual(
            self.client.get(reverse("analytics:observation-review-list")).status_code,
            403,
        )

        self.client.force_login(self.staff)
        list_response = self.client.get(reverse("analytics:observation-review-list"))
        detail_response = self.client.get(
            reverse(
                "analytics:observation-review-detail",
                kwargs={"observation_id": result.observation.id},
            )
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, self.player.display_name)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, result.observation.evaluator.username)

    def test_staff_review_search_uses_single_q_filter(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={
                question: 4
                for question in self.setup_result.question_set.questions.filter(
                    response_type=RESPONSE_TYPE_RATING_1_5
                )
            },
        )
        submit_observation(result.observation)
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("analytics:observation-review-list"), {"q": self.coach.username}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)

    def test_invalid_cycle_parameter_does_not_crash_staff_review_list(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("analytics:observation-review-list"), {"cycle": "bad"}
        )

        self.assertEqual(response.status_code, 200)

    def test_staff_review_detail_back_link_returns_to_review_list(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={
                question: 4
                for question in self.setup_result.question_set.questions.filter(
                    response_type=RESPONSE_TYPE_RATING_1_5
                )
            },
        )
        submit_observation(result.observation)
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse(
                "analytics:observation-review-detail",
                kwargs={"observation_id": result.observation.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, f'href="{reverse("analytics:observation-review-list")}"'
        )

    def test_staff_can_reopen_submitted_observation(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={
                question: 4
                for question in self.setup_result.question_set.questions.filter(
                    response_type=RESPONSE_TYPE_RATING_1_5
                )
            },
        )
        submit_observation(result.observation)
        original_perspective = result.observation.evaluation_perspective
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse(
                "analytics:observation-review-detail",
                kwargs={"observation_id": result.observation.id},
            ),
            {"action": "reopen"},
        )

        result.observation.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(result.observation.status, OBSERVATION_STATUS_REOPENED)
        self.assertEqual(
            result.observation.evaluation_perspective, original_perspective
        )

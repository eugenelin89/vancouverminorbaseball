from analytics.tests.helpers import (
    EVALUATION_PERSPECTIVE_PEER,
    EVALUATION_PERSPECTIVE_SELF,
    OBSERVATION_STATUS_DRAFT,
    OBSERVATION_STATUS_SUBMITTED,
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    ROLE_COACH,
    ROLE_GUEST_EVALUATOR,
    ROLE_PLAYER,
    AccountRole,
    Decimal,
    EvaluationCycle,
    Observation,
    Player,
    TestCase,
    User,
    UserPlayerRelationship,
    attach_player_to_season,
    create_coach_assessment_observation,
    create_season,
    ensure_default_coach_assessment_setup,
    link_user_to_player,
    reverse,
    set_account_role,
    submit_observation,
)


class EvaluationAccessSubmissionViewTests(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(
            username="coach-evaluator", password="testpass"
        )
        self.player_user = User.objects.create_user(
            username="player-evaluator", password="testpass"
        )
        self.guest = User.objects.create_user(
            username="guest-evaluator", password="testpass"
        )
        self.parent = User.objects.create_user(
            username="parent-user", password="testpass"
        )
        self.staff = User.objects.create_user(
            username="staff-evaluator", password="testpass", is_staff=True
        )
        set_account_role(self.coach, AccountRole.COACH)
        set_account_role(self.player_user, AccountRole.PLAYER)
        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
        set_account_role(self.parent, AccountRole.PARENT)
        set_account_role(self.staff, AccountRole.STAFF)
        self.self_player = Player.objects.create(
            first_name="Self", last_name="Player", division="13U", team_name="Expos"
        )
        self.target_player = Player.objects.create(
            first_name="Target", last_name="Player", division="13U", team_name="Expos"
        )
        self.inactive_player = Player.objects.create(
            first_name="Inactive", last_name="Player", division="13U", is_active=False
        )
        self.season = create_season(
            key="2026-spring", name="2026 Spring", is_current=True
        )
        attach_player_to_season(self.self_player, self.season)
        attach_player_to_season(self.target_player, self.season)
        link_user_to_player(
            self.player_user,
            self.self_player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )
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

    def service_response_payload(self):
        return {
            question: 4
            for question in self.setup_result.question_set.questions.filter(
                response_type=RESPONSE_TYPE_RATING_1_5,
                is_required=True,
                is_active=True,
            )
        }

    def test_evaluation_list_permissions(self):
        self.assertEqual(
            self.client.get(reverse("analytics:evaluation-list")).status_code, 302
        )
        for user in [self.player_user, self.coach, self.guest, self.staff]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("analytics:evaluation-list"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Evaluations")
                self.client.logout()

        self.client.force_login(self.parent)
        self.assertEqual(
            self.client.get(reverse("analytics:evaluation-list")).status_code, 403
        )

    def test_evaluation_list_allows_self_and_uses_evaluation_copy(self):
        self.client.force_login(self.player_user)

        response = self.client.get(
            reverse("analytics:evaluation-list"), {"q": "Player"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evaluate Player")
        self.assertContains(response, "My submission")
        self.assertContains(response, "Self Evaluation")
        self.assertContains(response, 'data-responsive="cards"')
        self.assertContains(response, 'data-label="Player"')
        self.assertContains(response, 'data-label="My submission"')
        self.assertContains(
            response,
            reverse(
                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
            ),
        )
        self.assertContains(
            response,
            reverse(
                "analytics:evaluation-player",
                kwargs={"player_id": self.target_player.id},
            ),
        )

    def test_player_can_open_evaluation_form_for_another_player(self):
        self.client.force_login(self.player_user)

        response = self.client.get(
            reverse(
                "analytics:evaluation-player",
                kwargs={"player_id": self.target_player.id},
            )
        )

        observation = Observation.objects.get(
            player=self.target_player, evaluator=self.player_user
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Evaluate {self.target_player.display_name}")
        self.assertContains(response, "Submit Evaluation")
        self.assertContains(response, "Peer Evaluation")
        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
        self.assertEqual(observation.evaluator_role_key, ROLE_PLAYER)
        self.assertEqual(
            observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER
        )

    def test_player_can_evaluate_self_but_not_inactive_player(self):
        self.client.force_login(self.player_user)

        self_response = self.client.get(
            reverse(
                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
            )
        )
        self_observation = Observation.objects.get(
            player=self.self_player, evaluator=self.player_user
        )
        self.assertEqual(self_response.status_code, 200)
        self.assertContains(self_response, "Self Evaluation")
        self.assertEqual(
            self_observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF
        )
        self.assertEqual(
            self.client.get(
                reverse(
                    "analytics:evaluation-player",
                    kwargs={"player_id": self.inactive_player.id},
                )
            ).status_code,
            404,
        )

    def test_player_can_save_draft_and_resume(self):
        question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        self.client.force_login(self.player_user)

        response = self.client.post(
            reverse(
                "analytics:evaluation-player",
                kwargs={"player_id": self.target_player.id},
            ),
            {"action": "save_draft", f"question_{question.id}": "3"},
        )
        second_response = self.client.get(
            reverse(
                "analytics:evaluation-player",
                kwargs={"player_id": self.target_player.id},
            )
        )

        observation = Observation.objects.get(
            player=self.target_player, evaluator=self.player_user
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse(
                "analytics:evaluation-player",
                kwargs={"player_id": self.target_player.id},
            ),
        )
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(
            Observation.objects.filter(
                player=self.target_player, evaluator=self.player_user
            ).count(),
            1,
        )
        self.assertEqual(
            observation.responses.get(question=question).numeric_value, Decimal("3.00")
        )

    def test_player_can_submit_complete_evaluation(self):
        self.client.force_login(self.player_user)
        data = {"action": "submit"}
        data.update(self.response_payload())

        response = self.client.post(
            reverse(
                "analytics:evaluation-player",
                kwargs={"player_id": self.target_player.id},
            ),
            data,
        )

        observation = Observation.objects.get(
            player=self.target_player, evaluator=self.player_user
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse(
                "analytics:assessment-detail", kwargs={"observation_id": observation.id}
            ),
        )
        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
        self.assertEqual(observation.evaluator_role_key, ROLE_PLAYER)
        self.assertEqual(
            observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER
        )

    def test_player_can_submit_with_optional_question_blank(self):
        optional_question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        optional_question.is_required = False
        optional_question.save(update_fields=["is_required", "updated_at"])
        self.client.force_login(self.player_user)
        data = {"action": "submit"}
        data.update(self.response_payload())
        data[f"question_{optional_question.id}"] = ""

        response = self.client.post(
            reverse(
                "analytics:evaluation-player",
                kwargs={"player_id": self.target_player.id},
            ),
            data,
        )

        observation = Observation.objects.get(
            player=self.target_player, evaluator=self.player_user
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
        self.assertFalse(
            observation.responses.filter(question=optional_question).exists()
        )

    def test_player_self_evaluation_draft_resumes_and_submitted_duplicate_redirects(
        self,
    ):
        self.client.force_login(self.player_user)
        first_response = self.client.get(
            reverse(
                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
            )
        )
        second_response = self.client.get(
            reverse(
                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
            )
        )
        observation = Observation.objects.get(
            player=self.self_player, evaluator=self.player_user
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(
            observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF
        )
        self.assertEqual(
            Observation.objects.filter(
                player=self.self_player, evaluator=self.player_user
            ).count(),
            1,
        )

        data = {"action": "submit"}
        data.update(self.response_payload())
        self.client.post(
            reverse(
                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
            ),
            data,
        )
        response = self.client.get(
            reverse(
                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
            )
        )
        observation.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse(
                "analytics:assessment-detail", kwargs={"observation_id": observation.id}
            ),
        )
        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)

    def test_submitted_evaluation_detail_is_private_to_evaluator_and_staff(self):
        result = create_coach_assessment_observation(
            player=self.target_player,
            evaluation_cycle=self.cycle,
            evaluator=self.player_user,
            responses=self.service_response_payload(),
        )
        observation = submit_observation(result.observation, actor=self.player_user)
        detail_url = reverse(
            "analytics:assessment-detail", kwargs={"observation_id": observation.id}
        )

        self.client.force_login(self.player_user)
        self.assertEqual(self.client.get(detail_url).status_code, 200)

        for user in [self.coach, self.guest]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                self.assertEqual(self.client.get(detail_url).status_code, 403)

        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(detail_url).status_code, 200)

    def test_player_cannot_view_another_evaluators_submitted_detail(self):
        other_player_user = User.objects.create_user(
            username="other-player-evaluator", password="testpass"
        )
        set_account_role(other_player_user, AccountRole.PLAYER)
        result = create_coach_assessment_observation(
            player=self.target_player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses=self.service_response_payload(),
        )
        observation = submit_observation(result.observation, actor=self.coach)

        self.client.force_login(other_player_user)
        response = self.client.get(
            reverse(
                "analytics:assessment-detail", kwargs={"observation_id": observation.id}
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_missing_required_responses_are_blocked(self):
        self.client.force_login(self.player_user)

        response = self.client.post(
            reverse(
                "analytics:evaluation-player",
                kwargs={"player_id": self.target_player.id},
            ),
            {"action": "submit"},
        )

        observation = Observation.objects.get(
            player=self.target_player, evaluator=self.player_user
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
        self.assertContains(response, "This field is required")

    def test_submitted_evaluation_cannot_be_duplicated(self):
        self.client.force_login(self.player_user)
        data = {"action": "submit"}
        data.update(self.response_payload())
        self.client.post(
            reverse(
                "analytics:evaluation-player",
                kwargs={"player_id": self.target_player.id},
            ),
            data,
        )
        observation = Observation.objects.get(
            player=self.target_player, evaluator=self.player_user
        )

        response = self.client.get(
            reverse(
                "analytics:evaluation-player",
                kwargs={"player_id": self.target_player.id},
            )
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
                player=self.target_player, evaluator=self.player_user
            ).count(),
            1,
        )

    def test_evaluation_list_submitted_copy_is_own_submission(self):
        result = create_coach_assessment_observation(
            player=self.target_player,
            evaluation_cycle=self.cycle,
            evaluator=self.player_user,
            responses=self.service_response_payload(),
        )
        submit_observation(result.observation, actor=self.player_user)
        self.client.force_login(self.player_user)

        response = self.client.get(
            reverse("analytics:evaluation-list"), {"q": "Target"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View My Submission")
        self.assertNotContains(response, ">View<")
        self.assertNotContains(response, "evaluations about me")

    def test_evaluation_list_uses_current_cycle_without_cycle_selector(self):
        self.client.force_login(self.player_user)

        response = self.client.get(
            reverse("analytics:evaluation-list"), {"cycle": "999"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cycle.name)
        self.assertNotContains(response, 'name="cycle"')

    def test_coach_and_guest_role_snapshots_continue_to_work(self):
        for user, expected_role in [
            (self.coach, ROLE_COACH),
            (self.guest, ROLE_GUEST_EVALUATOR),
        ]:
            with self.subTest(user=user.username):
                target = Player.objects.create(
                    first_name=user.username, last_name="Target", division="13U"
                )
                attach_player_to_season(target, self.season)
                self.client.force_login(user)
                response = self.client.get(
                    reverse(
                        "analytics:evaluation-player", kwargs={"player_id": target.id}
                    )
                )

                observation = Observation.objects.get(player=target, evaluator=user)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(observation.evaluator_role_key, expected_role)
                self.client.logout()

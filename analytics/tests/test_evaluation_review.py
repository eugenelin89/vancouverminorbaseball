from analytics.tests.helpers import (
    EVALUATION_PERSPECTIVE_COACH,
    EVALUATION_PERSPECTIVE_SELF,
    OBSERVATION_STATUS_REOPENED,
    OBSERVATION_STATUS_SUBMITTED,
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    ROLE_COACH,
    AccountRole,
    EvaluationCycle,
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
    timezone,
)


class EvaluationReviewViewTests(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(
            username="coach-review",
            password="testpass",
            first_name="Casey",
            last_name="Coach",
            email="coach-review@example.com",
        )
        self.second_coach = User.objects.create_user(
            username="second-coach-review",
            password="testpass",
            first_name="Sam",
            last_name="Coach",
            email="sam-coach@example.com",
        )
        self.player_user = User.objects.create_user(
            username="player-review", password="testpass"
        )
        self.parent = User.objects.create_user(
            username="parent-review", password="testpass"
        )
        self.guest = User.objects.create_user(
            username="guest-review", password="testpass"
        )
        self.staff = User.objects.create_user(
            username="staff-review-phase5", password="testpass", is_staff=True
        )
        self.role_staff = User.objects.create_user(
            username="role-staff-review", password="testpass"
        )
        self.role_admin = User.objects.create_user(
            username="role-admin-review", password="testpass"
        )
        set_account_role(self.coach, AccountRole.COACH)
        set_account_role(self.second_coach, AccountRole.COACH)
        set_account_role(self.player_user, AccountRole.PLAYER)
        set_account_role(self.parent, AccountRole.PARENT)
        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
        set_account_role(self.staff, AccountRole.STAFF)
        set_account_role(self.role_staff, AccountRole.STAFF)
        set_account_role(self.role_admin, AccountRole.ADMIN)
        self.player = Player.objects.create(
            first_name="Target", last_name="One", division="13U", team_name="Reds"
        )
        self.second_player = Player.objects.create(
            first_name="Target", last_name="Two", division="15U", team_name="Blues"
        )
        self.season = create_season(
            key="2026-spring", name="2026 Spring", is_current=True
        )
        self.second_season = create_season(key="2026-summer", name="2026 Summer")
        attach_player_to_season(
            self.player, self.season, team_name="Reds", division="13U"
        )
        attach_player_to_season(
            self.second_player, self.season, team_name="Reds", division="13U"
        )
        attach_player_to_season(
            self.second_player, self.second_season, team_name="Blues", division="15U"
        )
        self.setup_result = ensure_default_coach_assessment_setup()
        self.cycle = EvaluationCycle.objects.create(
            name="2026 13U Coach Assessment",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
            season=self.season,
        )
        self.second_cycle = EvaluationCycle.objects.create(
            name="2026 15U Coach Assessment",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
            season=self.second_season,
        )

    def service_response_payload(self, value=4, note="Good teammate."):
        payload = {
            question: value
            for question in self.setup_result.question_set.questions.filter(
                response_type=RESPONSE_TYPE_RATING_1_5,
                is_required=True,
                is_active=True,
            )
        }
        text_question = self.setup_result.question_set.questions.get(
            response_type=RESPONSE_TYPE_TEXT
        )
        payload[text_question] = note
        return payload

    def submitted_observation(
        self, player=None, evaluator=None, cycle=None, value=4, note="Good teammate."
    ):
        result = create_coach_assessment_observation(
            player=player or self.player,
            evaluation_cycle=cycle or self.cycle,
            evaluator=evaluator or self.coach,
            responses=self.service_response_payload(value=value, note=note),
        )
        return submit_observation(result.observation, actor=evaluator or self.coach)

    def test_coach_can_review_all_submitted_evaluations(self):
        first = self.submitted_observation(
            player=self.player, evaluator=self.coach, note="First submitted."
        )
        second = self.submitted_observation(
            player=self.second_player,
            evaluator=self.second_coach,
            cycle=self.second_cycle,
            note="Second submitted.",
        )
        link_user_to_player(
            self.player_user,
            self.player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )
        self_observation = self.submitted_observation(
            player=self.player, evaluator=self.player_user, note="Self submitted."
        )
        self.client.force_login(self.coach)

        response = self.client.get(reverse("analytics:evaluation-review-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)
        self.assertContains(response, self.second_player.display_name)
        self.assertContains(response, "Casey Coach")
        self.assertContains(response, "Sam Coach")
        self.assertContains(response, "Self Evaluation")
        self.assertContains(response, 'data-responsive="cards"')
        self.assertContains(response, 'data-label="Evaluator"')
        self.assertContains(response, 'data-label="Role"')
        self.assertContains(
            response,
            reverse(
                "analytics:evaluation-review-detail",
                kwargs={"observation_id": first.id},
            ),
        )
        self.assertContains(
            response,
            reverse(
                "analytics:evaluation-review-detail",
                kwargs={"observation_id": second.id},
            ),
        )
        self.assertContains(
            response,
            reverse(
                "analytics:evaluation-review-detail",
                kwargs={"observation_id": self_observation.id},
            ),
        )
        self.assertNotContains(response, self.coach.email)

    def test_review_detail_shows_unanswered_optional_questions(self):
        optional_question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        optional_question.is_required = False
        optional_question.save(update_fields=["is_required", "updated_at"])
        observation = self.submitted_observation(note="Required answers only.")
        self.client.force_login(self.coach)

        response = self.client.get(
            reverse(
                "analytics:evaluation-review-detail",
                kwargs={"observation_id": observation.id},
            )
        )

        self.assertContains(response, optional_question.prompt)
        self.assertContains(response, "Optional")
        self.assertContains(response, "Not answered")

    def test_coach_review_access_rules(self):
        self.submitted_observation()
        for user in [self.player_user, self.parent, self.guest]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("analytics:evaluation-review-list"))
                self.assertEqual(response.status_code, 403)
                self.client.logout()

        for user in [self.coach, self.staff, self.role_staff, self.role_admin]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("analytics:evaluation-review-list"))
                self.assertEqual(response.status_code, 200)
                self.client.logout()

    def test_coach_role_does_not_grant_account_operations(self):
        self.client.force_login(self.coach)

        self.assertEqual(
            self.client.get(reverse("accounts:operations-dashboard")).status_code, 403
        )

    def test_coach_review_filters_individually_and_in_combination(self):
        first = self.submitted_observation(
            player=self.player, evaluator=self.coach, note="Reds note."
        )
        second = self.submitted_observation(
            player=self.second_player,
            evaluator=self.second_coach,
            cycle=self.second_cycle,
            note="Blues note.",
        )
        link_user_to_player(
            self.player_user,
            self.player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )
        self_observation = self.submitted_observation(
            player=self.player, evaluator=self.player_user, note="Self note."
        )
        today = timezone.localdate().isoformat()
        self.client.force_login(self.coach)

        cases = [
            ({"q": "One"}, first, second),
            ({"player": str(self.player.id)}, first, second),
            ({"evaluator": str(self.coach.id)}, first, second),
            ({"evaluator": "second-coach"}, second, first),
            ({"evaluator_role": ROLE_COACH}, first, None),
            ({"perspective": EVALUATION_PERSPECTIVE_SELF}, self_observation, first),
            ({"perspective": EVALUATION_PERSPECTIVE_COACH}, first, self_observation),
            ({"team": "Reds"}, first, second),
            ({"division": "15U"}, second, first),
            ({"cycle": str(self.second_cycle.id)}, second, first),
            ({"submitted_from": today, "submitted_to": today}, first, None),
            (
                {"q": "Target", "team": "Blues", "cycle": str(self.second_cycle.id)},
                second,
                first,
            ),
        ]
        for params, included, excluded in cases:
            with self.subTest(params=params):
                response = self.client.get(
                    reverse("analytics:evaluation-review-list"), params
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    reverse(
                        "analytics:evaluation-review-detail",
                        kwargs={"observation_id": included.id},
                    ),
                )
                if excluded:
                    self.assertNotContains(
                        response,
                        reverse(
                            "analytics:evaluation-review-detail",
                            kwargs={"observation_id": excluded.id},
                        ),
                    )

    def test_coach_review_excludes_draft_and_reopened_observations(self):
        submitted = self.submitted_observation(player=self.player, evaluator=self.coach)
        draft = create_coach_assessment_observation(
            player=self.second_player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses=self.service_response_payload(),
        ).observation
        reopened = create_coach_assessment_observation(
            player=self.second_player,
            evaluation_cycle=self.second_cycle,
            evaluator=self.second_coach,
            responses=self.service_response_payload(),
        ).observation
        reopened.status = OBSERVATION_STATUS_REOPENED
        reopened.save(update_fields=["status", "updated_at"])
        self.client.force_login(self.coach)

        list_response = self.client.get(reverse("analytics:evaluation-review-list"))
        draft_detail = self.client.get(
            reverse(
                "analytics:evaluation-review-detail",
                kwargs={"observation_id": draft.id},
            )
        )
        reopened_detail = self.client.get(
            reverse(
                "analytics:evaluation-review-detail",
                kwargs={"observation_id": reopened.id},
            )
        )

        self.assertContains(
            list_response,
            reverse(
                "analytics:evaluation-review-detail",
                kwargs={"observation_id": submitted.id},
            ),
        )
        self.assertNotContains(
            list_response,
            reverse(
                "analytics:evaluation-review-detail",
                kwargs={"observation_id": draft.id},
            ),
        )
        self.assertNotContains(
            list_response,
            reverse(
                "analytics:evaluation-review-detail",
                kwargs={"observation_id": reopened.id},
            ),
        )
        self.assertEqual(draft_detail.status_code, 404)
        self.assertEqual(reopened_detail.status_code, 404)

    def test_coach_review_detail_is_read_only_and_exposes_safe_evaluator_identity(self):
        observation = self.submitted_observation(note="Review detail note.")
        self.client.force_login(self.coach)

        response = self.client.get(
            reverse(
                "analytics:evaluation-review-detail",
                kwargs={"observation_id": observation.id},
            )
        )
        post_response = self.client.post(
            reverse(
                "analytics:evaluation-review-detail",
                kwargs={"observation_id": observation.id},
            ),
            {"action": "reopen"},
        )
        observation.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)
        self.assertContains(response, "Casey Coach")
        self.assertContains(response, "Coach")
        self.assertContains(response, "Review detail note.")
        self.assertNotContains(response, self.coach.email)
        self.assertNotContains(response, "Reopen")
        self.assertEqual(post_response.status_code, 405)
        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)

    def test_staff_review_reopen_remains_separate(self):
        observation = self.submitted_observation()
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse(
                "analytics:observation-review-detail",
                kwargs={"observation_id": observation.id},
            ),
            {"action": "reopen"},
            follow=True,
        )
        observation.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(observation.status, OBSERVATION_STATUS_REOPENED)

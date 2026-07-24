from analytics.tests.helpers import (
    OBSERVATION_STATUS_REOPENED,
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    AccountRole,
    Decimal,
    EvaluationCycle,
    ObservationResponse,
    Player,
    TestCase,
    User,
    UserPlayerRelationship,
    activate_link,
    attach_player_to_season,
    create_coach_assessment_observation,
    create_season,
    deactivate_link,
    ensure_default_coach_assessment_setup,
    get_my_evaluation_detail,
    get_my_evaluations,
    link_user_to_player,
    reverse,
    set_account_role,
    submit_observation,
)


class MyEvaluationsViewTests(TestCase):
    def setUp(self):
        self.player_user = User.objects.create_user(
            username="linked-player-user",
            password="testpass",
            first_name="Linked",
            last_name="User",
            email="linked@example.com",
        )
        self.other_player_user = User.objects.create_user(
            username="other-linked-player", password="testpass"
        )
        self.coach = User.objects.create_user(
            username="coach-private-name",
            password="testpass",
            first_name="Coach",
            last_name="Private",
            email="coach-private@example.com",
        )
        self.guest = User.objects.create_user(
            username="guest-evaluator-private", password="testpass"
        )
        self.parent = User.objects.create_user(
            username="parent-no-self", password="testpass"
        )
        self.staff = User.objects.create_user(
            username="staff-review", password="testpass", is_staff=True
        )
        set_account_role(self.player_user, AccountRole.PLAYER)
        set_account_role(self.other_player_user, AccountRole.PLAYER)
        set_account_role(self.coach, AccountRole.COACH)
        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
        set_account_role(self.parent, AccountRole.PARENT)
        set_account_role(self.staff, AccountRole.STAFF)
        self.player = Player.objects.create(
            first_name="Linked", last_name="Player", division="13U"
        )
        self.second_player = Player.objects.create(
            first_name="Second", last_name="Player", division="15U"
        )
        self.other_player = Player.objects.create(
            first_name="Other", last_name="Player", division="13U"
        )
        self.season = create_season(
            key="2026-spring", name="2026 Spring", is_current=True
        )
        attach_player_to_season(self.player, self.season)
        attach_player_to_season(
            self.second_player, self.season, team_name="Mounties", division="15U"
        )
        attach_player_to_season(self.other_player, self.season)
        link_user_to_player(
            self.player_user,
            self.player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )
        link_user_to_player(
            self.other_player_user,
            self.other_player,
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
        self, player=None, evaluator=None, value=4, note="Good teammate."
    ):
        result = create_coach_assessment_observation(
            player=player or self.player,
            evaluation_cycle=self.cycle,
            evaluator=evaluator or self.coach,
            responses=self.service_response_payload(value=value, note=note),
        )
        return submit_observation(result.observation, actor=evaluator or self.coach)

    def test_my_evaluations_requires_login_and_handles_no_self_link(self):
        self.assertEqual(
            self.client.get(reverse("analytics:my-evaluations")).status_code, 302
        )

        self.client.force_login(self.parent)
        response = self.client.get(reverse("analytics:my-evaluations"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No player record is linked to your account.")

    def test_player_can_view_submitted_evaluations_about_self(self):
        observation = self.submitted_observation(note="Shows leadership.")
        self.client.force_login(self.player_user)

        response = self.client.get(reverse("analytics:my-evaluations"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)
        self.assertContains(response, self.cycle.name)
        self.assertContains(response, "Coach")
        self.assertContains(response, "Coach Evaluation")
        self.assertContains(
            response,
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            ),
        )

    def test_my_evaluation_detail_hides_evaluator_identity_and_shows_feedback(self):
        observation = self.submitted_observation(value=5, note="Strong instincts.")
        self.client.force_login(self.player_user)

        response = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)
        self.assertContains(response, "Coach Evaluation")
        self.assertContains(response, "Evaluator Role")
        self.assertContains(response, "Coach")
        self.assertContains(response, self.cycle.name)
        self.assertContains(response, "Strong instincts.")
        self.assertContains(response, "5")
        self.assertNotContains(response, self.coach.username)
        self.assertNotContains(response, self.coach.email)
        self.assertNotContains(response, self.coach.get_full_name())

        players, summaries = get_my_evaluations(self.player_user)
        detail = get_my_evaluation_detail(self.player_user, observation.id)
        self.assertEqual(players, [self.player])
        self.assertEqual(summaries[0].observation_id, observation.id)
        self.assertFalse(hasattr(summaries[0], "observation"))
        self.assertEqual(detail.observation_id, observation.id)
        self.assertFalse(hasattr(detail, "observation"))

    def test_my_evaluation_detail_shows_unanswered_optional_questions(self):
        optional_question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        optional_question.is_required = False
        optional_question.save(update_fields=["is_required", "updated_at"])
        observation = self.submitted_observation(note="Required answers only.")
        self.client.force_login(self.player_user)

        response = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            )
        )
        detail = get_my_evaluation_detail(self.player_user, observation.id)
        optional_response = next(
            item
            for item in detail.responses
            if item.question_prompt == optional_question.prompt
        )

        self.assertContains(response, optional_question.prompt)
        self.assertContains(response, "Optional")
        self.assertContains(response, "Not answered")
        self.assertFalse(optional_response.is_required)
        self.assertIsNone(optional_response.numeric_value)

    def test_my_evaluations_show_self_label_without_external_identity(self):
        self_observation = self.submitted_observation(
            player=self.player, evaluator=self.player_user, note="My reflection."
        )
        self.client.force_login(self.player_user)

        list_response = self.client.get(reverse("analytics:my-evaluations"))
        detail_response = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": self_observation.id},
            )
        )

        self.assertContains(list_response, "Self Evaluation")
        self.assertContains(detail_response, "Self Evaluation")
        self.assertContains(detail_response, "My reflection.")

    def test_nonexistent_my_evaluation_detail_returns_404(self):
        self.client.force_login(self.player_user)

        response = self.client.get(
            reverse("analytics:my-evaluation-detail", kwargs={"observation_id": 999999})
        )

        self.assertEqual(response.status_code, 404)

    def test_player_cannot_view_another_players_evaluation_by_url(self):
        observation = self.submitted_observation(
            player=self.other_player, evaluator=self.coach
        )
        self.client.force_login(self.player_user)

        response = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_draft_and_reopened_observations_are_not_player_results(self):
        draft = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses=self.service_response_payload(),
        ).observation
        reopened = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.guest,
            responses=self.service_response_payload(),
        ).observation
        reopened.status = OBSERVATION_STATUS_REOPENED
        reopened.save(update_fields=["status", "updated_at"])
        self.client.force_login(self.player_user)

        list_response = self.client.get(reverse("analytics:my-evaluations"))
        draft_detail = self.client.get(
            reverse(
                "analytics:my-evaluation-detail", kwargs={"observation_id": draft.id}
            )
        )
        reopened_detail = self.client.get(
            reverse(
                "analytics:my-evaluation-detail", kwargs={"observation_id": reopened.id}
            )
        )

        self.assertNotContains(
            list_response,
            reverse(
                "analytics:my-evaluation-detail", kwargs={"observation_id": draft.id}
            ),
        )
        self.assertNotContains(
            list_response,
            reverse(
                "analytics:my-evaluation-detail", kwargs={"observation_id": reopened.id}
            ),
        )
        self.assertEqual(draft_detail.status_code, 403)
        self.assertEqual(reopened_detail.status_code, 403)

    def test_multiple_self_links_are_listed_and_player_specific_route_enforces_ownership(
        self,
    ):
        link_user_to_player(
            self.player_user,
            self.second_player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=False,
        )
        inactive_player = Player.objects.create(
            first_name="Inactive", last_name="Linked"
        )
        inactive_link = link_user_to_player(
            self.player_user,
            inactive_player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=False,
        )
        deactivate_link(inactive_link)
        first_observation = self.submitted_observation(
            player=self.player, evaluator=self.coach
        )
        second_observation = self.submitted_observation(
            player=self.second_player, evaluator=self.guest
        )
        self.client.force_login(self.player_user)

        response = self.client.get(reverse("analytics:my-evaluations"))
        player_response = self.client.get(
            reverse(
                "analytics:my-evaluations-player",
                kwargs={"player_id": self.second_player.id},
            )
        )
        first_detail = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": first_observation.id},
            )
        )
        second_detail = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": second_observation.id},
            )
        )
        forbidden_response = self.client.get(
            reverse(
                "analytics:my-evaluations-player",
                kwargs={"player_id": self.other_player.id},
            )
        )

        self.assertContains(response, self.player.display_name)
        self.assertContains(response, self.second_player.display_name)
        self.assertNotContains(response, inactive_player.display_name)
        self.assertContains(
            response,
            reverse(
                "analytics:my-evaluations-player", kwargs={"player_id": self.player.id}
            ),
        )
        self.assertContains(
            response,
            reverse(
                "analytics:my-evaluations-player",
                kwargs={"player_id": self.second_player.id},
            ),
        )
        self.assertContains(
            response,
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": first_observation.id},
            ),
        )
        self.assertContains(player_response, self.second_player.display_name)
        self.assertContains(
            player_response,
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": second_observation.id},
            ),
        )
        self.assertNotContains(
            player_response,
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": first_observation.id},
            ),
        )
        self.assertEqual(first_detail.status_code, 200)
        self.assertEqual(second_detail.status_code, 200)
        self.assertEqual(forbidden_response.status_code, 403)

    def test_coach_without_self_link_cannot_view_player_result_detail(self):
        observation = self.submitted_observation()
        self.client.force_login(self.coach)

        list_response = self.client.get(reverse("analytics:my-evaluations"))
        detail_response = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            )
        )

        self.assertContains(
            list_response, "No player record is linked to your account."
        )
        self.assertEqual(detail_response.status_code, 403)

        self.client.force_login(self.parent)
        parent_detail_response = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            )
        )
        self.assertEqual(parent_detail_response.status_code, 403)

    def test_inactive_self_link_removes_my_evaluations_access(self):
        observation = self.submitted_observation()
        link = self.player_user.player_links.get(
            player=self.player, relationship=UserPlayerRelationship.SELF
        )
        deactivate_link(link)
        self.client.force_login(self.player_user)

        list_response = self.client.get(reverse("analytics:my-evaluations"))
        detail_response = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            )
        )
        profile_response = self.client.get(reverse("accounts:profile"))

        self.assertContains(
            list_response, "No player record is linked to your account."
        )
        self.assertNotContains(
            list_response,
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            ),
        )
        self.assertEqual(detail_response.status_code, 403)
        self.assertNotContains(profile_response, reverse("analytics:my-evaluations"))

        activate_link(link)
        restored_list_response = self.client.get(reverse("analytics:my-evaluations"))
        restored_detail_response = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            )
        )
        restored_profile_response = self.client.get(reverse("accounts:profile"))
        self.assertContains(
            restored_list_response,
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            ),
        )
        self.assertEqual(restored_detail_response.status_code, 200)
        self.assertContains(
            restored_profile_response, reverse("analytics:my-evaluations")
        )

    def test_inactive_player_is_not_available_in_my_evaluations(self):
        observation = self.submitted_observation()
        self.player.is_active = False
        self.player.save(update_fields=["is_active", "updated_at"])
        self.client.force_login(self.player_user)

        list_response = self.client.get(reverse("analytics:my-evaluations"))
        player_response = self.client.get(
            reverse(
                "analytics:my-evaluations-player", kwargs={"player_id": self.player.id}
            )
        )
        detail_response = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            )
        )
        profile_response = self.client.get(reverse("accounts:profile"))

        self.assertContains(
            list_response, "No player record is linked to your account."
        )
        self.assertEqual(player_response.status_code, 403)
        self.assertEqual(detail_response.status_code, 403)
        self.assertNotContains(profile_response, reverse("analytics:my-evaluations"))

    def test_staff_with_self_link_receives_player_safe_my_evaluation_output(self):
        staff_player = Player.objects.create(first_name="Staff", last_name="Player")
        attach_player_to_season(staff_player, self.season)
        link_user_to_player(
            self.staff,
            staff_player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )
        observation = self.submitted_observation(
            player=staff_player,
            evaluator=self.coach,
            note="Private staff-linked result.",
        )
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Private staff-linked result.")
        self.assertContains(response, "Coach")
        self.assertNotContains(response, self.coach.username)
        self.assertNotContains(response, self.coach.email)
        self.assertNotContains(response, self.coach.get_full_name())

    def test_my_evaluation_responses_follow_question_display_order(self):
        question_set = self.setup_result.question_set
        first_question = question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        second_question = question_set.questions.filter(
            response_type=RESPONSE_TYPE_TEXT
        ).first()
        first_question.display_order = 20
        first_question.save(update_fields=["display_order", "updated_at"])
        second_question.display_order = 10
        second_question.prompt = "Appears before the rating"
        second_question.save(update_fields=["display_order", "prompt", "updated_at"])
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses=[
                {"question": first_question, "value": 4},
                {"question": second_question, "value": "Ordered note."},
            ],
        ).observation
        for required_question in question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5,
            is_required=True,
            is_active=True,
        ).exclude(pk=first_question.pk):
            ObservationResponse.objects.create(
                observation=observation,
                question=required_question,
                response_type=required_question.response_type,
                numeric_value=Decimal("3"),
            )
        observation = submit_observation(observation, actor=self.coach)
        self.client.force_login(self.player_user)

        response = self.client.get(
            reverse(
                "analytics:my-evaluation-detail",
                kwargs={"observation_id": observation.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertLess(
            content.index("Appears before the rating"),
            content.index(first_question.prompt),
        )

    def test_staff_review_and_submission_routes_still_work(self):
        observation = self.submitted_observation()
        self.client.force_login(self.staff)

        self.assertEqual(
            self.client.get(reverse("analytics:observation-review-list")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                reverse(
                    "analytics:observation-review-detail",
                    kwargs={"observation_id": observation.id},
                )
            ).status_code,
            200,
        )

        self.client.force_login(self.player_user)
        self.assertEqual(
            self.client.get(reverse("analytics:evaluation-list")).status_code, 200
        )

from analytics.tests.helpers import (
    COACH_ASSESSMENT_RUBRIC,
    DEFAULT_COACH_ASSESSMENT_QUESTIONS,
    DEFAULT_EVALUATOR_ROLES,
    DEFAULT_OBSERVATION_SOURCES,
    EVALUATION_PERSPECTIVE_COACH,
    EVALUATION_PERSPECTIVE_GUEST,
    EVALUATION_PERSPECTIVE_PEER,
    EVALUATION_PERSPECTIVE_SELF,
    EVALUATION_PERSPECTIVE_STAFF,
    OBSERVATION_STATUS_SUBMITTED,
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    ROLE_ADMIN,
    ROLE_COACH,
    ROLE_GUEST_EVALUATOR,
    ROLE_PLAYER,
    ROLE_STAFF,
    SOURCE_COACH,
    AccountRole,
    Decimal,
    EvaluationCycle,
    EvaluatorRole,
    IntegrityError,
    Observation,
    ObservationQuestion,
    ObservationQuestionSet,
    ObservationResponse,
    ObservationSource,
    ObservationType,
    Player,
    TestCase,
    User,
    UserPlayerRelationship,
    ValidationError,
    admin,
    attach_player_to_season,
    can_evaluate_player,
    can_submit_evaluation,
    can_view_own_evaluation_draft,
    create_coach_assessment_observation,
    create_observation,
    create_season,
    deactivate_link,
    default_coach_assessment_question_set,
    ensure_default_coach_assessment_setup,
    evaluation_perspective_for_user,
    evaluator_role_for_user,
    get_active_questions,
    get_observation_detail,
    get_question_set_for_cycle,
    link_user_to_player,
    save_observation_responses,
    set_account_role,
    submit_observation,
    transaction,
    validate_required_responses,
)


class AnalyticsObservationFoundationTests(TestCase):
    def setUp(self):
        self.evaluator = User.objects.create_user(username="coach", password="testpass")
        self.other_evaluator = User.objects.create_user(
            username="othercoach", password="testpass"
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
        self.player_membership = attach_player_to_season(self.player, self.season)
        attach_player_to_season(self.other_player, self.season)
        self.setup_result = ensure_default_coach_assessment_setup()
        self.role = EvaluatorRole.objects.get(key=ROLE_COACH)
        self.source = ObservationSource.objects.get(key=SOURCE_COACH)
        self.cycle = EvaluationCycle.objects.create(
            name="2026 13U Coach Assessment",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
            season=self.season,
        )

    def required_response_payload(self):
        return {
            question: 4
            for question in self.setup_result.question_set.questions.filter(
                response_type=RESPONSE_TYPE_RATING_1_5,
                is_required=True,
                is_active=True,
            )
        }

    def test_default_setup_creates_coach_assessment_configuration(self):
        self.assertTrue(
            ObservationType.objects.filter(
                key=OBSERVATION_TYPE_COACH_ASSESSMENT
            ).exists()
        )
        self.assertEqual(
            ObservationSource.objects.count(), len(DEFAULT_OBSERVATION_SOURCES)
        )
        self.assertEqual(EvaluatorRole.objects.count(), len(DEFAULT_EVALUATOR_ROLES))
        self.assertEqual(self.setup_result.question_set.rubric, COACH_ASSESSMENT_RUBRIC)
        self.assertEqual(
            self.setup_result.question_set.questions.count(),
            len(DEFAULT_COACH_ASSESSMENT_QUESTIONS),
        )
        self.assertEqual(
            self.setup_result.question_set.questions.filter(
                response_type=RESPONSE_TYPE_TEXT
            ).count(),
            1,
        )
        self.assertEqual(
            self.setup_result.question_set.questions.filter(
                response_type=RESPONSE_TYPE_RATING_1_5
            ).count(),
            len(DEFAULT_COACH_ASSESSMENT_QUESTIONS) - 1,
        )

    def test_default_setup_is_idempotent(self):
        first_question_count = ObservationQuestion.objects.count()

        second_result = ensure_default_coach_assessment_setup()

        self.assertEqual(ObservationQuestion.objects.count(), first_question_count)
        self.assertEqual(second_result.questions_created, 0)

    def test_default_setup_does_not_overwrite_existing_questions(self):
        question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        question.prompt = "Edited prompt"
        question.display_order = 99
        question.is_required = False
        question.save()

        ensure_default_coach_assessment_setup()

        question.refresh_from_db()
        self.assertEqual(question.prompt, "Edited prompt")
        self.assertEqual(question.display_order, 99)
        self.assertFalse(question.is_required)

    def test_cycle_slug_generation_creates_unique_slugs(self):
        second_cycle = EvaluationCycle.objects.create(
            name=self.cycle.name, cycle_type="Coach Assessment"
        )

        self.assertEqual(self.cycle.slug, "2026-13u-coach-assessment")
        self.assertEqual(second_cycle.slug, "2026-13u-coach-assessment-2")

    def test_question_set_version_is_unique_per_observation_type(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ObservationQuestionSet.objects.create(
                    observation_type=self.setup_result.observation_type,
                    name="Duplicate",
                    version=1,
                )

    def test_question_key_is_unique_per_question_set(self):
        first_question = self.setup_result.question_set.questions.first()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ObservationQuestion.objects.create(
                    question_set=self.setup_result.question_set,
                    key=first_question.key,
                    prompt="Duplicate",
                    response_type=RESPONSE_TYPE_RATING_1_5,
                )

    def test_get_active_questions_and_cycle_question_set(self):
        questions = list(get_active_questions(self.setup_result.question_set))

        self.assertEqual(questions[0].display_order, 1)
        self.assertEqual(
            get_question_set_for_cycle(self.cycle), self.setup_result.question_set
        )
        fallback_cycle = EvaluationCycle.objects.create(
            name="Fallback Cycle", cycle_type="Coach Assessment"
        )
        self.assertEqual(
            get_question_set_for_cycle(fallback_cycle), self.setup_result.question_set
        )

    def test_cycle_rejects_non_coach_assessment_question_set(self):
        other_type = ObservationType.objects.create(key="tryout", name="Tryout")
        other_question_set = ObservationQuestionSet.objects.create(
            observation_type=other_type, name="Tryout", version=1
        )

        with self.assertRaises(ValidationError):
            EvaluationCycle.objects.create(
                name="Invalid Cycle",
                cycle_type="Coach Assessment",
                coach_assessment_question_set=other_question_set,
            )

    def test_create_coach_assessment_references_players_player_and_snapshots_role(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
            evaluator_role=self.role,
            source=self.source,
        )

        observation = result.observation
        self.assertEqual(observation.player, self.player)
        self.assertEqual(observation.evaluator_role_key, ROLE_COACH)
        self.assertEqual(observation.evaluator_role_name, "Coach")
        self.assertEqual(
            observation.observation_type_key, OBSERVATION_TYPE_COACH_ASSESSMENT
        )

    def test_evaluation_submission_permissions_by_role(self):
        anonymous = None
        coach = User.objects.create_user(username="rolecoach", password="testpass")
        player_user = User.objects.create_user(
            username="roleplayer", password="testpass"
        )
        staff_user = User.objects.create_user(
            username="rolestaff", password="testpass", is_staff=True
        )
        guest = User.objects.create_user(username="roleguest", password="testpass")
        parent = User.objects.create_user(username="roleparent", password="testpass")
        set_account_role(coach, AccountRole.COACH)
        set_account_role(player_user, AccountRole.PLAYER)
        set_account_role(staff_user, AccountRole.STAFF)
        set_account_role(guest, AccountRole.GUEST_EVALUATOR)
        set_account_role(parent, AccountRole.PARENT)

        self.assertFalse(can_submit_evaluation(anonymous))
        self.assertTrue(can_submit_evaluation(coach))
        self.assertTrue(can_submit_evaluation(player_user))
        self.assertTrue(can_submit_evaluation(staff_user))
        self.assertTrue(can_submit_evaluation(guest))
        self.assertFalse(can_submit_evaluation(parent))

    def test_self_evaluation_is_allowed_with_active_self_link_only(self):
        player_user = User.objects.create_user(
            username="selflinked", password="testpass"
        )
        set_account_role(player_user, AccountRole.PLAYER)
        link = link_user_to_player(
            player_user,
            self.player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )

        self.assertTrue(can_evaluate_player(player_user, self.player))
        self.assertTrue(can_evaluate_player(player_user, self.other_player))
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=player_user,
        )
        self.assertEqual(
            result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF
        )

        deactivate_link(link)
        self.assertFalse(can_evaluate_player(player_user, self.player))
        with self.assertRaises(ValidationError):
            evaluation_perspective_for_user(player_user, self.player)

    def test_evaluation_perspective_is_server_derived_by_role(self):
        users = [
            (AccountRole.COACH, EVALUATION_PERSPECTIVE_COACH),
            (AccountRole.PLAYER, EVALUATION_PERSPECTIVE_PEER),
            (AccountRole.STAFF, EVALUATION_PERSPECTIVE_STAFF),
            (AccountRole.ADMIN, EVALUATION_PERSPECTIVE_STAFF),
            (AccountRole.GUEST_EVALUATOR, EVALUATION_PERSPECTIVE_GUEST),
        ]
        for account_role, expected_perspective in users:
            with self.subTest(account_role=account_role):
                evaluator = User.objects.create_user(
                    username=f"perspective-{account_role}", password="testpass"
                )
                set_account_role(evaluator, account_role)
                self.assertEqual(
                    evaluation_perspective_for_user(evaluator, self.other_player),
                    expected_perspective,
                )

    def test_parent_role_cannot_create_observation(self):
        parent = User.objects.create_user(username="parent", password="testpass")
        set_account_role(parent, AccountRole.PARENT)

        with self.assertRaises(ValidationError):
            create_coach_assessment_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                evaluator=parent,
            )

    def test_evaluator_role_for_user_maps_account_roles(self):
        expectations = [
            (AccountRole.COACH, ROLE_COACH),
            (AccountRole.PLAYER, ROLE_PLAYER),
            (AccountRole.STAFF, ROLE_STAFF),
            (AccountRole.ADMIN, ROLE_ADMIN),
            (AccountRole.GUEST_EVALUATOR, ROLE_GUEST_EVALUATOR),
        ]
        for account_role, evaluator_role_key in expectations:
            with self.subTest(account_role=account_role):
                user = User.objects.create_user(
                    username=f"{account_role}-user", password="testpass"
                )
                set_account_role(user, account_role)

                evaluator_role = evaluator_role_for_user(user)

                self.assertEqual(evaluator_role.key, evaluator_role_key)

    def test_coach_assessment_snapshots_actual_account_role_by_default(self):
        role_expectations = [
            (AccountRole.COACH, ROLE_COACH),
            (AccountRole.PLAYER, ROLE_PLAYER),
            (AccountRole.STAFF, ROLE_STAFF),
            (AccountRole.ADMIN, ROLE_ADMIN),
            (AccountRole.GUEST_EVALUATOR, ROLE_GUEST_EVALUATOR),
        ]
        for index, (account_role, evaluator_role_key) in enumerate(
            role_expectations, start=1
        ):
            with self.subTest(account_role=account_role):
                evaluator = User.objects.create_user(
                    username=f"snapshot-{account_role}", password="testpass"
                )
                set_account_role(evaluator, account_role)
                player = Player.objects.create(
                    first_name=f"Snapshot{index}", last_name="Target", division="13U"
                )
                attach_player_to_season(player, self.season)

                result = create_coach_assessment_observation(
                    player=player,
                    evaluation_cycle=self.cycle,
                    evaluator=evaluator,
                )

                self.assertEqual(
                    result.observation.evaluator_role_key, evaluator_role_key
                )
                self.assertEqual(
                    result.observation.evaluator_role,
                    EvaluatorRole.objects.get(key=evaluator_role_key),
                )

    def test_draft_view_helpers_are_limited_to_own_drafts(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        self.assertTrue(can_view_own_evaluation_draft(self.evaluator, observation))
        self.assertFalse(
            can_view_own_evaluation_draft(self.other_evaluator, observation)
        )

        observation.status = OBSERVATION_STATUS_SUBMITTED
        observation.save(update_fields=["status", "updated_at"])
        self.assertFalse(can_view_own_evaluation_draft(self.evaluator, observation))

    def test_submitted_observation_sets_submitted_at(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
            responses=self.required_response_payload(),
        )
        submitted = submit_observation(result.observation)

        self.assertIsNotNone(submitted.submitted_at)

    def test_coach_assessment_requires_evaluator(self):
        with self.assertRaises(ValidationError):
            create_coach_assessment_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                evaluator=None,
            )

    def test_create_observation_rejects_mismatched_question_set_type(self):
        other_type = ObservationType.objects.create(key="tryout", name="Tryout")
        other_question_set = ObservationQuestionSet.objects.create(
            observation_type=other_type, name="Tryout", version=1
        )

        with self.assertRaises(ValidationError):
            create_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                observation_type=self.setup_result.observation_type,
                question_set=other_question_set,
                source=self.source,
                evaluator=self.evaluator,
                evaluator_role=self.role,
            )

    def test_save_numeric_text_and_payload_responses(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        rating_question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()
        text_question = self.setup_result.question_set.questions.get(
            response_type=RESPONSE_TYPE_TEXT
        )

        created, updated = save_observation_responses(
            observation,
            [
                {
                    "question": rating_question,
                    "value": 4,
                    "payload": {"source": "test"},
                },
                {"question": text_question.key, "value": "Good teammate."},
            ],
        )

        rating_response = ObservationResponse.objects.get(
            observation=observation, question=rating_question
        )
        text_response = ObservationResponse.objects.get(
            observation=observation, question=text_question
        )
        self.assertEqual(created, 2)
        self.assertEqual(updated, 0)
        self.assertEqual(rating_response.numeric_value, Decimal("4.00"))
        self.assertEqual(rating_response.payload, {"source": "test"})
        self.assertEqual(text_response.text_value, "Good teammate.")

    def test_save_response_updates_existing_response(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()

        save_observation_responses(observation, {question: 3})
        created, updated = save_observation_responses(observation, {question: 5})

        response = ObservationResponse.objects.get(
            observation=observation, question=question
        )
        self.assertEqual(created, 0)
        self.assertEqual(updated, 1)
        self.assertEqual(response.numeric_value, Decimal("5.00"))

    def test_invalid_rating_is_rejected(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()

        with self.assertRaises(ValidationError):
            save_observation_responses(observation, {question: 6})

    def test_decimal_and_non_finite_ratings_are_rejected(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        question = self.setup_result.question_set.questions.filter(
            response_type=RESPONSE_TYPE_RATING_1_5
        ).first()

        for value in ["3.5", "NaN", "Infinity"]:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    save_observation_responses(observation, {question: value})

    def test_question_from_different_question_set_is_rejected(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        other_question_set = ObservationQuestionSet.objects.create(
            observation_type=self.setup_result.observation_type,
            name="Other",
            version=2,
        )
        other_question = ObservationQuestion.objects.create(
            question_set=other_question_set,
            key="other_question",
            prompt="Other question",
            response_type=RESPONSE_TYPE_RATING_1_5,
        )

        with self.assertRaises(ValidationError):
            save_observation_responses(observation, {other_question: 3})

    def test_duplicate_coach_assessment_is_prevented_for_same_evaluator_player_cycle(
        self,
    ):
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        )

        with self.assertRaises(ValidationError):
            create_coach_assessment_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                evaluator=self.evaluator,
            )

    def test_duplicate_self_evaluation_is_prevented_for_player_cycle(self):
        first_player_user = User.objects.create_user(
            username="self-one", password="testpass"
        )
        second_player_user = User.objects.create_user(
            username="self-two", password="testpass"
        )
        set_account_role(first_player_user, AccountRole.PLAYER)
        set_account_role(second_player_user, AccountRole.PLAYER)
        link_user_to_player(
            first_player_user,
            self.player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )
        link_user_to_player(
            second_player_user,
            self.player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=False,
        )

        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=first_player_user,
        )

        with self.assertRaises(ValidationError):
            create_coach_assessment_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                evaluator=second_player_user,
            )

    def test_self_and_peer_evaluations_from_same_player_are_distinct(self):
        player_user = User.objects.create_user(
            username="self-peer", password="testpass"
        )
        set_account_role(player_user, AccountRole.PLAYER)
        link_user_to_player(
            player_user,
            self.player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )

        self_result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=player_user,
        )
        peer_result = create_coach_assessment_observation(
            player=self.other_player,
            evaluation_cycle=self.cycle,
            evaluator=player_user,
        )

        self.assertEqual(
            self_result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF
        )
        self.assertEqual(
            peer_result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER
        )

    def test_multiple_evaluators_can_assess_same_player_cycle(self):
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        )
        second = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_evaluator,
        )

        self.assertEqual(second.observation.player, self.player)
        self.assertEqual(
            Observation.objects.filter(
                player=self.player, evaluation_cycle=self.cycle
            ).count(),
            2,
        )

    def test_same_evaluator_can_assess_different_players_and_cycles(self):
        other_cycle = EvaluationCycle.objects.create(
            name="2026 15U Coach Assessment", cycle_type="Coach Assessment"
        )

        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        )
        create_coach_assessment_observation(
            player=self.other_player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        )
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=other_cycle,
            evaluator=self.evaluator,
        )

        self.assertEqual(
            Observation.objects.filter(evaluator=self.evaluator).count(), 3
        )

    def test_submit_observation_and_detail_loader(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        save_observation_responses(observation, self.required_response_payload())

        submitted = submit_observation(observation, actor=self.evaluator)
        detail = get_observation_detail(submitted.id)

        self.assertEqual(submitted.status, OBSERVATION_STATUS_SUBMITTED)
        self.assertIsNotNone(submitted.submitted_at)
        self.assertEqual(detail.player, self.player)

    def test_submit_observation_requires_required_responses(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation

        with self.assertRaises(ValidationError):
            validate_required_responses(observation)
        with self.assertRaises(ValidationError):
            submit_observation(observation, actor=self.evaluator)

    def test_default_question_set_wrapper(self):
        self.assertEqual(
            default_coach_assessment_question_set(), self.setup_result.question_set
        )

    def test_phase_three_models_registered_in_admin(self):
        for model in [
            EvaluationCycle,
            ObservationType,
            ObservationSource,
            EvaluatorRole,
            ObservationQuestionSet,
            ObservationQuestion,
            Observation,
            ObservationResponse,
        ]:
            self.assertIn(model, admin.site._registry)

from seasons.tests.helpers import (
    AccountRole,
    CoachAssignmentRole,
    CoachSeasonAssignment,
    TestCase,
    User,
    ValidationError,
    assignments_for_team,
    assignments_for_user,
    create_assignment,
    create_season,
    date,
    deactivate_assignment,
    get_or_create_account_profile,
    get_or_create_season_team,
    get_primary_assignment,
    set_account_role,
    update_assignment,
)


class CoachAssignmentTests(TestCase):
    def setUp(self):
        self.spring = create_season(key="2026-spring", name="2026 Spring")
        self.dodgers, _ = get_or_create_season_team(
            season=self.spring, name="Dodgers", division="13U"
        )
        self.expos, _ = get_or_create_season_team(
            season=self.spring, name="Expos", division="13U"
        )
        self.coach = User.objects.create_user(
            username="coach",
            password="original-pass",
            first_name="Casey",
            last_name="Coach",
            email="coach@example.com",
        )
        set_account_role(self.coach, AccountRole.COACH)

    def test_create_assignment_and_query_helpers(self):
        assignment = create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
            is_primary=True,
        )

        self.assertEqual(
            assignments_for_user(self.coach, self.spring).first(), assignment
        )
        self.assertEqual(assignments_for_team(self.dodgers).first(), assignment)
        self.assertEqual(get_primary_assignment(self.coach, self.spring), assignment)

    def test_multiple_assignments_and_multiple_coaches_allowed(self):
        other = User.objects.create_user(username="other", password="testpass")

        first = create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
        )
        second = create_assignment(
            user=self.coach,
            season_team=self.expos,
            assignment_role=CoachAssignmentRole.EVALUATOR,
        )
        third = create_assignment(
            user=other,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.ASSISTANT_COACH,
        )

        self.assertEqual(
            {first, second}, set(assignments_for_user(self.coach, self.spring))
        )
        self.assertIn(third, list(assignments_for_team(self.dodgers)))

    def test_duplicate_active_user_team_role_rejected(self):
        create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
        )

        with self.assertRaises(ValidationError):
            create_assignment(
                user=self.coach,
                season_team=self.dodgers,
                assignment_role=CoachAssignmentRole.HEAD_COACH,
            )

    def test_only_one_active_primary_assignment_per_user_season(self):
        first = create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
            is_primary=True,
        )
        second = create_assignment(
            user=self.coach,
            season_team=self.expos,
            assignment_role=CoachAssignmentRole.EVALUATOR,
            is_primary=True,
        )

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_primary)
        self.assertTrue(second.is_primary)

    def test_update_assignment_can_unset_primary(self):
        assignment = create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
            is_primary=True,
        )

        update_assignment(assignment, is_primary=False)
        assignment.refresh_from_db()

        self.assertFalse(assignment.is_primary)

    def test_direct_duplicate_primary_assignment_is_rejected(self):
        create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
            is_primary=True,
        )

        with self.assertRaises(ValidationError):
            CoachSeasonAssignment.objects.create(
                user=self.coach,
                season_team=self.expos,
                assignment_role=CoachAssignmentRole.EVALUATOR,
                is_primary=True,
            )

    def test_assignment_has_no_account_role_privilege_or_password_side_effects(self):
        original_password = self.coach.password
        create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
        )
        self.coach.refresh_from_db()
        profile = get_or_create_account_profile(self.coach)

        self.assertEqual(profile.role, AccountRole.COACH)
        self.assertFalse(self.coach.is_staff)
        self.assertFalse(self.coach.is_superuser)
        self.assertEqual(self.coach.password, original_password)

    def test_assignment_date_validation_and_deactivation(self):
        with self.assertRaises(ValidationError):
            create_assignment(
                user=self.coach,
                season_team=self.dodgers,
                assignment_role=CoachAssignmentRole.HEAD_COACH,
                starts_on=date(2026, 8, 1),
                ends_on=date(2026, 7, 1),
            )

        assignment = create_assignment(
            user=self.coach,
            season_team=self.dodgers,
            assignment_role=CoachAssignmentRole.HEAD_COACH,
            is_primary=True,
        )
        deactivate_assignment(assignment, ends_on=date(2026, 8, 1))
        assignment.refresh_from_db()
        self.assertFalse(assignment.is_active)
        self.assertFalse(assignment.is_primary)
        self.assertEqual(assignment.ends_on, date(2026, 8, 1))

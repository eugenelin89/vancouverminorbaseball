from accounts.tests.helpers import (
    ACCOUNT_LOGIN_PATH,
    ACCOUNT_LOGOUT_PATH,
    ACCOUNT_PASSWORD_PATH,
    ACCOUNT_PROFILE_PATH,
    ANALYTICS_HOME_PATH,
    SESSION_KEY,
    AccountRole,
    Player,
    TestCase,
    User,
    UserPlayerRelationship,
    get_or_create_account_profile,
    is_password_change_allowed_path,
    landing_url_for_user,
    link_user_to_player,
    reverse,
    set_account_role,
    settings,
    should_force_password_change,
)


class AccountAuthRedirectServiceTests(TestCase):
    def test_landing_url_for_user(self):
        anonymous = None
        staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )
        regular = User.objects.create_user(username="regular", password="testpass")

        self.assertEqual(landing_url_for_user(anonymous), ACCOUNT_LOGIN_PATH)
        self.assertEqual(landing_url_for_user(staff), ANALYTICS_HOME_PATH)
        self.assertEqual(landing_url_for_user(regular), ACCOUNT_PROFILE_PATH)

    def test_should_force_password_change(self):
        user = User.objects.create_user(username="user", password="testpass")
        profile = get_or_create_account_profile(user)

        self.assertFalse(should_force_password_change(user))
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password", "updated_at"])
        self.assertTrue(should_force_password_change(user))

    def test_missing_account_profile_is_safe(self):
        user = User.objects.create_user(username="user", password="testpass")

        self.assertFalse(should_force_password_change(user))

    def test_allowed_paths(self):
        user = User.objects.create_user(username="user", password="testpass")
        superuser = User.objects.create_superuser(username="admin", password="testpass")

        self.assertTrue(is_password_change_allowed_path(ACCOUNT_PASSWORD_PATH, user))
        self.assertTrue(is_password_change_allowed_path(ACCOUNT_LOGOUT_PATH, user))
        self.assertTrue(is_password_change_allowed_path(ACCOUNT_LOGIN_PATH, user))
        self.assertTrue(is_password_change_allowed_path("/static/app.css", user))
        self.assertTrue(is_password_change_allowed_path("/media/avatar.png", user))
        self.assertFalse(is_password_change_allowed_path("/admin/", user))
        self.assertTrue(is_password_change_allowed_path("/admin/", superuser))
        self.assertFalse(is_password_change_allowed_path("/analytics/", user))


class AccountAuthViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass")
        self.staff = User.objects.create_user(
            username="staff", password="testpass", is_staff=True
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account Login")

    def test_non_staff_login_lands_at_profile(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "user", "password": "testpass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], landing_url_for_user(self.user))

    def test_staff_login_lands_at_analytics(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "staff", "password": "testpass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], landing_url_for_user(self.staff))

    def test_safe_next_parameter_is_respected_without_forced_password_change(self):
        response = self.client.post(
            f"{reverse('accounts:login')}?next=/analytics/assessments/",
            {"username": "user", "password": "testpass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/analytics/assessments/")

    def test_forced_password_change_overrides_next_parameter(self):
        profile = get_or_create_account_profile(self.user)
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password", "updated_at"])

        response = self.client.post(
            f"{reverse('accounts:login')}?next=/analytics/assessments/",
            {"username": "user", "password": "testpass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], ACCOUNT_PASSWORD_PATH)

    def test_logout_redirects_to_account_login(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], ACCOUNT_LOGIN_PATH)

    def test_password_page_renders_for_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:password-change"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update Password")

    def test_password_change_clears_flag_and_keeps_user_logged_in(self):
        profile = get_or_create_account_profile(self.user)
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password", "updated_at"])
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:password-change"),
            {
                "old_password": "testpass",
                "new_password1": "new-strong-pass-123",
                "new_password2": "new-strong-pass-123",
            },
        )

        profile.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], landing_url_for_user(self.user))
        self.assertFalse(profile.must_change_password)
        self.assertIn(SESSION_KEY, self.client.session)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-strong-pass-123"))

        landing_response = self.client.get(response["Location"])
        self.assertEqual(landing_response.status_code, 200)
        self.assertNotEqual(landing_response.get("Location"), ACCOUNT_PASSWORD_PATH)

    def test_password_change_redirects_staff_to_landing_service_url(self):
        profile = get_or_create_account_profile(self.staff)
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password", "updated_at"])
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("accounts:password-change"),
            {
                "old_password": "testpass",
                "new_password1": "new-strong-pass-123",
                "new_password2": "new-strong-pass-123",
            },
        )

        profile.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], landing_url_for_user(self.staff))
        self.assertFalse(profile.must_change_password)
        self.assertIn(SESSION_KEY, self.client.session)

    def test_inactive_user_cannot_login(self):
        inactive = User.objects.create_user(
            username="inactive", password="testpass", is_active=False
        )
        get_or_create_account_profile(inactive)

        response = self.client.post(
            reverse("accounts:login"),
            {"username": "inactive", "password": "testpass"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_profile_page_renders_basic_account_info(self):
        get_or_create_account_profile(self.user)
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account Profile")
        self.assertContains(response, "Guest Evaluator")

    def test_profile_submit_evaluation_link_uses_service_permissions(self):
        cases = [
            (AccountRole.COACH, True),
            (AccountRole.PLAYER, True),
            (AccountRole.GUEST_EVALUATOR, True),
            (AccountRole.PARENT, False),
        ]
        for role, should_see_link in cases:
            with self.subTest(role=role):
                user = User.objects.create_user(
                    username=f"profile-{role}", password="testpass"
                )
                set_account_role(user, role)
                self.client.force_login(user)

                response = self.client.get(reverse("accounts:profile"))

                if should_see_link:
                    self.assertContains(response, reverse("analytics:evaluation-list"))
                    self.assertContains(response, "Submit Evaluation")
                else:
                    self.assertNotContains(
                        response, reverse("analytics:evaluation-list")
                    )
                    self.assertNotContains(response, "Submit Evaluation")
                self.client.logout()

    def test_profile_my_evaluations_link_requires_self_link(self):
        player = Player.objects.create(first_name="Linked", last_name="Player")
        player_user = User.objects.create_user(
            username="linked-player", password="testpass"
        )
        coach = User.objects.create_user(username="unlinked-coach", password="testpass")
        parent = User.objects.create_user(
            username="unlinked-parent", password="testpass"
        )
        set_account_role(player_user, AccountRole.PLAYER)
        set_account_role(coach, AccountRole.COACH)
        set_account_role(parent, AccountRole.PARENT)
        link_user_to_player(
            player_user,
            player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
        )

        self.client.force_login(player_user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertContains(response, reverse("analytics:my-evaluations"))
        self.assertContains(response, "My Evaluations")

        for user in [coach, parent]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("accounts:profile"))
                self.assertNotContains(response, reverse("analytics:my-evaluations"))
                self.client.logout()


class AccountPasswordMiddlewareTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass")
        self.profile = get_or_create_account_profile(self.user)

    def require_password_change(self):
        self.profile.must_change_password = True
        self.profile.save(update_fields=["must_change_password", "updated_at"])
        self.client.force_login(self.user)

    def test_forced_password_user_redirected_from_normal_page(self):
        self.require_password_change()

        response = self.client.get(reverse("analytics:assessment-list"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], ACCOUNT_PASSWORD_PATH)

    def test_allowed_paths_do_not_redirect_loop(self):
        self.require_password_change()

        self.assertEqual(
            self.client.get(reverse("accounts:password-change")).status_code, 200
        )
        self.assertNotEqual(self.client.get(reverse("accounts:login")).status_code, 302)
        self.assertEqual(self.client.post(reverse("accounts:logout")).status_code, 302)

    def test_password_page_post_is_not_blocked_by_middleware(self):
        self.require_password_change()

        response = self.client.post(
            reverse("accounts:password-change"),
            {
                "old_password": "wrong-password",
                "new_password1": "new-strong-pass-123",
                "new_password2": "new-strong-pass-123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update Password")

    def test_middleware_does_not_redirect_after_successful_password_change(self):
        self.require_password_change()

        response = self.client.post(
            reverse("accounts:password-change"),
            {
                "old_password": "testpass",
                "new_password1": "new-strong-pass-123",
                "new_password2": "new-strong-pass-123",
            },
        )

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.profile.must_change_password)
        profile_response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(profile_response.status_code, 200)

    def test_static_media_and_superuser_admin_paths_are_allowed(self):
        superuser = User.objects.create_superuser(username="admin", password="testpass")
        profile = get_or_create_account_profile(superuser)
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password", "updated_at"])
        self.client.force_login(superuser)

        self.assertNotEqual(self.client.get("/static/app.css").status_code, 302)
        self.assertNotEqual(self.client.get("/media/app.png").status_code, 302)
        self.assertNotEqual(self.client.get("/admin/").status_code, 302)

    def test_user_without_forced_password_change_is_not_redirected(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)

    def test_missing_account_profile_is_safe(self):
        user = User.objects.create_user(username="missing-profile", password="testpass")
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)


class AccountPdpCoexistenceTests(TestCase):
    def test_pdp_login_route_still_renders(self):
        response = self.client.get(reverse("pdp:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Athlete Login")

    def test_pdp_routes_and_middleware_remain_installed(self):
        self.assertEqual(reverse("pdp:login"), "/pdp/login/")
        self.assertIn(
            "pdp.middleware.FirstLoginPasswordChangeMiddleware", settings.MIDDLEWARE
        )
        self.assertIn(
            "accounts.middleware.AccountPasswordChangeRequiredMiddleware",
            settings.MIDDLEWARE,
        )
        self.assertLess(
            settings.MIDDLEWARE.index(
                "pdp.middleware.FirstLoginPasswordChangeMiddleware"
            ),
            settings.MIDDLEWARE.index(
                "accounts.middleware.AccountPasswordChangeRequiredMiddleware"
            ),
        )

    def test_global_login_settings_are_account_forward(self):
        self.assertEqual(settings.LOGIN_URL, ACCOUNT_LOGIN_PATH)
        self.assertEqual(settings.LOGIN_REDIRECT_URL, ACCOUNT_PROFILE_PATH)

    def test_account_operations_routes_are_platform_account_routes(self):
        self.assertEqual(reverse("accounts:operations-dashboard"), "/accounts/")
        self.assertEqual(reverse("accounts:user-list"), "/accounts/users/")

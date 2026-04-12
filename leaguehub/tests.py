import shutil
import tempfile
from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from leaguehub.models import (
    CoachRole,
    Game,
    GamePhoto,
    GameScoreAuditEntry,
    GameStatus,
    GameStory,
    GameVerificationStatus,
    League,
    LeagueSeason,
    Team,
    TeamCoachAssignment,
)
from leaguehub.services.score_workflow import submit_home_score, verify_game_score
from leaguehub.services.standings import calculate_official_standings
from pdp.models import Season


User = get_user_model()


@override_settings(ALLOWED_HOSTS=["testserver"])
class LeagueHubFlowTests(TestCase):
    GIF_BYTES = (
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
        b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00"
        b"\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media_root = tempfile.mkdtemp()
        cls._override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._override.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.season = Season.objects.create(name="2026 Season", slug="2026-season", year=2026, is_active=True)
        self.league = League.objects.create(name="13U House", slug="13u-house")
        self.league_season = LeagueSeason.objects.create(
            league=self.league,
            season=self.season,
            slug="13u-house-2026",
            title="2026 13U House",
        )
        self.home_team = Team.objects.create(league_season=self.league_season, name="Expos Navy", slug="expos-navy")
        self.away_team = Team.objects.create(league_season=self.league_season, name="Expos Gold", slug="expos-gold")
        self.third_team = Team.objects.create(league_season=self.league_season, name="Expos White", slug="expos-white")

        self.home_coach = User.objects.create_user(
            username="homecoach",
            password="testpass123",
            first_name="Home",
            last_name="Coach",
            email="home@example.com",
        )
        self.away_coach = User.objects.create_user(
            username="awaycoach",
            password="testpass123",
            first_name="Away",
            last_name="Coach",
            email="away@example.com",
        )
        self.assistant_coach = User.objects.create_user(
            username="assistantcoach",
            password="testpass123",
            first_name="Assist",
            last_name="Coach",
            email="assist@example.com",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123",
            first_name="Other",
            last_name="User",
            email="other@example.com",
        )
        self.admin = User.objects.create_superuser(
            username="adminuser",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
        )

        TeamCoachAssignment.objects.create(team=self.home_team, user=self.home_coach, role=CoachRole.HEAD_COACH)
        TeamCoachAssignment.objects.create(team=self.away_team, user=self.away_coach, role=CoachRole.HEAD_COACH)
        TeamCoachAssignment.objects.create(team=self.home_team, user=self.assistant_coach, role=CoachRole.ASSISTANT_COACH)

        self.game = Game.objects.create(
            league_season=self.league_season,
            game_date=date(2026, 4, 12),
            home_team=self.home_team,
            away_team=self.away_team,
            location="Nanaimo Park",
        )
        self.second_game = Game.objects.create(
            league_season=self.league_season,
            game_date=date(2026, 4, 13),
            home_team=self.home_team,
            away_team=self.third_team,
            location="Kensington Park",
        )

    def _login(self, user):
        self.client.force_login(user)

    def _test_image(self, name="test.gif"):
        return SimpleUploadedFile(name, self.GIF_BYTES, content_type="image/gif")

    def test_score_submission_permissions(self):
        submit_url = reverse("leaguehub:submit-score", kwargs={"pk": self.game.pk})

        self._login(self.away_coach)
        response = self.client.post(submit_url, {"home_score": 5, "away_score": 3})
        self.assertEqual(response.status_code, 403)

        self._login(self.home_coach)
        response = self.client.post(submit_url, {"home_score": 5, "away_score": 3})
        self.assertEqual(response.status_code, 302)
        self.game.refresh_from_db()
        self.assertEqual(self.game.home_score, 5)
        self.assertEqual(self.game.away_score, 3)
        self.assertEqual(self.game.verification_status, GameVerificationStatus.AWAITING_AWAY_VERIFICATION)

    def test_score_verification_permissions(self):
        submit_home_score(game=self.game, actor=self.home_coach, home_score=4, away_score=2)
        verify_url = reverse("leaguehub:verify-score", kwargs={"pk": self.game.pk})

        self._login(self.home_coach)
        response = self.client.post(verify_url, {"confirm": "on"})
        self.assertEqual(response.status_code, 403)

        self._login(self.away_coach)
        response = self.client.post(verify_url, {"confirm": "on"})
        self.assertEqual(response.status_code, 302)
        self.game.refresh_from_db()
        self.assertEqual(self.game.verification_status, GameVerificationStatus.VERIFIED_FINAL)

    def test_non_admin_edits_blocked_after_verified_final(self):
        submit_home_score(game=self.game, actor=self.home_coach, home_score=6, away_score=4)
        verify_game_score(game=self.game, actor=self.away_coach)

        submit_url = reverse("leaguehub:submit-score", kwargs={"pk": self.game.pk})
        self._login(self.home_coach)
        response = self.client.post(submit_url, {"home_score": 7, "away_score": 4})

        self.assertEqual(response.status_code, 200)
        self.game.refresh_from_db()
        self.assertEqual(self.game.home_score, 6)
        self.assertEqual(self.game.away_score, 4)
        self.assertContains(response, "Verified final games cannot be edited by non-admin users.")

    def test_admin_override_creates_audit_entry(self):
        submit_home_score(game=self.game, actor=self.home_coach, home_score=3, away_score=2)
        verify_game_score(game=self.game, actor=self.away_coach)

        submit_url = reverse("leaguehub:submit-score", kwargs={"pk": self.game.pk})
        self._login(self.admin)
        response = self.client.post(
            submit_url,
            {
                "home_score": 8,
                "away_score": 2,
                "require_reverification": "on",
                "note": "Correcting official scorebook entry.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.game.refresh_from_db()
        audit = GameScoreAuditEntry.objects.get(game=self.game)
        self.assertEqual(self.game.verification_status, GameVerificationStatus.AWAITING_AWAY_VERIFICATION)
        self.assertEqual(audit.previous_home_score, 3)
        self.assertEqual(audit.new_home_score, 8)
        self.assertTrue(audit.requires_reverification)

    def test_admin_score_entry_defaults_to_verified_final(self):
        submit_url = reverse("leaguehub:submit-score", kwargs={"pk": self.game.pk})
        self._login(self.admin)

        response = self.client.post(
            submit_url,
            {
                "home_score": 9,
                "away_score": 5,
                "note": "Admin entered score directly.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.game.refresh_from_db()
        self.assertEqual(self.game.verification_status, GameVerificationStatus.VERIFIED_FINAL)
        self.assertEqual(self.game.verified_by, self.admin)
        audit = GameScoreAuditEntry.objects.get(game=self.game)
        self.assertFalse(audit.requires_reverification)

    def test_only_verified_final_games_count_toward_standings(self):
        submit_home_score(game=self.game, actor=self.home_coach, home_score=4, away_score=1)
        verify_game_score(game=self.game, actor=self.away_coach)
        submit_home_score(game=self.second_game, actor=self.home_coach, home_score=10, away_score=0)

        standings = calculate_official_standings(league_season=self.league_season)
        home_row = next(row for row in standings if row.team_id == self.home_team.id)
        third_row = next(row for row in standings if row.team_id == self.third_team.id)

        self.assertEqual(home_row.points, 2)
        self.assertEqual(home_row.games_played, 1)
        self.assertEqual(third_row.games_played, 0)

    def test_unverified_games_appear_in_results_and_dashboard(self):
        submit_home_score(game=self.second_game, actor=self.home_coach, home_score=7, away_score=6)

        dashboard_url = reverse(
            "leaguehub:dashboard",
            kwargs={"league_slug": self.league.slug, "season_slug": self.season.slug},
        )
        results_url = reverse(
            "leaguehub:results",
            kwargs={"league_slug": self.league.slug, "season_slug": self.season.slug},
        )

        dashboard_response = self.client.get(dashboard_url)
        results_response = self.client.get(results_url)

        self.assertContains(dashboard_response, "Awaiting Away Verification")
        self.assertContains(dashboard_response, "Expos White")
        self.assertContains(results_response, "Awaiting Away Verification")
        self.assertContains(results_response, "Expos White")

    def test_one_story_per_team_per_game(self):
        story_url = reverse("leaguehub:submit-story", kwargs={"pk": self.game.pk, "team_id": self.home_team.pk})
        self._login(self.home_coach)

        first = self.client.post(story_url, {"headline": "First", "story": "Initial report."})
        second = self.client.post(story_url, {"headline": "Updated", "story": "Updated report."})

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(GameStory.objects.filter(game=self.game, team=self.home_team).count(), 1)
        story = GameStory.objects.get(game=self.game, team=self.home_team)
        self.assertEqual(story.headline, "Updated")

    def test_one_photo_per_team_per_game(self):
        photo_url = reverse("leaguehub:submit-photo", kwargs={"pk": self.game.pk, "team_id": self.home_team.pk})
        self._login(self.home_coach)

        first = self.client.post(
            photo_url,
            {
                "caption": "First photo",
                "image": self._test_image("one.gif"),
            },
        )
        second = self.client.post(
            photo_url,
            {
                "caption": "Second photo",
                "image": self._test_image("two.gif"),
            },
        )

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(GamePhoto.objects.filter(game=self.game, team=self.home_team).count(), 1)
        photo = GamePhoto.objects.get(game=self.game, team=self.home_team)
        self.assertEqual(photo.caption, "Second photo")

    def test_game_detail_story_and_photo_submission_permissions(self):
        story_url = reverse("leaguehub:submit-story", kwargs={"pk": self.game.pk, "team_id": self.home_team.pk})
        photo_url = reverse("leaguehub:submit-photo", kwargs={"pk": self.game.pk, "team_id": self.home_team.pk})

        self._login(self.other_user)
        story_response = self.client.post(story_url, {"headline": "Nope", "story": "Not allowed"})
        photo_response = self.client.post(
            photo_url,
            {
                "caption": "Nope",
                "image": self._test_image("forbidden.gif"),
            },
        )
        self.assertEqual(story_response.status_code, 403)
        self.assertEqual(photo_response.status_code, 403)

        self._login(self.assistant_coach)
        allowed_story = self.client.post(story_url, {"headline": "Allowed", "story": "Assistant report"})
        allowed_photo = self.client.post(
            photo_url,
            {
                "caption": "Assistant photo",
                "image": self._test_image("allowed.gif"),
            },
        )
        self.assertEqual(allowed_story.status_code, 302)
        self.assertEqual(allowed_photo.status_code, 302)

    def test_standings_page_and_dashboard_render_expected_league_season_data(self):
        submit_home_score(game=self.game, actor=self.home_coach, home_score=5, away_score=2)
        verify_game_score(game=self.game, actor=self.away_coach)

        dashboard_url = reverse(
            "leaguehub:dashboard",
            kwargs={"league_slug": self.league.slug, "season_slug": self.season.slug},
        )
        standings_url = reverse(
            "leaguehub:standings",
            kwargs={"league_slug": self.league.slug, "season_slug": self.season.slug},
        )

        dashboard_response = self.client.get(dashboard_url)
        standings_response = self.client.get(standings_url)

        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(standings_response.status_code, 200)
        self.assertContains(dashboard_response, "2026 13U House")
        self.assertContains(dashboard_response, "Verified Final")
        self.assertContains(standings_response, "Official standings derived only from verified final games.")
        self.assertContains(standings_response, "Expos Navy")
        self.assertContains(standings_response, reverse(
            "leaguehub:team-detail",
            kwargs={"league_slug": self.league.slug, "season_slug": self.season.slug, "team_slug": self.home_team.slug},
        ))
        standings = standings_response.context["standings"]
        home_row = next(row for row in standings if row["team_id"] == self.home_team.id)
        self.assertEqual(home_row["points"], 2)

    def test_index_page_lists_active_league_season_dashboards(self):
        response = self.client.get(reverse("leaguehub:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "League Hub")
        self.assertContains(response, "2026 13U House")
        self.assertContains(
            response,
            reverse(
                "leaguehub:dashboard",
                kwargs={"league_slug": self.league.slug, "season_slug": self.season.slug},
            ),
        )
        self.assertContains(response, 'name="season_destination"')

    def test_team_detail_page_and_navigation_selectors_render(self):
        submit_home_score(game=self.game, actor=self.home_coach, home_score=4, away_score=3)
        verify_game_score(game=self.game, actor=self.away_coach)
        url = reverse(
            "leaguehub:team-detail",
            kwargs={"league_slug": self.league.slug, "season_slug": self.season.slug, "team_slug": self.home_team.slug},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.home_team.name)
        self.assertContains(response, "Verified Record")
        self.assertContains(response, 'name="season_destination"')
        self.assertContains(response, 'name="team_destination"')
        self.assertContains(response, reverse("leaguehub:results", kwargs={"league_slug": self.league.slug, "season_slug": self.season.slug}))
        self.assertContains(response, reverse("leaguehub:game-detail", kwargs={"pk": self.game.pk}))

    def test_management_dashboard_requires_staff_and_renders_forms(self):
        url = reverse("leaguehub:manage")

        self._login(self.home_coach)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self._login(self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create league")
        self.assertContains(response, "Create coach account")
        self.assertContains(response, "Create game")

    def test_management_creation_flows_work_without_admin_site(self):
        self._login(self.admin)

        season_response = self.client.post(
            reverse("leaguehub:manage-season-create"),
            {
                "name": "2027 Season",
                "slug": "2027-season",
                "year": 2027,
                "start_date": "",
                "end_date": "",
                "is_active": True,
            },
        )
        self.assertEqual(season_response.status_code, 302)
        self.assertTrue(Season.objects.filter(slug="2027-season").exists())

        coach_response = self.client.post(
            reverse("leaguehub:manage-coach-create"),
            {
                "first_name": "New",
                "last_name": "Coach",
                "email": "newcoach@example.com",
                "username": "",
                "password": "coachpass123",
                "is_staff": False,
            },
        )
        self.assertEqual(coach_response.status_code, 302)
        self.assertTrue(User.objects.filter(email="newcoach@example.com").exists())

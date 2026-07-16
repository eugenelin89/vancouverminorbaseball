from seasons.tests.helpers import (
    Season,
    TestCase,
    ValidationError,
    apps,
    create_season,
    date,
    deactivate_season,
    get_current_season,
    get_or_create_season_team,
    set_current_season,
    transaction,
)


class SeasonModelServiceTests(TestCase):
    def test_seasons_app_is_installed(self):
        self.assertTrue(apps.is_installed("seasons"))

    def test_create_valid_season_normalizes_key(self):
        season = create_season(
            key=" 2026 Spring ", name=" 2026 Spring ", starts_on=date(2026, 4, 1)
        )

        self.assertEqual(season.key, "2026-spring")
        self.assertEqual(season.name, "2026 Spring")
        self.assertTrue(season.is_active)
        self.assertFalse(season.is_current)

    def test_season_key_is_unique(self):
        create_season(key="2026-spring", name="2026 Spring")

        with self.assertRaises(ValidationError):
            create_season(key="2026 Spring", name="Duplicate")

    def test_season_requires_key_name_and_valid_dates(self):
        with self.assertRaises(ValidationError):
            create_season(key="", name="2026 Spring")
        with self.assertRaises(ValidationError):
            create_season(key="2026-spring", name="")
        with self.assertRaises(ValidationError):
            create_season(
                key="2026-spring",
                name="2026 Spring",
                starts_on=date(2026, 8, 1),
                ends_on=date(2026, 4, 1),
            )

    def test_zero_current_seasons_allowed_before_setup(self):
        create_season(key="2026-spring", name="2026 Spring")

        self.assertIsNone(get_current_season())

    def test_set_first_current_season_and_switch_current(self):
        spring = create_season(key="2026-spring", name="2026 Spring")
        summer = create_season(key="2026-summer", name="2026 Summer")

        set_current_season(spring)
        self.assertEqual(get_current_season(), spring)

        set_current_season(summer)
        spring.refresh_from_db()
        summer.refresh_from_db()
        self.assertFalse(spring.is_current)
        self.assertTrue(summer.is_current)
        self.assertEqual(get_current_season(), summer)

    def test_model_validation_prevents_second_current_season(self):
        create_season(key="2026-spring", name="2026 Spring", is_current=True)

        with self.assertRaises(ValidationError):
            with transaction.atomic():
                Season.objects.create(
                    key="2026-summer", name="2026 Summer", is_current=True
                )

    def test_inactive_historical_season_remains_queryable(self):
        season = create_season(key="2026-spring", name="2026 Spring", is_current=True)

        deactivate_season(season)
        season.refresh_from_db()

        self.assertFalse(season.is_active)
        self.assertFalse(season.is_current)
        self.assertEqual(Season.objects.get(pk=season.pk), season)


class SeasonTeamTests(TestCase):
    def setUp(self):
        self.spring = create_season(key="2026-spring", name="2026 Spring")
        self.next_spring = create_season(key="2027-spring", name="2027 Spring")

    def test_create_team_normalizes_values(self):
        team, created = get_or_create_season_team(
            season=self.spring, name="  Dodgers  ", division=" 13U   House "
        )

        self.assertTrue(created)
        self.assertEqual(team.normalized_name, "dodgers")
        self.assertEqual(team.normalized_division, "13u house")

    def test_same_normalized_team_division_reused(self):
        first, created_first = get_or_create_season_team(
            season=self.spring, name="Dodgers", division="13U"
        )
        second, created_second = get_or_create_season_team(
            season=self.spring, name=" dodgers ", division=" 13u "
        )

        self.assertTrue(created_first)
        self.assertFalse(created_second)
        self.assertEqual(first, second)

    def test_same_team_name_in_different_seasons_allowed(self):
        first, _ = get_or_create_season_team(
            season=self.spring, name="Dodgers", division="13U"
        )
        second, _ = get_or_create_season_team(
            season=self.next_spring, name="Dodgers", division="13U"
        )

        self.assertNotEqual(first, second)

    def test_external_identifier_scoped_to_season_and_blank_does_not_conflict(self):
        first, _ = get_or_create_season_team(
            season=self.spring,
            name="Dodgers",
            division="13U",
            external_source="Roster",
            external_identifier="ABC",
        )
        second, created_second = get_or_create_season_team(
            season=self.next_spring,
            name="Dodgers",
            division="13U",
            external_source="Roster",
            external_identifier="ABC",
        )
        blank_one, _ = get_or_create_season_team(
            season=self.spring, name="Expos", division="13U"
        )
        blank_two, _ = get_or_create_season_team(
            season=self.spring, name="Mounties", division="13U"
        )

        self.assertNotEqual(first, second)
        self.assertTrue(created_second)
        self.assertNotEqual(blank_one, blank_two)

    def test_external_identifier_conflict_rejected(self):
        get_or_create_season_team(
            season=self.spring,
            name="Dodgers",
            division="13U",
            external_source="Roster",
            external_identifier="ABC",
        )

        with self.assertRaises(ValidationError):
            get_or_create_season_team(
                season=self.spring,
                name="Expos",
                division="13U",
                external_source="roster",
                external_identifier="abc",
            )

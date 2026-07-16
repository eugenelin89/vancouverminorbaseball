from seasons.tests.helpers import (
    CoachSeasonAssignment,
    PlayerRosterMembership,
    Season,
    SeasonTeam,
    TestCase,
    admin,
)


class SeasonsAdminTests(TestCase):
    def test_models_registered_in_admin(self):
        for model in [
            Season,
            SeasonTeam,
            PlayerRosterMembership,
            CoachSeasonAssignment,
        ]:
            self.assertIn(model, admin.site._registry)

    def test_admin_configuration_is_searchable_and_readonly_timestamps(self):
        for model in [
            Season,
            SeasonTeam,
            PlayerRosterMembership,
            CoachSeasonAssignment,
        ]:
            model_admin = admin.site._registry[model]
            self.assertIn("created_at", model_admin.readonly_fields)
            self.assertIn("updated_at", model_admin.readonly_fields)
            self.assertTrue(model_admin.search_fields)

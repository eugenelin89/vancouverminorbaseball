from players.tests.helpers import (
    MATCH_AMBIGUOUS,
    MATCH_EXACT,
    MATCH_HIGH_CONFIDENCE,
    MATCH_NO_MATCH,
    Player,
    PlayerAlias,
    PlayerImportBatch,
    PlayerSourceIdentifier,
    PlayerSourceRow,
    PlayerTag,
    TestCase,
    active_tags,
    add_source_identifier,
    admin,
    apps,
    assign_tag,
    create_player,
    date,
    find_player_match,
    import_service,
    match_by_identifier,
    match_by_name_and_birthdate,
    players_with_tag,
    remove_tag,
)


class PlayerServiceTests(TestCase):
    def test_create_player_service_creates_canonical_player(self):
        player = create_player(first_name="Eugene", last_name="Lin", division="13U")

        self.assertEqual(player.full_name, "Eugene Lin")
        self.assertEqual(player.division, "13U")

    def test_add_source_identifier_service_normalizes_values(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        identifier = add_source_identifier(
            player,
            source="Registration",
            identifier_type="Registrant ID",
            identifier_value=" ABC-123 ",
        )

        self.assertEqual(identifier.source, "registration")
        self.assertEqual(identifier.identifier_type, "registrant id")
        self.assertEqual(identifier.identifier_value, "abc-123")

    def test_match_by_identifier_returns_exact_match(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        add_source_identifier(player, "registration", "registrant_id", "abc-123")

        result = match_by_identifier("Registration", "Registrant_ID", " ABC-123 ")

        self.assertEqual(result.status, MATCH_EXACT)
        self.assertEqual(result.player, player)

    def test_name_and_birthdate_returns_high_confidence_match(self):
        player = Player.objects.create(
            first_name="Eugene", last_name="Lin", birthdate=date(2012, 5, 1)
        )

        result = match_by_name_and_birthdate("eugene", "lin", date(2012, 5, 1))

        self.assertEqual(result.status, MATCH_HIGH_CONFIDENCE)
        self.assertEqual(result.player, player)

    def test_duplicate_name_candidates_return_ambiguous(self):
        Player.objects.create(
            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
        )
        Player.objects.create(
            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
        )

        result = find_player_match(
            {
                "first_name": "Eugene",
                "last_name": "Lin",
                "birth_year": 2012,
                "division": "13U",
            }
        )

        self.assertEqual(result.status, MATCH_AMBIGUOUS)
        self.assertEqual(len(result.candidates), 2)

    def test_unknown_identity_returns_no_match(self):
        result = find_player_match({"first_name": "Unknown", "last_name": "Player"})

        self.assertEqual(result.status, MATCH_NO_MATCH)
        self.assertIsNone(result.player)

    def test_tag_service_assigns_removes_and_filters_tags(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")

        tag = assign_tag(player, "Strong Arm")

        self.assertEqual(tag.slug, "strong-arm")
        self.assertEqual(list(players_with_tag("strong-arm")), [player])
        self.assertEqual(list(active_tags()), [tag])

        remove_tag(player, "Strong Arm")
        self.assertFalse(players_with_tag("strong-arm").exists())

    def test_import_service_builds_identity_payload(self):
        row = {"First": " Eugene ", "Last": " Lin ", "Division": "13U", "Unused": "x"}
        payload = import_service.build_identity_payload(
            row,
            mapping={
                "first_name": "First",
                "last_name": "Last",
                "division": "Division",
            },
        )

        self.assertEqual(payload["first_name"], "Eugene")
        self.assertEqual(payload["last_name"], "Lin")
        self.assertEqual(payload["division"], "13U")
        self.assertEqual(
            import_service.normalize_header(" First   Name "), "first name"
        )


class PlayerIntegrationTests(TestCase):
    def test_players_app_is_installed(self):
        self.assertTrue(apps.is_installed("players"))

    def test_player_models_are_registered_in_admin(self):
        for model in [
            Player,
            PlayerAlias,
            PlayerImportBatch,
            PlayerSourceIdentifier,
            PlayerSourceRow,
            PlayerTag,
        ]:
            self.assertIn(model, admin.site._registry)

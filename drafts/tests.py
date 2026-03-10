from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Draft, DraftActionType, DraftPlayer, DraftStatus
from .services import (
    change_draft_status,
    create_draft,
    draft_player,
    import_players,
    move_player,
    parse_player_csv,
    remove_player_from_team,
    revert_action,
    trade_players,
)


class DraftServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="commissioner",
            password="secret123",
            is_staff=True,
        )
        self.draft = create_draft(
            name="2026 VCB 13U",
            year=2026,
            division="13U",
            description="Primary 13U draft room",
            created_by=self.user,
            teams=[
                {"name": "Expos Navy", "color": "#102a43"},
                {"name": "Expos Gold", "color": "#f7b733"},
            ],
        )

    def test_csv_preview_only_requires_first_and_last(self):
        upload = SimpleUploadedFile(
            "players.csv",
            b" First , LAST , Position , Pitching Score \nAva,Lopez,SS,82\n,Nguyen,P,77\n",
            content_type="text/csv",
        )
        preview = parse_player_csv(upload)
        self.assertEqual(preview["headers"], ["First", "LAST", "Position", "Pitching Score"])
        self.assertTrue(preview["rows"][0].imported)
        self.assertEqual(preview["rows"][0].cleaned_row["extra_data"]["Position"], "SS")
        self.assertFalse(preview["rows"][1].imported)

    def test_import_draft_move_remove_trade_and_revert(self):
        upload = SimpleUploadedFile(
            "players.csv",
            b"First,Last,Position\nAva,Lopez,SS\nMilo,Chen,P\nNoah,Patel,CF\n",
            content_type="text/csv",
        )
        preview = parse_player_csv(upload)
        result = import_players(draft=self.draft, rows=preview["rows"], actor=self.user)
        self.assertEqual(result["rows_imported"], 3)

        players = list(self.draft.players.order_by("first_name"))
        team_one, team_two = list(self.draft.teams.all())
        change_draft_status(draft=self.draft, new_status=DraftStatus.OPEN, actor=self.user)

        draft_action = draft_player(draft=self.draft, player_id=players[0].id, team_id=team_one.id, actor=self.user)
        move_action = move_player(draft=self.draft, player_id=players[0].id, to_team_id=team_two.id, actor=self.user)
        remove_action = remove_player_from_team(draft=self.draft, player_id=players[0].id, actor=self.user)
        player_two_action = draft_player(draft=self.draft, player_id=players[1].id, team_id=team_one.id, actor=self.user)
        player_three_action = draft_player(draft=self.draft, player_id=players[2].id, team_id=team_two.id, actor=self.user)

        trade_action = trade_players(
            draft=self.draft,
            team_one_id=team_one.id,
            team_two_id=team_two.id,
            team_one_player_ids=[players[1].id],
            team_two_player_ids=[players[2].id],
            actor=self.user,
        )
        players[1].refresh_from_db()
        players[2].refresh_from_db()
        self.assertEqual(players[1].current_team_id, team_two.id)
        self.assertEqual(players[2].current_team_id, team_one.id)

        revert_action(action=trade_action, actor=self.user)
        players[1].refresh_from_db()
        players[2].refresh_from_db()
        self.assertEqual(players[1].current_team_id, team_one.id)
        self.assertEqual(players[2].current_team_id, team_two.id)

        revert_action(action=player_three_action, actor=self.user)
        revert_action(action=player_two_action, actor=self.user)
        revert_action(action=remove_action, actor=self.user)
        revert_action(action=move_action, actor=self.user)
        players[0].refresh_from_db()
        self.assertEqual(players[0].current_team_id, team_one.id)

        revert_action(action=draft_action, actor=self.user)
        players[0].refresh_from_db()
        self.assertIsNone(players[0].current_team_id)

        self.assertTrue(self.draft.actions.filter(action_type=DraftActionType.DRAFT_PICK_REVERTED).exists())


class DraftViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="draft-admin",
            password="secret123",
            is_staff=True,
        )
        self.client.force_login(self.user)
        self.draft = create_draft(
            name="2026 VCB 13U",
            year=2026,
            division="13U",
            description="Primary 13U draft room",
            created_by=self.user,
            teams=[
                {"name": "Expos Navy", "color": "#102a43"},
                {"name": "Expos Gold", "color": "#f7b733"},
            ],
        )

    def test_command_center_renders(self):
        response = self.client.get(reverse("drafts:command-center", kwargs={"slug": self.draft.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Live rosters")

    def test_public_live_board_renders_without_login(self):
        self.client.logout()
        response = self.client.get(reverse("drafts:public-live", kwargs={"slug": self.draft.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public live board")

    def test_import_flow_via_view(self):
        upload = SimpleUploadedFile(
            "players.csv",
            b"First,Last,Position\nAva,Lopez,SS\nMilo,Chen,P\n",
            content_type="text/csv",
        )
        preview_response = self.client.post(
            reverse("drafts:import", kwargs={"slug": self.draft.slug}),
            {"csv_file": upload},
        )
        self.assertEqual(preview_response.status_code, 200)
        self.assertContains(preview_response, "Confirm Import")

        payload = preview_response.context["preview_payload"]
        confirm_response = self.client.post(
            reverse("drafts:import", kwargs={"slug": self.draft.slug}),
            {"preview_payload": payload, "confirm_import": "1"},
            follow=True,
        )
        self.assertEqual(confirm_response.status_code, 200)
        self.assertEqual(DraftPlayer.objects.filter(draft=self.draft).count(), 2)

    def test_assign_player_view_requires_open_draft(self):
        player = DraftPlayer.objects.create(
            draft=self.draft,
            first_name="Ava",
            last_name="Lopez",
            full_name="Ava Lopez",
        )
        team = self.draft.teams.first()
        response = self.client.post(
            reverse("drafts:assign-player", kwargs={"slug": self.draft.slug}),
            {"player_id": player.id, "team_id": team.id},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        player.refresh_from_db()
        self.assertIsNone(player.current_team_id)

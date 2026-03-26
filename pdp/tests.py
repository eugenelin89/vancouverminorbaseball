import io
import zipfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from pdp.models import (
    CoachAssignment,
    DevelopmentGoal,
    DevelopmentLogType,
    ParentChildAccess,
    PlayerDevelopmentLog,
    PlayerProfile,
    Season,
    VisibilityLevel,
)
from pdp.services.accounts import generate_unique_username, provision_player_account
from pdp.services.development import generate_development_roadmap, generate_progress_snapshot
from pdp.services.imports import parse_workbook
from pdp.services.permissions import can_view_log, get_accessible_players, visible_logs_for_user


User = get_user_model()


class AccountProvisioningTests(TestCase):
    def test_generate_unique_username_appends_numeric_suffix(self):
        User.objects.create(username="eugenelin")
        User.objects.create(username="eugenelin2")

        self.assertEqual(generate_unique_username("Eugene", "Lin"), "eugenelin3")

    def test_provision_player_account_uses_hashed_bootstrap_password(self):
        player = PlayerProfile.objects.create(first_name="Eugene", last_name="Lin", email="eugene@example.com")

        result = provision_player_account(player)

        player.refresh_from_db()
        self.assertTrue(result.created)
        self.assertEqual(result.username, "eugenelin")
        self.assertTrue(player.user.check_password("eugenelin"))
        self.assertNotEqual(player.user.password, "eugenelin")
        self.assertTrue(player.must_change_password)


class WorkbookImportParserTests(TestCase):
    def _build_minimal_xlsx(self):
        workbook = io.BytesIO()
        with zipfile.ZipFile(workbook, "w") as archive:
            archive.writestr(
                "xl/workbook.xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
                 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
                    <sheets><sheet name="Testing" sheetId="1" r:id="rId1"/></sheets>
                </workbook>""",
            )
            archive.writestr(
                "xl/_rels/workbook.xml.rels",
                """<?xml version="1.0" encoding="UTF-8"?>
                <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
                    <Relationship Id="rId1"
                        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
                        Target="worksheets/sheet1.xml"/>
                </Relationships>""",
            )
            archive.writestr(
                "xl/worksheets/sheet1.xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
                    <sheetData>
                        <row r="1">
                            <c r="A1" t="inlineStr"><is><t>Full Name</t></is></c>
                            <c r="B1" t="inlineStr"><is><t>Exit Velocity Avg</t></is></c>
                        </row>
                        <row r="2">
                            <c r="A2" t="inlineStr"><is><t>Eugene Lin</t></is></c>
                            <c r="B2"><v>82.1</v></c>
                        </row>
                    </sheetData>
                </worksheet>""",
            )
        workbook.seek(0)
        return workbook.getvalue()

    def test_parse_csv_workbook_returns_sheet_preview(self):
        upload = SimpleUploadedFile("players.csv", b"First,Last,Bat Speed\nEugene,Lin,72\n")

        preview = parse_workbook(upload)

        self.assertEqual(preview["sheet_count"], 1)
        self.assertEqual(preview["sheets"][0]["headers"], ["First", "Last", "Bat Speed"])
        self.assertEqual(preview["rows_by_sheet"]["Sheet1"][0]["Bat Speed"], "72")

    def test_parse_xlsx_workbook_returns_sheet_preview(self):
        upload = SimpleUploadedFile(
            "players.xlsx",
            self._build_minimal_xlsx(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        preview = parse_workbook(upload)

        self.assertEqual(preview["sheet_count"], 1)
        self.assertEqual(preview["sheets"][0]["name"], "Testing")
        self.assertEqual(preview["rows_by_sheet"]["Testing"][0]["Full Name"], "Eugene Lin")
        self.assertEqual(preview["rows_by_sheet"]["Testing"][0]["Exit Velocity Avg"], "82.1")


class PermissionAndDevelopmentTests(TestCase):
    def setUp(self):
        self.season = Season.objects.create(name="2026 Season", slug="2026-season", year=2026, is_active=True)
        self.player_user = User.objects.create_user(username="player1", password="testpass")
        self.coach_user = User.objects.create_user(username="coach1", password="testpass")
        self.parent_user = User.objects.create_user(username="parent1", password="testpass")
        self.player = PlayerProfile.objects.create(
            user=self.player_user,
            first_name="Eugene",
            last_name="Lin",
        )
        CoachAssignment.objects.create(coach=self.coach_user, player=self.player, season=self.season)
        ParentChildAccess.objects.create(parent=self.parent_user, player=self.player, relationship_label="Parent")

    def test_visibility_rules_limit_logs_by_role(self):
        player_log = PlayerDevelopmentLog.objects.create(
            player=self.player,
            season=self.season,
            author=self.coach_user,
            log_type=DevelopmentLogType.PRACTICE,
            title="Player-facing note",
            note="Keep attacking balance through every rep.",
            visibility=VisibilityLevel.PLAYER,
            occurred_at="2026-03-26T10:00:00Z",
        )
        coach_only_log = PlayerDevelopmentLog.objects.create(
            player=self.player,
            season=self.season,
            author=self.coach_user,
            log_type=DevelopmentLogType.PRACTICE,
            title="Coach note",
            note="Internal cueing note.",
            visibility=VisibilityLevel.COACH,
            occurred_at="2026-03-26T11:00:00Z",
        )

        self.assertTrue(can_view_log(self.coach_user, coach_only_log))
        self.assertFalse(can_view_log(self.parent_user, coach_only_log))
        self.assertFalse(can_view_log(self.player_user, coach_only_log))
        self.assertTrue(can_view_log(self.player_user, player_log))
        self.assertEqual(list(get_accessible_players(self.coach_user)), [self.player])
        self.assertEqual(list(visible_logs_for_user(self.parent_user)), [player_log])

    def test_snapshot_and_roadmap_generation_create_records(self):
        DevelopmentGoal.objects.create(
            player=self.player,
            season=self.season,
            title="Improve bat speed",
            category="Hitting",
            description="Create more fast, clean barrel turns.",
        )

        snapshot = generate_progress_snapshot(self.player, season=self.season)
        roadmap = generate_development_roadmap(self.player, season=self.season)

        self.assertIn("Next step", snapshot.summary)
        self.assertTrue(roadmap.items.exists())

# Create your tests here.

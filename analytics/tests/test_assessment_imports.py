from decimal import Decimal
from io import BytesIO

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from openpyxl import Workbook

from analytics.models import (
    ASSESSMENT_IMPORT_ROW_MATCHED,
    ASSESSMENT_IMPORT_ROW_SKIPPED,
    ASSESSMENT_IMPORT_ROW_UNMATCHED,
    ASSESSMENT_IMPORT_STATUS_COMMITTED,
    ASSESSMENT_STATUS_COMMITTED,
    AssessmentEvent,
    AssessmentImportBatch,
    AssessmentImportTemplate,
    AssessmentMetricDefinition,
    AssessmentScoringProfile,
    AssessmentTemplate,
    AssessmentTemplateMetric,
    AssessmentValue,
    PlayerAssessment,
)
from analytics.services.assessment_import_service import (
    commit_assessment_import_batch,
    create_assessment_import_batch,
    ensure_2026_13u_assessment_configuration,
    resolve_assessment_import_row,
)
from analytics.tests.helpers import (
    Player,
    TestCase,
    User,
    attach_player_to_season,
    create_season,
)


def assessment_workbook(rows):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Assessment Data"
    worksheet.append(["", "Athleticism Evaluation", ""])
    worksheet.append(["Name", "Home to 1st", "Broad Jump"])
    for row in rows:
        worksheet.append(row)
    pitching = workbook.create_sheet("Pitching Data ")
    pitching.append([])
    pitching.append(["Name", "Velocity Avg.", "Velocity Max"])
    for row in rows:
        pitching.append([row[0], 50, 52])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


class AssessmentImportTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff", password="test", is_staff=True
        )
        self.user = User.objects.create_user(username="regular", password="test")
        self.season = create_season(name="Spring 2026", key="spring-2026")
        ensure_2026_13u_assessment_configuration()
        self.template = AssessmentTemplate.objects.get(key="2026-13u-house-assessment")
        self.import_template = AssessmentImportTemplate.objects.get(
            key="2026-13u-house-assessment-xlsx"
        )
        self.scoring_profile = AssessmentScoringProfile.objects.get(
            key="2026-13u-house-assessment"
        )
        self.event = AssessmentEvent.objects.create(
            name="Spring 2026 13U Assessment",
            season=self.season,
            division="13U House",
            template=self.template,
            scoring_profile=self.scoring_profile,
        )
        self.player = Player.objects.create(first_name="Alex", last_name="Example")
        attach_player_to_season(
            self.player, self.season, team_name="Yankees", division="13U House"
        )

    def upload(self, rows):
        return SimpleUploadedFile(
            "assessment.xlsx",
            assessment_workbook(rows),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_feature_flag_blocks_assessment_routes_when_disabled(self):
        self.client.force_login(self.staff)
        with override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False):
            response = self.client.get(reverse("analytics:assessment-event-list"))
        self.assertEqual(response.status_code, 404)

    def test_staff_required_for_assessment_routes(self):
        self.client.force_login(self.user)
        with override_settings(ANALYTICS_ASSESSMENTS_ENABLED=True):
            response = self.client.get(reverse("analytics:assessment-event-list"))
        self.assertEqual(response.status_code, 403)

    def test_valid_workbook_preview_matches_existing_player(self):
        batch = create_assessment_import_batch(
            file_obj=self.upload([["Alex Example", 4.1, 82]]),
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
        )

        row = batch.rows.get()
        self.assertEqual(row.status, ASSESSMENT_IMPORT_ROW_MATCHED)
        self.assertEqual(row.player, self.player)
        self.assertEqual(len(row.values_snapshot), 4)

    def test_commit_creates_player_assessment_values(self):
        batch = create_assessment_import_batch(
            file_obj=self.upload([["Alex Example", 4.1, 82]]),
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
        )

        result = commit_assessment_import_batch(batch=batch, actor=self.staff)

        self.assertEqual(result.created, 1)
        batch.refresh_from_db()
        self.assertEqual(batch.status, ASSESSMENT_IMPORT_STATUS_COMMITTED)
        assessment = PlayerAssessment.objects.get(player=self.player, event=self.event)
        self.assertEqual(assessment.status, ASSESSMENT_STATUS_COMMITTED)
        self.assertEqual(
            AssessmentValue.objects.filter(player_assessment=assessment).count(), 4
        )

    def test_commit_blocks_unmatched_rows_until_resolved_or_skipped(self):
        batch = create_assessment_import_batch(
            file_obj=self.upload([["Unknown Player", 4.1, 82]]),
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
        )
        row = batch.rows.get()
        self.assertEqual(row.status, ASSESSMENT_IMPORT_ROW_UNMATCHED)

        with self.assertRaises(ValidationError):
            commit_assessment_import_batch(batch=batch, actor=self.staff)

        resolve_assessment_import_row(row=row, player=None, skip=True)
        row.refresh_from_db()
        self.assertEqual(row.status, ASSESSMENT_IMPORT_ROW_SKIPPED)
        result = commit_assessment_import_batch(batch=batch, actor=self.staff)
        self.assertEqual(result.skipped, 1)

    def test_commit_blocks_manual_override_overwrite(self):
        batch = create_assessment_import_batch(
            file_obj=self.upload([["Alex Example", 4.1, 82]]),
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
        )
        metric = AssessmentMetricDefinition.objects.get(key="home_to_1st")
        template_metric = AssessmentTemplateMetric.objects.get(
            template=self.template, metric=metric
        )
        assessment = PlayerAssessment.objects.create(
            player=self.player,
            event=self.event,
            status=ASSESSMENT_STATUS_COMMITTED,
        )
        AssessmentValue.objects.create(
            player_assessment=assessment,
            template_metric=template_metric,
            numeric_value=Decimal("9.999"),
            is_manual_override=True,
        )

        with self.assertRaises(ValidationError):
            commit_assessment_import_batch(batch=batch, actor=self.staff)

    def test_non_staff_cannot_commit_batch(self):
        batch = create_assessment_import_batch(
            file_obj=self.upload([["Alex Example", 4.1, 82]]),
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
        )
        with self.assertRaises(PermissionDenied):
            commit_assessment_import_batch(batch=batch, actor=self.user)

    def test_bootstrap_command_is_idempotent(self):
        first_count = AssessmentMetricDefinition.objects.count()
        ensure_2026_13u_assessment_configuration()
        self.assertEqual(AssessmentMetricDefinition.objects.count(), first_count)

    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=True)
    def test_upload_view_creates_preview_batch(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("analytics:assessment-import-new"),
            {
                "event": self.event.pk,
                "import_template": self.import_template.pk,
                "workbook": self.upload([["Alex Example", 4.1, 82]]),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(AssessmentImportBatch.objects.count(), 1)

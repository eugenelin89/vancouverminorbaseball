from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import override_settings
from django.urls import reverse

from analytics.models import (
    ASSESSMENT_IMPORT_ROW_MATCHED,
    ASSESSMENT_IMPORT_STATUS_COMMITTED,
    ASSESSMENT_STATUS_COMMITTED,
    AssessmentImportBatch,
    AssessmentMetricDefinition,
    AssessmentTemplateMetric,
    AssessmentValue,
    PlayerAssessment,
)
from analytics.services.assessment_import_service import (
    acknowledge_assessment_import_warnings,
    commit_assessment_import_batch,
    correct_assessment_value,
    create_assessment_import_batch,
    ensure_2026_13u_assessment_configuration,
)
from analytics.tests.assessment_test_helpers import AssessmentTestMixin
from analytics.tests.helpers import TestCase


class AssessmentImportIntegrationTests(AssessmentTestMixin, TestCase):
    def create_batch(self, upload=None):
        return create_assessment_import_batch(
            file_obj=upload or self.valid_upload(),
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
        )

    def test_valid_preview_matches_without_writing_assessments(self):
        batch = self.create_batch()

        row = batch.rows.get()
        self.assertEqual(row.status, ASSESSMENT_IMPORT_ROW_MATCHED)
        self.assertEqual(row.player, self.player)
        self.assertEqual(PlayerAssessment.objects.count(), 0)
        self.assertEqual(AssessmentValue.objects.count(), 0)

    def test_commit_creates_values_and_preserves_rating_scale(self):
        batch = self.acknowledge(self.create_batch())

        result = commit_assessment_import_batch(batch=batch, actor=self.staff)

        self.assertEqual(result.created, 1)
        batch.refresh_from_db()
        self.assertEqual(batch.status, ASSESSMENT_IMPORT_STATUS_COMMITTED)
        assessment = PlayerAssessment.objects.get(player=self.player, event=self.event)
        self.assertEqual(assessment.status, ASSESSMENT_STATUS_COMMITTED)
        rating = assessment.values.get(template_metric__metric__key="athletic_stance")
        self.assertEqual(rating.rating_value, Decimal("2"))
        self.assertEqual(rating.rating_scale_min, Decimal("1"))
        self.assertEqual(rating.rating_scale_max, Decimal("3"))

    def test_warning_acknowledgement_is_required_and_stale_token_is_rejected(self):
        batch = self.create_batch()
        self.assertTrue(batch.required_warning_codes)

        with self.assertRaises(ValidationError):
            commit_assessment_import_batch(batch=batch, actor=self.staff)
        with self.assertRaises(ValidationError):
            acknowledge_assessment_import_warnings(
                batch=batch, actor=self.staff, token="stale"
            )

        batch.refresh_from_db()
        acknowledge_assessment_import_warnings(
            batch=batch,
            actor=self.staff,
            token=batch.acknowledgement_token,
        )
        commit_assessment_import_batch(batch=batch, actor=self.staff)

    def test_non_staff_cannot_commit_or_acknowledge(self):
        batch = self.create_batch()
        with self.assertRaises(PermissionDenied):
            acknowledge_assessment_import_warnings(
                batch=batch,
                actor=self.user,
                token=batch.acknowledgement_token,
            )
        with self.assertRaises(PermissionDenied):
            commit_assessment_import_batch(batch=batch, actor=self.user)

    def test_commit_is_atomic_when_metric_write_fails(self):
        batch = self.acknowledge(self.create_batch())
        with patch(
            "analytics.services.assessment_import_service._apply_metric_change",
            side_effect=ValidationError("synthetic failure"),
        ):
            with self.assertRaises(ValidationError):
                commit_assessment_import_batch(batch=batch, actor=self.staff)

        self.assertEqual(PlayerAssessment.objects.count(), 0)
        self.assertEqual(AssessmentValue.objects.count(), 0)
        batch.refresh_from_db()
        self.assertNotEqual(batch.status, ASSESSMENT_IMPORT_STATUS_COMMITTED)

    def test_approved_manual_correction_records_audit_history(self):
        batch = self.acknowledge(self.create_batch())
        commit_assessment_import_batch(batch=batch, actor=self.staff)
        value = AssessmentValue.objects.get(
            player_assessment__player=self.player,
            template_metric__metric__key="home_to_1st",
        )

        corrected = correct_assessment_value(
            assessment_value=value,
            actor=self.staff,
            reason="Verified timing correction",
            new_value="4.2",
        )

        self.assertEqual(corrected.numeric_value, Decimal("4.2"))
        self.assertTrue(corrected.is_manual_override)
        self.assertEqual(corrected.corrections.count(), 1)

    def test_bootstrap_is_idempotent_and_ratings_are_one_to_three(self):
        first_count = AssessmentMetricDefinition.objects.count()
        ensure_2026_13u_assessment_configuration()
        self.assertEqual(AssessmentMetricDefinition.objects.count(), first_count)
        rating_metrics = AssessmentTemplateMetric.objects.filter(
            template=self.template,
            value_type="rating",
        )
        self.assertTrue(rating_metrics.exists())
        self.assertFalse(rating_metrics.exclude(rating_scale_min=1).exists())
        self.assertFalse(rating_metrics.exclude(rating_scale_max=3).exists())


class AssessmentRouteTests(AssessmentTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.batch = create_assessment_import_batch(
            file_obj=self.valid_upload(),
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
        )

    def assessment_urls(self):
        return [
            reverse("analytics:assessment-event-list"),
            reverse("analytics:assessment-event-detail", args=[self.event.pk]),
            reverse("analytics:assessment-import-list"),
            reverse("analytics:assessment-import-new"),
            reverse("analytics:assessment-import-preview", args=[self.batch.pk]),
            reverse("analytics:assessment-import-resolve", args=[self.batch.pk]),
            reverse("analytics:assessment-import-confirm", args=[self.batch.pk]),
            reverse("analytics:assessment-import-detail", args=[self.batch.pk]),
        ]

    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False)
    def test_all_assessment_routes_are_hidden_when_disabled(self):
        self.client.force_login(self.staff)
        for url in self.assessment_urls():
            self.assertEqual(self.client.get(url).status_code, 404, url)

    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=True)
    def test_non_staff_is_denied_and_staff_can_access(self):
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.get(reverse("analytics:assessment-event-list")).status_code,
            403,
        )
        self.client.force_login(self.staff)
        self.assertEqual(
            self.client.get(reverse("analytics:assessment-event-list")).status_code,
            200,
        )

    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False)
    def test_command_center_navigation_is_hidden_when_disabled(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("analytics:command-center"))
        self.assertNotContains(response, "Assessment Events")

    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False)
    def test_player_profile_does_not_query_or_show_assessments_when_disabled(self):
        self.client.force_login(self.staff)
        with patch(
            "analytics.views.assessment_records_for_player"
        ) as assessment_records:
            response = self.client.get(
                reverse(
                    "analytics:player-profile",
                    kwargs={"player_id": self.player.pk},
                )
            )
        self.assertEqual(response.status_code, 200)
        assessment_records.assert_not_called()
        self.assertNotContains(response, "Assessment Events")

    def test_existing_evaluation_pages_work_with_assessment_flag_off_and_on(self):
        self.client.force_login(self.staff)
        for enabled in (False, True):
            with override_settings(ANALYTICS_ASSESSMENTS_ENABLED=enabled):
                self.assertEqual(
                    self.client.get(reverse("analytics:evaluation-list")).status_code,
                    200,
                )
                self.assertEqual(
                    self.client.get(reverse("analytics:assessment-list")).status_code,
                    200,
                )

    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=True)
    def test_upload_view_creates_preview_batch(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("analytics:assessment-import-new"),
            {
                "event": self.event.pk,
                "import_template": self.import_template.pk,
                "workbook": self.valid_upload(),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AssessmentImportBatch.objects.count(), 2)


class AssessmentAdminSafetyTests(AssessmentTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.superuser = get_user_model().objects.create_superuser(
            username="assessment.admin",
            password="test",
            email="admin@example.invalid",
        )
        self.client.force_login(self.superuser)

    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False)
    def test_assessment_models_are_hidden_from_admin_navigation_when_disabled(self):
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Assessment templates")

    @override_settings(ANALYTICS_ASSESSMENTS_ENABLED=False)
    def test_direct_admin_url_remains_superuser_protected_when_disabled(self):
        response = self.client.get(
            reverse(
                "admin:analytics_assessmenttemplate_change",
                args=[self.template.pk],
            )
        )
        self.assertEqual(response.status_code, 200)

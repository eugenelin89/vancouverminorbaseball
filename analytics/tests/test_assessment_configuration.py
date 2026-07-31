from django.core.exceptions import ValidationError
from django.test import override_settings
from django.urls import reverse

from analytics.models import (
    AssessmentEvent,
    AssessmentImportTemplate,
    AssessmentMetricDefinition,
    AssessmentScoringProfile,
    AssessmentTemplate,
    AssessmentTemplateMetric,
    PlayerAssessment,
)
from analytics.services.assessment_import_service import (
    create_assessment_import_batch,
    default_2026_13u_config,
    ensure_2026_13u_assessment_configuration,
)
from analytics.tests.assessment_test_helpers import (
    AssessmentTestMixin,
)
from analytics.tests.helpers import TestCase


class AssessmentConfigurationTests(TestCase):
    def test_dry_run_writes_nothing_and_reports_safety_configuration(self):
        plan = ensure_2026_13u_assessment_configuration(dry_run=True)
        self.assertEqual(AssessmentTemplate.objects.count(), 0)
        self.assertEqual(AssessmentMetricDefinition.objects.count(), 0)
        self.assertEqual(PlayerAssessment.objects.count(), 0)
        self.assertEqual(plan["required_sheets"], ["Assessment Data"])
        self.assertEqual(plan["optional_sheets"], ["Pitching Data"])
        self.assertTrue(all("zero_policy" in metric for metric in plan["metrics"]))
        self.assertEqual(plan["sheets"][0]["header_row"], 2)
        self.assertIn("Athletic Stance", plan["sheets"][0]["required_headers"])

    def test_first_run_creates_and_second_run_is_idempotent(self):
        ensure_2026_13u_assessment_configuration()
        counts = (
            AssessmentTemplate.objects.count(),
            AssessmentMetricDefinition.objects.count(),
            AssessmentTemplateMetric.objects.count(),
            AssessmentImportTemplate.objects.count(),
            AssessmentScoringProfile.objects.count(),
        )
        ensure_2026_13u_assessment_configuration()
        self.assertEqual(
            counts,
            (
                AssessmentTemplate.objects.count(),
                AssessmentMetricDefinition.objects.count(),
                AssessmentTemplateMetric.objects.count(),
                AssessmentImportTemplate.objects.count(),
                AssessmentScoringProfile.objects.count(),
            ),
        )
        self.assertEqual(PlayerAssessment.objects.count(), 0)

    def test_conflicting_existing_rating_scale_is_detected(self):
        ensure_2026_13u_assessment_configuration()
        metric = AssessmentTemplateMetric.objects.get(
            template__key="2026-13u-house-assessment",
            metric__key="athletic_stance",
        )
        metric.rating_scale_max = 5
        metric.save()
        with self.assertRaises(ValidationError):
            ensure_2026_13u_assessment_configuration()
        metric.refresh_from_db()
        self.assertEqual(metric.rating_scale_max, 5)

        plan = ensure_2026_13u_assessment_configuration(dry_run=True)
        state = next(
            state
            for state in plan["states"]
            if state["object"] == "template_metric:athletic_stance"
        )
        self.assertEqual(state["state"], "conflict")
        self.assertIn("rating_scale_max", state["conflicts"])

    def test_locked_conflicting_configuration_is_never_rewritten(self):
        ensure_2026_13u_assessment_configuration()
        template = AssessmentTemplate.objects.get(key="2026-13u-house-assessment")
        template.is_locked = True
        template.save()
        metric = template.template_metrics.get(metric__key="athletic_stance")
        AssessmentTemplateMetric.objects.filter(pk=metric.pk).update(rating_scale_max=5)
        with self.assertRaises(ValidationError):
            ensure_2026_13u_assessment_configuration()
        metric.refresh_from_db()
        self.assertEqual(metric.rating_scale_max, 5)


class AssessmentCompatibilityTests(AssessmentTestMixin, TestCase):
    def test_wrong_import_template_is_rejected_by_form_and_service(self):
        other_template = AssessmentTemplate.objects.create(
            key="other-template", name="Other", version=1
        )
        wrong_import = AssessmentImportTemplate.objects.create(
            key="wrong-import",
            name="Wrong Import",
            version=1,
            assessment_template=other_template,
            config=default_2026_13u_config(),
        )
        with self.assertRaises(ValidationError):
            create_assessment_import_batch(
                file_obj=self.valid_upload(),
                event=self.event,
                import_template=wrong_import,
                uploaded_by=self.staff,
            )

        self.client.force_login(self.staff)
        with override_settings(ANALYTICS_ASSESSMENTS_ENABLED=True):
            response = self.client.post(
                reverse("analytics:assessment-import-new"),
                {
                    "event": self.event.pk,
                    "import_template": wrong_import.pk,
                    "workbook": self.valid_upload(),
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice")

    def test_scoring_profile_must_match_event_template(self):
        other_template = AssessmentTemplate.objects.create(
            key="other-template", name="Other", version=1
        )
        wrong_profile = AssessmentScoringProfile.objects.create(
            key="other-profile",
            name="Other Profile",
            version=1,
            assessment_template=other_template,
        )
        event = AssessmentEvent(
            name="Invalid Event",
            season=self.season,
            template=self.template,
            scoring_profile=wrong_profile,
        )
        with self.assertRaises(ValidationError):
            event.save()

    def test_batch_snapshot_is_authoritative_and_checksum_is_persisted(self):
        batch = create_assessment_import_batch(
            file_obj=self.valid_upload(),
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
        )
        self.assertTrue(batch.config_checksum)
        self.assertEqual(batch.config_snapshot, self.import_template.config)
        self.assertEqual(
            batch.preview_snapshot["config_checksum"], batch.config_checksum
        )

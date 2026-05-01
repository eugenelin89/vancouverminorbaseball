from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from scholarships.models import ScholarshipApplicantProfile, ScholarshipApplication, ScholarshipApplicationStatus, ScholarshipCycle


User = get_user_model()


class ScholarshipFlowTests(TestCase):
    def setUp(self):
        today = timezone.localdate()
        self.cycle = ScholarshipCycle.objects.create(
            title="18U Graduating Player Scholarship Program",
            year=today.year,
            status="open",
            application_open_date=today - timedelta(days=7),
            application_deadline=today + timedelta(days=14),
        )
        self.signup_url = reverse("scholarships:signup")
        self.apply_url = reverse("scholarships:apply")

    def signup_and_login(self):
        response = self.client.post(
            self.signup_url,
            {
                "first_name": "Eugene",
                "last_name": "Lin",
                "email": "eugene@example.com",
                "phone": "555-1234",
                "password1": "secure-test-pass-123",
                "password2": "secure-test-pass-123",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="eugene@example.com").exists())
        return ScholarshipApplicantProfile.objects.get(email="eugene@example.com")

    def application_payload(self, submit=False):
        statement = " ".join(["growth"] * 260)
        return {
            "player_full_name": "Eugene Lin",
            "date_of_birth": "2008-01-01",
            "vcb_team_or_program": "VCB 18U AAA",
            "primary_positions": "C, IF",
            "years_participated_in_vcb_programs": "5",
            "pathway_college_university": "on",
            "institution_or_program_name": "UBC",
            "intended_field_of_study_or_training": "Kinesiology",
            "nomination_statement": statement,
            "reference_1_name": "Coach A",
            "reference_1_role_relationship": "Head Coach",
            "reference_1_email": "coach@example.com",
            "reference_1_phone": "555-1111",
            "reference_2_name": "",
            "reference_2_role_relationship": "",
            "reference_2_email": "",
            "reference_2_phone": "",
            "confirm_information_is_accurate": "on" if submit else "",
            "confirm_good_standing": "on" if submit else "",
            "confirm_decisions_are_final": "on" if submit else "",
            "consent_to_reference_checks": "on" if submit else "",
            "nominator_signature": "Eugene Lin",
            "signature_date": str(timezone.localdate()),
            "submit_action": "submit" if submit else "draft",
        }

    def test_signup_flow_creates_profile(self):
        profile = self.signup_and_login()
        self.assertEqual(profile.full_name, "Eugene Lin")

    def test_application_creation_as_draft(self):
        profile = self.signup_and_login()
        response = self.client.post(self.apply_url, data=self.application_payload(submit=False), follow=True)
        self.assertEqual(response.status_code, 200)
        application = ScholarshipApplication.objects.get(applicant=profile, cycle=self.cycle)
        self.assertEqual(application.status, ScholarshipApplicationStatus.DRAFT)
        self.assertEqual(application.references.count(), 1)

    def test_one_application_per_cycle_rule(self):
        self.signup_and_login()
        self.client.post(self.apply_url, data=self.application_payload(submit=False))
        second_response = self.client.get(self.apply_url, follow=True)
        self.assertContains(second_response, "Eugene Lin")
        self.assertEqual(ScholarshipApplication.objects.count(), 1)

    def test_closed_cycle_restriction(self):
        self.signup_and_login()
        self.cycle.status = "closed"
        self.cycle.save()
        response = self.client.get(self.apply_url, follow=True)
        self.assertContains(response, "Applications are not open right now.")

    def test_required_declarations_on_submit(self):
        self.signup_and_login()
        response = self.client.post(self.apply_url, data=self.application_payload(submit=True) | {
            "confirm_information_is_accurate": "",
            "confirm_good_standing": "",
            "confirm_decisions_are_final": "",
            "consent_to_reference_checks": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You must confirm the information is accurate.")

    def test_submitted_application_cannot_be_edited(self):
        profile = self.signup_and_login()
        self.client.post(self.apply_url, data=self.application_payload(submit=True), follow=True)
        application = ScholarshipApplication.objects.get(applicant=profile, cycle=self.cycle)
        response = self.client.get(reverse("scholarships:application-edit", kwargs={"pk": application.pk}), follow=True)
        self.assertContains(response, "can no longer be edited")

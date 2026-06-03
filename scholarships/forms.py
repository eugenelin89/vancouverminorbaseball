from django import forms
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from scholarships.models import (
    ScholarshipApplicantProfile,
    ScholarshipApplication,
    ScholarshipApplicationStatus,
    ScholarshipCycle,
    ScholarshipReference,
)


User = get_user_model()


class ApplicantSignupForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=40, required=False)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username__iexact=email).exists() or ScholarshipApplicantProfile.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    @transaction.atomic
    def save(self, request=None):
        email = self.cleaned_data["email"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["first_name"].strip(),
            last_name=self.cleaned_data["last_name"].strip(),
        )
        profile = ScholarshipApplicantProfile.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            email=email,
            phone=self.cleaned_data.get("phone", "").strip(),
        )
        if request is not None:
            authenticated = authenticate(request, username=email, password=self.cleaned_data["password1"])
            if authenticated is not None:
                login(request, authenticated)
        return profile


class ApplicantLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()


class ScholarshipApplicationForm(forms.ModelForm):
    reference_1_name = forms.CharField(max_length=180)
    reference_1_role_relationship = forms.CharField(max_length=180)
    reference_1_email = forms.EmailField()
    reference_1_phone = forms.CharField(max_length=40, required=False)

    reference_2_name = forms.CharField(max_length=180, required=False)
    reference_2_role_relationship = forms.CharField(max_length=180, required=False)
    reference_2_email = forms.EmailField(required=False)
    reference_2_phone = forms.CharField(max_length=40, required=False)

    submit_action = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = ScholarshipApplication
        fields = [
            "player_full_name",
            "date_of_birth",
            "vcb_team_or_program",
            "primary_positions",
            "years_participated_in_vcb_programs",
            "pathway_college_university",
            "pathway_trade_vocational_training",
            "pathway_recognized_training_program",
            "pathway_undecided",
            "institution_or_program_name",
            "intended_field_of_study_or_training",
            "nomination_statement",
            "confirm_information_is_accurate",
            "confirm_good_standing",
            "confirm_decisions_are_final",
            "consent_to_reference_checks",
            "nominator_signature",
            "signature_date",
            "transcript_or_report_card",
            "supporting_documents",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "signature_date": forms.DateInput(attrs={"type": "date"}),
            "nomination_statement": forms.Textarea(attrs={"rows": 12}),
        }

    def __init__(self, *args, **kwargs):
        self.applicant = kwargs.pop("applicant", None)
        self.cycle = kwargs.pop("cycle", None)
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            if self.applicant:
                self.fields["player_full_name"].initial = self.applicant.full_name
            self.fields["signature_date"].initial = timezone.localdate()

        references = []
        if self.instance.pk:
            references = list(self.instance.references.order_by("display_order"))
        if references:
            first = references[0]
            self.fields["reference_1_name"].initial = first.name
            self.fields["reference_1_role_relationship"].initial = first.role_relationship
            self.fields["reference_1_email"].initial = first.email
            self.fields["reference_1_phone"].initial = first.phone
        if len(references) > 1:
            second = references[1]
            self.fields["reference_2_name"].initial = second.name
            self.fields["reference_2_role_relationship"].initial = second.role_relationship
            self.fields["reference_2_email"].initial = second.email
            self.fields["reference_2_phone"].initial = second.phone

    def clean_nomination_statement(self):
        statement = self.cleaned_data["nomination_statement"].strip()
        words = [word for word in statement.split() if word.strip()]
        if len(words) < 200:
            raise ValidationError("Applicant statement must be at least 200 words.")
        if len(words) > 700:
            raise ValidationError("Applicant statement must be no more than 700 words.")
        return statement

    def clean(self):
        cleaned_data = super().clean()
        second_reference_values = [
            cleaned_data.get("reference_2_name"),
            cleaned_data.get("reference_2_role_relationship"),
            cleaned_data.get("reference_2_email"),
            cleaned_data.get("reference_2_phone"),
        ]
        if any(value for value in second_reference_values):
            for field_name in ["reference_2_name", "reference_2_role_relationship", "reference_2_email"]:
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, "Complete all required fields for the optional second reference.")

        if cleaned_data.get("submit_action") == "submit":
            required_checks = {
                "confirm_information_is_accurate": "You must confirm the information is accurate.",
                "confirm_good_standing": "You must confirm good standing with Vancouver Community Baseball.",
                "confirm_decisions_are_final": "You must acknowledge that scholarship decisions are final.",
                "consent_to_reference_checks": "You must consent to reference checks.",
            }
            for field_name, message in required_checks.items():
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, message)

        signature_date = cleaned_data.get("signature_date")
        if signature_date and self.cycle and signature_date > self.cycle.application_deadline:
            self.add_error("signature_date", "Signature date cannot be after the application deadline.")
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        application = super().save(commit=False)
        if self.applicant is not None:
            application.applicant = self.applicant
        if self.cycle is not None:
            application.cycle = self.cycle
        if self.cleaned_data.get("submit_action") == "submit":
            application.status = ScholarshipApplicationStatus.SUBMITTED
            if not application.submitted_at:
                application.submitted_at = timezone.now()
            if not application.locked_at:
                application.locked_at = timezone.now()
        else:
            application.status = ScholarshipApplicationStatus.DRAFT
            application.locked_at = None
        if commit:
            application.save()
            self._save_references(application)
        return application

    def _save_references(self, application):
        application.references.all().delete()
        ScholarshipReference.objects.create(
            application=application,
            display_order=1,
            name=self.cleaned_data["reference_1_name"].strip(),
            role_relationship=self.cleaned_data["reference_1_role_relationship"].strip(),
            email=self.cleaned_data["reference_1_email"].strip().lower(),
            phone=self.cleaned_data.get("reference_1_phone", "").strip(),
        )
        if self.cleaned_data.get("reference_2_name"):
            ScholarshipReference.objects.create(
                application=application,
                display_order=2,
                name=self.cleaned_data["reference_2_name"].strip(),
                role_relationship=self.cleaned_data["reference_2_role_relationship"].strip(),
                email=self.cleaned_data["reference_2_email"].strip().lower(),
                phone=self.cleaned_data.get("reference_2_phone", "").strip(),
            )


class StaffApplicationFilterForm(forms.Form):
    cycle = forms.ModelChoiceField(queryset=ScholarshipCycle.objects.order_by("-year"), required=False)
    status = forms.ChoiceField(
        choices=[("", "All statuses"), *ScholarshipApplicationStatus.choices],
        required=False,
    )
    search = forms.CharField(required=False)

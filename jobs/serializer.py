from rest_framework import serializers
from .models import JobListing, SavedJob
from users.models import EmployerProfile
from applications.models import Application


class PublishJobListing(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    company = serializers.CharField(max_length=255, required=False)
    location = serializers.CharField(max_length=255)
    experience = serializers.CharField(max_length=255)
    experience_level = serializers.ChoiceField(
        choices=JobListing.EXPERIENCE_LEVEL_CHOICES, default="entry", required=False
    )
    salary = serializers.CharField(max_length=100, required=False)
    description = serializers.ListField(child=serializers.CharField())
    responsibilities = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    required_qualifications = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    preferred_qualifications = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    benefits = serializers.ListField(child=serializers.CharField(), required=False)
    job_type = serializers.ChoiceField(
        choices=JobListing.JOB_TYPE_CHOICES, default="full time", required=False
    )
    job_location_type = serializers.ChoiceField(
        choices=JobListing.JOB_LOCATION_TYPE_CHOICES, default="onsite", required=False
    )
    job_status = serializers.ChoiceField(
        choices=JobListing.JOB_STATUS_CHOICES, default="open", required=False
    )


class JobListingSerializer(serializers.ModelSerializer):
    employer = serializers.SerializerMethodField()
    has_applied = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = JobListing
        fields = [
            "id",
            "title",
            "location",
            "company",
            "description",
            "responsibilities",
            "required_qualifications",
            "preferred_qualifications",
            "benefits",
            "experience_required",
            "experience_level",
            "salary",
            "job_type",
            "job_location_type",
            "job_status",
            "created_at",
            "employer",
            "applicants",
            "has_applied",
            "is_saved",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "employer",
            "applicants",
            "has_applied",
            "is_saved",
        ]

    def get_has_applied(self, obj):
        # First try to get from annotation
        if hasattr(obj, "user_has_applied"):
            return obj.user_has_applied

        # Fall back to the database query if annotation isn't available
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Application.objects.filter(job=obj, candidate=request.user).exists()
        return False

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return SavedJob.objects.filter(user=request.user, job=obj).exists()
        return False

    def get_employer(self, obj):
        try:
            employer_profile = EmployerProfile.objects.get(user=obj.employer)
            return {
                "name": employer_profile.user.name,
                "username": employer_profile.user.username,
                "photo": (
                    employer_profile.user.photo.url
                    if employer_profile.user.photo
                    else None
                ),
                "company_name": employer_profile.company_name,
                "address": employer_profile.user.address,
                "company_size": employer_profile.company_size,
                "about_company": employer_profile.about_company,
                "industry": employer_profile.industry,
            }
        except EmployerProfile.DoesNotExist:
            return None  # Return None if employer profile does not exist

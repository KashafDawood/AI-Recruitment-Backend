from rest_framework import serializers
from .models import JobListing
from users.serializers import EmployerSerializer
from users.serializers import EmployerSerializer
from users.models import EmployerProfile

class PublishJobListing(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    company = serializers.CharField(max_length=255, required=False)
    location = serializers.CharField(max_length=255)
    experience = serializers.CharField(max_length=255)
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
    employer = serializers.SerializerMethodField()  # Fetch employer details dynamically

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
            "salary",
            "job_type",
            "job_location_type",
            "job_status",
            "created_at",
            "employer",
            "applicants",
        ]
        read_only_fields = ["id", "created_at", "employer", "applicants"]

    def get_employer(self, obj):
        try:
            employer_profile = EmployerProfile.objects.get(user=obj.employer)
            return {
                "name": employer_profile.user.name,
                "username": employer_profile.user.username, 
                "photo": employer_profile.user.photo.url if employer_profile.user.photo else None,
                "company_name": employer_profile.company_name,
            }
        except EmployerProfile.DoesNotExist:
            return None  # Return None if employer profile does not exist
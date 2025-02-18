from rest_framework import serializers
from .models import JobListing


class PublishJobListing(serializers.Serializer):

    job_title = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)
    description = serializers.CharField()
    experience_required = serializers.CharField(max_length=255)
    salary_range = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    job_type = serializers.CharField(max_length=10)


class JobListingSerializer(serializers.ModelSerializer):
    employer = serializers.ReadOnlyField(source="employer.username")

    class Meta:
        model = JobListing
        fields = [
            "id",
            "title",
            "location",
            "description",
            "experience_required",
            "salary",
            "job_type",
            "job_location_type",
            "job_status",
            "created_at",
            "employer",
        ]
        read_only_fields = ["id", "created_at", "employer"]

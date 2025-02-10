from rest_framework import serializers
from .models import JobListing


class GenerateJobListing(serializers.Serializer):
    job_title = serializers.CharField(max_length=255)
    company = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)
    requirements = serializers.CharField(max_length=1000)
    experience_required = serializers.CharField(max_length=255)
    salary_range = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    benefits = serializers.CharField(max_length=255, required=False, allow_blank=True)


class PublishJobListing(serializers.Serializer):

    job_title = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)
    description = serializers.CharField()
    experience_required = serializers.CharField(max_length=255)
    salary_range = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    job_type = serializers.CharField(max_length=10)

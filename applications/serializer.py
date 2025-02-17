from rest_framework import serializers
from .models import Application

class ApplicationSerializer(serializers.ModelSerializer):
    candidate_username = serializers.ReadOnlyField(source="candidate.username")
    job_title = serializers.ReadOnlyField(source="job.title")

    class Meta:
        model = Application
        fields = [
            "id",
            "candidate",
            "candidate_username",
            "job",
            "job_title",
            "application_status",
            "created_at",
        ]
        read_only_fields = ["id", "candidate_username", "job_title", "created_at"]

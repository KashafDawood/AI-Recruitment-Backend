from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    candidate_username = serializers.ReadOnlyField(source="candidate.username")
    candidate_name = serializers.ReadOnlyField(source="candidate.name")
    candidate_photo = serializers.SerializerMethodField()
    candidate_email = serializers.ReadOnlyField(source="candidate.email")
    job_title = serializers.ReadOnlyField(source="job.title")

    def get_candidate_photo(self, obj):
        if obj.candidate.photo:
            return str(obj.candidate.photo.url)
        return None

    class Meta:
        model = Application
        fields = [
            "id",
            "candidate",
            "candidate_username",
            "candidate_name",
            "candidate_photo",
            "candidate_email",
            "job",
            "job_title",
            "application_status",
            "resume",
            "extracted_resume",
            "contract",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "candidate_username",
            "candidate_name",
            "candidate_photo",
            "candidate_email",
            "job_title",
            "extracted_resume",
            "contract",
            "created_at",
        ]


class ApplyJobSerializer(serializers.ModelSerializer):
    candidate = serializers.ReadOnlyField(source="request.user")

    class Meta:
        model = Application
        fields = [
            "id",
            "candidate",
            "job",
            "resume",
            "extracted_resume",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "extracted_resume",
        ]


class UpdateApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["application_status"]
        read_only_fields = ["id", "candidate", "job", "resume", "created_at"]

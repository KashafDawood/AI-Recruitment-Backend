from jobs.models import SavedJob
from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    candidate_username = serializers.ReadOnlyField(source="candidate.username")
    candidate_name = serializers.ReadOnlyField(source="candidate.name")
    candidate_photo = serializers.SerializerMethodField()
    candidate_email = serializers.ReadOnlyField(source="candidate.email")
    job_title = serializers.ReadOnlyField(source="job.title")

    def get_candidate_photo(self, obj):
        if (obj.candidate.photo):
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
    APPLICATION_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewing", "Reviewing"),
        ("shortlisted", "ShortListed"),
        ("interviewed", "Interviewed"),
        ("hired", "Hired"),
        ("rejected", "Rejected"),
    ]

    application_status = serializers.ChoiceField(choices=APPLICATION_STATUS_CHOICES)

    class Meta:
        model = Application
        fields = ["application_status"]
        read_only_fields = ["id", "candidate", "job", "resume", "created_at"]

    def validate_application_status(self, value):
        valid_statuses = dict(self.APPLICATION_STATUS_CHOICES).keys()
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Choose from: {', '.join(valid_statuses)}"
            )
        return value


class AppliedJobSerializer(serializers.ModelSerializer):
    company = serializers.ReadOnlyField(source="job.company")
    location = serializers.ReadOnlyField(source="job.location")
    type = serializers.ReadOnlyField(source="job.type")
    applied_date = serializers.DateTimeField(source="created_at", format="%Y-%m-%d")
    status = serializers.ReadOnlyField(source="application_status")
    salary = serializers.ReadOnlyField(source="job.salary")
    is_saved = serializers.SerializerMethodField()
    job_location_type = serializers.ReadOnlyField(source="job.job_location_type")
    job_status = serializers.ReadOnlyField(source="job.job_status")
    job_type = serializers.ReadOnlyField(source="job.job_type")
    applicants = serializers.ReadOnlyField(source="job.applicants")
    created_at = serializers.DateTimeField(source="job.created_at", format="%Y-%m-%d")
    candidate = serializers.ReadOnlyField(source="candidate.id")
    candidate_email = serializers.ReadOnlyField(source="candidate.email")
    candidate_name = serializers.ReadOnlyField(source="candidate.name")
    candidate_photo = serializers.SerializerMethodField()
    candidate_username = serializers.ReadOnlyField(source="candidate.username")
    title = serializers.ReadOnlyField(source="job.title")
    description = serializers.ReadOnlyField(source="job.description")

    def get_candidate_photo(self, obj):
        if obj.candidate.photo:
            return str(obj.candidate.photo.url)
        return None

    def get_is_saved(self, obj):
        print("obj", obj)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            is_saved = SavedJob.objects.filter(user=request.user, job=obj.id).exists()
            print(f"Debug: is_saved for job {obj.id} and user {request.user.id}: {is_saved}")
            return is_saved
        return False

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "company",
            "location",
            "type",
            "applied_date",
            "status",
            "salary",
            "is_saved",
            "job_location_type",
            "job_status",
            "job_type",
            "applicants",
            "created_at",
            "candidate",
            "candidate_email",
            "candidate_name",
            "candidate_photo",
            "candidate_username",
            "title",
            "description",
        ]

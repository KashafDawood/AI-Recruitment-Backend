from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializer import PublishJobListing, JobListingSerializer
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployer, IsEmployerAndOwner
from .models import JobListing, SavedJob
from users.models import User
from ai.job_filter import job_filtering
from django.db import transaction
from core.pagination import CustomPageNumberPagination
from .utils import apply_job_filters
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import JobListing


class PublishJobListingView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request, *args, **kwargs):
        serializer = PublishJobListing(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Prepare job data dictionary for AI filtering
        job_dict = {
            "title": serializer.validated_data.get("title"),
            "location": serializer.validated_data.get("location", ""),
            "company": serializer.validated_data.get("company", ""),
            "experience": serializer.validated_data.get("experience", ""),
            "salary": serializer.validated_data.get("salary", ""),
            "job_type": serializer.validated_data.get("job_type", "full time"),
            "job_location_type": serializer.validated_data.get(
                "job_location_type", "onsite"
            ),
            "job_status": serializer.validated_data.get("job_status", "open"),
            "description": serializer.validated_data.get("description", []),
            "responsibilities": serializer.validated_data.get("responsibilities", []),
            "required_qualifications": serializer.validated_data.get(
                "required_qualifications", []
            ),
            "preferred_qualifications": serializer.validated_data.get(
                "preferred_qualifications", []
            ),
            "benefits": serializer.validated_data.get("benefits", []),
        }

        # Filter job post before saving to database
        filter_result = job_filtering(job_dict)
        approved = filter_result.get("approved", True)

        # If AI modified the job, update our data dictionary
        if not approved and "modified_job" in filter_result:
            for field, value in filter_result.get("modified_job", {}).items():
                if field in job_dict:
                    job_dict[field] = value

        # Create job listing with final data (original or modified by AI)
        with transaction.atomic():
            job_listing = JobListing.objects.create(
                employer=request.user,
                title=job_dict["title"],
                location=job_dict["location"],
                company=job_dict["company"],
                experience_required=job_dict["experience"],
                salary=job_dict["salary"],
                job_type=job_dict["job_type"],
                job_location_type=job_dict["job_location_type"],
                job_status=job_dict["job_status"],
                description=job_dict["description"],
                responsibilities=job_dict["responsibilities"],
                required_qualifications=job_dict["required_qualifications"],
                preferred_qualifications=job_dict["preferred_qualifications"],
                benefits=job_dict["benefits"],
            )

        job_serializer = JobListingSerializer(job_listing)

        return Response(
            {
                "message": "Job listing successfully published!",
                "job_listing": job_serializer.data,
                "policy_violations": filter_result.get("policy_violations", []),
                "approved": approved,
            },
            status=status.HTTP_201_CREATED,
        )


class MyJobListingView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobListing.objects.all()
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated, IsEmployerAndOwner]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class JobListingListView(generics.ListAPIView):
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobListing.objects.exclude(job_status="draft")


class FetchTenJobsView(generics.ListAPIView):
    serializer_class = JobListingSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = JobListing.objects.exclude(job_status="draft").order_by(
            "-created_at"
        )

        # Use the utility function for filtering
        return apply_job_filters(queryset, self.request.query_params, user)


class jobListingView(generics.RetrieveAPIView):
    queryset = JobListing.objects.all()
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"


class EmployerJobListingsView(generics.ListAPIView):
    serializer_class = JobListingSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = self.request.user

        try:
            employer = User.objects.get(username=username)
            queryset = JobListing.objects.filter(employer=employer).order_by(
                "-created_at"
            )

            # Use the utility function for filtering
            return apply_job_filters(queryset, self.request.query_params, user)

        except User.DoesNotExist:
            return JobListing.objects.none()


class SaveJobView(APIView):
    permission_classes = [IsAuthenticated]

    MAX_SAVED_JOBS = 100

    def post(self, request, job_id):
        job = get_object_or_404(JobListing, id=job_id)

        saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)

        if not created:
            saved_job.delete()
            return Response({"message": "Job unsaved."}, status=200)

        # Ensure we don’t exceed MAX_SAVED_JOBS
        if SavedJob.objects.filter(user=request.user).count() > self.MAX_SAVED_JOBS:
            SavedJob.objects.filter(user=request.user).order_by(
                "saved_at"
            ).first().delete()

        return Response({"message": "Job saved."}, status=201)


class SavedJobsListView(generics.ListAPIView):
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        saved_jobs = SavedJob.objects.filter(user=self.request.user).order_by(
            "-saved_at"
        )
        return JobListing.objects.filter(id__in=saved_jobs.values("job_id")).order_by(
            "-created_at"
        )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsEmployerAndOwner])
def update_job_status(request, job_id):
    """
    Simple endpoint to update just the job status.
    Valid statuses: 'open', 'closed', 'draft'
    """
    try:
        job = JobListing.objects.get(id=job_id)

        # Check ownership (the permission class should handle this, but double-check)
        if job.employer != request.user:
            return Response(
                {"error": "You do not have permission to modify this job"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the new status from request data
        new_status = request.data.get("job_status")

        # Validate the status
        if new_status not in ["open", "closed", "draft"]:
            return Response(
                {"error": 'Invalid job status. Must be "open", "closed", or "draft"'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update the job status
        job.job_status = new_status
        job.save(update_fields=["job_status"])

        return Response(
            {
                "message": f"Job status updated to {new_status}",
                "job_id": job_id,
                "job_status": new_status,
            }
        )

    except JobListing.DoesNotExist:
        return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

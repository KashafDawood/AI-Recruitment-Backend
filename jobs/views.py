from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializer import PublishJobListing, JobListingSerializer
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployer, IsEmployerAndOwner
from .models import JobListing
from ai.job_filter import job_filtering
from django.db import transaction


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
    queryset = JobListing.objects.all()
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated]

class FetchTenJobsView(generics.ListAPIView):
    serializer_class = JobListingSerializer

    def get_queryset(self):
        page = self.request.query_params.get('page', 1)
        limit = self.request.query_params.get('limit', 10)
        offset = (int(page) - 1) * int(limit)
        return JobListing.objects.all().order_by("-created_at")[offset:offset + int(limit)]

class jobListingView(generics.RetrieveAPIView):
    queryset = JobListing.objects.all()
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"


class MyJobListingsView(generics.ListAPIView):

    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated, IsEmployerAndOwner]

    def get_queryset(self):
        """Return only job listings created by the current user"""
        return JobListing.objects.filter(employer=self.request.user).order_by(
            "-created_at"
        )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializer import PublishJobListing, JobListingSerializer
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployer, IsEmployerAndOwner
from .models import JobListing
from ai.job_filter import job_filtering


class PublishJobListingView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request, *args, **kwargs):

        serializer = PublishJobListing(data=request.data)
        if serializer.is_valid():
            job_listing = JobListing.objects.create(
                employer=request.user,
                title=serializer.validated_data.get("title"),
                location=serializer.validated_data.get("location", ""),
                company=serializer.validated_data.get("company", ""),
                experience_required=serializer.validated_data.get("experience", ""),
                salary=serializer.validated_data.get("salary", ""),
                job_type=serializer.validated_data.get("job_type", "full time"),
                job_location_type=serializer.validated_data.get(
                    "job_location_type", "onsite"
                ),
                job_status=serializer.validated_data.get("job_status", "open"),
                # Store JSON fields directly
                description=serializer.validated_data.get("description", []),
                responsibilities=serializer.validated_data.get("responsibilities", []),
                required_qualifications=serializer.validated_data.get(
                    "required_qualifications", []
                ),
                preferred_qualifications=serializer.validated_data.get(
                    "preferred_qualifications", []
                ),
                benefits=serializer.validated_data.get("benefits", []),
            )

            # Get the job listing as a dictionary to send to the AI
            job_dict = {
                "title": job_listing.title,
                "location": job_listing.location,
                "company": job_listing.company,
                "experience": job_listing.experience_required,
                "salary": job_listing.salary,
                "job_type": job_listing.job_type,
                "job_location_type": job_listing.job_location_type,
                "job_status": job_listing.job_status,
                "description": job_listing.description,
                "responsibilities": job_listing.responsibilities,
                "required_qualifications": job_listing.required_qualifications,
                "preferred_qualifications": job_listing.preferred_qualifications,
                "benefits": job_listing.benefits,
            }

            # Filter job post
            filter_result = job_filtering(job_dict)

            # Update job listing with modified data if needed
            if not filter_result.get("approved", True):
                modified_job = filter_result.get("modified_job", {})
                # Update the job listing with modified fields
                for field, value in modified_job.items():
                    if hasattr(job_listing, field):
                        setattr(job_listing, field, value)
                job_listing.save()

            # Serialize the actual job listing object, not the filter result
            job_serializer = JobListingSerializer(job_listing)

            return Response(
                {
                    "message": "Job listing successfully published!",
                    "job_listing": job_serializer.data,
                    "policy_violations": filter_result.get("policy_violations", []),
                    "approved": filter_result.get("approved", True),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

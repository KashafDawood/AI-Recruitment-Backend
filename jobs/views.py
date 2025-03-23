from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializer import PublishJobListing, JobListingSerializer
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployer, IsEmployerAndOwner
from .models import JobListing
from users.models import User
from ai.job_filter import job_filtering
from django.db import transaction
from core.pagination import CustomLimitOffsetPagination
from django.db.models import Q, F
from django.contrib.postgres.search import TrigramSimilarity


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
    pagination_class = CustomLimitOffsetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = JobListing.objects.all().order_by("-created_at")
        query_params = self.request.query_params

        valid_filters = {
            "title": "title__icontains",
            "company": "company__icontains",
            "location": "location__icontains",
            "job_location_type": "job_location_type__icontains",
            "job_type": "job_type__icontains",
        }

        filters = Q()
        has_filters = False

        # Apply direct field filters
        for param, db_field in valid_filters.items():
            value = query_params.get(param, None)
            if value:
                filters &= Q(**{db_field: value.strip()})
                has_filters = True

        # Apply enhanced search across multiple fields
        search_query = query_params.get("search", None)
        if search_query:
            search_query = search_query.lower().strip()
            search_words = search_query.split()

            search_filter = Q()
            for word in search_words:
                search_filter |= (
                    Q(title__icontains=word)
                    | Q(company__icontains=word)
                    | Q(location__icontains=word)
                    | Q(job_location_type__icontains=word)
                    | Q(job_type__icontains=word)
                )

            filters &= search_filter
            has_filters = True

            # Apply Trigram Similarity Search only when `search_query` exists
            queryset = (
                queryset.annotate(similarity=TrigramSimilarity("title", search_query))
                .filter(similarity__gt=0.2)
                .order_by(F("similarity").desc())
            )

        if has_filters:
            queryset = queryset.filter(filters)

        return queryset


class jobListingView(generics.RetrieveAPIView):
    queryset = JobListing.objects.all()
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"


class EmployerJobListingsView(generics.ListAPIView):
    serializer_class = JobListingSerializer

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
            return JobListing.objects.filter(employer=user).order_by("-created_at")
        except User.DoesNotExist:
            return JobListing.objects.none()

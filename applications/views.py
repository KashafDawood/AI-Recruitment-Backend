from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsCandidate, IsJobEmployer
from .models import Application
from .serializer import (
    ApplicationSerializer,
    AppliedJobSerializer,
    ApplyJobSerializer,
    UpdateApplicationStatusSerializer,
)
from rest_framework.views import APIView
from core.pagination import CustomPageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from .models import Application
from .serializer import UpdateApplicationStatusSerializer
from rest_framework.permissions import IsAuthenticated
from core.utils import extract_text_from_pdf, download_pdf_from_url
from django.db import transaction


class ApplyJobView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsCandidate]
    serializer_class = ApplyJobSerializer

    def perform_create(self, serializer):
        # Extract resume text before saving
        resume = serializer.validated_data.get("resume")
        extracted_text = ""

        if resume:
            # If resume is a URL, download it first
            if resume.startswith("http"):
                pdf_file = download_pdf_from_url(resume)
                if not isinstance(pdf_file, str):  # Check if it's not an error message
                    extracted_text = extract_text_from_pdf(pdf_file)
            else:
                # Assume it's a file path or file object
                try:
                    extracted_text = extract_text_from_pdf(resume)
                except Exception as e:
                    extracted_text = f"Error extracting text: {str(e)}"

        # Save the application with extracted text
        serializer.save(candidate=self.request.user, extracted_resume=extracted_text)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            job = serializer.validated_data["job"]
            candidate = self.request.user

            # Check if job is closed
            if job.job_status == "closed":
                return Response(
                    {
                        "message": "Job is closed",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if user already applied for this job
            if Application.objects.filter(job=job, candidate=candidate).exists():
                return Response(
                    {
                        "message": "You have already applied for this job",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            self.perform_create(serializer)
            job.applicants += 1
            job.save()
            return Response(
                {
                    "message": "You successfully applied on this job",
                    "application": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "message": "There was an error with your application",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class JobApplicationsListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsJobEmployer]

    def get_queryset(self):
        job_id = self.kwargs.get("job_id")
        return Application.objects.filter(job_id=job_id)


class UpdateApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated, IsJobEmployer]
    serializer_class = UpdateApplicationStatusSerializer

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        user = request.user
        job_id = self.kwargs.get("job_id")
        application_ids = request.data.get("application_ids", [])
        new_status = request.data.get("application_status")

        if not application_ids or not new_status:
            return Response(
                {"error": "application_ids and application_status are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate the status using the serializer
        serializer = self.serializer_class(data={"application_status": new_status})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get all applications that belong to the employer and match the IDs
        applications = Application.objects.filter(
            job__employer=user, job_id=job_id, id__in=application_ids
        )
        existing_ids = list(applications.values_list("id", flat=True))
        missing_ids = set(map(int, application_ids)) - set(existing_ids)

        # Bulk update the application status
        applications.update(application_status=new_status)

        response_data = {
            "updated_applications": existing_ids,
            "missing_applications": list(missing_ids),
            "status": new_status,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class AppliedJobsListView(generics.ListAPIView):
    serializer_class = AppliedJobSerializer  # Updated to use AppliedJobSerializer
    permission_classes = [IsAuthenticated, IsCandidate]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Application.objects.filter(candidate=self.request.user).order_by('-created_at')

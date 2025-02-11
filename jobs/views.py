from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializer import GenerateJobListing, PublishJobListing, JobListingSerializer
from .ai_generating import generate_job_listing
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployer, IsEmployerAndOwner
import markdown
from bs4 import BeautifulSoup
from .models import JobListing


class GenerateJobPostingView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request, *args, **kwargs):
        serializer = GenerateJobListing(data=request.data)
        if serializer.is_valid():
            job_title = serializer.validated_data["job_title"]
            company = serializer.validated_data["company"]
            location = serializer.validated_data["location"]
            requirements = serializer.validated_data["requirements"]
            experience_required = serializer.validated_data["experience_required"]
            salary_range = serializer.validated_data.get(
                "salary_range", "Not specified"
            )
            benefits = serializer.validated_data.get(
                "benefits",
            )

            job_listing = generate_job_listing(
                job_title,
                company,
                location,
                requirements,
                experience_required,
                salary_range,
                benefits,
            )

            # Remove Markdown code block markers (```markdown ... ```)
            if job_listing.startswith("```markdown"):
                job_listing = job_listing.strip("```markdown").strip("```")

            # Convert Markdown to HTML
            formatted_job = markdown.markdown(job_listing)
            soup = BeautifulSoup(formatted_job, "html.parser")
            formatted_job = soup.prettify(formatter="html").replace("\n", " ")

            return Response({"job_listing": formatted_job}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublishJobListingView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request, *args, **kwargs):
        serializer = PublishJobListing(data=request.data)
        if serializer.is_valid():
            job_title = serializer.validated_data["job_title"]
            location = serializer.validated_data["location"]
            description = serializer.validated_data["description"]
            job_type = serializer.validated_data["job_type"]
            experience_required = serializer.validated_data["experience_required"]
            salary_range = serializer.validated_data.get(
                "salary_range", "Not specified"
            )

            job_listing = JobListing.objects.create(
                employer=request.user,
                title=job_title,
                location=location,
                description=description,
                experience_required=experience_required,
                salary=salary_range,
                job_type=job_type,
            )

            job_data = {
                "id": job_listing.id,
                "title": job_listing.title,
                "location": job_listing.location,
                "description": job_listing.description,
                "experience_required": job_listing.experience_required,
                "salary": job_listing.salary,
                "job_type": job_listing.job_type,
                "created_at": job_listing.created_at.isoformat(),
            }

            return Response(
                {
                    "message": "Job listing successfully published!",
                    "job_listing": job_data,
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

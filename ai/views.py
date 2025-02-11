from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import GenerateJobListing
from .generator import generate_job_listing
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployer
import markdown
from bs4 import BeautifulSoup


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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import (
    GenerateJobListing,
    GenerateBlogSerializer,
    BestCandidateSerializer,
    GenerateContractSerializer,
)
from .JobList_generator import generate_job_listing
from .bio_generator import generate_candidate_bio
from .blog_post_generator import generate_blog_post
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployer, IsCandidate
import markdown
from bs4 import BeautifulSoup
from .candidate_recommender import recommend_best_candidate
from jobs.models import JobListing
from django.http import HttpResponse

from .contract_generator import generate_contract


class GenerateJobPostingView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request, *args, **kwargs):
        serializer = GenerateJobListing(data=request.data)
        if serializer.is_valid():
            job_title = serializer.validated_data["job_title"]
            company = serializer.validated_data["company"]
            location = serializer.validated_data["location"]
            description = serializer.validated_data["description"]
            experience_required = serializer.validated_data["experience_required"]
            salary_range = serializer.validated_data.get(
                "salary_range", "Not specified"
            )

            job_listing = generate_job_listing(
                description,
                job_title,
                company,
                location,
                experience_required,
                salary_range,
            )

            return Response({"job_listing": job_listing}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateCandidateBioView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def post(self, request, *args, **kwargs):
        user = request.user

        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        bio = generate_candidate_bio(user)

        # Remove Markdown code block markers (```markdown ... ```)
        if bio.startswith("```markdown"):
            bio = bio.strip("```markdown").strip("```")

        # Convert Markdown to HTML
        formatted_bio = markdown.markdown(bio)
        soup = BeautifulSoup(formatted_bio, "html.parser")
        formatted_bio = soup.prettify(formatter="html").replace("\n", " ")

        return Response({"bio": formatted_bio}, status=status.HTTP_200_OK)


class GenerateBlogView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request, *args, **kwargs):
        serializer = GenerateBlogSerializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data["blog_title"]
            description = serializer.validated_data["blog_description"]
            keywords = serializer.validated_data["blog_keywords"]
            blog_length = serializer.validated_data["blog_length"]

            blog = generate_blog_post(title, description, keywords, blog_length)

            # Remove Markdown code block markers (```markdown ... ```)
            if blog.startswith("```markdown"):
                blog = blog.strip("```markdown").strip("```")

            # Convert Markdown to HTML
            formatted_blog = markdown.markdown(blog)
            soup = BeautifulSoup(formatted_blog, "html.parser")
            formatted_blog = soup.prettify(formatter="html").replace("\n", " ")

            return Response({"blog": formatted_blog}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BestCandidateRecommenderView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request, *args, **kwargs):
        serializer = BestCandidateSerializer(data=request.data)
        if serializer.is_valid():
            applications = serializer.validated_data["applications"]
            job_id = serializer.validated_data["job_id"]

            try:
                job = JobListing.objects.get(id=job_id)
                description = job.description
                responsibilities = job.responsibilities
                required_qualifications = job.required_qualifications
                preferred_qualifications = job.preferred_qualifications

                result = recommend_best_candidate(
                    applications,
                    description,
                    responsibilities,
                    required_qualifications,
                    preferred_qualifications,
                )

                return Response({"result": result}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response(
                    {"error": f"Failed to process recommendation: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateContractView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request, *args, **kwargs):
        serializer = GenerateContractSerializer(data=request.data)
        if serializer.is_valid():
            contract_data = serializer.validated_data
            contract_path = generate_contract(contract_data)
            with open(contract_path, "rb") as contract_file:
                response = HttpResponse(
                    contract_file.read(),
                    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
                response["Content-Disposition"] = (
                    f'attachment; filename="{contract_data["employee_name"]}_contract.docx"'
                )
                return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

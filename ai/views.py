from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import GenerateJobListing, GenerateBlogSerializer, GenerateContractSerializer
from .JobList_generator import generate_job_listing
from .bio_generator import generate_candidate_bio
from .blog_post_generator import generate_blog_post
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployer, IsCandidate
import markdown
from bs4 import BeautifulSoup
from django.http import JsonResponse, HttpResponse
from .bio_filter import filter_bio
from .contract_generator import generate_contract

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
            title = serializer["blog_title"]
            description = serializer["blog_description"]
            keywords = serializer["blog_keywords"]
            blog_length = serializer["blog_length"]

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

class GenerateContractView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request, *args, **kwargs):
        serializer = GenerateContractSerializer(data=request.data)
        if serializer.is_valid():
            contract_data = serializer.validated_data
            contract_path = generate_contract(contract_data)
            with open(contract_path, 'rb') as contract_file:
                response = HttpResponse(contract_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename="{contract_data["employee_name"]}_contract.docx"'
                return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
from applications.models import Application
from users.models import User, CandidateProfile, EmployerProfile
from django.http import HttpResponse
from .contract_generator import generate_contract
import os
from core.b2_storage import BackblazeB2Storage
from emails.email import send_contract_email
from django.utils import timezone
from datetime import timedelta


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

        try:
            bio = generate_candidate_bio(user)

            # Remove Markdown code block markers (```markdown ... ```)
            if bio.startswith("```markdown"):
                bio = bio.strip("```markdown").strip("```")

            # Convert Markdown to HTML
            formatted_bio = markdown.markdown(bio)
            soup = BeautifulSoup(formatted_bio, "html.parser")
            formatted_bio = soup.prettify(formatter="html").replace("\n", " ")

            return Response({"bio": formatted_bio}, status=status.HTTP_200_OK)
        except ValueError as e:
            # More descriptive error message for missing skills or resume
            error_message = str(e)
            if "Skills are required" in error_message:
                error_message = "Either skills or resume are required to generate your bio. Please add skills or upload your resume."

            return Response(
                {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to generate bio: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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

                # Ensure each application has extracted_resume data
                for app in applications:
                    if "id" in app and not app.get("extracted_resume"):
                        try:
                            application = Application.objects.get(id=app["id"])
                            app["extracted_resume"] = application.extracted_resume
                        except Application.DoesNotExist:
                            pass

                result = recommend_best_candidate(
                    applications,
                    description,
                    preferred_qualifications,
                    required_qualifications,
                    responsibilities,
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
            app_id = serializer.validated_data["app_id"]
            start_date = serializer.validated_data["start_date"]
            end_date = serializer.validated_data.get("end_date")
            terms = serializer.validated_data.get("terms", "")

            try:
                # Get all necessary data
                application = Application.objects.get(id=app_id)
                job = JobListing.objects.get(id=application.job.id)
                employee = User.objects.get(id=application.candidate.id)
                employer = request.user

                # Prepare data for contract generation
                contract_data = {
                    "employer_name": employer.name,
                    "employer_address": job.location,
                    "employee_name": employee.name,
                    "employee_address": (
                        employee.address
                        if hasattr(employee, "address") and employee.address
                        else "Address to be provided"
                    ),
                    "company_name": job.company,
                    "job_title": job.title,
                    "start_date": start_date.strftime("%B %d, %Y"),
                    "salary": job.salary,
                    "responsibilities": (
                        ", ".join(job.responsibilities)
                        if isinstance(job.responsibilities, list)
                        else str(job.responsibilities)
                    ),
                    "benefits": (
                        ", ".join(job.benefits)
                        if isinstance(job.benefits, list)
                        else str(job.benefits)
                    ),
                    "terms": terms,
                }

                # Add end date if provided
                if end_date:
                    contract_data["end_date"] = end_date.strftime("%B %d, %Y")

                # Generate the contract and get the B2 URL directly
                contract_url = generate_contract(contract_data)

                # Update application with contract URL
                application.contract = contract_url
                application.save()

                # Send email to candidate
                send_contract_email(
                    employee.email, contract_url, job.company, job.title
                )

                # Return success response with contract information
                return Response(
                    {
                        "status": "success",
                        "message": f"Contract generated and sent to {employee.email}",
                        "contract_url": contract_url,
                        "candidate_name": employee.name,
                        "job_title": job.title,
                        "company": job.company,
                    },
                    status=status.HTTP_200_OK,
                )

            except Application.DoesNotExist:
                return Response(
                    {"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except JobListing.DoesNotExist:
                return Response(
                    {"error": "Job listing not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"error": f"Failed to generate contract: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

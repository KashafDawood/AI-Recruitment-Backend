from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsCandidate
from ..models import CandidateProfile
from ..serializers import (
    CandidateSerializer,
    EducationSerializer,
    CertificationSerializer,
    GenerateBioSerializer,
    CandidateBioSerializer
)
from datetime import date
import json
from ai.bio_generator import generate_candidate_bio
from ai.bio_filter import filter_bio


class CandidateMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_object(self):
        return self.request.user.candidate_profile

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        resume_file = request.FILES.get("resume")
        if resume_file:
            candidate_profile = self.get_object()
            candidate_profile.add_resume(resume_file, resume_file.name)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class CandidateListView(generics.ListAPIView):
    queryset = CandidateProfile.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]


class DeleteResumeView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def delete(self, request, resume_name):
        candidate_profile = request.user.candidate_profile
        success = candidate_profile.delete_resume(resume_name)
        if success:
            return Response(
                {"message": "Resume deleted successfully"}, status=status.HTTP_200_OK
            )
        return Response({"error": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)


class AddEducationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EducationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        education_entry = serializer.validated_data

        # Convert date objects to strings
        if isinstance(education_entry["start_date"], date):
            education_entry["start_date"] = education_entry["start_date"].isoformat()
        if education_entry.get("end_date") and isinstance(
            education_entry["end_date"], date
        ):
            education_entry["end_date"] = education_entry["end_date"].isoformat()

        # Handle education as a list instead of a dictionary
        if user.education is None:
            user.education = []

        # Since user.education is a list, just append the new entry
        user.education.append(education_entry)
        user.save()

        return Response(
            {"message": "Education added successfully"}, status=status.HTTP_201_CREATED
        )


class AddCertificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CertificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        certification_entry = serializer.validated_data

        # Convert date objects to strings
        if certification_entry.get("date_obtained") and isinstance(
            certification_entry["date_obtained"], date
        ):
            certification_entry["date_obtained"] = certification_entry[
                "date_obtained"
            ].isoformat()

        # Ensure certifications is a list
        if isinstance(user.certifications, str):
            user.certifications = json.loads(user.certifications)
        if not isinstance(user.certifications, list):
            user.certifications = []

        user.certifications.append(certification_entry)
        user.save()
        return Response(
            {"message": "Certification added successfully"},
            status=status.HTTP_201_CREATED,
        )


class EducationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EducationSerializer

    def get_object(self):
        user = self.request.user
        degree_name = self.kwargs.get("degree_name")

        # Handle education as a list
        for idx, education in enumerate(user.education):
            if education.get("degree_name") == degree_name:
                # Store index for later use
                self._education_index = idx
                return education
        return None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(
                {"error": "Education not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = request.user

        # Update the education entry in the list
        if hasattr(self, "_education_index"):
            user.education[self._education_index].update(serializer.validated_data)
            user.save()
            return Response(
                {"message": "Education updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Education not found"}, status=status.HTTP_404_NOT_FOUND
        )

    def destroy(self, request, *args, **kwargs):
        user = request.user
        degree_name = self.kwargs.get("degree_name")

        # Remove education from list
        for idx, education in enumerate(user.education):
            if education.get("degree_name") == degree_name:
                user.education.pop(idx)
                user.save()
                return Response(
                    {"message": "Education deleted successfully"},
                    status=status.HTTP_200_OK,
                )

        return Response(
            {"error": "Education not found"}, status=status.HTTP_404_NOT_FOUND
        )


class CertificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CertificationSerializer

    def get_object(self):
        user = self.request.user
        certification_name = self.kwargs.get("certification_name")

        certifications = user.certifications
        if isinstance(certifications, str):
            certifications = json.loads(certifications)

        for certification in certifications:
            if (
                isinstance(certification, dict)
                and certification.get("certification_name") == certification_name
            ):
                return certification

        return None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(
                {"error": "Certification not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user = request.user
        certifications = user.certifications
        if isinstance(certifications, str):
            certifications = json.loads(certifications)

        for i, certification in enumerate(certifications):
            if (
                isinstance(certification, dict)
                and certification["certification_name"]
                == instance["certification_name"]
            ):
                certifications[i].update(serializer.validated_data)
                # Convert date fields to strings
                if "date_obtained" in certifications[i] and isinstance(
                    certifications[i]["date_obtained"], date
                ):
                    certifications[i]["date_obtained"] = certifications[i][
                        "date_obtained"
                    ].isoformat()
                user.certifications = certifications  # Assign back the modified list
                user.save()
                return Response(
                    {"message": "Certification updated successfully"},
                    status=status.HTTP_200_OK,
                )

        return Response(
            {"error": "Certification not found"}, status=status.HTTP_404_NOT_FOUND
        )

    def destroy(self, request, *args, **kwargs):
        user = request.user
        certification_name = self.kwargs.get("certification_name")

        certifications = user.certifications
        if isinstance(certifications, str):
            certifications = json.loads(certifications)

        for i, certification in enumerate(certifications):
            if (
                isinstance(certification, dict)
                and certification["certification_name"] == certification_name
            ):
                del certifications[i]
                user.certifications = certifications  # Assign back updated list
                user.save()
                return Response(
                    {"message": "Certification deleted successfully"},
                    status=status.HTTP_200_OK,
                )

        return Response(
            {"error": "Certification not found"}, status=status.HTTP_404_NOT_FOUND
        )


class GenerateBioView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def post(self, request):
        serializer = GenerateBioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bio = serializer.validated_data["bio"]
        candidate_profile = request.user.candidate_profile
        # Use CandidateBioSerializer to handle bio filtering
        bio_serializer = CandidateBioSerializer(candidate_profile, data={"bio": bio}, context={'request': request})
        bio_serializer.is_valid(raise_exception=True)
        bio_serializer.save()
        return Response({"bio": bio_serializer.data["bio"]}, status=status.HTTP_200_OK)


class GenerateBioAIView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def post(self, request):
        user = request.user
        bio = generate_candidate_bio(user)
        candidate_profile = user.candidate_profile
        candidate_profile.bio = bio
        candidate_profile.save()
        return Response({"bio": bio}, status=status.HTTP_200_OK)

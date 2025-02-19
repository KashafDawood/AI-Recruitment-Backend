from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsCandidate, IsJobEmployer
from .models import Application
from .serializer import ApplicationSerializer, createApplicationSerializer


class CreateApplicationView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsCandidate]
    serializer_class = createApplicationSerializer

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            job = serializer.validated_data["job"]
            if job.job_status == "closed":
                return Response(
                    {
                        "message": "Job is closed",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            self.perform_create(serializer)
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

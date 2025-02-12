from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployer
from ..models import EmployerProfile
from ..serializers import EmployerSerializer


class EmployerMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployerSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def get_object(self):
        return self.request.user.employer_profile


class EmployerListView(generics.ListAPIView):
    queryset = EmployerProfile.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = [IsAuthenticated]

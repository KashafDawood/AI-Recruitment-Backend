from rest_framework import generics, status
from rest_framework.response import Response
from .models import Users
from .serializers import UserSerializer

class UserSignup(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        header = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=header, status=status.HTTP_201_CREATED)
from rest_framework import generics, status
from rest_framework.response import Response
from .models import User
from .serializers import SignupSerializer

# class UserSignup(generics.CreateAPIView):
#     queryset = Users.objects.all()
#     serializer_class = UserSerializer

#     def post(self, request):
#         serializer = self.get_serializer(data = request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         header = self.get_success_headers(serializer.data)
#         return Response(serializer.data, headers=header, status=status.HTTP_201_CREATED)

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        self.perform_create(serializer)
        header = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=header, status=status.HTTP_201_CREATED)
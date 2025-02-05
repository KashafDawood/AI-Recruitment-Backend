from rest_framework import generics, status
from rest_framework.response import Response
from .models import User, Candidate
from .serializers import SignupSerializer, CandidateRegisterSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer
from rest_framework.views import APIView

def res(user, res, status_code=status.HTTP_201_CREATED):
    serializer = user.get_serializer(data = res.data)
    serializer.is_valid(raise_exception = True)
    user.perform_create(serializer)
    header = user.get_success_headers(serializer.data)
    return Response(serializer.data, headers=header, status=status_code)

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def post(self, request):
        return res(self, request)
       
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You are authenticated!", "user": request.user.email})

class CandidateRegisterView(generics.CreateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateRegisterSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return res(self, request)
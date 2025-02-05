from rest_framework import generics, status
from rest_framework.response import Response
from .models import User, Candidate
from .serializers import SignupSerializer, CandidateRegisterSerializer
from rest_framework.permissions import AllowAny
from .serializers import LoginSerializer

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
    
class CandidateRegisterView(generics.CreateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateRegisterSerializer

    def post(self, request):
        return res(self, request)
    

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
from rest_framework import generics, status
from rest_framework.response import Response
from .models import User
from .serializers import SignupSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": f"Successfully registered as {user.role}",
            "user": serializer.data,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        }, status=status.HTTP_201_CREATED)
       
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

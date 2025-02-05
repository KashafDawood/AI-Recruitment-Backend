from rest_framework import generics, status
from rest_framework.response import Response
from .models import User
from .serializers import SignupSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
import datetime
from datetime import UTC

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
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({
            "message": "Login successful",
            "status": status.HTTP_200_OK,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "name": user.name,
            },
            'access': access_token,
            'refresh': str(refresh),
        })

        # Set Access Token Cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=access_token,
            httponly=True,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            expires=datetime.datetime.now(UTC) + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        )

        # Set Refresh Token Cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            value=str(refresh),
            httponly=True,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            expires=datetime.datetime.now(UTC) + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
        )

        return response
    
class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You are authenticated!", "user": request.user.email})

class LogoutAPIView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        return response
    
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])

        if refresh_token is None:
            return Response({"error": "No refresh token provided"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({"message": "Token refreshed", 'access': access_token}, status=status.HTTP_200_OK)
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access_token,
                httponly=True,
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                expires=datetime.datetime.now(UTC) + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            )
            return response
        except Exception as e:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from datetime import UTC
import datetime
from ..models import User
from ..serializers import SignupSerializer, LoginSerializer, VerifyEmailOTP
from emails.models import EmailOTP
from emails.views import generate_otp
from ..helper import set_http_only_cookie


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        generate_otp(user)

        if user.role == "candidate":
            candidate_profile = user.candidate_profile
            resume_file = request.FILES.get("resume")
            if resume_file:
                candidate_profile.add_resume(resume_file, resume_file.name)

        return Response(
            {
                "message": f"Successfully registered as {user.role}",
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class ResendEmailOTPView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            user_data = request.data.get("user")
            if not user_data or not user_data.get("email"):
                return Response(
                    {"error": "User not provided in request body"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                user = User.objects.get(email=user_data.get("email"))
            except User.DoesNotExist:
                return Response(
                    {"error": "User does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        generate_otp(user)
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


class VerifyEmailOTPView(APIView):
    def post(self, request):
        serializer = VerifyEmailOTP(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        otp_submitted = serializer.validated_data["otp"]

        if not user.is_authenticated:
            email = request.data.get("user", {}).get("email")
            if not email:
                return Response(
                    {"error": "User not provided in request body"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "User does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            with transaction.atomic():
                # Get the most recent OTP specifically for this user
                otp_obj = (
                    EmailOTP.objects.select_for_update()
                    .filter(
                        user=user,
                        otp=otp_submitted,
                        verified=False,
                        expires_at__gt=timezone.now(),
                    )
                    .order_by("-created_at")
                    .first()
                )

                # Check if we found a valid OTP
                if not otp_obj:
                    return Response(
                        {"error": "Invalid or expired OTP"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                otp_obj.verified = True
                otp_obj.save()

                # Update the user instance directly
                user.is_verified = True
                user.save()

        except Exception as e:
            return Response(
                {"error": f"OTP verification failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response(
            {
                "message": "Email verified successfully",
                "access": access_token,
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )

        set_http_only_cookie(res=response, access_token=access_token, refresh=refresh)

        return response


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        if not user.is_verified:
            generate_otp(user)
            return Response(
                {
                    "error": "Please verify your email before logging in.",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "role": user.role,
                        "name": user.name,
                        "username": user.username,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {"error": "Your account is deactivated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response(
            {
                "message": "Login successful",
                "status": status.HTTP_200_OK,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "name": user.name,
                    "username": user.username,
                },
                "access": access_token,
                "refresh": str(refresh),
            }
        )
        set_http_only_cookie(response, access_token, refresh)

        return response


class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {"message": "You are authenticated!", "user": request.user.email}
        )


class LogoutAPIView(APIView):
    def post(self, request):
        response = Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )
        response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
        response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])

        if refresh_token is None:
            return Response(
                {"error": "No refresh token provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            # Create serializer with the token from cookie
            serializer = self.get_serializer(data={"refresh": refresh_token})
            serializer.is_valid(raise_exception=True)

            # Get validated data containing access and possibly new refresh token
            validated_data = serializer.validated_data
            access_token = validated_data.get("access")

            # Create response with access token
            response = Response(
                {"message": "Token refreshed", "access": access_token},
                status=status.HTTP_200_OK,
            )

            # Set the access token in cookie
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=access_token,
                httponly=True,
                secure=True,
                samesite="None",
                expires=datetime.datetime.now(UTC)
                + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            )

            # If ROTATE_REFRESH_TOKENS is enabled, set the new refresh token in cookie
            if (
                settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"]
                and "refresh" in validated_data
            ):
                new_refresh_token = validated_data.get("refresh")
                response.set_cookie(
                    key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                    value=new_refresh_token,
                    httponly=True,
                    secure=True,
                    samesite="None",
                    expires=datetime.datetime.now(UTC)
                    + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                )

            return response
        except Exception as e:
            return Response(
                {"error": "Invalid refresh token", "details": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

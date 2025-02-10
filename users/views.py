from rest_framework import generics, status
from rest_framework.response import Response
from .models import User, CandidateProfile, EmployerProfile
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    CandidateSerializer,
    EmployerSerializer,
    ChangePasswordSerializer,
    ChangeUsername,
    VerifyEmailOTP,
    UserSerializer,
    ForgetPassword,
    ResetPassword,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
import datetime
from datetime import UTC, timedelta
from django.utils import timezone
from core.permissions import IsCandidate, IsEmployer
from emails.models import EmailOTP
from emails.views import generate_otp, send_forget_password_email
from django.db import transaction


def set_http_only_cookie(res, access_token, refresh):
    # set acess token cookie
    res.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=access_token,
        httponly=True,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        expires=datetime.datetime.now(UTC)
        + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
    )

    # Set Refresh Token Cookie
    res.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
        value=str(refresh),
        httponly=True,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        expires=datetime.datetime.now(UTC)
        + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
    )


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        generate_otp(user)

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
                    {"error": "User not provided in request body"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        try:
            with transaction.atomic():  # ensure OTP update is atomic
                otp_obj = (
                    EmailOTP.objects.select_for_update()
                    .filter(user__email=user.email, otp=otp_submitted, verified=False)
                    .latest("created_at")
                )

                if timezone.now() > otp_obj.expires_at:
                    return Response(
                        {"error": "OTP has expired"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                otp_obj.verified = True
                otp_obj.save()
        except EmailOTP.DoesNotExist:
            return Response(
                {"error": "Invalid OTP or email"},
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
            return Response(
                {"error": "Please verify your email before logging in."},
                status=status.HTTP_401_UNAUTHORIZED,
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

        set_http_only_cookie(res=response, access_token=access_token, refresh=refresh)

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
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response(
                {"message": "Token refreshed", "access": access_token},
                status=status.HTTP_200_OK,
            )
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=access_token,
                httponly=True,
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                expires=datetime.datetime.now(UTC)
                + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            )
            return response
        except Exception as e:
            return Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED
            )


class CandidateMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_object(self):
        return self.request.user.candidate_profile


class EmployerMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployerSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def get_object(self):
        return self.request.user.employer_profile


class CandidateListView(generics.ListAPIView):
    queryset = CandidateProfile.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]


class EmployerListView(generics.ListAPIView):
    queryset = EmployerProfile.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = [IsAuthenticated]


class UserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"old_password": "Wrong password"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeUsernameView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangeUsername(data=request.data)
        if serializer.is_valid():
            user = request.user
            change_username_at = user.changeUsernameAt
            if (
                not change_username_at
                or change_username_at == ""
                or (timezone.now() - change_username_at) > timedelta(hours=48)
            ):
                new_username = serializer.validated_data["username"]
                if User.objects.filter(username=new_username).exists():
                    return Response(
                        {"new_username": "Username already taken"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user.username = new_username
                user.changeUsernameAt = timezone.now()
                user.save()
                return Response(
                    {"message": "Username updated successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Username can only be changed once every 48 hours"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ForgetPassword(data=request.data)
        serializer.is_valid(raise_exception=True)

        useremail = serializer.validated_data["email"]

        try:
            user_data = User.objects.get(email=useremail)
            reset_token = RefreshToken.for_user(user_data).access_token
            # Update URL to use lowercase 'resetpassword'
            reset_url = f"{request.scheme}://{request.get_host()}/api/users/resetpassword/{reset_token}"

            # send reset password email
            send_forget_password_email(useremail, reset_url)

            return Response(
                {
                    "message": "Reset password email sent successfully",
                    "reset_url": reset_url,
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordView(APIView):
    def post(self, request, token, *args, **kwargs):
        serializer = ResetPassword(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            access = AccessToken(token)
            user = User.objects.get(id=access["user_id"])
        except (User.DoesNotExist, Exception):
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"message": "Password reset successfully"},
            status=status.HTTP_200_OK,
        )

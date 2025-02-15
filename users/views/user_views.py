from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from ..models import User
from ..serializers import (
    UserSerializer,
    ChangePasswordSerializer,
    ChangeUsername,
    ForgetPassword,
    ResetPassword,
)
from emails.views import send_forget_password_email, send_reactivate_account_email
from ..helper import set_http_only_cookie


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


class DeactivateAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_active = False
        user.save()
        response = Response(
            {"message": "Account deactivated successfully"}, status=status.HTTP_200_OK
        )
        response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
        response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])
        return response


class ReactivateAccountView(APIView):
    def post(self, request, token, *args, **kwargs):
        try:
            access = AccessToken(token)
            user = User.objects.get(id=access["user_id"])
            if user.is_active:
                return Response(
                    {"message": "Account already active"}, status=status.HTTP_200_OK
                )
            user.is_active = True
            user.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            response = Response(
                {
                    "message": "Account reactivated successfully",
                    "access": access_token,
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
            set_http_only_cookie(
                res=response, access_token=access_token, refresh=refresh
            )
            return response
        except Exception:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReactivateAccountEmailView(APIView):
    def post(self, request):
        serializer = ForgetPassword(data=request.data)
        serializer.is_valid(raise_exception=True)
        useremail = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=useremail)
            if user.is_active:
                return Response(
                    {"message": "Account is already active"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken.for_user(user).access_token
            url = (
                f"{request.scheme}://{request.get_host()}/api/users/reactivate/{token}/"
            )

            send_reactivate_account_email(useremail, url)
            return Response(
                {"message": "Reactivation email sent successfully"},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

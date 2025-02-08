from django.urls import path
from .views import (
    SignupView,
    LoginView,
    ProtectedAPIView,
    CookieTokenRefreshView,
    LogoutAPIView,
    CandidateMeView,
    EmployerMeView,
    CandidateListView,
    EmployerListView,
    AdminAccessible_CandidateView,
    ChangePasswordView,
    ChangeUsernameView,
    VerifyEmailOTPView,
    ResendEmailOTPView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="user-signup"),
    path("verify-email/", VerifyEmailOTPView.as_view(), name="verify-email"),
    path("resend-otp-email/", ResendEmailOTPView.as_view(), name="resend-otp-email"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("protected/", ProtectedAPIView.as_view(), name="protected-api"),
    path("candidate/", CandidateListView.as_view(), name="get-all-candidate"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("change-username/", ChangeUsernameView.as_view(), name="change-username"),
    path(
        "candidate/me",
        CandidateMeView.as_view(),
        name="candidate-endpoints",
    ),
    path("employer/", EmployerListView.as_view(), name="get-all-employer"),
    path("employer/me", EmployerMeView.as_view(), name="employer-endpoints"),
    path(
        "candidate/<int:id>",
        AdminAccessible_CandidateView.as_view(),
        name="admin-accessible-candidate-view",
    ),
]

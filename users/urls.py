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
    UserView,
    ChangePasswordView,
    ChangeUsernameView,
    VerifyEmailOTPView,
    ResendEmailOTPView,
    ForgetPasswordView,
    ResetPasswordView,
    DeactivateAccountView,
    ReactivateAccountView,
    ReactivateAccountEmailView,
    DeleteResumeView,
    AddEducationView,
    AddCertificationView,
    EducationDetailView,
    CertificationDetailView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="user-signup"),
    path("verify-email/", VerifyEmailOTPView.as_view(), name="verify-email"),
    path("resend-otp-email/", ResendEmailOTPView.as_view(), name="resend-otp-email"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path(
        "deactivate-me/", DeactivateAccountView.as_view(), name="deactivate-my-account"
    ),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("protected/", ProtectedAPIView.as_view(), name="protected-api"),
    path("candidate/", CandidateListView.as_view(), name="get-all-candidate"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("forget-password/", ForgetPasswordView.as_view(), name="forget-password"),
    path(
        "resetpassword/<str:token>", ResetPasswordView.as_view(), name="reset-password"
    ),
    path("change-username/", ChangeUsernameView.as_view(), name="change-username"),
    path(
        "candidate/me",
        CandidateMeView.as_view(),
        name="candidate-endpoints",
    ),
    path("employer/", EmployerListView.as_view(), name="get-all-employer"),
    path("employer/me", EmployerMeView.as_view(), name="employer-endpoints"),
    path(
        "<int:id>",
        UserView.as_view(),
        name="user-by-id-view",
    ),
    path(
        "reactivate/<str:token>/",
        ReactivateAccountView.as_view(),
        name="reactivate-account",
    ),
    path(
        "reactivate-request/",
        ReactivateAccountEmailView.as_view(),
        name="reactivate-request",
    ),
    path(
        "candidate/resume/<str:resume_name>",
        DeleteResumeView.as_view(),
        name="delete_resume",
    ),
    path("education/", AddEducationView.as_view(), name="add-education"),
    path("certification/", AddCertificationView.as_view(), name="add-certification"),
    path(
        "education/<str:degree_name>",
        EducationDetailView.as_view(),
        name="education-detail",
    ),
    path(
        "certification/<str:certification_name>",
        CertificationDetailView.as_view(),
        name="certification-detail",
    ),
]

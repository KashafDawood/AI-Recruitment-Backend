from django.urls import path
from .views.auth_views import (
    SignupView,
    LoginView,
    LogoutAPIView,
    ProtectedAPIView,
    CookieTokenRefreshView,
    VerifyEmailOTPView,
    ResendEmailOTPView,
)
from .views.candidate_views import (
    CandidateMeView,
    CandidateListView,
    DeleteResumeView,
    AddEducationView,
    AddCertificationView,
    EducationDetailView,
    CertificationDetailView,
    UpdateBioView,
)
from .views.employer_views import EmployerMeView, EmployerListView
from .views.user_views import (
    UserView,
    GetMeView,
    UpdateMeView,
    DeleteMeView,
    ChangePasswordView,
    ChangeUsernameView,
    ForgetPasswordView,
    ResetPasswordView,
    DeactivateAccountView,
    ReactivateAccountView,
    ReactivateAccountEmailView,
    GetUserByUsernameView,
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
    path("me/", GetMeView.as_view(), name="Get Me"),
    path("update-me/", UpdateMeView.as_view(), name="Update Me"),
    path("delete-me/", DeleteMeView.as_view(), name="Delete Me"),
    path("candidate/update-bio/", UpdateBioView.as_view(), name="update-bio"),
    path("<str:username>/", GetUserByUsernameView.as_view(), name="getuserbyusername"),
]

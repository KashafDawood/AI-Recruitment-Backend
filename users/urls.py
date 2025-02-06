from django.urls import path
from .views import (
    SignupView,
    LoginView,
    ProtectedAPIView,
    CookieTokenRefreshView,
    LogoutAPIView,
    CandidateMeView,  # changed from CandidateView
    EmployerMeView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="user-signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("protected/", ProtectedAPIView.as_view(), name="protected-api"),
    path(
        "candidate/me",
        CandidateMeView.as_view(),
        name="candidate-endpoints",
    ),
    path("employer/me", EmployerMeView.as_view(), name="employer-endpoints"),
]

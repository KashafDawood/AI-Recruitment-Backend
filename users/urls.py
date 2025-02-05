from django.urls import path
from .views import SignupView, CandidateRegisterView, LoginView, ProtectedAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name= 'user-signup'),
    path('login/', LoginView.as_view(), name= 'login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('protected/', ProtectedAPIView.as_view(), name='protected-api'),
    path('register/candidate', CandidateRegisterView.as_view(), name= 'candidate-register'),
]
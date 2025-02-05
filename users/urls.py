from django.urls import path
from .views import SignupView, CandidateRegisterView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name= 'user-signup'),
    path('login/', LoginView.as_view(), name= 'login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('register/candidate', CandidateRegisterView.as_view(), name= 'candidate-register')
]
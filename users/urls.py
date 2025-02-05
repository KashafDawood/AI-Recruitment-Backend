from django.urls import path
from .views import SignupView, LoginView, ProtectedAPIView
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('signup/', SignupView.as_view(), name= 'user-signup'),
    path('login/', LoginView.as_view(), name= 'login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('protected/', ProtectedAPIView.as_view(), name='protected-api'),
]
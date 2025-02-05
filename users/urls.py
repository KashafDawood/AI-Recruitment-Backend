from django.urls import path
from .views import SignupView, CandidateRegisterView

urlpatterns = [
    path('signup/', SignupView.as_view(), name= 'user-signup'),
    path('register/candidate', CandidateRegisterView.as_view(), name= 'candidate-register')
]
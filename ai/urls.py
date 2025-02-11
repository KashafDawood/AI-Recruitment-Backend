from django.urls import path
from .views import GenerateJobPostingView, GenerateCandidateBioView

urlpatterns = [
    path(
        "generate-job-post/",
        GenerateJobPostingView.as_view(),
        name="generate-job-post",
    ),
    path(
        "generate-candidate-bio/",
        GenerateCandidateBioView.as_view(),
        name="generate-candidate-bio",
    ),
]

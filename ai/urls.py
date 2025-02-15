from django.urls import path
from .views import GenerateJobPostingView, GenerateCandidateBioView, GenerateBlogView

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
    path("generate-blog-post/", GenerateBlogView.as_view(), name="generate-blog-post"),
]

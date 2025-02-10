from django.urls import path
from .views import GenerateJobPostingView, PublishJobListingView

urlpatterns = [
    path(
        "ai/generate-job-post/",
        GenerateJobPostingView.as_view(),
        name="generate-job-post",
    ),
    path("publish-job-post/", PublishJobListingView.as_view(), name="publish-job-post"),
]

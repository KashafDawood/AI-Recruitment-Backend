from django.urls import path
from .views import (
    GenerateJobPostingView,
    PublishJobListingView,
    MyJobListingView,
    JobListingListView,
    jobListingView,
)

urlpatterns = [
    path(
        "ai/generate-job-post/",
        GenerateJobPostingView.as_view(),
        name="generate-job-post",
    ),
    path("publish-job-post/", PublishJobListingView.as_view(), name="publish-job-post"),
    path("my-job-listing/<int:id>", MyJobListingView.as_view(), name="my-jobs"),
    path("", JobListingListView.as_view(), name="get-all-jobs"),
    path("<int:id>", jobListingView.as_view(), name="get-job-by-id"),
]

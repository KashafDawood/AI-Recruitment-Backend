from django.urls import path
from .views import (
    PublishJobListingView,
    MyJobListingView,
    JobListingListView,
    jobListingView,
    FetchTenJobsView,
    EmployerJobListingsView,
)

urlpatterns = [
    path("publish-job-post/", PublishJobListingView.as_view(), name="publish-job-post"),
    path("my-job-listing/<int:id>", MyJobListingView.as_view(), name="my-jobs"),
    path(
        "employers/<str:username>/",
        EmployerJobListingsView.as_view(),
        name="employer-jobs",
    ),
    path("", JobListingListView.as_view(), name="get-all-jobs"),
    path("fetchTenJobs/", FetchTenJobsView.as_view, name="get-first-ten-jobs"),
    path("<int:id>", jobListingView.as_view(), name="get-job-by-id"),
]

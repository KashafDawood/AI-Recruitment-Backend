from django.urls import path
from .views import (
    CreateApplicationView,
    JobApplicationsListView,
)

urlpatterns = [
    path("apply/", CreateApplicationView.as_view(), name="apply-for-job"),
    path(
        "job/<int:job_id>",
        JobApplicationsListView.as_view(),
        name="job-applications-list",
    ),
]

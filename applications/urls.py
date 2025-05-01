from django.urls import path
from .views import (
    ApplyJobView,
    JobApplicationsListView,
    UpdateApplicationStatusView,
    AppliedJobsListView,
)

urlpatterns = [
    path("apply/", ApplyJobView.as_view(), name="apply-for-job"),
    path(
        "job/<int:job_id>",
        JobApplicationsListView.as_view(),
        name="job-applications-list",
    ),
    path('job/<int:job_id>/update-status/', 
         UpdateApplicationStatusView.as_view(), 
         name='update-application-status'),
    path("applied/", 
         AppliedJobsListView.as_view(), 
         name="applied-jobs-list"),
]

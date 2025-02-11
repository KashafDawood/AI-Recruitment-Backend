from django.urls import path
from .views import (
    GenerateJobPostingView,
)

urlpatterns = [
    path(
        "generate-job-post/",
        GenerateJobPostingView.as_view(),
        name="generate-job-post",
    ),
]

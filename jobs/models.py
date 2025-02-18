from django.db import models
from django.conf import settings


class JobListing(models.Model):
    JOB_LOCATION_TYPE_CHOICES = [
        ("onsite", "OnSite"),
        ("remote", "Remote"),
    ]

    JOB_TYPE_CHOICES = [
        ("internship", "InternShip"),
        ("full time", "Full Time"),
        ("part time", "Part Time"),
    ]

    JOB_STATUS_CHOICES = [("open", "Open"), ("closed", "Closed")]

    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    experience_required = models.CharField(max_length=100)
    salary = models.CharField(max_length=100, blank=True, null=True)
    job_location_type = models.CharField(
        max_length=10, choices=JOB_LOCATION_TYPE_CHOICES, default="onsite"
    )
    job_type = models.CharField(
        max_length=10, choices=JOB_TYPE_CHOICES, default="full time"
    )
    job_status = models.CharField(
        max_length=10, choices=JOB_STATUS_CHOICES, default="open"
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

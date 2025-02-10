from django.db import models
from django.conf import settings


class JobListing(models.Model):
    JOB_TYPE_CHOICES = [
        ("onsite", "OnSite"),
        ("remote", "Remote"),
    ]

    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    experience_required = models.CharField(max_length=100)
    salary = models.CharField(max_length=100, blank=True, null=True)
    job_type = models.CharField(
        max_length=10, choices=JOB_TYPE_CHOICES, default="onsite"
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

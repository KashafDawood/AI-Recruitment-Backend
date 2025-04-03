from django.db import models
from django.conf import settings
import json


class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey('JobListing', on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)


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

    EXPERIENCE_LEVEL_CHOICES = [
        ("entry", "Entry Level"),
        ("mid", "Mid Level"),
        ("senior", "Senior Level"),
        ("executive", "Executive Level"),
    ]

    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    experience_required = models.CharField(max_length=100)
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVEL_CHOICES,
        default="entry",
        blank=True,
        null=True,
    )
    salary = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    job_location_type = models.CharField(
        max_length=10, choices=JOB_LOCATION_TYPE_CHOICES, default="onsite"
    )
    job_type = models.CharField(
        max_length=10, choices=JOB_TYPE_CHOICES, default="full time"
    )
    job_status = models.CharField(
        max_length=10, choices=JOB_STATUS_CHOICES, default="open"
    )
    description = models.JSONField(default=list, blank=True)
    responsibilities = models.JSONField(default=list, blank=True)
    required_qualifications = models.JSONField(default=list, blank=True)
    preferred_qualifications = models.JSONField(default=list, blank=True)
    benefits = models.JSONField(default=list, blank=True)
    applicants = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

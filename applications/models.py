from django.db import models
from django.conf import settings


class Application(models.Model):
    APPLICATION_STATUS_CHOICES = [
        ("applied", "Applied"),
        ("interviewing", "Interviewing"),
        ("offered", "Offered"),
        ("rejected", "Rejected"),
    ]

    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    job = models.ForeignKey(
        "jobs.JobListing", on_delete=models.CASCADE, related_name="applications"
    )
    application_status = models.CharField(
        max_length=20, choices=APPLICATION_STATUS_CHOICES, default="applied"
    )
    resume = models.CharField(max_length=100)
    extracted_resume = models.CharField(blank=True, default="")
    contract = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application of {self.candidate.username} for {self.job.title}"

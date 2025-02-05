# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('candidate', 'Candidate'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    socials = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'users_user'
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username

class Candidate(User):
    skills = models.TextField()
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'users_candidate'

    def __str__(self):
        return f"Candidate: {self.username}"

class Employer(User):
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    industry = models.CharField(max_length=100)

    class Meta:
        db_table = 'users_employer'

    def __str__(self):
        return f"Employer: {self.username}"

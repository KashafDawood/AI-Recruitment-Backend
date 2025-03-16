from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from django.db import models
from core.b2_storage import BackblazeB2Storage
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ("candidate", "Candidate"),
        ("employer", "Employer"),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, null=True, blank=True, default=None
    )
    photo = CloudinaryField(
        null=True,
        blank=True,
    )
    phone = models.CharField(max_length=20, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    socials = models.JSONField(null=True, blank=True)
    changeUsernameAt = models.DateTimeField(null=True, blank=True)
    certifications = models.JSONField(default=dict, blank=True)
    education = models.JSONField(default=dict, blank=True)
    address = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "users_user"
        swappable = "AUTH_USER_MODEL"

    def __str__(self):
        return self.username


class CandidateProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="candidate_profile"
    )
    skills = models.JSONField(default=list)
    resumes = models.JSONField(default=dict)
    bio = models.TextField(null=True, blank=True)
    experience = models.PositiveIntegerField(default=0)
    interests = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        db_table = "users_candidate_profile"

    def __str__(self):
        return f"Candidate Profile: {self.user.username}"

    def add_resume(self, resume_file, resume_name):

        storage = BackblazeB2Storage()
        resume_path = storage._save(resume_name, resume_file)

        resume_data = {
            "name": resume_name,
            "resume": storage.url(resume_path),
            "created_at": timezone.now().isoformat(),
        }
        self.resumes[resume_name] = resume_data
        self.save()

    def delete_resume(self, resume_name):
        if resume_name in self.resumes:
            del self.resumes[resume_name]
            self.save()
            return True
        return False


class EmployerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employer_profile"
    )
    company_name = models.CharField(max_length=255)
    logo = CloudinaryField(
        null=True,
        blank=True,
    )
    industry = models.CharField(max_length=100)
    about_company = models.TextField(null=True, blank=True)
    company_size = models.CharField(max_length=25, null=True, blank=True)

    class Meta:
        db_table = "users_employer_profile"

    def __str__(self):
        return f"Employer Profile: {self.user.username}"

from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField


class Blog(models.Model):
    blog_status_choices = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    thumbnail = CloudinaryField(
        null=True,
        blank=True,
    )
    keywords = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, choices=blog_status_choices, default="draft"
    )
    slug = models.SlugField(max_length=255, unique=True)
    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blogs",
    )
    category = models.CharField(max_length=100, blank=True) 

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"

    def __str__(self):
        return self.title

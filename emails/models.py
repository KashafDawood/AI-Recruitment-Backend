from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random


class EmailOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        return super().save(*args, **kwargs)

    @staticmethod
    def generate_otp():
        return f"{random.randint(100000, 999999)}"

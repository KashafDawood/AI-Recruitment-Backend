from django.core.mail import send_mail
from django.conf import settings
from .models import EmailOTP


def send_otp_email(email, otp):
    subject = "Your OTP for Signup Verification"
    message = f"Your OTP is {otp}. Please enter this to verify your email. The OTP will expire after 10 minutes."

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


def generate_otp(user):
    otp_code = EmailOTP.generate_otp()
    EmailOTP.objects.create(user=user, otp=otp_code)
    send_otp_email(user.email, otp_code)

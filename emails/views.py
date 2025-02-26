from .email import send_simple_message
from .models import EmailOTP
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


def send_otp_email(email, otp):
    subject = "Your OTP for Signup Verification"
    message = f"Your OTP is {otp}. Please enter this to verify your email. The OTP will expire after 10 minutes."
    html_message = render_to_string(
        "./otp_email_template.html", {"otp": otp, "expiry_minutes": 10}
    )
    send_simple_message(subject, message, [email], html_message=html_message)


def generate_otp(user):
    """
    Generate and send OTP to user email
    """
    # First, invalidate any existing unused OTPs for this user
    EmailOTP.objects.filter(
        user=user, verified=False, expires_at__gt=timezone.now()
    ).update(expires_at=timezone.now())

    # Generate a new OTP
    otp_code = EmailOTP.generate_otp()

    # Create and save the OTP
    otp_obj = EmailOTP(
        user=user,
        otp=otp_code,
    )
    otp_obj.save()

    # Send email with OTP
    subject = "Email Verification OTP"
    message = f"Your OTP code is: {otp_code}. It will expire in 10 minutes."
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        send_mail(subject, message, email_from, recipient_list)
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return False


def send_forget_password_email(email, url):
    subject = "Reset Your Password"
    message = "Click the link below to reset your password. If you did not request a password reset, please ignore this email."
    html_message = render_to_string(
        "./forget_password_email_template.html", {"email": email, "url": url}
    )
    send_simple_message(subject, message, [email], html_message=html_message)


def send_reactivate_account_email(email, url):
    subject = "Reactivate Your Account"
    message = "Click the link below to reactivate your account. If you did not request this action, please ignore this email."
    html_message = render_to_string(
        "./reactivate_account_email_template.html", {"email": email, "url": url}
    )
    send_simple_message(subject, message, [email], html_message=html_message)

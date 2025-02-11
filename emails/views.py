from .email import send_simple_message
from .models import EmailOTP
from django.template.loader import render_to_string


def send_otp_email(email, otp):
    subject = "Your OTP for Signup Verification"
    message = f"Your OTP is {otp}. Please enter this to verify your email. The OTP will expire after 10 minutes."
    html_message = render_to_string(
        "./otp_email_template.html", {"otp": otp, "expiry_minutes": 10}
    )
    send_simple_message(subject, message, [email], html_message=html_message)


def generate_otp(user):
    otp_code = EmailOTP.generate_otp()
    EmailOTP.objects.create(user=user, otp=otp_code)
    send_otp_email(user.email, otp_code)


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

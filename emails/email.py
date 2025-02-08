from django.core.mail import send_mail
from django.conf import settings


def send_custom_email(subject, message, recipient_list, html_message=None):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
        html_message=html_message,  # For HTML templates
    )

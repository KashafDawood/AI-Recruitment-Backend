import requests
from django.conf import settings


def send_simple_message(subject, text, recipient_list, html_message=None):
    # TODO Remove later
    if settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
        # Log email details to console
        print("----- Email Sent to Console -----")
        print("Subject:", subject)
        print("Text:", text)
        print("Recipients:", recipient_list)
        if html_message:
            print("HTML:", html_message)
        print("----- End Email -----")
        return None
    data = {
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": recipient_list,
        "subject": subject,
        "text": text,
    }
    if html_message:
        data["html"] = html_message
    return requests.post(
        f"https://api.mailgun.net/v3/{settings.ANYMAIL['MAILGUN_SENDER_DOMAIN']}/messages",
        auth=("api", settings.ANYMAIL["MAILGUN_API_KEY"]),
        data=data,
    )

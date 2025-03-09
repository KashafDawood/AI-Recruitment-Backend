import requests
from django.conf import settings
from django.template.loader import render_to_string


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


def send_contract_email(email, contract_url, company_name, job_title):
    """
    Send an email to the candidate with the contract link

    Args:
        email (str): Recipient email address
        contract_url (str): URL to the contract document
        company_name (str): Name of the employer company
        job_title (str): Job title for the position offered
    """
    subject = f"Your Employment Contract for {job_title} at {company_name}"
    text_message = (
        f"Congratulations! We are pleased to offer you a position with {company_name} as {job_title}. "
        f"Please review your employment contract at: {contract_url}\n\n"
        f"Important: This contract will expire in 7 days if not completed."
    )

    html_message = render_to_string(
        "./contract_email_template.html",
        {
            "contract_url": contract_url,
            "company_name": company_name,
            "job_title": job_title,
        },
    )

    return send_simple_message(
        subject, text_message, [email], html_message=html_message
    )

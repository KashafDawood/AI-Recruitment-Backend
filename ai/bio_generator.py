import os
import json
import re
from io import BytesIO
import requests
from openai import OpenAI
from django.conf import settings
from users.models import CandidateProfile
import PyPDF2
import docx


def parse_pdf_resume(file_stream):
    """Extract text from a PDF resume."""
    reader = PyPDF2.PdfReader(file_stream)
    text = "\n".join(
        [page.extract_text() for page in reader.pages if page.extract_text()]
    )
    return text


def parse_docx_resume(file_stream):
    """Extract text from a DOCX resume."""
    doc = docx.Document(file_stream)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def extract_info_using_ai(text):
    """Extract structured information from the resume text using OpenAI."""
    prompt = f"""
    Extract the following information from the resume text below in JSON format:
    - education
    - experience
    - certifications
    - languages
    
    Resume:
    {text}
    
    The output must be valid JSON with keys "education", "experience", "certifications", and "languages", and no additional text.
    """

    client = OpenAI(
        base_url=settings.OPENAI_ENDPOINT,
        api_key=settings.OPENAI_TOKEN,
    )

    completion = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that extracts resume details in JSON format.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )

    response_content = completion.choices[0].message.content.strip()

    # Ensure valid JSON extraction
    if response_content.startswith("```") and response_content.endswith("```"):
        response_content = re.sub(r"^```json\s*", "", response_content)
        response_content = re.sub(r"\s*```$", "", response_content)

    try:
        data = json.loads(response_content)
    except json.JSONDecodeError:
        data = {
            "education": "Not provided",
            "experience": "Not provided",
            "certifications": [],
            "languages": [],
        }

    return data


def parse_resume(resume_url):
    """Parse a resume from a URL (PDF or DOCX) and extract text."""
    if settings.DEBUG and (
        resume_url.startswith(settings.MEDIA_URL) or resume_url.startswith("/media/")
    ):
        # Local file handling in DEBUG mode
        relative_path = (
            resume_url[len(settings.MEDIA_URL) :]
            if resume_url.startswith(settings.MEDIA_URL)
            else resume_url
        )
        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        file_stream = BytesIO(file_bytes)
        extension_check = file_path
    else:
        # Remote file handling
        if not resume_url.startswith("http"):
            resume_url = settings.BASE_URL.rstrip("/") + resume_url
        response = requests.get(resume_url)
        file_stream = BytesIO(response.content)
        extension_check = resume_url

    if extension_check.endswith(".pdf"):
        text = parse_pdf_resume(file_stream)
    elif extension_check.endswith(".docx"):
        text = parse_docx_resume(file_stream)
    else:
        raise ValueError("Unsupported file format")

    return extract_info_using_ai(text)


def generate_candidate_bio(candidate):
    """Generate a well-structured candidate bio using AI."""
    candidate_profile = CandidateProfile.objects.get(user__id=candidate.id)
    user = candidate_profile.user
    name = user.name
    education = user.education
    experience = "Not provided"
    skills = candidate_profile.skills
    certifications = (
        user.certifications if isinstance(user.certifications, list) else []
    )

    # Get the latest resume
    resume = None
    if candidate_profile.resumes:
        latest_resume = max(
            candidate_profile.resumes.values(), key=lambda x: x["created_at"]
        )
        resume = latest_resume.get("resume")

    if not resume and not skills:
        raise ValueError(
            "Skills are required to generate the candidate bio. Please add skills."
        )

    if resume:
        parsed = parse_resume(resume)
        education = parsed.get("education", education)
        experience = parsed.get("experience", experience)
        parsed_certifications = parsed.get("certifications", [])
        certifications.extend(parsed_certifications)

    # Ensure certifications are properly formatted
    certifications = [
        (
            cert["certification_name"]
            if isinstance(cert, dict) and "certification_name" in cert
            else str(cert)
        )
        for cert in certifications
    ]
    certifications = list(
        set(filter(None, certifications))
    )  # Remove empty values and duplicates

    # Construct candidate details
    candidate_details = f"""
    - **Name:** {name}
    - **Education:** {json.dumps(education, indent=2)}
    - **Experience:** {experience}
    - **Skills:** {skills}
    - **Certifications:** {', '.join(certifications)}
    """

    # AI prompt for generating candidate bio
    prompt = f"""
    IMPORTANT:
    - Generate a well-formatted candidate bio using Markdown. Ensure proper sectioning and formatting without inserting unnecessary newline characters. Don't use \\n in the output.

    Candidate Details:
    {candidate_details}

    **Structure the output as follows (avoid extra newline characters):**
    - Education, Experience, Skills (Formatted clearly)
    - A compelling bio description (2-3 paragraphs)
    - Key Achievements (Bulleted list)
    - Technical Skills (Bulleted list)
    - Certifications (Bulleted list)
    - Contact Information (Clear Call to Action)
    """

    client = OpenAI(
        base_url=settings.OPENAI_ENDPOINT,
        api_key=settings.OPENAI_TOKEN,
    )

    completion = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        store=True,
        messages=[
            {
                "role": "system",
                "content": "You are a professional HR assistant who formats candidate bios professionally.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    return completion.choices[0].message.content

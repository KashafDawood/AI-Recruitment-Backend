import os
import json
from io import BytesIO
import requests
from openai import OpenAI
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
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


def extract_info_using_nltk(text):
    """Extract structured information from the resume text using NLTK."""
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    filtered_words = [w for w in words if w.lower() not in stop_words]

    # Dummy extraction logic for demonstration purposes
    education = [sent for sent in sentences if "education" in sent.lower()]
    experience = [sent for sent in sentences if "experience" in sent.lower()]
    certifications = [sent for sent in sentences if "certification" in sent.lower()]
    languages = [
        word
        for word in filtered_words
        if word.lower() in ["english", "spanish", "french"]
    ]

    data = {
        "education": education if education else "Not provided",
        "experience": experience if experience else "Not provided",
        "certifications": certifications,
        "languages": languages,
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

    return extract_info_using_nltk(text)


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

    # Determine the most suitable data to use
    final_education = (
        education
        if education != "Not provided"
        else parsed.get("education", "Not provided")
    )
    final_experience = (
        experience
        if experience != "Not provided"
        else parsed.get("experience", "Not provided")
    )
    final_skills = skills if skills else parsed.get("skills", [])
    final_certifications = (
        certifications if certifications else parsed.get("certifications", [])
    )

    # Construct candidate details
    candidate_details = f"""
    - **Name:** {name}
    - **Education:** {json.dumps(final_education, indent=2)}
    - **Experience:** {final_experience}
    - **Skills:** {final_skills}
    - **Certifications:** {', '.join(final_certifications)}
    """

    # AI prompt for generating candidate bio
    prompt = f"""
    Write a concise and engaging candidate bio in FIRST PERSON perspective (using "I am" instead of third person), suitable for LinkedIn, job applications, or professional profiles. Keep it under 200-400 words, highlighting expertise, achievements, and career aspirations. Format the bio using HTML tags, including <strong> for important keywords and <em> for emphasis.

    Candidate Details:
    {candidate_details}

    Example Output:
    "I am a dedicated and results-oriented [Job Title] with [X] years of experience in [Industry]. Skilled in [Key Skills], I have successfully contributed to [mention impact, projects, or achievements]. I am passionate about [mention career focus] and thrive in [work environment, e.g., collaborative teams, fast-paced settings]. I am seeking opportunities to leverage my expertise in [mention job role or industry] and make a meaningful impact in [specific field]."
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

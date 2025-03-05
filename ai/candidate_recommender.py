from openai import OpenAI
from django.conf import settings
import PyPDF2
import io
import requests


def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        # If pdf_file is already bytes or file-like object
        pdf_reader = PyPDF2.PdfReader(
            io.BytesIO(pdf_file) if isinstance(pdf_file, bytes) else pdf_file
        )

        # Extract text from each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"

        return text
    except Exception as e:
        # Handle exceptions gracefully
        return f"Error extracting text from PDF: {str(e)}"


def download_pdf_from_url(url):
    """Download PDF content from URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        return io.BytesIO(response.content)
    except Exception as e:
        return f"Error downloading PDF: {str(e)}"


def parse_applications(applications):
    parsed_applications = []

    for app in applications:
        # Extract resume URL from the dictionary
        resume_url = app.get("resume")

        # Download PDF content from URL
        pdf_content = download_pdf_from_url(resume_url)

        # Extract text from PDF content
        resume_content = extract_text_from_pdf(pdf_content)

        # Format the application data
        app_text = f"""
        Application ID: {app.get('id')}
        Candidate ID: {app.get('candidate')}
        Candidate Username: {app.get('candidate_username')}
        Job Title: {app.get('job_title')}
        
        Resume Content:
        {resume_content}
        
        ---
        """
        parsed_applications.append(app_text)

    return "\n".join(parsed_applications)


def recommend_best_candidate(applications, job_description):
    # Parse applications into a format suitable for AI analysis
    formatted_applications = parse_applications(applications)

    prompt = f"""
    You are a professional HR assistant. Please analyze the candidates below and recommend the best match for the job description.

    Job Description:
    {job_description}
    
    Candidates Applications:
    {formatted_applications}
    
    Please provide:
    1. The list of best candiate with the score of 90 to 100
    2. A brief explanation of why they are the best match
    3. Top 3 skills that make them suitable for this role
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
                "content": "You are a professional HR assistant who analyzes candidate applications and recommends the best match.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content

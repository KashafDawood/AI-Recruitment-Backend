from openai import OpenAI
from django.conf import settings
import json


def generate_job_listing(
    requirements,
    job_title=None,
    company=None,
    location=None,
    experience_required=None,
    salary_range=None,
):
    prompt = f"""
    Generate a well-structured job listing based on the following details:
    - Job Title: {job_title}
    - Company: {company}
    - Location: {location}
    - Requirements: {requirements}
    - Experience: {experience_required}
    - Salary: {salary_range}
    
    IMPORTANT: Return the response as a structured JSON object with the following fields:
    - title: Job title
    - meta: Object containing company, location, experience, and salary
    - description: Array of paragraphs for the job description
    - responsibilities: Array of key responsibilities
    - required_qualifications: Array of required skills and qualifications
    - preferred_qualifications: Array of preferred skills and qualifications
    - benefits: Array of benefits and reasons to join
    - application_instructions: Application process details
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
                "content": "You are a professional HR assistant who creates structured job listings in JSON format.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    response_content = completion.choices[0].message.content
    job_lising = json.loads(response_content)
    return job_lising

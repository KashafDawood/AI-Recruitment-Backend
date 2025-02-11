from openai import OpenAI
from django.conf import settings


def generate_job_listing(
    job_title,
    company,
    location,
    requirements,
    experience_required,
    salary_range=None,
    benefits=None,
):
    prompt = f"""
    IMPORTANT:
    - Generate a well-formatted job listing using Markdown. Ensure proper sectioning and formatting without inserting unnecessary newline characters. Don't need to add the company email as all candidate will apply through the portal. don't use \\n in the output

    Job Details:
    - **Job Title:** {job_title}
    - **Company:** {company}
    - **Location:** {location}
    - **Requirements:** {requirements}
    - **Experience:** {experience_required}
    - **Salary:** {salary_range or 'Not specified'}
    - **benefits** {benefits}

    **Structure the output as follows (avoid extra newline characters):**
    - Job Title (H2)
    - Company, Location, Experience, Salary (Formatted Clearly in a single line separate them with '|' )
    - A compelling job description (2-3 paragraphs)
    - Key Responsibilities (Bulleted list)
    - Required Qualifications and Skills (Bulleted list)
    - Preferred Qualifications (Bulleted list)
    - Why Join Us? (Engaging description with bullet points)
    - Application Instructions (Clear Call to Action)
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
                "content": "You are a professional HR assistant who formats job listings professionally.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content


# ...existing code...

from openai import OpenAI
from django.conf import settings
import json


def job_filtering(job_details):
    # Convert job_details to dict if it's a string
    if isinstance(job_details, str):
        try:
            job_details = json.loads(job_details)
        except json.JSONDecodeError:
            # Handle as a text block if not valid JSON
            pass

    prompt = f"""
        I need you to analyze this job posting and filter it based on our standard policies. 
        Please analyze each field and only modify those that violate our policies.

        Job posting: {job_details}

        Please evaluate according to these policies:
        1. No discriminatory language or requirements based on age, gender, race, religion, or disability
        2. No unrealistic job expectations (e.g., entry-level positions requiring 10+ years of experience)
        3. No unethical practices or requirements
        4. Salary transparency (preferred but not required)
        5. Clear job responsibilities and qualifications
        6. No misleading titles or descriptions

        Return a JSON object with:
        1. "approved" (boolean): Whether the job posting is approved as-is or needs modifications
        2. "policy_violations" (array): List of specific violations found (empty if approved)
        3. "modified_job" (object): The job details with any problematic fields corrected
        
        The modified_job should have the SAME structure as the input job posting, with changes ONLY to fields that violate policies.
        Do not modify fields that do not violate policies.
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
                "content": "You are a professional HR assistant who analyzes job listings for policy violations and makes targeted corrections while preserving the original structure.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    response_content = completion.choices[0].message.content
    result = json.loads(response_content)

    return result

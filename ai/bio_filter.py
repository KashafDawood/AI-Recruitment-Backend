from django.conf import settings
from openai import OpenAI
import re


def contains_inappropriate_content(text):
    # Basic patterns for detecting potentially inappropriate content
    patterns = [
        r"\b(fuck|shit|damn|bitch|ass|crap|dick|pussy|cock|whore|slut)\b",  # Profanity
        r"\b(stupid|idiot|moron|dumb|retard)\b",  # Derogatory terms
        r"\b(hate|kill|murder|attack|destroy)\b",  # Violent terms
        r"\b(nazi|racist|sexist|homophobic|transphobic)\b",  # Discriminatory terms
    ]

    # Check for patterns
    for pattern in patterns:
        if re.search(pattern, text.lower()):
            return True

    return False


def filter_bio(bio):
    # First check if the bio contains inappropriate content
    if not contains_inappropriate_content(bio):
        return bio  # Return original if clean

    prompt = f"""
    Please review the following candidate bio to ensure it aligns with company policies and maintains professionalism.  

    **Company Bio Policy:**  
    All candidate bios must maintain a professional tone, be free from inappropriate language, and align with company policies. Any content that includes offensive, discriminatory, or unprofessional wording will be removed or modified. Bios should accurately represent the candidate's qualifications and experience while maintaining respect and integrity.  

    **Instructions:**  
    - Identify and remove any inappropriate wording, abusive language, or policy violations.  
    - Ensure the bio remains professional, appropriate, and well-structured.  
    - Retain the original intent while improving clarity and professionalism if necessary.  
    - Keep the same perspective, length and tone of the original bio where appropriate.
    - Provide only the refined bio text without any additional notes or prefixes.
    - Only make changes if there are inappropriate or unprofessional elements, otherwise preserve the original text.

    **Candidate Bio:**  
    {bio}  
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

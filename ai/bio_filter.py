from django.conf import settings
from openai import OpenAI
import re

def filter_bio(bio):
    """Filter and clean the candidate bio to ensure it contains no inappropriate wording or policy violations."""
    # AI prompt for checking and cleaning the bio
    
    prompt = f"""
    Please review the following candidate bio to ensure it aligns with company policies and maintains professionalism.  

    **Company Bio Policy:**  
    All candidate bios must maintain a professional tone, be free from inappropriate language, and align with company policies. Any content that includes offensive, discriminatory, or unprofessional wording will be removed or modified. Bios should accurately represent the candidate’s qualifications and experience while maintaining respect and integrity.  

    **Instructions:**  
    - Identify and remove any inappropriate wording, abusive language, or policy violations.  
    - Ensure the bio remains professional, appropriate, and well-structured.  
    - Retain the original intent while improving clarity and professionalism if necessary.  
    - Expand the bio to make it more detailed, engaging, and attractive while keeping it concise and relevant.  
    - Provide only the refined bio text in HTML format without any additional notes or prefixes.  

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

    cleaned_bio = completion.choices[0].message.content.strip()

    return cleaned_bio

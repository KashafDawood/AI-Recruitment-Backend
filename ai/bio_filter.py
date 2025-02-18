from django.conf import settings
from openai import OpenAI

def filter_bio(bio):
    """Filter and clean the candidate bio to ensure it contains no inappropriate wording or policy violations."""
    # AI prompt for checking and cleaning the bio
    prompt = f"""
    Please review the following candidate bio and check for any inappropriate wording, abusive language, or content that violates company policies. 
    Ensure it is professional, appropriate, and free of any offensive or unprofessional language.
    If necessary, clean up the bio while maintaining its original intent and professionalism.

    Bio:
    {bio}

    Cleaned Bio:
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
    return cleaned_bio if cleaned_bio != bio else None

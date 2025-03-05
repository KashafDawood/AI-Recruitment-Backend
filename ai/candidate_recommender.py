from openai import OpenAI
from django.conf import settings


def recommend_best_candidate():
    prompt = f"""
    
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

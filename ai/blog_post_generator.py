from openai import OpenAI
from django.conf import settings


def generate_blog_post(
    blog_title,
    blog_description,
    focus_keywords,
    blog_length="600 words",
):

    blog_detail = {
        "blog_breif": blog_description,
        "focus_keywords": focus_keywords,
        "blog_length": blog_length,
    }

    prompt = f"""
    Write a detailed, SEO-optimized blog post on the topic: **"{blog_title}"** following Google's EEAT (Experience, Expertise, Authoritativeness, and Trustworthiness) guidelines.

    ### **Blog details:**
    {blog_detail}

    ### **Requirements:**
    - The post should be **well-researched, engaging, and plagiarism-free**.
    - Use **short paragraphs, bullet points, and subheadings (H2, H3, H4) for readability**.
    - Include a strong **introduction** that hooks the reader and explains the importance of the topic.
    - Provide in-depth **analysis, real-world examples, expert opinions, and data-backed insights**.
    - Follow an **informative yet conversational tone**, maintaining **clarity and credibility**.
    - Use **SEO-friendly keywords** naturally throughout the content.
    - End with a compelling **conclusion + CTA (Call-to-Action)** to engage readers.

    ### **Structure:**

    **Title:** [Click-Worthy Title with Keywords]

    **Introduction**
    - Hook the reader with an interesting fact, question, or statement.
    - Explain why the topic is important and relevant.
    - Provide a brief overview of what the post will cover.

    **Main Content (Use H2, H3 for subheadings)**
    - **What is {blog_title}?** (Define the topic with simple, clear explanations)
    - **Why is {blog_title} Important?** (Explain benefits, industry impact, etc.)
    - **Key Benefits or Challenges** (Use bullet points for easy reading)
    - **Best Practices/Tips for {blog_title}** (Actionable insights for readers)
    - **Real-World Examples or Case Studies** (Boosts credibility)
    - **Common Mistakes & How to Avoid Them**

    **Conclusion**
    - Summarize the key takeaways.
    - Include a strong Call-to-Action (e.g., "Start implementing these tips today!" or "Share your thoughts in the comments!").
    - Don't make heading with the text "call to action"

    **Tone & Style:**
    - **Conversational, engaging, and informative**
    - **Authoritative but easy to understand**
    - **Optimized for search engines and user engagement**
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
                "content": "You are a professional content writer who creates SEO-optimized blog posts.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content

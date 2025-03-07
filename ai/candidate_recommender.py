from openai import OpenAI
from django.conf import settings
import PyPDF2
import io
import requests
import json


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
        try:
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
            Candidate Name: {app.get('candidate_name', app.get('candidate_username', 'Unknown'))}
            Job Title: {app.get('job_title')}
           
            Resume Content:
            {resume_content}
           
            ---
            """
            parsed_applications.append(
                {
                    "application_id": app.get("id"),
                    "candidate_id": app.get("candidate"),
                    "candidate_name": app.get(
                        "candidate_name", app.get("candidate_username", "Unknown")
                    ),
                    "resume_text": resume_content,
                }
            )
        except Exception as e:
            # Handle errors for individual applications without failing the entire process
            parsed_applications.append(
                {
                    "application_id": app.get("id", "Unknown"),
                    "candidate_id": app.get("candidate", "Unknown"),
                    "candidate_name": app.get(
                        "candidate_name", app.get("candidate_username", "Unknown")
                    ),
                    "resume_text": f"Error processing resume: {str(e)}",
                }
            )

    return parsed_applications


def recommend_best_candidate(applications, job_description, limit=5, minimum_score=70):
    # Parse applications into a format suitable for AI analysis
    parsed_applications = parse_applications(applications)

    prompt = f"""
    You are a professional HR assistant specializing in candidate evaluation.
    
    Job Description:
    {job_description}
    
    Candidates Applications:
    {json.dumps(parsed_applications, indent=2)}
    
    Analyze each candidate's resume against the job description.
    
    Return a JSON response with the following structure:
    {{
      "recommendations": [
        {{
          "rank": 1,
          "candidate_id": "candidate_id",
          "application_id": "application_id",
          "candidate_name": "candidate_name",
          "match_score": 85.5,
          "match_reasons": [
            {{
              "category": "skills|experience|education|cultural_fit",
              "strength": "strong|moderate|weak",
              "details": "Specific reason for match"
            }}
          ],
          "gaps": [
            {{
              "category": "skills|experience|education|certifications",
              "importance": "high|medium|low",
              "details": "Specific missing qualification"
            }}
          ]
        }}
      ],
      "metadata": {{
        "total_candidates_evaluated": number,
        "job_description_summary": "Brief summary of key requirements",
        "processing_time_ms": 0
      }}
    }}
    
    Important guidelines:
    1. Only include candidates with a match score of {minimum_score} or higher
    2. Limit to top {limit} candidates
    3. Provide at least 2-3 specific match reasons per candidate
    4. Identify any critical gaps or missing qualifications
    5. Ensure scores accurately reflect how well candidates match the specific job requirements
    6. Consider both technical skills and soft skills in your evaluation
    """

    client = OpenAI(
        base_url=settings.OPENAI_ENDPOINT,
        api_key=settings.OPENAI_TOKEN,
    )

    try:
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional HR assistant who analyzes candidate applications and recommends the best matches. You provide structured JSON responses with detailed analysis.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        # Parse the response to ensure it's valid JSON
        response_content = completion.choices[0].message.content
        recommendations = json.loads(response_content)
        return recommendations

    except Exception as e:
        # Handle API errors gracefully
        return {
            "error": str(e),
            "recommendations": [],
            "metadata": {
                "total_candidates_evaluated": len(applications),
                "error_details": str(e),
            },
        }

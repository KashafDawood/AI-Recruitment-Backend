from docx import Document
import os
from openai import OpenAI
from django.conf import settings

def generate_contract(data):
    prompt = f"""
    Generate a professional employment contract with the following details:

    Employer: {data['employer_name']}, a company organized and existing under the laws of {data['state']}, with its principal office located at {data['employer_address']}
    Employee: {data['employee_name']}, residing at {data['employee_address']}
    Job Title: {data['job_title']}
    Start Date: {data['start_date']}
    End Date: {data.get('end_date', 'Not specified')}
    Salary: {data['salary']}
    Responsibilities: {data['responsibilities']}
    Benefits: {data.get('benefits', 'Not specified')}
    Terms: {data['terms']}

    The contract should be **formal, concise, and legally structured**.
    - Do NOT use square brackets around terms like "Agreement," "Employer," or "Employee."
    - Ensure that names provided in the input are used directly without placeholders like "[Insert Name]."
    - Do NOT include a generic "Title" section at the end unless explicitly mentioned in the input.
    - Write in full paragraphs and keep section titles simple (e.g., "Job Title", "Salary", "Responsibilities").
    - Use legal language but keep it readable.
    - Ensure the contract fits within 2-3 pages and removes extra whitespace.
    - Provide a clear signature section at the end for both parties.
    """


    client = OpenAI(
        base_url=settings.OPENAI_ENDPOINT,
        api_key=settings.OPENAI_TOKEN,
    )

    completion = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a professional HR assistant who generates clean and concise employment contracts without unnecessary symbols.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,  # Reduce randomness for more structured output
    )

    contract_content = completion.choices[0].message.content.strip()

    # Remove Markdown code block markers if they appear
    if contract_content.startswith("```"):
        contract_content = contract_content.strip("```").strip()

    # Create a Word document
    document = Document()
    document.add_heading('Employment Contract', 0)

    # Ensure proper paragraph formatting
    for line in contract_content.split("\n\n"):  # Avoids excess empty lines
        document.add_paragraph(line.strip())

    # Ensure the contracts directory exists
    contracts_dir = 'contracts'
    if not os.path.exists(contracts_dir):
        os.makedirs(contracts_dir)

    contract_path = os.path.join(contracts_dir, f"{data['employee_name']}_contract.docx")
    document.save(contract_path)
    return contract_path

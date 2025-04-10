import PyPDF2
import io
import requests


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

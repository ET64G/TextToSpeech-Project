import pdfplumber
from typing import Optional

def extract_text_from_pdf(path: str) -> Optional[str]:
    """
    Extracts text from all pages in a PDF file.
    Returns the text as a single string, or None if no text was found.
    """
    try:
        all_text = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text.append(text)
        
        joined = "\n".join(all_text).strip()
        return joined or None
    except Exception as e:
        # For now jusr re-raise; GUI will handle showing a message
        raise RuntimeError(f"Failed to read PDF: {e}") from e
        
    
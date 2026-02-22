import pdfplumber


def extract_text_corpus(pdf_path: str) -> str:
    """
    Extract and clean text from a PDF file, returning a single string
    corpus ready to be appended to an LLM prompt.

    Args:
        pdf_path: Absolute or relative path to the PDF file.

    Returns:
        A cleaned, newline-separated text corpus from all pages.
    """
    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())

    return "\n\n".join(pages)

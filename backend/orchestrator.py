import os

from services.pdf_parser import extract_text_corpus
from services.chroma_query import chroma_query
from anything import call_llm
from response_validator import call_with_retry

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompt")

PROMPT_MAP = {
    "vulnerability_detection": "vulnerability_detection.txt",
    "legal_risk_scoring": "legal_risk_scoring.txt",
    "pii_masking": "pii_masking.txt",
}


def load_prompt(selection: str) -> str:
    """Load the prompt text for the given user selection."""
    filename = PROMPT_MAP.get(selection)
    if filename is None:
        raise ValueError(
            f"Unknown selection '{selection}'. "
            f"Valid options: {list(PROMPT_MAP.keys())}"
        )
    prompt_path = os.path.join(PROMPTS_DIR, filename)
    with open(prompt_path, "r") as f:
        return f.read().strip()


def run_analysis(pdf_path: str, selection: str) -> dict:
    """
    Full pipeline:
      1. Extract text corpus from PDF.
      2. Query ChromaDB for relevant context chunks.
      3. Load the prompt for the user's selection.
      4. Send all three to AnythingLLM, retrying up to 3 times if the
         response is not valid JSON matching the expected schema.

    Args:
        pdf_path:  Path to the PDF file to analyse.
        selection: One of 'vulnerability_detection', 'legal_risk_scoring', 'pii_masking'.

    Returns:
        Parsed dict matching the schema for the given selection.

    Raises:
        RuntimeError: If the LLM fails to return valid JSON after 3 attempts.
    """
    # 1. PDF → text corpus
    pdf_text = extract_text_corpus(pdf_path)

    # 2. ChromaDB context
    chroma_chunks = chroma_query(pdf_text)
    chroma_context = "\n\n".join(chroma_chunks)

    # 3. Task-specific prompt
    prompt_text = load_prompt(selection)

    # 4. Assemble message for the LLM
    message = (
        f"{prompt_text}\n\n"
        f"--- Relevant Context ---\n{chroma_context}\n\n"
        f"--- Document Text ---\n{pdf_text}"
    )

    # 5. Call LLM with retry + JSON validation
    return call_with_retry(call_llm, message, selection)

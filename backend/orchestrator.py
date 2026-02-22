import os

from services.pdf_processor import process_pdf_to_queries
from services.chroma_query import ChromaQueryService
from anything import call_llm
from response_validator import call_with_retry

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompt")

PROMPT_MAP = {
    "vulnerability_detection": "vulnerability_detection.txt",
    "legal_risk_scoring": "legal_risk_scoring.txt",
    "pii_masking": "pii_masking.txt",
}

chroma = ChromaQueryService()


def load_prompt(selection: str) -> str:
    filename = PROMPT_MAP.get(selection)
    if filename is None:
        raise ValueError(
            f"Unknown selection '{selection}'. "
            f"Valid options: {list(PROMPT_MAP.keys())}"
        )
    with open(os.path.join(PROMPTS_DIR, filename), "r") as f:
        return f.read().strip()


def _aggregate(results: list[dict], selection: str) -> dict:
    """Merge per-chunk LLM results into a single response dict."""
    if selection == "vulnerability_detection":
        findings = []
        for r in results:
            findings.extend(r.get("findings", []))
        return {"findings": findings}

    elif selection == "legal_risk_scoring":
        findings = []
        scores = []
        for r in results:
            findings.extend(r.get("findings", []))
            if isinstance(r.get("score"), (int, float)):
                scores.append(r["score"])
        score = round(sum(scores) / len(scores)) if scores else 0
        return {"score": score, "findings": findings}

    elif selection == "pii_masking":
        instances = []
        for r in results:
            instances.extend(r.get("pii_instances", []))
        return {"pii_instances": instances}

    return {}


def run_analysis(pdf_path: str, selection: str) -> dict:
    """
    Full pipeline:
      1. Split PDF into chunks via pdf_processor.
      2. For each chunk, retrieve top-3 ChromaDB references.
      3. Build a prompt message per chunk and call AnythingLLM with retry.
      4. Aggregate all per-chunk results into a single response dict.

    Args:
        pdf_path:  Path to the PDF file to analyse.
        selection: One of 'vulnerability_detection', 'legal_risk_scoring', 'pii_masking'.

    Returns:
        Aggregated dict matching the schema for the given selection.
    """
    prompt_text = load_prompt(selection)
    chunks = process_pdf_to_queries(pdf_path)
    results = []

    for chunk in chunks:
        references = chroma.get_top_3_matches(chunk)
        chroma_context = "\n\n".join(references)

        message = (
            f"{prompt_text}\n\n"
            f"--- Relevant Context ---\n{chroma_context}\n\n"
            f"--- Document Chunk ---\n{chunk}"
        )

        result = call_with_retry(call_llm, message, selection)
        results.append(result)

    return _aggregate(results, selection)

import os

from .services.pdf_processor import process_pdf_to_queries
from .services.chroma_query import ChromaQueryService
from .anything import call_llm
from .response_validator import call_with_retry

# --- 1. Hardcoded Fixed PDF Path ---
FIXED_PDF_PATH = os.path.join(os.path.dirname(__file__), "temp_uploaded_contract.pdf")

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompt")

PROMPT_MAP = {
    "vulnerability_detection": "vulnerability_detection.txt",
    "legal_risk_scoring": "legal_risk_scoring.txt",
    "pii_masking": "pii_masking.txt",
}

chroma = ChromaQueryService(r"C:\Users\hackathon user\Documents\SentinelAI\cuad_chroma_db")


def load_prompt(analysis_mode: str) -> str:
    filename = PROMPT_MAP.get(analysis_mode)
    if filename is None:
        raise ValueError(
            f"Unknown analysis mode '{analysis_mode}'. "
            f"Valid options: {list(PROMPT_MAP.keys())}"
        )
    with open(os.path.join(PROMPTS_DIR, filename), "r") as f:
        return f.read().strip()


def _aggregate(results: list[dict], analysis_mode: str) -> dict:
    """Merge per-chunk LLM results into a single response dict."""
    if analysis_mode == "vulnerability_detection":
        findings = []
        for r in results:
            findings.extend(r.get("findings", []))
        return {"findings": findings}

    elif analysis_mode == "legal_risk_scoring":
        findings = []
        scores = []
        for r in results:
            findings.extend(r.get("findings", []))
            if isinstance(r.get("score"), (int, float)):
                scores.append(r["score"])
            elif isinstance(r.get("score"), str) and r.get("score").isdigit():
                scores.append(int(r["score"]))
        score = round(sum(scores) / len(scores)) if scores else 0
        return {"score": score, "findings": findings}

    elif analysis_mode == "pii_masking":
        instances = []
        for r in results:
            instances.extend(r.get("pii_instances", []))
        return {"pii_instances": instances}

    return {}


def run_analysis(analysis_mode: str) -> dict:
    """
    Full pipeline:
      1. Split fixed PDF into chunks.
      2. For each chunk, retrieve top-3 ChromaDB references.
      3. Build a prompt message per chunk and call AnythingLLM.
      4. Aggregate all per-chunk results into a single response dict.
    """
    prompt_text = load_prompt(analysis_mode)
    
    chunks = process_pdf_to_queries(FIXED_PDF_PATH)
    
    chunks_to_process = chunks[2:5] 
    
    results = []

    for chunk in chunks_to_process:
        references = chroma.get_top_3_matches(chunk)
        chroma_context = "\n\n".join(references)

        message = (
            f"{prompt_text}\n\n"
            f"--- Relevant Context ---\n{chroma_context}\n\n"
            f"--- Document Chunk ---\n{chunk}"
        )

        result = call_with_retry(call_llm, message, analysis_mode)
        results.append(result)

    return _aggregate(results, analysis_mode)
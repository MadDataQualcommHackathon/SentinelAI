import json


REQUIRED_KEYS = {
    "vulnerability_detection": {"findings"},
    "legal_risk_scoring": {"score", "findings"},
    "pii_masking": {"pii_instances"},
}


def validate(raw: str, selection: str) -> dict:
    """
    Parse raw LLM output as JSON and verify it contains the required keys
    for the given selection.

    Returns the parsed dict on success.
    Raises ValueError if the output is not valid JSON or is missing required keys.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Response is not valid JSON: {e}")

    required = REQUIRED_KEYS.get(selection, set())
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Response missing required keys: {missing}")

    return data


def call_with_retry(call_llm_fn, message: str, selection: str, max_attempts: int = 3) -> dict:
    """
    Call call_llm_fn(message) up to max_attempts times.
    Each attempt validates the response against the expected schema for selection.
    Returns the parsed dict on the first passing attempt.
    Raises RuntimeError if all attempts fail.

    Args:
        call_llm_fn:   The call_llm function from anything.py.
        message:       The full prompt message to send.
        selection:     One of 'vulnerability_detection', 'legal_risk_scoring', 'pii_masking'.
        max_attempts:  Number of retries before giving up (default 3).
    """
    last_error = None

    for attempt in range(1, max_attempts + 1):
        raw = call_llm_fn(message)
        print(f"[response_validator] Attempt {attempt}/{max_attempts} raw output:\n{raw}\n")
        try:
            return validate(raw, selection)
        except ValueError as e:
            last_error = e
            print(f"[response_validator] Attempt {attempt}/{max_attempts} failed: {e}. Retrying...")

    raise RuntimeError(
        f"LLM failed to return valid JSON after {max_attempts} attempts. "
        f"Last error: {last_error}"
    )

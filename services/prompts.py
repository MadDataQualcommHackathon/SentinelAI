from nexaai import LlmChatMessage

LEGAL_PROMPT_TEMPLATE = """You are a legal risk auditor. Analyze the following contract clause and identify any risks.

KNOWLEDGE BASE CONTEXT:
{context}

CONTRACT CLAUSE:
{chunk}

Respond ONLY with valid JSON in this exact format (no markdown, no explanation):
{{"risk_level": "HIGH" | "MED" | "LOW" | "NONE", "clause_type": "<type>", "excerpt": "<key phrase from clause>", "recommendation": "<actionable advice>"}}
"""

CODE_PROMPT_TEMPLATE = """You are a security code auditor. Analyze the following code snippet for vulnerabilities.

KNOWLEDGE BASE CONTEXT:
{context}

CODE:
{chunk}

Respond ONLY with valid JSON in this exact format (no markdown, no explanation):
{{"risk_level": "HIGH" | "MED" | "LOW" | "NONE", "vulnerability_type": "<type>", "excerpt": "<vulnerable line or pattern>", "recommendation": "<fix>"}}
"""

def build_prompt(file_type: str, context: list[str], chunk: str) -> list[LlmChatMessage]:
    ctx_str = "\n".join(context) if context else "No context available."
    if file_type == "legal":
        content = LEGAL_PROMPT_TEMPLATE.format(context=ctx_str, chunk=chunk)
    else:
        content = CODE_PROMPT_TEMPLATE.format(context=ctx_str, chunk=chunk)
    return [LlmChatMessage(role="user", content=content)]

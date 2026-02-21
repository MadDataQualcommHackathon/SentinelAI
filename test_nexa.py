"""
test_nexa.py

Verifies that the Nexa SDK can be imported and the LLM can be loaded
and prompted from a plain Python script (no FastAPI, no server).

Run on Snapdragon X Elite:
    python test_nexa.py
"""

from nexaai import LLM, GenerationConfig, ModelConfig

MODEL_ID = "NexaAI/Llama3.2-3B-NPU-Turbo"

TEST_MESSAGES = [
    {
        "role": "system",
        "content": "You are a security auditor. Respond with valid JSON only."
    },
    {
        "role": "user",
        "content": (
            "Analyze the following Python snippet for security risks and return a JSON object "
            "with keys: risk_level (HIGH/MEDIUM/LOW/NONE), finding, recommendation.\n\n"
            "Snippet:\n"
            "password = 'abc123'  # hardcoded credential"
        )
    }
]


def main():
    print(f"[1/3] Loading model: {MODEL_ID}")
    model = LLM.from_(model=MODEL_ID, config=ModelConfig())
    print("[2/3] Model loaded. Applying chat template...")

    prompt = model.apply_chat_template(TEST_MESSAGES)

    print("[3/3] Streaming response from NPU...\n")
    tokens = []
    for token in model.generate_stream(prompt, GenerationConfig(max_tokens=256, temperature=0.1)):
        print(token, end="", flush=True)
        tokens.append(token)

    raw = "".join(tokens).strip()
    print("\n\n--- Raw output ---")
    print(raw)


if __name__ == "__main__":
    main()

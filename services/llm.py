import json
import re
from nexaai import LLM, GenerationConfig, ModelConfig

MODEL_ID = "NexaAI/Llama3.2-3B-NPU-Turbo"  # NPU-optimized for Qualcomm Snapdragon X Elite


class LLMService:
    def __init__(self):
        self._model = None

    def _load(self):
        if self._model is not None:
            return
        self._model = LLM.from_(model=MODEL_ID, config=ModelConfig())

    def is_loaded(self) -> bool:
        return self._model is not None

    def analyze(self, messages: list) -> dict:
        self._load()
        prompt = self._model.apply_chat_template(messages)
        tokens = []
        for token in self._model.generate_stream(prompt, GenerationConfig(max_tokens=256, temperature=0.1)):
            tokens.append(token)
        raw = "".join(tokens).strip()
        return self._parse(raw)

    def _parse(self, raw: str) -> dict:
        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        try:
            data = json.loads(raw)
            if "risk_level" not in data:
                return {"risk_level": "NONE"}
            return data
        except json.JSONDecodeError:
            # Try to extract JSON object from noisy output
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            return {"risk_level": "NONE"}

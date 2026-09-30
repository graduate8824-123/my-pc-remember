import httpx
from typing import Optional
from .base import LLMProvider
from .mock_provider import MockLLMProvider
from ..core.logging import logger
from ..core.config import settings

class OllamaProvider(LLMProvider):
    """
    Local Ollama integration for on-device LLM inference.
    Connects to local server (e.g. http://127.0.0.1:11434).
    If Ollama is offline or uninstalled, gracefully falls back to deterministic explanation.
    """

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.LLM_MODEL
        self._fallback = MockLLMProvider()

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=1.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        if not self.is_available():
            return self._fallback.generate(prompt, context)

        system_prompt = (
            "You are a local computer memory assistant. "
            "You only answer questions using the provided indexed context. "
            "If the context does not contain the answer, say: "
            "'I couldn't find enough information in your indexed files.' Do not hallucinate."
        )

        full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}" if context else prompt

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "system": system_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_predict": 150
                        }
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()
        except Exception as e:
            logger.warning(f"Ollama generation failed: {e}")

        return self._fallback.generate(prompt, context)

    def explain_match(self, query: str, filename: str, matched_chunk: str) -> str:
        if not self.is_available():
            return self._fallback.explain_match(query, filename, matched_chunk)

        prompt = (
            f"The user searched for: \"{query}\"\n"
            f"File: {filename}\n"
            f"Matched content excerpt:\n{matched_chunk[:400]}\n\n"
            "In ONE short, clear sentence, explain why this file matches what the user is looking for based strictly on the excerpt. Do not invent details."
        )

        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.0,
                            "num_predict": 60
                        }
                    }
                )
                if res.status_code == 200:
                    explanation = res.json().get("response", "").strip()
                    if explanation:
                        return explanation
        except Exception as e:
            logger.warning(f"Ollama explanation call failed: {e}")

        return self._fallback.explain_match(query, filename, matched_chunk)

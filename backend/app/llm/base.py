from abc import ABC, abstractmethod
from typing import Optional

class LLMProvider(ABC):
    """
    Abstract interface for local language models.
    Supports local Ollama, mock development provider, or future Snapdragon on-device LLM.
    """

    @abstractmethod
    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        """Generates grounded response based on context."""
        pass

    @abstractmethod
    def explain_match(self, query: str, filename: str, matched_chunk: str) -> str:
        """
        Explains WHY a specific file and chunk match the user's natural query.
        Must be strictly grounded in matched_chunk without hallucinating.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if local LLM service is currently operational."""
        pass

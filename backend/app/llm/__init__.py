from .base import LLMProvider
from .mock_provider import MockLLMProvider
from .ollama_provider import OllamaProvider
from ..core.config import settings

def get_llm_provider() -> LLMProvider:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "ollama":
        return OllamaProvider(base_url=settings.OLLAMA_BASE_URL, model=settings.LLM_MODEL)
    return MockLLMProvider()

from pydantic import BaseModel
from typing import Optional, Dict

class SettingsPayload(BaseModel):
    embedding_provider: Optional[str] = None
    embedding_model: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    ollama_base_url: Optional[str] = None
    top_k: Optional[int] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    inference_target: Optional[str] = None

class SettingsResponse(BaseModel):
    embedding_provider: str
    embedding_model: str
    llm_provider: str
    llm_model: str
    ollama_base_url: str
    top_k: int
    chunk_size: int
    chunk_overlap: int
    inference_target: str
    database_path: str
    vector_index_path: str
    privacy_notice: str

import os
from pathlib import Path
from pydantic import BaseModel, Field

class Settings(BaseModel):
    # App
    APP_NAME: str = "MY PC REMEMBERS"
    APP_DESCRIPTION: str = "Private, Local AI Memory for Your Computer"
    VERSION: str = "0.1.0"
    
    # Server
    HOST: str = Field(default_factory=lambda: os.getenv("HOST", "127.0.0.1"))
    PORT: int = Field(default_factory=lambda: int(os.getenv("PORT", "8001")))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    
    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = Field(default_factory=lambda: Path(os.getenv("DATA_DIR", "./data")).resolve())
    DATABASE_PATH: str = Field(default_factory=lambda: os.getenv("DATABASE_PATH", "./data/app.db"))
    VECTOR_INDEX_PATH: str = Field(default_factory=lambda: os.getenv("VECTOR_INDEX_PATH", "./data/faiss.index"))
    METADATA_STORE_PATH: str = Field(default_factory=lambda: os.getenv("METADATA_STORE_PATH", "./data/metadata.json"))

    # Embeddings
    # "fastembed", "hash" (offline deterministic test), or "sentence-transformers"
    EMBEDDING_PROVIDER: str = Field(default_factory=lambda: os.getenv("EMBEDDING_PROVIDER", "fastembed"))
    EMBEDDING_MODEL: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"))
    EMBEDDING_DIMENSION: int = Field(default_factory=lambda: int(os.getenv("EMBEDDING_DIMENSION", "384")))
    
    # Document Chunker
    CHUNK_SIZE: int = Field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "700")))
    CHUNK_OVERLAP: int = Field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "100")))
    
    # Search
    TOP_K: int = Field(default_factory=lambda: int(os.getenv("TOP_K", "8")))
    SIMILARITY_THRESHOLD: float = Field(default_factory=lambda: float(os.getenv("SIMILARITY_THRESHOLD", "0.20")))
    
    # LLM
    # "mock" or "ollama"
    LLM_PROVIDER: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "mock"))
    LLM_MODEL: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "llama3.2:1b"))
    OLLAMA_BASE_URL: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    
    # Hardware / Snapdragon
    INFERENCE_TARGET: str = Field(default_factory=lambda: os.getenv("INFERENCE_TARGET", "cpu"))

    def ensure_directories(self) -> None:
        """Ensure data directories exist."""
        db_path = Path(self.DATABASE_PATH).parent
        db_path.mkdir(parents=True, exist_ok=True)
        idx_path = Path(self.VECTOR_INDEX_PATH).parent
        idx_path.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()

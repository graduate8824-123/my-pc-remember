from fastapi import APIRouter
from typing import Dict, Any
from ..schemas.settings import SettingsPayload, SettingsResponse
from ..core.config import settings
from ..db.repositories import Repository
from ..runtime.device import get_hardware_profile
from ..runtime.inference import get_inference_backend

router = APIRouter(prefix="/api/settings", tags=["settings"])

def get_repo() -> Repository:
    from ..main import repo
    return repo

@router.get("", response_model=SettingsResponse)
async def get_app_settings():
    repo = get_repo()
    return SettingsResponse(
        embedding_provider=repo.get_setting("embedding_provider", settings.EMBEDDING_PROVIDER),
        embedding_model=repo.get_setting("embedding_model", settings.EMBEDDING_MODEL),
        llm_provider=repo.get_setting("llm_provider", settings.LLM_PROVIDER),
        llm_model=repo.get_setting("llm_model", settings.LLM_MODEL),
        ollama_base_url=repo.get_setting("ollama_base_url", settings.OLLAMA_BASE_URL),
        top_k=int(repo.get_setting("top_k", str(settings.TOP_K))),
        chunk_size=int(repo.get_setting("chunk_size", str(settings.CHUNK_SIZE))),
        chunk_overlap=int(repo.get_setting("chunk_overlap", str(settings.CHUNK_OVERLAP))),
        inference_target=repo.get_setting("inference_target", settings.INFERENCE_TARGET),
        database_path=settings.DATABASE_PATH,
        vector_index_path=settings.VECTOR_INDEX_PATH,
        privacy_notice="Your indexed content stays on this computer unless you explicitly configure an external service."
    )

@router.put("", response_model=SettingsResponse)
async def update_settings(payload: SettingsPayload):
    repo = get_repo()
    if payload.embedding_provider is not None:
        repo.set_setting("embedding_provider", payload.embedding_provider)
    if payload.embedding_model is not None:
        repo.set_setting("embedding_model", payload.embedding_model)
    if payload.llm_provider is not None:
        repo.set_setting("llm_provider", payload.llm_provider)
    if payload.llm_model is not None:
        repo.set_setting("llm_model", payload.llm_model)
    if payload.ollama_base_url is not None:
        repo.set_setting("ollama_base_url", payload.ollama_base_url)
    if payload.top_k is not None:
        repo.set_setting("top_k", str(payload.top_k))
    if payload.chunk_size is not None:
        repo.set_setting("chunk_size", str(payload.chunk_size))
    if payload.chunk_overlap is not None:
        repo.set_setting("chunk_overlap", str(payload.chunk_overlap))
    if payload.inference_target is not None:
        repo.set_setting("inference_target", payload.inference_target)

    return await get_app_settings()

@router.get("/hardware")
async def get_hardware_status():
    backend = get_inference_backend()
    profile = get_hardware_profile()
    return {
        "hardware_profile": profile,
        "inference_backend": backend.get_specs(),
        "local_only": True,
        "snapdragon_readiness": "Architecture fully abstracted for Snapdragon Hexagon NPU."
    }

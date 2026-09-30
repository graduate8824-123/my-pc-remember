from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.logging import logger
from .db.database import init_db
from .db.repositories import Repository
from .vectorstore.faiss_store import FAISSVectorStore
from .services.indexing_service import IndexingService
from .services.search_service import SearchService
from .services.file_service import FileService
from .runtime.device import get_hardware_profile

# Initialize database
init_db()

# Initialize core singletons
repo = Repository()
vector_store = FAISSVectorStore(dimension=settings.EMBEDDING_DIMENSION)

# Try loading existing vector index
vector_store.load(settings.VECTOR_INDEX_PATH)

indexing_service = IndexingService(repo, vector_store)
search_service = SearchService(repo, vector_store)
file_service = FileService(repo)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.VERSION
)

# CORS: strictly local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
from .api.routes_index import router as index_router
from .api.routes_search import router as search_router
from .api.routes_files import router as files_router
from .api.routes_settings import router as settings_router

app.include_router(index_router)
app.include_router(search_router)
app.include_router(files_router)
app.include_router(settings_router)

@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.APP_NAME} started on {settings.HOST}:{settings.PORT}")
    # If no folders exist yet, auto-register the sample documents folder for effortless out-of-the-box demo
    existing = repo.get_folders()
    if not existing:
        sample_dir = Path("data/sample_documents/DSA").resolve()
        if sample_dir.exists():
            logger.info(f"Auto-registering sample demo folder: {sample_dir}")
            f_rec = repo.add_folder(str(sample_dir))
            indexing_service.start_indexing(folder_id=f_rec.id)

@app.get("/api/health")
async def health_check():
    stats = repo.get_indexed_stats()
    profile = get_hardware_profile()
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "indexed_files": stats["total_files"],
        "indexed_chunks": stats["total_chunks"],
        "device": profile["active_device"],
        "target": profile["hardware_target"],
        "local_mode": True
    }

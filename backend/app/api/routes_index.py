from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from ..schemas.files import IndexStatusResponse, AddFolderRequest, FolderItem
from ..schemas.indexing import IndexRequest
from ..services.indexing_service import IndexingService
from ..db.repositories import Repository
from ..ingestion.scanner import validate_user_folder

router = APIRouter(prefix="/api/index", tags=["indexing"])

def get_services():
    from ..main import indexing_service, repo
    return indexing_service, repo

@router.get("/status", response_model=IndexStatusResponse)
async def get_index_status():
    indexing_service, _ = get_services()
    return indexing_service.get_status()

@router.get("/folders", response_model=List[FolderItem])
async def list_folders():
    _, repo = get_services()
    folders = repo.get_folders()
    return [
        FolderItem(
            id=f.id,
            path=f.path,
            added_at=f.added_at,
            last_scanned_at=f.last_scanned_at,
            file_count=f.file_count,
            status=f.status
        )
        for f in folders
    ]

@router.post("/folder", response_model=FolderItem)
async def add_folder(payload: AddFolderRequest):
    indexing_service, repo = get_services()
    try:
        validated_path = validate_user_folder(payload.path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    folder_rec = repo.add_folder(str(validated_path))
    # Trigger auto-index for newly added folder
    indexing_service.start_indexing(folder_id=folder_rec.id)
    
    return FolderItem(
        id=folder_rec.id,
        path=folder_rec.path,
        added_at=folder_rec.added_at,
        last_scanned_at=folder_rec.last_scanned_at,
        file_count=folder_rec.file_count,
        status=folder_rec.status
    )

@router.delete("/folders/{folder_id}")
async def remove_folder(folder_id: int):
    _, repo = get_services()
    success = repo.delete_folder(folder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"message": "Folder and associated indexed data removed successfully"}

@router.post("/start")
async def start_indexing(payload: IndexRequest = None):
    indexing_service, _ = get_services()
    folder_id = payload.folder_id if payload else None
    force = payload.force_reindex if payload else False
    return indexing_service.start_indexing(folder_id=folder_id, force_reindex=force)

@router.post("/stop")
async def stop_indexing():
    indexing_service, _ = get_services()
    return indexing_service.stop_indexing()

@router.post("/rebuild")
async def rebuild_index():
    indexing_service, _ = get_services()
    return indexing_service.rebuild_index()

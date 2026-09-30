from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..schemas.files import FileDetail
from ..services.file_service import FileService

router = APIRouter(prefix="/api/files", tags=["files"])

def get_file_service() -> FileService:
    from ..main import file_service
    return file_service

@router.get("/{file_id}", response_model=FileDetail)
async def get_file_info(file_id: int):
    file_svc = get_file_service()
    detail = file_svc.get_file_detail(file_id)
    if not detail:
        raise HTTPException(status_code=404, detail="File not found")
    return FileDetail(**detail)

@router.post("/{file_id}/open")
async def open_file(file_id: int):
    file_svc = get_file_service()
    try:
        result = file_svc.open_file_locally(file_id)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

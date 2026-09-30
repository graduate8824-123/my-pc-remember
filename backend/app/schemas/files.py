from pydantic import BaseModel
from typing import Optional, List

class FolderItem(BaseModel):
    id: int
    path: str
    added_at: Optional[str] = None
    last_scanned_at: Optional[str] = None
    file_count: int = 0
    status: str = "idle"

class AddFolderRequest(BaseModel):
    path: str

class FileDetail(BaseModel):
    id: int
    path: str
    filename: str
    extension: str
    size: int
    modified_at: Optional[str] = None
    indexed_at: Optional[str] = None
    status: str
    word_count: Optional[int] = 0
    page_count: Optional[int] = 1
    content_preview: Optional[str] = None
    chunks_count: Optional[int] = 0

class IndexStatusResponse(BaseModel):
    is_indexing: bool
    total_files: int
    total_documents: int
    total_code: int
    total_chunks: int
    indexed_folders: List[FolderItem]
    current_file: Optional[str] = None
    progress: float = 0.0 # 0.0 to 1.0
    processed_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    recent_errors: List[str] = []

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class FolderRecord:
    id: Optional[int]
    path: str
    added_at: Optional[str] = None
    last_scanned_at: Optional[str] = None
    file_count: int = 0
    status: str = "idle"

@dataclass
class FileRecord:
    id: Optional[int]
    path: str
    filename: str
    extension: str
    size: int
    content_hash: str
    folder_id: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    indexed_at: Optional[str] = None
    status: str = "indexed"

@dataclass
class DocumentRecord:
    id: Optional[int]
    file_id: int
    content: str
    word_count: int = 0
    page_count: int = 1
    created_at: Optional[str] = None

@dataclass
class ChunkRecord:
    id: Optional[int]
    document_id: int
    file_id: int
    chunk_index: int
    content: str
    start_position: int = 0
    end_position: int = 0
    vector_id: Optional[int] = None
    created_at: Optional[str] = None

@dataclass
class SearchHistoryRecord:
    id: Optional[int]
    query: str
    result_count: int = 0
    created_at: Optional[str] = None

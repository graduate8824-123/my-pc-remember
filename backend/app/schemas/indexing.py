from pydantic import BaseModel
from typing import Optional, List

class IndexRequest(BaseModel):
    folder_id: Optional[int] = None
    force_reindex: bool = False

class IndexProgress(BaseModel):
    is_active: bool
    status_message: str
    current_file: Optional[str] = None
    total_found: int = 0
    processed: int = 0
    skipped: int = 0
    failed: int = 0
    errors: List[str] = []

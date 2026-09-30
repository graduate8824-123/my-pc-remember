import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, Optional
from ..core.logging import logger
from ..db.repositories import Repository

class FileService:
    """
    Secure file management and platform-native file opener.
    Uses platform-native handlers:
      - macOS: open
      - Windows: os.startfile / cmd /c start
      - Linux: xdg-open
    Strictly validates file existence and prevents arbitrary command injection.
    """

    def __init__(self, repo: Repository):
        self.repo = repo

    def get_file_detail(self, file_id: int) -> Optional[Dict[str, Any]]:
        file_rec = self.repo.get_file_by_id(file_id)
        if not file_rec:
            return None

        doc_rec = self.repo.get_document_by_file_id(file_id)
        chunks = self.repo.get_chunks_for_file(file_id)

        preview = doc_rec.content[:1000] if doc_rec else ""

        return {
            "id": file_rec.id,
            "path": file_rec.path,
            "filename": file_rec.filename,
            "extension": file_rec.extension,
            "size": file_rec.size,
            "modified_at": file_rec.modified_at,
            "indexed_at": file_rec.indexed_at,
            "status": file_rec.status,
            "word_count": doc_rec.word_count if doc_rec else 0,
            "page_count": doc_rec.page_count if doc_rec else 1,
            "content_preview": preview,
            "chunks_count": len(chunks)
        }

    def open_file_locally(self, file_id: int) -> Dict[str, Any]:
        file_rec = self.repo.get_file_by_id(file_id)
        if not file_rec:
            raise FileNotFoundError(f"File ID {file_id} not found in database.")

        target_path = Path(file_rec.path).resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"File no longer exists on disk at: {target_path}")

        system = platform.system()
        try:
            if system == "Darwin": # macOS
                subprocess.Popen(["open", str(target_path)])
            elif system == "Windows":
                # Use os.startfile if available (safe, no shell injection)
                if hasattr(os, "startfile"):
                    os.startfile(str(target_path))
                else:
                    subprocess.Popen(["cmd", "/c", "start", "", str(target_path)], shell=False)
            else: # Linux
                # On headless or container Linux, xdg-open might not have X11 display, handle gracefully
                try:
                    subprocess.Popen(["xdg-open", str(target_path)])
                except Exception:
                    logger.info(f"Linux open requested for: {target_path}")

            logger.info(f"Opened file: {target_path}")
            return {
                "success": True,
                "message": f"Opened {file_rec.filename}",
                "path": str(target_path)
            }
        except Exception as e:
            logger.error(f"Failed opening file {target_path}: {e}")
            return {
                "success": False,
                "message": f"Could not launch viewer: {str(e)}",
                "path": str(target_path)
            }

import threading
from typing import Dict, Any, List, Optional
from ..core.logging import logger
from ..core.config import settings
from ..db.repositories import Repository
from ..vectorstore.faiss_store import FAISSVectorStore
from ..ingestion.indexer import Indexer

class IndexingService:
    """
    Manages indexing lifecycle, background worker threads,
    and live progress reporting.
    """

    def __init__(self, repo: Repository, vector_store: FAISSVectorStore):
        self.repo = repo
        self.vector_store = vector_store
        self.indexer = Indexer(repo, vector_store)
        
        self._is_indexing = False
        self._stop_requested = False
        self._lock = threading.Lock()
        
        self._current_progress: Dict[str, Any] = {
            "is_indexing": False,
            "current_file": None,
            "progress": 0.0,
            "processed_count": 0,
            "skipped_count": 0,
            "failed_count": 0,
            "recent_errors": []
        }

    def get_status(self) -> Dict[str, Any]:
        stats = self.repo.get_indexed_stats()
        folders = self.repo.get_folders()

        with self._lock:
            return {
                "is_indexing": self._is_indexing,
                "total_files": stats["total_files"],
                "total_documents": stats["total_documents"],
                "total_code": stats["total_code"],
                "total_chunks": stats["total_chunks"],
                "indexed_folders": [
                    {
                        "id": f.id,
                        "path": f.path,
                        "added_at": f.added_at,
                        "last_scanned_at": f.last_scanned_at,
                        "file_count": f.file_count,
                        "status": f.status
                    }
                    for f in folders
                ],
                "current_file": self._current_progress["current_file"],
                "progress": self._current_progress["progress"],
                "processed_count": self._current_progress["processed_count"],
                "skipped_count": self._current_progress["skipped_count"],
                "failed_count": self._current_progress["failed_count"],
                "recent_errors": self._current_progress["recent_errors"]
            }

    def _progress_callback(self, p: Dict[str, Any]):
        with self._lock:
            self._current_progress["current_file"] = p.get("current_file")
            self._current_progress["progress"] = p.get("progress", 0.0)
            self._current_progress["processed_count"] = p.get("processed", 0)
            self._current_progress["skipped_count"] = p.get("skipped", 0)
            self._current_progress["failed_count"] = p.get("failed", 0)

    def start_indexing(self, folder_id: Optional[int] = None, force_reindex: bool = False) -> Dict[str, Any]:
        with self._lock:
            if self._is_indexing:
                return {"message": "Indexing is already running in background.", "status": "running"}
            self._is_indexing = True
            self._stop_requested = False
            self._current_progress = {
                "is_indexing": True,
                "current_file": None,
                "progress": 0.0,
                "processed_count": 0,
                "skipped_count": 0,
                "failed_count": 0,
                "recent_errors": []
            }

        thread = threading.Thread(
            target=self._run_indexing_worker,
            args=(folder_id, force_reindex),
            daemon=True
        )
        thread.start()
        return {"message": "Indexing started.", "status": "started"}

    def _run_indexing_worker(self, folder_id: Optional[int], force_reindex: bool):
        try:
            folders_to_scan = []
            if folder_id:
                folder = self.repo.get_folder_by_id(folder_id)
                if folder:
                    folders_to_scan.append(folder)
            else:
                folders_to_scan = self.repo.get_folders()

            total_processed = 0
            total_skipped = 0
            total_failed = 0
            all_errors = []

            for folder in folders_to_scan:
                if self._stop_requested:
                    break

                res = self.indexer.index_folder(
                    folder_path=folder.path,
                    folder_id=folder.id,
                    force_reindex=force_reindex,
                    progress_cb=self._progress_callback
                )
                total_processed += res["processed"]
                total_skipped += res["skipped"]
                total_failed += res["failed"]
                all_errors.extend(res.get("errors", []))

            with self._lock:
                self._current_progress["processed_count"] = total_processed
                self._current_progress["skipped_count"] = total_skipped
                self._current_progress["failed_count"] = total_failed
                self._current_progress["recent_errors"] = all_errors[-10:]
                self._current_progress["progress"] = 1.0
                self._current_progress["current_file"] = None

        except Exception as e:
            logger.error(f"Error during background indexing: {e}")
            with self._lock:
                self._current_progress["recent_errors"].append(str(e))
        finally:
            with self._lock:
                self._is_indexing = False
                self._current_progress["is_indexing"] = False

    def stop_indexing(self) -> Dict[str, str]:
        with self._lock:
            if not self._is_indexing:
                return {"message": "No indexing process currently running."}
            self._stop_requested = True
            return {"message": "Stop requested. Indexer will halt after the current file."}

    def rebuild_index(self) -> Dict[str, Any]:
        with self._lock:
            if self._is_indexing:
                return {"message": "Cannot rebuild while indexing is active."}

        # Clear vector store and DB tables
        self.vector_store.clear()
        self.repo.clear_all_index_data()
        self.vector_store.save(settings.VECTOR_INDEX_PATH)

        return self.start_indexing(force_reindex=True)

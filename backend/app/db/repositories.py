import sqlite3
from typing import List, Optional, Dict, Any, Tuple
from .database import get_connection
from .models import FolderRecord, FileRecord, DocumentRecord, ChunkRecord, SearchHistoryRecord
from ..core.logging import logger

class Repository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    @property
    def conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)

    # ------------------- Folders -------------------
    def add_folder(self, path: str) -> FolderRecord:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO folders (path, status) VALUES (?, 'idle') "
                "ON CONFLICT(path) DO UPDATE SET status='idle' RETURNING id, path, added_at, last_scanned_at, file_count, status",
                (path,)
            )
            row = cursor.fetchone()
            return FolderRecord(*row)

    def get_folders(self) -> List[FolderRecord]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, path, added_at, last_scanned_at, file_count, status FROM folders ORDER BY id ASC")
        return [FolderRecord(*row) for row in cursor.fetchall()]

    def get_folder_by_id(self, folder_id: int) -> Optional[FolderRecord]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, path, added_at, last_scanned_at, file_count, status FROM folders WHERE id = ?", (folder_id,))
        row = cursor.fetchone()
        return FolderRecord(*row) if row else None

    def delete_folder(self, folder_id: int) -> bool:
        with self.conn:
            cursor = self.conn.cursor()
            # Also delete files associated with this folder
            cursor.execute("DELETE FROM files WHERE folder_id = ?", (folder_id,))
            cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
            return cursor.rowcount > 0

    def update_folder_stats(self, folder_id: int, file_count: int, status: str = "idle") -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE folders SET file_count = ?, status = ?, last_scanned_at = CURRENT_TIMESTAMP WHERE id = ?",
                (file_count, status, folder_id)
            )

    # ------------------- Files -------------------
    def get_file_by_path(self, path: str) -> Optional[FileRecord]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, path, filename, extension, size, content_hash, folder_id, mime_type, created_at, modified_at, indexed_at, status FROM files WHERE path = ?",
            (path,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return FileRecord(
            id=row[0], path=row[1], filename=row[2], extension=row[3], size=row[4],
            content_hash=row[5], folder_id=row[6], mime_type=row[7], created_at=row[8],
            modified_at=row[9], indexed_at=row[10], status=row[11]
        )

    def get_file_by_id(self, file_id: int) -> Optional[FileRecord]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, path, filename, extension, size, content_hash, folder_id, mime_type, created_at, modified_at, indexed_at, status FROM files WHERE id = ?",
            (file_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return FileRecord(
            id=row[0], path=row[1], filename=row[2], extension=row[3], size=row[4],
            content_hash=row[5], folder_id=row[6], mime_type=row[7], created_at=row[8],
            modified_at=row[9], indexed_at=row[10], status=row[11]
        )

    def upsert_file(self, file_rec: FileRecord) -> int:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO files (folder_id, path, filename, extension, mime_type, size, created_at, modified_at, content_hash, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    filename=excluded.filename,
                    extension=excluded.extension,
                    size=excluded.size,
                    modified_at=excluded.modified_at,
                    content_hash=excluded.content_hash,
                    indexed_at=CURRENT_TIMESTAMP,
                    status=excluded.status
                RETURNING id
            """, (
                file_rec.folder_id, file_rec.path, file_rec.filename, file_rec.extension,
                file_rec.mime_type, file_rec.size, file_rec.created_at, file_rec.modified_at,
                file_rec.content_hash, file_rec.status
            ))
            row = cursor.fetchone()
            return row[0]

    def delete_file(self, file_id: int) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM files WHERE id = ?", (file_id,))

    def get_indexed_stats(self) -> Dict[str, int]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files")
        total_files = cursor.fetchone()[0]
        
        # Document extensions
        doc_exts = "('.pdf', '.docx', '.txt', '.md', '.csv', '.pptx')"
        cursor.execute(f"SELECT COUNT(*) FROM files WHERE extension IN {doc_exts}")
        total_docs = cursor.fetchone()[0]
        
        # Code extensions
        code_exts = "('.py', '.cpp', '.c', '.h', '.java', '.js', '.ts', '.tsx', '.html', '.css', '.sql', '.json', '.yaml', '.yml', '.sh')"
        cursor.execute(f"SELECT COUNT(*) FROM files WHERE extension IN {code_exts}")
        total_code = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM chunks")
        total_chunks = cursor.fetchone()[0]

        return {
            "total_files": total_files,
            "total_documents": total_docs,
            "total_code": total_code,
            "total_chunks": total_chunks
        }

    # ------------------- Documents & Chunks -------------------
    def save_document(self, doc_rec: DocumentRecord) -> int:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO documents (file_id, content, word_count, page_count)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(file_id) DO UPDATE SET
                    content=excluded.content,
                    word_count=excluded.word_count,
                    page_count=excluded.page_count,
                    created_at=CURRENT_TIMESTAMP
                RETURNING id
            """, (doc_rec.file_id, doc_rec.content, doc_rec.word_count, doc_rec.page_count))
            row = cursor.fetchone()
            return row[0]

    def get_document_by_file_id(self, file_id: int) -> Optional[DocumentRecord]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, file_id, content, word_count, page_count, created_at FROM documents WHERE file_id = ?", (file_id,))
        row = cursor.fetchone()
        return DocumentRecord(*row) if row else None

    def delete_chunks_for_file(self, file_id: int) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM chunks WHERE file_id = ?", (file_id,))

    def save_chunks(self, chunks: List[ChunkRecord]) -> List[int]:
        if not chunks:
            return []
        ids = []
        with self.conn:
            cursor = self.conn.cursor()
            for c in chunks:
                cursor.execute("""
                    INSERT INTO chunks (document_id, file_id, chunk_index, content, start_position, end_position, vector_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    RETURNING id
                """, (c.document_id, c.file_id, c.chunk_index, c.content, c.start_position, c.end_position, c.vector_id))
                ids.append(cursor.fetchone()[0])
        return ids

    def get_chunk_by_vector_id(self, vector_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.id, c.document_id, c.file_id, c.chunk_index, c.content, c.vector_id,
                   f.filename, f.path, f.extension, f.modified_at, f.size
            FROM chunks c
            JOIN files f ON c.file_id = f.id
            WHERE c.id = ? OR c.vector_id = ?
        """, (vector_id, vector_id))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "chunk_id": row[0],
            "document_id": row[1],
            "file_id": row[2],
            "chunk_index": row[3],
            "content": row[4],
            "vector_id": row[5],
            "filename": row[6],
            "path": row[7],
            "extension": row[8],
            "modified_at": row[9],
            "size": row[10]
        }

    def get_chunks_for_file(self, file_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, chunk_index, content, start_position, end_position, vector_id
            FROM chunks WHERE file_id = ? ORDER BY chunk_index ASC
        """, (file_id,))
        return [
            {
                "id": r[0],
                "chunk_index": r[1],
                "content": r[2],
                "start_position": r[3],
                "end_position": r[4],
                "vector_id": r[5]
            }
            for r in cursor.fetchall()
        ]

    # ------------------- Search History -------------------
    def log_search(self, query: str, result_count: int = 0) -> None:
        with self.conn:
            self.conn.execute("INSERT INTO search_history (query, result_count) VALUES (?, ?)", (query, result_count))

    def get_recent_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, query, result_count, created_at FROM search_history ORDER BY id DESC LIMIT ?", (limit,))
        return [{"id": r[0], "query": r[1], "result_count": r[2], "created_at": r[3]} for r in cursor.fetchall()]

    def clear_search_history(self) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM search_history")

    # ------------------- Settings -------------------
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self.conn:
            self.conn.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))

    def get_all_settings(self) -> Dict[str, str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        return {r[0]: r[1] for r in cursor.fetchall()}

    def clear_all_index_data(self) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM chunks")
            self.conn.execute("DELETE FROM documents")
            self.conn.execute("DELETE FROM files")
            self.conn.execute("UPDATE folders SET file_count = 0, status = 'idle'")

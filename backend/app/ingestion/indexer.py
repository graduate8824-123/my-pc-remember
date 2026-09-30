import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from ..core.logging import logger
from ..core.config import settings
from ..db.repositories import Repository
from ..db.models import FileRecord, DocumentRecord, ChunkRecord
from .scanner import scan_directory, validate_user_folder
from .extractor import DocumentExtractor
from .chunker import TextChunker
from ..embeddings.local_embeddings import get_embedding_provider
from ..vectorstore.faiss_store import FAISSVectorStore

class Indexer:
    """
    Incremental Document and Code Indexer.
    Checks file hashes: unchanged files are skipped to save CPU/battery.
    Processes documents in streaming batches to keep memory <100MB.
    """

    def __init__(self, repo: Repository, vector_store: FAISSVectorStore):
        self.repo = repo
        self.vector_store = vector_store
        self.chunker = TextChunker(
            target_tokens=settings.CHUNK_SIZE,
            overlap_tokens=settings.CHUNK_OVERLAP
        )
        self.embedding_provider = get_embedding_provider()

    def index_folder(
        self,
        folder_path: str,
        folder_id: Optional[int] = None,
        force_reindex: bool = False,
        progress_cb: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        target_dir = validate_user_folder(folder_path)
        logger.info(f"Starting incremental index scan for: {target_dir}")

        stats = {
            "folder": str(target_dir),
            "processed": 0,
            "skipped": 0,
            "failed": 0,
            "total_chunks": 0,
            "errors": []
        }

        # Collect files generator
        scanned_files = list(scan_directory(target_dir))
        total_files = len(scanned_files)

        for idx, file_meta in enumerate(scanned_files):
            file_path = file_meta["path"]
            filename = file_meta["filename"]

            if progress_cb:
                progress_cb({
                    "current_file": filename,
                    "progress": (idx + 1) / max(1, total_files),
                    "processed": stats["processed"],
                    "skipped": stats["skipped"],
                    "failed": stats["failed"],
                    "total": total_files
                })

            existing_file = self.repo.get_file_by_path(file_path)

            # Check if unchanged (Incremental Check)
            if existing_file and not force_reindex:
                if existing_file.content_hash == file_meta["content_hash"]:
                    stats["skipped"] += 1
                    continue

            try:
                # 1. Extract content
                extracted = DocumentExtractor.extract(file_path)
                if not extracted.content.strip():
                    stats["skipped"] += 1
                    continue

                # 2. Upsert file record in SQLite
                file_rec = FileRecord(
                    id=None,
                    folder_id=folder_id,
                    path=file_path,
                    filename=filename,
                    extension=file_meta["extension"],
                    size=file_meta["size"],
                    content_hash=file_meta["content_hash"],
                    created_at=file_meta["created_at"],
                    modified_at=file_meta["modified_at"],
                    status="indexed"
                )
                db_file_id = self.repo.upsert_file(file_rec)

                # 3. Save document record
                doc_rec = DocumentRecord(
                    id=None,
                    file_id=db_file_id,
                    content=extracted.content,
                    word_count=extracted.word_count,
                    page_count=extracted.page_count
                )
                db_doc_id = self.repo.save_document(doc_rec)

                # 4. Clean old chunks if file was modified
                self.repo.delete_chunks_for_file(db_file_id)

                # 5. Chunk text
                chunks = self.chunker.chunk_text(extracted.content)
                if not chunks:
                    stats["processed"] += 1
                    continue

                # 6. Generate embeddings
                chunk_texts = [c.content for c in chunks]
                embeddings = self.embedding_provider.embed_batch(chunk_texts)

                # 7. Save chunk records and link to vector store
                chunk_records = []
                for c_idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                    chunk_records.append(ChunkRecord(
                        id=None,
                        document_id=db_doc_id,
                        file_id=db_file_id,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        start_position=chunk.start_pos,
                        end_position=chunk.end_pos,
                        vector_id=None
                    ))

                saved_chunk_ids = self.repo.save_chunks(chunk_records)

                # 8. Add embeddings into local vector store
                self.vector_store.add(embeddings, saved_chunk_ids)

                stats["processed"] += 1
                stats["total_chunks"] += len(saved_chunk_ids)

            except Exception as e:
                logger.error(f"Error indexing {file_path}: {e}")
                stats["failed"] += 1
                stats["errors"].append(f"{filename}: {str(e)}")

        # Persist updated vector store
        self.vector_store.save(settings.VECTOR_INDEX_PATH)

        if folder_id:
            self.repo.update_folder_stats(
                folder_id=folder_id,
                file_count=stats["processed"] + stats["skipped"],
                status="idle"
            )

        logger.info(f"Indexing complete for {target_dir}. Processed: {stats['processed']}, Skipped: {stats['skipped']}, Failed: {stats['failed']}")
        return stats

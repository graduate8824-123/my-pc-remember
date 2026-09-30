import sqlite3
import threading
from typing import Generator
from pathlib import Path
from ..core.config import settings
from ..core.logging import logger

_local = threading.local()

def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Returns a thread-local SQLite connection with WAL mode enabled."""
    target_path = db_path or settings.DATABASE_PATH
    Path(target_path).parent.mkdir(parents=True, exist_ok=True)
    
    if not hasattr(_local, "connection") or _local.target_path != target_path:
        conn = sqlite3.connect(target_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Performance tuning for local SSD / low-overhead indexing
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        _local.connection = conn
        _local.target_path = target_path
    return _local.connection

def init_db(db_path: str = None) -> None:
    """Initializes SQLite database tables and indexes."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # 1. Folders table (user-selected directories)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS folders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_scanned_at TIMESTAMP,
        file_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'idle'
    );
    """)

    # 2. Files table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folder_id INTEGER,
        path TEXT UNIQUE NOT NULL,
        filename TEXT NOT NULL,
        extension TEXT NOT NULL,
        mime_type TEXT,
        size INTEGER NOT NULL,
        created_at TIMESTAMP,
        modified_at TIMESTAMP,
        indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        content_hash TEXT NOT NULL,
        status TEXT DEFAULT 'indexed',
        FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE
    );
    """)

    # 3. Documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER UNIQUE NOT NULL,
        content TEXT NOT NULL,
        word_count INTEGER DEFAULT 0,
        page_count INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
    );
    """)

    # 4. Chunks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        file_id INTEGER NOT NULL,
        chunk_index INTEGER NOT NULL,
        content TEXT NOT NULL,
        start_position INTEGER,
        end_position INTEGER,
        vector_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
        FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
    );
    """)

    # 5. Search history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        result_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """)

    # Performance indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_hash ON files(content_hash);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_modified ON files(modified_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_file_id ON chunks(file_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_vector_id ON chunks(vector_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_history_created ON search_history(created_at);")
    
    conn.commit()
    logger.info(f"Database initialized at {db_path or settings.DATABASE_PATH}")

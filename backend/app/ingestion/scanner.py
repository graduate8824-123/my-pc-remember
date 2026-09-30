import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Generator, Optional
from datetime import datetime
from ..core.logging import logger

# Strictly supported file extensions
SUPPORTED_DOCUMENT_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md", ".csv", ".pptx"
}

SUPPORTED_CODE_EXTENSIONS = {
    ".py", ".cpp", ".c", ".h", ".hpp", ".java", ".js", ".ts", ".tsx",
    ".html", ".css", ".sql", ".json", ".xml", ".yaml", ".yml", ".sh"
}

ALL_SUPPORTED_EXTENSIONS = SUPPORTED_DOCUMENT_EXTENSIONS | SUPPORTED_CODE_EXTENSIONS

# Forbidden paths to guarantee security and privacy
FORBIDDEN_DIR_NAMES = {
    ".git", ".svn", ".hg", "node_modules", ".venv", "venv", "__pycache__",
    ".ssh", ".gnupg", ".aws", ".config", ".azure", ".gcloud",
    "keychains", "system", "library", "proc", "sys", "dev"
}

def is_safe_and_supported_path(file_path: Path) -> bool:
    """Verifies that a file path is safe to index and has a supported extension."""
    parts = set(part.lower() for part in file_path.parts)
    if any(forbidden in parts for forbidden in FORBIDDEN_DIR_NAMES):
        return False
    
    # Ignore hidden files starting with .
    if file_path.name.startswith("."):
        return False
        
    return file_path.suffix.lower() in ALL_SUPPORTED_EXTENSIONS

def validate_user_folder(folder_path_str: str) -> Path:
    """
    Validates user-selected folder path to prevent path traversal
    and ensure directory exists and is safe to scan.
    """
    p = Path(folder_path_str).expanduser().resolve()
    if not p.exists() or not p.is_dir():
        raise ValueError(f"Directory does not exist or is not a folder: {folder_path_str}")
        
    # Check if root or sensitive directory
    p_str = str(p).lower()
    if p_str in ["/", "c:\\", "c:/", "/system", "/etc", "/private"]:
        raise ValueError("Scanning system root directories is prohibited for safety.")
        
    return p

def calculate_file_hash(file_path: Path, max_bytes: int = 10 * 1024 * 1024) -> str:
    """
    Computes SHA-256 hash of file content.
    Reads in 64KB blocks. Limits reading to 10MB to maintain low RAM on 8GB machines.
    """
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        bytes_read = 0
        while chunk := f.read(65536):
            hasher.update(chunk)
            bytes_read += len(chunk)
            if bytes_read >= max_bytes:
                break
    return hasher.hexdigest()

def scan_directory(folder_path: Path) -> Generator[Dict[str, Any], None, None]:
    """
    Recursively scans user folder and yields file metadata.
    Does not load file contents into memory.
    """
    for root, dirs, files in os.walk(folder_path):
        # Exclude forbidden directories in-place to avoid descending into them
        dirs[:] = [d for d in dirs if d.lower() not in FORBIDDEN_DIR_NAMES and not d.startswith(".")]
        
        for file in files:
            file_path = Path(root) / file
            if not is_safe_and_supported_path(file_path):
                continue
                
            try:
                stat = file_path.stat()
                # Skip files larger than 50MB to protect memory
                if stat.st_size > 50 * 1024 * 1024:
                    logger.warning(f"Skipping oversized file ({stat.st_size} bytes): {file_path.name}")
                    continue
                    
                content_hash = calculate_file_hash(file_path)
                
                yield {
                    "path": str(file_path.resolve()),
                    "filename": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "content_hash": content_hash
                }
            except (PermissionError, FileNotFoundError, OSError) as e:
                logger.warning(f"Could not read metadata for {file_path}: {e}")
                continue

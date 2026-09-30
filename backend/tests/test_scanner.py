import pytest
from pathlib import Path
from backend.app.ingestion.scanner import (
    validate_user_folder,
    is_safe_and_supported_path,
    calculate_file_hash,
    scan_directory
)

def test_validate_user_folder_valid(tmp_path):
    validated = validate_user_folder(str(tmp_path))
    assert validated.resolve() == tmp_path.resolve()

def test_validate_user_folder_nonexistent():
    with pytest.raises(ValueError):
        validate_user_folder("/non_existent_directory_abc_123")

def test_validate_user_folder_root_prohibited():
    with pytest.raises(ValueError):
        validate_user_folder("/")

def test_supported_extensions():
    assert is_safe_and_supported_path(Path("notes.pdf"))
    assert is_safe_and_supported_path(Path("algo.cpp"))
    assert is_safe_and_supported_path(Path("main.py"))
    assert is_safe_and_supported_path(Path("data.csv"))
    assert not is_safe_and_supported_path(Path("app.exe"))
    assert not is_safe_and_supported_path(Path(".env"))
    assert not is_safe_and_supported_path(Path(".ssh/id_rsa"))

def test_file_hashing(tmp_path):
    test_file = tmp_path / "hello.txt"
    test_file.write_text("Hello PC Memory!")
    h1 = calculate_file_hash(test_file)
    assert len(h1) == 64
    
    # Same content -> same hash
    h2 = calculate_file_hash(test_file)
    assert h1 == h2

    # Modified content -> different hash
    test_file.write_text("Hello PC Memory Modified!")
    h3 = calculate_file_hash(test_file)
    assert h1 != h3

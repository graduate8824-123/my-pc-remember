import pytest
import tempfile
import os
from pathlib import Path
from backend.app.db.database import init_db
from backend.app.db.repositories import Repository
from backend.app.vectorstore.faiss_store import FAISSVectorStore

@pytest.fixture
def temp_db_and_repo():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        init_db(db_path)
        repo = Repository(db_path)
        yield repo, db_path

@pytest.fixture
def temp_vector_store():
    store = FAISSVectorStore(dimension=384)
    yield store

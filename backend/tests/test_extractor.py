import pytest
from pathlib import Path
from backend.app.ingestion.extractor import DocumentExtractor

def test_extract_text_file(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("Dijkstra algorithm uses a priority queue to calculate shortest paths.")
    extracted = DocumentExtractor.extract(str(f))
    assert "Dijkstra" in extracted.content
    assert extracted.word_count >= 8
    assert extracted.page_count == 1

def test_extract_code_file(tmp_path):
    f = tmp_path / "test.cpp"
    f.write_text("""
    #include <iostream>
    int main() {
        std::cout << "Graph traversal";
        return 0;
    }
    """)
    extracted = DocumentExtractor.extract(str(f))
    assert "Graph traversal" in extracted.content
    assert extracted.word_count > 4

def test_extract_pdf_file():
    sample_pdf = Path("data/sample_documents/DSA/graph_notes.pdf")
    if sample_pdf.exists():
        extracted = DocumentExtractor.extract(str(sample_pdf))
        assert "Dijkstra" in extracted.content
        assert extracted.page_count >= 1

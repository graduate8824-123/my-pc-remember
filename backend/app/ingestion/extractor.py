import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from ..core.logging import logger

@dataclass
class ExtractedDocument:
    content: str
    word_count: int
    page_count: int = 1

class DocumentExtractor:
    """
    Modular, safe text extractor for PDFs, DOCX, PPTX, and standard text/code files.
    Never executes file content.
    """

    @classmethod
    def extract(cls, file_path: str) -> ExtractedDocument:
        p = Path(file_path)
        ext = p.suffix.lower()

        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            if ext == ".pdf":
                return cls._extract_pdf(p)
            elif ext == ".docx":
                return cls._extract_docx(p)
            elif ext == ".pptx":
                return cls._extract_pptx(p)
            else:
                return cls._extract_text_or_code(p)
        except Exception as e:
            logger.error(f"Failed extracting text from {p.name}: {e}")
            raise

    @classmethod
    def _extract_pdf(cls, file_path: Path) -> ExtractedDocument:
        try:
            import pymupdf  # PyMuPDF
            doc = pymupdf.open(str(file_path))
        except ImportError:
            try:
                import fitz
                doc = fitz.open(str(file_path))
            except ImportError:
                raise RuntimeError("PyMuPDF is not installed for PDF extraction.")

        pages_text = []
        page_count = len(doc)

        for page_idx in range(page_count):
            try:
                page = doc[page_idx]
                text = page.get_text()
                if text.strip():
                    pages_text.append(text.strip())
            except Exception as e:
                logger.warning(f"Error reading page {page_idx} of {file_path.name}: {e}")

        doc.close()
        full_text = "\n\n".join(pages_text).strip()
        word_count = len(full_text.split())
        return ExtractedDocument(content=full_text, word_count=word_count, page_count=max(1, page_count))

    @classmethod
    def _extract_docx(cls, file_path: Path) -> ExtractedDocument:
        try:
            import docx
            doc = docx.Document(str(file_path))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n".join(paragraphs).strip()
            word_count = len(full_text.split())
            return ExtractedDocument(content=full_text, word_count=word_count, page_count=1)
        except ImportError:
            raise RuntimeError("python-docx is not installed.")

    @classmethod
    def _extract_pptx(cls, file_path: Path) -> ExtractedDocument:
        try:
            import pptx
            prs = pptx.Presentation(str(file_path))
            slide_texts = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_texts.append(shape.text.strip())
            full_text = "\n\n".join(slide_texts).strip()
            word_count = len(full_text.split())
            return ExtractedDocument(content=full_text, word_count=word_count, page_count=len(prs.slides))
        except ImportError:
            raise RuntimeError("python-pptx is not installed.")

    @classmethod
    def _extract_text_or_code(cls, file_path: Path) -> ExtractedDocument:
        # Try UTF-8 first, fallback to Latin-1
        text = ""
        for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                with open(file_path, "r", encoding=encoding, errors="replace") as f:
                    text = f.read()
                break
            except Exception:
                continue

        text = text.strip()
        word_count = len(text.split())
        return ExtractedDocument(content=text, word_count=word_count, page_count=1)

import re
from typing import List
from dataclasses import dataclass

@dataclass
class TextChunk:
    chunk_index: int
    content: str
    start_pos: int
    end_pos: int
    token_estimate: int

class TextChunker:
    """
    Splits text into chunks of target token count with overlap.
    Preserves paragraph and sentence boundaries for higher semantic coherence.
    Token estimate: ~4 characters per token (standard heuristic).
    """

    def __init__(self, target_tokens: int = 700, overlap_tokens: int = 100):
        self.target_tokens = max(10, target_tokens)
        self.overlap_tokens = max(0, min(overlap_tokens, self.target_tokens // 2))
        self.target_chars = self.target_tokens * 4
        self.overlap_chars = self.overlap_tokens * 4

    def chunk_text(self, text: str) -> List[TextChunk]:
        clean_text = text.strip()
        if not clean_text:
            return []

        # If text is small enough, return as single chunk
        if len(clean_text) <= self.target_chars:
            return [TextChunk(
                chunk_index=0,
                content=clean_text,
                start_pos=0,
                end_pos=len(clean_text),
                token_estimate=len(clean_text) // 4
            )]

        # Split into paragraphs or sentences
        paragraphs = re.split(r'(\n\s*\n)', clean_text)
        segments: List[str] = []
        for p in paragraphs:
            if not p:
                continue
            if len(p) > self.target_chars:
                # Break large paragraph by sentences
                sentences = re.split(r'((?<=[.?!])\s+)', p)
                segments.extend([s for s in sentences if s])
            else:
                segments.append(p)

        chunks: List[TextChunk] = []
        current_chunk_pieces: List[str] = []
        current_length = 0
        current_start = 0
        text_pointer = 0
        chunk_idx = 0

        for seg in segments:
            seg_len = len(seg)
            if current_length + seg_len > self.target_chars and current_chunk_pieces:
                # Complete the current chunk
                chunk_text = "".join(current_chunk_pieces).strip()
                if chunk_text:
                    chunks.append(TextChunk(
                        chunk_index=chunk_idx,
                        content=chunk_text,
                        start_pos=current_start,
                        end_pos=current_start + len(chunk_text),
                        token_estimate=max(1, len(chunk_text) // 4)
                    ))
                    chunk_idx += 1

                # Retain overlap for the next chunk
                overlap_pieces: List[str] = []
                overlap_len = 0
                for p in reversed(current_chunk_pieces):
                    if overlap_len + len(p) <= self.overlap_chars:
                        overlap_pieces.insert(0, p)
                        overlap_len += len(p)
                    else:
                        break

                current_chunk_pieces = overlap_pieces + [seg]
                current_length = overlap_len + seg_len
                current_start = max(0, text_pointer - overlap_len)
            else:
                current_chunk_pieces.append(seg)
                current_length += seg_len

            text_pointer += seg_len

        # Final chunk
        if current_chunk_pieces:
            chunk_text = "".join(current_chunk_pieces).strip()
            if chunk_text:
                chunks.append(TextChunk(
                    chunk_index=chunk_idx,
                    content=chunk_text,
                    start_pos=current_start,
                    end_pos=current_start + len(chunk_text),
                    token_estimate=max(1, len(chunk_text) // 4)
                ))

        return chunks

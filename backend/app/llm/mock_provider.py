import re
from typing import Optional, List
from .base import LLMProvider

class MockLLMProvider(LLMProvider):
    """
    Deterministic local development provider.
    Provides explainable search results without requiring external LLM installation.
    Analyzes semantic query overlap and extracts grounded reasoning directly from text.
    """

    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        if not context:
            return "I couldn't find enough information in your indexed files."
        return f"Based on indexed context: {context[:200]}..."

    def explain_match(self, query: str, filename: str, matched_chunk: str) -> str:
        clean_chunk = matched_chunk.strip()
        if not clean_chunk:
            return "Relevant content found, but no explanation could be generated."

        # Extract salient terms from query
        query_words = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', query.lower()))
        # Remove common stop words
        stop_words = {"find", "the", "where", "what", "with", "that", "this", "some", "notes", "file", "code", "worked", "recently", "remember"}
        salient_terms = [w for w in query_words if w not in stop_words]

        # Find which salient terms or synonyms appear in matched chunk
        matched_terms: List[str] = []
        chunk_lower = clean_chunk.lower()
        for term in salient_terms:
            if term in chunk_lower:
                # Find matching case from chunk
                m = re.search(rf'\b{re.escape(term)}\b', clean_chunk, re.IGNORECASE)
                if m:
                    matched_terms.append(m.group(0))
                else:
                    matched_terms.append(term)

        # Look for domain concepts if specific terms match
        concepts = []
        if "dijkstra" in chunk_lower:
            concepts.append("Dijkstra's algorithm")
        if "shortest" in chunk_lower and "path" in chunk_lower:
            concepts.append("shortest paths")
        if "priority" in chunk_lower or "queue" in chunk_lower or "heap" in chunk_lower:
            concepts.append("priority queues")
        if "kruskal" in chunk_lower:
            concepts.append("Kruskal's algorithm")
        if "dsu" in chunk_lower or "disjoint" in chunk_lower or "union" in chunk_lower:
            concepts.append("disjoint set union (DSU)")
        if "bfs" in chunk_lower or "breadth" in chunk_lower:
            concepts.append("breadth-first graph traversal")
        if "tree" in chunk_lower or "graph" in chunk_lower:
            concepts.append("graph structures")

        # Combine distinct concepts
        for c in concepts:
            if not any(c.lower() in m.lower() for m in matched_terms):
                matched_terms.append(c)

        if matched_terms:
            terms_str = ", ".join(matched_terms[:4])
            if filename.endswith(('.cpp', '.py', '.c', '.java', '.js', '.ts', '.tsx', '.sh')):
                return f"Contains implementation concepts for {terms_str}."
            return f"Contains notes covering {terms_str} and related concepts."

        # Fallback to key snippet sentence
        sentences = [s.strip() for s in re.split(r'[.!?\n]', clean_chunk) if len(s.strip()) > 15]
        if sentences:
            return f"Matches context: \"{sentences[0][:120]}...\""
            
        return "Relevant content found matching semantic context."

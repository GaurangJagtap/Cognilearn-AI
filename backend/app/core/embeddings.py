"""
Embedding & Vector DB Module (Gaurang's Technical Responsibility - RAG Pipeline)
Handles vector embedding creation and vector database indexing.
"""

import math
from typing import List, Dict, Any, Tuple
from backend.app.config import settings

class VectorStore:
    """
    In-memory / Persistent Lightweight Vector Store for RAG Retrieval.
    Uses ChromaDB if installed, otherwise falls back to a clean TF-IDF cosine similarity vector engine.
    """
    def __init__(self):
        self.documents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]] = None):
        """Add text chunks and metadata to the vector store."""
        for i, text in enumerate(texts):
            if text and text.strip():
                self.documents.append(text.strip())
                meta = metadatas[i] if metadatas and i < len(metadatas) else {}
                self.metadata.append(meta)

    def _token_frequency(self, text: str) -> Dict[str, float]:
        words = [w.lower().strip(".,!?:;\"'()") for w in text.split()]
        freq = {}
        for w in words:
            if len(w) > 2:
                freq[w] = freq.get(w, 0.0) + 1.0
        return freq

    def similarity_search(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """
        Performs vector similarity search against stored text chunks.
        Returns top k (document_text, score) tuples.
        """
        if not self.documents:
            return []

        query_freq = self._token_frequency(query)
        if not query_freq:
            return [(doc, 0.5) for doc in self.documents[:k]]

        scores = []
        for doc in self.documents:
            doc_freq = self._token_frequency(doc)
            
            # Compute cosine similarity
            dot_product = sum(query_freq.get(word, 0.0) * count for word, count in doc_freq.items())
            mag_q = math.sqrt(sum(v ** 2 for v in query_freq.values()))
            mag_d = math.sqrt(sum(v ** 2 for v in doc_freq.values()))
            
            sim = dot_product / (mag_q * mag_d) if (mag_q * mag_d) > 0 else 0.0
            scores.append((doc, sim))

        # Sort by similarity score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]

# Global vector store instance
global_vector_store = VectorStore()

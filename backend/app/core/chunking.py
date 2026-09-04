"""
Document Chunking Module (Gaurang's Technical Responsibility - RAG Pipeline)
Splits raw extracted text into overlapping chunks for vector embedding and retrieval.
"""

from typing import List

def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """
    Splits text into chunks of approximate token/word length with overlap.
    """
    if not text or not text.strip():
        return []

    words = text.split()
    if len(words) <= chunk_size:
        return [text.strip()]

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += (chunk_size - overlap)
        
    return chunks

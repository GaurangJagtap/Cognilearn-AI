"""
RAG Retriever Module (Gaurang's Technical Responsibility - Knowledge Grounding)
Ingests text documents into vector store and retrieves relevant grounded context chunks.
"""

from typing import List
from backend.app.core.chunking import chunk_text
from backend.app.core.embeddings import global_vector_store

def ingest_document(text: str, chunk_size: int = 200, overlap: int = 30, reset: bool = True) -> int:
    """
    Chunks document text and indexes into the RAG vector store.
    Clears existing vector store by default to avoid cross-document pollution.
    Returns the number of chunks indexed.
    """
    if reset:
        global_vector_store.clear()
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    if chunks:
        global_vector_store.add_texts(chunks)
    return len(chunks)

def retrieve_relevant_chunks(query: str, top_k: int = 3) -> str:
    """
    Retrieves the top-k grounded context chunks for a query.
    Returns formatted context string to inject into Lesson Planner prompt.
    """
    results = global_vector_store.similarity_search(query, k=top_k)
    if not results:
        return ""

    formatted_context = []
    for idx, (doc, score) in enumerate(results, 1):
        formatted_context.append(f"--- Grounded Context Excerpt {idx} (Relevance: {score:.2f}) ---\n{doc}")

    return "\n\n".join(formatted_context)

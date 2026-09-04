import json
from backend.app.core.chunking import chunk_text
from backend.app.core.retriever import ingest_document, retrieve_relevant_chunks
from backend.app.core.lesson_planner import generate_lesson_plan

def run_step_3_tests():
    print("=== Testing Step 3: RAG Pipeline & Knowledge Grounding ===")
    
    # Sample document text (e.g. uploaded physics chapter text)
    sample_text = """
    Electric current is defined as the rate of flow of electric charge through a cross-section of a conductor.
    The SI unit of electric current is Ampere (A). 1 Ampere equals 1 Coulomb per second.
    Voltage or potential difference is the energy required to move a unit charge between two points.
    Ohm's Law states that at constant temperature, the electric current passing through a metallic conductor
    is directly proportional to the potential difference across its ends: V = I * R.
    Resistance is the property of a material by which it opposes the flow of electric current.
    Electric power is calculated using P = V * I or P = I^2 * R.
    """
    
    # Test 1: Chunking
    chunks = chunk_text(sample_text, chunk_size=30, overlap=5)
    print(f"[OK] Document chunked successfully: {len(chunks)} chunks created")
    assert len(chunks) > 0, "Chunking produced 0 chunks"
    
    # Test 2: Document Ingestion into RAG Vector Store
    indexed_count = ingest_document(sample_text, chunk_size=30, overlap=5)
    print(f"[OK] RAG Vector store indexed {indexed_count} chunks")
    assert indexed_count > 0, "Ingestion failed"
    
    # Test 3: RAG Retrieval
    query = "Ohm's Law formula and voltage"
    retrieved_context = retrieve_relevant_chunks(query, top_k=2)
    print(f"[OK] RAG Retrieval for query '{query}':")
    print(retrieved_context)
    assert "Ohm's Law" in retrieved_context or "Voltage" in retrieved_context, "Retrieval missed key terms"
    
    # Test 4: End-to-end RAG grounded Lesson Planner call
    plan = generate_lesson_plan(
        topic="Electricity and Ohm's Law",
        profile={"preferred_level": "beginner"},
        time_minutes=20,
        language="en",
        retrieved_context=retrieved_context
    )
    print(f"[OK] Grounded Lesson Plan generated: '{plan.title}' with {len(plan.sections)} sections")
    assert plan is not None, "Grounded lesson plan generation failed"
    print("\n=== STEP 3 VERIFICATION PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_step_3_tests()

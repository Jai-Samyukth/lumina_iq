"""
Test script for Advanced RAG System
Demonstrates all 4 retrieval strategies with example queries
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.rag_service import rag_service
from services.query_classifier import query_classifier, query_metadata_extractor
from utils.logger import chat_logger


async def test_query_classification():
    """Test query classification"""
    print("\n" + "="*70)
    print("TEST 1: Query Classification")
    print("="*70)
    
    test_queries = [
        "What is photosynthesis?",
        "Check my answer: Photosynthesis is the process...",
        "Generate 25 questions from Chapter 3",
        "Create notes for Chapter 5",
        "Explain Newton's laws from chapter 2"
    ]
    
    for query in test_queries:
        result = query_classifier.classify_query(query)
        metadata = query_metadata_extractor.extract_all_metadata(query)
        
        print(f"\nQuery: {query}")
        print(f"  > Use Case: {result['use_case']} (confidence: {result['confidence']:.2f})")
        print(f"  > Chapter: {metadata['chapter']['value']}")
        print(f"  > Topic: {metadata['topic']['value']}")
        print(f"  > Matched Keywords: {result['matched_keywords'][:3]}")


async def test_chat_strategy():
    """Test CHAT strategy"""
    print("\n" + "="*70)
    print("TEST 2: CHAT Strategy (Conversational Q&A)")
    print("="*70)
    
    # Note: Replace with actual token and filename from your system
    test_token = "test_user_123"
    test_filename = "sample_textbook.pdf"
    
    query = "What is the definition of machine learning?"
    
    print(f"\nQuery: {query}")
    print("Expected: CHAT strategy with cross-chapter search, reranking")
    
    # Uncomment when you have actual documents indexed:
    # result = await rag_service.retrieve_context(
    #     query=query,
    #     token=test_token,
    #     filename=test_filename,
    #     top_k=5
    # )
    # 
    # print(f"\n[OK] Strategy Used: {result.get('strategy')}")
    # print(f"[OK] Chunks Retrieved: {result.get('num_chunks')}")
    # print(f"[OK] Context Length: {len(result.get('context', ''))}")
    
    print("\n[Demo Mode] Would retrieve 5-10 relevant chunks with reranking")


async def test_evaluation_strategy():
    """Test EVALUATION strategy"""
    print("\n" + "="*70)
    print("TEST 3: EVALUATION Strategy (Answer Checking)")
    print("="*70)
    
    test_token = "test_user_123"
    test_filename = "physics_textbook.pdf"
    
    query = "Evaluate this answer: Newton's first law states that an object at rest stays at rest"
    
    print(f"\nQuery: {query}")
    print("Expected: EVALUATION strategy with high threshold, context expansion")
    
    # Uncomment when you have actual documents indexed:
    # result = await rag_service.retrieve_context(
    #     query=query,
    #     token=test_token,
    #     filename=test_filename,
    #     use_case="evaluation"  # Explicit specification
    # )
    # 
    # print(f"\n[OK] Strategy Used: {result.get('strategy')}")
    # print(f"[OK] Core Chunks: {result.get('num_core_chunks')}")
    # print(f"[OK] Expanded Chunks: {result.get('num_chunks')}")
    
    print("\n[Demo Mode] Would retrieve precise chunks + ±2 context expansion")


async def test_qa_generation_strategy():
    """Test QA_GENERATION strategy"""
    print("\n" + "="*70)
    print("TEST 4: QA_GENERATION Strategy (Question Generation)")
    print("="*70)
    
    test_token = "test_user_123"
    test_filename = "chemistry_textbook.pdf"
    
    query = "Generate 25 questions from Chapter 3"
    
    print(f"\nQuery: {query}")
    print("Expected: QA_GENERATION strategy, filtered to Chapter 3, sequential chunks")
    
    # Extract metadata to show filtering
    metadata = query_metadata_extractor.extract_all_metadata(query)
    print(f"\nMetadata Extracted:")
    print(f"  > Chapter: {metadata['chapter']['value']} (conf: {metadata['chapter']['confidence']:.2f})")
    
    # Uncomment when you have actual documents indexed:
    # result = await rag_service.retrieve_context(
    #     query=query,
    #     token=test_token,
    #     filename=test_filename,
    #     use_case="qa_generation"
    # )
    # 
    # print(f"\n[OK] Strategy Used: {result.get('strategy')}")
    # print(f"[OK] Filtered By Chapter: {result.get('filtered_by_chapter')}")
    # print(f"[OK] Sequential Chunks Retrieved: {result.get('num_chunks')}")
    
    print("\n[Demo Mode] Would retrieve 15-25 sequential chunks from Chapter 3 ONLY")


async def test_notes_strategy():
    """Test NOTES strategy"""
    print("\n" + "="*70)
    print("TEST 5: NOTES Strategy (Summary Generation)")
    print("="*70)
    
    test_token = "test_user_123"
    test_filename = "biology_textbook.pdf"
    
    query = "Generate notes for Chapter 2"
    
    print(f"\nQuery: {query}")
    print("Expected: NOTES strategy, all chunks from Chapter 2, hierarchical grouping")
    
    # Extract metadata
    metadata = query_metadata_extractor.extract_all_metadata(query)
    print(f"\nMetadata Extracted:")
    print(f"  > Chapter: {metadata['chapter']['value']} (conf: {metadata['chapter']['confidence']:.2f})")
    
    # Uncomment when you have actual documents indexed:
    # result = await rag_service.retrieve_context(
    #     query=query,
    #     token=test_token,
    #     filename=test_filename,
    #     use_case="notes"
    # )
    # 
    # print(f"\n[OK] Strategy Used: {result.get('strategy')}")
    # print(f"[OK] Total Chunks: {result.get('num_chunks')}")
    # print(f"[OK] Sections Found: {result.get('num_sections')}")
    
    print("\n[Demo Mode] Would retrieve ALL chunks from Chapter 2, grouped by sections")


async def test_metadata_extraction():
    """Test metadata extraction from documents"""
    print("\n" + "="*70)
    print("TEST 6: Document Metadata Extraction")
    print("="*70)
    
    sample_text = """
    Chapter 3: Thermodynamics
    
    Section 3.1: Introduction to Heat Transfer
    
    Heat transfer is defined as the movement of thermal energy from one object to another.
    There are three main types of heat transfer: conduction, convection, and radiation.
    
    For example, when you touch a hot stove, heat is transferred through conduction.
    
    Section 3.2: Laws of Thermodynamics
    
    The first law of thermodynamics states that energy cannot be created or destroyed.
    """
    
    from services.chunking_service import chunking_service
    
    print("\nSample Document Text:")
    print(sample_text[:200] + "...")
    
    # Test chunking with metadata
    chunks_with_metadata = chunking_service.chunk_with_rich_metadata(
        text=sample_text,
        document_name="thermodynamics.pdf",
        chunk_size=500,
        overlap=100
    )
    
    print(f"\n[OK] Created {len(chunks_with_metadata)} chunks with metadata")
    
    # Show first chunk metadata
    if chunks_with_metadata:
        first_chunk = chunks_with_metadata[0]
        metadata = first_chunk['metadata']
        
        print(f"\nFirst Chunk Metadata:")
        print(f"  > Chapter: {metadata.get('chapter_number')} - {metadata.get('chapter_title')}")
        print(f"  > Section: {metadata.get('section_number')} - {metadata.get('section_title')}")
        print(f"  > Content Types: {metadata.get('content_types')}")
        print(f"  > Word Count: {metadata.get('word_count')}")
        print(f"  > Has Headings: {metadata.get('has_headings')}")


async def test_strategy_comparison():
    """Compare all strategies side by side"""
    print("\n" + "="*70)
    print("TEST 7: Strategy Comparison Table")
    print("="*70)
    
    print("""
    ┌──────────────┬─────────────┬──────────────┬────────────┬─────────────┐
    │ Strategy     │ Chunk Size  │ # Chunks     │ Filtering  │ Ordering    │
    ├──────────────┼─────────────┼──────────────┼────────────┼─────────────┤
    │ CHAT         │ Medium      │ 5-10         │ Optional   │ Relevance   │
    │ EVALUATION   │ Small       │ 5-10 (exp.)  │ Strict     │ Relevance   │
    │ QA_GEN       │ Large       │ 15-25        │ MANDATORY  │ Sequential  │
    │ NOTES        │ Large       │ 20-50        │ Strict     │ Sequential  │
    └──────────────┴─────────────┴──────────────┴────────────┴─────────────┘
    
    Key Differences:
    
    1. CHAT: Best for general questions, allows cross-chapter retrieval
    2. EVALUATION: High precision for answer checking, includes context
    3. QA_GEN: Chapter-specific, sequential for complete concepts
    4. NOTES: Comprehensive coverage, hierarchical organization
    """)


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("ADVANCED RAG SYSTEM - TEST SUITE")
    print("="*70)
    print("\nThis test suite demonstrates all features of the Advanced RAG system.")
    print("For full functionality, index actual documents first.\n")
    
    try:
        await test_query_classification()
        await test_metadata_extraction()
        await test_chat_strategy()
        await test_evaluation_strategy()
        await test_qa_generation_strategy()
        await test_notes_strategy()
        await test_strategy_comparison()
        
        print("\n" + "="*70)
        print("[SUCCESS] ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70)
        
        print("\n[INFO] Next Steps:")
        print("1. Index documents using: await rag_service.index_document()")
        print("2. Run queries with: await rag_service.retrieve_context()")
        print("3. Check ADVANCED_RAG_SYSTEM.md for detailed documentation")
        print("4. System auto-detects use case from query")
        print("5. Or specify explicitly with use_case parameter\n")
        
    except Exception as e:
        print(f"\n[ERROR] Error during tests: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

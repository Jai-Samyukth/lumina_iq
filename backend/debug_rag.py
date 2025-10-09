import sys
import asyncio
sys.path.append('C:\\Shyamnath\\learning\\backend')

from services.rag_service import RAGService
from services.embedding_service import EmbeddingService
from services.chunking_service import chunking_service

async def debug_rag():
    print("=== Testing RAG Pipeline Components ===\n")
    
    # Test data
    test_text = """
    This is a test document for debugging RAG pipeline.
    It contains multiple sentences and paragraphs to test the chunking process.
    
    The second paragraph has different content.
    We want to make sure everything works correctly.
    """
    test_token = "debug_user_123"
    test_filename = "debug_test.pdf"
    
    # Test 1: Chunking
    print("--- Test 1: Chunking Service ---")
    try:
        chunks = chunking_service.chunk_text(test_text, chunk_size=100, chunk_overlap=20)
        print(f"✅ Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            print(f"   Chunk {i+1}: {chunk[:50]}...")
    except Exception as e:
        print(f"❌ Chunking failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Embedding Generation
    print("\n--- Test 2: Embedding Service ---")
    try:
        print("Generating embedding for single text...")
        test_embedding = await EmbeddingService.generate_embedding(chunks[0])
        print(f"✅ Generated embedding with {len(test_embedding)} dimensions")
        print(f"   First 5 values: {test_embedding[:5]}")
    except Exception as e:
        print(f"❌ Single embedding failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 3: Batch Embedding Generation
    print("\n--- Test 3: Batch Embedding Generation ---")
    try:
        print(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = await EmbeddingService.generate_embeddings_batch(chunks)
        print(f"✅ Generated {len(embeddings)} embeddings")
        for i, emb in enumerate(embeddings):
            print(f"   Embedding {i+1}: {len(emb)} dimensions")
    except Exception as e:
        print(f"❌ Batch embedding failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 4: Full RAG Indexing
    print("\n--- Test 4: Full RAG Indexing ---")
    try:
        print(f"Indexing document: {test_filename}")
        result = await RAGService.index_document(
            filename=test_filename,
            content=test_text,
            token=test_token
        )
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        if result.get('status') == 'success':
            print(f"✅ Successfully indexed {result.get('num_indexed')} chunks")
        else:
            print(f"❌ Indexing failed")
    except Exception as e:
        print(f"❌ RAG indexing failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 5: Retrieval
    print("\n--- Test 5: RAG Retrieval ---")
    try:
        print("Searching for relevant chunks...")
        result = await RAGService.retrieve_context(
            query="test document",
            token=test_token,
            filename=test_filename,
            top_k=2
        )
        print(f"Status: {result.get('status')}")
        print(f"Found {result.get('num_chunks', 0)} chunks")
        if result.get('chunks'):
            for i, chunk in enumerate(result['chunks'], 1):
                print(f"   {i}. Score: {chunk['score']:.4f}, Text: {chunk['text'][:50]}...")
        print("✅ Retrieval successful")
    except Exception as e:
        print(f"❌ Retrieval failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    asyncio.run(debug_rag())

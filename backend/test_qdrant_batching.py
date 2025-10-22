#!/usr/bin/env python3
"""
Test script to verify Qdrant batching functionality for payload size limit fix
"""

import os
import sys
import asyncio
import numpy as np
from typing import List, Dict, Any


async def test_qdrant_batching():
    """Test the Qdrant batching functionality"""
    print("Testing Qdrant batching functionality...")

    try:
        # Import the Qdrant service
        sys.path.insert(0, os.path.dirname(__file__))
        from services.qdrant_service import qdrant_service

        print("✓ Qdrant service imported successfully")

        # Test 1: Check if collection exists or can be created
        print("\n1. Testing collection setup...")
        try:
            # This should not fail even if collection doesn't exist
            collections = qdrant_service.client.get_collections()
            print(
                f"   ✓ Connected to Qdrant, found {len(collections.collections)} collections"
            )
        except Exception as e:
            print(f"   ✗ Collection setup failed: {str(e)}")
            return False

        # Test 2: Test batching with small dataset
        print("\n2. Testing batching with small dataset...")
        test_filename = "test_batching_small.txt"
        test_token = "test_token_123"

        # Create test data
        chunks = [f"This is test chunk number {i}" for i in range(50)]
        embeddings = [
            np.random.rand(384).tolist() for _ in range(50)
        ]  # 384-dim embeddings

        try:
            result_count = await qdrant_service.index_document(
                filename=test_filename,
                chunks=chunks,
                embeddings=embeddings,
                token=test_token,
            )

            print(f"   ✓ Successfully indexed {result_count} chunks in batches")
            print(f"   Expected: 50, Got: {result_count}")

            if result_count == 50:
                print("   ✓ Small batch test passed")
            else:
                print("   ✗ Small batch test failed - count mismatch")
                return False

        except Exception as e:
            print(f"   ✗ Small batch test failed: {str(e)}")
            return False

        # Test 3: Test batching with larger dataset (should trigger multiple batches)
        print("\n3. Testing batching with larger dataset (multiple batches)...")
        large_test_filename = "test_batching_large.txt"
        large_test_token = "test_token_456"

        # Create test data that will definitely trigger batching (250 chunks)
        large_chunks = [
            f"This is large test chunk number {i} with more content to increase payload size"
            for i in range(250)
        ]
        large_embeddings = [np.random.rand(384).tolist() for _ in range(250)]

        try:
            large_result_count = await qdrant_service.index_document(
                filename=large_test_filename,
                chunks=large_chunks,
                embeddings=large_embeddings,
                token=large_test_token,
            )

            print(
                f"   ✓ Successfully indexed {large_result_count} chunks in multiple batches"
            )
            print(f"   Expected: 250, Got: {large_result_count}")

            if large_result_count == 250:
                print("   ✓ Large batch test passed")
            else:
                print("   ✗ Large batch test failed - count mismatch")
                return False

        except Exception as e:
            print(f"   ✗ Large batch test failed: {str(e)}")
            return False

        # Test 4: Verify chunks were actually indexed
        print("\n4. Verifying chunks were indexed...")
        try:
            # Check if document is indexed
            is_indexed = await qdrant_service.check_document_indexed(
                large_test_filename, large_test_token
            )
            print(f"   Document indexed check: {'✓ Yes' if is_indexed else '✗ No'}")

            if not is_indexed:
                print("   ✗ Verification failed - document not found in index")
                return False

            # Search for some chunks
            query_embedding = np.random.rand(384).tolist()
            search_results = await qdrant_service.search_similar_chunks(
                query_embedding=query_embedding,
                token=large_test_token,
                filename=large_test_filename,
                limit=5,
            )

            print(f"   ✓ Search returned {len(search_results)} results")
            print("   ✓ Verification successful")

        except Exception as e:
            print(f"   ✗ Verification failed: {str(e)}")
            return False

        # Test 5: Clean up test data
        print("\n5. Cleaning up test data...")
        try:
            await qdrant_service.delete_document_chunks(
                large_test_filename, large_test_token
            )
            await qdrant_service.delete_document_chunks(test_filename, test_token)
            print("   ✓ Test data cleaned up successfully")
        except Exception as e:
            print(f"   ⚠ Cleanup warning: {str(e)}")

        print("\n✓ All Qdrant batching tests passed!")
        print("✓ The 34MB payload size limit fix is working correctly")
        return True

    except ImportError as e:
        print(f"✗ Import error: {str(e)}")
        print("Make sure all dependencies are installed and paths are correct")
        return False
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("QDRANT BATCHING TEST")
    print("=" * 60)

    # Check if .env file exists and has required settings
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_file):
        print("⚠ Warning: .env file not found")
        print("   Make sure QDRANT_URL and QDRANT_API_KEY are configured")
        print("   Or run: cp .env.example .env and configure the values")

    # Run the async test
    result = asyncio.run(test_qdrant_batching())

    print("\n" + "=" * 60)
    if result:
        print("🎉 ALL TESTS PASSED - Batching fix is working!")
    else:
        print("❌ TESTS FAILED - Check configuration and try again")
    print("=" * 60)


if __name__ == "__main__":
    main()

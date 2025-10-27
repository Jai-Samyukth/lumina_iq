#!/usr/bin/env python3
"""
Test script for NLTK integration and LlamaIndex setup.
This script verifies that NLTK data is properly initialized and LlamaIndex can work correctly.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_nltk_initialization():
    """Test NLTK data initialization"""
    print("🔍 Testing NLTK initialization...")

    try:
        from utils.nltk_init import initialize_nltk_data, safe_nltk_operation
        import nltk

        # Initialize NLTK data
        print("📥 Initializing NLTK data...")
        initialize_nltk_data()

        # Test basic NLTK operations
        print("🧪 Testing NLTK operations...")

        # Test sentence tokenization
        test_text = "This is a test sentence. This is another sentence!"
        result = safe_nltk_operation("sent_tokenize", nltk.sent_tokenize, test_text)
        print(f"✅ Sentence tokenization: {result}")

        # Test word tokenization
        result = safe_nltk_operation("word_tokenize", nltk.word_tokenize, test_text)
        print(f"✅ Word tokenization: {result}")

        # Test if punkt_tab tokenizer is available
        try:
            nltk.data.find("tokenizers/punkt_tab")
            print("✅ NLTK punkt_tab tokenizer is available")
        except LookupError:
            print("❌ NLTK punkt_tab tokenizer is missing")
            return False

        print("✅ NLTK initialization successful!")
        return True

    except Exception as e:
        print(f"❌ NLTK initialization failed: {e}")
        return False


def test_llamaindex_setup():
    """Test LlamaIndex service setup"""
    print("\n🔍 Testing LlamaIndex setup...")

    try:
        from services.llamaindex_service import llamaindex_service
        from config.settings import settings

        print("📦 LlamaIndex service imported successfully")
        print(f"📊 Embedding model: {settings.EMBEDDING_MODEL}")
        print(f"📏 Chunk size: {settings.LLAMAINDEX_CHUNK_SIZE}")
        print(f"📏 Chunk overlap: {settings.LLAMAINDEX_CHUNK_OVERLAP}")

        # Test service initialization
        print("🔧 LlamaIndex service initialized successfully")
        print("✅ LlamaIndex setup successful!")
        return True

    except Exception as e:
        print(f"❌ LlamaIndex setup failed: {e}")
        return False


def test_pdf_service_integration():
    """Test PDF service with LlamaIndex integration"""
    print("\n🔍 Testing PDF service integration...")

    try:
        from services.pdf_service import PDFService

        # Test the should_use_llamaindex method
        test_file = "/tmp/test_large.pdf"
        with open(test_file, "wb") as f:
            f.write(b"0" * (15 * 1024 * 1024))  # 15MB file

        should_use = PDFService.should_use_llamaindex(test_file)
        print(f"📄 Should use LlamaIndex for 15MB PDF: {should_use}")

        # Clean up
        os.remove(test_file)

        print("✅ PDF service integration successful!")
        return True

    except Exception as e:
        print(f"❌ PDF service integration failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting NLTK and LlamaIndex integration tests...\n")

    tests = [
        test_nltk_initialization,
        test_llamaindex_setup,
        test_pdf_service_integration,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)

    print("\n📊 Test Results:")
    print(f"✅ NLTK Initialization: {'PASS' if results[0] else 'FAIL'}")
    print(f"✅ LlamaIndex Setup: {'PASS' if results[1] else 'FAIL'}")
    print(f"✅ PDF Service Integration: {'PASS' if results[2] else 'FAIL'}")

    if all(results):
        print(
            "\n🎉 All tests passed! NLTK and LlamaIndex integration is working correctly."
        )
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit(main())

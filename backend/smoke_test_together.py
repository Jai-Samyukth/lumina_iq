#!/usr/bin/env python3
"""
Simple smoke test for Together.ai integration without requiring API key

This script tests the basic functionality that doesn't require API calls:
1. Configuration loading and validation
2. Service initialization
3. Error handling for missing API key
4. Basic service structure validation

Usage:
    python smoke_test_together.py
"""

import sys
import os

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))


def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")

    try:
        from config.settings import settings

        print("  ✓ Settings imported successfully")

        from services.together_service import TogetherService

        print("  ✓ TogetherService imported successfully")

        from services.embedding_service import EmbeddingService

        print("  ✓ EmbeddingService imported successfully")

        from services.chat_service import ChatService

        print("  ✓ ChatService imported successfully")

        return True
    except Exception as e:
        print(f"  ✗ Import failed: {str(e)}")
        return False


def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")

    try:
        from config.settings import settings

        # Check API key (will be placeholder)
        api_key = settings.TOGETHER_API_KEY
        print(f"  API Key configured: {api_key != 'your_together_api_key_here'}")
        print(f"  API Key length: {len(api_key) if api_key else 0}")

        # Check model configuration
        model = settings.TOGETHER_MODEL
        embedding_model = settings.EMBEDDING_MODEL
        print(f"  Chat Model: {model}")
        print(f"  Embedding Model: {embedding_model}")

        # Check embedding dimensions
        dimensions = settings.EMBEDDING_DIMENSIONS
        print(f"  Embedding Dimensions: {dimensions}")

        return True
    except Exception as e:
        print(f"  ✗ Configuration test failed: {str(e)}")
        return False


def test_service_initialization():
    """Test service initialization without API calls"""
    print("\nTesting service initialization...")

    try:
        from config.settings import settings
        from services.together_service import TogetherService
        from services.embedding_service import EmbeddingService

        # Test static methods that don't require API calls
        print("  Testing TogetherService static methods...")

        # These should work without API key validation
        api_key = TogetherService.get_api_key()
        model = TogetherService.get_model()
        base_url = TogetherService.get_base_url()

        print(f"    API Key: {len(api_key) if api_key else 0} chars")
        print(f"    Model: {model}")
        print(f"    Base URL: {base_url}")

        print("  Testing EmbeddingService static methods...")
        emb_api_key = EmbeddingService.get_api_key()
        emb_model = EmbeddingService.get_embedding_model()
        emb_dimensions = EmbeddingService.get_embedding_dimensions()

        print(f"    API Key: {len(emb_api_key) if emb_api_key else 0} chars")
        print(f"    Embedding Model: {emb_model}")
        print(f"    Dimensions: {emb_dimensions}")

        return True
    except Exception as e:
        print(f"  ✗ Service initialization failed: {str(e)}")
        return False


def test_error_handling():
    """Test error handling for missing API key"""
    print("\nTesting error handling...")

    try:
        from config.settings import settings
        from services.together_service import TogetherService

        # Test that proper errors are raised for missing API key
        print("  Testing API key validation...")

        # Temporarily set invalid key
        original_key = settings.TOGETHER_API_KEY
        settings.TOGETHER_API_KEY = ""

        try:
            # This should raise an error
            TogetherService.initialize_client()
            print("    ✗ Expected error for empty API key")
            return False
        except ValueError as e:
            print(f"    ✓ Proper error for empty API key: {str(e)}")
        except Exception as e:
            print(f"    ✓ Error for empty API key (unexpected type): {str(e)}")
        finally:
            # Restore original key
            settings.TOGETHER_API_KEY = original_key

        # Test with placeholder key
        settings.TOGETHER_API_KEY = "your_together_api_key_here"

        try:
            # This should raise an error for invalid key
            TogetherService.initialize_client()
            print("    ✗ Expected error for placeholder API key")
            return False
        except Exception as e:
            print(f"    ✓ Proper error for placeholder API key: {type(e).__name__}")
        finally:
            # Restore original key
            settings.TOGETHER_API_KEY = original_key

        return True
    except Exception as e:
        print(f"  ✗ Error handling test failed: {str(e)}")
        return False


def main():
    """Run all smoke tests"""
    print("🔥 Together.ai Integration Smoke Tests")
    print("=" * 50)

    tests = [
        test_imports,
        test_configuration,
        test_service_initialization,
        test_error_handling,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"💥 Test {test.__name__} crashed: {str(e)}")
            results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)

    print(f"\n{'=' * 50}")
    print("SMOKE TEST SUMMARY")
    print(f"{'=' * 50}")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed / total * 100:.1f}%" if total > 0 else "N/A")

    if passed == total:
        print(
            "\n🎉 All smoke tests passed! The integration structure is working correctly."
        )
        print("   Note: API functionality tests require a valid Together.ai API key.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the implementation.")

    print(f"{'=' * 50}")
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

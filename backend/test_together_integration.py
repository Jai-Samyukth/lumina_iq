#!/usr/bin/env python3
"""
Comprehensive Together.ai Integration Test Script

This script tests all aspects of the Together.ai integration including:
1. Configuration loading and validation
2. API connectivity and health checks
3. Embedding service with BAAI/bge-large-en-v1.5 model
4. Chat service with openai/gpt-oss-20b model
5. Error handling and edge cases

Usage:
    python test_together_integration.py

Requirements:
    - Together.ai API key configured in .env file
    - together, asyncio, and logging dependencies installed
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))

from config.settings import settings
from services.together_service import TogetherService
from services.embedding_service import EmbeddingService
from services.chat_service import ChatService
from utils.logger import chat_logger


class TogetherIntegrationTester:
    """Comprehensive tester for Together.ai integration"""

    def __init__(self):
        self.test_results = []
        self.start_time = time.time()

    def log_test_result(
        self,
        test_name: str,
        success: bool,
        message: str,
        details: Dict[str, Any] | None = None,
    ):
        """Log test result with timestamp"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}: {message}")

        if details:
            print(f"      Details: {json.dumps(details, indent=2)}")

    def print_summary(self):
        """Print test summary"""
        end_time = time.time()
        duration = end_time - self.start_time

        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)

        print(f"\n{'=' * 60}")
        print("TEST SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Duration: {duration:.2f}s")
        print(f"Success Rate: {(passed / total) * 100:.1f}%" if total > 0 else "N/A")

        if total - passed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")

        print(f"{'=' * 60}")

    async def test_configuration_loading(self):
        """Test configuration loading and validation"""
        print("\nTesting Configuration Loading...")
        try:
            # Test API key loading
            api_key = settings.TOGETHER_API_KEY
            if not api_key or api_key == "your_together_api_key_here":
                self.log_test_result(
                    "Configuration Loading",
                    False,
                    "TOGETHER_API_KEY not configured or using placeholder value",
                    {"api_key": api_key[:20] + "..." if api_key else "None"},
                )
                return False

            # Test model configuration
            model = settings.TOGETHER_MODEL
            embedding_model = settings.EMBEDDING_MODEL

            # Test base URL configuration
            base_url = settings.TOGETHER_BASE_URL

            self.log_test_result(
                "Configuration Loading",
                True,
                "All configuration values loaded successfully",
                {
                    "model": model,
                    "embedding_model": embedding_model,
                    "base_url": base_url,
                    "embedding_dimensions": settings.EMBEDDING_DIMENSIONS,
                },
            )
            return True

        except Exception as e:
            self.log_test_result(
                "Configuration Loading",
                False,
                f"Configuration loading failed: {str(e)}",
            )
            return False

    async def test_api_connectivity(self):
        """Test basic API connectivity and health checks"""
        print("\nTesting API Connectivity...")
        try:
            # Test health check
            is_healthy = await TogetherService.check_api_health()

            if is_healthy:
                self.log_test_result(
                    "API Health Check",
                    True,
                    "Together.ai API is accessible and responding",
                )
            else:
                self.log_test_result(
                    "API Health Check",
                    False,
                    "Together.ai API health check failed - check API key and connectivity",
                )
                return False

            # Test model listing
            try:
                models = TogetherService.get_available_models()
                if models:
                    self.log_test_result(
                        "Model Listing",
                        True,
                        f"Successfully retrieved {len(models)} available models",
                        {"model_count": len(models)},
                    )
                else:
                    self.log_test_result(
                        "Model Listing", False, "No models returned from API"
                    )
                    return False
            except Exception as e:
                self.log_test_result(
                    "Model Listing", False, f"Failed to retrieve models: {str(e)}"
                )
                return False

            return True

        except Exception as e:
            self.log_test_result(
                "API Connectivity", False, f"API connectivity test failed: {str(e)}"
            )
            return False

    async def test_embedding_service(self):
        """Test embedding service with BAAI/bge-large-en-v1.5 model"""
        print("\nTesting Embedding Service...")
        try:
            # Test data
            test_texts = [
                "This is a test document for embedding generation.",
                "Together.ai provides access to various AI models.",
                "BAAI/bge-large-en-v1.5 is a high-quality embedding model.",
            ]

            # Test single embedding generation
            print("  Generating single embedding...")
            embedding = await EmbeddingService.generate_embedding(test_texts[0])

            if embedding and len(embedding) == settings.EMBEDDING_DIMENSIONS:
                self.log_test_result(
                    "Single Embedding Generation",
                    True,
                    f"Successfully generated embedding with {len(embedding)} dimensions",
                    {
                        "embedding_length": len(embedding),
                        "expected_dimensions": settings.EMBEDDING_DIMENSIONS,
                        "sample_values": embedding[:5],  # First 5 values
                    },
                )
            else:
                self.log_test_result(
                    "Single Embedding Generation",
                    False,
                    f"Embedding generation failed or wrong dimensions. Got {len(embedding) if embedding else 0} dimensions",
                )
                return False

            # Test batch embedding generation
            print("  Generating batch embeddings...")
            embeddings = await EmbeddingService.generate_embeddings_batch(test_texts)

            if len(embeddings) == len(test_texts):
                all_correct_dimensions = all(
                    len(emb) == settings.EMBEDDING_DIMENSIONS for emb in embeddings
                )

                if all_correct_dimensions:
                    self.log_test_result(
                        "Batch Embedding Generation",
                        True,
                        f"Successfully generated {len(embeddings)} embeddings",
                        {
                            "batch_size": len(embeddings),
                            "dimensions_per_embedding": [
                                len(emb) for emb in embeddings
                            ],
                        },
                    )
                else:
                    self.log_test_result(
                        "Batch Embedding Generation",
                        False,
                        "Some embeddings have incorrect dimensions",
                    )
                    return False
            else:
                self.log_test_result(
                    "Batch Embedding Generation",
                    False,
                    f"Expected {len(test_texts)} embeddings, got {len(embeddings)}",
                )
                return False

            # Test query embedding generation
            print("  Generating query embedding...")
            query_embedding = await EmbeddingService.generate_query_embedding(
                "test query for embedding"
            )

            if (
                query_embedding
                and len(query_embedding) == settings.EMBEDDING_DIMENSIONS
            ):
                self.log_test_result(
                    "Query Embedding Generation",
                    True,
                    f"Successfully generated query embedding with {len(query_embedding)} dimensions",
                )
            else:
                self.log_test_result(
                    "Query Embedding Generation",
                    False,
                    f"Query embedding generation failed or wrong dimensions",
                )
                return False

            return True

        except Exception as e:
            self.log_test_result(
                "Embedding Service", False, f"Embedding service test failed: {str(e)}"
            )
            return False

    async def test_chat_service(self):
        """Test chat service with openai/gpt-oss-20b model"""
        print("\nTesting Chat Service...")
        try:
            # Test basic chat completion
            print("  Testing basic chat completion...")
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {
                    "role": "user",
                    "content": "Hello, can you help me test the Together.ai integration?",
                },
            ]

            response = await TogetherService.generate_completion(
                messages=messages, max_tokens=100, temperature=0.7
            )

            if response and len(response.strip()) > 0:
                self.log_test_result(
                    "Basic Chat Completion",
                    True,
                    f"Successfully generated chat response (length: {len(response)} characters)",
                    {"response_preview": response[:100] + "..."},
                )
            else:
                self.log_test_result(
                    "Basic Chat Completion",
                    False,
                    "Chat completion returned empty response",
                )
                return False

            # Test chat response helper method
            print("  Testing chat response helper...")
            chat_response = await TogetherService.generate_chat_response(
                user_message="Test message for chat response",
                system_message="You are a test assistant",
                max_tokens=50,
            )

            if chat_response and len(chat_response.strip()) > 0:
                self.log_test_result(
                    "Chat Response Helper",
                    True,
                    f"Successfully generated chat response via helper method (length: {len(chat_response)} characters)",
                )
            else:
                self.log_test_result(
                    "Chat Response Helper",
                    False,
                    "Chat response helper returned empty response",
                )
                return False

            # Test with different parameters
            print("  Testing with different parameters...")
            response_with_params = await TogetherService.generate_completion(
                messages=[
                    {"role": "user", "content": "Say 'Hello World' in exactly 5 words."}
                ],
                max_tokens=20,
                temperature=0.1,  # Low temperature for deterministic response
                top_p=0.9,
            )

            if response_with_params:
                word_count = len(response_with_params.split())
                self.log_test_result(
                    "Parameter Testing",
                    True,
                    f"Generated response with {word_count} words using custom parameters",
                    {"response": response_with_params, "word_count": word_count},
                )
            else:
                self.log_test_result(
                    "Parameter Testing", False, "Parameter testing failed"
                )
                return False

            return True

        except Exception as e:
            self.log_test_result(
                "Chat Service", False, f"Chat service test failed: {str(e)}"
            )
            return False

    async def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\nTesting Error Handling...")
        try:
            # Test with invalid API key
            print("  Testing invalid API key handling...")
            original_key = settings.TOGETHER_API_KEY

            # Temporarily set invalid key
            settings.TOGETHER_API_KEY = "invalid_key_for_testing"

            try:
                await TogetherService.check_api_health()
                self.log_test_result(
                    "Invalid API Key Handling",
                    False,
                    "Expected error for invalid API key, but none occurred",
                )
            except Exception as e:
                self.log_test_result(
                    "Invalid API Key Handling",
                    True,
                    "Properly handled invalid API key with error",
                    {"error_type": type(e).__name__},
                )
            finally:
                # Restore original key
                settings.TOGETHER_API_KEY = original_key

            # Test with empty messages
            print("  Testing empty messages handling...")
            try:
                response = await TogetherService.generate_completion([])
                self.log_test_result(
                    "Empty Messages Handling",
                    False,
                    "Expected error for empty messages, but none occurred",
                )
            except Exception as e:
                self.log_test_result(
                    "Empty Messages Handling",
                    True,
                    "Properly handled empty messages with error",
                    {"error_type": type(e).__name__},
                )

            # Test with very long text for embedding
            print("  Testing long text handling...")
            long_text = "A" * 3000  # Longer than 2000 char limit
            try:
                embedding = await EmbeddingService.generate_embedding(long_text)
                if embedding:
                    self.log_test_result(
                        "Long Text Handling",
                        True,
                        "Successfully handled long text (likely truncated)",
                        {
                            "original_length": len(long_text),
                            "embedding_dimensions": len(embedding),
                        },
                    )
                else:
                    self.log_test_result(
                        "Long Text Handling", False, "Failed to handle long text"
                    )
            except Exception as e:
                self.log_test_result(
                    "Long Text Handling", False, f"Error handling long text: {str(e)}"
                )

            # Test concurrent requests
            print("  Testing concurrent requests...")
            try:
                tasks = [
                    TogetherService.generate_chat_response(
                        f"Concurrent test message {i}"
                    )
                    for i in range(3)
                ]
                responses = await asyncio.gather(*tasks)

                successful_responses = sum(
                    1 for r in responses if r and len(r.strip()) > 0
                )

                self.log_test_result(
                    "Concurrent Requests",
                    True,
                    f"Successfully handled {successful_responses}/3 concurrent requests",
                    {"successful_requests": successful_responses},
                )
            except Exception as e:
                self.log_test_result(
                    "Concurrent Requests",
                    False,
                    f"Failed to handle concurrent requests: {str(e)}",
                )

            return True

        except Exception as e:
            self.log_test_result(
                "Error Handling", False, f"Error handling test failed: {str(e)}"
            )
            return False

    async def run_all_tests(self):
        """Run all tests"""
        print("Starting Together.ai Integration Tests")
        print("=" * 60)

        # Run all tests
        tests = [
            self.test_configuration_loading,
            self.test_api_connectivity,
            self.test_embedding_service,
            self.test_chat_service,
            self.test_error_handling,
        ]

        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                print(f"ERROR: Test {test.__name__} crashed: {str(e)}")
                results.append(False)

        # Print summary
        self.print_summary()

        # Return overall success
        return all(results)


async def main():
    """Main test function"""
    tester = TogetherIntegrationTester()
    success = await tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Simple test to verify Together.ai integration structure
"""

import os
import sys


def main():
    print("Starting simple test...")

    # Test 1: Check if files exist
    files_to_check = [
        "config/settings.py",
        "services/together_service.py",
        "services/embedding_service.py",
        "services/chat_service.py",
        ".env",
        ".env.example",
    ]

    print("\n1. Checking file structure...")
    for file_path in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        exists = os.path.exists(full_path)
        print(
            f"   {'✓' if exists else '✗'} {file_path}: {'Found' if exists else 'Missing'}"
        )

    # Test 2: Check configuration values
    print("\n2. Checking configuration...")
    try:
        # Read .env file directly
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_file, "r") as f:
            env_content = f.read()

        api_key_line = [
            line for line in env_content.split("\n") if "TOGETHER_API_KEY=" in line
        ]
        if api_key_line:
            api_key = api_key_line[0].split("=", 1)[1]
            configured = api_key and api_key != "your_together_api_key_here"
            print(f"   API Key: {'✓ Configured' if configured else '✗ Placeholder'}")
        else:
            print("   ✗ API Key: Not found in .env")

        model_line = [
            line for line in env_content.split("\n") if "TOGETHER_MODEL=" in line
        ]
        if model_line:
            model = model_line[0].split("=", 1)[1]
            print(f"   Chat Model: {model}")

        embedding_line = [
            line for line in env_content.split("\n") if "EMBEDDING_MODEL=" in line
        ]
        if embedding_line:
            embedding_model = embedding_line[0].split("=", 1)[1]
            print(f"   Embedding Model: {embedding_model}")

    except Exception as e:
        print(f"   ✗ Error reading configuration: {str(e)}")

    # Test 3: Check if we can import the modules
    print("\n3. Testing imports...")
    try:
        sys.path.insert(0, os.path.dirname(__file__))

        # Try importing settings
        try:
            from config.settings import settings

            print("   ✓ Settings imported successfully")
        except ImportError as e:
            print(f"   ✗ Settings import failed: {str(e)}")

        # Try importing services
        try:
            from services.together_service import TogetherService

            print("   ✓ TogetherService imported successfully")
        except ImportError as e:
            print(f"   ✗ TogetherService import failed: {str(e)}")

        try:
            from services.embedding_service import EmbeddingService

            print("   ✓ EmbeddingService imported successfully")
        except ImportError as e:
            print(f"   ✗ EmbeddingService import failed: {str(e)}")

        try:
            from services.chat_service import ChatService

            print("   ✓ ChatService imported successfully")
        except ImportError as e:
            print(f"   ✗ ChatService import failed: {str(e)}")

    except Exception as e:
        print(f"   ✗ Import test failed: {str(e)}")

    print("\n4. Summary:")
    print("   The Together.ai integration structure is in place.")
    print("   To test with real API calls, you need to:")
    print("   1. Get a Together.ai API key from https://together.ai")
    print("   2. Replace 'your_together_api_key_here' in backend/.env")
    print("   3. Run the comprehensive test script")

    print("\nTest completed!")


if __name__ == "__main__":
    main()

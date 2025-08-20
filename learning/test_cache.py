#!/usr/bin/env python3
"""
Test script to verify PDF text extraction caching functionality
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000/api/pdf"

def test_cache_functionality():
    print("🧪 Testing PDF Text Extraction Caching")
    print("=" * 50)
    
    # Test 1: Check initial cache state
    print("\n1. Checking initial cache state...")
    response = requests.get(f"{BASE_URL}/cache/info")
    if response.status_code == 200:
        cache_info = response.json()
        print(f"   Cache directory: {cache_info['cache_directory']}")
        print(f"   Cached files: {cache_info['total_cached_files']}")
        print(f"   Cache size: {cache_info['total_cache_size_mb']} MB")
    else:
        print(f"   ❌ Failed to get cache info: {response.status_code}")
        return
    
    # Test 2: Select a PDF for the first time (should extract and cache)
    print("\n2. Selecting PDF for the first time (cache miss)...")
    pdf_filename = "Python_Basics.pdf"  # Using a smaller PDF for faster testing
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/select", json={"filename": pdf_filename})
    first_extraction_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ PDF selected successfully")
        print(f"   Filename: {result['filename']}")
        print(f"   Text length: {result['text_length']} characters")
        print(f"   Extraction time: {first_extraction_time:.3f} seconds")
    else:
        print(f"   ❌ Failed to select PDF: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    # Test 3: Check cache state after first extraction
    print("\n3. Checking cache state after first extraction...")
    response = requests.get(f"{BASE_URL}/cache/info")
    if response.status_code == 200:
        cache_info = response.json()
        print(f"   Cached files: {cache_info['total_cached_files']}")
        print(f"   Cache size: {cache_info['total_cache_size_mb']} MB")
    
    # Test 4: Select the same PDF again (should use cache)
    print("\n4. Selecting the same PDF again (cache hit)...")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/select", json={"filename": pdf_filename})
    second_extraction_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ PDF selected successfully")
        print(f"   Filename: {result['filename']}")
        print(f"   Text length: {result['text_length']} characters")
        print(f"   Extraction time: {second_extraction_time:.3f} seconds")
        
        # Calculate performance improvement
        if first_extraction_time > 0:
            improvement = ((first_extraction_time - second_extraction_time) / first_extraction_time) * 100
            print(f"   🚀 Performance improvement: {improvement:.1f}%")
            print(f"   ⚡ Speed up: {first_extraction_time / second_extraction_time:.1f}x faster")
    else:
        print(f"   ❌ Failed to select PDF: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 5: Test with a larger PDF
    print("\n5. Testing with a larger PDF...")
    large_pdf_filename = "Ikigai - The Japanese secret to a long and happy life.pdf"
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/select", json={"filename": large_pdf_filename})
    large_pdf_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Large PDF selected successfully")
        print(f"   Filename: {result['filename']}")
        print(f"   Text length: {result['text_length']} characters")
        print(f"   Extraction time: {large_pdf_time:.3f} seconds")
    else:
        print(f"   ❌ Failed to select large PDF: {response.status_code}")
    
    # Test 6: Select large PDF again (should use cache)
    print("\n6. Selecting large PDF again (cache hit)...")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/select", json={"filename": large_pdf_filename})
    large_pdf_cached_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Large PDF selected successfully from cache")
        print(f"   Extraction time: {large_pdf_cached_time:.3f} seconds")
        
        if large_pdf_time > 0:
            improvement = ((large_pdf_time - large_pdf_cached_time) / large_pdf_time) * 100
            print(f"   🚀 Performance improvement: {improvement:.1f}%")
            print(f"   ⚡ Speed up: {large_pdf_time / large_pdf_cached_time:.1f}x faster")
    
    # Test 7: Final cache state
    print("\n7. Final cache state...")
    response = requests.get(f"{BASE_URL}/cache/info")
    if response.status_code == 200:
        cache_info = response.json()
        print(f"   Cached files: {cache_info['total_cached_files']}")
        print(f"   Cache size: {cache_info['total_cache_size_mb']} MB")
    
    print("\n" + "=" * 50)
    print("✅ Cache testing completed!")

if __name__ == "__main__":
    try:
        test_cache_functionality()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the backend server.")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

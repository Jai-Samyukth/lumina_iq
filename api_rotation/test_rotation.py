#!/usr/bin/env python3
"""
Test script for API key rotation functionality.
This script tests the APIKeyRotator class to ensure it works correctly.
"""

import sys
import os
import logging

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from api_key_rotator import APIKeyRotator

def test_api_key_rotation():
    """Test the API key rotation functionality."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("API Key Rotation Test")
    print("=" * 60)
    
    # Create a test rotator
    rotator = APIKeyRotator()
    
    # Display initial stats
    stats = rotator.get_current_stats()
    print(f"\nInitial Stats:")
    print(f"  Total keys: {stats['total_keys']}")
    print(f"  Current index: {stats['current_index']}")
    print(f"  Has keys: {stats['has_keys']}")
    print(f"  Keys file: {stats['keys_file']}")
    print(f"  Index file: {stats['index_file']}")
    
    if not stats['has_keys']:
        print("\n❌ No API keys found! Please check your API_Keys.txt file.")
        return False
    
    print(f"\n🔄 Testing rotation with {stats['total_keys']} keys...")
    
    # Test rotation - get keys equal to total + 2 to test wraparound
    test_count = stats['total_keys'] + 2
    used_keys = []
    
    for i in range(test_count):
        key = rotator.get_next_key()
        if key:
            key_preview = rotator.get_key_preview(key)
            print(f"  Request {i+1}: {key_preview}")
            used_keys.append(key)
        else:
            print(f"  Request {i+1}: ❌ No key returned")
    
    # Verify rotation worked correctly
    print(f"\n📊 Rotation Analysis:")
    print(f"  Total requests: {test_count}")
    print(f"  Keys returned: {len(used_keys)}")
    
    # Check if we got the expected rotation pattern
    if len(used_keys) == test_count:
        # Check if keys repeat after total_keys
        if stats['total_keys'] > 1:
            first_key = used_keys[0]
            repeated_key = used_keys[stats['total_keys']]
            if first_key == repeated_key:
                print("  ✅ Rotation wraparound working correctly")
            else:
                print("  ❌ Rotation wraparound not working")
        
        # Check if all keys are being used
        unique_keys = set(used_keys[:stats['total_keys']])
        if len(unique_keys) == stats['total_keys']:
            print("  ✅ All keys are being rotated")
        else:
            print(f"  ❌ Only {len(unique_keys)} out of {stats['total_keys']} keys used")
    
    # Test stats after rotation
    final_stats = rotator.get_current_stats()
    print(f"\nFinal Stats:")
    print(f"  Current index: {final_stats['current_index']}")
    
    print(f"\n🧪 Testing reload functionality...")
    reload_success = rotator.reload_keys()
    print(f"  Reload successful: {reload_success}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    
    return True

def test_concurrent_access():
    """Test concurrent access to the rotator."""
    import threading
    import time
    
    print("\n🔀 Testing concurrent access...")
    
    rotator = APIKeyRotator()
    results = []
    
    def worker(worker_id, num_requests=5):
        """Worker function for concurrent testing."""
        for i in range(num_requests):
            key = rotator.get_next_key()
            if key:
                key_preview = rotator.get_key_preview(key)
                results.append(f"Worker-{worker_id}-{i+1}: {key_preview}")
            time.sleep(0.01)  # Small delay to simulate real usage
    
    # Create multiple threads
    threads = []
    num_workers = 3
    
    for worker_id in range(num_workers):
        thread = threading.Thread(target=worker, args=(worker_id,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(f"  Concurrent requests completed: {len(results)}")
    for result in sorted(results):
        print(f"    {result}")
    
    print("  ✅ Concurrent access test completed")

if __name__ == "__main__":
    try:
        success = test_api_key_rotation()
        if success:
            test_concurrent_access()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

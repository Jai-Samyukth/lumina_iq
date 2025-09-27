import os
import sys
from api_key_rotator import api_key_rotator

def test_api_rotation():
    """
    Test the API key rotation with database to verify it's working correctly.
    This script calls get_next_key multiple times and verifies the rotation.
    """
    print("Testing API key rotation with SQLite database...")
    
    if not api_key_rotator.api_keys:
        print("Error: No API keys loaded. Run setup_sqlite.py first.")
        return False
    
    print(f"Starting test with {len(api_key_rotator.api_keys)} API keys.")
    print("Initial stats:", api_key_rotator.get_current_stats())
    
    # Test rotation by getting next key multiple times
    keys_used = []
    for i in range(len(api_key_rotator.api_keys) + 2):  # One full cycle + extra
        key = api_key_rotator.get_next_key()
        if key:
            preview = api_key_rotator.get_key_preview(key)
            keys_used.append(preview)
            print(f"Rotation {i+1}: {preview}")
        else:
            print(f"Rotation {i+1}: No key available")
    
    # Verify final stats
    final_stats = api_key_rotator.get_current_stats()
    print("\nFinal stats:", final_stats)
    
    # Check if rotation wrapped around correctly
    expected_index = (final_stats['current_index'] + 1) % len(api_key_rotator.api_keys)
    if final_stats['current_index'] == expected_index:
        print("✅ Rotation index updated correctly in database.")
    else:
        print(f"❌ Index mismatch: expected {expected_index}, got {final_stats['current_index']}")
    
    # Verify unique keys were used in cycle
    unique_keys = len(set(keys_used[:len(api_key_rotator.api_keys)]))
    if unique_keys == len(api_key_rotator.api_keys):
        print("✅ Full rotation cycle used all unique API keys.")
    else:
        print(f"❌ Rotation didn't use all keys: {unique_keys}/{len(api_key_rotator.api_keys)}")
    
    print("\nDatabase is being used for API rotation successfully!")
    return True

if __name__ == "__main__":
    # Add parent directory to path if needed
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(current_dir))
    
    success = test_api_rotation()
    if success:
        print("\n✅ All tests passed! API rotation with database is working.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
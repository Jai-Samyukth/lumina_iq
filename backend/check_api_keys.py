"""Check API keys status"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_rotation.api_key_rotator import api_key_rotator
import sqlite3

# Get stats
stats = api_key_rotator.get_current_stats()
print(f"\n{'='*60}")
print("API KEY ROTATION STATUS")
print(f"{'='*60}")
print(f"Total Keys: {stats['total_keys']}")
print(f"Current Index: {stats['current_index']}")
print(f"Has Keys: {stats['has_keys']}")
print(f"Database: {stats['database_path']}")

# Check database directly
db_path = stats['database_path']
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM api_keys")
    count = cursor.fetchone()[0]
    print(f"\nKeys in database: {count}")
    
    # Show first few characters of each key (for verification)
    cursor.execute("SELECT id, api_key FROM api_keys ORDER BY id ASC")
    keys = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print("API KEYS (First 15 chars only)")
    print(f"{'='*60}")
    for key_id, key in keys:
        preview = key[:15] + "..." if len(key) > 15 else key
        print(f"Key {key_id}: {preview}")
    
    conn.close()
else:
    print(f"\nDatabase not found at: {db_path}")

print(f"\n{'='*60}")

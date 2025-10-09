"""Test API keys and check their quota status"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_rotation.api_key_rotator import api_key_rotator
import google.generativeai as genai
import sqlite3

# Suppress gRPC warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_TRACE'] = ''

def test_single_key(api_key: str, key_index: int):
    """Test a single API key"""
    try:
        genai.configure(api_key=api_key)
        
        # Try a simple embedding
        result = genai.embed_content(
            model="models/embedding-001",
            content="Test query to check quota",
            task_type="retrieval_query"
        )
        
        if result and 'embedding' in result:
            return "[OK] WORKING", None
        else:
            return "[FAIL] FAILED", "No embedding returned"
            
    except Exception as e:
        error_str = str(e).lower()
        
        if 'quota' in error_str or 'exhausted' in error_str or '429' in error_str:
            return "[QUOTA] EXHAUSTED", str(e)[:100]
        elif 'invalid' in error_str or 'api key' in error_str:
            return "[FAIL] INVALID KEY", str(e)[:100]
        elif 'permission' in error_str or 'disabled' in error_str:
            return "[FAIL] DISABLED", str(e)[:100]
        else:
            return "[ERROR]", str(e)[:100]

# Get all keys from database
db_path = api_key_rotator.get_current_stats()['database_path']
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT id, api_key FROM api_keys ORDER BY id ASC")
keys = cursor.fetchall()
conn.close()

print(f"\n{'='*70}")
print("TESTING API KEYS - QUOTA STATUS")
print(f"{'='*70}\n")

working_keys = 0
quota_exhausted = 0
failed_keys = 0

for key_id, api_key in keys:
    key_preview = api_key[:15] + "..." if len(api_key) > 15 else api_key
    print(f"Key {key_id:2d}: {key_preview:20s} ", end="", flush=True)
    
    status, error = test_single_key(api_key, key_id)
    
    print(f"{status}", end="")
    if error:
        print(f" - {error}", end="")
    print()
    
    if "WORKING" in status:
        working_keys += 1
    elif "QUOTA" in status:
        quota_exhausted += 1
    else:
        failed_keys += 1

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"Total Keys:          {len(keys)}")
print(f"Working Keys:        {working_keys} {'[OK]' if working_keys > 0 else '[FAIL]'}")
print(f"Quota Exhausted:     {quota_exhausted} {'[WARNING]' if quota_exhausted > 0 else ''}")
print(f"Failed/Invalid Keys: {failed_keys} {'[FAIL]' if failed_keys > 0 else ''}")
print(f"{'='*70}\n")

if working_keys == 0:
    print("[WARNING] No working keys available!")
    print("\nPossible solutions:")
    print("1. Wait for quota reset (resets at midnight PST)")
    print("2. Upgrade API keys to paid tier")
    print("3. Add more API keys")
    print("4. Use alternative embedding service (OpenAI, Cohere, etc.)")
elif quota_exhausted > 0:
    print(f"[WARNING] {quota_exhausted} keys have exhausted quota")
    print(f"[OK] {working_keys} keys still have quota available")

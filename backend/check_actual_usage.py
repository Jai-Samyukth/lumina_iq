"""Check actual document and chunk counts to understand quota usage"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.qdrant_service import qdrant_service
import sqlite3

print("\n" + "="*70)
print("ANALYZING ACTUAL USAGE")
print("="*70)

# Check document tracking database
tracking_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                           "backend", "document_tracking.db")

if os.path.exists(tracking_db):
    conn = sqlite3.connect(tracking_db)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]
    
    cursor.execute("SELECT user_id, filename, chunk_count, upload_date FROM documents ORDER BY upload_date DESC LIMIT 20")
    recent_docs = cursor.fetchall()
    
    print(f"\nTotal documents uploaded: {total_docs}")
    print(f"\nRecent uploads:")
    print("-" * 70)
    
    total_chunks = 0
    for user_id, filename, chunk_count, upload_date in recent_docs:
        print(f"{upload_date[:19]} | {filename[:40]:40s} | {chunk_count:5d} chunks")
        total_chunks += chunk_count
    
    print("-" * 70)
    print(f"Total chunks from recent uploads: {total_chunks:,}")
    
    # Get all chunks count
    cursor.execute("SELECT SUM(chunk_count) FROM documents")
    all_chunks = cursor.fetchone()[0] or 0
    print(f"Total chunks across ALL documents: {all_chunks:,}")
    
    conn.close()
else:
    print(f"\nDocument tracking DB not found at: {tracking_db}")

# Check Qdrant
try:
    collection_name = qdrant_service.collection_name
    client = qdrant_service.client
    
    collection_info = client.get_collection(collection_name)
    points_count = collection_info.points_count
    
    print(f"\n" + "="*70)
    print(f"Qdrant Collection: {collection_name}")
    print(f"Total vectors stored: {points_count:,}")
    print("="*70)
    
    # Estimate requests used
    print(f"\nQuota Analysis:")
    print(f"Each vector = 1 embedding request")
    print(f"Total embedding requests used: {points_count:,}")
    print(f"Keys needed (1000 req/key): {points_count / 1000:.1f}")
    
    if points_count > 14000:
        print(f"\n[WARNING] You used {points_count:,} requests!")
        print(f"This exceeds 14 keys × 1000 requests = 14,000 limit")
        print(f"Overflow: {points_count - 14000:,} requests beyond quota")
    
except Exception as e:
    print(f"\nError checking Qdrant: {e}")

print("\n" + "="*70)
print("POSSIBLE CAUSES")
print("="*70)
print("1. Multiple uploads (not just 1 book)")
print("2. Duplicate uploads (same book multiple times)")
print("3. Failed uploads that retried")
print("4. Development/testing with repeated uploads")
print("5. Very large books creating 1000+ chunks each")
print("="*70 + "\n")

from qdrant_client import QdrantClient

qdrant_client = QdrantClient(
    url="https://1f6b3bbc-d09e-40c2-b333-0a823825f876.europe-west3-0.gcp.cloud.qdrant.io:6333", 
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.O8xNwnZuHGOxo1dcIdcgKrRVZGryxKPYyGaCVyNXziQ",
)

collection_name = "learning_app_documents"

print(f"Deleting collection: {collection_name}")
try:
    qdrant_client.delete_collection(collection_name)
    print(f"[SUCCESS] Deleted collection: {collection_name}")
except Exception as e:
    print(f"[INFO] Collection may not exist: {e}")

print("\nCollection will be recreated automatically on next service use with proper indexes.")

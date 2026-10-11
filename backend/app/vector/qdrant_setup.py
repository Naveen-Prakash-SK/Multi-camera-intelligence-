from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from app.core.config import settings

def init_qdrant_collections():
    client = QdrantClient(url=settings.QDRANT_URL)
    
    # SigLIP 2 typical embedding dimension is 768 (or 1152 depending on model)
    # BGE-M3 typical embedding dimension is 1024
    
    collections = {
        "events_text": 1024, # BGE-M3
        "events_vision": 768, # SigLIP 2
        "identities_person": 512, # OSNet
        "identities_vehicle": 512 # Vehicle Re-ID
    }
    
    for collection_name, dim in collections.items():
        if not client.collection_exists(collection_name):
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )
            print(f"Created Qdrant collection: {collection_name}")
        else:
            print(f"Qdrant collection {collection_name} already exists.")

if __name__ == "__main__":
    init_qdrant_collections()

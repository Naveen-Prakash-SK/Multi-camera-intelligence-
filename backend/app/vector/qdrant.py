from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.config import settings
import uuid

# Global client
qdrant_client = QdrantClient(url=settings.QDRANT_URL)

COLLECTION_NAME = "video_frames"
VECTOR_SIZE = 1536 # Default for many text embedding models (e.g., openai text-embedding-ada-002 or Qwen equivalents if configurable)

def init_qdrant():
    collections = qdrant_client.get_collections().collections
    if not any(c.name == COLLECTION_NAME for c in collections):
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

def index_frame(frame_id: uuid.UUID, video_id: uuid.UUID, camera_id: uuid.UUID, timestamp_s: float, embedding: list[float], attributes: dict = None):
    payload = {
        "frame_id": str(frame_id),
        "video_id": str(video_id),
        "camera_id": str(camera_id),
        "timestamp_s": timestamp_s,
    }
    if attributes:
        payload.update(attributes)
        
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(frame_id),
                vector=embedding,
                payload=payload
            )
        ]
    )

def search_frames(query_embedding: list[float], limit: int = 10, camera_id: str = None, time_range: tuple = None):
    # Optional filtering
    from qdrant_client.http import models as rest
    must_conditions = []
    
    if camera_id:
        must_conditions.append(
            rest.FieldCondition(
                key="camera_id",
                match=rest.MatchValue(value=str(camera_id))
            )
        )
        
    if time_range:
        must_conditions.append(
            rest.FieldCondition(
                key="timestamp_s",
                range=rest.Range(
                    gte=time_range[0],
                    lte=time_range[1]
                )
            )
        )
        
    query_filter = rest.Filter(must=must_conditions) if must_conditions else None
    
    response = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=query_filter,
        limit=limit
    )
    return response.points

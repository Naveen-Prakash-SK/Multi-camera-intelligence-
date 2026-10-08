from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.config import settings
import uuid

# Global client
qdrant_client = QdrantClient(url=settings.QDRANT_URL)

COLLECTION_NAME = "video_frames"
VECTOR_SIZE = 512 # CLIP models usually output 512 dimensions

def init_qdrant(vector_size: int = VECTOR_SIZE):
    collections = qdrant_client.get_collections().collections
    if not any(c.name == COLLECTION_NAME for c in collections):
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        
        # Create payload indexes for faster filtering
        from qdrant_client.http import models as rest
        qdrant_client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="camera_id",
            field_schema=rest.PayloadSchemaType.KEYWORD
        )
        qdrant_client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="timestamp_s",
            field_schema=rest.PayloadSchemaType.FLOAT
        )

def index_frame(
    vector_id: uuid.UUID,
    embedding: list[float],
    camera_id: uuid.UUID,
    video_id: uuid.UUID,
    frame_id: uuid.UUID,
    timestamp_s: float,
    detection_id: uuid.UUID = None,
    track_id: str = None,
    event_id: uuid.UUID = None,
    label: str = None,
    confidence: float = None,
    bounding_box: dict = None,
    attributes: dict = None
):
    payload = {
        "camera_id": str(camera_id),
        "video_id": str(video_id),
        "frame_id": str(frame_id),
        "timestamp_s": timestamp_s,
    }
    
    if detection_id: payload["detection_id"] = str(detection_id)
    if track_id: payload["track_id"] = track_id
    if event_id: payload["event_id"] = str(event_id)
    if label: payload["label"] = label
    if confidence is not None: payload["confidence"] = confidence
    if bounding_box: payload["bounding_box"] = bounding_box
    if attributes: payload["attributes"] = attributes
        
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(vector_id),
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

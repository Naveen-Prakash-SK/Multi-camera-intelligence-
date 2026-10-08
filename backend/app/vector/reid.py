import uuid
from typing import Optional

class CrossCameraIdentityService:
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
        self.similarity_threshold = 0.85

    def match_track_across_cameras(self, track_vector: list[float], timestamp_s: float, current_camera_id: str) -> str:
        """
        Takes an appearance embedding from one camera and searches Qdrant 
        for highly similar vectors in other cameras within a time window.
        Returns the global_track_id if matched, otherwise creates a new one.
        """
        from app.vector.qdrant import search_frames
        
        # Search for similar objects in the past hour, EXCLUDING the current camera
        # (Assuming search_frames can take an exclude_camera_id parameter in the future)
        results = search_frames(query_embedding=track_vector, limit=3)
        
        for hit in results:
            if hit.score >= self.similarity_threshold:
                if hit.payload.get("camera_id") != current_camera_id:
                    if "global_track_id" in hit.payload:
                        return hit.payload["global_track_id"]
        
        # No strong cross-camera match found. Generate a new Global Identity.
        return f"global_{uuid.uuid4()}"

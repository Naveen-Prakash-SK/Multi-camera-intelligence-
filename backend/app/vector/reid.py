import uuid
from typing import Optional
from app.vector.qdrant import search_frames

class CrossCameraIdentityService:
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
        self.base_threshold = 0.82
        self.time_penalty_factor = 0.02 # Decrease threshold required by time penalty

    def match_track_across_cameras(
        self, 
        track_vector: list[float], 
        timestamp_s: float, 
        current_camera_id: str,
        object_label: str = "person"
    ) -> str:
        """
        Takes an appearance embedding from one camera and searches Qdrant 
        for highly similar vectors in other cameras within a time window.
        Returns the global_track_id if matched, otherwise creates a new one.
        """
        
        # Search for similar objects
        results = search_frames(query_embedding=track_vector, limit=10)
        
        best_match_id = None
        highest_score = 0.0
        
        for hit in results:
            payload = hit.payload
            
            # 1. Enforce Object Class Match
            if payload.get("label", "person") != object_label:
                continue
                
            hit_cam = payload.get("camera_id")
            hit_time = payload.get("timestamp_s", 0.0)
            
            # 2. Time similarity (Penalty for huge time differences, max 1 hour)
            time_diff = abs(timestamp_s - hit_time)
            if time_diff > 3600: 
                continue
                
            # Decrease the score based on time difference (e.g. -0.01 per minute)
            time_penalty = (time_diff / 60.0) * self.time_penalty_factor
            adjusted_score = hit.score - time_penalty
            
            # 3. Dynamic Threshold check
            if adjusted_score >= self.base_threshold:
                # We can match within the same camera if it's been a while (re-entry)
                # But prefer cross-camera matches
                if hit_cam != current_camera_id or time_diff > 300: 
                    if "global_track_id" in payload:
                        if adjusted_score > highest_score:
                            highest_score = adjusted_score
                            best_match_id = payload["global_track_id"]
        
        if best_match_id:
            return best_match_id
            
        # No strong cross-camera match found. Generate a new Global Identity.
        return f"global_{uuid.uuid4()}"

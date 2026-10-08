from pydantic import BaseModel
from typing import List, Optional

class CameraIn(BaseModel):
    camera_id: str
    camera_name: str
    location: str

class CameraOut(CameraIn):
    status: str = "Online"

class EventOut(BaseModel):
    id: str
    camera_id: str
    camera_name: str
    timestamp: str
    frame_number: Optional[int] = None
    description: str
    frame_url: str
    clip_url: Optional[str] = None
    video_path: Optional[str] = None

class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    camera_id: str
    camera_name: str
    timestamp: str
    frame_number: Optional[int] = None
    description: str
    score: float
    verified: bool = True
    frame_url: str
    clip_url: Optional[str] = None
    video_path: Optional[str] = None
    verification_details: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    answer: str
    results: List[SearchResult]

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.deps import get_db
from app.models.core import GlobalTrack, Camera
import uuid
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class TimelineEntry(BaseModel):
    camera_id: str
    camera_name: str
    first_seen: datetime
    last_seen: datetime
    confidence: float

class TimelineResponse(BaseModel):
    global_identity_id: str
    timeline: List[TimelineEntry]
    insufficient_evidence: bool = False

@router.get("/api/timeline/{global_identity_id}", response_model=TimelineResponse)
async def get_cross_camera_timeline(global_identity_id: str, db: AsyncSession = Depends(get_db)):
    """
    Constructs a chronological timeline of where an identity was seen across the camera network.
    """
    # Fetch all global track segments for this identity, ordered by time
    result = await db.execute(
        select(GlobalTrack).where(GlobalTrack.local_track_id == global_identity_id).order_by(GlobalTrack.first_seen)
    )
    tracks = result.scalars().all()
    
    if not tracks:
        # Check if the global identity exists or if we lack evidence
        return TimelineResponse(
            global_identity_id=global_identity_id,
            timeline=[],
            insufficient_evidence=True
        )
        
    timeline = []
    for track in tracks:
        cam_res = await db.execute(select(Camera).where(Camera.id == track.camera_id))
        camera = cam_res.scalars().first()
        camera_name = camera.name if camera else "Unknown Camera"
        
        timeline.append(TimelineEntry(
            camera_id=str(track.camera_id),
            camera_name=camera_name,
            first_seen=track.first_seen,
            last_seen=track.last_seen,
            confidence=track.confidence
        ))
        
    return TimelineResponse(
        global_identity_id=global_identity_id,
        timeline=timeline,
        insufficient_evidence=False
    )

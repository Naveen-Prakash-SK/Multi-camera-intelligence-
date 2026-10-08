from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.deps import get_db
from app.models.core import Evidence, VideoFile
import uuid
import os
import subprocess
from app.core.config import settings

router = APIRouter()

@router.get("/api/evidence/{id}/thumbnail")
async def get_evidence_thumbnail(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evidence).where(Evidence.id == uuid.UUID(id)))
    evidence = result.scalars().first()
    if not evidence or not evidence.frame_path:
        raise HTTPException(status_code=404, detail="Evidence frame not found")
        
    if not os.path.exists(evidence.frame_path):
        raise HTTPException(status_code=404, detail="Evidence frame file is missing on disk")
        
    return FileResponse(evidence.frame_path, media_type="image/jpeg")

@router.get("/api/evidence/{id}/clip")
async def get_evidence_clip(id: str, type: str = "raw", db: AsyncSession = Depends(get_db)):
    # Extract a 10s clip around the event using ffmpeg stream copy
    result = await db.execute(select(Evidence).where(Evidence.id == uuid.UUID(id)))
    evidence = result.scalars().first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
        
    # Get the parent video
    video_res = await db.execute(select(VideoFile).where(VideoFile.id == evidence.video_id))
    video = video_res.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="Source video not found")
        
    source_path = video.file_path
    if type == "processed":
        annotated_path = os.path.join(settings.STORAGE_PATH, f"annotated_{video.id}.mp4")
        if os.path.exists(annotated_path):
            source_path = annotated_path
            
    if not os.path.exists(source_path):
        raise HTTPException(status_code=404, detail="Video file missing on disk")
        
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    clip_filename = os.path.join(settings.STORAGE_PATH, f"clip_{type}_{id}.mp4")
    if os.path.exists(clip_filename):
        return FileResponse(clip_filename, media_type="video/mp4")
        
    start_time = max(0, evidence.timestamp_s - 5.0)
    
    # Use ffmpeg to extract clip without re-encoding
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-i", source_path,
        "-t", "10",
        "-c", "copy",
        clip_filename
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to extract clip")
        
    return FileResponse(clip_filename, media_type="video/mp4")

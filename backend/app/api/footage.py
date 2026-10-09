from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import List, Optional
from pydantic import UUID4
import uuid
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.deps import get_db
from app.models.core import Job, VideoFile
from app.workers.tasks import process_video_pipeline
from app.core.config import settings
from datetime import datetime, timezone

router = APIRouter()

@router.post("/api/footage")
async def upload_footage(
    file: UploadFile = File(...),
    camera_id: str = Form(...),
    capture_start_utc: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith(('.mp4', '.mkv', '.avi')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
        
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    
    # Store with unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(settings.STORAGE_PATH, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    # Parse UTC string
    dt_capture = datetime.fromisoformat(capture_start_utc.replace("Z", "+00:00"))
        
    # Create VideoFile record
    video = VideoFile(
        camera_id=uuid.UUID(camera_id),
        capture_start_utc=dt_capture,
        provenance="uploaded_footage",
        file_path=file_path
    )
    db.add(video)
    await db.flush() # flush to get video.id
        
    job_id = uuid.uuid4()
    
    # Create Job record
    job = Job(
        id=job_id,
        job_type="video_processing",
        status="QUEUED",
        progress=0.0,
        metadata_payload={"video_id": str(video.id), "camera_id": camera_id}
    )
    db.add(job)
    await db.commit()
    
    # Enqueue processing
    task = process_video_pipeline.delay(str(job_id), str(video.id), file_path, camera_id, capture_start_utc)
    
    return {
        "job_id": str(job_id),
        "task_id": task.id,
        "status": "QUEUED",
        "message": "Video uploaded and queued for processing"
    }

@router.get("/api/jobs/{id}")
async def get_job_status(id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "id": str(job.id),
        "status": job.status,
        "progress": job.progress,
        "error": job.error,
        "job_type": job.job_type,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at
    }

@router.get("/api/footage")
async def list_footage(camera_id: Optional[UUID4] = None, db: AsyncSession = Depends(get_db)):
    query = select(VideoFile)
    if camera_id:
        query = query.where(VideoFile.camera_id == camera_id)
    query = query.order_by(VideoFile.capture_start_utc.desc())
    result = await db.execute(query)
    videos = result.scalars().all()
    
    return [
        {
            "id": str(v.id),
            "camera_id": str(v.camera_id),
            "capture_start_utc": v.capture_start_utc,
            "provenance": v.provenance,
            "url": f"/storage/{os.path.basename(v.file_path)}",
            "duration_s": v.duration_s
        }
        for v in videos
    ]

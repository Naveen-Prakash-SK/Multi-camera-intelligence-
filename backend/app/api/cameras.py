from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from pydantic import BaseModel, UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.deps import get_db
from app.models.core import Camera, VideoFile, Job
import uuid
import asyncio
import os
from datetime import datetime, timezone

router = APIRouter()

class CameraCreate(BaseModel):
    name: str
    description: str | None = None
    source_type: str = "file"
    stream_url: str | None = None
    location: str | None = None
    clock_offset_ms: int = 0

class CameraResponse(CameraCreate):
    id: UUID4
    status: str

@router.post("/api/cameras", response_model=CameraResponse)
async def create_camera(camera: CameraCreate, db: AsyncSession = Depends(get_db)):
    new_camera = Camera(
        name=camera.name,
        description=camera.description,
        source_type=camera.source_type,
        stream_url=camera.stream_url,
        location=camera.location,
        clock_offset_ms=camera.clock_offset_ms,
        status="OFFLINE"
    )
    db.add(new_camera)
    await db.commit()
    await db.refresh(new_camera)
    return new_camera

@router.get("/api/cameras", response_model=List[CameraResponse])
async def list_cameras(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera))
    return result.scalars().all()

@router.get("/api/cameras/{id}", response_model=CameraResponse)
async def get_camera(id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.put("/api/cameras/{id}", response_model=CameraResponse)
async def update_camera(id: UUID4, camera_in: CameraCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    for var, value in vars(camera_in).items():
        setattr(camera, var, value)
        
    await db.commit()
    await db.refresh(camera)
    return camera

@router.delete("/api/cameras/{id}")
async def delete_camera(id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    await db.delete(camera)
    await db.commit()
    return {"status": "Deleted"}

@router.post("/api/cameras/{id}/start")
async def start_camera(id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    camera.status = "ONLINE"
    await db.commit()
    
    if camera.source_type == "live" and camera.stream_url:
        from app.workers.tasks import process_live_stream_task
        process_live_stream_task.delay(str(camera.id), camera.stream_url)
        
    return {"status": "ONLINE"}

@router.post("/api/cameras/{id}/stop")
async def stop_camera(id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
        
    camera.status = "STOPPING"
    await db.commit()
    
    # Send stop signal to worker
    r = redis.Redis.from_url(settings.REDIS_URL)
    r.set(f"camera:{camera.id}:stop", "1", ex=60)
    
    return {"status": "STOPPING"}

import redis
from app.core.config import settings

def mjpeg_generator(camera_id: str, stream_type: str):
    r = redis.Redis.from_url(settings.REDIS_URL)
    import time
    while True:
        frame_bytes = r.get(f"camera:{camera_id}:{stream_type}")
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.1)

@router.get("/api/cameras/{id}/stream/{stream_type}")
async def get_camera_stream(id: UUID4, stream_type: str):
    if stream_type not in ["raw", "processed"]:
        raise HTTPException(status_code=400, detail="Invalid stream type. Use 'raw' or 'processed'.")
    return StreamingResponse(mjpeg_generator(str(id), stream_type), media_type="multipart/x-mixed-replace; boundary=frame")

@router.post("/api/cameras/{id}/record")
async def record_camera(id: UUID4, duration: int = 5, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == id))
    camera = result.scalars().first()
    if not camera or not camera.stream_url:
        raise HTTPException(status_code=400, detail="Camera not found or missing stream_url")
    
    timestamp_utc = datetime.now(timezone.utc)
    file_id = str(uuid.uuid4())
    output_path = f"/app/storage/{file_id}.mp4"
    
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y", "-use_wallclock_as_timestamps", "1",
        "-i", camera.stream_url,
        "-t", str(duration),
        "-c:v", "libx264",
        output_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    if proc.returncode != 0 or not os.path.exists(output_path):
        raise HTTPException(status_code=500, detail=f"Failed to record stream: {stderr.decode()}")
        
    new_video = VideoFile(
        id=uuid.UUID(file_id),
        camera_id=camera.id,
        file_path=output_path,
        duration_s=duration,
        capture_start_utc=timestamp_utc
    )
    db.add(new_video)
    
    job_id = uuid.uuid4()
    new_job = Job(
        id=job_id,
        video_id=uuid.UUID(file_id),
        status="QUEUED",
        progress=0.0
    )
    db.add(new_job)
    await db.commit()
    
    from app.workers.tasks import process_video_pipeline
    process_video_pipeline.delay(
        job_id=str(job_id),
        video_id=file_id,
        file_path=output_path,
        camera_id=str(camera.id),
        capture_start_utc=timestamp_utc.isoformat()
    )
    
    return {"job_id": str(job_id), "status": "RECORDED_AND_PROCESSING"}

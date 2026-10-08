from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from pydantic import UUID4
import uuid
import os
from app.workers.tasks import process_video_pipeline
from app.core.config import settings

router = APIRouter()

@router.post("/api/footage")
async def upload_footage(
    file: UploadFile = File(...),
    camera_id: str = Form(...),
    capture_start_utc: str = Form(...)
):
    if not file.filename.endswith(('.mp4', '.mkv', '.avi')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
        
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    file_path = os.path.join(settings.STORAGE_PATH, file.filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    job_id = str(uuid.uuid4())
    
    # Enqueue processing
    task = process_video_pipeline.delay(job_id, file_path, camera_id, capture_start_utc)
    
    return {
        "job_id": job_id,
        "task_id": task.id,
        "status": "QUEUED",
        "message": "Video uploaded and queued for processing"
    }

@router.get("/api/jobs/{id}")
async def get_job_status(id: str):
    return {"id": id, "status": "MOCKED"}

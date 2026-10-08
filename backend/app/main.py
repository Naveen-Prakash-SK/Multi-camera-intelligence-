import os
import uuid
import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from app.models.schemas import SearchResponse, SearchResult, EventOut, CameraOut, CameraIn, SearchRequest
from app.services.video_processor import process_video_bg
from app.services.indexer import search_index, get_all_events
from app.models.database import init_db
from app.models.memory import get_mapping, set_mapping

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-camera-intelligence MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/api/cameras", response_model=List[CameraOut])
def get_cameras():
    from app.models.database import get_all_cameras
    return get_all_cameras()

@app.post("/api/cameras")
def add_camera(camera: CameraIn):
    from app.models.database import add_camera_to_db
    add_camera_to_db(camera)
    return {"status": "ok"}

@app.get("/api/events", response_model=List[EventOut])
def get_events():
    return get_all_events()

class ProcessRequest(BaseModel):
    camera_id: str
    video_path: str

@app.post("/api/process")
def process_video_endpoint(req: ProcessRequest, background_tasks: BackgroundTasks):
    if not os.path.exists(req.video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    background_tasks.add_task(process_video_bg, req.camera_id, req.video_path)
    return {"status": "processing_started"}

@app.post("/api/process-all")
def process_all_endpoint(background_tasks: BackgroundTasks):
    from pathlib import Path
    data_dir = Path("data")
    if not data_dir.exists():
        raise HTTPException(status_code=404, detail="Data directory not found")
        
    videos = list(data_dir.glob("*.mp4"))
    if not videos:
        return {"status": "no_videos_found"}
        
    for video_path in videos:
        # Expected naming: camera_01.mp4 -> camera_01
        camera_id = video_path.stem
        background_tasks.add_task(process_video_bg, camera_id, str(video_path))
        
    return {"status": "processing_started", "count": len(videos)}

@app.post("/api/search", response_model=SearchResponse)
def search_events(req: SearchRequest):
    # clarify-once memory resolution could happen here or in search_index
    results = search_index(req.query)
    
    if len(results) > 0:
        answer = "Yes, matching evidence was found."
    else:
        answer = "No matching evidence found."
        
    return SearchResponse(
        query=req.query,
        answer=answer,
        results=results
    )

@app.get("/api/evidence/frames/{frame_name}")
def get_frame(frame_name: str):
    path = os.path.join("storage", "frames", frame_name)
    if not os.path.exists(path):
        raise HTTPException(404, "Frame not found")
    return FileResponse(path)

@app.get("/api/evidence/clips/{clip_name}")
def get_clip(clip_name: str):
    path = os.path.join("storage", "clips", clip_name)
    if not os.path.exists(path):
        raise HTTPException(404, "Clip not found")
    return FileResponse(path)

@app.get("/api/memory")
def read_memory(key: str):
    val = get_mapping(key)
    if val:
        return {"key": key, "value": val}
    return {"key": key, "value": None}

class MemoryIn(BaseModel):
    key: str
    value: str

@app.post("/api/memory")
def write_memory(req: MemoryIn):
    set_mapping(req.key, req.value)
    return {"status": "ok"}

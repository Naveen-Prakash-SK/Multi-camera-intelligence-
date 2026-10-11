import os
import uuid
import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path

from app.models.schemas import SearchResponse, SearchResult, EventOut, CameraOut, CameraIn, SearchRequest
from app.services.video_processor import process_video_bg
from app.services.indexer import search_index, get_all_events, HAS_TRANSFORMERS
from app.models.database import init_db, FRAMES_DIR, CLIPS_DIR, BACKEND_DIR
from app.models.memory import get_mapping, set_mapping

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MultiCameraIntel")

app = FastAPI(title="Multi-camera-intelligence MVP", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    logger.info("Initializing SQLite database & storage directories...")
    init_db()
    
    # Startup Model Health Verification
    logger.info("=" * 50)
    logger.info("MULTI-CAMERA-INTELLIGENCE SYSTEM STARTUP")
    try:
        import torch
        logger.info(f"PyTorch available: TRUE (v{torch.__version__}, CUDA: {torch.cuda.is_available()})")
    except ImportError:
        logger.info("PyTorch available: FALSE")
        
    logger.info(f"CLIP available: {HAS_TRANSFORMERS}")
    logger.info(f"CLIP model loaded: {HAS_TRANSFORMERS}")
    logger.info(f"Frames storage path: {FRAMES_DIR}")
    logger.info("=" * 50)

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
    video_file = os.path.abspath(req.video_path)
    if not os.path.exists(video_file):
        # Also check inside data/
        alt_path = os.path.join(BACKEND_DIR, "data", os.path.basename(req.video_path))
        if os.path.exists(alt_path):
            video_file = alt_path
        else:
            raise HTTPException(status_code=404, detail=f"Video file not found at {req.video_path}")
    
    background_tasks.add_task(process_video_bg, req.camera_id, video_file)
    return {"status": "processing_started", "camera_id": req.camera_id}

@app.post("/api/process-all")
def process_all_endpoint(background_tasks: BackgroundTasks):
    data_dir = Path(BACKEND_DIR) / "data"
    if not data_dir.exists():
        raise HTTPException(status_code=404, detail="Data directory not found")
        
    videos = sorted(list(data_dir.glob("camera_*.mp4")))
    if not videos:
        return {"status": "no_videos_found"}
        
    for video_path in videos:
        # Standard naming: camera_01.mp4 -> camera_01
        camera_id = video_path.stem.split(" ")[0].split("(")[0].strip()
        background_tasks.add_task(process_video_bg, camera_id, str(video_path))
        
    return {"status": "processing_started", "count": len(videos)}

@app.post("/api/search", response_model=SearchResponse)
def search_events(req: SearchRequest):
    if not req.query or not req.query.strip():
        return SearchResponse(query="", answer="Please enter a valid search query.", results=[])
        
    results = search_index(req.query.strip())
    
    if len(results) > 0:
        answer = f"Yes, verified matching evidence was found ({len(results)} instances)."
    else:
        answer = "No verified match found."
        
    return SearchResponse(
        query=req.query,
        answer=answer,
        results=results
    )

@app.get("/api/evidence/frames/{frame_name}")
def get_frame(frame_name: str):
    path = os.path.join(FRAMES_DIR, frame_name)
    if not os.path.exists(path):
        raise HTTPException(404, f"Frame not found: {frame_name}")
    return FileResponse(path, media_type="image/jpeg")

@app.get("/api/evidence/clips/{clip_name}")
def get_clip(clip_name: str):
    path = os.path.join(CLIPS_DIR, clip_name)
    if not os.path.exists(path):
        raise HTTPException(404, f"Clip not found: {clip_name}")
    return FileResponse(path, media_type="video/mp4")

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


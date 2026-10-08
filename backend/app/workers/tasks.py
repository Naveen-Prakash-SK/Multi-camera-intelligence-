import uuid
import time
import os
import cv2
import numpy as np
from datetime import datetime, timezone, timedelta
from celery import shared_task
from app.workers.celery_app import celery_app
from app.api.deps import SyncSessionLocal
from app.models.core import Job, Frame, Detection, VideoFile, Evidence
from app.models.events import Event
from app.vector.qdrant import index_frame

def get_dummy_embedding(text: str) -> list[float]:
    # Placeholder since Ollama is blocked by user's corporate firewall
    return [0.1] * 1536

@celery_app.task(bind=True)
def process_video_pipeline(self, job_id: str, video_id: str, file_path: str, camera_id: str, capture_start_utc: str):
    """
    Core video processing pipeline.
    Steps:
    1. ffprobe/FFmpeg decode -> frame sampling (using OpenCV)
    2. detection -> tracking (Mocked for MVP)
    3. embeddings -> DB/Qdrant
    """
    with SyncSessionLocal() as db:
        # Update Job Status to RUNNING
        job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
        if job:
            job.status = "RUNNING"
            job.started_at = datetime.now(timezone.utc)
            db.commit()

        try:
            self.update_state(state='RUNNING', meta={'progress': 10, 'step': 'decode'})
            
            # Start OpenCV decoding
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                raise Exception(f"Failed to open video file: {file_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            base_time = datetime.fromisoformat(capture_start_utc.replace("Z", "+00:00"))
            
            # Sample 1 frame every second
            frame_interval = int(fps)
            frame_count = 0
            processed_count = 0
            events_generated = 0
            
            while True:
                ret, img = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    timestamp_s = frame_count / fps
                    frame_time = base_time + timedelta(seconds=timestamp_s)
                    
                    # Create Frame DB Record
                    frame_db = Frame(
                        video_id=uuid.UUID(video_id),
                        timestamp_s=timestamp_s,
                        frame_path=file_path # Mock for now
                    )
                    db.add(frame_db)
                    db.flush()
                    
                    # Generate Mock Detection
                    det = Detection(
                        frame_id=frame_db.id,
                        label="person",
                        confidence=0.9,
                        bbox={"x1": 100, "y1": 100, "x2": 200, "y2": 300},
                        attributes={"clothing_color": "red"}
                    )
                    db.add(det)
                    
                    # Generate Event
                    evt = Event(
                        camera_id=uuid.UUID(camera_id),
                        timestamp_start=frame_time,
                        event_type="person_detected",
                        object_type="person",
                        attributes={"clothing_color": "red"},
                        confidence=0.9,
                        pipeline_version="1.0"
                    )
                    db.add(evt)
                    db.flush()
                    
                    # Generate Evidence
                    evd = Evidence(
                        video_id=uuid.UUID(video_id),
                        camera_id=uuid.UUID(camera_id),
                        timestamp_s=timestamp_s,
                        frame_path=file_path, # Mock
                        event_id=evt.id
                    )
                    db.add(evd)
                    
                    # Qdrant vector index
                    emb = get_dummy_embedding(f"person with red clothing at {frame_time}")
                    index_frame(
                        frame_id=frame_db.id,
                        video_id=uuid.UUID(video_id),
                        camera_id=uuid.UUID(camera_id),
                        timestamp_s=timestamp_s,
                        embedding=emb,
                        attributes={"object_type": "person", "clothing_color": "red"}
                    )
                    
                    processed_count += 1
                    events_generated += 1
                    
                    if processed_count % 5 == 0:
                        progress = int(10 + (frame_count / total_frames) * 80)
                        self.update_state(state='RUNNING', meta={'progress': progress, 'step': 'processing'})
                        if job:
                            job.progress = progress
                            db.commit()

                frame_count += 1
                
            cap.release()
            
            if job:
                job.status = "COMPLETED"
                job.progress = 100.0
                job.completed_at = datetime.now(timezone.utc)
                db.commit()
            
            return {
                "job_id": job_id,
                "status": "COMPLETED",
                "frames_processed": processed_count,
                "events_generated": events_generated
            }
        except Exception as e:
            if job:
                job.status = "FAILED"
                job.error = str(e)
                db.commit()
            raise e


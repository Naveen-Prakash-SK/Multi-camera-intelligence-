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
from app.workers.tracking import Tracker
from app.workers.frame_source import RecordedVideoSource
from app.vector.qdrant import index_frame

# Lazy loaded services
detection_service = None
embedding_service = None

@celery_app.task(bind=True)
def process_video_pipeline(self, job_id: str, video_id: str, file_path: str, camera_id: str, capture_start_utc: str):
    """
    Core video processing pipeline.
    Steps:
    1. OpenCV decode -> frame sampling
    2. Real Open-Vocabulary Detection
    3. IoU Tracking
    4. CLIP Embeddings -> DB/Qdrant
    """
    global detection_service, embedding_service
    if detection_service is None:
        from app.vector.detection import DetectionService
        detection_service = DetectionService()
    if embedding_service is None:
        from app.vector.embeddings import EmbeddingService
        embedding_service = EmbeddingService()

    tracker = Tracker()
    open_vocab_prompts = ["person", "car", "truck", "bicycle", "motorcycle", "bus", "bag", "box"]
    with SyncSessionLocal() as db:
        # Update Job Status to RUNNING
        job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
        if job:
            job.status = "RUNNING"
            job.started_at = datetime.now(timezone.utc)
            db.commit()

        try:
            self.update_state(state='DECODING', meta={'progress': 5, 'step': 'init'})
            
            # Use new abstraction instead of direct OpenCV
            fps_sample_rate = float(os.getenv("FRAME_SAMPLE_FPS", "1.0"))
            video_source = RecordedVideoSource(file_path, fps_sample_rate=fps_sample_rate)
            
            base_time = datetime.fromisoformat(capture_start_utc.replace("Z", "+00:00"))
            
            processed_count = 0
            events_generated = 0
            
            for frame_count, timestamp_s, img in video_source.get_frames():
                self.update_state(state='PROCESSING', meta={'progress': 10, 'step': 'decode'})
                frame_time = base_time + timedelta(seconds=timestamp_s)
                    
                # 1. Save frame to disk
                frame_filename = f"/app/storage/{job_id}_{frame_count}.jpg"
                cv2.imwrite(frame_filename, img)
                
                # 2. DB Frame Record
                frame_db = Frame(
                    video_id=uuid.UUID(video_id),
                    timestamp_s=timestamp_s,
                    frame_path=frame_filename
                )
                db.add(frame_db)
                db.flush()
                
                # 3. Detection & Tracking
                self.update_state(state='DETECTING', meta={'progress': 20, 'step': 'detect'})
                raw_detections = detection_service.detect(frame_filename, open_vocab_prompts, threshold=0.1)
                
                self.update_state(state='TRACKING', meta={'progress': 40, 'step': 'track'})
                tracked_detections = tracker.update(raw_detections, camera_id, timestamp_s)
                
                # 4. Embeddings
                self.update_state(state='EMBEDDING', meta={'progress': 60, 'step': 'embed'})
                frame_embedding = embedding_service.encode_image(frame_filename)
                
                # 5. Index Full Frame
                self.update_state(state='INDEXING', meta={'progress': 80, 'step': 'index'})
                index_frame(
                    vector_id=uuid.uuid4(),
                    embedding=frame_embedding,
                    camera_id=uuid.UUID(camera_id),
                    video_id=uuid.UUID(video_id),
                    frame_id=frame_db.id,
                    timestamp_s=frame_time.timestamp(),
                    attributes={"type": "full_frame"}
                )
                
                # 6. Index Detections & Create Events
                for det in tracked_detections:
                    det_db = Detection(
                        frame_id=frame_db.id,
                        label=det['label'],
                        confidence=det['confidence'],
                        bbox=det['bbox']
                    )
                    db.add(det_db)
                    db.flush()
                    
                    evt = Event(
                        camera_id=uuid.UUID(camera_id),
                        timestamp_start=frame_time,
                        event_type=f"{det['label']}_detected",
                        object_type=det['label'],
                        confidence=det['confidence'],
                        pipeline_version="2.0"
                    )
                    db.add(evt)
                    db.flush()
                    
                    evd = Evidence(
                        video_id=uuid.UUID(video_id),
                        camera_id=uuid.UUID(camera_id),
                        timestamp_s=timestamp_s,
                        frame_path=frame_filename,
                        event_id=evt.id
                    )
                    db.add(evd)
                    
                    index_frame(
                        vector_id=uuid.uuid4(),
                        embedding=frame_embedding, # Using full frame embedding to save compute
                        camera_id=uuid.UUID(camera_id),
                        video_id=uuid.UUID(video_id),
                        frame_id=frame_db.id,
                        timestamp_s=frame_time.timestamp(),
                        detection_id=det_db.id,
                        track_id=det['track_id'],
                        event_id=evt.id,
                        label=det['label'],
                        confidence=det['confidence'],
                        bounding_box=det['bbox'],
                        attributes={"type": "object"}
                    )
                
                processed_count += 1
                events_generated += 1
                
                if processed_count % 5 == 0:
                    progress = min(99, 10 + processed_count) # simplified progress for stream
                    self.update_state(state='PROCESSING', meta={'progress': progress, 'step': 'processing'})
                    if job:
                        job.progress = progress
                        job.status = "PROCESSING"
                        db.commit()

            video_source.close()
            
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


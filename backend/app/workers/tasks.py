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
from app.core.config import settings

# Lazy loaded services
advanced_pipeline = None

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
    global advanced_pipeline
    if advanced_pipeline is None:
        from app.vector.advanced_pipeline import AdvancedPipeline
        advanced_pipeline = AdvancedPipeline()
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
            alerted_tracks = {}
            
            # Setup VideoWriter for annotated output
            import cv2
            tmp_cap = cv2.VideoCapture(file_path)
            width = int(tmp_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(tmp_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            orig_fps = tmp_cap.get(cv2.CAP_PROP_FPS) or 25.0
            tmp_cap.release()
            
            import os
            from app.core.config import settings
            annotated_filename = f"annotated_{video_id}.mp4"
            annotated_path = os.path.join(settings.STORAGE_PATH, annotated_filename)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_writer = cv2.VideoWriter(annotated_path, fourcc, orig_fps, (width, height))
            
            for frame_count, timestamp_s, img in video_source.get_frames():
                self.update_state(state='PROCESSING', meta={'progress': 10, 'step': 'decode'})
                frame_time = base_time + timedelta(seconds=timestamp_s)
                    
                # 3 & 4. Advanced Pipeline (YOLO + ByteTrack + SigLIP + ReID + Face Blur)
                self.update_state(state='PROCESSING', meta={'progress': 40, 'step': 'advanced_vision'})
                pipeline_results = advanced_pipeline.process_frame(img, timestamp_s, camera_id)
                
                # 1. Save processed frame to disk (now it includes blur and bbox!)
                os.makedirs(settings.STORAGE_PATH, exist_ok=True)
                frame_filename = os.path.join(settings.STORAGE_PATH, f"{job_id}_{frame_count}.jpg")
                cv2.imwrite(frame_filename, pipeline_results["frame_bgr"])
                
                # Write to annotated MP4
                if out_writer:
                    out_writer.write(pipeline_results["frame_bgr"])
                
                # 2. DB Frame Record
                frame_db = Frame(
                    video_id=uuid.UUID(video_id),
                    timestamp_s=timestamp_s,
                    frame_path=frame_filename
                )
                db.add(frame_db)
                db.flush()
                
                frame_embedding = pipeline_results["siglip_embedding"]
                tracked_detections = pipeline_results["detections"]
                
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
                        bbox=det['box']
                    )
                    db.add(det_db)
                    db.flush()
                    
                    track_id = det['track_id']
                    
                    # Deduplicate events: only 1 event per track per 60 seconds
                    last_alert = alerted_tracks.get(track_id, 0)
                    evt_id = None
                    if timestamp_s - last_alert > 60:
                        alerted_tracks[track_id] = timestamp_s
                        
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
                        evt_id = evt.id
                        
                        evd = Evidence(
                            video_id=uuid.UUID(video_id),
                            camera_id=uuid.UUID(camera_id),
                            timestamp_s=timestamp_s,
                            frame_path=frame_filename,
                            event_id=evt.id
                        )
                        db.add(evd)
                    
                    det_embedding = det.get("reid_embedding") or frame_embedding
                    
                    index_frame(
                        vector_id=uuid.uuid4(),
                        embedding=det_embedding,
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
                
                # Write the annotated frame to our output processed video file
                out_writer.write(pipeline_results["frame_bgr"])
                
                processed_count += 1
                events_generated += 1
                
                if processed_count % 5 == 0:
                    progress = min(99, 10 + processed_count) # simplified progress for stream
                    self.update_state(state='PROCESSING', meta={'progress': progress, 'step': 'processing'})
                    if job:
                        job.progress = progress
                        job.status = "PROCESSING"
                        db.commit()

            video_source.release()
            out_writer.release()
            
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

import redis
redis_client = None

@celery_app.task(bind=True)
def process_live_stream_task(self, camera_id: str, stream_url: str):
    """
    Long-running task to process a live stream.
    Publishes raw and processed JPEG frames to Redis for MJPEG streaming endpoints.
    """
    global advanced_pipeline, redis_client
    if advanced_pipeline is None:
        from app.vector.advanced_pipeline import AdvancedPipeline
        advanced_pipeline = AdvancedPipeline()
    if redis_client is None:
        redis_client = redis.Redis.from_url(settings.REDIS_URL)

    import time
    from sqlalchemy.future import select
    from app.models.core import Camera
    
    stop_key = f"camera:{camera_id}:stop"
    redis_client.delete(stop_key) # clear any previous stop signals
    
    # 1. Update DB to RUNNING
    with SyncSessionLocal() as db:
        camera = db.query(Camera).filter(Camera.id == uuid.UUID(camera_id)).first()
        if camera:
            camera.status = "RUNNING"
            db.commit()

    print(f"Started live processing for camera {camera_id} from {stream_url}")
    
    reconnect_attempts = 0
    max_reconnect_attempts = 10
    
    while reconnect_attempts < max_reconnect_attempts:
        if redis_client.get(stop_key):
            print(f"Stop signal received for camera {camera_id}")
            break
            
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            print(f"Failed to open live stream: {stream_url}. Retrying...")
            reconnect_attempts += 1
            
            with SyncSessionLocal() as db:
                camera = db.query(Camera).filter(Camera.id == uuid.UUID(camera_id)).first()
                if camera:
                    camera.status = "RECONNECTING"
                    db.commit()
            
            time.sleep(5)
            continue
            
        # Successfully connected
        reconnect_attempts = 0
        with SyncSessionLocal() as db:
            camera = db.query(Camera).filter(Camera.id == uuid.UUID(camera_id)).first()
            if camera and camera.status != "RUNNING":
                camera.status = "RUNNING"
                db.commit()
        
        while cap.isOpened():
            if redis_client.get(stop_key):
                break
                
            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                print("Stream ended or disconnected.")
                break
                
            # Encode RAW frame to JPEG for Redis
            _, raw_jpeg = cv2.imencode('.jpg', frame)
            redis_client.set(f"camera:{camera_id}:raw", raw_jpeg.tobytes(), ex=10) # 10s TTL
            
            # Process frame
            timestamp_s = time.time()
            pipeline_results = advanced_pipeline.process_frame(frame, timestamp_s, camera_id)
            
            processed_frame = pipeline_results["frame_bgr"]
            
            # Encode PROCESSED frame to JPEG for Redis
            _, proc_jpeg = cv2.imencode('.jpg', processed_frame)
            redis_client.set(f"camera:{camera_id}:processed", proc_jpeg.tobytes(), ex=10)
            
            # Rate limit processing to ~5 fps (0.2s per frame)
            elapsed = time.time() - start_time
            if elapsed < 0.2:
                time.sleep(0.2 - elapsed)
                
        cap.release()
        
        if redis_client.get(stop_key):
            break
            
        # If we broke out of the inner loop without a stop signal, it means disconnect
        time.sleep(2)
        reconnect_attempts += 1

    # Cleanup and exit
    with SyncSessionLocal() as db:
        camera = db.query(Camera).filter(Camera.id == uuid.UUID(camera_id)).first()
        if camera:
            camera.status = "STOPPED" if redis_client.get(stop_key) else "ERROR"
            db.commit()
            
    return True


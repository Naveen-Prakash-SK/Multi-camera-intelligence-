import cv2
import os
import time
from .indexer import save_event, HAS_TRANSFORMERS
from PIL import Image

try:
    if HAS_TRANSFORMERS:
        from .indexer import model, processor, device
        import torch
except ImportError:
    pass

def process_video_bg(camera_id: str, video_path: str, interval_seconds: int = 2):
    """
    Extracts frames every N seconds, classifies them or gets embeddings, and saves events.
    """
    if not os.path.exists(video_path):
        print(f"Video path {video_path} does not exist.")
        return
        
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 25 # Fallback
        
    frame_interval = int(fps * interval_seconds)
    
    frame_count = 0
    saved_count = 0
    
    # Common MVP categories to generate a textual description
    categories = [
        "a red car",
        "a person carrying a bag",
        "a bicycle",
        "a vehicle",
        "a person entering",
        "empty scene",
        "a white car",
        "a truck"
    ]
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            # Calculate timestamp
            seconds = frame_count // fps
            timestamp = time.strftime('%H:%M:%S', time.gmtime(seconds))
            
            # Save frame
            frame_name = f"{camera_id}_{saved_count}_{int(time.time())}.jpg"
            frame_path = os.path.join("storage", "frames", frame_name)
            cv2.imwrite(frame_path, frame)
            
            # Generate description using zero-shot CLIP
            description = "Detected activity"
            if HAS_TRANSFORMERS:
                try:
                    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    inputs = processor(text=categories, images=image, return_tensors="pt", padding=True).to(device)
                    with torch.no_grad():
                        outputs = model(**inputs)
                    logits_per_image = outputs.logits_per_image
                    probs = logits_per_image.softmax(dim=1)
                    max_idx = probs.argmax().item()
                    
                    if probs[0][max_idx].item() > 0.2: # basic threshold
                        category = categories[max_idx]
                        if category != "empty scene":
                            description = f"Detected {category}"
                except Exception as e:
                    print(f"Error during classification: {e}")
            
            # Save event
            # To save clips, we'd need ffmpeg, for now we will just use the frame for MVP speed
            save_event(
                camera_id=camera_id,
                timestamp=timestamp,
                description=description,
                frame_path=frame_path,
                clip_path=None
            )
            saved_count += 1
            
        frame_count += 1
        
    cap.release()
    print(f"Finished processing {video_path}. Saved {saved_count} events.")

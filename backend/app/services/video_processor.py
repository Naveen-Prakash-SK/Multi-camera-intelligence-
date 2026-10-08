import cv2
import os
import time
from .indexer import save_event, HAS_TRANSFORMERS
from ..models.database import FRAMES_DIR
from PIL import Image

try:
    if HAS_TRANSFORMERS:
        from .indexer import model, processor, device
        import torch
except ImportError:
    pass

def process_video_bg(camera_id: str, video_path: str, interval_seconds: float = 2.0):
    """
    Extracts frames every N seconds, classifies them with CLIP zero-shot, computes visual embeddings, and saves events.
    """
    if not os.path.exists(video_path):
        print(f"Video path {video_path} does not exist.")
        return
        
    os.makedirs(FRAMES_DIR, exist_ok=True)
        
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 25.0 # Fallback
        
    frame_interval = max(1, int(round(fps * interval_seconds)))
    
    frame_count = 0
    saved_count = 0
    
    # Granular categories for accurate zero-shot event labeling
    categories = [
        "a white car",
        "a red car",
        "a black car",
        "a silver car",
        "a pickup truck",
        "a person walking",
        "a person riding a bicycle",
        "a bicycle",
        "construction workers wearing safety vests",
        "an empty road"
    ]
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            # Calculate timestamp accurately based on video FPS
            total_seconds = frame_count / fps
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # Save frame to verified FRAMES_DIR
            frame_name = f"{camera_id}_{saved_count}_{int(time.time())}.jpg"
            frame_path = os.path.join(FRAMES_DIR, frame_name)
            success = cv2.imwrite(frame_path, frame)
            if not success or not os.path.exists(frame_path):
                print(f"Warning: Failed to write frame to {frame_path}")
            
            # Generate description using zero-shot CLIP
            description = "Detected activity"
            if HAS_TRANSFORMERS and os.path.exists(frame_path):
                try:
                    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    inputs = processor(text=categories, images=image, return_tensors="pt", padding=True).to(device)
                    with torch.no_grad():
                        outputs = model(**inputs)
                    logits_per_image = outputs.logits_per_image
                    probs = logits_per_image.softmax(dim=1)
                    max_idx = probs.argmax().item()
                    
                    top_prob = probs[0][max_idx].item()
                    if top_prob > 0.30:
                        category = categories[max_idx]
                        if category != "an empty road":
                            description = f"Detected {category}"
                        else:
                            description = "Empty scene / road"
                except Exception as e:
                    print(f"Error during classification for {frame_name}: {e}")
            
            # Save event with visual embedding from the verified frame
            save_event(
                camera_id=camera_id,
                timestamp=timestamp,
                description=description,
                frame_path=frame_path,
                clip_path=None,
                frame_number=frame_count,
                video_path=video_path
            )
            saved_count += 1
            
        frame_count += 1
        
    cap.release()
    print(f"Finished processing {video_path} for {camera_id}. Saved {saved_count} events.")

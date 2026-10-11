import os
import cv2
import uuid
import numpy as np
import torch
from PIL import Image
from ultralytics import YOLO
import open_clip
from app.core.config import settings

class AdvancedPipeline:
    def __init__(self):
        print("Initializing Advanced Vision Pipeline...")
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # 1. YOLOv8 + ByteTrack
        print("Loading YOLOv8...")
        self.yolo = YOLO('yolov8n.pt') 
        
        # 2. ReID via SigLIP (Fallback for OSNet)
        print("Loading SigLIP2 for ReID and Full Frame...")
        self.siglip_model, _, self.siglip_preprocess = open_clip.create_model_and_transforms('ViT-B-16-SigLIP', pretrained='webli')
        self.siglip_model = self.siglip_model.to(self.device)
        self.siglip_model.eval()
        
    def extract_siglip(self, img_rgb: np.ndarray):
        pil_img = Image.fromarray(img_rgb)
        image_input = self.siglip_preprocess(pil_img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            features = self.siglip_model.encode_image(image_input)
            features = features / features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy()[0].tolist()

    def extract_reid(self, img_rgb: np.ndarray):
        # We reuse SigLIP for high-quality ReID embeddings
        return self.extract_siglip(img_rgb)

    def process_frame(self, frame_bgr: np.ndarray, timestamp_s: float, camera_id: str):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        
        # YOLO + ByteTrack
        results = self.yolo.track(frame_bgr, persist=True, tracker="bytetrack.yaml", verbose=False)
        
        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            for i in range(len(boxes)):
                box = boxes[i].xyxy[0].cpu().numpy()
                cls = int(boxes[i].cls[0].cpu().numpy())
                conf = float(boxes[i].conf[0].cpu().numpy())
                track_id = int(boxes[i].id[0].cpu().numpy()) if boxes[i].id is not None else -1
                
                label = self.yolo.names[cls]
                
                # Crop and extract SigLIP features for all objects
                reid_embedding = None
                x1, y1, x2, y2 = map(int, box)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame_rgb.shape[1], x2), min(frame_rgb.shape[0], y2)
                
                if (x2 - x1) > 10 and (y2 - y1) > 10:
                    crop = frame_rgb[y1:y2, x1:x2]
                    reid_embedding = self.extract_reid(crop)
                
                if label == 'person':
                    
                    # Privacy Anonymization: Blur the top 15% of the person's bounding box (Head/Upper-Body)
                    head_y_end = int(y1 + (y2 - y1) * 0.15)
                    if head_y_end > y1 and x2 > x1:
                        upper_body_region = frame_bgr[y1:head_y_end, x1:x2]
                        # Apply heavy gaussian blur
                        blurred = cv2.GaussianBlur(upper_body_region, (51, 51), 30)
                        frame_bgr[y1:head_y_end, x1:x2] = blurred
                        
                # Draw bounding box and label for visualization
                cv2.rectangle(frame_bgr, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
                text = f"{label} (ID: {track_id}) {conf:.2f}"
                cv2.putText(frame_bgr, text, (int(box[0]), max(10, int(box[1]) - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                detections.append({
                    "track_id": track_id,
                    "label": label,
                    "box": box.tolist(),
                    "confidence": conf,
                    "reid_embedding": reid_embedding
                })
                
        siglip_embedding = self.extract_siglip(frame_rgb)
        
        return {
            "siglip_embedding": siglip_embedding,
            "detections": detections,
            "frame_bgr": frame_bgr
        }

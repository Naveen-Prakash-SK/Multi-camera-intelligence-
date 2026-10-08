import os
import sqlite3
import json
import uuid
import numpy as np
from typing import List

from ..models.schemas import SearchResult, EventOut
from ..models.database import DB_PATH

# Try importing transformers. If it's not installed or slow, provide a fallback.
try:
    from transformers import CLIPProcessor, CLIPModel
    import torch
    from PIL import Image
    HAS_TRANSFORMERS = True
    print("Loading CLIP model...")
    # Use a small clip model for hackathon speed
    model_id = "openai/clip-vit-base-patch32"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained(model_id).to(device)
    processor = CLIPProcessor.from_pretrained(model_id)
    print("CLIP model loaded.")
except Exception as e:
    HAS_TRANSFORMERS = False
    print(f"Error loading transformers/CLIP: {e}. Falling back to keyword search.")

def get_text_embedding(text: str) -> np.ndarray:
    if not HAS_TRANSFORMERS:
        return np.random.rand(512)
    inputs = processor(text=[text], return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    return text_features.cpu().numpy().flatten()

def get_image_embedding(image_path: str) -> np.ndarray:
    if not HAS_TRANSFORMERS:
        return np.random.rand(512)
    try:
        image = Image.open(image_path)
        inputs = processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy().flatten()
    except Exception as e:
        print(f"Error getting image embedding for {image_path}: {e}")
        return np.random.rand(512)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def save_event(camera_id: str, timestamp: str, description: str, frame_path: str, clip_path: str = None, frame_number: int = 0, video_path: str = None):
    # Get embedding
    if HAS_TRANSFORMERS and os.path.exists(frame_path):
        emb = get_image_embedding(frame_path)
    else:
        # Fallback or dummy embedding
        emb = get_text_embedding(description)
        
    emb_list = emb.tolist()
    emb_json = json.dumps(emb_list)
    
    event_id = str(uuid.uuid4())
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (id, camera_id, timestamp, frame_number, description, frame_path, clip_path, video_path, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (event_id, camera_id, timestamp, frame_number, description, frame_path, clip_path, video_path, emb_json))
    conn.commit()
    conn.close()

def get_all_events() -> List[EventOut]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id, e.camera_id, c.camera_name, e.timestamp, e.description, e.frame_path, e.clip_path, e.frame_number, e.video_path
        FROM events e
        LEFT JOIN cameras c ON e.camera_id = c.camera_id
        ORDER BY e.timestamp DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    events = []
    for r in rows:
        events.append(EventOut(
            id=r[0],
            camera_id=r[1],
            camera_name=r[2] or "Unknown",
            timestamp=r[3],
            description=r[4],
            frame_url=f"/api/evidence/frames/{os.path.basename(r[5])}" if r[5] else "",
            clip_url=f"/api/evidence/clips/{os.path.basename(r[6])}" if r[6] else None,
            frame_number=r[7],
            video_path=r[8]
        ))
    return events

def search_index(query: str, threshold: float = 0.2) -> List[SearchResult]:
    from ..models.memory import get_mapping
    
    # Simple semantic search
    query_emb = get_text_embedding(query)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id, e.camera_id, c.camera_name, e.timestamp, e.description, e.frame_path, e.clip_path, e.embedding, e.frame_number, e.video_path
        FROM events e
        LEFT JOIN cameras c ON e.camera_id = c.camera_id
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    
    # Very basic entity extraction/memory fallback for hackathon
    mapped_camera = None
    for token in ["main gate", "lobby", "parking", "traffic", "highway", "crosswalk", "intersection"]:
        if token in query.lower():
            mapped = get_mapping(token)
            if mapped:
                mapped_camera = mapped
    
    # Seen frames suppression based on clip_url/frame_url to avoid duplicate events
    seen = set()
    
    for r in rows:
        event_cam_id = r[1]
        
        # If user explicitly asked for a known memory mapped area but it's not this camera, skip or penalize
        if mapped_camera and mapped_camera != event_cam_id:
            continue
            
        emb_json = r[7]
        try:
            event_emb = np.array(json.loads(emb_json))
            score = cosine_similarity(query_emb, event_emb)
        except:
            score = 0
            
        # Keyword fallback
        if not HAS_TRANSFORMERS:
            score = 0
            if any(word in r[4].lower() for word in query.lower().split()):
                score = 0.8
                
        if score >= threshold:
            key = f"{r[1]}_{r[3]}"
            if key in seen:
                continue
            seen.add(key)
            
            results.append({
                "score": score,
                "data": SearchResult(
                    camera_id=r[1],
                    camera_name=r[2] or "Unknown",
                    timestamp=r[3],
                    description=r[4],
                    score=float(score),
                    frame_url=f"/api/evidence/frames/{os.path.basename(r[5])}" if r[5] else "",
                    clip_url=f"/api/evidence/clips/{os.path.basename(r[6])}" if r[6] else None,
                    frame_number=r[8],
                    video_path=r[9]
                )
            })
            
    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top 3
    return [r["data"] for r in results[:3]]

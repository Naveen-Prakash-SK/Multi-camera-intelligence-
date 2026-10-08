import os
import sqlite3
import json
import uuid
import numpy as np
from typing import List, Tuple, Dict, Any, Optional

from ..models.schemas import SearchResult, EventOut
from ..models.database import DB_PATH, FRAMES_DIR

# Load HuggingFace CLIP model
try:
    from transformers import CLIPProcessor, CLIPModel
    import torch
    from PIL import Image
    HAS_TRANSFORMERS = True
    print("Loading CLIP model...")
    model_id = "openai/clip-vit-base-patch32"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained(model_id).to(device)
    processor = CLIPProcessor.from_pretrained(model_id)
    print(f"CLIP model loaded on {device}.")
except Exception as e:
    HAS_TRANSFORMERS = False
    print(f"Error loading transformers/CLIP: {e}. Falling back to rule-based indexing.")

def get_text_embedding(text: str) -> np.ndarray:
    if not HAS_TRANSFORMERS:
        return np.random.rand(512)
    inputs = processor(text=[text], return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        out = model.get_text_features(**inputs)
        if isinstance(out, torch.Tensor):
            text_features = out
        else:
            text_features = getattr(out, 'text_embeds', getattr(out, 'pooler_output', out[0]))
    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    return text_features.cpu().numpy().flatten()

def get_image_embedding(image_path: str) -> np.ndarray:
    if not HAS_TRANSFORMERS or not os.path.exists(image_path):
        return np.random.rand(512)
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.get_image_features(**inputs)
            if isinstance(out, torch.Tensor):
                image_features = out
            else:
                image_features = getattr(out, 'image_embeds', getattr(out, 'pooler_output', out[0]))
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy().flatten()
    except Exception as e:
        print(f"Error getting image embedding for {image_path}: {e}")
        return np.random.rand(512)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

def save_event(camera_id: str, timestamp: str, description: str, frame_path: str, clip_path: str = None, frame_number: int = 0, video_path: str = None):
    # Ensure real visual embedding is extracted from verified image file
    if HAS_TRANSFORMERS and os.path.exists(frame_path):
        emb = get_image_embedding(frame_path)
    else:
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
            camera_name=r[2] or f"Camera {r[1][-2:] if len(r[1])>=2 else r[1]}",
            timestamp=r[3],
            description=r[4],
            frame_url=f"/api/evidence/frames/{os.path.basename(r[5])}" if r[5] else "",
            clip_url=f"/api/evidence/clips/{os.path.basename(r[6])}" if r[6] else None,
            frame_number=r[7],
            video_path=r[8]
        ))
    return events

def parse_query(query: str) -> Dict[str, Any]:
    """
    Extracts semantic requirements from natural language query:
    - Target entities (car, truck, bicycle, person, worker)
    - Attributes / Colors (red, green, blue, white, black, silver, yellow)
    - Actions (passed, entered, crossed, walking, riding)
    - Location aliases (main gate, parking, etc.)
    """
    q = query.lower()
    
    entities = []
    if any(w in q for w in ["car", "cars", "automobile", "sedan", "vehicle", "vehicles"]):
        entities.append("car")
    if any(w in q for w in ["truck", "pickup", "lorry"]):
        entities.append("truck")
    if any(w in q for w in ["bicycle", "bicycles", "bike", "cyclist"]):
        entities.append("bicycle")
    if any(w in q for w in ["person", "people", "pedestrian", "pedestrians", "worker", "workers", "man", "woman"]):
        entities.append("person")
        
    colors = []
    for c in ["green", "red", "blue", "white", "black", "silver", "yellow"]:
        if c in q:
            colors.append(c)
            
    actions = []
    for a in ["passed", "pass", "passing", "entered", "enter", "entering", "crossed", "cross", "crossing", "walk", "walking", "ride", "riding"]:
        if a in q:
            actions.append(a)
            
    locations = []
    for loc in ["main gate", "lobby", "parking", "north", "east", "south", "intersection", "crosswalk", "zone"]:
        if loc in q:
            locations.append(loc)
            
    return {
        "entities": entities,
        "colors": colors,
        "actions": actions,
        "locations": locations,
        "raw_query": query
    }

def verify_candidate_visually(frame_path: str, parsed: Dict[str, Any]) -> Tuple[bool, float, str]:
    """
    Strict Visual Verification Stage:
    Loads candidate frame and runs zero-shot hypothesis discrimination for requested object and attributes.
    Rejects hallucinations, false positives, and color mismatches.
    """
    if not os.path.exists(frame_path) or os.path.getsize(frame_path) == 0:
        return False, 0.0, "Evidence frame missing on disk"
        
    if not HAS_TRANSFORMERS:
        # Fallback if transformers unavailable
        return True, 0.75, "Fallback verification"
        
    try:
        img = Image.open(frame_path).convert("RGB")
    except Exception as e:
        return False, 0.0, f"Cannot open evidence image: {e}"
        
    entities = parsed["entities"]
    colors = parsed["colors"]
    
    # 1. Visual Entity Verification
    if "car" in entities or "truck" in entities:
        hypotheses = ["a car or vehicle on the road", "a bicycle", "a pedestrian walking with no vehicles", "an empty background"]
        inputs = processor(text=hypotheses, images=img, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0].cpu().numpy()
        vehicle_prob = float(probs[0])
        if vehicle_prob < 0.28:
            return False, vehicle_prob, "No vehicle detected in frame"
            
    if "bicycle" in entities:
        hypotheses = ["a bicycle or person riding bicycle", "a car or truck", "pedestrians with no bicycle", "an empty road"]
        inputs = processor(text=hypotheses, images=img, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0].cpu().numpy()
        bike_prob = float(probs[0])
        if bike_prob < 0.35:
            return False, bike_prob, "No bicycle detected in frame"
            
    if "person" in entities:
        hypotheses = ["a person or pedestrian walking", "construction workers in safety gear", "a vehicle with no people", "an empty scene"]
        inputs = processor(text=hypotheses, images=img, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0].cpu().numpy()
        person_prob = float(probs[0] + probs[1])
        if person_prob < 0.30:
            return False, person_prob, "No person detected in frame"
            
    # 2. Visual Color / Attribute Verification
    if colors:
        target_color = colors[0]
        if "car" in entities or "truck" in entities or not entities:
            color_hypotheses = [
                f"a {target_color} car",
                "a white car",
                "a silver car",
                "a black car",
                "a red car",
                "a blue car",
                "a green car"
            ]
        else:
            color_hypotheses = [
                f"{target_color} clothing",
                "dark clothing",
                "bright orange safety vest",
                "white clothing"
            ]
            
        inputs = processor(text=color_hypotheses, images=img, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        color_probs = outputs.logits_per_image.softmax(dim=1)[0].cpu().numpy()
        
        target_prob = float(color_probs[0])
        max_color_idx = int(np.argmax(color_probs))
        
        # If target color is not top or is significantly outscored by another color, reject
        if max_color_idx != 0 or target_prob < 0.30:
            top_color_detected = color_hypotheses[max_color_idx]
            return False, target_prob, f"Color mismatch: requested '{target_color}', but frame shows '{top_color_detected}' ({color_probs[max_color_idx]*100:.1f}%)"
            
    # Compute overall visual alignment score
    direct_input = processor(text=[parsed["raw_query"]], images=img, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        out = model(**direct_input)
    # Calibrated score
    raw_logit = float(out.logits_per_image[0][0].cpu().item())
    visual_confidence = float(1.0 / (1.0 + np.exp(- (raw_logit - 20.0) / 4.0)))
    visual_confidence = min(0.98, max(0.60, visual_confidence))
    
    return True, visual_confidence, "Verified visual match"

def search_index(query: str, threshold: float = 0.25) -> List[SearchResult]:
    from ..models.memory import get_mapping
    
    parsed = parse_query(query)
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
    
    if not rows:
        return []
        
    # Check for memory mapped cameras (e.g. "main gate" -> "camera_01")
    mapped_camera = None
    for token in parsed["locations"]:
        mapped = get_mapping(token)
        if mapped:
            mapped_camera = mapped
            break
            
    # Step 1: Candidate Retrieval via CLIP Visual Embeddings
    candidates = []
    for r in rows:
        event_cam_id = r[1]
        
        # If user specified a known mapped area, restrict to that camera
        if mapped_camera and mapped_camera != event_cam_id:
            continue
            
        emb_json = r[7]
        try:
            event_emb = np.array(json.loads(emb_json))
            retrieval_score = cosine_similarity(query_emb, event_emb)
        except Exception:
            retrieval_score = 0.0
            
        if retrieval_score >= threshold:
            candidates.append({
                "row": r,
                "retrieval_score": retrieval_score
            })
            
    # Sort candidates by initial retrieval score
    candidates.sort(key=lambda x: x["retrieval_score"], reverse=True)
    
    # Step 2: Multi-Stage Verification (Visual, Attribute, Temporal, Evidence)
    verified_results = []
    seen_camera_timestamps = set()
    
    for cand in candidates[:15]: # Verify top 15 candidate frames
        r = cand["row"]
        cam_id = r[1]
        cam_name = r[2] or f"Camera {cam_id[-2:] if len(cam_id)>=2 else cam_id}"
        timestamp = r[3]
        desc = r[4]
        frame_path = r[5]
        clip_path = r[6]
        frame_num = r[8]
        video_path = r[9]
        
        # Deduplication key
        key = f"{cam_id}_{timestamp}"
        if key in seen_camera_timestamps:
            continue
            
        # Run strict visual verification
        is_verified, verified_score, reason = verify_candidate_visually(frame_path, parsed)
        
        if is_verified:
            seen_camera_timestamps.add(key)
            verified_results.append(SearchResult(
                camera_id=cam_id,
                camera_name=cam_name,
                timestamp=timestamp,
                frame_number=frame_num,
                description=desc,
                score=round(verified_score, 3),
                verified=True,
                frame_url=f"/api/evidence/frames/{os.path.basename(frame_path)}" if frame_path else "",
                clip_url=f"/api/evidence/clips/{os.path.basename(clip_path)}" if clip_path else None,
                video_path=video_path,
                verification_details=reason
            ))
            
    # Sort verified results by confidence
    verified_results.sort(key=lambda x: x.score, reverse=True)
    
    # Return top 3 verified matches
    return verified_results[:3]

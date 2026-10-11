import httpx
import json
from app.core.config import settings

OLLAMA_PROXY_URL = f"{settings.OLLAMA_BASE_URL}/api/generate"

OLLAMA_AUTH = None
if settings.OLLAMA_AUTH_USER and settings.OLLAMA_AUTH_PASSWORD:
    OLLAMA_AUTH = (settings.OLLAMA_AUTH_USER, settings.OLLAMA_AUTH_PASSWORD)

async def parse_query_with_llm(user_query: str) -> dict:
    prompt = f"""
    You are an intelligent video surveillance query parser.
    Extract the following from the user query into strict JSON:
    - entity (e.g. person, vehicle, car)
    - description (e.g. red car, man with bag)
    - attributes (e.g. {{"color": "red"}})
    - location (e.g. main gate, lobby)
    - event (e.g. pass_through, entered)
    
    Query: "{user_query}"
    
    Output ONLY valid JSON.
    """
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(OLLAMA_PROXY_URL, headers={"ngrok-skip-browser-warning": "true"}, auth=OLLAMA_AUTH, json={
                "model": settings.OLLAMA_REASONING_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }, timeout=settings.OLLAMA_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "{}")
            return json.loads(response_text)
    except Exception as e:
        print(f"LLM Parsing failed: {e}. Falling back to rule-based parsing.")
        import re
        location = None
        if " at " in user_query:
            location = user_query.split(" at ")[-1].strip()
            # Remove time fragments from location
            location = re.sub(r'(between|from|around).+', '', location).strip()
        elif " in " in user_query:
            location = user_query.split(" in ")[-1].strip()
            location = re.sub(r'(between|from|around).+', '', location).strip()
            
        time_range = None
        time_match = re.search(r'between\s+(\d+\s*(?:AM|PM|am|pm)?)\s+and\s+(\d+\s*(?:AM|PM|am|pm)?)', user_query, re.IGNORECASE)
        if time_match:
            time_range = {"start": time_match.group(1), "end": time_match.group(2)}
        
        entity = "object"
        for obj in ["person", "car", "truck", "bicycle", "vehicle"]:
            if obj in user_query.lower():
                entity = obj
                break

        return {
            "entity": entity,
            "description": user_query,
            "attributes": {},
            "location": location,
            "time_range": time_range,
            "event": None
        }

import base64

async def verify_evidence_with_vlm(user_query: str, image_path: str) -> dict:
    """
    Use VLM to verify if the frame answers the user query.
    If VLM is unavailable, returns a degraded state with 0 confidence, 
    but still allows the match to pass through based on previous OwlViT/CLIP scores.
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        prompt = f"""
        Does this image show evidence of the following event?
        Query: "{user_query}"
        
        Respond ONLY in strict JSON format:
        {{
            "match": true/false,
            "confidence": 0.0 to 1.0,
            "reason": "Brief explanation"
        }}
        """
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(OLLAMA_PROXY_URL, headers={"ngrok-skip-browser-warning": "true"}, auth=OLLAMA_AUTH, json={
                "model": settings.OLLAMA_VISION_MODEL,
                "prompt": prompt,
                "images": [encoded_string],
                "stream": False,
                "format": "json"
            }, timeout=settings.OLLAMA_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "{}")
            return json.loads(response_text)
            
    except Exception as e:
        print(f"VLM Verification failed or unavailable: {e}")
        return {
            "match": True, 
            "confidence": 0.0, 
            "reason": "VLM unavailable, degraded state."
        }

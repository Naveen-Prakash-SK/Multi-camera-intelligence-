from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.core.config import settings
import httpx
import redis
import sqlalchemy
from sqlalchemy import text
from qdrant_client import QdrantClient

router = APIRouter()

# Dependency or utility functions for health checks
def check_postgres() -> str:
    try:
        engine = sqlalchemy.create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 2})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ONLINE"
    except Exception as e:
        return f"DEGRADED: {str(e)}"

def check_redis() -> str:
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, socket_timeout=2)
        if r.ping():
            return "ONLINE"
        return "DEGRADED: Ping failed"
    except Exception as e:
        return f"DEGRADED: {str(e)}"

def check_qdrant() -> str:
    try:
        # Assuming Qdrant HTTP API is at QDRANT_URL
        client = httpx.Client(timeout=2)
        response = client.get(f"{settings.QDRANT_URL}/healthz")
        if response.status_code == 200:
            return "ONLINE"
        return f"DEGRADED: Status {response.status_code}"
    except Exception as e:
        return f"DEGRADED: {str(e)}"

def check_ollama() -> str:
    try:
        client = httpx.Client(timeout=2)
        response = client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            return "ONLINE"
        return f"DEGRADED: Status {response.status_code}"
    except Exception as e:
        return f"OFFLINE"

@router.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ONLINE"}

@router.get("/health/services")
def health_services() -> Dict[str, Any]:
    return {
        "postgres": check_postgres(),
        "redis": check_redis(),
        "qdrant": check_qdrant(),
        "ollama": check_ollama(),
        "gateway": "NOT_CONFIGURED" # Gateway check to be implemented
    }

@router.get("/health/models")
def health_models() -> Dict[str, Any]:
    # Placeholder for actual model availability checks
    ollama_status = check_ollama()
    models = {
        "qwen3-8b": "OFFLINE",
        "qwen3-vl": "OFFLINE",
        "bge-m3": "OFFLINE",
        "siglip-2": "OFFLINE",
        "yolo": "OFFLINE",
        "reid": "OFFLINE"
    }
    
    if ollama_status == "ONLINE":
        try:
            client = httpx.Client(timeout=2)
            response = client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                available_models = [m["name"] for m in response.json().get("models", [])]
                if any(settings.OLLAMA_REASONING_MODEL in m for m in available_models):
                    models["qwen3-8b"] = "ONLINE"
                if any(settings.OLLAMA_VISION_MODEL in m for m in available_models):
                    models["qwen3-vl"] = "ONLINE"
        except:
            pass
            
    return models

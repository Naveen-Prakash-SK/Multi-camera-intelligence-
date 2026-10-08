from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.core.config import settings
import httpx
import redis
import sqlalchemy
from sqlalchemy import text
from qdrant_client import QdrantClient
from app.api.llm_service import OLLAMA_AUTH

router = APIRouter()

# Dependency or utility functions for health checks
def check_postgres() -> str:
    try:
        sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
        engine = sqlalchemy.create_engine(sync_url, connect_args={"connect_timeout": 2})
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
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
        client = httpx.Client(timeout=1.0, verify=False, headers={"ngrok-skip-browser-warning": "true"}, auth=OLLAMA_AUTH)
        response = client.get(url)
        if response.status_code == 200:
            return "ONLINE"
        return f"DEGRADED: Status {response.status_code}"
    except Exception as e:
        return f"OFFLINE: {str(e)}"

def check_live_stream() -> str:
    try:
        url = "http://host.docker.internal:8001/health"
        client = httpx.Client(timeout=2.0, verify=False)
        response = client.get(url)
        if response.status_code == 200:
            return "ONLINE"
        return f"DEGRADED: Status {response.status_code}"
    except Exception as e:
        return f"OFFLINE: {str(e)}"

@router.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ONLINE"}

@router.get("/api/health/services")
def health_services() -> Dict[str, Any]:
    return {
        "api": "ONLINE",
        "services": {
            "postgresql": check_postgres(),
            "redis": check_redis(),
            "qdrant": check_qdrant(),
            "live_stream": check_live_stream(),
        },
        "models": {
            "ollama": check_ollama(),
        }
    }

@router.get("/api/health/models")
def health_models() -> Dict[str, Any]:
    # Placeholder for actual model availability checks
    ollama_status = check_ollama()
    models = {
        settings.OLLAMA_REASONING_MODEL: "OFFLINE",
        settings.OLLAMA_VISION_MODEL: "OFFLINE",
        "bge-m3": "OFFLINE",
        "siglip-2": "OFFLINE",
        "yolo": "OFFLINE",
        "reid": "OFFLINE"
    }

    if ollama_status == "ONLINE":
        try:
            url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
            client = httpx.Client(timeout=1.0, verify=False, headers={"ngrok-skip-browser-warning": "true"}, auth=OLLAMA_AUTH)
            response = client.get(url)
            if response.status_code == 200:
                available_models = [m["name"] for m in response.json().get("models", [])]
                if any(settings.OLLAMA_REASONING_MODEL in m for m in available_models):
                    models[settings.OLLAMA_REASONING_MODEL] = "ONLINE"
                if any(settings.OLLAMA_VISION_MODEL in m for m in available_models):
                    models[settings.OLLAMA_VISION_MODEL] = "ONLINE"
        except:
            pass
            
    return models

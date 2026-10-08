from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel, UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.core import Camera, CameraZone

router = APIRouter()

class CameraCreate(BaseModel):
    name: str
    stream_url: str | None = None
    clock_offset_ms: int = 0

class CameraResponse(CameraCreate):
    id: UUID4
    status: str

@router.post("/api/cameras", response_model=CameraResponse)
async def create_camera(camera: CameraCreate):
    # Dummy implementation for now (no DB connection without Postgres)
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": camera.name,
        "stream_url": camera.stream_url,
        "clock_offset_ms": camera.clock_offset_ms,
        "status": "OFFLINE"
    }

@router.get("/api/cameras", response_model=List[CameraResponse])
async def list_cameras():
    return []

@router.get("/api/cameras/{id}", response_model=CameraResponse)
async def get_camera(id: UUID4):
    raise HTTPException(status_code=404, detail="Camera not found")

@router.post("/api/cameras/{id}/start")
async def start_camera(id: UUID4):
    return {"status": "Starting"}

@router.post("/api/cameras/{id}/stop")
async def stop_camera(id: UUID4):
    return {"status": "Stopping"}

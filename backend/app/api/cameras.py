from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel, UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.deps import get_db
from app.models.core import Camera
import uuid

router = APIRouter()

class CameraCreate(BaseModel):
    name: str
    description: str | None = None
    source_type: str = "file"
    stream_url: str | None = None
    location: str | None = None
    clock_offset_ms: int = 0

class CameraResponse(CameraCreate):
    id: UUID4
    status: str

@router.post("/api/cameras", response_model=CameraResponse)
async def create_camera(camera: CameraCreate, db: AsyncSession = Depends(get_db)):
    new_camera = Camera(
        name=camera.name,
        description=camera.description,
        source_type=camera.source_type,
        stream_url=camera.stream_url,
        location=camera.location,
        clock_offset_ms=camera.clock_offset_ms,
        status="OFFLINE"
    )
    db.add(new_camera)
    await db.commit()
    await db.refresh(new_camera)
    return new_camera

@router.get("/api/cameras", response_model=List[CameraResponse])
async def list_cameras(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera))
    return result.scalars().all()

@router.get("/api/cameras/{id}", response_model=CameraResponse)
async def get_camera(id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.put("/api/cameras/{id}", response_model=CameraResponse)
async def update_camera(id: UUID4, camera_in: CameraCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    for var, value in vars(camera_in).items():
        setattr(camera, var, value)
        
    await db.commit()
    await db.refresh(camera)
    return camera

@router.delete("/api/cameras/{id}")
async def delete_camera(id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    await db.delete(camera)
    await db.commit()
    return {"status": "Deleted"}

@router.post("/api/cameras/{id}/start")
async def start_camera(id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    camera.status = "ONLINE"
    await db.commit()
    return {"status": "ONLINE"}

@router.post("/api/cameras/{id}/stop")
async def stop_camera(id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    camera.status = "OFFLINE"
    await db.commit()
    return {"status": "OFFLINE"}

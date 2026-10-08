from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, UUID4
import uuid

router = APIRouter()

class MemoryItem(BaseModel):
    id: UUID4
    location_name: str
    camera_id: UUID4
    zone_id: Optional[UUID4] = None
    aliases: List[str] = []
    version: int

class MemoryCreate(BaseModel):
    location_name: str
    camera_id: UUID4
    zone_id: Optional[UUID4] = None
    aliases: List[str] = []

@router.post("/api/memory", response_model=MemoryItem)
async def create_memory(memory: MemoryCreate):
    return MemoryItem(
        id=uuid.uuid4(),
        location_name=memory.location_name,
        camera_id=memory.camera_id,
        zone_id=memory.zone_id,
        aliases=memory.aliases,
        version=1
    )

@router.get("/api/memory", response_model=List[MemoryItem])
async def list_memory():
    return []

@router.get("/api/memory/{id}", response_model=MemoryItem)
async def get_memory(id: UUID4):
    raise HTTPException(status_code=404, detail="Memory not found")

@router.put("/api/memory/{id}", response_model=MemoryItem)
async def update_memory(id: UUID4, memory: MemoryCreate):
    return MemoryItem(
        id=id,
        location_name=memory.location_name,
        camera_id=memory.camera_id,
        zone_id=memory.zone_id,
        aliases=memory.aliases,
        version=2
    )

@router.delete("/api/memory/{id}")
async def delete_memory(id: UUID4):
    return {"status": "Deleted"}

@router.get("/api/memory/{id}/versions")
async def memory_versions(id: UUID4):
    return []

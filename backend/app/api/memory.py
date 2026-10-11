from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel, UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.deps import get_db
from app.models.events import SceneMemory
import uuid

router = APIRouter()

class MemoryCreate(BaseModel):
    location_name: str
    camera_id: UUID4
    zone_id: UUID4 | None = None
    aliases: List[str] = []

class MemoryItem(MemoryCreate):
    id: UUID4
    version: int

@router.post("/api/memory", response_model=MemoryItem)
async def create_memory(memory: MemoryCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SceneMemory).where(SceneMemory.location_name == memory.location_name))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=409, detail="Location name already exists")

    new_memory = SceneMemory(
        location_name=memory.location_name,
        camera_id=memory.camera_id,
        zone_id=memory.zone_id,
        aliases=memory.aliases,
        version=1
    )
    db.add(new_memory)
    await db.commit()
    await db.refresh(new_memory)
    return new_memory

@router.get("/api/memory", response_model=List[MemoryItem])
async def list_memory(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SceneMemory))
    return result.scalars().all()

@router.get("/api/memory/{id}", response_model=MemoryItem)
async def get_memory(id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SceneMemory).where(SceneMemory.id == id))
    memory = result.scalars().first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@router.put("/api/memory/{id}", response_model=MemoryItem)
async def update_memory(id: UUID4, memory_in: MemoryCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SceneMemory).where(SceneMemory.id == id))
    memory = result.scalars().first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    memory.location_name = memory_in.location_name
    memory.camera_id = memory_in.camera_id
    memory.zone_id = memory_in.zone_id
    memory.aliases = memory_in.aliases
    memory.version += 1
        
    await db.commit()
    await db.refresh(memory)
    return memory

@router.delete("/api/memory/{id}")
async def delete_memory(id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SceneMemory).where(SceneMemory.id == id))
    memory = result.scalars().first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    await db.delete(memory)
    await db.commit()
    return {"status": "Deleted"}

@router.get("/api/memory/{id}/versions")
async def memory_versions(id: UUID4):
    return []

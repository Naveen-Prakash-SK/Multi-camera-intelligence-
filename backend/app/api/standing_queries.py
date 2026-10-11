from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.deps import get_db
from app.models.core import StandingQuery
from app.api.llm_service import parse_query_with_llm
import uuid

router = APIRouter()

from pydantic import BaseModel

class StandingQueryRequest(BaseModel):
    query: str
    condition: str = ""
    cooldown_seconds: int = 60
    camera_id: str = None

@router.post("/api/standing_queries")
async def create_standing_query(req: StandingQueryRequest, db: AsyncSession = Depends(get_db)):
    """
    Creates a new standing query.
    Future frames will be evaluated against this in tasks.py.
    """
    # 1. Parse intention
    structured_query = await parse_query_with_llm(req.query)
    
    # 2. Store in database
    sq = StandingQuery(
        id=uuid.uuid4(),
        original_query=req.query,
        structured_query=structured_query,
        camera_id=uuid.UUID(req.camera_id) if req.camera_id else None
    )
    db.add(sq)
    await db.commit()
    
    return {"status": "success", "id": str(sq.id), "structured": structured_query}

@router.get("/api/standing_queries")
async def list_standing_queries(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StandingQuery))
    return [{"id": str(sq.id), "query": sq.original_query, "enabled": sq.enabled} for sq in res.scalars().all()]

from app.models.events import Alert
from sqlalchemy import desc

@router.get("/api/alerts")
async def list_alerts(db: AsyncSession = Depends(get_db), limit: int = 20):
    res = await db.execute(select(Alert).order_by(desc(Alert.timestamp)).limit(limit))
    return [
        {
            "id": str(a.id),
            "standing_query_id": str(a.standing_query_id),
            "camera_id": str(a.camera_id),
            "timestamp": a.timestamp.isoformat(),
            "message": a.message,
            "is_read": a.is_read
        } for a in res.scalars().all()
    ]


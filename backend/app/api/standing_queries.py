from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.deps import get_db
from app.models.core import StandingQuery
from app.api.llm_service import parse_query_with_llm
import uuid

router = APIRouter()

@router.post("/api/standing_queries")
async def create_standing_query(query_text: str, camera_id: str = None, db: AsyncSession = Depends(get_db)):
    """
    Creates a new standing query (Phase 21).
    Future frames will be evaluated against this via StandingQueryMatcher.
    """
    # 1. Parse intention
    structured_query = await parse_query_with_llm(query_text)
    
    # 2. Store in database
    sq = StandingQuery(
        id=uuid.uuid4(),
        original_query=query_text,
        structured_query=structured_query,
        camera_id=uuid.UUID(camera_id) if camera_id else None
    )
    db.add(sq)
    await db.commit()
    
    return {"status": "success", "id": str(sq.id), "structured": structured_query}

@router.get("/api/standing_queries")
async def list_standing_queries(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StandingQuery))
    return [{"id": str(sq.id), "query": sq.original_query, "enabled": sq.enabled} for sq in res.scalars().all()]

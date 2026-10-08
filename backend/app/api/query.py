from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.deps import get_db
from app.models.core import QueryHistory, Camera, Frame
from app.vector.qdrant import search_frames
import uuid
from datetime import datetime, timezone

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    clarification_answer: Optional[dict] = None

class EvidenceRef(BaseModel):
    evidence_id: str
    thumbnail_url: str
    clip_url: str

class QueryResultItem(BaseModel):
    event_id: str
    camera_id: str
    camera_name: str
    timestamp: str
    object_type: str
    attributes: Dict[str, Any]
    confidence: float
    verification: Dict[str, str]
    evidence: EvidenceRef

class QueryResponse(BaseModel):
    verdict: str
    answer: str
    grounded: bool
    resolved: Dict[str, Any]
    coverage: Dict[str, Any]
    results: List[QueryResultItem]
    trace_id: str

def get_dummy_embedding(text: str) -> list[float]:
    # Placeholder for Ollama text embedding model blocked by corporate firewall
    return [0.1] * 1536

@router.post("/api/query", response_model=QueryResponse)
async def execute_query(req: QueryRequest, db: AsyncSession = Depends(get_db)):
    trace_id = str(uuid.uuid4())
    
    # 1. Store QueryHistory in DB
    history = QueryHistory(
        id=uuid.UUID(trace_id),
        query=req.query,
        parsed_query={"session_id": req.session_id} if req.session_id else None
    )
    db.add(history)
    
    # 2. Convert text query to Embedding
    query_emb = get_dummy_embedding(req.query)
    
    # 3. Search Qdrant for matching frames
    search_results = search_frames(query_embedding=query_emb, limit=5)
    
    # 4. Construct Results
    response_items = []
    for hit in search_results:
        # hit.payload contains camera_id, timestamp_s, object_type, etc.
        camera_id = hit.payload.get("camera_id")
        timestamp_s = hit.payload.get("timestamp_s")
        
        # Resolve camera name
        camera = await db.execute(select(Camera).where(Camera.id == uuid.UUID(camera_id)))
        camera_obj = camera.scalars().first()
        camera_name = camera_obj.name if camera_obj else "Unknown Camera"
        
        response_items.append(
            QueryResultItem(
                event_id=hit.id,
                camera_id=camera_id,
                camera_name=camera_name,
                timestamp=datetime.now(timezone.utc).isoformat(), # Mock relative timestamp
                object_type=hit.payload.get("object_type", "unknown"),
                attributes={"hit_score": hit.score},
                confidence=hit.score,
                verification={"verdict": "matches", "model": "qdrant_cosine"},
                evidence=EvidenceRef(
                    evidence_id=str(uuid.uuid4()),
                    thumbnail_url=f"/api/evidence/{hit.id}/thumbnail",
                    clip_url=f"/api/evidence/{hit.id}/clip"
                )
            )
        )
    
    # Update Query History with response payload
    if history.parsed_query:
        history.parsed_query["intent"] = req.query
        history.parsed_query["embedding"] = "dummy"
    else:
        history.parsed_query = {"intent": req.query, "embedding": "dummy"}
    history.result_ids = {"results_count": len(response_items)}
    await db.commit()
    
    return QueryResponse(
        verdict="YES_UNVERIFIED" if len(response_items) > 0 else "NO",
        answer=f"Found {len(response_items)} results for: {req.query}",
        grounded=len(response_items) > 0,
        resolved={"location": "All", "time_window": {"from": "T1", "to": "T2"}, "relaxed_filters": []},
        coverage={"cameras_searched": [], "indexed_range": {"from": "T1", "to": "T2"}},
        results=response_items,
        trace_id=trace_id
    )

@router.get("/api/queries/{id}")
async def get_query_trace(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(QueryHistory).where(QueryHistory.id == uuid.UUID(id)))
    history = result.scalars().first()
    if not history:
        raise HTTPException(status_code=404, detail="Trace not found")
        
    return {
        "id": str(history.id),
        "query": history.query,
        "parsed_query": history.parsed_query,
        "result_ids": history.result_ids,
        "created_at": history.created_at
    }

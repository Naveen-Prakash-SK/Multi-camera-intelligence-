from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.api.deps import get_db
from app.models.core import QueryHistory, Camera, Frame, Evidence
from app.vector.qdrant import search_frames
from app.api.llm_service import parse_query_with_llm, verify_evidence_with_vlm
from app.models.events import SceneMemory
from app.vector.embeddings import embedding_service
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
    confidence: float
    grounded: bool
    resolved: Dict[str, Any]
    coverage: Dict[str, Any]
    results: List[QueryResultItem]
    trace_id: str

@router.post("/api/query", response_model=QueryResponse)
async def execute_query(req: QueryRequest, db: AsyncSession = Depends(get_db)):
    trace_id = str(uuid.uuid4())
    
    # 1. Parse natural language with LLM
    parsed = await parse_query_with_llm(req.query)
    
    # 2. Scene Memory Resolution
    target_camera_id = None
    clarification_required = False
    candidates = []
    
    if req.clarification_answer and req.clarification_answer.get("camera_id"):
        # User answered the clarification
        target_camera_id = req.clarification_answer["camera_id"]
        if parsed.get("location"):
            loc = parsed["location"].lower()
            mem = SceneMemory(
                location_name=loc,
                camera_id=uuid.UUID(target_camera_id),
                aliases=[],
                version=1
            )
            db.add(mem)
            await db.commit()
    elif parsed.get("location"):
        # Try to resolve location (by canonical name or any alias)
        loc = parsed["location"].lower()
        mem_query = await db.execute(
            select(SceneMemory).where(
                or_(
                    SceneMemory.location_name == loc,
                    SceneMemory.aliases.contains([loc])
                )
            )
        )
        mem = mem_query.scalars().first()
        if mem:
            target_camera_id = str(mem.camera_id)
        else:
            # Need clarification
            clarification_required = True
            cams = await db.execute(select(Camera))
            for c in cams.scalars().all():
                candidates.append({"id": str(c.id), "name": c.name})

    if clarification_required:
        return QueryResponse(
            verdict="CLARIFICATION_REQUIRED",
            answer=f"Which camera represents '{parsed['location']}'?",
            grounded=False,
            resolved={"location": parsed["location"]},
            coverage={"candidates": candidates},
            results=[],
            trace_id=trace_id
        )

    # 3. Store QueryHistory in DB
    history = QueryHistory(
        id=uuid.UUID(trace_id),
        query=req.query,
        parsed_query=parsed
    )
    db.add(history)
    
    # 4. Convert text query to Embedding
    query_emb = embedding_service.encode_text(req.query)
    
    # Process time range
    time_filter = None
    if parsed.get("time_range"):
        try:
            # Quick heuristic parser for "9 AM", "10 AM" to absolute Unix today
            # Real impl would use dateparser or LLM ISO8601 extraction
            now = datetime.now(timezone.utc)
            start_str = parsed["time_range"]["start"]
            end_str = parsed["time_range"]["end"]
            
            from dateutil import parser as date_parser
            start_dt = date_parser.parse(start_str, default=now)
            end_dt = date_parser.parse(end_str, default=now)
            
            time_filter = (start_dt.timestamp(), end_dt.timestamp())
        except Exception as e:
            print(f"Time parse error: {e}")
            pass

    # 5. Search Qdrant for matching frames
    search_results = search_frames(
        query_embedding=query_emb, 
        limit=5, 
        camera_id=target_camera_id, 
        time_range=time_filter
    )
    
    # 6. Construct Results & Verification
    response_items = []
    
    # OwlViT verification (model weights are cached across requests)
    from app.vector.detection import get_detection_service
    detection_svc = get_detection_service()
    
    for hit in search_results:
        camera_id = hit.payload.get("camera_id")
        timestamp_s = hit.payload.get("timestamp_s")
        frame_id = hit.payload.get("frame_id")
        
        # Get Frame from DB
        frame_db = await db.execute(select(Frame).where(Frame.id == uuid.UUID(frame_id)))
        frame_obj = frame_db.scalars().first()
        if not frame_obj:
            continue
            
        # OwlViT Query-Driven Verification
        owlvit_detections = detection_svc.detect_with_query(frame_obj.frame_path, req.query, threshold=0.08)
        if not owlvit_detections:
            continue # Prune if OwlViT doesn't see concepts related to the query
            
        best_owl_score = max([d["confidence"] for d in owlvit_detections])
        
        # Resolve camera name
        camera = await db.execute(select(Camera).where(Camera.id == uuid.UUID(camera_id)))
        camera_obj = camera.scalars().first()
        camera_name = camera_obj.name if camera_obj else "Unknown Camera"
        
        # VLM Verification
        vlm_res = await verify_evidence_with_vlm(req.query, frame_obj.frame_path)
        if not vlm_res.get("match", False):
            continue
            
        final_confidence = (hit.score * 0.3) + (best_owl_score * 0.3) + (vlm_res.get("confidence", 0.0) * 0.4)

        # Persist the evidence so the thumbnail/clip endpoints can resolve it
        evd = Evidence(
            video_id=frame_obj.video_id,
            camera_id=uuid.UUID(camera_id),
            timestamp_s=frame_obj.timestamp_s,
            frame_path=frame_obj.frame_path,
        )
        db.add(evd)
        await db.flush()

        response_items.append(
            QueryResultItem(
                event_id=hit.id,
                camera_id=camera_id,
                camera_name=camera_name,
                timestamp=datetime.fromtimestamp(timestamp_s, tz=timezone.utc).isoformat(),
                object_type=hit.payload.get("label", parsed.get("entity", "unknown")),
                attributes={"hit_score": hit.score, "vlm_reason": vlm_res.get("reason", "")},
                confidence=final_confidence,
                verification={"verdict": "verified", "model": "qwen_vlm"},
                evidence=EvidenceRef(
                    evidence_id=str(evd.id),
                    thumbnail_url=f"/api/evidence/{evd.id}/thumbnail",
                    clip_url=f"/api/evidence/{evd.id}/clip"
                )
            )
        )
        
    # Rank by final confidence
    response_items.sort(key=lambda x: x.confidence, reverse=True)
    
    # Update Query History with response payload
    if history.parsed_query:
        history.parsed_query["intent"] = req.query
        history.parsed_query["embedding"] = "dummy"
    else:
        history.parsed_query = {"intent": req.query, "embedding": "dummy"}
    history.result_ids = {"results_count": len(response_items)}
    await db.commit()
    
    # 7. Grounded Answer Generation
    if response_items:
        best = response_items[0]
        answer = f"Yes. A {best.object_type} matching your query was detected at {best.camera_name} at {best.timestamp}."
        verdict = "YES"
        top_conf = best.confidence
    else:
        answer = "I could not verify this event from the available footage."
        verdict = "NO"
        top_conf = 0.0

    return QueryResponse(
        verdict=verdict,
        answer=answer,
        confidence=top_conf,
        grounded=len(response_items) > 0,
        resolved={"location": parsed.get("location", "All"), "time_window": parsed.get("time_range")},
        coverage={"cameras_searched": [], "indexed_range": {}},
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

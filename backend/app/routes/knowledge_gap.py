from fastapi import APIRouter, HTTPException
from ..models.schemas import KnowledgeGapRequest, KnowledgeGapResponse, ErrorResponse
from ..services import knowledge_gap_service

router = APIRouter()

@router.post('/knowledge-gap', response_model=KnowledgeGapResponse, responses={400:{'model': ErrorResponse}, 502:{'model': ErrorResponse}})
async def knowledge_gap(payload: KnowledgeGapRequest):
    if not payload.target_topic or not payload.known_concepts:
        raise HTTPException(status_code=400, detail={'error':True,'message':'Invalid request','code':'INVALID_REQUEST'})
    try:
        res = await knowledge_gap_service.analyze(payload.known_concepts, payload.target_topic)
        return res
    except Exception as e:
        raise HTTPException(status_code=502, detail={"error": True, "message": str(e), "code": "LLM_ERROR"})

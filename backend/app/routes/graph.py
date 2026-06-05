from fastapi import APIRouter, HTTPException
from ..models.schemas import TopicRequest, GraphResponseSchema, ErrorResponse
from ..services import groq_service, graph_service

router = APIRouter()

@router.post('/generate-graph', response_model=GraphResponseSchema, responses={400: {"model": ErrorResponse}, 502:{"model": ErrorResponse}})
async def generate_graph(payload: TopicRequest):
    if not payload.topic or not payload.topic.strip():
        raise HTTPException(status_code=400, detail={"error": True, "message": "Missing topic", "code": "INVALID_TOPIC"})

    # Use graph_service to build/return graph
    try:
        graph = await graph_service.generate_graph(payload.topic)
        return graph
    except Exception as e:
        raise HTTPException(status_code=502, detail={"error": True, "message": str(e), "code": "LLM_ERROR"})

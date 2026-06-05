from fastapi import APIRouter, HTTPException
from ..models.schemas import ExpandNodeRequest, ExpandNodeResponse, ErrorResponse
from ..services import expansion_service

router = APIRouter()

@router.post('/expand-node', response_model=ExpandNodeResponse, responses={400:{'model': ErrorResponse}, 502:{'model': ErrorResponse}})
async def expand_node(payload: ExpandNodeRequest):
    if not payload.node_id:
        raise HTTPException(status_code=400, detail={'error':True,'message':'Missing node_id','code':'MISSING_NODE_ID'})
    try:
        res = await expansion_service.expand_node(payload.node_id, payload.current_depth)
        return res
    except Exception as e:
        raise HTTPException(status_code=502, detail={"error": True, "message": str(e), "code": "LLM_ERROR"})

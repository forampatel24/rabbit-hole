import logging
from fastapi import APIRouter, HTTPException
from ..models.schemas import ExpandNodeRequest, ExpandNodeResponse
from ..services.expansion_service import ExpansionService
from ..services.groq_service import RateLimitError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["expansion"])

expansion_service = ExpansionService()


@router.post("/expand-node", response_model=ExpandNodeResponse)
async def expand_node(request: ExpandNodeRequest):
    logger.info(f"Received expansion request for node: {request.node_id}")

    try:
        if not request.node_id or not request.node_id.strip():
            raise HTTPException(status_code=400, detail="Node ID cannot be empty")

        response = expansion_service.expand_node(
            request.node_id,
            request.current_depth,
            []
        )

        logger.info(f"Successfully expanded node: {request.node_id}")
        return response

    except HTTPException:
        raise
    except RateLimitError as e:
        logger.warning(f"Rate limited: {str(e)}")
        raise HTTPException(status_code=429, detail="API rate limit exceeded. Please wait a moment and try again.")
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in expansion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to expand node")

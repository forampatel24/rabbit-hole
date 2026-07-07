"""
Graph generation routes
"""

import logging
from fastapi import APIRouter, HTTPException
from ..models.schemas import TopicRequest, GraphResponse, ErrorResponse
from ..services.graph_service import GraphService
from ..services.groq_service import RateLimitError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["graph"])

# Initialize service
graph_service = GraphService()


@router.post("/generate-graph", response_model=GraphResponse)
async def generate_graph(request: TopicRequest):
    logger.info(f"Received graph generation request for topic: {request.topic} mode: {request.mode}")

    try:
        if not request.topic or not request.topic.strip():
            logger.warning("Empty topic provided")
            raise HTTPException(status_code=400, detail="Topic cannot be empty")

        valid_modes = {"learn", "interview", "project", "research", "quick"}
        mode = request.mode if request.mode in valid_modes else "learn"

        logger.info(f"Generating graph for topic: {request.topic} mode: {mode}")
        response = graph_service.generate_graph(request.topic, mode)

        logger.info(f"Successfully generated graph with {len(response.graph.nodes)} nodes and {len(response.graph.edges)} edges")
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
        logger.error(f"Unexpected error in graph generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate graph")


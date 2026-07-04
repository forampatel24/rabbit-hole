import logging
from fastapi import APIRouter, HTTPException
from ..models.schemas import KnowledgeGapRequest, KnowledgeGapResponse
from ..services.knowledge_gap_service import KnowledgeGapService
from ..services.groq_service import RateLimitError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["knowledge_gap"])

knowledge_gap_service = KnowledgeGapService()


@router.post("/knowledge-gap", response_model=KnowledgeGapResponse)
async def analyze_knowledge_gap(request: KnowledgeGapRequest):
    logger.info(f"Received knowledge gap request for target: {request.target_topic}")

    try:
        if not request.target_topic or not request.target_topic.strip():
            raise HTTPException(status_code=400, detail="Target topic cannot be empty")

        response = knowledge_gap_service.analyze_gap(
            request.known_concepts,
            request.target_topic
        )

        logger.info("Knowledge gap analysis completed successfully")
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
        logger.error(f"Unexpected error in knowledge gap analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to analyze knowledge gap")

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from urllib.parse import unquote

from ..database import get_db
from ..models.schemas import LearningResourcesResponse
from ..services.resource_service import ResourceService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["resources"])

resource_service = ResourceService()


@router.get("/resources/{concept_name}", response_model=LearningResourcesResponse)
async def get_resources(concept_name: str, db: Session = Depends(get_db)):
    decoded_name = unquote(concept_name).strip()
    if not decoded_name:
        raise HTTPException(status_code=400, detail="Concept name cannot be empty")

    logger.info(f"Resource request for concept: {decoded_name}")
    try:
        resources = await resource_service.get_resources(decoded_name, db)
        return LearningResourcesResponse(**resources)
    except Exception as e:
        logger.error(f"Failed to fetch resources for '{decoded_name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch resources: {str(e)}")

"""
Health check route
"""

import logging
from fastapi import APIRouter
from ..models.schemas import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns:
        HealthResponse with status
    """
    logger.info("Health check requested")
    return HealthResponse(status="healthy", service="rabbit-hole-api")


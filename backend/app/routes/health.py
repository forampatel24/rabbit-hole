from fastapi import APIRouter
from ..models.schemas import HealthResponse

router = APIRouter()

@router.get('/health', response_model=HealthResponse)
async def health():
    return {"status": "healthy", "service": "rabbit-hole-api"}

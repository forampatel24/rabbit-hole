"""
RabbitHole Backend - FastAPI Application
AI-powered knowledge exploration platform
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import health, graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RabbitHole API",
    description="AI-powered knowledge exploration platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health.router)
app.include_router(graph.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {"message": "RabbitHole API v1.0.0"}


# Life cycle events
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("RabbitHole API starting up...")
    logger.info("API endpoints: GET /api/v1/health, POST /api/v1/generate-graph")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("RabbitHole API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




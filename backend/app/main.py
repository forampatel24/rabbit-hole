from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from backend/.env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.routes.health import router as health_router
from app.routes.graph import router as graph_router
from app.routes.expansion import router as expansion_router
from app.routes.knowledge_gap import router as knowledge_gap_router

app = FastAPI(title="rabbit-hole-api", version="1.0.0")

# Configure CORS
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api/v1
app.include_router(health_router, prefix="/api/v1")
app.include_router(graph_router, prefix="/api/v1")
app.include_router(expansion_router, prefix="/api/v1")
app.include_router(knowledge_gap_router, prefix="/api/v1")

# Expose app variable for uvicorn


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

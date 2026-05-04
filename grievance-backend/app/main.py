"""
FastAPI application entry point for Grievance Backend

This module initializes the FastAPI app and registers route routers
for both user and authority endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import user_routes, authority_routes
from app.config import settings


# Initialize FastAPI app with Phase 2 metadata
app = FastAPI(
    title="Grievance API",
    description="Shared backend for User and Authority applications",
    version="1.0",
)


# Configure CORS for frontend development URLs
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Basic root endpoint retained from Phase 1."""
    return {"message": "Grievance backend is running"}


@app.get("/health")
async def health():
    """Standard health check endpoint for orchestration checks."""
    return {"status": "ok"}


# Include routers for different client types (do not remove)
app.include_router(
    user_routes.router,
    prefix="/api/user",
    tags=["User"],
)

app.include_router(
    authority_routes.router,
    prefix="/api/authority",
    tags=["Authority"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

"""
FastAPI application entry point for Grievance Backend.

This module initializes the FastAPI app and registers legacy as well as
JanSetu-style v1 route routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import user_routes, authority_routes, auth, grievances, officer, ws
from app.api.v1 import auth as v1_auth
from app.api.v1 import authority as v1_authority
from app.api.v1 import grievances as v1_grievances
from app.api.v1 import officer as v1_officer
from app.api.v1 import users as v1_users
from app.api.v1 import ws as v1_ws
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


# Phase 5: Include auth and grievance route contracts (mock responses)
app.include_router(auth.router)
app.include_router(grievances.router)

# Officer dashboard and websocket integration (Phase 8)
app.include_router(officer.router)
app.include_router(ws.router)

# JanSetu v1 route layer (safe scaffold, legacy routes remain available)
app.include_router(v1_auth.router)
app.include_router(v1_users.router)
app.include_router(v1_authority.router)
app.include_router(v1_grievances.router)
app.include_router(v1_officer.router)
app.include_router(v1_ws.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

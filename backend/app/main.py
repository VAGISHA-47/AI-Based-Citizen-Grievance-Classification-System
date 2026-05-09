"""FastAPI application entry point for Grievance Backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import user_routes, authority_routes, auth, grievances, officer, ws


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
    "http://127.0.0.1:8000",
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
    return {"message": "JanSetu Grievance API", "version": "1.0", "status": "running"}


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

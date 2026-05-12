"""FastAPI application entry point for JanSetu Grievance Backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import user_routes, authority_routes, auth, grievances, officer, ws
from app.api.complaints import router as complaints_router
from app.api.locations import router as locations_router
from app.api.officers_v1 import router as officers_v1_router
from app.db.supabase_client import ping_supabase


app = FastAPI(
    title="JanSetu Grievance API",
    description="Shared backend for Citizen and Officer applications",
    version="2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jansetu-five.vercel.app",  # Production Vercel frontend
        "http://localhost:5173",             # Local dev (Vite frontend)
        "http://localhost:5000",             # Local dev (alternative port)
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await ping_supabase()


@app.get("/")
async def root():
    return {"message": "JanSetu Grievance API", "version": "2.0", "status": "running"}


@app.get("/health")
@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "timestamp": __import__("datetime").datetime.utcnow().isoformat()}


# ── User / Authority base routes ───────────────────────────────────────────
app.include_router(user_routes.router, prefix="/api/user", tags=["User"])
app.include_router(authority_routes.router, prefix="/api/authority", tags=["Authority"])

# ── Auth: legacy /auth/* + v1 /api/v1/auth/* ──────────────────────────────
app.include_router(auth.router)
app.include_router(auth.router_v1)

# ── Complaints / Grievances ────────────────────────────────────────────────
app.include_router(grievances.router)
app.include_router(complaints_router)

# ── Officer dashboard (legacy + v1) ────────────────────────────────────────
app.include_router(officer.router)
app.include_router(officers_v1_router)

# ── WebSocket ──────────────────────────────────────────────────────────────
app.include_router(ws.router)

# ── Locations ──────────────────────────────────────────────────────────────
app.include_router(locations_router)


# ── Grievance queue alias (used by Queue.jsx) ─────────────────────────────
@app.get("/grievances/queue")
async def grievances_queue():
    """Officer complaint queue — public alias used by frontend."""
    from app.db.supabase_client import supabase
    try:
        r = supabase.table("complaints").select("*").not_.in_(
            "status", ["resolved", "closed"]
        ).order("created_at", desc=True).limit(50).execute()
        return r.data or []
    except Exception:
        return []


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

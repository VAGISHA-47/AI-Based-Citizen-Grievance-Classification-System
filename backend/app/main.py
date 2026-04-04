import logging

import nltk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import admin, auth_routes, complaints

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Grievance Classification API",
    description="AI-Based Citizen Grievance Classification System",
    version="1.0.0",
)

# ── CORS (open for development) ───────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_routes.router, prefix="/api")
app.include_router(complaints.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created / verified.")
    for resource in ("punkt", "punkt_tab", "stopwords", "wordnet"):
        try:
            nltk.download(resource, quiet=True)
        except Exception as exc:
            logger.warning("NLTK download failed for '%s': %s", resource, exc)


# ── Health & root endpoints ───────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Grievance Classification API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

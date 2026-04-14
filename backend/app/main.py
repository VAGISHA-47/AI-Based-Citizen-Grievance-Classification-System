from fastapi import FastAPI

from app.api.routes import auth, grievances
from app.core.config import settings
from app.db.database import Base, engine

# Import models before create_all so SQLAlchemy metadata is populated.
from app.models import grievance, user  # noqa: F401


app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(grievances.router, prefix=settings.api_v1_prefix)

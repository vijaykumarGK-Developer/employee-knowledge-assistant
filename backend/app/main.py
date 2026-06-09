from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.api.deps import get_current_user, require_admin
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.chats import router as chats_router
from app.api.analytics import router as analytics_router
from app import models  # noqa: F401 — registers all models for create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(chats_router)
app.include_router(analytics_router)


@app.get("/api/health")
def health_check(db=Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "app": settings.APP_NAME, "database": db_status}


@app.get("/api/admin/check")
def admin_check(_: User = Depends(require_admin)):
    return {"status": "authorized", "role": "admin"}

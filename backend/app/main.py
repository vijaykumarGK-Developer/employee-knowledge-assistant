from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.deps import get_current_user, require_admin
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.chats import router as chats_router
from app.api.analytics import router as analytics_router
from app.models.user import User

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(chats_router)
app.include_router(analytics_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/api/admin/check")
def admin_check(_: User = Depends(require_admin)):
    return {"status": "authorized", "role": "admin"}

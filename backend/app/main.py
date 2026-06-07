from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.deps import get_current_user, require_admin
from app.models.user import User

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/api/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role}


@app.get("/api/admin/check")
def admin_check(_: User = Depends(require_admin)):
    return {"status": "authorized", "role": "admin"}

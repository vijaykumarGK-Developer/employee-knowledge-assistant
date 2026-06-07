from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    title: str
    file_type: str
    department: str
    uploaded_by: str
    version: int
    uploaded_at: datetime
    is_active: bool
    processing_status: str = "pending"
    processing_error: str | None = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int

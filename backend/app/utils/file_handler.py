import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "csv", "xlsx", "pptx"}


def validate_file(file: UploadFile) -> None:
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"File type '{ext}' not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB",
        )


def save_file(file: UploadFile, department: str = "all") -> dict:
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "bin"
    upload_dir = Path(settings.UPLOAD_DIR) / department
    upload_dir.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = upload_dir / unique_name
    content = file.file.read()
    file_path.write_bytes(content)
    return {
        "file_path": str(file_path),
        "file_size": len(content),
        "file_type": ext,
        "original_name": file.filename,
    }

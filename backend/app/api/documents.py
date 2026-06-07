from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, require_admin
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.utils.file_handler import validate_file, save_file

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    department: str = Form("all"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> DocumentResponse:
    validate_file(file)
    file_info = save_file(file, department)
    doc = Document(
        title=title,
        file_type=file_info["file_type"],
        file_path=file_info["file_path"],
        department=department,
        uploaded_by=admin.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return DocumentResponse.model_validate(doc)


@router.get("/", response_model=DocumentListResponse)
def list_documents(
    department: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentListResponse:
    query = db.query(Document).filter(Document.is_active == True)
    if current_user.role != "admin":
        query = query.filter(
            (Document.department == current_user.department) | (Document.department == "all")
        )
    elif department:
        query = query.filter(Document.department == department)
    items = query.order_by(Document.uploaded_at.desc()).all()
    return DocumentListResponse(items=[DocumentResponse.model_validate(d) for d in items], total=len(items))


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    doc = db.query(Document).filter(Document.id == doc_id, Document.is_active == True).first()
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    if current_user.role != "admin" and doc.department not in (current_user.department, "all"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")
    return DocumentResponse.model_validate(doc)


@router.delete("/{doc_id}")
def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    doc = db.query(Document).filter(Document.id == doc_id, Document.is_active == True).first()
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    doc.is_active = False
    db.commit()
    return {"status": "deleted"}


@router.post("/{doc_id}/reprocess", response_model=DocumentResponse)
def reprocess_document(
    doc_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> DocumentResponse:
    doc = db.query(Document).filter(Document.id == doc_id, Document.is_active == True).first()
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    doc.version += 1
    db.commit()
    db.refresh(doc)
    return DocumentResponse.model_validate(doc)

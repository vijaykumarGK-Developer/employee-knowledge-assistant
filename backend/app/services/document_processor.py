from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.document import Document
from app.services.extractors import extract_text
from app.services.chunker import chunk_document


def process_document(doc_id: str) -> None:
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return

        doc.processing_status = "processing"
        db.commit()

        pages = extract_text(doc.file_path, doc.file_type)
        chunks = chunk_document(pages, doc.id)

        # Block 6 will add: generate embeddings + store in ChromaDB
        # For now, we just mark as completed
        doc.processing_status = "completed"
        doc.processing_error = None
        db.commit()

    except Exception as e:
        db.rollback()
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.processing_status = "failed"
            doc.processing_error = str(e)
            db.commit()
    finally:
        db.close()

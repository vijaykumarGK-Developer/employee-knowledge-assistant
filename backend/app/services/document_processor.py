from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.document import Document
from app.services.extractors import extract_text
from app.services.chunker import chunk_document
from app.services.embeddings import generate_embeddings
from app.services.vector_store import add_document_chunks, delete_document_chunks


def process_document(doc_id: str, db: Session | None = None) -> None:
    own_session = db is None
    if db is None:
        db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return

        doc.processing_status = "processing"
        db.commit()

        pages = extract_text(doc.file_path, doc.file_type)
        chunks = chunk_document(pages, doc.id)

        if not chunks:
            doc.processing_status = "completed"
            doc.processing_error = None
            db.commit()
            return

        texts = [c["text"] for c in chunks]
        embeddings = generate_embeddings(texts)

        add_document_chunks(chunks, embeddings, doc.title, doc.department)

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
        if own_session:
            db.close()


def reprocess_document(doc_id: str, db: Session | None = None) -> None:
    try:
        delete_document_chunks(doc_id)
    except Exception:
        pass
    process_document(doc_id, db)

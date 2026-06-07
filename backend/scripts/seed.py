"""Seed the database with demo users and sample documents.

Usage from backend/ directory:
    python scripts/seed.py

Requires a running PostgreSQL database.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.document import Document
from app.models.chat import Chat
from app.models.message import Message
from app.models.analytics_event import AnalyticsEvent


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        admin = User(
            email="admin@company.com",
            password_hash=get_password_hash("admin123"),
            full_name="Admin User",
            role="admin",
            department="all",
        )
        hr_user = User(
            email="hr@company.com",
            password_hash=get_password_hash("hr123456"),
            full_name="HR Manager",
            role="employee",
            department="hr",
        )
        eng_user = User(
            email="engineer@company.com",
            password_hash=get_password_hash("eng12345"),
            full_name="Software Engineer",
            role="employee",
            department="engineering",
        )
        db.add_all([admin, hr_user, eng_user])
        db.commit()
        db.refresh(admin)
        db.refresh(hr_user)
        db.refresh(eng_user)

        sample_docs = [
            Document(
                title="Company Leave Policy 2025",
                file_type="pdf",
                file_path="sample_data/leave_policy.pdf",
                department="hr",
                uploaded_by=admin.id,
            ),
            Document(
                title="Health Insurance Benefits",
                file_type="pdf",
                file_path="sample_data/health_insurance.pdf",
                department="hr",
                uploaded_by=admin.id,
            ),
            Document(
                title="Engineering Onboarding Guide",
                file_type="docx",
                file_path="sample_data/onboarding.docx",
                department="engineering",
                uploaded_by=admin.id,
            ),
            Document(
                title="API Style Guide",
                file_type="txt",
                file_path="sample_data/api_style.txt",
                department="engineering",
                uploaded_by=admin.id,
            ),
            Document(
                title="Budget Planning 2025",
                file_type="csv",
                file_path="sample_data/budget.csv",
                department="finance",
                uploaded_by=admin.id,
            ),
            Document(
                title="Company Code of Conduct",
                file_type="pdf",
                file_path="sample_data/code_of_conduct.pdf",
                department="all",
                uploaded_by=admin.id,
            ),
        ]
        for doc in sample_docs:
            existing = db.query(Document).filter(Document.title == doc.title).first()
            if not existing:
                db.add(doc)
        db.commit()

        print("Seed data created successfully!")
        print(f"  Admin:     admin@company.com / admin123")
        print(f"  HR:        hr@company.com / hr123456")
        print(f"  Engineer:  engineer@company.com / eng12345")
        print(f"  Documents: {len(sample_docs)}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

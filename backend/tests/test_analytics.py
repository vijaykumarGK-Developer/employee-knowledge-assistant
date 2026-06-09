from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.analytics_event import AnalyticsEvent
from app.models.message import Message
from app.models.user import User
from app.models.document import Document


def test_analytics_overview(client: TestClient, admin_headers: dict, db: Session, sample_doc: str):
    res = client.get("/api/analytics/overview", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data
    assert "total_documents" in data
    assert data["total_users"] >= 1


def test_analytics_employee_forbidden(client: TestClient, user_headers: dict):
    res = client.get("/api/analytics/overview", headers=user_headers)
    assert res.status_code == 403


def test_analytics_popular_questions(client: TestClient, admin_headers: dict, db: Session):
    user = db.query(User).first()
    msg = Message(chat_id="fake-chat", role="user", content="What is policy?")
    db.add(msg)
    db.commit()

    res = client.get("/api/analytics/popular-questions", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_analytics_unanswered(client: TestClient, admin_headers: dict, db: Session):
    msg = Message(chat_id="fake-chat-2", role="assistant", content="I don't know", sources=None)
    db.add(msg)
    db.commit()

    res = client.get("/api/analytics/unanswered", headers=admin_headers)
    assert res.status_code == 200


def test_track_event(db: Session):
    from app.services.analytics_service import track_event
    user = db.query(User).first()
    track_event(db, "test_event", user_id=user.id if user else None, metadata={"key": "value"})
    count = db.query(AnalyticsEvent).filter(AnalyticsEvent.event_type == "test_event").count()
    assert count == 1

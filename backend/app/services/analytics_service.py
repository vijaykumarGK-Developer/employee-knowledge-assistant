from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analytics_event import AnalyticsEvent
from app.models.user import User
from app.models.document import Document
from app.models.message import Message


def track_event(
    db: Session,
    event_type: str,
    user_id: str | None = None,
    metadata: dict | None = None,
) -> None:
    event = AnalyticsEvent(
        event_type=event_type,
        user_id=user_id,
        event_metadata=metadata,
    )
    db.add(event)
    db.commit()


def get_overview_stats(db: Session) -> dict:
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_docs = db.query(func.count(Document.id)).filter(Document.is_active == True).scalar() or 0
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    questions_today = (
        db.query(func.count(Message.id))
        .filter(Message.role == "user", Message.created_at >= today_start)
        .scalar()
        or 0
    )
    unanswered = (
        db.query(func.count(Message.id))
        .filter(
            Message.role == "assistant",
            Message.sources.is_(None),
        )
        .scalar()
        or 0
    )
    total_questions = (
        db.query(func.count(Message.id)).filter(Message.role == "user").scalar() or 1
    )
    unanswered_pct = round((unanswered / total_questions) * 100, 1)
    return {
        "total_users": total_users,
        "total_documents": total_docs,
        "questions_today": questions_today,
        "unanswered_count": unanswered,
        "unanswered_percentage": unanswered_pct,
    }


def get_popular_questions(db: Session, limit: int = 10) -> list[dict]:
    rows = (
        db.query(Message.content, func.count(Message.id).label("count"))
        .filter(Message.role == "user")
        .group_by(Message.content)
        .order_by(func.count(Message.id).desc())
        .limit(limit)
        .all()
    )
    return [{"question": row.content, "count": row.count} for row in rows]


def get_unanswered_questions(db: Session) -> list[dict]:
    rows = (
        db.query(Message.content, Message.created_at)
        .filter(
            Message.role == "assistant",
            Message.sources.is_(None),
        )
        .order_by(Message.created_at.desc())
        .limit(50)
        .all()
    )
    return [{"content": row.content, "created_at": row.created_at.isoformat()} for row in rows]


def get_user_activity(db: Session, days: int = 30) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            func.date(AnalyticsEvent.created_at).label("date"),
            func.count(func.distinct(AnalyticsEvent.user_id)).label("active_users"),
        )
        .filter(AnalyticsEvent.created_at >= cutoff, AnalyticsEvent.event_type == "user_login")
        .group_by(func.date(AnalyticsEvent.created_at))
        .order_by(func.date(AnalyticsEvent.created_at))
        .all()
    )
    return [{"date": str(row.date), "active_users": row.active_users} for row in rows]

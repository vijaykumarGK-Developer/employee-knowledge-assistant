import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

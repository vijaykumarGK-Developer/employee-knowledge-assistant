"""initial

Revision ID: 001
Revises:
Create Date: 2026-06-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), server_default="employee"),
        sa.Column("department", sa.String(100), server_default="all"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("file_path", sa.Text, nullable=False),
        sa.Column("department", sa.String(100), server_default="all"),
        sa.Column("uploaded_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean, server_default="true"),
    )

    op.create_table(
        "chats",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), server_default="New Chat"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("chat_id", sa.String(36), sa.ForeignKey("chats.id"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("sources", JSONB, nullable=True),
        sa.Column("feedback", sa.Boolean, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "analytics_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("analytics_events")
    op.drop_table("messages")
    op.drop_table("chats")
    op.drop_table("documents")
    op.drop_table("users")

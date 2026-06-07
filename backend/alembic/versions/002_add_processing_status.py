"""add processing_status to documents

Revision ID: 002
Revises: 001
Create Date: 2026-06-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("processing_status", sa.String(20), server_default="pending"))
    op.add_column("documents", sa.Column("processing_error", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "processing_error")
    op.drop_column("documents", "processing_status")

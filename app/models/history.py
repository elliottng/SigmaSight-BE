"""
History tracking models for exports and data backfill progress
"""
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .users import User  # noqa: F401
    from .portfolio import Portfolio  # noqa: F401


class ExportHistory(Base):
    """
    Minimal audit trail for export operations.
    Tracks what was exported, when, and in what format.
    """
    __tablename__ = "export_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    export_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="Type of export: portfolio, trades, modeling_session"
    )
    export_format: Mapped[str] = mapped_column(
        String(10), 
        nullable=False,
        comment="Format: csv, json, fix"
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship()

    __table_args__ = (
        CheckConstraint(
            export_type.in_(['portfolio', 'trades', 'modeling_session']), 
            name='export_type_check'
        ),
        CheckConstraint(
            export_format.in_(['csv', 'json', 'fix']), 
            name='export_format_check'
        ),
    )



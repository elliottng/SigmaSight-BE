"""
Agent user preferences model
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, DateTime, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, Dict, Any
from app.database import Base
from app.core.datetime_utils import utc_now


class UserPreference(Base):
    """User preferences for agent interactions"""
    __tablename__ = "agent_user_preferences"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # User reference - no foreign key for clean separation
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)
    
    # Default mode preference
    default_mode: Mapped[str] = mapped_column(String(50), default="green", nullable=False)
    
    # Model preferences (can be overridden by admin)
    preferred_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Feature toggles
    code_interpreter_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    tool_calls_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    streaming_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # User context/primer (small text for cross-session memory)
    user_context: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    
    # Settings and metadata
    settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Indexes
    __table_args__ = (
        Index("idx_agent_user_preferences_user_id", "user_id"),
    )
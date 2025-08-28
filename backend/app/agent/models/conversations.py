"""
Agent conversation and message models
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Dict, Any
from app.database import Base
from app.core.datetime_utils import utc_now


class Conversation(Base):
    """Conversation model - stores agent conversation sessions"""
    __tablename__ = "agent_conversations"
    
    # Our canonical ID - returned as conversation_id to frontend
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # User reference - no foreign key for clean separation
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    
    # Mode: green|blue|indigo|violet
    mode: Mapped[str] = mapped_column(String(50), default="green", nullable=False)
    
    # Provider tracking (vendor-agnostic)
    provider: Mapped[str] = mapped_column(String(32), default="openai", nullable=False)
    provider_thread_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # OpenAI thread ID if using Assistants
    provider_run_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)     # OpenAI run ID if applicable
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Metadata for model version, settings, etc.
    meta_data: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    
    # Relationships
    messages: Mapped[List["ConversationMessage"]] = relationship(
        "ConversationMessage", 
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_agent_conversations_user_id", "user_id"),
        Index("idx_agent_conversations_created_at", "created_at"),
        Index("idx_agent_conversations_provider_thread_id", "provider_thread_id"),
    )


class ConversationMessage(Base):
    """Conversation message model - stores individual messages in a conversation"""
    __tablename__ = "agent_messages"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("agent_conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Role: 'user', 'assistant', 'system', 'tool'
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Content - can be null for tool-only responses
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Tool calls and results
    tool_calls: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    
    # Performance metrics
    first_token_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Time to first SSE token
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)      # Total response time
    
    # Token tracking
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Provider tracking
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # OpenAI message ID
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    
    # Error tracking
    error: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index("idx_agent_messages_conversation_id", "conversation_id"),
        Index("idx_agent_messages_created_at", "created_at"),
    )
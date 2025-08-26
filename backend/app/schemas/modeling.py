"""
Schemas for modeling session operations
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import Field, validator

from .base import BaseSchema, TimestampedSchema


class ModelingSessionCreate(BaseSchema):
    """Request schema for creating a new modeling session"""
    name: str = Field(..., min_length=1, max_length=255)
    portfolio_id: UUID


class ModelingSessionUpdate(BaseSchema):
    """Request schema for updating a modeling session"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern="^(active|completed|cancelled)$")
    modified_portfolio_snapshot: Optional[Dict[str, Any]] = None
    changes: Optional[List[Dict[str, Any]]] = None
    impact_summary: Optional[Dict[str, Any]] = None
    
    @validator('changes')
    def validate_changes(cls, v):
        """Ensure changes have required fields"""
        if v is not None:
            for change in v:
                if 'action' not in change or 'symbol' not in change:
                    raise ValueError("Each change must have 'action' and 'symbol' fields")
        return v


class ModelingSessionInDB(TimestampedSchema):
    """Database representation of a modeling session"""
    id: UUID
    session_id: str
    user_id: UUID
    name: str
    status: str
    base_portfolio_snapshot: Dict[str, Any]
    modified_portfolio_snapshot: Optional[Dict[str, Any]] = None
    changes: Optional[List[Dict[str, Any]]] = None
    impact_summary: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None


class ModelingSessionResponse(ModelingSessionInDB):
    """API response for modeling session"""
    pass  # Same as InDB for now, but allows future customization


class ModelingSessionListResponse(BaseSchema):
    """Response for listing modeling sessions"""
    sessions: List[ModelingSessionResponse]
    total: int

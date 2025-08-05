"""
Schemas for export history and backfill progress
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import Field

from .base import BaseSchema, TimestampedSchema


class ExportHistoryCreate(BaseSchema):
    """Request schema for recording an export"""
    export_type: str = Field(..., pattern="^(portfolio|trades|modeling_session)$")
    export_format: str = Field(..., pattern="^(csv|json|fix)$")
    file_name: str = Field(..., min_length=1, max_length=255)
    file_size_bytes: Optional[int] = Field(None, ge=0)


class ExportHistoryInDB(BaseSchema):
    """Database representation of export history"""
    id: UUID
    user_id: Optional[UUID] = None
    export_type: str
    export_format: str
    file_name: str
    file_size_bytes: Optional[int] = None
    created_at: datetime


class ExportHistoryResponse(ExportHistoryInDB):
    """API response for export history"""
    pass



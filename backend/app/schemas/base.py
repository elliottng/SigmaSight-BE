"""
Base schema classes for common patterns
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.core.datetime_utils import to_utc_iso8601


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,  # Support ORM model conversion
        str_strip_whitespace=True,  # Auto-strip strings
        use_enum_values=True,  # Use enum values not names
        json_encoders={
            datetime: lambda v: to_utc_iso8601(v),  # Standardized UTC ISO 8601 with Z suffix
            UUID: lambda v: str(v) if v else None,
        }
    )


class TimestampedSchema(BaseSchema):
    """Schema with timestamp fields"""
    created_at: datetime
    updated_at: Optional[datetime] = None

"""
Base schema for Agent modules
"""
from pydantic import BaseModel, ConfigDict
from app.core.datetime_utils import to_utc_iso8601
from datetime import datetime
from uuid import UUID


class AgentBaseSchema(BaseModel):
    """Base schema with common configuration for Agent modules"""
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: to_utc_iso8601(v),
            UUID: lambda v: str(v) if v else None,
        }
    )
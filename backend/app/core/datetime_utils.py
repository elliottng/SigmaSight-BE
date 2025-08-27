"""
Datetime utility functions for UTC ISO 8601 standardization.

This module provides consistent datetime formatting across the application
to ensure all API responses use UTC ISO 8601 format with 'Z' suffix.

Author: SigmaSight Team
Date: 2025-08-27
"""

from datetime import datetime, date, timezone
from typing import Optional, Any, Dict, Union, List
import re


def utc_now() -> datetime:
    """
    Get current UTC time.
    
    This function should replace all instances of datetime.now() in the codebase
    to ensure consistent UTC timezone usage.
    
    Returns:
        datetime: Current UTC datetime object (timezone-naive)
    """
    return datetime.utcnow()


def utc_now_iso8601() -> str:
    """
    Get current UTC time as ISO 8601 string with Z suffix.
    
    Returns:
        str: Current UTC time in format: YYYY-MM-DDTHH:MM:SS.sssZ
        
    Example:
        >>> utc_now_iso8601()
        '2025-08-27T10:30:45.123456Z'
    """
    return datetime.utcnow().isoformat() + "Z"


def to_utc_iso8601(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert any datetime to UTC ISO 8601 format with Z suffix.
    
    Handles:
    - None values (returns None)
    - Naive datetimes (assumes UTC)
    - Timezone-aware datetimes (converts to UTC)
    - Already UTC datetimes
    
    Args:
        dt: Datetime object to convert (can be None, naive, or timezone-aware)
        
    Returns:
        Optional[str]: ISO 8601 formatted string with Z suffix, or None
        
    Examples:
        >>> to_utc_iso8601(datetime(2025, 8, 27, 10, 30, 45))
        '2025-08-27T10:30:45Z'
        
        >>> to_utc_iso8601(None)
        None
    """
    if dt is None:
        return None
    
    # If naive datetime, assume it's already UTC
    if dt.tzinfo is None:
        return dt.isoformat() + "Z"
    
    # If timezone-aware, convert to UTC
    if dt.tzinfo == timezone.utc:
        # Already UTC, just format
        return dt.replace(tzinfo=None).isoformat() + "Z"
    else:
        # Convert to UTC first
        utc_dt = dt.astimezone(timezone.utc)
        return utc_dt.replace(tzinfo=None).isoformat() + "Z"


def to_iso_date(d: Optional[date]) -> Optional[str]:
    """
    Convert date to ISO 8601 date string.
    
    Args:
        d: Date object to convert (can be None)
        
    Returns:
        Optional[str]: ISO 8601 date string YYYY-MM-DD, or None
        
    Example:
        >>> to_iso_date(date(2025, 8, 27))
        '2025-08-27'
    """
    return d.isoformat() if d else None


def parse_iso8601(iso_string: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO 8601 string to datetime object.
    
    Handles various ISO 8601 formats:
    - With Z suffix: 2025-08-27T10:30:45Z
    - With timezone offset: 2025-08-27T10:30:45+00:00
    - Without timezone: 2025-08-27T10:30:45 (assumes UTC)
    
    Args:
        iso_string: ISO 8601 formatted string
        
    Returns:
        Optional[datetime]: Parsed datetime object (naive, in UTC), or None
    """
    if not iso_string:
        return None
    
    # Remove 'Z' suffix if present
    if iso_string.endswith('Z'):
        iso_string = iso_string[:-1] + '+00:00'
    
    try:
        # Try parsing with timezone
        if '+' in iso_string or iso_string.count('-') > 2:
            dt = datetime.fromisoformat(iso_string)
            # Convert to UTC if needed
            if dt.tzinfo and dt.tzinfo != timezone.utc:
                dt = dt.astimezone(timezone.utc)
            # Return as naive UTC
            return dt.replace(tzinfo=None)
        else:
            # Parse as naive, assume UTC
            return datetime.fromisoformat(iso_string)
    except (ValueError, AttributeError):
        return None


def standardize_datetime_field(value: Any) -> Any:
    """
    Standardize a single datetime field value.
    
    Args:
        value: Field value (could be datetime, date, string, or any other type)
        
    Returns:
        Any: Standardized value (ISO 8601 string if datetime/date, unchanged otherwise)
    """
    if isinstance(value, datetime):
        return to_utc_iso8601(value)
    elif isinstance(value, date):
        return to_iso_date(value)
    elif isinstance(value, str):
        # Check if it looks like a datetime with timezone offset
        if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*\+00:00$', value):
            # Convert +00:00 to Z
            return value.replace('+00:00', 'Z')
    return value


def standardize_datetime_dict(data: Dict[str, Any], depth: int = 10) -> Dict[str, Any]:
    """
    Recursively standardize all datetime fields in a dictionary.
    
    Detects and converts:
    - datetime objects to ISO 8601 with Z suffix
    - date objects to ISO 8601 date format
    - Strings with +00:00 to Z suffix
    - Nested dictionaries and lists
    
    Args:
        data: Dictionary to process
        depth: Maximum recursion depth (default 10, prevents infinite recursion)
        
    Returns:
        Dict[str, Any]: New dictionary with standardized datetime fields
        
    Example:
        >>> data = {
        ...     'created_at': datetime(2025, 8, 27, 10, 30),
        ...     'date': date(2025, 8, 27),
        ...     'nested': {'updated_at': datetime(2025, 8, 27, 11, 0)}
        ... }
        >>> standardize_datetime_dict(data)
        {
            'created_at': '2025-08-27T10:30:00Z',
            'date': '2025-08-27',
            'nested': {'updated_at': '2025-08-27T11:00:00Z'}
        }
    """
    if depth <= 0:
        return data
    
    result = {}
    
    for key, value in data.items():
        if isinstance(value, dict):
            # Recursively process nested dictionaries
            result[key] = standardize_datetime_dict(value, depth - 1)
        elif isinstance(value, list):
            # Process lists (might contain dicts with datetimes)
            result[key] = standardize_datetime_list(value, depth - 1)
        else:
            # Standardize the field value
            result[key] = standardize_datetime_field(value)
    
    return result


def standardize_datetime_list(data: List[Any], depth: int = 10) -> List[Any]:
    """
    Recursively standardize all datetime fields in a list.
    
    Args:
        data: List to process
        depth: Maximum recursion depth
        
    Returns:
        List[Any]: New list with standardized datetime fields
    """
    if depth <= 0:
        return data
    
    result = []
    
    for item in data:
        if isinstance(item, dict):
            result.append(standardize_datetime_dict(item, depth - 1))
        elif isinstance(item, list):
            result.append(standardize_datetime_list(item, depth - 1))
        else:
            result.append(standardize_datetime_field(item))
    
    return result


def is_datetime_field(field_name: str) -> bool:
    """
    Check if a field name suggests it contains a datetime value.
    
    Used for intelligent field detection in standardization.
    
    Args:
        field_name: Name of the field
        
    Returns:
        bool: True if field name suggests datetime content
    """
    datetime_patterns = [
        '_at', '_date', '_time', 'timestamp', 'created', 'updated', 
        'modified', 'deleted', 'start', 'end', 'expiry', 'expiration'
    ]
    
    field_lower = field_name.lower()
    return any(pattern in field_lower for pattern in datetime_patterns)


def validate_iso8601_format(value: str) -> bool:
    """
    Validate if a string is in proper ISO 8601 format with Z suffix.
    
    Args:
        value: String to validate
        
    Returns:
        bool: True if valid ISO 8601 with Z suffix
        
    Example:
        >>> validate_iso8601_format('2025-08-27T10:30:45.123456Z')
        True
        >>> validate_iso8601_format('2025-08-27T10:30:45+00:00')
        False
    """
    # Pattern for ISO 8601 with Z suffix
    iso8601_z_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$'
    return bool(re.match(iso8601_z_pattern, value))


def ensure_utc_datetime(dt: datetime) -> datetime:
    """
    Ensure a datetime is in UTC timezone (naive).
    
    Args:
        dt: Datetime object (can be naive or timezone-aware)
        
    Returns:
        datetime: Naive datetime in UTC
    """
    if dt.tzinfo is None:
        # Assume naive datetime is already UTC
        return dt
    elif dt.tzinfo == timezone.utc:
        # Already UTC, just make naive
        return dt.replace(tzinfo=None)
    else:
        # Convert to UTC and make naive
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
"""
Central tool registry with dispatch and uniform envelope handling.
Implements the ultra-thin handler pattern with validation, dispatch, and wrapping.
"""
from typing import Dict, Callable, Any, Optional, List
from uuid import uuid4
from datetime import datetime
import logging
from pydantic import BaseModel, ValidationError

from app.core.datetime_utils import utc_now, to_utc_iso8601
from app.agent.tools.handlers import PortfolioTools

logger = logging.getLogger(__name__)


# Pydantic models for tool inputs/outputs
class ToolRequest(BaseModel):
    """Base model for tool requests"""
    tool_name: str
    arguments: Dict[str, Any]
    request_id: Optional[str] = None
    
    def __init__(self, **data):
        if 'request_id' not in data or not data['request_id']:
            data['request_id'] = str(uuid4())
        super().__init__(**data)


class MetaInfo(BaseModel):
    """Meta information for all tool responses"""
    requested: Dict[str, Any]
    applied: Dict[str, Any]
    as_of: str
    truncated: bool = False
    limits: Dict[str, Any] = {}
    retryable: bool = False
    retries: int = 0
    cache_hit: bool = False
    request_id: Optional[str] = None


class ToolResponse(BaseModel):
    """Uniform envelope for all tool responses"""
    meta: MetaInfo
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class ToolRegistry:
    """
    Central registry for all tools with uniform dispatch and envelope handling.
    Implements the ultra-thin handler pattern.
    """
    
    def __init__(self, tools: Optional[PortfolioTools] = None, auth_token: Optional[str] = None):
        """
        Initialize the tool registry.
        
        Args:
            tools: PortfolioTools instance (will create if not provided)
            auth_token: Bearer token for API authentication
        """
        self.tools = tools or PortfolioTools(auth_token=auth_token)
        self.auth_token = auth_token
        
        # Registry mapping tool names to methods
        self.registry: Dict[str, Callable] = {
            "get_portfolio_complete": self.tools.get_portfolio_complete,
            "get_positions_details": self.tools.get_positions_details,
            "get_prices_historical": self.tools.get_prices_historical,
            "get_current_quotes": self.tools.get_current_quotes,
            "get_portfolio_data_quality": self.tools.get_portfolio_data_quality,
            "get_factor_etf_prices": self.tools.get_factor_etf_prices,
        }
        
    async def dispatch_tool_call(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        ctx: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Central dispatcher that validates, calls, and wraps tool responses.
        
        Args:
            tool_name: Name of the tool to execute
            payload: Tool arguments
            ctx: Optional context (user info, conversation id, etc.)
            
        Returns:
            Uniform envelope response with meta, data, and optional error
        """
        request_id = ctx.get("request_id") if ctx else str(uuid4())
        start_time = utc_now()
        
        try:
            # (a) Validate tool exists
            if tool_name not in self.registry:
                return self._format_error_envelope(
                    message=f"Unknown tool: {tool_name}",
                    requested_params=payload,
                    retryable=False,
                    error_type="validation_error",
                    request_id=request_id
                )
            
            # (b) Validate input with Pydantic (basic validation)
            try:
                request = ToolRequest(
                    tool_name=tool_name,
                    arguments=payload,
                    request_id=request_id
                )
            except ValidationError as e:
                return self._format_error_envelope(
                    message=f"Invalid arguments: {e}",
                    requested_params=payload,
                    retryable=False,
                    error_type="validation_error",
                    request_id=request_id
                )
            
            # (c) Call underlying tool
            handler = self.registry[tool_name]
            result = await handler(**payload)
            
            # Check if the result is an error
            if isinstance(result, dict) and "error" in result:
                return self._format_error_envelope(
                    message=result.get("error", "Unknown error"),
                    requested_params=payload,
                    retryable=result.get("retryable", False),
                    error_type="execution_error",
                    request_id=request_id
                )
            
            # (d) Wrap in uniform envelope
            return self._format_success_envelope(
                data=result,
                requested_params=payload,
                request_id=request_id
            )
            
        except Exception as e:
            logger.error(f"Error in dispatch_tool_call for {tool_name}: {e}")
            # (d) Map exceptions to error envelope
            return self._format_error_envelope(
                message=str(e),
                requested_params=payload,
                retryable=True,
                error_type="execution_error",
                request_id=request_id
            )
    
    def _format_success_envelope(
        self,
        data: Any,
        requested_params: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format successful response with uniform envelope.
        
        Args:
            data: Tool response data
            requested_params: Original request parameters
            request_id: Request ID for tracking
            
        Returns:
            Formatted response with meta and data
        """
        # Extract meta information from the response if available
        applied_params = requested_params.copy()
        truncated = False
        limits = {}
        
        if isinstance(data, dict):
            # Extract meta from response
            if "meta" in data:
                meta_data = data["meta"]
                applied_params = meta_data.get("applied", requested_params)
                truncated = meta_data.get("truncated", False)
                limits = meta_data.get("limits", {})
        
        return {
            "meta": {
                "requested": requested_params,
                "applied": applied_params,
                "as_of": to_utc_iso8601(utc_now()),
                "truncated": truncated,
                "limits": limits or {
                    "symbols_max": 5,
                    "lookback_days_max": 180,
                    "timeout_ms": 3000
                },
                "retryable": False,
                "retries": 0,
                "cache_hit": False,
                "request_id": request_id
            },
            "data": data,
            "error": None
        }
    
    def _format_error_envelope(
        self,
        message: str,
        requested_params: Dict[str, Any],
        retryable: bool = False,
        error_type: str = "execution_error",
        suggested_params: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format error response with uniform envelope.
        
        Args:
            message: Error message
            requested_params: Original request parameters
            retryable: Whether the request can be retried
            error_type: Type of error (validation_error, execution_error, etc.)
            suggested_params: Suggested parameters that might work
            request_id: Request ID for tracking
            
        Returns:
            Formatted error response
        """
        return {
            "meta": {
                "requested": requested_params,
                "applied": {},
                "as_of": to_utc_iso8601(utc_now()),
                "truncated": False,
                "limits": {
                    "symbols_max": 5,
                    "lookback_days_max": 180,
                    "timeout_ms": 3000
                },
                "retryable": retryable,
                "retries": 0,
                "cache_hit": False,
                "request_id": request_id
            },
            "data": None,
            "error": {
                "type": error_type,
                "message": message,
                "details": {
                    "suggested_params": suggested_params
                } if suggested_params else {}
            }
        }
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names.
        
        Returns:
            List of registered tool names
        """
        return list(self.registry.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool information or None if not found
        """
        if tool_name not in self.registry:
            return None
            
        # Return basic info about the tool
        return {
            "name": tool_name,
            "available": True,
            "handler": self.registry[tool_name].__name__
        }
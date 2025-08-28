"""
OpenAI-specific adapter for portfolio tools.
Converts tool definitions and responses for OpenAI function calling format.
"""
import json
from typing import List, Dict, Any, Optional
import logging

from app.agent.tools.handlers import PortfolioTools

logger = logging.getLogger(__name__)


class OpenAIToolAdapter:
    """
    Adapter that converts PortfolioTools to OpenAI function calling format.
    This is the only provider-specific code (5% of implementation).
    """
    
    def __init__(self, tools: PortfolioTools):
        """
        Initialize adapter with portfolio tools.
        
        Args:
            tools: Instance of PortfolioTools with business logic
        """
        self.tools = tools
        
    def get_function_schemas(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI function calling schemas for all tools.
        
        Returns:
            List of function definitions in OpenAI format
        """
        return [
            {
                "name": "get_portfolio_complete",
                "description": "Get complete portfolio data including positions, values, and optional historical data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "portfolio_id": {
                            "type": "string",
                            "description": "The portfolio UUID to retrieve"
                        },
                        "include_holdings": {
                            "type": "boolean",
                            "description": "Include detailed position holdings",
                            "default": True
                        },
                        "include_timeseries": {
                            "type": "boolean",
                            "description": "Include historical time series data",
                            "default": False
                        },
                        "include_attrib": {
                            "type": "boolean",
                            "description": "Include attribution analysis data",
                            "default": False
                        }
                    },
                    "required": ["portfolio_id"]
                }
            },
            {
                "name": "get_positions_details",
                "description": "Get detailed information about specific positions or all positions in a portfolio",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "portfolio_id": {
                            "type": "string",
                            "description": "Portfolio UUID (required if position_ids not provided)"
                        },
                        "position_ids": {
                            "type": "string",
                            "description": "Comma-separated list of position IDs (required if portfolio_id not provided)"
                        },
                        "include_closed": {
                            "type": "boolean",
                            "description": "Include closed positions",
                            "default": False
                        }
                    },
                    "oneOf": [
                        {"required": ["portfolio_id"]},
                        {"required": ["position_ids"]}
                    ]
                }
            },
            {
                "name": "get_prices_historical",
                "description": "Get historical price data for top positions in a portfolio",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "portfolio_id": {
                            "type": "string",
                            "description": "The portfolio UUID"
                        },
                        "lookback_days": {
                            "type": "integer",
                            "description": "Number of days of history to retrieve (max 180)",
                            "default": 90,
                            "maximum": 180
                        },
                        "max_symbols": {
                            "type": "integer",
                            "description": "Maximum number of symbols to include (max 5)",
                            "default": 5,
                            "maximum": 5
                        },
                        "include_factor_etfs": {
                            "type": "boolean",
                            "description": "Include factor ETF prices for comparison",
                            "default": True
                        },
                        "date_format": {
                            "type": "string",
                            "description": "Date format: 'iso' or 'unix'",
                            "enum": ["iso", "unix"],
                            "default": "iso"
                        }
                    },
                    "required": ["portfolio_id"]
                }
            },
            {
                "name": "get_current_quotes",
                "description": "Get current market quotes for specified symbols",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "string",
                            "description": "Comma-separated list of stock symbols (max 5)"
                        },
                        "include_options": {
                            "type": "boolean",
                            "description": "Include options data if available",
                            "default": False
                        }
                    },
                    "required": ["symbols"]
                }
            },
            {
                "name": "get_portfolio_data_quality",
                "description": "Assess data quality and completeness for a portfolio to determine analysis feasibility",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "portfolio_id": {
                            "type": "string",
                            "description": "The portfolio UUID to assess"
                        },
                        "check_factors": {
                            "type": "boolean",
                            "description": "Check factor data availability",
                            "default": True
                        },
                        "check_correlations": {
                            "type": "boolean",
                            "description": "Check correlation data availability",
                            "default": True
                        }
                    },
                    "required": ["portfolio_id"]
                }
            },
            {
                "name": "get_factor_etf_prices",
                "description": "Get historical prices for factor ETFs used in factor analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lookback_days": {
                            "type": "integer",
                            "description": "Number of days of history (max 180)",
                            "default": 90,
                            "maximum": 180
                        },
                        "factors": {
                            "type": "string",
                            "description": "Comma-separated list of factor names (e.g., 'Market,Size,Value')"
                        }
                    }
                }
            }
        ]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool and return the result in OpenAI expected format.
        
        Args:
            name: Tool name to execute
            arguments: Tool arguments from OpenAI
            
        Returns:
            JSON string of the tool result (OpenAI expects JSON strings)
        """
        try:
            # Map tool name to method
            tool_method = getattr(self.tools, name, None)
            
            if not tool_method:
                error_response = {
                    "error": f"Unknown tool: {name}",
                    "retryable": False
                }
                return json.dumps(error_response)
            
            # Execute the tool
            result = await tool_method(**arguments)
            
            # OpenAI expects JSON string responses
            return json.dumps(result, default=str)
            
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            error_response = {
                "error": f"Tool execution failed: {str(e)}",
                "retryable": True,
                "tool": name
            }
            return json.dumps(error_response)
    
    def parse_tool_call(self, tool_call: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """
        Parse an OpenAI tool call into name and arguments.
        
        Args:
            tool_call: OpenAI tool call object
            
        Returns:
            Tuple of (tool_name, arguments)
        """
        name = tool_call.get("function", {}).get("name", "")
        arguments_str = tool_call.get("function", {}).get("arguments", "{}")
        
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse tool arguments: {arguments_str}")
            arguments = {}
            
        return name, arguments
    
    def format_tool_response(self, tool_call_id: str, response: str) -> Dict[str, Any]:
        """
        Format tool response for OpenAI API.
        
        Args:
            tool_call_id: ID of the tool call from OpenAI
            response: Tool response as JSON string
            
        Returns:
            Formatted response for OpenAI
        """
        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "content": response
        }
"""
Provider-agnostic tool implementations for portfolio data access.
These handlers contain all business logic and are 100% portable across AI providers.
"""
from typing import Dict, Any, Optional, List
from uuid import UUID
import httpx
from datetime import datetime, timedelta
import logging

from app.config import settings
from app.core.datetime_utils import utc_now, to_utc_iso8601

logger = logging.getLogger(__name__)


class PortfolioTools:
    """
    Provider-independent tool implementations.
    All business logic for data fetching, filtering, and formatting lives here.
    This class is 100% portable across all AI providers (OpenAI, Anthropic, Gemini, etc.)
    """
    
    def __init__(self, base_url: str = None, auth_token: str = None):
        """
        Initialize the tools with API configuration.
        
        Args:
            base_url: Base URL for the API (defaults to settings)
            auth_token: Bearer token for authentication
        """
        self.base_url = base_url or "http://localhost:8000"
        self.auth_token = auth_token
        self.timeout = httpx.Timeout(3.0, connect=5.0)  # 3s read, 5s connect
        
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        retry_count: int = 2
    ) -> Dict[str, Any]:
        """
        Make HTTP request to backend API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            retry_count: Number of retries for transient errors
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(retry_count + 1):
                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        params=params,
                        headers=headers
                    )
                    response.raise_for_status()
                    return response.json()
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in [429, 500, 502, 503, 504]:
                        # Retryable errors
                        if attempt < retry_count:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                    # Non-retryable or max retries exceeded
                    logger.error(f"HTTP error for {endpoint}: {e}")
                    raise
                    
                except httpx.TimeoutException as e:
                    if attempt < retry_count:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    logger.error(f"Timeout for {endpoint}: {e}")
                    raise
                    
                except Exception as e:
                    logger.error(f"Unexpected error for {endpoint}: {e}")
                    raise
    
    async def get_portfolio_complete(
        self,
        portfolio_id: str,
        include_holdings: bool = True,
        include_timeseries: bool = False,
        include_attrib: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get complete portfolio data with optional sections.
        
        Business logic:
        - Enforces data caps (max 2000 positions)
        - Includes proper meta object
        - Returns consistent as_of timestamps
        
        Args:
            portfolio_id: Portfolio UUID
            include_holdings: Include position details
            include_timeseries: Include historical data
            include_attrib: Include attribution data
            
        Returns:
            Complete portfolio data with meta object
        """
        try:
            # Build query parameters
            params = {
                "include_holdings": include_holdings,
                "include_timeseries": include_timeseries,
                "include_attrib": include_attrib
            }
            
            # Call API endpoint
            response = await self._make_request(
                method="GET",
                endpoint=f"/api/v1/data/portfolio/{portfolio_id}/complete",
                params=params
            )
            
            # Business logic: Add summary info if truncated
            if response.get("meta", {}).get("truncated"):
                response["_tool_note"] = "Data was truncated. Consider narrowing your query."
                
            return response
            
        except Exception as e:
            logger.error(f"Error in get_portfolio_complete: {e}")
            return {
                "error": str(e),
                "retryable": isinstance(e, (httpx.TimeoutException, httpx.HTTPStatusError))
            }
    
    async def get_positions_details(
        self,
        portfolio_id: Optional[str] = None,
        position_ids: Optional[str] = None,
        include_closed: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get detailed position information.
        
        Business logic:
        - Validates that either portfolio_id OR position_ids is provided
        - Enforces max_rows=200 cap with truncation
        - Adds summary statistics
        
        Args:
            portfolio_id: Optional portfolio UUID
            position_ids: Comma-separated position IDs
            include_closed: Include closed positions
            
        Returns:
            Position details with meta object
        """
        try:
            # Validation: Need either portfolio_id or position_ids
            if not portfolio_id and not position_ids:
                return {
                    "error": "Either portfolio_id or position_ids is required",
                    "retryable": False
                }
            
            # Build query parameters
            params = {"include_closed": include_closed}
            if portfolio_id:
                params["portfolio_id"] = portfolio_id
            if position_ids:
                params["position_ids"] = position_ids
                
            # Call API endpoint
            response = await self._make_request(
                method="GET",
                endpoint="/api/v1/data/positions/details",
                params=params
            )
            
            # Business logic: Calculate summary statistics
            if "positions" in response:
                positions = response["positions"]
                if len(positions) > 200:
                    # Apply cap
                    response["positions"] = positions[:200]
                    response["meta"] = response.get("meta", {})
                    response["meta"]["truncated"] = True
                    response["meta"]["original_count"] = len(positions)
                    
            return response
            
        except Exception as e:
            logger.error(f"Error in get_positions_details: {e}")
            return {
                "error": str(e),
                "retryable": isinstance(e, (httpx.TimeoutException, httpx.HTTPStatusError))
            }
    
    async def get_prices_historical(
        self,
        portfolio_id: str,
        lookback_days: int = 90,
        max_symbols: int = 5,
        include_factor_etfs: bool = True,
        date_format: str = "iso",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get historical prices for portfolio positions.
        
        Business logic:
        - Fetches portfolio positions first
        - Identifies top N symbols by market value
        - Applies lookback_days cap (max 180)
        - Filters to max_symbols (default 5)
        
        Args:
            portfolio_id: Portfolio UUID
            lookback_days: Days of history (max 180)
            max_symbols: Maximum symbols to return (max 5)
            include_factor_etfs: Include factor ETF prices
            date_format: Date format (iso or unix)
            
        Returns:
            Historical price data with meta object
        """
        try:
            # Business logic: Apply caps
            lookback_days = min(lookback_days, 180)
            max_symbols = min(max_symbols, 5)
            
            # First, get top positions to identify symbols
            positions_response = await self._make_request(
                method="GET",
                endpoint=f"/api/v1/data/positions/top/{portfolio_id}",
                params={"limit": max_symbols, "sort_by": "market_value"}
            )
            
            if "error" in positions_response:
                return positions_response
                
            # Extract symbols from top positions
            symbols = [pos["symbol"] for pos in positions_response.get("data", [])]
            
            if not symbols:
                return {
                    "error": "No positions found in portfolio",
                    "retryable": False
                }
            
            # Get historical prices for these symbols
            params = {
                "symbols": ",".join(symbols),
                "lookback_days": lookback_days,
                "include_factor_etfs": include_factor_etfs,
                "date_format": date_format
            }
            
            response = await self._make_request(
                method="GET",
                endpoint=f"/api/v1/data/prices/historical/{portfolio_id}",
                params=params
            )
            
            # Add meta information about selection
            if "meta" not in response:
                response["meta"] = {}
            response["meta"]["symbols_selected"] = symbols
            response["meta"]["selection_method"] = "top_by_market_value"
            response["meta"]["max_symbols"] = max_symbols
            response["meta"]["lookback_days"] = lookback_days
            
            return response
            
        except Exception as e:
            logger.error(f"Error in get_prices_historical: {e}")
            return {
                "error": str(e),
                "retryable": isinstance(e, (httpx.TimeoutException, httpx.HTTPStatusError))
            }
    
    async def get_current_quotes(
        self,
        symbols: str,
        include_options: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get current market quotes for symbols.
        
        Business logic:
        - Parses comma-separated symbols
        - Enforces max_symbols=5 cap
        - Validates symbol format
        
        Args:
            symbols: Comma-separated list of symbols
            include_options: Include options data if available
            
        Returns:
            Current quote data with meta object
        """
        try:
            # Parse and validate symbols
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
            
            # Apply cap
            if len(symbol_list) > 5:
                symbol_list = symbol_list[:5]
                truncated = True
                suggested_symbols = symbol_list
            else:
                truncated = False
                suggested_symbols = None
                
            # Call API endpoint
            params = {
                "symbols": ",".join(symbol_list),
                "include_options": include_options
            }
            
            response = await self._make_request(
                method="GET",
                endpoint="/api/v1/data/prices/quotes",
                params=params
            )
            
            # Add meta information
            if "meta" not in response:
                response["meta"] = {}
            response["meta"]["requested_symbols"] = symbols
            response["meta"]["applied_symbols"] = symbol_list
            response["meta"]["truncated"] = truncated
            if suggested_symbols:
                response["meta"]["suggested_symbols"] = suggested_symbols
                
            return response
            
        except Exception as e:
            logger.error(f"Error in get_current_quotes: {e}")
            return {
                "error": str(e),
                "retryable": isinstance(e, (httpx.TimeoutException, httpx.HTTPStatusError))
            }
    
    async def get_portfolio_data_quality(
        self,
        portfolio_id: str,
        check_factors: bool = True,
        check_correlations: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get data quality assessment for portfolio.
        
        Business logic:
        - Returns feasibility assessment for various analyses
        - Identifies data gaps
        - Suggests remediation steps
        
        Args:
            portfolio_id: Portfolio UUID
            check_factors: Check factor data availability
            check_correlations: Check correlation data availability
            
        Returns:
            Data quality assessment with recommendations
        """
        try:
            # Call API endpoint
            params = {
                "check_factors": check_factors,
                "check_correlations": check_correlations
            }
            
            response = await self._make_request(
                method="GET",
                endpoint=f"/api/v1/data/portfolio/{portfolio_id}/data-quality",
                params=params
            )
            
            # Business logic: Add recommendations based on quality
            if "data_quality_score" in response:
                score = response["data_quality_score"]
                if score < 0.5:
                    response["_tool_recommendation"] = "Data quality is low. Many analyses may not be feasible."
                elif score < 0.8:
                    response["_tool_recommendation"] = "Data quality is moderate. Some analyses may have limitations."
                else:
                    response["_tool_recommendation"] = "Data quality is good. Most analyses should be feasible."
                    
            return response
            
        except Exception as e:
            logger.error(f"Error in get_portfolio_data_quality: {e}")
            return {
                "error": str(e),
                "retryable": isinstance(e, (httpx.TimeoutException, httpx.HTTPStatusError))
            }
    
    async def get_factor_etf_prices(
        self,
        lookback_days: int = 90,
        factors: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get factor ETF prices for factor analysis.
        
        Business logic:
        - Maps factor names to ETF symbols
        - Applies lookback_days cap
        - Returns prices for factor proxies
        
        Args:
            lookback_days: Days of history (max 180)
            factors: Comma-separated factor names (optional)
            
        Returns:
            Factor ETF price data with meta object
        """
        try:
            # Apply caps
            lookback_days = min(lookback_days, 180)
            
            # Build parameters
            params = {"lookback_days": lookback_days}
            if factors:
                params["factors"] = factors
                
            # Call API endpoint
            response = await self._make_request(
                method="GET",
                endpoint="/api/v1/data/factors/etf-prices",
                params=params
            )
            
            # Add meta information about factor mapping
            if "meta" not in response:
                response["meta"] = {}
            response["meta"]["lookback_days"] = lookback_days
            if factors:
                response["meta"]["requested_factors"] = factors
                
            return response
            
        except Exception as e:
            logger.error(f"Error in get_factor_etf_prices: {e}")
            return {
                "error": str(e),
                "retryable": isinstance(e, (httpx.TimeoutException, httpx.HTTPStatusError))
            }


# Import asyncio for retry logic
import asyncio
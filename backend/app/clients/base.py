"""
Abstract base class for market data providers
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date


class MarketDataProvider(ABC):
    """Abstract base class for market data providers"""
    
    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    async def get_stock_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get current stock prices for multiple symbols
        
        Args:
            symbols: List of stock symbols (e.g., ['AAPL', 'MSFT'])
            
        Returns:
            Dict mapping symbol to price data:
            {
                'AAPL': {
                    'price': Decimal('150.25'),
                    'change': Decimal('2.15'),
                    'change_percent': Decimal('1.45'),
                    'volume': 50000000,
                    'timestamp': datetime,
                    'provider': 'FMPClient'
                }
            }
        """
        pass
    
    @abstractmethod
    async def get_fund_holdings(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get holdings for a mutual fund or ETF
        
        Args:
            symbol: Fund symbol (e.g., 'FXNAX', 'VTI')
            
        Returns:
            List of holdings:
            [
                {
                    'symbol': 'AAPL',
                    'name': 'Apple Inc',
                    'weight': Decimal('0.0525'),  # 5.25%
                    'shares': 1000000,
                    'market_value': Decimal('150250000.00'),
                    'provider': 'FMPClient'
                }
            ]
        """
        pass
    
    async def validate_api_key(self) -> bool:
        """
        Validate that the API key is working
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Test with a simple request (Apple stock)
            result = await self.get_stock_prices(['AAPL'])
            return bool(result and 'AAPL' in result)
        except Exception:
            return False
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get provider information"""
        return {
            'name': self.provider_name,
            'timeout': str(self.timeout),
            'max_retries': str(self.max_retries),
            'api_key_configured': bool(self.api_key)
        }
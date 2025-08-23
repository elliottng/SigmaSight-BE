"""
Market data provider factory for creating and managing API clients
"""
import logging
from typing import Dict, Optional, Union
from enum import Enum

from app.config import settings
from app.clients.base import MarketDataProvider
from app.clients.fmp_client import FMPClient
from app.clients.tradefeeds_client import TradeFeedsClient

logger = logging.getLogger(__name__)


class DataType(Enum):
    """Data types supported by providers"""
    STOCKS = "stocks"
    FUNDS = "funds"
    OPTIONS = "options"


class MarketDataFactory:
    """Factory for creating and managing market data provider clients"""
    
    def __init__(self):
        self._clients: Dict[str, MarketDataProvider] = {}
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize all available clients based on configuration"""
        if self._initialized:
            return
        
        # Initialize FMP client if API key is available
        if settings.FMP_API_KEY:
            try:
                self._clients['FMP'] = FMPClient(
                    api_key=settings.FMP_API_KEY,
                    timeout=settings.FMP_TIMEOUT_SECONDS,
                    max_retries=settings.FMP_MAX_RETRIES
                )
                logger.info("FMP client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize FMP client: {str(e)}")
        else:
            logger.warning("FMP_API_KEY not configured, FMP client not available")
        
        # Initialize TradeFeeds client if API key is available
        if settings.TRADEFEEDS_API_KEY:
            try:
                self._clients['TradeFeeds'] = TradeFeedsClient(
                    api_key=settings.TRADEFEEDS_API_KEY,
                    timeout=settings.TRADEFEEDS_TIMEOUT_SECONDS,
                    max_retries=settings.TRADEFEEDS_MAX_RETRIES,
                    rate_limit=settings.TRADEFEEDS_RATE_LIMIT
                )
                logger.info("TradeFeeds client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize TradeFeeds client: {str(e)}")
        else:
            logger.warning("TRADEFEEDS_API_KEY not configured, TradeFeeds client not available")
        
        self._initialized = True
        logger.info(f"Market data factory initialized with {len(self._clients)} clients")
    
    def get_provider_for_data_type(self, data_type: DataType) -> Optional[MarketDataProvider]:
        """
        Get the appropriate provider for a specific data type based on configuration
        
        Args:
            data_type: Type of data requested (stocks, funds, options)
            
        Returns:
            MarketDataProvider instance or None if no provider is available
        """
        self.initialize()
        
        if data_type == DataType.STOCKS:
            if settings.USE_FMP_FOR_STOCKS and 'FMP' in self._clients:
                return self._clients['FMP']
            elif 'TradeFeeds' in self._clients:
                logger.warning("FMP not available for stocks, falling back to TradeFeeds")
                return self._clients['TradeFeeds']
        
        elif data_type == DataType.FUNDS:
            if settings.USE_FMP_FOR_FUNDS and 'FMP' in self._clients:
                return self._clients['FMP']
            elif 'TradeFeeds' in self._clients:
                logger.warning("FMP not available for funds, falling back to TradeFeeds")
                return self._clients['TradeFeeds']
        
        elif data_type == DataType.OPTIONS:
            # Options always use Polygon (handled by existing market data service)
            logger.info("Options data requested - should use existing Polygon integration")
            return None
        
        logger.error(f"No provider available for data type: {data_type}")
        return None
    
    def get_client(self, provider_name: str) -> Optional[MarketDataProvider]:
        """
        Get a specific client by name
        
        Args:
            provider_name: Name of the provider ('FMP' or 'TradeFeeds')
            
        Returns:
            MarketDataProvider instance or None
        """
        self.initialize()
        return self._clients.get(provider_name)
    
    def get_available_providers(self) -> Dict[str, Dict[str, str]]:
        """Get information about all available providers"""
        self.initialize()
        
        providers = {}
        for name, client in self._clients.items():
            providers[name] = client.get_provider_info()
        
        return providers
    
    async def validate_all_providers(self) -> Dict[str, bool]:
        """Validate API keys for all configured providers"""
        self.initialize()
        
        validation_results = {}
        for name, client in self._clients.items():
            try:
                is_valid = await client.validate_api_key()
                validation_results[name] = is_valid
                logger.info(f"Provider {name} validation: {'✓' if is_valid else '✗'}")
            except Exception as e:
                logger.error(f"Error validating {name}: {str(e)}")
                validation_results[name] = False
        
        return validation_results
    
    async def close_all(self):
        """Close all client sessions"""
        for client in self._clients.values():
            if hasattr(client, 'close'):
                await client.close()
        logger.info("All provider clients closed")


# Global factory instance
market_data_factory = MarketDataFactory()
"""
Trading calendar utilities for determining market trading days
"""
import logging
from datetime import date, datetime, timedelta
from typing import List, Optional
import pandas as pd
import pandas_market_calendars as mcal
from functools import lru_cache

logger = logging.getLogger(__name__)


class TradingCalendar:
    """Utility class for working with trading calendars"""
    
    def __init__(self, exchange: str = "NYSE"):
        """
        Initialize trading calendar
        
        Args:
            exchange: Exchange calendar to use (default: NYSE)
        """
        self.exchange = exchange
        self.calendar = mcal.get_calendar(exchange)
        logger.info(f"Initialized trading calendar for {exchange}")
    
    @lru_cache(maxsize=365)
    def is_trading_day(self, check_date: date) -> bool:
        """
        Check if a given date is a trading day
        
        Args:
            check_date: Date to check
            
        Returns:
            True if trading day, False otherwise
        """
        # Convert date to pandas timestamp
        pd_date = pd.Timestamp(check_date)
        
        # Get valid trading days for the date range
        schedule = self.calendar.valid_days(
            start_date=pd_date,
            end_date=pd_date
        )
        
        return len(schedule) > 0
    
    def get_previous_trading_day(self, from_date: date) -> Optional[date]:
        """
        Get the previous trading day before a given date
        
        Args:
            from_date: Date to start from
            
        Returns:
            Previous trading day or None if none found in last 10 days
        """
        current = from_date - timedelta(days=1)
        max_lookback = 10  # Don't look back more than 10 days
        
        for _ in range(max_lookback):
            if self.is_trading_day(current):
                return current
            current -= timedelta(days=1)
        
        logger.warning(f"No trading day found in {max_lookback} days before {from_date}")
        return None
    
    def get_next_trading_day(self, from_date: date) -> Optional[date]:
        """
        Get the next trading day after a given date
        
        Args:
            from_date: Date to start from
            
        Returns:
            Next trading day or None if none found in next 10 days
        """
        current = from_date + timedelta(days=1)
        max_lookahead = 10  # Don't look ahead more than 10 days
        
        for _ in range(max_lookahead):
            if self.is_trading_day(current):
                return current
            current += timedelta(days=1)
        
        logger.warning(f"No trading day found in {max_lookahead} days after {from_date}")
        return None
    
    def get_trading_days_between(
        self,
        start_date: date,
        end_date: date,
        include_start: bool = True,
        include_end: bool = True
    ) -> List[date]:
        """
        Get all trading days between two dates
        
        Args:
            start_date: Start date
            end_date: End date
            include_start: Whether to include start date if it's a trading day
            include_end: Whether to include end date if it's a trading day
            
        Returns:
            List of trading days
        """
        # Get schedule from calendar
        schedule = self.calendar.valid_days(
            start_date=pd.Timestamp(start_date),
            end_date=pd.Timestamp(end_date)
        )
        
        # Convert to dates
        trading_days = [ts.date() for ts in schedule]
        
        # Handle inclusion flags
        if not include_start and trading_days and trading_days[0] == start_date:
            trading_days = trading_days[1:]
        if not include_end and trading_days and trading_days[-1] == end_date:
            trading_days = trading_days[:-1]
        
        return trading_days
    
    def should_run_batch_job(self, check_date: Optional[date] = None) -> bool:
        """
        Determine if batch jobs should run on a given date
        
        Args:
            check_date: Date to check (default: today)
            
        Returns:
            True if batch jobs should run, False otherwise
        """
        if check_date is None:
            check_date = date.today()
        
        # Batch jobs run on trading days
        return self.is_trading_day(check_date)


# Global instance for convenience
trading_calendar = TradingCalendar()
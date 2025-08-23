"""Portfolio-related constants for SigmaSight backend.

This module contains configuration constants used in portfolio aggregation,
calculations, and related operations.
"""

# Position multipliers
OPTIONS_MULTIPLIER = 100  # Standard options contract multiplier (1 contract = 100 shares)
STOCK_MULTIPLIER = 1     # Stock positions have no multiplier

# Decimal precision settings
GREEKS_DECIMAL_PLACES = 4    # Precision for Greeks values (delta, gamma, theta, vega, rho)
MONETARY_DECIMAL_PLACES = 2  # Precision for monetary values (exposures, P&L, etc.)
PERCENTAGE_DECIMAL_PLACES = 2  # Precision for percentage values

# Cache settings
AGGREGATION_CACHE_TTL = 60  # Cache time-to-live in seconds for aggregation results

# Default values for missing data
DEFAULT_SECTOR = "Unknown"
DEFAULT_INDUSTRY = "Unknown"

# Position type constants
POSITION_TYPE_LONG = "LONG"
POSITION_TYPE_SHORT = "SHORT"
POSITION_TYPE_LONG_CALL = "LC"
POSITION_TYPE_LONG_PUT = "LP"
POSITION_TYPE_SHORT_CALL = "SC"
POSITION_TYPE_SHORT_PUT = "SP"

# Options position types set for quick lookup
OPTIONS_POSITION_TYPES = {
    POSITION_TYPE_LONG_CALL,
    POSITION_TYPE_LONG_PUT,
    POSITION_TYPE_SHORT_CALL,
    POSITION_TYPE_SHORT_PUT
}

# Stock position types set for quick lookup
STOCK_POSITION_TYPES = {
    POSITION_TYPE_LONG,
    POSITION_TYPE_SHORT
}

# Legacy lists for backward compatibility
OPTION_TYPES = ["LC", "LP", "SC", "SP"]
STOCK_TYPES = ["LONG", "SHORT"]

# Cache key format templates
CACHE_KEY_FORMAT = "portfolio_agg:{user_id}:{agg_type}:{filters}"
CACHE_KEY_EXPOSURES = "portfolio_agg:{portfolio_id}:exposures"
CACHE_KEY_GREEKS = "portfolio_agg:{portfolio_id}:greeks"
CACHE_KEY_TAGS = "portfolio_agg:{portfolio_id}:tags:{tag_filter}:{tag_mode}"
CACHE_KEY_UNDERLYING = "portfolio_agg:{portfolio_id}:underlying"

# Performance targets
MAX_AGGREGATION_TIME_SECONDS = 1.0  # Target: <1 second for 10,000 positions

# Tag filtering modes
TAG_MODE_ANY = "any"  # OR logic - position must have at least one of the tags
TAG_MODE_ALL = "all"  # AND logic - position must have all of the tags

# Batch job timing
BATCH_JOB_MARKET_DATA_TIME = "16:00"  # 4 PM EST
BATCH_JOB_RISK_METRICS_TIME = "17:00"  # 5 PM EST
BATCH_JOB_SNAPSHOTS_TIME = "17:30"    # 5:30 PM EST

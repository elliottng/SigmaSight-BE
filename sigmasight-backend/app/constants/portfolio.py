"""Portfolio aggregation constants"""

# Multipliers
OPTIONS_MULTIPLIER = 100
STOCK_MULTIPLIER = 1

# Precision
MONETARY_DECIMAL_PLACES = 2
GREEKS_DECIMAL_PLACES = 4
PERCENTAGE_DECIMAL_PLACES = 2

# Defaults
DEFAULT_SECTOR = "Unknown"
DEFAULT_INDUSTRY = "Unknown"

# Cache settings
AGGREGATION_CACHE_TTL = 60  # seconds

# Position types
OPTION_TYPES = ["LC", "LP", "SC", "SP"]
STOCK_TYPES = ["LONG", "SHORT"]

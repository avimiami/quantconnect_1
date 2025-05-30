# Configuration for trading strategies

# API Keys and settings
API_CONFIG = {
    "tiingo_api_key": "YOUR_TIINGO_API_KEY_HERE",  # Replace with your actual Tiingo API key
    "data_source": "tiingo",  # Options: "tiingo", "quantconnect"
    "default_timeframe": "daily",  # Options: "daily", "hourly", "minute"
}

# Strategy configurations
STRATEGY_CONFIG = {
    "default_allocation": 0.05,  # 5% allocation per position by default
    "max_positions": 20,  # Maximum number of concurrent positions
    "risk_free_rate": 0.03,  # For Sharpe ratio calculations
    "default_stop_loss": 0.05,  # 5% stop loss by default
    "default_take_profit": 0.15,  # 15% take profit by default
}

# Symbols to track
SYMBOLS = [
    {"symbol": "AAPL", "tags": ["tech", "large_cap", "growth"]},
    {"symbol": "XLF", "tags": ["sector", "financials", "retirement_core"]},
    {"symbol": "SPY", "tags": ["index", "large_cap", "retirement_core"]},
    # Add more symbols as needed
]

# Strategy tags for categorization
STRATEGY_TAGS = [
    "momentum", "value", "growth", "income", "retirement", "swing_trade", 
    "day_trade", "long_term", "short_term", "sector", "index", "crypto"
]
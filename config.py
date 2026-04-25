"""
config.py — Central configuration for Market Trend Analyzer.

All constants, paths, and defaults live here.
Modules must import from this file instead of hard-coding values.
"""

import logging
import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR    = "data"
DB_PATH     = os.path.join(DATA_DIR, "market.db")
SCHEMA_PATH = os.path.join("db", "schema.sql")

PLOT_STOCK_TRENDS      = os.path.join(DATA_DIR, "stock_trends.png")
PLOT_REALESTATE        = os.path.join(DATA_DIR, "realestate_comparison.png")
PLOT_VOLATILITY        = os.path.join(DATA_DIR, "volatility.png")
PLOT_CORRELATION       = os.path.join(DATA_DIR, "correlation_heatmap.png")

SUMMARY_CSV_PATH       = os.path.join(DATA_DIR, "summary_report.csv")
PLOT_FORECAST          = os.path.join(DATA_DIR, "price_forecast.png")

# Demo mode — pre-cached CSVs so the pipeline runs without a live API call
DEMO_DIR               = "demo"
DEMO_STOCKS_CSV        = os.path.join(DEMO_DIR, "demo_stocks.csv")
DEMO_RE_CSV            = os.path.join(DEMO_DIR, "demo_realestate.csv")

# ---------------------------------------------------------------------------
# Stock settings
# ---------------------------------------------------------------------------
# US blue-chips + Indian NSE large-caps (cohesive with the Indian RE data)
DEFAULT_STOCK_SYMBOLS = [
    "AAPL", "GOOGL", "MSFT", "TSLA",   # US
    "INFY.NS", "TCS.NS", "RELIANCE.NS", # India (NSE)
]
DEFAULT_STOCK_PERIOD  = "6mo"   # yfinance period string

# ---------------------------------------------------------------------------
# Real-estate settings
# ---------------------------------------------------------------------------
CITIES = [
    {"city": "Mumbai",    "state": "MH"},
    {"city": "Delhi",     "state": "DL"},
    {"city": "Bangalore", "state": "KA"},
    {"city": "Pune",      "state": "MH"},
]

# Simulated realistic Indian real-estate data (INR).
# Replace with a live API (e.g. Rentcast, PropTiger) once a key is available.
MARKET_DATA = {
    "Mumbai":    {"avg_price": 18_500_000, "avg_rent": 45_000, "listings_count": 320},
    "Delhi":     {"avg_price": 12_000_000, "avg_rent": 28_000, "listings_count": 275},
    "Bangalore": {"avg_price":  9_500_000, "avg_rent": 32_000, "listings_count": 410},
    "Pune":      {"avg_price":  7_200_000, "avg_rent": 22_000, "listings_count": 190},
}

# Price-to-rent ratio thresholds for market signal classification
PTR_BUY_THRESHOLD     = 15
PTR_NEUTRAL_THRESHOLD = 20

# ---------------------------------------------------------------------------
# Moving-average windows
# ---------------------------------------------------------------------------
MA_SHORT_WINDOW  = 7
MA_LONG_WINDOW   = 30
RSI_WINDOW       = 14   # standard RSI lookback period
FORECAST_DAYS    = 7    # how many calendar days ahead to project

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FORMAT  = "%(asctime)s | %(levelname)-8s | %(name)s — %(message)s"
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL   = logging.INFO


def setup_logging(level: int = LOG_LEVEL) -> None:
    """Configure root logger for the entire application."""
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATEFMT,
    )

"""
generate_demo_data.py — Creates demo/demo_stocks.csv and demo/demo_realestate.csv.

Run once to (re-)generate demo data:
    python demo/generate_demo_data.py

The CSVs match the exact schema written by the live collectors, so every
downstream analysis and visualisation module works identically in --demo mode.

Data is 100% synthetic but calibrated to realistic price levels and volatility.
"""

import os
import sys

# Allow running from the repo root regardless of where python is invoked from
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from datetime import date

from config import DEMO_DIR, DEMO_STOCKS_CSV, DEMO_RE_CSV, DEFAULT_STOCK_SYMBOLS

os.makedirs(DEMO_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Seed for reproducibility
# ---------------------------------------------------------------------------
RNG = np.random.default_rng(seed=2024)

# ---------------------------------------------------------------------------
# Stock parameters: (start_price, daily_drift, daily_vol)
# Calibrated to real-world orders-of-magnitude (prices in native currency)
# ---------------------------------------------------------------------------
STOCK_PARAMS = {
    "AAPL":       (185.0,   0.0008, 0.012),
    "GOOGL":      (140.0,   0.0006, 0.013),
    "MSFT":       (375.0,   0.0009, 0.011),
    "TSLA":       (240.0,  -0.0004, 0.028),   # higher vol, slight downtrend
    "INFY.NS":    (1450.0,  0.0005, 0.014),   # INR
    "TCS.NS":     (3900.0,  0.0004, 0.010),   # INR
    "RELIANCE.NS":(2800.0,  0.0007, 0.012),   # INR
}

TRADING_DAYS = 126   # ~6 months of business days


def _simulate_prices(start: float, drift: float, vol: float, n: int) -> np.ndarray:
    """Geometric Brownian Motion price path."""
    returns = RNG.normal(drift, vol, n)
    prices  = start * np.exp(np.cumsum(returns))
    return np.round(prices, 2)


def generate_stocks_csv() -> None:
    end_date   = pd.Timestamp(date.today())
    date_range = pd.bdate_range(end=end_date, periods=TRADING_DAYS)

    rows = []
    for symbol, (start, drift, vol) in STOCK_PARAMS.items():
        closes  = _simulate_prices(start, drift, vol, TRADING_DAYS)
        highs   = np.round(closes * (1 + RNG.uniform(0.002, 0.015, TRADING_DAYS)), 2)
        lows    = np.round(closes * (1 - RNG.uniform(0.002, 0.015, TRADING_DAYS)), 2)
        opens   = np.round(closes * (1 + RNG.uniform(-0.006, 0.006, TRADING_DAYS)), 2)
        volumes = RNG.integers(1_000_000, 50_000_000, TRADING_DAYS)

        for i, d in enumerate(date_range):
            rows.append({
                "symbol": symbol,
                "date":   d.date(),
                "open":   opens[i],
                "close":  closes[i],
                "high":   highs[i],
                "low":    lows[i],
                "volume": int(volumes[i]),
            })

    df = pd.DataFrame(rows)
    df.to_csv(DEMO_STOCKS_CSV, index=False)
    print(f"✓  Generated {len(df):,} stock rows  →  {DEMO_STOCKS_CSV}")


def generate_realestate_csv() -> None:
    from config import CITIES, MARKET_DATA

    today = date.today()
    rows  = []

    for city_info in CITIES:
        city  = city_info["city"]
        state = city_info["state"]
        data  = MARKET_DATA[city]

        # Add slight noise so the CSV feels like real fetched data
        noise = RNG.uniform(0.97, 1.03)
        rows.append({
            "city":           city,
            "state":          state,
            "date":           today,
            "avg_price":      round(data["avg_price"]      * noise),
            "avg_rent":       round(data["avg_rent"]       * noise),
            "listings_count": round(data["listings_count"] * noise),
        })

    df = pd.DataFrame(rows)
    df.to_csv(DEMO_RE_CSV, index=False)
    print(f"✓  Generated {len(df)} real-estate rows  →  {DEMO_RE_CSV}")


if __name__ == "__main__":
    generate_stocks_csv()
    generate_realestate_csv()
    print("\nDemo data ready.  Run:  python main.py --demo")

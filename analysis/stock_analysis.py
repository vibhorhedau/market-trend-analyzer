"""stock_analysis.py — Computes moving averages, RSI, trend signals, and volatility."""

import logging
from typing import Optional

import pandas as pd

from config import MA_SHORT_WINDOW, MA_LONG_WINDOW, RSI_WINDOW
from db.db_connect import get_connection

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Indicator helpers
# ---------------------------------------------------------------------------

def compute_rsi(series: pd.Series, window: int = RSI_WINDOW) -> pd.Series:
    """
    Compute the Relative Strength Index (RSI) using Wilder's smoothing method.

    Uses only pandas — no external TA libraries required.

    Parameters
    ----------
    series : pd.Series
        Close price series (single symbol, time-ordered).
    window : int
        Lookback period (standard = 14).

    Returns
    -------
    pd.Series
        RSI values in the range [0, 100].
    """
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)

    # Wilder's smoothing ≡ EWM with com = window - 1
    avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
    avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()

    rs  = avg_gain / avg_loss.replace(0, float("nan"))   # avoid ÷0
    rsi = 100 - (100 / (1 + rs))
    return rsi


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

def analyze_stocks() -> Optional[pd.DataFrame]:
    """
    Read stock data from DB, compute indicators, and log a per-symbol summary.

    Indicators computed
    -------------------
    - MA{short} / MA{long}  : rolling close-price means
    - trend                 : Bullish / Bearish based on MA crossover
    - pct_change            : daily percentage change in close
    - volatility            : short-window rolling std deviation
    - RSI                   : 14-period Relative Strength Index (pure pandas)

    Returns
    -------
    pd.DataFrame or None
        Enriched DataFrame, or None if the stocks table is empty.
    """
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stocks ORDER BY symbol, date", conn)
    conn.close()

    if df.empty:
        logger.warning("No stock data found. Run the collector first.")
        return None

    short = MA_SHORT_WINDOW
    long_ = MA_LONG_WINDOW

    # Moving averages
    df[f"MA{short}"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(short).mean()
    )
    df[f"MA{long_}"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(long_).mean()
    )

    # Trend signal
    df["trend"] = df.apply(
        lambda r: "Bullish"
        if pd.notna(r[f"MA{short}"]) and pd.notna(r[f"MA{long_}"])
           and r[f"MA{short}"] > r[f"MA{long_}"]
        else "Bearish",
        axis=1,
    )

    # Daily % change
    df["pct_change"] = df.groupby("symbol")["close"].pct_change() * 100

    # Volatility (short-window rolling std dev)
    df["volatility"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(short).std()
    )

    # RSI (Wilder, 14-period)
    df["RSI"] = df.groupby("symbol")["close"].transform(compute_rsi)

    def _rsi_zone(rsi: float) -> str:
        if pd.isna(rsi):
            return "N/A"
        if rsi >= 70:
            return "Overbought"
        if rsi <= 30:
            return "Oversold"
        return "Neutral"

    df["RSI_zone"] = df["RSI"].apply(_rsi_zone)

    # Summary — latest row per symbol
    logger.info("===== Stock Trend Summary =====")
    latest = df.sort_values("date").groupby("symbol").tail(1)
    for _, row in latest.iterrows():
        logger.info(
            "  %-12s | Close: %10.2f | MA%d: %8.2f | MA%d: %8.2f | "
            "Trend: %-7s | RSI: %5.1f (%s)",
            row["symbol"], row["close"],
            short, row[f"MA{short}"],
            long_, row[f"MA{long_}"],
            row["trend"],
            row["RSI"] if pd.notna(row["RSI"]) else float("nan"),
            row["RSI_zone"],
        )

    return df


if __name__ == "__main__":
    from config import setup_logging
    setup_logging()
    analyze_stocks()

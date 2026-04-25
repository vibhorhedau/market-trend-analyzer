"""realestate_analysis.py — Computes rent yield, price-to-rent ratio, and market signals."""

import logging
from typing import Optional

import pandas as pd

from config import PTR_BUY_THRESHOLD, PTR_NEUTRAL_THRESHOLD
from db.db_connect import get_connection

logger = logging.getLogger(__name__)


def analyze_realestate() -> Optional[pd.DataFrame]:
    """
    Read real-estate data from DB, compute derived metrics, and log a summary.

    Returns
    -------
    pd.DataFrame or None
        Enriched DataFrame with price_to_rent, price_change_pct, rent_yield_pct,
        and market_signal columns.  Returns None if the table is empty.
    """
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM real_estate ORDER BY city, date", conn)
    conn.close()

    if df.empty:
        logger.warning("No real-estate data found. Run the collector first.")
        return None

    # Price-to-rent ratio (lower = better to buy; higher = better to rent)
    df["price_to_rent"] = df["avg_price"] / (df["avg_rent"] * 12)

    # % change in price vs previous entry per city
    df["price_change_pct"] = df.groupby("city")["avg_price"].pct_change() * 100

    # Rent yield % (annual rent / price)
    df["rent_yield_pct"] = (df["avg_rent"] * 12) / df["avg_price"] * 100

    # Market signal
    def _signal(ptr: float) -> str:
        if ptr < PTR_BUY_THRESHOLD:
            return "Buy market"
        if ptr < PTR_NEUTRAL_THRESHOLD:
            return "Neutral"
        return "Rent market"

    df["market_signal"] = df["price_to_rent"].apply(_signal)

    # Log summary — latest entry per city
    logger.info("===== Real Estate Trend Summary =====")
    latest = df.sort_values("date").groupby("city").tail(1)
    for _, row in latest.iterrows():
        logger.info(
            "  %s | Avg Price: INR %12,.0f | Rent Yield: %.2f%% | Signal: %s",
            row["city"], row["avg_price"], row["rent_yield_pct"], row["market_signal"],
        )

    return df


if __name__ == "__main__":
    from config import setup_logging
    setup_logging()
    analyze_realestate()

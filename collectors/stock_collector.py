"""stock_collector.py — Fetches OHLCV data from yfinance and stores it in SQLite."""

import logging
from typing import List

import pandas as pd
import yfinance as yf

from config import DEFAULT_STOCK_SYMBOLS, DEFAULT_STOCK_PERIOD
from db.db_connect import get_connection

logger = logging.getLogger(__name__)


def fetch_and_store_stocks(
    symbols: List[str] = None,
    period: str = None,
) -> None:
    """
    Download historical OHLCV data for each ticker and persist to the DB.

    Parameters
    ----------
    symbols : list of str, optional
        Ticker symbols to fetch.  Defaults to config.DEFAULT_STOCK_SYMBOLS.
    period : str, optional
        yfinance period string (e.g. '6mo', '1y').
        Defaults to config.DEFAULT_STOCK_PERIOD.
    """
    if symbols is None:
        symbols = DEFAULT_STOCK_SYMBOLS
    if period is None:
        period = DEFAULT_STOCK_PERIOD

    conn = get_connection()

    for symbol in symbols:
        logger.info("Fetching %s (period=%s)…", symbol, period)
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
        except Exception as exc:               # network / API errors
            logger.warning("Could not fetch %s — skipping. Reason: %s", symbol, exc)
            continue

        if df.empty:
            logger.warning("No data returned for %s — skipping.", symbol)
            continue

        df.reset_index(inplace=True)
        df["symbol"] = symbol
        df["date"]   = pd.to_datetime(df["Date"]).dt.date

        df_clean = df[["symbol", "date", "Open", "Close", "High", "Low", "Volume"]].rename(
            columns={"Open": "open", "Close": "close", "High": "high",
                     "Low": "low", "Volume": "volume"}
        )

        try:
            df_clean.to_sql("stocks", conn, if_exists="append", index=False)
            logger.info("  Stored %d rows for %s.", len(df_clean), symbol)
        except Exception as exc:
            logger.error("DB write failed for %s: %s", symbol, exc)

    conn.close()
    logger.info("Stock collection complete.")


if __name__ == "__main__":
    from config import setup_logging
    setup_logging()
    fetch_and_store_stocks()

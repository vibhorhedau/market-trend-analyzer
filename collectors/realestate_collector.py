"""realestate_collector.py — Stores Indian real-estate market data in SQLite."""

import logging
from datetime import date

import pandas as pd

from config import CITIES, MARKET_DATA
from db.db_connect import get_connection

logger = logging.getLogger(__name__)


def fetch_and_store_realestate() -> None:
    """
    Build a DataFrame from the configured market data and persist to the DB.

    Extend MARKET_DATA in config.py or swap in a live API call here once a
    key is available (e.g. Rentcast, PropTiger).
    """
    conn = get_connection()
    rows = []

    for city_info in CITIES:
        city  = city_info["city"]
        state = city_info["state"]

        if city not in MARKET_DATA:
            logger.warning("No market data configured for %s — skipping.", city)
            continue

        data = MARKET_DATA[city]
        rows.append({
            "city":           city,
            "state":          state,
            "date":           date.today(),
            "avg_price":      data["avg_price"],
            "avg_rent":       data["avg_rent"],
            "listings_count": data["listings_count"],
        })
        logger.info("Queued data for %s.", city)

    if rows:
        df = pd.DataFrame(rows)
        try:
            df.to_sql("real_estate", conn, if_exists="append", index=False)
            logger.info("Stored %d real-estate rows.", len(rows))
        except Exception as exc:
            logger.error("DB write failed for real_estate: %s", exc)

    conn.close()
    logger.info("Real-estate collection complete.")


if __name__ == "__main__":
    from config import setup_logging
    setup_logging()
    fetch_and_store_realestate()

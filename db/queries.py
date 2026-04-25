"""queries.py — Canned SQL analytics queries; results logged and exported to CSV."""

import logging
import os
from typing import List, Tuple, Any

import pandas as pd

from config import SUMMARY_CSV_PATH, DATA_DIR
from db.db_connect import get_connection

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Individual query runners (return DataFrame for CSV export)
# ---------------------------------------------------------------------------

def _q_best_stock(conn) -> Tuple[str, pd.DataFrame]:
    title = "Best performing stock (avg close)"
    logger.info("--- %s ---", title)
    rows = conn.execute("""
        SELECT symbol,
               ROUND(AVG(close), 2) AS avg_close,
               ROUND(MAX(close), 2) AS max_close,
               ROUND(MIN(close), 2) AS min_close
        FROM stocks
        GROUP BY symbol
        ORDER BY avg_close DESC
    """).fetchall()
    for r in rows:
        logger.info("  %s | Avg: %s | Max: %s | Min: %s", r[0], r[1], r[2], r[3])
    df = pd.DataFrame(rows, columns=["symbol", "avg_close", "max_close", "min_close"])
    return title, df


def _q_most_volatile(conn) -> Tuple[str, pd.DataFrame]:
    title = "Most volatile stock (close variance)"
    logger.info("--- %s ---", title)
    rows = conn.execute("""
        SELECT symbol,
               ROUND(AVG((close - sub.avg_c) * (close - sub.avg_c)), 4) AS variance
        FROM stocks
        JOIN (SELECT symbol AS sym, AVG(close) AS avg_c FROM stocks GROUP BY symbol) sub
          ON stocks.symbol = sub.sym
        GROUP BY symbol
        ORDER BY variance DESC
    """).fetchall()
    for r in rows:
        logger.info("  %s | Variance: %s", r[0], r[1])
    df = pd.DataFrame(rows, columns=["symbol", "variance"])
    return title, df


def _q_monthly_avg(conn) -> Tuple[str, pd.DataFrame]:
    title = "Monthly avg close per stock"
    logger.info("--- %s ---", title)
    rows = conn.execute("""
        SELECT symbol,
               STRFTIME('%Y-%m', date) AS month,
               ROUND(AVG(close), 2)    AS avg_close
        FROM stocks
        GROUP BY symbol, month
        ORDER BY symbol, month
    """).fetchall()
    for r in rows:
        logger.info("  %s | %s | %s", r[0], r[1], r[2])
    df = pd.DataFrame(rows, columns=["symbol", "month", "avg_close"])
    return title, df


def _q_best_rent_yield(conn) -> Tuple[str, pd.DataFrame]:
    title = "Best rent yield city"
    logger.info("--- %s ---", title)
    rows = conn.execute("""
        SELECT city,
               ROUND((avg_rent * 12.0 / avg_price) * 100, 2) AS rent_yield_pct
        FROM real_estate
        GROUP BY city
        ORDER BY rent_yield_pct DESC
    """).fetchall()
    for r in rows:
        logger.info("  %s | Rent Yield: %s%%", r[0], r[1])
    df = pd.DataFrame(rows, columns=["city", "rent_yield_pct"])
    return title, df


def _q_listing_count(conn) -> Tuple[str, pd.DataFrame]:
    title = "Cities by listing count"
    logger.info("--- %s ---", title)
    rows = conn.execute("""
        SELECT city, SUM(listings_count) AS total_listings
        FROM real_estate
        GROUP BY city
        ORDER BY total_listings DESC
    """).fetchall()
    for r in rows:
        logger.info("  %s | Listings: %s", r[0], r[1])
    df = pd.DataFrame(rows, columns=["city", "total_listings"])
    return title, df


# ---------------------------------------------------------------------------
# Main entry — runs all queries and exports a combined CSV report
# ---------------------------------------------------------------------------

def run_all_queries() -> None:
    """Run all analytics queries, log results, and export to SUMMARY_CSV_PATH."""
    conn = get_connection()

    query_results: List[Tuple[str, pd.DataFrame]] = [
        _q_best_stock(conn),
        _q_most_volatile(conn),
        _q_monthly_avg(conn),
        _q_best_rent_yield(conn),
        _q_listing_count(conn),
    ]

    conn.close()

    # ------------------------------------------------------------------
    # Export to CSV — each section is preceded by a header row so the
    # file is human-readable in Excel / a text editor.
    # ------------------------------------------------------------------
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(SUMMARY_CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        first = True
        for title, df in query_results:
            if df.empty:
                continue
            if not first:
                fh.write("\n")          # blank line between sections
            fh.write(f"# {title}\n")
            df.to_csv(fh, index=False)
            first = False

    logger.info("Summary report exported → %s  (%d sections)", SUMMARY_CSV_PATH, len(query_results))


if __name__ == "__main__":
    from config import setup_logging
    setup_logging()
    run_all_queries()

"""
demo_loader.py — Loads pre-cached demo CSVs into the DB instead of calling yfinance.

Used when the pipeline is invoked with  --demo.
Recruiters / reviewers can run the full project with zero API calls:

    python main.py --demo
"""

import logging
import os

import pandas as pd

from config import DEMO_STOCKS_CSV, DEMO_RE_CSV
from db.db_connect import get_connection

logger = logging.getLogger(__name__)


def load_demo_stocks() -> None:
    """Read demo/demo_stocks.csv and insert into the stocks table."""
    if not os.path.exists(DEMO_STOCKS_CSV):
        raise FileNotFoundError(
            f"Demo CSV not found: {DEMO_STOCKS_CSV}\n"
            "Run  python demo/generate_demo_data.py  to create it."
        )

    df = pd.read_csv(DEMO_STOCKS_CSV, parse_dates=["date"])
    df["date"] = df["date"].dt.date

    conn = get_connection()
    try:
        df.to_sql("stocks", conn, if_exists="append", index=False)
        logger.info("[DEMO] Loaded %d stock rows from %s", len(df), DEMO_STOCKS_CSV)
    except Exception as exc:
        logger.error("[DEMO] DB write failed for stocks: %s", exc)
    finally:
        conn.close()


def load_demo_realestate() -> None:
    """Read demo/demo_realestate.csv and insert into the real_estate table."""
    if not os.path.exists(DEMO_RE_CSV):
        raise FileNotFoundError(
            f"Demo CSV not found: {DEMO_RE_CSV}\n"
            "Run  python demo/generate_demo_data.py  to create it."
        )

    df = pd.read_csv(DEMO_RE_CSV, parse_dates=["date"])
    df["date"] = df["date"].dt.date

    conn = get_connection()
    try:
        df.to_sql("real_estate", conn, if_exists="append", index=False)
        logger.info("[DEMO] Loaded %d real-estate rows from %s", len(df), DEMO_RE_CSV)
    except Exception as exc:
        logger.error("[DEMO] DB write failed for real_estate: %s", exc)
    finally:
        conn.close()

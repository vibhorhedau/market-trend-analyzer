
"""
main.py — Market Trend Analyzer entry point with CLI support.

Usage examples
--------------
# Full pipeline with defaults
python main.py

# Custom tickers and a 1-year window
python main.py --stocks INFY TCS WIPRO --period 1y

# Skip chart generation (useful for headless / CI runs)
python main.py --skip-plots

# Combine options
python main.py --stocks AAPL MSFT --period 3mo --skip-plots

# Verbose logging
python main.py -v
"""

import argparse
import logging
import sys
from typing import List, Optional

from config import DEFAULT_STOCK_SYMBOLS, DEFAULT_STOCK_PERIOD, setup_logging
from db.db_connect import init_db
from collectors.stock_collector import fetch_and_store_stocks
from collectors.realestate_collector import fetch_and_store_realestate
from analysis.stock_analysis import analyze_stocks
from analysis.realestate_analysis import analyze_realestate
from db.queries import run_all_queries
from visualize.plots import (
    plot_stock_trends,
    plot_realestate_comparison,
    plot_volatility,
    plot_correlation_heatmap,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CLI definition
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="market-trend-analyzer",
        description="Collect, analyse, and visualise stock & real-estate market trends.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--stocks",
        nargs="+",
        metavar="TICKER",
        default=DEFAULT_STOCK_SYMBOLS,
        help=(
            "Space-separated list of yfinance ticker symbols to fetch. "
            f"Default: {' '.join(DEFAULT_STOCK_SYMBOLS)}"
        ),
    )
    parser.add_argument(
        "--period",
        default=DEFAULT_STOCK_PERIOD,
        metavar="PERIOD",
        help=(
            "yfinance history period string (e.g. 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y). "
            f"Default: {DEFAULT_STOCK_PERIOD}"
        ),
    )
    parser.add_argument(
        "--skip-plots",
        action="store_true",
        help="Skip chart generation (useful for headless / CI environments).",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging.",
    )

    return parser


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(
    stocks: List[str],
    period: str,
    skip_plots: bool,
) -> None:
    logger.info("========================================")
    logger.info("   Market Trend Analyzer — Full Run")
    logger.info("========================================")
    logger.info("Tickers : %s", ", ".join(stocks))
    logger.info("Period  : %s", period)
    logger.info("Plots   : %s", "disabled" if skip_plots else "enabled")

    logger.info("[1/6] Initializing database…")
    init_db()

    logger.info("[2/6] Collecting stock data…")
    fetch_and_store_stocks(symbols=stocks, period=period)

    logger.info("[3/6] Collecting real estate data…")
    fetch_and_store_realestate()

    logger.info("[4/6] Analyzing stock trends…")
    analyze_stocks()

    logger.info("[5/6] Analyzing real estate trends…")
    analyze_realestate()

    logger.info("[6/6] Running SQL queries…")
    run_all_queries()

    if not skip_plots:
        logger.info("Generating charts…")
        plot_stock_trends()
        plot_realestate_comparison()
        plot_volatility()
        plot_correlation_heatmap()
    else:
        logger.info("Chart generation skipped (--skip-plots).")

    logger.info("Pipeline complete!")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args   = parser.parse_args(argv)

    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)

    run_pipeline(
        stocks=args.stocks,
        period=args.period,
        skip_plots=args.skip_plots,
    )


if __name__ == "__main__":
    main()

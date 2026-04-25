"""
forecast.py — 7-day linear price forecast using numpy.polyfit.

⚠️  DISCLAIMER: Forecasts are purely illustrative (linear extrapolation on
    historical closing prices).  They are NOT financial advice and should NOT
    be used to make investment decisions.
"""

import logging
from typing import Optional, Tuple

import numpy as np
import pandas as pd

from config import FORECAST_DAYS
from db.db_connect import get_connection

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "⚠️  ILLUSTRATIVE ONLY — linear extrapolation, not financial advice."
)


# ---------------------------------------------------------------------------
# Core regression helper
# ---------------------------------------------------------------------------

def _linear_forecast(
    dates: pd.Series,
    prices: pd.Series,
    n_days: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fit a degree-1 polynomial (line) to *prices* over integer-indexed *dates*
    and return forecast points for the next *n_days* calendar days.

    Parameters
    ----------
    dates   : pd.Series of datetime-like values (used for x-axis labelling only)
    prices  : pd.Series of float close prices (aligned with dates)
    n_days  : int, number of future days to project

    Returns
    -------
    fit_x     : np.ndarray — integer indices for the fitted range (0…len-1)
    fit_y     : np.ndarray — regression line over the historical window
    future_x  : np.ndarray — integer indices for the forecast window
    future_y  : np.ndarray — projected prices for the next n_days
    future_dates : pd.DatetimeIndex — actual calendar dates for the forecast
    """
    x = np.arange(len(prices), dtype=float)
    y = prices.values.astype(float)

    # Drop any NaNs (shouldn't happen after collector, but be safe)
    mask = ~np.isnan(y)
    x_clean, y_clean = x[mask], y[mask]

    # Degree-1 poly: y = m*x + b
    coeffs = np.polyfit(x_clean, y_clean, deg=1)
    poly   = np.poly1d(coeffs)

    fit_y = poly(x_clean)

    # Extrapolate n_days beyond the last index
    last_x      = x_clean[-1]
    future_x    = np.arange(last_x + 1, last_x + 1 + n_days)
    future_y    = poly(future_x)

    # Map future indices → calendar dates (using the same daily step)
    last_date    = pd.to_datetime(dates.iloc[-1])
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=n_days, freq="B")

    return x_clean, fit_y, future_x, future_y, future_dates, poly, coeffs


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

def forecast_stocks(n_days: int = FORECAST_DAYS) -> Optional[pd.DataFrame]:
    """
    Compute and log a linear-regression price forecast for every symbol.

    Parameters
    ----------
    n_days : int
        Number of business days to project forward. Default: config.FORECAST_DAYS.

    Returns
    -------
    pd.DataFrame or None
        One row per (symbol, future_date) with columns:
        symbol, forecast_date, forecast_price, slope, intercept.
        Returns None if the stocks table is empty.
    """
    conn = get_connection()
    df = pd.read_sql("SELECT symbol, date, close FROM stocks ORDER BY symbol, date", conn)
    conn.close()

    if df.empty:
        logger.warning("No stock data — skipping forecast.")
        return None

    df["date"] = pd.to_datetime(df["date"])
    all_forecasts = []

    logger.info("===== 7-Day Price Forecast (Linear Regression) =====")
    logger.info("%s", DISCLAIMER)

    for symbol, sdf in df.groupby("symbol"):
        sdf = sdf.sort_values("date").reset_index(drop=True)

        if len(sdf) < 10:
            logger.warning("  %s: not enough data points (%d) — skipping.", symbol, len(sdf))
            continue

        _, _, _, future_y, future_dates, _, coeffs = _linear_forecast(
            sdf["date"], sdf["close"], n_days
        )

        slope, intercept = coeffs[0], coeffs[1]
        direction = "↑" if slope > 0 else "↓"

        logger.info(
            "  %-12s | Slope: %+.4f %s | Last close: %9.2f | "
            "Forecast +%dd: %9.2f",
            symbol, slope, direction,
            sdf["close"].iloc[-1],
            n_days, future_y[-1],
        )

        for date_, price in zip(future_dates, future_y):
            all_forecasts.append({
                "symbol":         symbol,
                "forecast_date":  date_.date(),
                "forecast_price": round(float(price), 4),
                "slope":          round(float(slope), 6),
                "intercept":      round(float(intercept), 4),
            })

    if not all_forecasts:
        return None

    result = pd.DataFrame(all_forecasts)

    # Also persist the forecast to CSV alongside the summary report
    from config import DATA_DIR
    import os
    forecast_csv = os.path.join(DATA_DIR, "forecast.csv")
    os.makedirs(DATA_DIR, exist_ok=True)
    result.to_csv(forecast_csv, index=False)
    logger.info("Forecast exported → %s", forecast_csv)

    return result


if __name__ == "__main__":
    from config import setup_logging
    setup_logging()
    forecast_stocks()

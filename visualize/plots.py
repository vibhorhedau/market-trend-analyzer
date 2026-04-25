"""plots.py — Matplotlib/Seaborn visualizations for stock and real-estate data."""

import logging
import math

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns

from config import (
    MA_SHORT_WINDOW, MA_LONG_WINDOW,
    PLOT_STOCK_TRENDS, PLOT_REALESTATE, PLOT_VOLATILITY,
    PLOT_CORRELATION, PLOT_FORECAST, FORECAST_DAYS,
)
from db.db_connect import get_connection

logger = logging.getLogger(__name__)

_COLORS = ["#378ADD", "#1D9E75", "#D85A30", "#7F77DD",
           "#E8A838", "#9B59B6", "#2ECC71"]   # 7 slots for 7 default symbols


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _grid_dims(n: int) -> tuple:
    """Return (nrows, ncols) for a compact grid that fits n subplots."""
    ncols = min(n, 4)          # max 4 columns
    nrows = math.ceil(n / ncols)
    return nrows, ncols


# ---------------------------------------------------------------------------
# Plot functions
# ---------------------------------------------------------------------------

def plot_stock_trends() -> None:
    """Plot close price with short/long moving averages for every symbol."""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stocks ORDER BY symbol, date", conn)
    conn.close()

    if df.empty:
        logger.warning("No stock data — skipping stock trend plot.")
        return

    short, long_ = MA_SHORT_WINDOW, MA_LONG_WINDOW
    df["date"]       = pd.to_datetime(df["date"])
    df[f"MA{short}"] = df.groupby("symbol")["close"].transform(lambda x: x.rolling(short).mean())
    df[f"MA{long_}"] = df.groupby("symbol")["close"].transform(lambda x: x.rolling(long_).mean())

    symbols  = df["symbol"].unique()
    nrows, ncols = _grid_dims(len(symbols))

    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows))
    fig.suptitle("Stock Price Trends — 6-Month Analysis", fontsize=15, fontweight="bold")

    # Flatten and hide any extra axes
    axes_flat = axes.flatten() if hasattr(axes, "flatten") else [axes]
    for ax in axes_flat[len(symbols):]:
        ax.set_visible(False)

    for i, symbol in enumerate(symbols):
        ax  = axes_flat[i]
        sdf = df[df["symbol"] == symbol]

        ax.plot(sdf["date"], sdf["close"],        label="Close",        color="#378ADD", linewidth=1.5)
        ax.plot(sdf["date"], sdf[f"MA{short}"],   label=f"MA{short}",   color="#1D9E75", linewidth=1, linestyle="--")
        ax.plot(sdf["date"], sdf[f"MA{long_}"],   label=f"MA{long_}",   color="#D85A30", linewidth=1, linestyle="--")

        ax.set_title(symbol, fontsize=11, fontweight="bold")
        ax.set_xlabel("Date",       fontsize=8)
        ax.set_ylabel("Price",      fontsize=8)
        ax.legend(fontsize=7)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.tick_params(axis="x", rotation=30, labelsize=7)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(PLOT_STOCK_TRENDS, dpi=150)
    plt.close()
    logger.info("Saved: %s", PLOT_STOCK_TRENDS)


def plot_realestate_comparison() -> None:
    """Bar charts comparing avg price, avg rent, and rent yield across cities."""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM real_estate", conn)
    conn.close()

    if df.empty:
        logger.warning("No real-estate data — skipping comparison plot.")
        return

    df["rent_yield"] = (df["avg_rent"] * 12) / df["avg_price"] * 100

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Real Estate Market Comparison", fontsize=15, fontweight="bold")

    bar_colors = _COLORS[:len(df)]

    axes[0].bar(df["city"], df["avg_price"] / 1_000_000, color=bar_colors)
    axes[0].set_title("Avg Property Price (₹ M)", fontsize=11)
    axes[0].set_ylabel("Price (Millions ₹)")
    axes[0].tick_params(axis="x", rotation=20)
    axes[0].grid(axis="y", alpha=0.3)

    axes[1].bar(df["city"], df["avg_rent"], color=bar_colors)
    axes[1].set_title("Avg Monthly Rent (₹)", fontsize=11)
    axes[1].set_ylabel("Rent (₹)")
    axes[1].tick_params(axis="x", rotation=20)
    axes[1].grid(axis="y", alpha=0.3)

    axes[2].bar(df["city"], df["rent_yield"], color=bar_colors)
    axes[2].set_title("Annual Rent Yield (%)", fontsize=11)
    axes[2].set_ylabel("Yield %")
    axes[2].tick_params(axis="x", rotation=20)
    axes[2].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(PLOT_REALESTATE, dpi=150)
    plt.close()
    logger.info("Saved: %s", PLOT_REALESTATE)


def plot_volatility() -> None:
    """Line chart of rolling volatility (std dev) for each stock."""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stocks ORDER BY symbol, date", conn)
    conn.close()

    if df.empty:
        logger.warning("No stock data — skipping volatility plot.")
        return

    short = MA_SHORT_WINDOW
    df["volatility"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(short).std()
    )
    df["date"] = pd.to_datetime(df["date"])

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.suptitle(f"Stock Volatility — {short}-Day Rolling Std Dev", fontsize=13, fontweight="bold")

    for color, symbol in zip(_COLORS, df["symbol"].unique()):
        sdf = df[df["symbol"] == symbol]
        ax.plot(sdf["date"], sdf["volatility"], label=symbol, linewidth=1.5, color=color)

    ax.set_xlabel("Date")
    ax.set_ylabel("Volatility (Std Dev)")
    ax.legend(fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.tick_params(axis="x", rotation=30)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(PLOT_VOLATILITY, dpi=150)
    plt.close()
    logger.info("Saved: %s", PLOT_VOLATILITY)


def plot_correlation_heatmap() -> None:
    """
    Seaborn heatmap of pairwise Pearson correlations between daily close prices.

    Correlation is computed on raw close prices (same calendar date),
    after pivoting so each column is one symbol.  Only dates present
    for ALL symbols are used (inner join), keeping the matrix balanced.
    """
    conn = get_connection()
    df = pd.read_sql("SELECT symbol, date, close FROM stocks", conn)
    conn.close()

    if df.empty:
        logger.warning("No stock data — skipping correlation heatmap.")
        return

    # Pivot: rows = date, columns = symbol, values = close price
    pivot = df.pivot_table(index="date", columns="symbol", values="close")

    # Drop dates where any symbol has NaN (keeps correlation matrix clean)
    pivot.dropna(how="any", inplace=True)

    if pivot.shape[0] < 5:
        logger.warning(
            "Not enough overlapping dates across all symbols (%d rows) — "
            "skipping correlation heatmap.", pivot.shape[0]
        )
        return

    corr = pivot.corr(method="pearson")

    fig, ax = plt.subplots(figsize=(max(8, len(corr) * 1.1), max(6, len(corr) * 0.9)))
    fig.suptitle("Stock Return Correlation Heatmap", fontsize=14, fontweight="bold", y=1.01)

    sns.heatmap(
        corr,
        ax=ax,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",          # red = negative, green = positive
        vmin=-1, vmax=1,
        linewidths=0.5,
        linecolor="white",
        annot_kws={"size": 9},
        cbar_kws={"shrink": 0.8, "label": "Pearson r"},
    )

    ax.set_title(
        f"Based on {pivot.shape[0]} overlapping trading days",
        fontsize=9, style="italic", pad=4,
    )
    ax.tick_params(axis="x", rotation=30, labelsize=9)
    ax.tick_params(axis="y", rotation=0,  labelsize=9)

    plt.tight_layout()
    plt.savefig(PLOT_CORRELATION, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Saved: %s", PLOT_CORRELATION)


def plot_forecast(n_days: int = FORECAST_DAYS) -> None:
    """
    Plot historical close prices with a linear-regression fit and n_days
    forward projection for every symbol.

    The forecast band is shaded and clearly labelled as illustrative only.
    """
    from analysis.forecast import _linear_forecast, DISCLAIMER

    conn = get_connection()
    df = pd.read_sql("SELECT symbol, date, close FROM stocks ORDER BY symbol, date", conn)
    conn.close()

    if df.empty:
        logger.warning("No stock data — skipping forecast plot.")
        return

    df["date"] = pd.to_datetime(df["date"])
    symbols    = df["symbol"].unique()
    nrows, ncols = _grid_dims(len(symbols))

    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows))
    fig.suptitle(
        f"7-Day Price Forecast (Linear Regression)\n{DISCLAIMER}",
        fontsize=12, fontweight="bold", color="#333333",
    )

    axes_flat = axes.flatten() if hasattr(axes, "flatten") else [axes]
    for ax in axes_flat[len(symbols):]:
        ax.set_visible(False)

    for i, (symbol, color) in enumerate(zip(symbols, _COLORS)):
        ax  = axes_flat[i]
        sdf = df[df["symbol"] == symbol].sort_values("date").reset_index(drop=True)

        if len(sdf) < 10:
            ax.set_title(f"{symbol} (insufficient data)", fontsize=10)
            continue

        x_clean, fit_y, _, future_y, future_dates, _, _ = _linear_forecast(
            sdf["date"], sdf["close"], n_days
        )

        hist_dates = sdf["date"].values

        # Historical close
        ax.plot(hist_dates, sdf["close"], color=color, linewidth=1.4, label="Close")

        # Regression fit over historical window
        ax.plot(
            hist_dates[x_clean.astype(int)], fit_y,
            color="grey", linewidth=1, linestyle=":", label="Fit",
        )

        # Forecast segment
        last_date  = sdf["date"].iloc[-1]
        last_close = sdf["close"].iloc[-1]
        fore_x     = [last_date] + list(future_dates)
        fore_y     = [last_close] + list(future_y)

        ax.plot(fore_x, fore_y, color="#E8A838", linewidth=1.8,
                linestyle="--", label=f"+{n_days}d forecast")

        # Shaded uncertainty band (±2% of last close as a simple visual cue)
        band = last_close * 0.02
        fore_y_arr = np.array(fore_y)
        ax.fill_between(
            fore_x, fore_y_arr - band, fore_y_arr + band,
            alpha=0.15, color="#E8A838",
        )

        # Vertical divider at forecast start
        ax.axvline(last_date, color="grey", linewidth=0.8, linestyle="-", alpha=0.5)

        ax.set_title(symbol, fontsize=10, fontweight="bold")
        ax.set_xlabel("Date", fontsize=8)
        ax.set_ylabel("Price", fontsize=8)
        ax.legend(fontsize=7)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.tick_params(axis="x", rotation=30, labelsize=7)
        ax.grid(True, alpha=0.25)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(PLOT_FORECAST, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Saved: %s", PLOT_FORECAST)


if __name__ == "__main__":
    from config import setup_logging
    setup_logging()
    plot_stock_trends()
    plot_realestate_comparison()
    plot_volatility()
    plot_correlation_heatmap()
    plot_forecast()

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from db.db_connect import get_connection

def plot_stock_trends():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stocks ORDER BY symbol, date", conn)
    conn.close()

    df["date"] = pd.to_datetime(df["date"])
    df["MA7"]  = df.groupby("symbol")["close"].transform(lambda x: x.rolling(7).mean())
    df["MA30"] = df.groupby("symbol")["close"].transform(lambda x: x.rolling(30).mean())

    symbols = df["symbol"].unique()
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle("Stock Price Trends — 6 Month Analysis", fontsize=15, fontweight="bold")
    axes = axes.flatten()

    for i, symbol in enumerate(symbols):
        ax  = axes[i]
        sdf = df[df["symbol"] == symbol]

        ax.plot(sdf["date"], sdf["close"], label="Close",  color="#378ADD", linewidth=1.5)
        ax.plot(sdf["date"], sdf["MA7"],   label="MA7",    color="#1D9E75", linewidth=1,   linestyle="--")
        ax.plot(sdf["date"], sdf["MA30"],  label="MA30",   color="#D85A30", linewidth=1,   linestyle="--")

        ax.set_title(symbol, fontsize=12, fontweight="bold")
        ax.set_xlabel("Date",  fontsize=9)
        ax.set_ylabel("Price (USD)", fontsize=9)
        ax.legend(fontsize=8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.tick_params(axis="x", rotation=30, labelsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("data/stock_trends.png", dpi=150)
    plt.show()
    print("Saved: data/stock_trends.png")


def plot_realestate_comparison():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM real_estate", conn)
    conn.close()

    df["rent_yield"] = (df["avg_rent"] * 12) / df["avg_price"] * 100

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Real Estate Market Comparison", fontsize=15, fontweight="bold")

    colors = ["#378ADD", "#1D9E75", "#D85A30", "#7F77DD"]

    # Chart 1 — Avg property price
    axes[0].bar(df["city"], df["avg_price"] / 1_000_000, color=colors)
    axes[0].set_title("Avg Property Price (₹ M)", fontsize=11)
    axes[0].set_ylabel("Price (Millions ₹)")
    axes[0].tick_params(axis="x", rotation=20)
    axes[0].grid(axis="y", alpha=0.3)

    # Chart 2 — Avg monthly rent
    axes[1].bar(df["city"], df["avg_rent"], color=colors)
    axes[1].set_title("Avg Monthly Rent (₹)", fontsize=11)
    axes[1].set_ylabel("Rent (₹)")
    axes[1].tick_params(axis="x", rotation=20)
    axes[1].grid(axis="y", alpha=0.3)

    # Chart 3 — Rent yield %
    axes[2].bar(df["city"], df["rent_yield"], color=colors)
    axes[2].set_title("Annual Rent Yield (%)", fontsize=11)
    axes[2].set_ylabel("Yield %")
    axes[2].tick_params(axis="x", rotation=20)
    axes[2].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("data/realestate_comparison.png", dpi=150)
    plt.show()
    print("Saved: data/realestate_comparison.png")


def plot_volatility():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stocks ORDER BY symbol, date", conn)
    conn.close()

    df["volatility"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(7).std()
    )

    df["date"] = pd.to_datetime(df["date"])
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.suptitle("Stock Volatility — 7-Day Rolling Std Dev", fontsize=13, fontweight="bold")

    for symbol in df["symbol"].unique():
        sdf = df[df["symbol"] == symbol]
        ax.plot(sdf["date"], sdf["volatility"], label=symbol, linewidth=1.5)

    ax.set_xlabel("Date")
    ax.set_ylabel("Volatility (Std Dev)")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.tick_params(axis="x", rotation=30)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("data/volatility.png", dpi=150)
    plt.show()
    print("Saved: data/volatility.png")


if __name__ == "__main__":
    plot_stock_trends()
    plot_realestate_comparison()
    plot_volatility()

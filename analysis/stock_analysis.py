import pandas as pd
from db.db_connect import get_connection

def analyze_stocks():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stocks ORDER BY symbol, date", conn)
    conn.close()

    if df.empty:
        print("No stock data found. Run collector first.")
        return

    # Moving averages
    df["MA7"]  = df.groupby("symbol")["close"].transform(lambda x: x.rolling(7).mean())
    df["MA30"] = df.groupby("symbol")["close"].transform(lambda x: x.rolling(30).mean())

    # Trend signal
    df["trend"] = df.apply(
        lambda r: "Bullish" if pd.notna(r["MA7"]) and pd.notna(r["MA30"])
                               and r["MA7"] > r["MA30"] else "Bearish", axis=1
    )

    # Daily % change
    df["pct_change"] = df.groupby("symbol")["close"].pct_change() * 100

    # Volatility (7-day rolling std deviation)
    df["volatility"] = df.groupby("symbol")["close"].transform(lambda x: x.rolling(7).std())

    # Summary: latest signal per stock
    print("\n===== Stock Trend Summary =====")
    latest = df.sort_values("date").groupby("symbol").tail(1)
    for _, row in latest.iterrows():
        print(f"  {row['symbol']:6s} | Close: {row['close']:8.2f} | "
              f"MA7: {row['MA7']:8.2f} | MA30: {row['MA30']:8.2f} | "
              f"Trend: {row['trend']}")

    return df

if __name__ == "__main__":
    analyze_stocks()

import yfinance as yf
import pandas as pd
from db.db_connect import get_connection

SYMBOLS = ["AAPL", "GOOGL", "MSFT", "TSLA"]

def fetch_and_store_stocks():
    conn = get_connection()

    for symbol in SYMBOLS:
        print(f"Fetching {symbol}...")

        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo")

        if df.empty:
            print(f"  No data for {symbol}, skipping.")
            continue

        df.reset_index(inplace=True)
        df["symbol"] = symbol
        df["date"]   = pd.to_datetime(df["Date"]).dt.date

        df_clean = df[["symbol","date","Open","Close","High","Low","Volume"]].rename(columns={
            "Open":   "open",
            "Close":  "close",
            "High":   "high",
            "Low":    "low",
            "Volume": "volume"
        })

        df_clean.to_sql("stocks", conn, if_exists="append", index=False)
        print(f"  Stored {len(df_clean)} rows for {symbol}.")

    conn.close()
    print("Stock collection complete.")

if __name__ == "__main__":
    fetch_and_store_stocks()

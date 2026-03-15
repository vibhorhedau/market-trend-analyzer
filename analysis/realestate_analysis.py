import pandas as pd
from db.db_connect import get_connection

def analyze_realestate():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM real_estate ORDER BY city, date", conn)
    conn.close()

    if df.empty:
        print("No real estate data found. Run collector first.")
        return

    # Price-to-rent ratio (lower = better to buy, higher = better to rent)
    df["price_to_rent"] = df["avg_price"] / (df["avg_rent"] * 12)

    # % change in price vs previous entry per city
    df["price_change_pct"] = df.groupby("city")["avg_price"].pct_change() * 100

    # Rent yield % (annual rent / price)
    df["rent_yield_pct"] = (df["avg_rent"] * 12) / df["avg_price"] * 100

    # Market signal
    df["market_signal"] = df["price_to_rent"].apply(
        lambda r: "Buy market" if r < 15 else ("Neutral" if r < 20 else "Rent market")
    )

    print("\n===== Real Estate Trend Summary =====")
    latest = df.sort_values("date").groupby("city").tail(1)
    for _, row in latest.iterrows():
        print(f"  {row['city']:12s} | Avg Price: INR {row['avg_price']:>12,.0f} | "
              f"Rent Yield: {row['rent_yield_pct']:.2f}% | "
              f"Signal: {row['market_signal']}")

    return df

if __name__ == "__main__":
    analyze_realestate()

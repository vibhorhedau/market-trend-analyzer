from db.db_connect import get_connection

def run_all_queries():
    conn = get_connection()

    # Query 1: Best performing stock (highest avg close price)
    print("\n--- Best performing stock (avg close) ---")
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
        print(f"  {r[0]} | Avg: {r[1]} | Max: {r[2]} | Min: {r[3]}")

    # Query 2: Most volatile stock (highest std deviation of close)
    print("\n--- Most volatile stock ---")
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
        print(f"  {r[0]} | Variance: {r[1]}")

    # Query 3: Monthly average close price per stock
    print("\n--- Monthly avg close per stock ---")
    rows = conn.execute("""
        SELECT symbol,
               STRFTIME('%Y-%m', date) AS month,
               ROUND(AVG(close), 2)    AS avg_close
        FROM stocks
        GROUP BY symbol, month
        ORDER BY symbol, month
    """).fetchall()
    for r in rows:
        print(f"  {r[0]} | {r[1]} | {r[2]}")

    # Query 4: Real estate — best rent yield city
    print("\n--- Best rent yield city ---")
    rows = conn.execute("""
        SELECT city,
               ROUND((avg_rent * 12.0 / avg_price) * 100, 2) AS rent_yield_pct
        FROM real_estate
        GROUP BY city
        ORDER BY rent_yield_pct DESC
    """).fetchall()
    for r in rows:
        print(f"  {r[0]} | Rent Yield: {r[1]}%")

    # Query 5: Cities with highest listing activity
    print("\n--- Cities by listing count ---")
    rows = conn.execute("""
        SELECT city, SUM(listings_count) AS total_listings
        FROM real_estate
        GROUP BY city
        ORDER BY total_listings DESC
    """).fetchall()
    for r in rows:
        print(f"  {r[0]} | Listings: {r[1]}")

    conn.close()

if __name__ == "__main__":
    run_all_queries()

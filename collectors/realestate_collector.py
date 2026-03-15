import requests
import pandas as pd
from datetime import date
from db.db_connect import get_connection

CITIES = [
    {"city": "Mumbai",    "state": "MH", "avg_price": None},
    {"city": "Delhi",     "state": "DL", "avg_price": None},
    {"city": "Bangalore", "state": "KA", "avg_price": None},
    {"city": "Pune",      "state": "MH", "avg_price": None},
]

# Simulated realistic Indian real estate data (in INR lakhs)
# Replace with live API once you have a key (e.g. Rentcast, PropTiger)
MARKET_DATA = {
    "Mumbai":    {"avg_price": 18500000, "avg_rent": 45000, "listings_count": 320},
    "Delhi":     {"avg_price": 12000000, "avg_rent": 28000, "listings_count": 275},
    "Bangalore": {"avg_price":  9500000, "avg_rent": 32000, "listings_count": 410},
    "Pune":      {"avg_price":  7200000, "avg_rent": 22000, "listings_count": 190},
}

def fetch_and_store_realestate():
    conn = get_connection()
    rows = []

    for city_info in CITIES:
        city  = city_info["city"]
        state = city_info["state"]
        data  = MARKET_DATA[city]

        rows.append({
            "city":           city,
            "state":          state,
            "date":           date.today(),
            "avg_price":      data["avg_price"],
            "avg_rent":       data["avg_rent"],
            "listings_count": data["listings_count"]
        })
        print(f"Stored data for {city}.")

    df = pd.DataFrame(rows)
    df.to_sql("real_estate", conn, if_exists="append", index=False)
    conn.close()
    print("Real estate collection complete.")

if __name__ == "__main__":
    fetch_and_store_realestate()

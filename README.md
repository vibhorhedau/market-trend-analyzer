# Market Trend Analyzer

A data pipeline that collects, stores, and analyzes trends in **stock prices** and **real estate markets** using Python and SQL.

Built as a portfolio project to demonstrate end-to-end data engineering and analysis skills.

---

## Features

- Fetches 6 months of live stock data (AAPL, GOOGL, MSFT, TSLA) via `yfinance`
- Stores all data in a structured **SQLite** database
- Detects **Bullish/Bearish** signals using MA7 vs MA30 moving average crossover
- Calculates **rent yield**, **price-to-rent ratio**, and **market signals** for Indian cities
- Runs **SQL trend queries** — volatility, monthly averages, best yield cities
- Generates **3 charts** — stock trends, real estate comparison, volatility

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Core language |
| yfinance | Live stock data |
| pandas | Data manipulation |
| SQLite + SQL | Data storage & querying |
| SQLAlchemy | Python-DB bridge |
| matplotlib | Data visualization |

---

## Project Structure

market-trend-analyzer/
├── data/                         # SQLite DB + saved charts
├── collectors/
│   ├── stock_collector.py        # Fetch & store stock data
│   └── realestate_collector.py   # Fetch & store real estate data
├── db/
│   ├── schema.sql                # Table definitions
│   ├── db_connect.py             # DB connection helper
│   └── queries.py                # SQL trend queries
├── analysis/
│   ├── stock_analysis.py         # Moving averages + trend signals
│   └── realestate_analysis.py    # Rent yield + market signals
├── visualize/
│   └── plots.py                  # Matplotlib charts
├── main.py                       # Full pipeline runner
└── requirements.txt
---

## Sample Output
```text
[1/6] Initializing database...
[2/6] Collecting stock data...
[3/6] Collecting real estate data...
[4/6] Analyzing stock trends...

===== Stock Trend Summary =====
  AAPL   | Close:   189.30 | MA7:   191.20 | MA30:   185.40 | Trend: Bullish
  GOOGL  | Close:   141.80 | MA7:   140.10 | MA30:   138.90 | Trend: Bullish
  MSFT   | Close:   378.50 | MA7:   375.20 | MA30:   372.10 | Trend: Bullish
  TSLA   | Close:   245.60 | MA7:   248.30 | MA30:   261.80 | Trend: Bearish

===== Real Estate Trend Summary =====
  Mumbai       | Avg Price: ₹18,500,000 | Rent Yield: 2.92% | Signal: Rent market
  Bangalore    | Avg Price: ₹ 9,500,000 | Rent Yield: 4.04% | Signal: Rent market
```

---

## Charts Generated

- `data/stock_trends.png` — 6-month price + moving averages per stock
- `data/realestate_comparison.png` — Price, rent, yield by city
- `data/volatility.png` — 7-day rolling volatility per stock

---

## Author

**[Vibhor Hedau]**  
[LinkedIn]((https://www.linkedin.com/in/vibhor-hedau-1b7911160/)) • [GitHub]((https://github.com/vibhorhedau))

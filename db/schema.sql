CREATE TABLE IF NOT EXISTS stocks (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol    TEXT NOT NULL,
    date      DATE NOT NULL,
    open      REAL,
    close     REAL,
    high      REAL,
    low       REAL,
    volume    INTEGER,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS real_estate (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    city           TEXT NOT NULL,
    state          TEXT,
    date           DATE NOT NULL,
    avg_price      REAL,
    avg_rent       REAL,
    listings_count INTEGER,
    fetched_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

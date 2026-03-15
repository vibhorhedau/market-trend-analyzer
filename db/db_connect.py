import sqlite3
import os

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/market.db")
    return conn

def init_db():
    conn = get_connection()
    with open("db/schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    print("Database initialized.")

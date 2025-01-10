import sqlite3
import csv
import os
from config.configs import DB_PATH, CSV_PATH

def create_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS addresses (id INTEGER PRIMARY KEY, address TEXT)")
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            addr = line.strip()
            cursor.execute("INSERT INTO addresses (address) VALUES (?)", (addr,))
    conn.commit()
    conn.close()

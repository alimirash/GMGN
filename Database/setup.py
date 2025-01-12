import sqlite3
import csv
import os
from config.configs import DB_PATH, CSV_PATH

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT UNIQUE NOT NULL
        )
    """)

    with open(CSV_PATH, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        addresses = [(row[0],) for row in reader]
        cursor.executemany("INSERT OR IGNORE INTO addresses (address) VALUES (?)", addresses)
    conn.commit()
    conn.close()

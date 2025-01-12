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
    conn.commit()
    conn.close()

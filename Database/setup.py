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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT UNIQUE NOT NULL,
            winrate REAL,
            pnl REAL,
            pnl_7d REAL,
            pnl_30d REAL,
            realized_profit REAL,
            realized_profit_7d REAL,
            realized_profit_30d REAL,
            unrealized_profit REAL,
            unrealized_pnl REAL,
            eth_balance REAL,
            sol_balance REAL,
            trx_balance REAL,
            balance REAL,
            total_value REAL,
            all_pnl REAL,
            total_profit REAL,
            total_profit_pnl REAL,
            buy_30d INTEGER,
            sell_30d INTEGER,
            buy_7d INTEGER,
            sell_7d INTEGER,
            buy INTEGER,
            sell INTEGER,
            history_bought_cost REAL,
            token_avg_cost REAL,
            token_sold_avg_profit REAL,
            token_num INTEGER,
            profit_num INTEGER,
            pnl_lt_minus_dot5_num INTEGER,
            pnl_minus_dot5_0x_num INTEGER,
            pnl_lt_2x_num INTEGER,
            pnl_2x_5x_num INTEGER,
            pnl_gt_5x_num INTEGER,
            last_active_timestamp INTEGER,
            tags TEXT,
            tag_rank TEXT,
            followers_count INTEGER,
            is_contract BOOLEAN,
            updated_at INTEGER,
            refresh_requested_at TEXT,
            avg_holding_peroid INTEGER,
            name TEXT,
            avatar TEXT,
            ens TEXT,
            twitter_bind BOOLEAN,
            twitter_fans_num INTEGER,
            twitter_username TEXT,
            twitter_name TEXT
        )
    """)

    with open(CSV_PATH, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        addresses = [(row[0],) for row in reader]
        cursor.executemany("INSERT OR IGNORE INTO addresses (address) VALUES (?)", addresses)
    conn.commit()
    conn.close()

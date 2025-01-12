import time
import sqlite3
import os
from Database.setup import create_db
from Database.update import execute_bot
from Scrap.wallet_activity import wallet_scrap
from config.configs import DB_PATH


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    db = conn.cursor()
    create_db()
    execute_bot()
   

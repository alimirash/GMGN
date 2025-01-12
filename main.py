import time
import sqlite3
import os
from Database.setup import create_db
from Database.update import run_bot
from Scrap.wallet_activity import wallet_scrap
from config.configs import DB_PATH


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    db = conn.cursor()

    # create_db()
    run_bot()
    # db.execute("""SELECT * FROM addresses""")
    # addresses = db.fetchall()
    # for address in addresses:
    #     wallet_scrap(address[1])
    #     time.sleep(300)

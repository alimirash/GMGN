import time
import sqlite3
import os
from Database.setup import create_db
from Database.update import execute_bot
from Scrap.req_res import scrape_address
from Scrap.parse_address_details import extract_address_info
from config.configs import DB_PATH


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    db = conn.cursor()
    create_db()
    execute_bot()
    response=scrape_address(address="0x")
    extract_address_info("0x",response)

   

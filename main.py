from Database.setup import create_db
from Bot.main_handlers import execute_bot

if __name__ == "__main__":
    print("Bot is Running ...")
    create_db()
    execute_bot()
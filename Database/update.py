import sqlite3
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config.configs import TELEGRAM_BOT_TOKEN, DB_PATH

async def start(update, context):
    await update.message.reply_text("Send me an address to add.")

async def add_address(update, context):
    address = update.message.text.strip()
    if not (len(address) == 44):
        await update.message.reply_text("It's not the correct wallet address format.")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    row = cursor.execute("SELECT 1 FROM addresses WHERE address = ?", (address,)).fetchone()
    if row:
        await update.message.reply_text("We are already tracking this wallet.")
    else:
        cursor.execute("INSERT INTO addresses (address) VALUES (?)", (address,))
        conn.commit()
        await update.message.reply_text(f"Address `{address}` added.")
    conn.close()

def run_bot():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_address))
    application.run_polling()

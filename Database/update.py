import sqlite3
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler
)
from config.configs import TELEGRAM_BOT_TOKEN, DB_PATH
from Scrap.wallet_activity import wallet_scrap
from Database.setup import create_db
AWAITING_VALID_ADDRESS = 1


async def start(update, context):
    await update.message.reply_text(
        "Welcome to the wallet tracker bot!\n"
        "Use the following commands:\n"
        "/add_address - Add New Wallet Address\n"
        "/list_addresses - See tracked addresses\n"
        "/get_result <address> - Scrape a single address\n"
        "/scrap_all - Scrape all tracked addresses\n"
        "Send me a wallet address to add."
    )


async def add_address(update, context):
    await update.message.reply_text("Please enter the wallet address you want to add:")
    return AWAITING_VALID_ADDRESS


async def process_address(update, context):
    address = update.message.text.strip()

    if len(address) > 40:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        row = cursor.execute(
            "SELECT 1 FROM addresses WHERE address = ?", (address,)).fetchone()

        if row:
            await update.message.reply_text("This wallet is already being tracked.")
        else:
            cursor.execute(
                "INSERT INTO addresses (address) VALUES (?)", (address,))
            conn.commit()
            await update.message.reply_text(f"Address `{address}` added successfully.")

        conn.close()
    else:
        await update.message.reply_text("Invalid wallet address format. Please provide a valid address.")

    return AWAITING_VALID_ADDRESS


async def send_result(update, context):
    address = " ".join(context.args).strip()
    if not address:
        await update.message.reply_text("Please provide an address using /get_result <address>.")
        return

    # Re-scrape the address before sending results
    wallet_scrap(address)

    csv_path = os.path.join("results", f"{address}.csv")
    if os.path.exists(csv_path):
        with open(csv_path, "rb") as file:
            await update.message.reply_document(document=file, filename=f"{address}_{os.times}.csv")
    else:
        await update.message.reply_text("No results found for this address.")


async def list_addresses(update, context):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT address FROM addresses LIMIT 5")
    addresses = cursor.fetchall()
    conn.close()

    if not addresses:
        await update.message.reply_text("No addresses found. Use the 'Add New Address' option to add one.")
        return

    keyboard = [[InlineKeyboardButton(
        addr[0], callback_data=addr[0])] for addr in addresses]
    keyboard.append([InlineKeyboardButton(
        "Add New Address", callback_data="add_new_address")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select an address or add a new one:", reply_markup=reply_markup)


async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    address = query.data

    if address == "add_new_address":
        await query.message.reply_text("Please send the address you want to add:")
        context.user_data["awaiting_address"] = True
        return

    # Handle existing addresses
    csv_path = os.path.join("results", f"{address}.csv")
    if os.path.exists(csv_path):
        with open(csv_path, "rb") as file:
            await query.message.reply_document(document=file, filename=f"{address}.csv")
    else:
        await query.message.reply_text("No results found for this address.")


async def scrap_all(update, context):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT address FROM addresses")
    addresses = cursor.fetchall()
    conn.close()

    if not addresses:
        await update.message.reply_text("No addresses found.")
        return

    for (addr,) in addresses:
        wallet_scrap(addr)
        csv_path = os.path.join("results", f"{addr}.csv")
        if os.path.exists(csv_path):
            with open(csv_path, "rb") as file:
                await update.message.reply_document(document=file, filename=f"{addr}.csv")
        else:
            await update.message.reply_text(f"No results for {addr}.")


async def cancel(update, context):
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END


def run_bot():
    create_db()
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("add_address", add_address)],
        states={
            AWAITING_VALID_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    ))
    application.add_handler(CommandHandler("get_result", send_result))
    application.add_handler(CommandHandler("list_addresses", list_addresses))
    application.add_handler(CommandHandler("scrap_all", scrap_all))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()


if __name__ == "__main__":
    run_bot()

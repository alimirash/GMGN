import sqlite3
import os
import time
import telebot
from telebot import types
from config.configs import TELEGRAM_BOT_TOKEN, DB_PATH
from Scrap.req_res import scrape_address
from Database.setup import create_db
from datetime import datetime

AWAITING_VALID_ADDRESS = 1
AWAITING_SEND_RESULT = 1

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
user_states = {}  # to hold conversation states


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("Add Address", callback_data="ADD_ADDRESS"),
        types.InlineKeyboardButton(
            "List Addresses", callback_data="LIST_ADDRESSES")
    )
    keyboard.row(
        types.InlineKeyboardButton("Get Result", callback_data="GET_RESULT"),
        types.InlineKeyboardButton("Update All", callback_data="UPDATE_ALL")
    )
    keyboard.row(
        types.InlineKeyboardButton("Cancel", callback_data="CANCEL")
    )
    bot.send_message(
        message.chat.id,
        "<b>Welcome to the Wallet Tracker Bot!</b> 🤖\n\n"
        "Here's what I can do:\n"
        "• Track multiple wallet addresses\n"
        "• Scrape data for individual or all addresses\n"
        "• Provide CSV exports on demand\n\n"
        "Pick an option below or type /help for more commands.",
        parse_mode="HTML",
        reply_markup=keyboard
    )


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def address_exists(conn, address: str) -> bool:
    return conn.cursor().execute("SELECT 1 FROM addresses WHERE address = ?", (address,)).fetchone() is not None


def add_wallet_address_to_db(conn, address: str):
    conn.cursor().execute("INSERT INTO addresses (address) VALUES (?)", (address,))
    conn.commit()


def send_message(chat_id, text):
    bot.send_message(chat_id, text)


@bot.callback_query_handler(func=lambda call: True)
def button_handler(call):
    if call.data == "ADD_ADDRESS":
        bot.send_message(call.message.chat.id,
                         "Please enter the wallet address you want to add:")
        user_states[call.message.chat.id] = "AWAITING_VALID_ADDRESS"
    elif call.data == "LIST_ADDRESSES":
        list_tracked_addresses(call.message)
    elif call.data == "GET_RESULT":
        bot.send_message(call.message.chat.id,
                         "Please enter the wallet address you want to scrap:")
        user_states[call.message.chat.id] = "AWAITING_SEND_RESULT"
    elif call.data == "UPDATE_ALL":
        update_all_addresses(call.message)
    elif call.data == "CANCEL":
        cancel_operation(call.message)


@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "AWAITING_VALID_ADDRESS")
def handle_address_input(message):
    address = message.text.strip()

    if len(address) > 40:
        with get_db_connection() as conn:
            if address_exists(conn, address):
                send_message(message.chat.id,
                             "This wallet is already being tracked.")
            else:
                add_wallet_address_to_db(conn, address)
                send_message(message.chat.id,
                             f"Address `{address}` added successfully.")
    else:
        send_message(
            message.chat.id, "Invalid wallet address format. Please provide a valid address.")

    user_states[message.chat.id] = None  # reset state


@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "AWAITING_SEND_RESULT")
def process_scrape_result(message):
    address = message.text.strip()
    # we can offer to user use address in database

    if AWAITING_SEND_RESULT:
        with get_db_connection() as conn:
            if address_exists(conn, address):
                send_message(message.chat.id, "Awaiting, I'm Scraping . . .")
                scrape_address(address)
                send_message(message.chat.id, "Scraping successfully.")
            else:
                if len(address) > 40:
                    add_wallet_address_to_db(conn, address)
                    send_message(message.chat.id,
                                 f"Address `{address}` added successfully.")
                    send_message(message.chat.id,
                                 "Awaiting, I'm Scraping . . .")
                    scrape_address(address)
                    send_message(message.chat.id, "Scraping successfully.")
                    conn.commit()

        csv_path = os.path.join("results", "csv", f"{address}.csv")
        if os.path.exists(csv_path):
            with open(csv_path, "rb") as file:
                bot.send_document(
                    message.chat.id,
                    (f"{address}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv", file)
                )
        else:
            send_message(message.chat.id, "No results found for this address.")


@bot.message_handler(commands=['list_addresses'])
def list_tracked_addresses(message):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT address FROM addresses Limit 20")
        addresses = cursor.fetchall()

    if not addresses:
        send_message(
            message.chat.id, "No addresses found. Use the 'Add New Address' option to add one.")
        return

    addresses_text = "\n".join(f"`{address[0]}`" for address in addresses)
    bot.send_message(message.chat.id, f"Tracked Addresses:\n{addresses_text}")
    send_message(message.chat.id, "Use /add_address to add a new address.")


@bot.message_handler(commands=['update_all'])
def update_all_addresses(message):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT address FROM addresses")
        addresses = cursor.fetchall()

    if not addresses:
        send_message(message.chat.id, "No addresses found.")
        return
    
    for (addr,) in addresses:
        scrape_address(addr)
        time.sleep(40)
        csv_path = os.path.join("results", "csv", f"{addr}.csv")
        if os.path.exists(csv_path):
            with open(csv_path, "rb") as file:
                bot.send_document(
                    message.chat.id,
                    (f"{addr}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv", file)
                )
        else:
            send_message(message.chat.id, f"No results for {addr}.")


@bot.message_handler(commands=['cancel'])
def cancel_operation(message):
    send_message(message.chat.id, "Operation canceled.")
    user_states[message.chat.id] = None  # reset state


@bot.message_handler(commands=['help'])
def help_command(message):
    send_message(
        message.chat.id,
        "Available commands:\n"
        "/start - Start the bot\n"
        "/add_address - Add a new wallet address\n"
        "/list_addresses - List tracked addresses\n"
        "/get_result - Scrape a single address\n"
        "/update_all - Scrape all addresses\n"
        "/cancel - Cancel the current operation\n"
        "/help - Show help message"
    )


def execute_bot():
    create_db()
    bot.set_my_commands([
        telebot.types.BotCommand("start", "Start the bot"),
        telebot.types.BotCommand("add_address", "Add New Wallet Address"),
        telebot.types.BotCommand("list_addresses", "List tracked addresses"),
        telebot.types.BotCommand("get_result", "Scrape a single address"),
        telebot.types.BotCommand("update_all", "Update all addresses"),
        telebot.types.BotCommand("cancel", "Cancel operation"),
        telebot.types.BotCommand("help", "Show help message")
    ])
    bot.infinity_polling()

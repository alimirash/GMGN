import sqlite3

import random
import telebot
from telebot import types
from enum import Enum
from config.configs import TELEGRAM_BOT_TOKEN, DB_PATH
from Scrap.request_response import scrape_address
from Database.setup import create_db
from Bot.update_service import update_all_addresses, resume_update_addresses
from Bot.csv_service import send_results_csv
from Bot.db_service import drop_database


class UserState(Enum):
    AWAITING_VALID_ADDRESS = 1
    AWAITING_SEND_RESULT = 2
    UPDATING = 3
    AWAITING_CSV_UPLOAD = 4


bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
user_states = {}


def log_username(func):
    def wrapper(message, *args, **kwargs):
        print(message.from_user.username)
        return func(message, *args, **kwargs)
    return wrapper


# def human_likely_delay():
#     return random.randint(1, 2)


def _fetch_db_connection():
    return sqlite3.connect(DB_PATH)


def _is_address_present(conn, address: str) -> bool:
    return conn.cursor().execute("SELECT 1 FROM addresses WHERE address = ?", (address,)).fetchone() is not None


def _insert_wallet_address(conn, address: str):
    conn.cursor().execute("INSERT INTO addresses (address) VALUES (?)", (address,))
    conn.commit()


def _send_message(chat_id, text):
    bot.send_message(chat_id, text)


@bot.message_handler(commands=['start'])
@log_username
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
        types.InlineKeyboardButton(
            "Upload CSV", callback_data="UPLOAD_CSV"),  # Existing button
        types.InlineKeyboardButton(
            "Download CSV", callback_data="DOWNLOAD_CSV"),  # New button
    )
    keyboard.row(
        types.InlineKeyboardButton("Drop DB", callback_data="DROP_DB"),
        types.InlineKeyboardButton("Cancel", callback_data="CANCEL")
    )
    keyboard.row(
        types.InlineKeyboardButton(
            "Resume Update", callback_data="RESUME_UPDATE")
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


@bot.message_handler(commands=['help'])
@log_username
def help_command(message):
    _send_message(
        message.chat.id,
        "Available commands:\n"
        "/start - Start the bot\n"
        "/add_address - Add a new wallet address\n"
        "/list_addresses - List tracked addresses\n"
        "/get_result - Scrape a single address\n"
        "/update_all - Scrape all addresses\n"
        "/download_csv - Download the results as CSV\n"
        "/cancel - Cancel the current operation\n"
        "/help - Show help message"
    )


@bot.callback_query_handler(func=lambda call: True)
def manage_user_requests(call):
    if call.data == "ADD_ADDRESS":
        bot.send_message(call.message.chat.id,
                         "Please enter the wallet address you want to add:")
        user_states[call.message.chat.id] = UserState.AWAITING_VALID_ADDRESS
    elif call.data == "LIST_ADDRESSES":
        list_tracked_addresses(call.message)
    elif call.data == "GET_RESULT":
        bot.send_message(call.message.chat.id,
                         "Please enter the wallet address you want to scrap:")
        user_states[call.message.chat.id] = UserState.AWAITING_SEND_RESULT
    elif call.data == "UPDATE_ALL":
        update_all_addresses(call.message)
    elif call.data == "UPLOAD_CSV":
        bot.send_message(call.message.chat.id, "Please send the CSV file.")
        user_states[call.message.chat.id] = UserState.AWAITING_CSV_UPLOAD
    elif call.data == "DOWNLOAD_CSV":
        send_results_csv(call.message.chat.id)
    elif call.data == "DROP_DB":
        drop_database(call.message)
    elif call.data == "CANCEL":
        cancel_operation(call.message)
    elif call.data == "RESUME_UPDATE":
        resume_update_addresses(call.message)


@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == UserState.AWAITING_VALID_ADDRESS)
def check_and_save_address(message):
    address = message.text.strip()

    if len(address) > 40:
        with _fetch_db_connection() as conn:
            if _is_address_present(conn, address):
                _send_message(message.chat.id,
                              "This wallet is already being tracked.")
            else:
                _insert_wallet_address(conn, address)
                _send_message(message.chat.id,
                              f"Address `{address}` added successfully.")
    else:
        _send_message(
            message.chat.id, "Invalid wallet address format. Please provide a valid address.")

    user_states[message.chat.id] = None


@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == UserState.AWAITING_SEND_RESULT)
def process_scrape_result(message):
    address = message.text.strip()

    if UserState.AWAITING_SEND_RESULT:
        with _fetch_db_connection() as conn:
            if _is_address_present(conn, address):
                _send_message(message.chat.id, "Awaiting, I'm Scraping . . .")
                status = scrape_address(address)
                _send_message(message.chat.id, f"Scraping {status}.")
            else:
                if len(address) > 40:
                    _insert_wallet_address(conn, address)
                    _send_message(message.chat.id,
                                  f"Address `{address}` added successfully.")
                    _send_message(message.chat.id,
                                  "Awaiting, I'm Scraping . . .")
                    status = scrape_address(address)
                    _send_message(message.chat.id, f"Scraping {status}.")
                    conn.commit()

    try:
        conn = _fetch_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM results WHERE address = ?", (address,))
        result = cursor.fetchone()
        if result:
            result_text = f"Results for `{address}`:\n"
            columns = [description[0] for description in cursor.description]
            for col, val in zip(columns, result):
                result_text += f"{col}: {val}\n"
            _send_message(message.chat.id, result_text)
        else:
            _send_message(message.chat.id,
                          "No results found for this address.")
    except sqlite3.Error as e:
        _send_message(message.chat.id, f"Database error: {e}")
    finally:
        conn.close()

    user_states[message.chat.id] = None


@bot.message_handler(commands=['list_addresses'])
@log_username
def list_tracked_addresses(message):
    with _fetch_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT address FROM addresses Limit 20")
        addresses = cursor.fetchall()

    if not addresses:
        _send_message(
            message.chat.id, "No addresses found. Use the 'Add New Address' option to add one.")
        return

    addresses_text = "\n".join(f"`{address[0]}`" for address in addresses)
    bot.send_message(message.chat.id, f"Tracked Addresses:\n{addresses_text}")
    _send_message(message.chat.id,
                  "Use /get_result to get result of wallet address.")


@bot.message_handler(commands=['cancel'])
@log_username
def cancel_operation(message):
    user_states[message.chat.id] = None


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

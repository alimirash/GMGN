
import time
from Scrap.request_response import scrape_address
# ...existing imports (if needed)...


def update_all_addresses(message, bot, user_states, UserState, _fetch_db_connection, _send_message, human_likely_delay):
    user_states[message.chat.id] = UserState.UPDATING
    with _fetch_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT address FROM addresses")
        addresses = cursor.fetchall()

    if not addresses:
        _send_message(message.chat.id, "No addresses found.")
        user_states[message.chat.id] = None
        return

    total = len(addresses)
    status_message = bot.send_message(
        message.chat.id, "Starting update... 0% completed.")
    status_message_id = status_message.message_id

    for idx, (addr,) in enumerate(addresses, start=1):
        if user_states.get(message.chat.id) != UserState.UPDATING:
            bot.edit_message_text(
                "Update canceled.", chat_id=message.chat.id, message_id=status_message_id)
            break
        scrape_address(addr)
        percent = int((idx / total) * 100)
        bot.edit_message_text(f"Updating addresses: {percent}% completed.\nLast updated: `{addr}`",
                              chat_id=message.chat.id,
                              message_id=status_message_id)
        # time.sleep(human_likely_delay())

    else:
        bot.edit_message_text("Update completed successfully.",
                              chat_id=message.chat.id, message_id=status_message_id)

    user_states[message.chat.id] = None


def resume_update_addresses(message, bot, user_states, UserState, _fetch_db_connection, _send_message, human_likely_delay):
    with _fetch_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.address
            FROM addresses a
            LEFT JOIN results r ON a.address = r.address
            WHERE r.address IS NULL
        """)
        missing = cursor.fetchall()

    if not missing:
        _send_message(message.chat.id, "All addresses have results.")
        return

    user_states[message.chat.id] = UserState.UPDATING
    total = len(missing)
    status_message = bot.send_message(
        message.chat.id, "Resuming update... 0% completed.")
    status_message_id = status_message.message_id

    for idx, (addr,) in enumerate(missing, start=1):
        if user_states.get(message.chat.id) != UserState.UPDATING:
            bot.edit_message_text(
                "Resume update canceled.",
                chat_id=message.chat.id,
                message_id=status_message_id
            )
            break
        scrape_address(addr)
        percent = int((idx / total) * 100)
        bot.edit_message_text(
            f"Resuming update: {percent}% completed.\nLast updated: `{addr}`",
            chat_id=message.chat.id,
            message_id=status_message_id
        )
        # time.sleep(human_likely_delay())
    else:
        bot.edit_message_text(
            "Resume update completed successfully.",
            chat_id=message.chat.id,
            message_id=status_message_id
        )

    user_states[message.chat.id] = None

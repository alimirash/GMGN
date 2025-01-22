
import csv
import os
# ...existing imports (if needed)...


def send_results_csv(chat_id, bot, _fetch_db_connection):
    with _fetch_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM results")
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

    with open("results.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        writer.writerows(results)

    with open("results.csv", "rb") as file:
        bot.send_document(chat_id, file)
    os.remove("results.csv")


def handle_csv_upload(message, bot, user_states, UserState, _fetch_db_connection, _is_address_present, _insert_wallet_address):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    csv_data = downloaded_file.decode('utf-8').splitlines()
    reader = csv.reader(csv_data)
    with _fetch_db_connection() as conn:
        for row in reader:
            address = row[0].strip()
            if len(address) > 40 and not _is_address_present(conn, address):
                _insert_wallet_address(conn, address)
    bot.send_message(
        message.chat.id, "CSV data has been imported successfully.")
    user_states[message.chat.id] = None

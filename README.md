# GMGN

## Overview
GMGN is a web scraping project designed to track wallet activities on the GMGN platform. It uses Selenium for web scraping and integrates with a Telegram bot to manage wallet addresses.

## Features
- Scrape wallet activity data from GMGN.
- Store wallet addresses in a SQLite database.
- Add wallet addresses via a Telegram bot.
- Retrieve and display XHR responses from the web scraping process.

## Requirements
- Python 3.8+
- Selenium 4.27.1
- Pandas 2.2.3
- Webdriver Manager 4.0.2
- Python Telegram Bot 21.10
- Fake UserAgent

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/GMGN.git
    cd GMGN
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up the SQLite database:
    ```sh
    python -m Database.setup
    ```

## Usage
1. Start the web scraping script:
    ```sh
    python Scrap/wallet_activity.py
    ```

2. Run the Telegram bot:
    ```sh
    python main.py
    ```

## Configuration
- Ensure you have a valid Telegram bot token and update the `config/configs.py` file with your token and database path.

## File Structure
```
GMGN/
├── Database/
│   ├── setup.py
│   ├── update.py
├── Scrap/
│   ├── wallet_activity.py
├── Data/
│   ├── address.csv
├── config/
│   ├── configs.py
├── .gitignore
├── README.md
├── requirements.txt
├── main.py
```

## License
This project is licensed under the MIT License.
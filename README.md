# GMGN Project

![GitHub repo size](https://img.shields.io/github/repo-size/alimirash/GMGN)
![GitHub contributors](https://img.shields.io/github/contributors/alimirash/GMGN)
![GitHub stars](https://img.shields.io/github/stars/alimirash/GMGN?style=social)
![GitHub forks](https://img.shields.io/github/forks/alimirash/GMGN?style=social)

## Overview
GMGN is a simple yet powerful solution for collecting, tracking, and analyzing on-chain data. It fetches information from various blockchains, stores them in a local database, and provides commands for quickly retrieving or updating wallet data.

## Features
- Manage multiple wallet addresses
- Retrieve token balances, PnL, and other on-chain metrics
- Update and retrieve data via Telegram Bot
- Export results to CSV for quick sharing or further analysis

## Directory Structure
- **Scrap/**: Contains scraping scripts (request/response logic, address parsing)
- **Database/**: Database setup and migration scripts
- **Bot/**: Telegram bot handlers, including main interface and services
- **config/**: Global configurations (DB paths, tokens, etc.)

## Requirements
- Python 3.9+
- Required libraries are listed in requirements.txt (PyJWT, cloudscraper, etc.)
- A Telegram bot token (see configs.py)

## Installation
1. Clone or download this repository.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Edit configs.py to set your own DB_PATH, CSV_PATH, and TELEGRAM_BOT_TOKEN.

## Usage
1. Run main.py to initialize the bot:
   ```
   python main.py
   ```
2. Interact with the bot via Telegram to add wallet addresses, scrape results, and export data.

## Contributing
Contributions are welcome! Please create a pull request for any improvements or bug fixes.

## License
MIT License
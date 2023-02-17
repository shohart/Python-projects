# SQL Diary Telegram Bot

- [SQL Diary Telegram Bot](#sql-diary-telegram-bot)
  - [Requirements](#requirements)
  - [How to run](#how-to-run)
  - [Bot commands](#bot-commands)
  - [Notes](#notes)

This is a telegram bot that helps users keep a daily diary by writing entries and viewing previous entries, all stored in an SQL database. The bot uses the python [aiogram](https://docs.aiogram.io/en/latest/index.html) library for the telegram bot API. Bot encrypts messages in database using password, provided by user.

## Requirements

- Python 3.7+
- aiogram 2.24
- aiohttp 3.8.3
- aiosignal 1.3.1
- async-timeout 4.0.2
- attrs 22.2.0
- Babel 2.9.1
- bcrypt 4.0.1
- certifi 2022.12.7
- cffi 1.15.1
- charset-normalizer 2.1.1
- cryptography 39.0.0
- frozenlist 1.3.3
- idna 3.4
- magic-filter 1.0.9
- multidict 6.0.4
- passlib 1.7.4
- pycparser 2.21
- python-dateutil 2.8.2
- pytz 2022.7.1
- requests 2.28.2
- six 1.16.0
- urllib3 1.26.14
- yarl 1.8.2

## How to run

1. Get a telegram bot API key by talking to [@BotFather](https://telegram.me/BotFather)
2. Save the API key as `TELEGRAM_API_KEY` in a `config.ini` file in the following format:

   ```ini
   [DEFAULT]
   TELEGRAM_API_KEY = <API_KEY>
   DEBUG = False
   ```

3. Run the bot using:

   ```sh
   python diary_bot.py
   ```

## Bot commands

- **/start** - start the bot and either register or choose an action if already registered
- **/delete_user** - delete current user account with all the data.

## Notes

The SQL diary database will be created as **sql_diary.db** the first time the bot is run.

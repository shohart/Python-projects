# SQL Diary Telegram Bot

- [SQL Diary Telegram Bot](#sql-diary-telegram-bot)
  - [Requirements](#requirements)
  - [How to run](#how-to-run)
  - [Bot commands](#bot-commands)
  - [Notes](#notes)

This is a telegram bot that helps users keep a daily diary by writing entries and viewing previous entries, all stored in an SQL database. The bot uses the python [aiogram](https://docs.aiogram.io/en/latest/index.html) library for the telegram bot API. Bot encrypts messages in database using password, provided by user.

## Requirements

- Python 3.7+
- aiogram
- configparser
- logging
- datetime
- os

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
- **/register** - register with the bot
- **/cancel** - cancel any action
- **/add_entry** - add a new diary entry
- **/view_previous** - view previous diary entries

## Notes

The SQL diary database will be created as **sql_diary.db** the first time the bot is run.

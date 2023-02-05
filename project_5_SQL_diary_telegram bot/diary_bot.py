import time
import os
import configparser
import logging
from datetime import datetime as dt
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

import sql_diary_tg as diary

if os.path.exists("config.ini"):
    config = configparser.ConfigParser()
    config.read("config.ini")

    TELEGRAM_API_KEY = config["DEFAULT"]["TELEGRAM_API_KEY"]
    DEBUG = config["DEFAULT"].getboolean("DEBUG")
else:
    raise Exception("config.ini file not found!")


bot = Bot(token=TELEGRAM_API_KEY)

db_name = "sql_diary.db"
db = diary.Database(db_name)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

# keyboards
kb_reg = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
kb_reg.add("/register")
kb_reg.add("/cancel")

kb_main = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
kb_main.add("/add_entry", "/view_previous")
kb_main.add("/cancel")

kb_clear = types.ReplyKeyboardRemove()

kb_gender = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
kb_gender.add("Male", "Female")
kb_gender.add("Other")
kb_gender.add("/cancel")

kb_read = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
kb_read.add("1", "5", "10", "Custom date")
kb_read.add("/cancel")

kb_mood = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
kb_mood.add("Don't ask", "Bad", "Will do", "Good", "Amazing!")
kb_mood.add("/cancel")


# States
class Form(StatesGroup):
    password = State()
    birth_year = State()
    gender = State()
    email = State()


class WriteStates(StatesGroup):
    password = State()
    mood = State()
    msg_entry = State()


class ReadStates(StatesGroup):
    password = State()
    read_entry = State()
    custom_date = State()


# Handling of initial message
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f"{user_id} {user_full_name} {time.asctime()} started bot.")

    if not db.check_user(user_id):
        await bot.send_message(
            message.chat.id,
            f"Hello, {user_full_name}! You need to register!",
            reply_markup=kb_reg,
        )
    else:
        await bot.send_message(
            message.chat.id,
            f"Hello, {user_full_name}! Choose an action:",
            reply_markup=kb_main,
        )


# Allowing user to cancel input
@dp.message_handler(state="*", commands="cancel")
@dp.message_handler(Text(equals="cancel", ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state {}".format(current_state))
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply(
        f"{user_id} {user_full_name} {time.asctime()} cancelled action.",
        reply_markup=kb_clear,
    )


# Handling registration
@dp.message_handler(commands=["register"])
async def register_handler(message: types.Message):
    user_full_name = message.from_user.full_name
    user_id = message.from_user.id
    if not db.check_user(user_full_name):
        # Set password
        await Form.password.set()
        await bot.send_message(
            message.chat.id, "Enter your password:", reply_markup=kb_clear
        )
        logging.info(
            f"{user_id} {user_full_name} {time.asctime()} started registration."
        )


@dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    """
    Process password
    """
    async with state.proxy() as data:
        data["password"] = message.text

    await Form.next()
    await bot.send_message(message.chat.id, "What year were you born?")


# Check age. Age gotta be digit
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.birth_year)
async def process_year_invalid(message: types.Message):
    """
    If birth_year is invalid
    """
    return await message.reply(
        "Born year gotta be a number.\nWhat year were you born? (digits only)"
    )


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.birth_year)
async def process_year(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(birth_year=int(message.text))
    await bot.send_message(
        message.chat.id, "What is your gender?", reply_markup=kb_gender
    )


@dp.message_handler(
    lambda message: message.text not in ["Male", "Female", "Other"], state=Form.gender
)
async def process_gender_invalid(message: types.Message):
    """
    In this example gender has to be one of: Male, Female, Other.
    """
    return await message.reply("Bad gender name. Choose your gender from the keyboard.")


@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["gender"] = message.text
        await Form.next()

        # And send message
        await bot.send_message(
            message.chat.id, "Please enter your email.", reply_markup=kb_clear
        )


@dp.message_handler(state=Form.email)
async def process_email(message: types.Message, state: FSMContext):
    """
    Process user email
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_name = message.from_user.first_name
    cur_year = int(dt.now().strftime("%Y"))
    async with state.proxy() as data:

        data["email"] = message.text

        db.create_user(
            user_full_name,
            data["birth_year"],
            data["email"],
            data["password"],
            user_id,
            data["gender"],
        )
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text("Hi! Nice to meet you,", md.bold(user_name) + "!"),
                md.text("You are now registered!"),
                md.text(
                    "Your age is: " + md.code(cur_year - data["birth_year"]),
                ),
                md.text("Gender:", md.bold(data["gender"])),
                md.text("Your email is:", data["email"]),
                md.text("You can choose action now:"),
                sep="\n",
            ),
            reply_markup=kb_main,
            parse_mode=ParseMode.MARKDOWN,
        )
        logging.info(
            f"{user_id} {user_full_name} {time.asctime()} registered successfully."
        )

    # Finish conversation
    await state.finish()


# Handling writing messages
@dp.message_handler(commands=["add_entry"])
async def add_entry_handler(message: types.Message):
    user_id = message.from_user.id

    if db.check_user(user_id):
        await WriteStates.password.set()
        await bot.send_message(
            message.chat.id, "Enter your password.", reply_markup=kb_clear
        )
    else:
        await bot.send_message(
            message.chat.id, "You need to register!", reply_markup=kb_clear
        )


@dp.message_handler(state=WriteStates.password)
async def process_password_msg(message: types.Message, state: FSMContext):
    """
    Process message password
    """
    user_id = message.from_user.id

    async with state.proxy() as data:
        data["password"] = message.text
    if db.check_password(user_id, message.text):
        await WriteStates.next()
        await bot.send_message(
            message.chat.id, "What is your mood?.", reply_markup=kb_mood
        )
    else:
        await message.reply(
            "Password is incorrect! Please enter correct password.",
            reply_markup=kb_clear,
        )


@dp.message_handler(
    lambda message: message.text
    not in ["Don't ask", "Bad", "Will do", "Good", "Amazing!"],
    state=WriteStates.mood,
)
async def process_mood_invalid(message: types.Message):
    """
    If mod entry not valid
    """
    return await message.reply(
        "This input one of the suggested.\n" "Enter a valid value."
    )


@dp.message_handler(state=WriteStates.mood)
async def process_mood(message: types.Message, state: FSMContext):
    """
    Process mood entry
    """
    async with state.proxy() as data:
        data["mood"] = message.text
        await bot.send_message(
            message.chat.id, "Enter your message.", reply_markup=kb_clear
        )
    await WriteStates.next()


@dp.message_handler(state=WriteStates.msg_entry)
async def process_new_entry(message: types.Message, state: FSMContext):
    """
    Process diary entry
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name

    async with state.proxy() as data:
        db.create_entry(
            user_full_name, user_id, message.text, data["password"], data["mood"]
        )

    logging.info(f"{user_id} {user_full_name} {time.asctime()} added new entry.")

    await bot.send_message(
        message.chat.id,
        "New diary entry created!",
        reply_markup=kb_main,
        parse_mode=ParseMode.MARKDOWN,
    )
    await state.finish()


# Handling reading messages
@dp.message_handler(commands=["view_previous"])
async def process_view_previous(message: types.Message):
    user_id = message.from_user.id

    if db.check_user(user_id):
        await ReadStates.password.set()
        await bot.send_message(
            message.chat.id, "Enter your password.", reply_markup=kb_clear
        )
    else:
        await bot.send_message(
            message.chat.id, "You need to register!", reply_markup=kb_clear
        )


@dp.message_handler(state=ReadStates.password)
async def process_password_read(message: types.Message, state: FSMContext):
    """
    Process message password to read
    """
    user_id = message.from_user.id
    async with state.proxy() as data:
        data["password"] = message.text
    if db.check_password(user_id, message.text):

        await bot.send_message(
            message.chat.id,
            "Select range to search for entries:",
            reply_markup=kb_read,
            parse_mode=ParseMode.MARKDOWN,
        )
        await ReadStates.next()
    else:
        await bot.send_message(
            message.chat.id, "Password is incorrect! Please enter correct password."
        )


@dp.message_handler(
    lambda message: not message.text.isdigit() and message.text != "Custom date",
    state=ReadStates.read_entry,
)
async def process_number_invalid(message: types.Message):
    """
    If read number of messages not valid
    """
    return await message.reply(
        "This input should be a number.\n"
        "Enter a digit or press 'Custom date' to enter date period."
    )


@dp.message_handler(state=ReadStates.read_entry)
async def process_read_period(message: types.Message, state: FSMContext):
    """
    Process message lookup
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_name = message.from_user.first_name

    async with state.proxy() as data:
        if message.text == "Custom date":

            await bot.send_message(
                message.chat.id,
                md.text(
                    md.text("You can specify date period in the following format:"),
                    md.text("YYYY-MM-DD - YYYY-MM-DD"),
                    sep="\n",
                ),
                reply_markup=kb_clear,
            )
            await ReadStates.custom_date.set()
        else:
            data = db.show_prev_entry(
                user_full_name, user_id, data["password"], int(message.text), offset=0
            )

            for date, msg, msg_time, mood in data:
                await bot.send_message(
                    message.chat.id,
                    md.text(
                        md.text("On", date, md.bold(user_name), "wrote:\n"),
                        md.text(msg),
                        md.text(
                            "\nTime:",
                            md.bold(msg_time) + ".",
                            "Mood:",
                            md.bold(mood) + ".",
                        ),
                        sep="\n",
                    ),
                    reply_markup=kb_main,
                    parse_mode=ParseMode.MARKDOWN,
                )
            # Finish conversation
            await state.finish()


@dp.message_handler(
    lambda message: message.text != r"\d{4}-\d{2}-\d{2} - \d{4}-\d{2}-\d{2}",
    state=ReadStates.read_entry,
)
async def process_custom_period_read_invalid(message: types.Message):
    """
    If read number of messages not valid
    """
    return await message.reply(
        "This input should be formatted as YYYY-MM-DD - YYYY-MM-DD.\n"
        "Eg. 2021-05-06 - 2022-06-01.\n"
    )


@dp.message_handler(state=ReadStates.custom_date)
async def process_custom_period(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_name = message.from_user.first_name
    begin, _, end = message.text.partition(" - ")
    async with state.proxy() as data:
        data = db.show_entries_range(
            user_full_name, user_id, data["password"], begin, end
        )

        for date, msg, msg_time, mood in data:
            await bot.send_message(
                message.chat.id,
                md.text(
                    md.text("On", date, md.bold(user_name), "wrote:\n"),
                    md.text(msg),
                    md.text(
                        "\nTime:", md.bold(msg_time) + ".", "Mood:", md.bold(mood) + "."
                    ),
                    sep="\n",
                ),
                reply_markup=kb_main,
                parse_mode=ParseMode.MARKDOWN,
            )
    # Finish conversation
    await state.finish()


if __name__ == "__main__":

    executor.start_polling(dp)

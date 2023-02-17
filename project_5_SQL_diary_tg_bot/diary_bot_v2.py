import time
import os
import re
import configparser
import logging
import datetime as dt
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

# from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

import sql_diary_tg as diary

from inline_calendar import InlineCalendar


# Check if config file exists.
if os.path.exists("config.ini"):
    config = configparser.ConfigParser()
    config.read("config.ini")

    TELEGRAM_API_KEY = config["DEFAULT"]["TELEGRAM_API_KEY"]
    DEBUG = config["DEFAULT"].getboolean("DEBUG")
else:
    raise Exception("config.ini file not found!")


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# initial variables
bot = Bot(token=TELEGRAM_API_KEY)
db_name = "sql_diary.db"
db = diary.Database(db_name)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

# defining keyboard buttons
buttons_dict = {
    "cancel": ("❌ Cancel", "cancel"),
    "reg": ("🔑 Register", "reg"),
    "add": ("📝 Add new", "add"),
    "view": ("📖 View old", "view"),
    "male": ("👨‍🦰 Male", "Male"),
    "female": ("👩‍🦰 Female", "Female"),
    "other": ("🤖👩‍🎤👨‍🎤 Other", "Other"),
    "one": ("1️⃣", "1"),
    "five": ("5️⃣", "5"),
    "ten": ("🔟", "10"),
    "custom": ("📆 Period", "custom"),
    "mood0": ("😭 Don't ask", "Don't ask"),
    "mood1": ("😥 Sad", "Sad"),
    "mood2": ("😐 Will do", "Will do"),
    "mood3": ("😊 Happy", "Happy"),
    "mood4": ("🤩 Amazing!", "Amazing"),
    "delete": ("☠️ Yes, DELETE!", "delete"),
    "approve": ("👌 Ok", "ok"),
    "hist": ("📄 Single", "prev"),
    "back": ("⬅️ Previous", "back"),
    "next": ("➡️ Next", "next"),
}


def create_keeb(*rows):
    """A function to create keyboards"""

    def create_row(buttons):
        """
        A function to create keyboard rows
        """
        return (
            types.InlineKeyboardButton(text, callback_data=data)
            for text, data in buttons
        )

    keeb = types.InlineKeyboardMarkup(row_width=3)
    rows = (create_row(x) for x in rows)
    for x in rows:
        keeb.row(*x)

    return keeb


def text_format(date, msg, msg_time, mood, user_name):
    """A function to format text

    Args:
        date (_type_): Date of the entry
        msg (_type_): Entry's body
        msg_time (_type_): Time of the entry
        mood (_type_): Mood of the entry
        user_name (_type_): name of the user od a diary

    Returns:
        str: A formatted text, containing all the data.
    """
    date_formatted = dt.datetime.strptime(date, "%Y-%m-%d").strftime("%d %B %Y")
    return md.text(
        md.text("On", md.bold(date_formatted), ", ", md.code(user_name), "wrote:\n"),
        md.text(msg),
        md.text(
            "\nTime:",
            md.bold(msg_time) + ".",
            "Mood:",
            md.bold(mood) + ".",
        ),
        sep="\n",
    )


def process_message(text, chat_id, replmk=None):
    """A function to process diary entry

    Args:
        chat_id (_type_): id of a chat to where send a message
        replymk (_type_): keyboard markup

    Returns:
        bot message: A formatted message, containing all the data.
    """
    return bot.send_message(
        chat_id,
        text,
        reply_markup=replmk,
        parse_mode=ParseMode.MARKDOWN,
    )


def ask_proceed(chat_id):
    """Ask a user for next actions

    Args:
        chat_id (str): id of a chat to where send a message

    Returns:
        bot_message: bot message, containing info
    """
    return bot.send_message(
        chat_id,
        "That was all messages for chosen period.\nDo you wand anything else?",
        reply_markup=kb_main,
    )


# creating keyboards
kb_reg = create_keeb((buttons_dict["reg"],))
kb_main = create_keeb((buttons_dict["add"], buttons_dict["view"]))
kb_cancel = create_keeb((buttons_dict["cancel"],))
kb_approve = create_keeb((buttons_dict["approve"], buttons_dict["cancel"]))
kb_gender = create_keeb(
    (buttons_dict["male"], buttons_dict["female"]),
    (buttons_dict["other"],),
    (buttons_dict["cancel"],),
)
kb_read = create_keeb(
    (buttons_dict["hist"], buttons_dict["custom"]),
    (buttons_dict["cancel"],),
)
kb_mood = create_keeb(
    (buttons_dict["mood0"],),
    (buttons_dict["mood1"], buttons_dict["mood2"], buttons_dict["mood3"]),
    (buttons_dict["mood4"],),
    (buttons_dict["cancel"],),
)
kb_del = create_keeb((buttons_dict["delete"], buttons_dict["cancel"]))
kb_list = create_keeb(
    (buttons_dict["back"], buttons_dict["next"]), (buttons_dict["cancel"],)
)
kb_list_start = create_keeb((buttons_dict["back"], buttons_dict["cancel"]))

# initialize calendar
inline_calendar = InlineCalendar()


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
    read_entry_num = State()
    custom_start = State()
    custom_end = State()
    custom_display = State()


class DeleteAcStates(StatesGroup):
    password = State()


# Handling keyboard events, using callback handlers
@dp.callback_query_handler(
    lambda call: call.data in [i[1] for i in buttons_dict.values()], state="*"
)
async def process_callback_query(
    callback_query: types.CallbackQuery, state: FSMContext
):
    """Process callback queries, except for calendar.

    Args:
        callback_query (types.CallbackQuery): Callbackquery object
        state (FSMContext): currents state object
    """
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    current_state = await state.get_state()
    user_full_name = callback_query.from_user.full_name
    user_name = callback_query.from_user.first_name

    await callback_query.answer(f"Processing your query {data!r}")

    if data == "reg":

        if not db.check_user(user_full_name):
            # Set password
            await Form.password.set()
            await bot.send_message(
                chat_id,
                "Enter your password:",
                reply_markup=kb_cancel,
            )
            logging.info(
                f"{user_id} {user_full_name} {time.asctime()} started registration."
            )

    elif data == "add":

        if db.check_user(user_id):
            await WriteStates.password.set()
            await bot.send_message(
                chat_id,
                "Enter your password.",
                reply_markup=kb_cancel,
            )
        else:
            await bot.send_message(
                chat_id,
                "You need to register!",
                reply_markup=kb_reg,
            )

    elif data == "view":

        if db.check_user(user_id):
            await ReadStates.password.set()
            await bot.send_message(
                chat_id,
                "Enter your password.",
                reply_markup=kb_cancel,
            )
        else:
            await bot.send_message(
                chat_id,
                "You need to register!",
                reply_markup=kb_reg,
            )

    elif data == "cancel":

        if current_state is None:
            return

        logging.info(
            "{} {} at {} cancelled state {}".format(
                user_id, user_full_name, time.asctime(), current_state
            )
        )

        # Cancel state and inform user about it
        await state.finish()
        # And remove keyboard (just in case)
        await bot.send_message(
            chat_id,
            "Cancelled. Choose an option:",
            reply_markup=kb_main,
        )

    elif data in ["Male", "Female", "Other"]:
        async with state.proxy() as storage_data:
            storage_data["gender"] = data
            await Form.next()

            # And send message
            await bot.send_message(
                chat_id, "Please enter your email.", reply_markup=kb_cancel
            )

    elif data in ["Don't ask", "Sad", "Will do", "Happy", "Amazing"]:
        async with state.proxy() as storage_data:
            storage_data["mood"] = data
            await bot.send_message(
                chat_id, "Enter your message.", reply_markup=kb_cancel
            )
        await WriteStates.next()

    elif data == "delete":
        db.remove_user(user_id)
        await bot.send_message(
            chat_id,
            "Your account has been DELETED. You can register again.",
            reply_markup=kb_reg,
        )
        # Finish conversation
        await state.finish()

    elif data in ["1", "5", "10"]:
        async with state.proxy() as storage_data:
            diary_data = db.show_prev_entry(
                user_full_name, user_id, storage_data["password"], int(data), offset=0
            )

            if not diary_data:
                await bot.send_message(
                    chat_id, "You have no messages to view!", reply_markup=kb_main
                )

            else:

                for date, msg, msg_time, mood in diary_data:
                    await process_message(
                        text_format(date, msg, msg_time, mood, user_name), chat_id
                    )

            await ask_proceed(chat_id)

            # Finish conversation
            await state.finish()

    elif data == "custom":

        period_in_weeks = int(db.get_user_bithdate(user_id)) * 52

        inline_calendar.init(
            dt.date.today(),
            dt.date.today() - dt.timedelta(weeks=period_in_weeks),
            dt.date.today(),
        )
        await ReadStates.custom_start.set()
        await bot.send_message(
            chat_id,
            md.text("Choose ", md.bold("START"), " date:"),
            reply_markup=inline_calendar.get_keyboard(),
            # reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN,
        )

    elif data == "ok":
        async with state.proxy() as storage_data:
            begin, end = storage_data["custom_start"], storage_data["custom_end"]
            diary_data = db.show_entries_range(
                user_full_name, user_id, storage_data["password"], begin, end
            )

            for date, msg, msg_time, mood in diary_data:
                await process_message(
                    text_format(date, msg, msg_time, mood, user_name), chat_id
                )

        await ask_proceed(chat_id)

        # Finish conversation
        await state.finish()

    elif data == "prev":
        await ReadStates.read_entry_num.set()
        async with state.proxy() as storage_data:
            storage_data["read_entry_num"] = 0

            diary_data = db.show_prev_entry(
                user_full_name,
                user_id,
                storage_data["password"],
                1,
                offset=storage_data["read_entry_num"],
            )

            if not diary_data:
                await bot.send_message(
                    chat_id, "You have no messages to view!", reply_markup=kb_main
                )

            else:
                for date, msg, msg_time, mood in diary_data:
                    await process_message(
                        text_format(date, msg, msg_time, mood, user_name),
                        chat_id,
                        kb_list_start,
                    )

    elif data in ["back", "next"]:
        await bot.answer_callback_query(callback_query.id)
        message_id = callback_query.message.message_id
        async with state.proxy() as storage_data:
            if data == "back":
                storage_data["read_entry_num"] += 1
            else:
                storage_data["read_entry_num"] -= 1

            diary_data = db.show_prev_entry(
                user_full_name,
                user_id,
                storage_data["password"],
                1,
                offset=storage_data["read_entry_num"],
            )

            if storage_data["read_entry_num"] == 0:
                repl_kbd = kb_list_start

            else:
                repl_kbd = kb_list

            if not diary_data:
                await bot.send_message(
                    chat_id,
                    "You have no messages to view for selected period!",
                    reply_markup=kb_read,
                )

            else:
                for date, msg, msg_time, mood in diary_data:
                    edit_msg = text_format(date, msg, msg_time, mood, user_name)
                await bot.edit_message_text(
                    text=edit_msg,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=repl_kbd,
                    parse_mode=ParseMode.MARKDOWN,
                )


# Handling choosing start date for custom calendar
@dp.callback_query_handler(inline_calendar.filter(), state=ReadStates.custom_start)
async def start_date_calendar_callback_handler(
    callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    await bot.answer_callback_query(callback_query.id)

    return_data = inline_calendar.handle_callback(user_id, callback_data)
    if return_data is None:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_calendar.get_keyboard(user_id),
        )
    else:
        picked_data = return_data
        async with state.proxy() as storage_data:
            storage_data["custom_start"] = picked_data
        await ReadStates.custom_end.set()
        await bot.edit_message_text(
            md.text("Choose ", md.bold("END"), " date:"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_calendar.get_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
            # reply_markup=types.ReplyKeyboardRemove(),
        )


# Handling end date for custom calendar
@dp.callback_query_handler(inline_calendar.filter(), state=ReadStates.custom_end)
async def end_date_calendar_callback_handler(
    callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    await bot.answer_callback_query(callback_query.id)

    return_data = inline_calendar.handle_callback(user_id, callback_data)
    if return_data is None:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=inline_calendar.get_keyboard(user_id),
        )
    else:
        picked_data = return_data
        async with state.proxy() as storage_data:
            storage_data["custom_end"] = picked_data
            start = storage_data["custom_start"]
            end = storage_data["custom_end"]
        await ReadStates.custom_display.set()
        await bot.send_message(
            chat_id,
            md.text(
                md.text("You chose period:\n"),
                md.text("From:\n") + "         " + md.bold(start.strftime("%d %B, %Y")),
                md.text("To:\n")
                + "         "
                + md.bold(end.strftime("%d %B, %Y") + "\n"),
                md.text("Is it correct?"),
                sep="\n",
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb_approve,
        )


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


# Handle user-delete command
@dp.message_handler(commands=["delete_user"])
async def delete_user_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    chat_id = message.chat.id
    logging.info(
        f"{user_id} {user_full_name} {time.asctime()} initialized account deletion."
    )

    if not db.check_user(user_id):
        await bot.send_message(
            message.chat.id,
            f"Whoa, {user_full_name}! You are not registered!",
            reply_markup=kb_reg,
        )
    else:
        await DeleteAcStates.password.set()
        await bot.send_message(
            chat_id,
            "Enter your password:",
            reply_markup=kb_cancel,
        )


# Handling registration
@dp.message_handler(state=Form.password)
async def reg_process_password(message: types.Message, state: FSMContext):
    """
    Process password
    """
    async with state.proxy() as data:
        data["password"] = message.text

    await Form.next()
    await bot.send_message(message.chat.id, "What year were you born?")


# Process password for user_delete state
@dp.message_handler(state=DeleteAcStates.password)
async def del_process_password(message: types.Message, state: FSMContext):
    """
    Process password
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    async with state.proxy() as data:
        data["password"] = message.text
        if db.check_password(user_id, message.text):
            await bot.send_message(
                chat_id,
                md.text(
                    md.text(md.bold(user_name), "!"),
                    md.text(
                        "Are you ",
                        md.bold("SURE"),
                        " you wand to ",
                        md.bold("DELETE"),
                        " your account?",
                    ),
                    md.text(
                        md.text("This will permanently delete, your account,"),
                        md.text("including all entries and all registration data."),
                        sep=" ",
                    ),
                    md.text(""),
                    md.text(md.bold("THIS CAN NOT BE UNDONE") + "!"),
                    sep="\n",
                ),
                reply_markup=kb_del,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await message.reply(
                "Password is incorrect! Please enter correct password.",
                reply_markup=kb_cancel,
            )


# Process password fro state "new message"
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
            message.chat.id, "What is your mood?", reply_markup=kb_mood
        )
    else:
        await message.reply(
            "Password is incorrect! Please enter correct password.",
            reply_markup=kb_cancel,
        )


# process password for Read state
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
            message.chat.id,
            "Password is incorrect! Please enter correct password.",
            reply_markup=kb_cancel,
        )


# Check age. Age gotta be digit
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.birth_year)
async def process_year_invalid(message: types.Message):
    """
    If birth_year is invalid
    """
    return await message.reply(
        "Born year gotta be a number.\nWhat year were you born? (digits only)"
    )


# Process user-input year
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.birth_year)
async def process_year(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(birth_year=int(message.text))
    await bot.send_message(
        message.chat.id, "What is your gender?", reply_markup=kb_gender
    )


# Process user-input gender
@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["gender"] = message.text
        await Form.next()

        # And send message
        await bot.send_message(
            message.chat.id, "Please enter your email.", reply_markup=kb_cancel
        )


# Check if email is of valid value
@dp.message_handler(
    lambda email: bool(
        re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)
    ),
    state=Form.email,
)
async def process_email_invalid(message: types.Message, state: FSMContext):
    """
    Process invalid email entry
    """
    return await message.reply(
        "This is not a valid email address! Please enter a correct one"
    )


# Process user-input email
@dp.message_handler(state=Form.email)
async def process_email(message: types.Message, state: FSMContext):
    """
    Process user email
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_name = message.from_user.first_name
    cur_year = int(dt.datetime.now().strftime("%Y"))
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


# Process mood for message
@dp.message_handler(state=WriteStates.mood)
async def process_mood(message: types.Message, state: FSMContext):
    """
    Process mood entry
    """
    async with state.proxy() as data:
        data["mood"] = message.text
        await bot.send_message(
            message.chat.id, "Enter your message.", reply_markup=kb_cancel
        )
    await WriteStates.next()


# process entered message
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


if __name__ == "__main__":

    executor.start_polling(dp)

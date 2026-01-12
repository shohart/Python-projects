import time
import os
import re
import io
import configparser
import logging
import datetime as dt

import matplotlib
import matplotlib.pyplot as plt
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
from translations import TRANSLATIONS

matplotlib.use("Agg")

def get_lang(language_code):
    if not language_code:
        return "en"
    return "ru" if language_code.lower().startswith("ru") else "en"


def tr(key, language_code, **kwargs):
    lang = get_lang(language_code)
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, "")
    return text.format(**kwargs)


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
db_name = os.getenv("SQL_DIARY_DB_PATH", "sql_diary.db")
db = diary.Database(db_name)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

# defining keyboard buttons
buttons_dict = {
    "cancel": ("❌ Cancel", "cancel"),
    "reg": ("🔑 Register", "reg"),
    "add": ("📝 Add entry", "add"),
    "view": ("📖 View entries", "view"),
    "stats": ("📊 Insights", "stats"),
    "male": ("👨‍🦰 Male", "Male"),
    "female": ("👩‍🦰 Female", "Female"),
    "other": ("🤖👩‍🎤👨‍🎤 Other", "Other"),
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


def ask_proceed(chat_id, language_code):
    """Ask a user for next actions

    Args:
        chat_id (str): id of a chat to where send a message

    Returns:
        bot_message: bot message, containing info
    """
    return bot.send_message(
        chat_id,
        tr("period_done", language_code),
        reply_markup=kb_main,
    )


def incorrect_password(message):
    """
    Reply for an incorrect password
    """
    return message.reply(
        tr("incorrect_password", message.from_user.language_code),
        reply_markup=kb_cancel,
    )


def not_registered(chat_id, language_code):
    return bot.send_message(
        chat_id,
        tr("register_needed", language_code),
        reply_markup=kb_reg,
    )


def ask_password(chat_id, language_code):
    return bot.send_message(
        chat_id,
        tr("enter_password", language_code),
        reply_markup=kb_cancel,
    )


def _chart_to_bytes(fig):
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def build_mood_chart(mood_stats):
    if not mood_stats:
        return None

    labels = [row[0] for row in mood_stats]
    values = [row[1] for row in mood_stats]
    colors = ["#6C63FF", "#F9A826", "#06D6A0", "#EF476F", "#118AB2"]

    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, values, color=colors[: len(labels)])
    ax.set_title("Mood snapshot", fontsize=14, weight="bold")
    ax.set_ylabel("Entries")
    ax.set_xlabel("Mood")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    return _chart_to_bytes(fig)


def build_entries_chart(entries_by_date):
    if not entries_by_date:
        return None

    dates = [row[0] for row in entries_by_date]
    values = [row[1] for row in entries_by_date]

    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(dates, values, marker="o", color="#6C63FF", linewidth=2)
    ax.fill_between(dates, values, alpha=0.2, color="#6C63FF")
    ax.set_title("Entries over time", fontsize=14, weight="bold")
    ax.set_ylabel("Entries")
    ax.set_xlabel("Date")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    return _chart_to_bytes(fig)


async def send_stats(chat_id, user_id, language_code):
    mood_stats = db.get_mood_stats(user_id) or []
    entries_by_date = db.get_entries_by_date(user_id, days_back=14) or []

    if not mood_stats and not entries_by_date:
        await bot.send_message(
            chat_id,
            tr("stats_empty", language_code),
            reply_markup=kb_main,
        )
        return

    mood_chart = build_mood_chart(mood_stats)
    entries_chart = build_entries_chart(entries_by_date)

    if mood_chart:
        await bot.send_photo(
            chat_id,
            mood_chart,
            caption=tr("stats_mood_caption", language_code),
            reply_markup=kb_main,
        )

    if entries_chart:
        await bot.send_photo(
            chat_id,
            entries_chart,
            caption=tr("stats_entries_caption", language_code),
            reply_markup=kb_main,
        )


# creating keyboards
kb_reg = create_keeb((buttons_dict["reg"],))
kb_main = create_keeb(
    (buttons_dict["add"], buttons_dict["view"]),
    (buttons_dict["stats"],),
)
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


class StatsStates(StatesGroup):
    password = State()


# Handling keyboard events, using callback handlers
@dp.callback_query_handler(
    lambda call: call.data in [i[1] for i in buttons_dict.values()]
    and call.data not in ["Male", "Female", "Other"],
    state="*",
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
    language_code = callback_query.from_user.language_code

    await callback_query.answer(tr("processing_query", language_code, query=data))

    if data == "reg":

        if not db.check_user(user_id):
            # Set password
            await Form.password.set()
            await ask_password(chat_id, language_code)
            logging.info(
                f"{user_id} {user_full_name} {time.asctime()} started registration."
            )
        else:
            await bot.send_message(
                chat_id,
                tr("already_registered", language_code),
                reply_markup=kb_main,
            )

    elif data == "add":

        if db.check_user(user_id):
            await WriteStates.password.set()
            await bot.send_message(
                chat_id,
                tr("enter_password_prompt", language_code),
                reply_markup=kb_cancel,
            )
        else:
            await not_registered(chat_id, language_code)

    elif data == "view":

        if db.check_user(user_id):
            await ReadStates.password.set()
            await ask_password(chat_id, language_code)
        else:
            await not_registered(chat_id, language_code)

    elif data == "stats":

        if db.check_user(user_id):
            await StatsStates.password.set()
            await ask_password(chat_id, language_code)
        else:
            await not_registered(chat_id, language_code)

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

        if not db.check_user(user_id):
            await bot.send_message(
                chat_id,
                tr("cancelled", language_code),
                reply_markup=kb_reg,
            )
        else:
            await bot.send_message(
                chat_id,
                tr("cancelled_choose", language_code),
                reply_markup=kb_main,
            )

    elif data in ["Don't ask", "Sad", "Will do", "Happy", "Amazing"]:
        async with state.proxy() as storage_data:
            try:
                storage_data["mood"] = data
                await bot.send_message(
                    chat_id,
                    tr("add_message_prompt", language_code),
                    reply_markup=kb_cancel,
                )
                await WriteStates.next()
            except KeyError():
                await bot.send_message(chat_id, tr("error_acquired", language_code))
                await state.finish()

    elif data == "delete":
        try:
            db.remove_user(user_id)
            await bot.send_message(
                chat_id,
                tr("delete_done", language_code),
                reply_markup=kb_reg,
            )
            logging.info(
                f"{user_id} {user_full_name} {time.asctime()} successfully deleted."
            )
        except KeyError():
            await bot.send_message(chat_id, tr("error_acquired", language_code))
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
            md.text(tr("choose_start_date", language_code)),
            reply_markup=inline_calendar.get_keyboard(),
            # reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN,
        )

    elif data == "prev":
        await ReadStates.read_entry_num.set()
        async with state.proxy() as storage_data:
            storage_data["read_entry_num"] = 0

            try:
                diary_data = db.show_prev_entry(
                    user_full_name,
                    user_id,
                    storage_data["password"],
                    1,
                    offset=storage_data["read_entry_num"],
                )
            except KeyError():
                await bot.send_message(chat_id, tr("error_acquired", language_code))

                # Finish conversation
                await state.finish()

                await ask_proceed(chat_id, language_code)

                # Finish conversation
                await state.finish()

            if not diary_data:
                await bot.send_message(
                    chat_id,
                    tr("no_messages", language_code),
                    reply_markup=kb_main,
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

            try:
                diary_data = db.show_prev_entry(
                    user_full_name,
                    user_id,
                    storage_data["password"],
                    1,
                    offset=storage_data["read_entry_num"],
                )

            except KeyError():
                await bot.send_message(chat_id, tr("error_acquired", language_code))

                # Finish conversation
                await state.finish()

                await ask_proceed(chat_id, language_code)

                # Finish conversation
                await state.finish()

            if storage_data["read_entry_num"] == 0:
                repl_kbd = kb_list_start

            else:
                repl_kbd = kb_list

            if not diary_data:
                await bot.send_message(
                    chat_id,
                    tr("no_messages_period", language_code),
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


# Handling gender button
@dp.callback_query_handler(
    lambda call: call.data in ["Male", "Female", "Other"], state=Form.gender
)
async def process_gender_button(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    language_code = callback_query.from_user.language_code
    async with state.proxy() as storage_data:
        try:
            storage_data["gender"] = data
            await Form.email.set()

            # And send message
            await bot.send_message(
                chat_id,
                tr("register_email", language_code),
                reply_markup=kb_cancel,
            )

        except KeyError():
            await bot.send_message(chat_id, tr("error_acquired", language_code))
            await state.finish()


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
        language_code = callback_query.from_user.language_code
        await bot.edit_message_text(
            md.text(tr("choose_end_date", language_code)),
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
    user_full_name = callback_query.from_user.full_name
    user_name = callback_query.from_user.first_name
    language_code = callback_query.from_user.language_code
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
        # await ReadStates.custom_display.set()
        async with state.proxy() as storage_data:
            begin, end = storage_data["custom_start"], storage_data["custom_end"]

            try:
                diary_data = db.show_entries_range(
                    user_full_name, user_id, storage_data["password"], begin, end
                )

            except KeyError():
                await bot.send_message(chat_id, tr("error_acquired", language_code))

                # Finish conversation
                await state.finish()

                await ask_proceed(chat_id, language_code)

                # Finish conversation
                await state.finish()

            for date, msg, msg_time, mood in diary_data:
                await process_message(
                    text_format(date, msg, msg_time, mood, user_name), chat_id
                )

        await ask_proceed(chat_id, language_code)

        # Finish conversation
        await state.finish()


# Handling of initial message
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    language_code = message.from_user.language_code
    logging.info(f"{user_id} {user_full_name} {time.asctime()} started bot.")

    if not db.check_user(user_id):
        await bot.send_message(
            message.chat.id,
            tr("welcome_new", language_code, user_full_name=user_full_name),
            reply_markup=kb_reg,
        )
    else:
        await bot.send_message(
            message.chat.id,
            tr("welcome_back", language_code, user_full_name=user_full_name),
            reply_markup=kb_main,
        )


# Handle user-delete command
@dp.message_handler(commands=["delete_user"])
async def delete_user_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    chat_id = message.chat.id
    language_code = message.from_user.language_code
    logging.info(
        f"{user_id} {user_full_name} {time.asctime()} initialized account deletion."
    )

    if not db.check_user(user_id):
        await not_registered(chat_id, language_code)
    else:
        await DeleteAcStates.password.set()
        await bot.send_message(
            chat_id,
            tr("enter_password", language_code),
            reply_markup=kb_cancel,
        )


@dp.message_handler(commands=["stats"])
async def stats_handler(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    language_code = message.from_user.language_code
    if not db.check_user(user_id):
        await not_registered(chat_id, language_code)
    else:
        await StatsStates.password.set()
        await bot.send_message(
            chat_id,
            tr("enter_password", language_code),
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
    await bot.send_message(
        message.chat.id,
        tr("register_birth_year", message.from_user.language_code),
        reply_markup=kb_cancel,
    )


# Process password for user_delete state
@dp.message_handler(state=DeleteAcStates.password)
async def del_process_password(message: types.Message, state: FSMContext):
    """
    Process password
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    language_code = message.from_user.language_code
    async with state.proxy() as data:
        data["password"] = message.text
        if db.check_password(user_id, message.text):
            await bot.send_message(
                chat_id,
                md.text(
                    tr(
                        "delete_confirm",
                        language_code,
                        user_name=user_name,
                    )
                ),
                reply_markup=kb_del,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await incorrect_password(message)


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
            message.chat.id,
            tr("add_mood_prompt", message.from_user.language_code),
            reply_markup=kb_mood,
        )
    else:
        await incorrect_password(message)


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
            tr("choose_range", message.from_user.language_code),
            reply_markup=kb_read,
            parse_mode=ParseMode.MARKDOWN,
        )
        await ReadStates.next()
    else:
        await incorrect_password(message)


@dp.message_handler(state=StatsStates.password)
async def process_password_stats(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if db.check_password(user_id, message.text):
        await send_stats(chat_id, user_id, message.from_user.language_code)
        await state.finish()
    else:
        await incorrect_password(message)


# Check age. Age gotta be digit
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.birth_year)
async def process_year_invalid(message: types.Message):
    """
    If birth_year is invalid
    """
    return await message.reply(
        tr("wrong_year", message.from_user.language_code)
    )


# Process user-input year
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.birth_year)
async def process_year(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(birth_year=int(message.text))
    await bot.send_message(
        message.chat.id,
        tr("register_gender", message.from_user.language_code),
        reply_markup=kb_gender,
    )


# Process user-input gender
@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["gender"] = message.text
        await Form.next()

        # And send message
        await bot.send_message(
            message.chat.id,
            tr("register_email", message.from_user.language_code),
            reply_markup=kb_cancel,
        )


# Check if email is of valid value
@dp.message_handler(
    lambda msg: not bool(
        re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", msg.text)
    ),
    state=Form.email,
)
async def process_email_invalid(message: types.Message, state: FSMContext):
    """
    Process invalid email entry
    """
    return await message.reply(
        tr("invalid_email", message.from_user.language_code)
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
    language_code = message.from_user.language_code
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
                md.text(
                    tr("register_success_intro", language_code, user_name=user_name)
                ),
                md.text(tr("register_success_confirm", language_code)),
                md.text(
                    tr(
                        "register_success_age",
                        language_code,
                        age=cur_year - data["birth_year"],
                    )
                ),
                md.text(
                    tr(
                        "register_success_gender",
                        language_code,
                        gender=md.bold(data["gender"]),
                    )
                ),
                md.text(
                    tr("register_success_email", language_code, email=data["email"])
                ),
                md.text(tr("register_success_action", language_code)),
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
            message.chat.id,
            tr("add_message_prompt", message.from_user.language_code),
            reply_markup=kb_cancel,
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
        tr("entry_created", message.from_user.language_code),
        reply_markup=kb_main,
        parse_mode=ParseMode.MARKDOWN,
    )
    await state.finish()


if __name__ == "__main__":

    executor.start_polling(dp)

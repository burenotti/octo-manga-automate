from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

callback_data_factory = CallbackData("action", "action_type")


def get_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("👀 Преисполниться",
                             switch_inline_query_current_chat="")
    )
    return markup
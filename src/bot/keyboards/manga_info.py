from backend.entities import MangaInfo
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import create_manga_id, hash_manga_info

action_callback_factory = CallbackData("manga_action", "manga_id", "action")
nav_callback_factory = CallbackData("manga_nav", "manga_id", "offset")


def get_action_callback(manga_id: str, action: str):
    return action_callback_factory.new(manga_id, action)


def get_keyboard(
        manga_info: MangaInfo,
        level: int = 0,
        volume: int = 0,
        offset: int = 0,
) -> InlineKeyboardMarkup:
    levels = {
        1: get_info_keyboard,
        2: get_volume_keyboard,
        3: get_chapter_keyboard,
    }
    return levels[level](manga_info, level, volume, offset)


async def get_info_keyboard(manga_info: MangaInfo, *args, **kwargs) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    manga_id = await create_manga_id(manga_info)
    markup.row(
        InlineKeyboardButton("💗  В избранное",
                             callback_data=get_action_callback(manga_id, "favourite")),
        InlineKeyboardButton("📖  Читать c начала",
                             callback_data=get_action_callback(manga_id, "start_read")),
    )
    markup.row(
        InlineKeyboardButton("📄 Список глав",
                             callback_data=get_action_callback(manga_id, "nav")),
    )

    return markup


def get_volume_keyboard(manga_info: MangaInfo, *args, **kwargs) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add("❌ Назад")
    return markup


def get_chapter_keyboard(
        manga_info: MangaInfo,
        volume: int = 0,
        offset: int = 0
) -> InlineKeyboardMarkup:

    markup = InlineKeyboardMarkup(row_width=3)

    return markup

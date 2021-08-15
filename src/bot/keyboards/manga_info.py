from hashlib import md5
from backend.entities import MangaInfo
from yarl import URL
from typing import List, Optional
from loader import local_storage
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


action_callback_factory = CallbackData("manga_action", "manga_id", "action")
nav_callback_factory = CallbackData("manga_nav", "manga_id", "offset")

local_storage["manga_actions"] = {}
local_storage["manga_navigation"] = {}


def hash_manga_info(manga_info: MangaInfo):
    return md5(manga_info.url.path.encode('utf-8')).hexdigest()


def get_action_callback(manga: MangaInfo, action: str):
    manga_id = hash_manga_info(manga)
    return action_callback_factory.new(manga_id, action)


def get_nav_callback(manga: MangaInfo, offset: int):
    manga_id = hash_manga_info(manga)
    return nav_callback_factory.new(manga_id, offset)


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


def get_info_keyboard(manga_info: MangaInfo, *args, **kwargs) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    local_storage["manga_actions"][hash_manga_info(manga_info)] = manga_info
    markup.row(
        InlineKeyboardButton("💗  В избранное",
                             callback_data=get_action_callback(manga_info, "favourite")),
        InlineKeyboardButton("📖  Читать c начала",
                             callback_data=get_action_callback(manga_info, "start_read")),
    )
    markup.row(
        InlineKeyboardButton("📄 Список глав",
                             callback_data=get_action_callback(manga_info, "nav")),
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

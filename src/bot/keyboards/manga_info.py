from typing import Optional

from backend.entities import MangaInfo
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import create_manga_id, hash_manga_info

action_callback_factory = CallbackData("manga_action", "manga_id", "action")
nav_callback_factory = CallbackData("manga_nav", "manga_id", "offset", "action", "chapter")
in_place_callback_factory = CallbackData("in_place", "manga_id", "action", "chapter")


def get_action_callback(manga_id: str, action: str):
    return action_callback_factory.new(manga_id, action)


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


async def get_chapter_keyboard(
        manga_info: MangaInfo,
        offset: int = 0,
        page_size: int = 10,
) -> InlineKeyboardMarkup:
    manga_id = await create_manga_id(manga_info)

    markup = InlineKeyboardMarkup(row_width=3)

    for chapter in manga_info.chapter_list[offset: offset + page_size]:
        markup.add(InlineKeyboardButton(
            text=chapter.name,
            callback_data=nav_callback_factory.new(manga_id, offset, "open", chapter.number)
        ))

    nav_buttons = []

    if offset != 0:
        nav_buttons.append(InlineKeyboardButton(
            text="◀ Назад",
            callback_data=nav_callback_factory.new(manga_id, offset, "back", offset)
        ))

    if len(manga_info.chapter_list) - offset >= page_size:
        nav_buttons.append(InlineKeyboardButton(
            text="Вперед ▶",
            callback_data=nav_callback_factory.new(manga_id, offset, "forward", offset)
        ))

    markup.row(*nav_buttons)

    markup.row(
        InlineKeyboardButton(
            text="✏️ По номеру главы",
            callback_data=nav_callback_factory.new(manga_id, offset, "number", offset)
        ),
        InlineKeyboardButton(
            text="❌ Закрыть",
            callback_data=nav_callback_factory.new(manga_id, offset, "cancel", offset)
        )
    )

    return markup


async def get_in_place_keyboard(
        manga_info: MangaInfo,
        current_chapter: int = 0
) -> Optional[InlineKeyboardMarkup]:
    if current_chapter == len(manga_info.chapter_list) - 1:
        return None
    markup = InlineKeyboardMarkup(row_width=3)
    manga_id = await create_manga_id(manga_info)
    data = in_place_callback_factory.new(manga_id, "next", current_chapter)
    markup.add(
        InlineKeyboardButton(
            text="✅ Вперед",
            callback_data=data
        )
    )

    return markup
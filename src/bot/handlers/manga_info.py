from aiogram.types import CallbackQuery

from backend.entities import MangaInfo
from bot.keyboards import manga_info as keyboard

from utils import (
    include_shortname,
    default_on_key_error,
    from_callback_data
)

from loader import (
    dispatcher, driver
)


@dispatcher.callback_query_handler(
    keyboard.action_callback_factory.filter(action='start_read')
)
@include_shortname(on_error=default_on_key_error)
async def info_actions(
        query: CallbackQuery,
        callback_data: dict,
        manga_shortname: str = None,
        **kwargs
):
    manga = await driver.get_manga_info(manga_shortname)

    if manga.chapter_list:
        chapter_info = manga.chapter_list[0]
        url = await driver.publish_chapter(chapter_info)
        markup = await keyboard.get_in_place_keyboard(manga, 1)
        await query.message.answer(f"<a href=\"{url}\">{chapter_info.name}</a>",
                                   reply_markup=markup)
    else:
        await query.message.answer("У нас какие-то проблемы: "
                                   "пока не выходит получить первую главу( "
                                   "Попробуй позже")


@dispatcher.callback_query_handler(
    keyboard.action_callback_factory.filter(action='nav')
)
@include_shortname(on_error=default_on_key_error)
async def info_actions(
        query: CallbackQuery,
        callback_data: dict,
        manga_shortname: str = None,
        **kwargs
):
    manga = await driver.get_manga_info(manga_shortname)

    return await query.message.edit_reply_markup(
        await keyboard.get_chapter_keyboard(manga)
    )


@dispatcher.callback_query_handler(
    keyboard.action_callback_factory.filter(action='favourite')
)
@include_shortname(on_error=default_on_key_error)
async def info_actions(
        query: CallbackQuery,
        callback_data: dict,
        manga_shortname: str = None,
        **kwargs
):
    return await query.answer("Очень жаль, но это пока не работает(")
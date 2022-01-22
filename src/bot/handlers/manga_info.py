from aiogram.types import CallbackQuery

from backend.entities import MangaInfo
from bot.keyboards import manga_info as keyboard

from utils import (
    include_url,
    default_on_key_error,
    from_callback_data
)

from loader import (
    dispatcher, driver, reply_renderer
)


@dispatcher.callback_query_handler(
    keyboard.action_callback_factory.filter(action='start_read')
)
@include_url(on_error=default_on_key_error)
async def info_actions(
        query: CallbackQuery,
        callback_data: dict,
        manga_url: str = None,
        **kwargs
):
    manga = await driver.get_manga_info(manga_url)

    if manga.chapter_list:
        chapter_info = manga.chapter_list[0]
        url = await driver.publish_chapter(chapter_info)
        markup = await keyboard.get_in_place_keyboard(manga, 1)

        text = reply_renderer.ready_chapter(url, chapter_info)

        await query.message.answer(text, reply_markup=markup)
    else:
        await query.message.answer("У нас какие-то проблемы: "
                                   "пока не выходит получить первую главу( "
                                   "Попробуй позже")


@dispatcher.callback_query_handler(
    keyboard.action_callback_factory.filter(action='nav')
)
@include_url(on_error=default_on_key_error)
async def info_actions(
        query: CallbackQuery,
        callback_data: dict,
        manga_url: str = None,
        **kwargs
):
    manga = await driver.get_manga_info(manga_url)

    return await query.message.edit_reply_markup(
        await keyboard.get_chapter_keyboard(manga)
    )


@dispatcher.callback_query_handler(
    keyboard.action_callback_factory.filter(action='favourite')
)
@include_url(on_error=default_on_key_error)
async def info_actions(
        query: CallbackQuery,
        callback_data: dict,
        manga_url: str = None,
        **kwargs
):
    return await query.answer("Очень жаль, но это пока не работает(")
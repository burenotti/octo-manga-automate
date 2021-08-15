from aiogram.types import CallbackQuery
from backend.entities import MangaInfo
from bot.keyboards import manga_info as keyboard
from utils import include_shortname
from loader import (
    dispatcher,
    driver,
    publisher
)


async def on_key_error(query: CallbackQuery, callback_data: dict):
    await query.message.delete_reply_markup()
    await query.answer("Данная кнопка устарела и больше не работает.")


@dispatcher.callback_query_handler(keyboard.action_callback_factory.filter())
@include_shortname(on_error=on_key_error)
async def info_actions(query: CallbackQuery, callback_data: dict, manga_shortname: str = None):
    action = callback_data.get('action')
    manga = await driver.get_manga_info(manga_shortname)

    if action == "start_read":
        if manga.chapter_list:
            chapter = await driver.with_chapter_pages(manga.chapter_list[0])
            response = publisher.publish(chapter)
            await dispatcher.bot.send_message(query.from_user.id, response["url"])

    elif action == "favourite":
        return await query.answer("Очень жаль, но это пока не работает(")

from aiogram.types import CallbackQuery
from backend.entities import MangaInfo
from bot.keyboards import manga_info as keyboard

from loader import (
    dispatcher,
    local_storage,
    driver,
    publisher
)


@dispatcher.callback_query_handler(keyboard.action_callback_factory.filter())
async def info_actions(query: CallbackQuery, callback_data: dict):
    manga_id = callback_data.get('manga_id')
    action = callback_data.get('action')
    manga : MangaInfo = local_storage["manga_actions"].get(manga_id)
    if not manga:
        return await query.answer("Данная кнопка устарела и больше не работает.")

    if action == "start_read":
        if manga.chapter_list:
            chapter = await driver.with_chapter_pages(manga.chapter_list[0])
            response = publisher.publish(chapter)
            await dispatcher.bot.send_message(query.from_user.id, response["url"])

    elif action == "favourite":
        return await query.answer("Очень жаль, но это пока не работает(")

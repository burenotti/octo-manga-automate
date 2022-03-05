from aiogram.dispatcher.filters import Command
from loader import dispatcher, manga_source
from backend.entities import ResultType
from bot.keyboards import search_keyboard
from aiogram.types import (
    Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
)


@dispatcher.message_handler(Command("search"))
async def search(message: Message):
    text = "А вот и поиск!👇"
    await message.answer(text, reply_markup=search_keyboard.get_keyboard())


@dispatcher.inline_handler()
async def search(query: InlineQuery):
    result = await manga_source.search(query.query)
    items = []
    for index, match in enumerate(result):
        if match.type == ResultType.Manga and match.thumbnail is not None:
            input_content = InputTextMessageContent(f"/info <a href=\"{match.url!s}\">ссылка</a>")
            items.append(InlineQueryResultArticle(
                id=str(index),
                title=match.value,
                thumb_url=str(match.thumbnail),
                input_message_content=input_content,
            ))

    await query.answer(items, cache_time=1, is_personal=True)

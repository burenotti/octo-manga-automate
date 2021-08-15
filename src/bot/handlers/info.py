from utils import get_stars_score
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import Message, CallbackQuery
from yarl import URL

from loader import dispatcher, bot, driver
from bot.keyboards import manga_info as keyboard


@dispatcher.message_handler(Command("info"))
async def get_manga_info(message: Message):

    # await message.delete()

    urls = list(filter(lambda e: e.type == "url", message.entities))
    if len(urls) == 0:

        await message.answer("Так нельзя! После <b>/info</b> вводи ссылку!")

    if len(urls) > 1:

        await message.answer("Так нельзя! Можно вводить только одну ссылку!")

    else:
        url = URL(message.text[urls[0].offset: urls[0].offset + urls[0].length])

        if url.host != 'readmanga.live':
            return await message.answer("Ты чего? Я работаю только с readmanga.live")

        try:

            manga_info = await driver.get_manga_info(url)

        except Exception as e:

            return await message.answer("Что-то пошло не так! 😱 Если ссылка правильная, "
                                        "то скоро всё должно наладиться, обещаем! 😉")

        score = float(manga_info.score)
        text = (f"<b>{manga_info.name}</b>\n\n"
                f"{get_stars_score(score)}\n\n"
                f"{manga_info.description}")

        if manga_info.thumbnail_urls:
            await message.answer_photo(manga_info.thumbnail_urls[0])

        await message.answer(text, reply_markup=keyboard.get_info_keyboard(manga_info))

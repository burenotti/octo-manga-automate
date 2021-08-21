from utils import get_stars_score
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from yarl import URL

from loader import dispatcher, bot, driver
from bot.keyboards import manga_info as keyboard


@dispatcher.message_handler(Command("info"))
async def get_manga_info(message: Message):

    urls = list(filter(lambda e: e.type in ("url", "text_link"), message.entities))
    if len(urls) == 0:

        await message.answer("Так нельзя! После <b>/info</b> вводи ссылку!")

    elif len(urls) > 1:

        await message.answer("Так нельзя! Можно вводить только одну ссылку!")

    else:

        if urls[0].type == "url":

            url = URL(message.text[urls[0].offset: urls[0].offset + urls[0].length])

        else:

            url = URL(urls[0].url)

        if url.host != 'readmanga.live':
            return await message.answer("Ты чего? Я работаю только с readmanga.live")

        try:

            manga_info = await driver.get_manga_info(url)

        except Exception as e:

            return await message.answer("Что-то пошло не так! 😱 Если ссылка правильная, "
                                        "то скоро всё должно наладиться, обещаем! 😉")

        score = float(manga_info.score)
        text = (f"<b>{manga_info.name}</b>\n"
                f"\n{get_stars_score(score)}\n\n" +
                (f"<b>Автор: </b> {manga_info.author}\n\n" if manga_info.author else "") +
                f"{manga_info.description}")

        if manga_info.thumbnail_urls:
            media = list(map(InputMediaPhoto, manga_info.thumbnail_urls))
            await message.answer_media_group(media)

        markup = await keyboard.get_info_keyboard(manga_info)
        await message.answer(text, reply_markup=markup)

import itertools


from aiogram.dispatcher.filters import Command, Text
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from yarl import URL

from loader import dispatcher, driver, reply_renderer
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

        if not driver.is_host_available(url.host):

            resource_list_str = '\n'.join(
                itertools.starmap("{}. {}".format, enumerate(driver.available_hosts, 1))
            )

            return await message.answer(
                "Извини, я работаю только с этими ресурсами:\n" + resource_list_str
            )

        try:

            manga_info = await driver.get_manga_info(url)

        except Exception as e:

            return await message.answer("Что-то пошло не так! 😱 Если ссылка правильная, "
                                        "то скоро всё должно наладиться, обещаем! 😉")

        score = float(manga_info.score)

        text = reply_renderer.manga_info(manga_info)

        if manga_info.thumbnail_urls:
            media = list(map(InputMediaPhoto, manga_info.thumbnail_urls))
            await message.answer_media_group(media)

        markup = await keyboard.get_info_keyboard(manga_info)
        await message.answer(text, reply_markup=markup)

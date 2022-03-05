import itertools

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, InputMediaPhoto
from yarl import URL

from backend.exceptions import UnprocessableEntity
from loader import dispatcher, driver, reply_renderer, manga_source
from bot.keyboards import manga_info as keyboard


@dispatcher.message_handler(Command("info"))
async def get_manga_info(message: Message):
    urls = [ent for ent in message.entities if ent.type in ("url", "text_link")]
    if len(urls) == 0:

        await message.answer("Так нельзя! После <b>/info</b> вводи ссылку!")

    elif len(urls) > 1:

        await message.answer("Так нельзя! Можно вводить только одну ссылку!")

    else:

        if urls[0].type == "url":

            url = URL(message.text[urls[0].offset: urls[0].offset + urls[0].length])

        else:

            url = URL(urls[0].url)

        try:

            manga_info = await manga_source.get_manga_info(url)

        except UnprocessableEntity:

            resource_list_str = '\n'.join(
                # TODO: Выпилить здесь драйвер
                itertools.starmap("{}. {}".format, enumerate(driver.available_hosts, 1))
            )

            return await message.answer(
                "Извини, я работаю только с этими ресурсами:\n" + resource_list_str
            )

        except Exception:

            return await message.answer("Что-то пошло не так! 😱 Если ссылка правильная, "
                                        "то скоро всё должно наладиться, обещаем! 😉")

        text = reply_renderer.manga_info(manga_info)

        if manga_info.thumbnail_urls:
            media = list(map(InputMediaPhoto, manga_info.thumbnail_urls))
            await message.answer_media_group(media)

        markup = await keyboard.get_info_keyboard(manga_info)
        await message.answer(text, reply_markup=markup)

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from hashlib import md5
from loader import dispatcher, driver
from backend.entities import ResultType
from bot.keyboards import search_keyboard


@dispatcher.message_handler(Command("start"))
async def search(message: Message):
    text = ("Хэй! Ты же здесь, чтобы читать мангу, верно? "
            "Ну так давай начнем!"
            " Кнопка снизу 👇 открывает поиск!")
    await message.answer(text, reply_markup=search_keyboard.get_keyboard())


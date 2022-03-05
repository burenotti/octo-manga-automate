import bot
import asyncio
from aiogram import executor
from loader import dispatcher, manga_source


async def on_startup(*args, **kwargs):
    bot.include_default_handlers()


def on_shutdown(*args, **kwargs):
    asyncio.ensure_future(manga_source.close())


if __name__ == '__main__':
    executor.start_polling(dispatcher,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown
                           )

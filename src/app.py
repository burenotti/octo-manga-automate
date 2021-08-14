from aiogram import executor
from loader import dispatcher


async def on_startup(*args, **kwargs):
    pass


def on_shutdown(*args, **kwargs):
    pass


if __name__ == '__main__':
    executor.start_polling(dispatcher,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown
                           )

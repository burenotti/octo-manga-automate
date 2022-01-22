from aiogram.types import CallbackQuery

from .redis_ import (
    include_url,
    create_manga_id,
    hash_manga_info
)

__all__ = [
    "create_manga_id",
    "include_url",
    "hash_manga_info",
    "default_on_key_error",
    "from_callback_data",
]


async def default_on_key_error(query: CallbackQuery, callback_data: dict):
    await query.message.delete_reply_markup()
    await query.answer("Данная кнопка устарела и больше не работает.")


def from_callback_data(*values: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            callback_data = kwargs.get('callback_data')

            if callback_data is None:
                raise ValueError("Cannot extract values from callback data, "
                                 "because callback_data is None")

            data = {key: value for key, value in callback_data.items() if key in values}

            return func(*args, **kwargs, **data)

        return wrapper

    return decorator

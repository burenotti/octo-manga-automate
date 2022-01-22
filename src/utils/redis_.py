from hashlib import md5
from backend.entities import MangaInfo
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from loader import redis
from typing import Dict, Any, Callable, Awaitable

redis_key_factory = CallbackData("manga_id", "manga_id")


def include_url(
        on_error: Callable[[CallbackQuery, Dict[str, Any]], Awaitable] = lambda a, b: None
):
    def decorator(function):

        async def wrapper(query: CallbackQuery, callback_data: Dict[str, Any], *args, **kwargs):

            manga_id = callback_data.get("manga_id")
            key = redis_key_factory.new(manga_id)
            manga_url = await redis.get(key)

            if manga_url is None:

                await on_error(query, callback_data)

            else:

                await function(query,
                               callback_data,
                               *args,
                               **kwargs,
                               manga_url=manga_url.decode('utf-8'))

        return wrapper

    return decorator


def hash_manga_info(manga_info: MangaInfo):
    return md5(manga_info.shortname.encode('utf-8')).hexdigest()


async def create_manga_id(manga: MangaInfo):
    manga_hash = hash_manga_info(manga)
    key = redis_key_factory.new(manga_hash)
    await redis.set(key, str(manga.url))
    return manga_hash

from hashlib import md5
from backend.entities import MangaInfo
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from loader import redis
from typing import Dict, Any, Callable, Awaitable

redis_key_factory = CallbackData("manga_id", "manga_id")


def include_shortname(
        on_error: Callable[[CallbackQuery, Dict[str, Any]], Awaitable] = lambda a, b: None
):
    def decorator(function):

        async def wrapper(query: CallbackQuery, callback_data: Dict[str, Any]):

            manga_id = callback_data.get("manga_id")
            key = redis_key_factory.new(manga_id)
            manga_shortname = await redis.get(key)

            if manga_shortname is None:

                await on_error(query, callback_data)

            else:

                await function(query,
                               callback_data,
                               manga_shortname=manga_shortname.decode('utf-8'))

        return wrapper

    return decorator


def hash_manga_info(manga_info: MangaInfo):
    return md5(manga_info.shortname.encode('utf-8')).hexdigest()


async def create_manga_id(manga: MangaInfo):
    manga_hash = hash_manga_info(manga)
    key = redis_key_factory.new(manga_hash)
    await redis.set(key, manga.shortname)
    return manga_hash

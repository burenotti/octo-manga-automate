from typing import Union, overload, List

import aioredis
from yarl import URL

from . import entities
from .manga_source import MangaSource


class RedisMangaSource(MangaSource):

    def __init__(
            self,
            redis_host: str = "localhost",
            redis_port: int = 6379
    ):
        super().__init__()
        self.__redis = aioredis.Redis(host=redis_host, port=redis_port)

    async def search(self, query: str) -> List[entities.SearchResult]:
        return await super().search(query)

    @overload
    async def get_manga_info(self, url: URL) -> entities.MangaInfo:
        pass

    @overload
    async def get_manga_info(self, shortname: str) -> entities.MangaInfo:
        pass

    async def get_manga_info(self, identity: Union[str, URL]) -> entities.MangaInfo:
        return await super().get_manga_info(identity)

    async def with_chapter_pages(self, chapter_info: entities.ChapterInfo) -> entities.Chapter:
        return await super().with_chapter_pages(chapter_info)

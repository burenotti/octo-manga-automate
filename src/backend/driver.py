from typing import List, Union, overload

from aiohttp import ClientSession
from yarl import URL
from . import entities
from .parser import ReadMangaParser


class Driver:

    """
    Драйвер, объединяя кэш и парсер источника,
    предоставляет API для использования бэкенда.

    ВАЖНО:
    В данный момент кэш не реализован, поэтому каждый вызов драйвера
    будет приводить к повторным (возможно излишним) запросам к источнику.
    """

    HOST = URL("https://readmanga.live/")

    def __init__(self, session: ClientSession):
        self.parser = ReadMangaParser(session=session)

    async def search(self, query: str) -> List[entities.SearchResult]:
        return await self.parser.search(query)

    @overload
    async def get_manga_info(self, url: URL) -> entities.MangaInfo:
        pass

    @overload
    async def get_manga_info(self, shortname: str) -> entities.MangaInfo:
        pass

    async def get_manga_info(self, id: Union[str, URL]) -> entities.MangaInfo:
        if isinstance(id, str):
            url = self.HOST.with_path(id)
        else:
            url = id

        return await self.parser.get_manga_info(url)

    async def with_chapter_pages(self, chapter_info: entities.ChapterInfo) -> entities.Chapter:
        return entities.Chapter(
            chapter_info,
            await self.parser.get_chapter_pages(chapter_info.url)
        )

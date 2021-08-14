from typing import List
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

    def __init__(self):
        self.parser = ReadMangaParser()

    async def search(self, query: str) -> List[entities.SearchResult]:
        return await self.parser.search(query)

    async def get_manga_info(self, shortname: str) -> entities.MangaInfo:
        url = self.HOST.with_path(shortname)
        return await self.parser.get_manga_info(url)

    async def with_chapter_pages(self, chapter_info: entities.ChapterInfo) -> entities.Chapter:
        return entities.Chapter(
            chapter_info,
            await self.parser.get_chapter_pages(chapter_info.url)
        )

from typing import List, Union, overload
from .publisher import TelegraphPublisher
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

    def __init__(
            self,
            session: ClientSession,
            telegraph_access_token: str,
            author_name: str = None,
            author_url: str = None,
    ):
        self.parser = ReadMangaParser(
            session=session,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/93.0.4577.63 Safari/537.36 "
            }
        )
        self.publisher = TelegraphPublisher(
            access_token=telegraph_access_token,
            author_name=author_name,
            author_url=author_url
        )

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

    @overload
    async def publish_chapter(self, chapter: entities.ChapterInfo):
        pass

    @overload
    async def publish_chapter(self, chapter: entities.Chapter):
        pass

    async def publish_chapter(
            self,
            chapter: Union[entities.Chapter, entities.ChapterInfo]
    ) -> URL:

        if isinstance(chapter, entities.ChapterInfo):
            chapter = await self.with_chapter_pages(chapter)

        return await self.publisher.publish_chapter(chapter)

    async def close(self):
        return self.publisher.close()
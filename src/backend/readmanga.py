from typing import Union, overload, List

from yarl import URL

from . import entities
from .manga_source import MangaSource
from .parser import ReadMangaParser


class ReadMangaSource(MangaSource):

    def __init__(self):
        super(ReadMangaSource, self).__init__()
        self.parser = ReadMangaParser()
        self.host = URL('https://readmanga.live/')

    async def search(self, query: str) -> List[entities.SearchResult]:
        return await self.parser.search(query)

    @overload
    async def get_manga_info(self, url: URL) -> entities.MangaInfo:
        pass

    @overload
    async def get_manga_info(self, shortname: str) -> entities.MangaInfo:
        pass

    async def get_manga_info(self, identity: Union[str, URL]) -> entities.MangaInfo:
        if isinstance(id, str):
            if not URL(id).is_absolute():
                url = self.host.with_path(id)
            else:
                url = URL(id)
        else:
            url = id

        return await self.parser.get_manga_info(url)

    async def with_chapter_pages(self, chapter_info: entities.ChapterInfo) -> entities.Chapter:
        return entities.Chapter(
            chapter_info,
            await self.parser.get_chapter_pages(chapter_info.url)
        )

    async def close(self) -> None:
        await self.parser.close()
        await super().close()

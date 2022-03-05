from __future__ import annotations

from abc import abstractmethod, ABC
from yarl import URL
from typing import (
    Optional, overload, List, Union
)

from backend import entities
from backend.exceptions import UnprocessableEntity


class MangaSource(ABC):

    def __init__(self):
        self.__next_source: Optional[MangaSource] = None

    def next(self, next_source: MangaSource) -> MangaSource:
        """
        Sets manga source passed as argument and returns it.
        """
        self.__next_source = next_source
        return next_source

    async def __delegate_next(self, method_name: str, *args, **kwargs):
        if source := self.__next_source:
            return await getattr(source, method_name)(*args, **kwargs)
        else:
            raise UnprocessableEntity()

    @abstractmethod
    async def search(self, query: str) -> List[entities.SearchResult]:
        return await self.__delegate_next('search', query)

    @overload
    async def get_manga_info(self, url: URL) -> entities.MangaInfo:
        pass

    @overload
    async def get_manga_info(self, shortname: str) -> entities.MangaInfo:
        pass

    @abstractmethod
    async def get_manga_info(self, identity: Union[str, URL]) -> entities.MangaInfo:
        return await self.__delegate_next('get_manga_info', identity)

    @abstractmethod
    async def with_chapter_pages(self, chapter_info: entities.ChapterInfo) -> entities.Chapter:
        return await self.__delegate_next('with_chapter_pages', chapter_info)

    @abstractmethod
    async def close(self) -> None:
        await self.__delegate_next('close')

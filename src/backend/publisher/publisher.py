from typing import Iterable, Optional

from aiotelegraph import TelegraphClient, Node, Page, TelegraphException
from aiohttp import ClientSession
from yarl import URL

from .renderer import render_chapter
from backend.entities import Chapter
from bs4 import BeautifulSoup


class TelegraphPublisher(TelegraphClient):

    def __init__(
            self,
            access_token: str = None,
            author_name: str = None,
            author_url: str = None
    ):

        super().__init__(access_token)
        self.auth_url = author_url
        self.author_name = author_name

    async def create_page(
            self,
            title: str,
            content: Iterable[Node] = None,
            author_name: (str, None) = None,
            return_content: bool = False,
            html_content: str = None
    ):

        if content is not None and html_content is not None:
            raise ValueError("Please, use either `content` or `html_content` arguments, not both.")

        if content is not None:

            return await super().create_page(title, content, author_name, return_content)

        else:

            params = {}
            if author_name is not None:
                params["author_name"] = author_name

            data = await self.request(method="createPage", access_token=self.access_token, title=title,
                                      content=content, return_content=return_content, **params)
            return Page.parse(data)

    async def publish_chapter(self, chapter: Chapter) -> URL:
        html = render_chapter(chapter)
        response = await self.create_page(title=chapter.info.name,
                                          author_name=self.author_name,
                                          html_content=html)

        return URL(response.url)

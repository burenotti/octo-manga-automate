import json
from typing import Iterable, Optional
from asynctelegraph import TelegraphClient, types
from aiohttp import ClientSession
from yarl import URL

from .renderer import render_chapter
from backend.entities import Chapter
from bs4 import BeautifulSoup


class TelegraphPublisher:

    def __init__(
            self,
            access_token: str = None,
            author_name: str = None,
            author_url: str = None
    ):
        self.auth_url = author_url
        self.author_name = author_name
        self.client = TelegraphClient(access_token)

    async def publish_chapter(self, chapter: Chapter) -> URL:
        html = render_chapter(chapter)
        response = await self.client.create_page(title=chapter.info.name,
                                                 author_name=self.author_name,
                                                 html_content=html)

        return URL(response.url)

    async def close(self):
        await self.client.close()

import json
import re
from yarl import URL
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from backend.entities import Page, ChapterInfo, MangaInfo, SearchResult
from typing import List


# Немного терминологии:
# 1. Главная страница (Main page) - основная страница сайта (https://readmanga.live/)

# 2. Страница манги (Manga page) - страница, содержащая основную информацию о манги
# URL вида https://readmanga.live/some_manga_name, например, https://readmanga.live/monstr_1994

# 3. Страница главы манги (Chapter page) - страница, просмотра главы манги,
# с нее можно получить ссылки на страницы главы (изображения)
# URL вида https://readmanga.live/some_manga_name/volXXX/YYY?mtr=true, где XXX - номер тома, YYY - номер главы.
# mtr=true является проверкой на совершеннолетие, он обязателен только для доступа к 18+ контенту.
# https://readmanga.live/monstr_1994/vol3/19.

# TODO: Список неполный, будет дополняться.


class ReadMangaParser:
    """
    ReadMangaParser используется для парсинга сайта readmanga.live.
    В данный момент парсер помимо своей основной задачи выполняет еще и запросы к сайту.
    На мой взгляд это неправильно, необходимо разделить запросы и парсинг содержимого на две сущности.
    """

    DOMAIN = URL("https://readmanga.live/")

    CHAPTER_NAME_REGEX = re.compile("(?P<volume_number>\d+)( - (?P<chapter_number>\d+))? (?P<chapter_name>.+)",
                                    re.MULTILINE)

    def __init__(self, session=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if session is None:
            session = ClientSession()
        self.session = session

    async def get_manga_info(self, url: URL) -> MangaInfo:
        """
        Парсит информацию о манге по url.
        Важно: MangaInfo включает себя только список ChapterInfo, элементы которого не содержат
        ссылок на страницы главы (Потому что их получения необходимо выполнить большое количество запросов,
        но они нужны не во всех сценариях использования).
        Используйте get_chapter_pages, если они вам необходимы.
        :param url: url страницы манги с сайта (например, https://readmanga.live/monstr_1994)
        :return: Информация о манге, которую удалось спарсить.
        """
        response = await self.session.get(url)
        dom = BeautifulSoup(await response.text(), features="html.parser")

        # Parse main info
        name = dom.select_one('span.name').text
        description = dom.select_one('meta[name="description"]').get_attribute_list('content')[0]
        score = dom.select_one('.rating-block').get_attribute_list('data-score')[0]

        # Parse thumbnail pictures
        thumbnails = []
        thumbnails_img_tags = dom.select_one('.picture-fotorama').select('img')
        for img in thumbnails_img_tags:
            thumbnails.append(img.get_attribute_list('src')[0])

        # Parse chapter list
        chapter_links = dom.select('.chapters-link>table>tr>td>a')
        chapter_list = self.parse_chapter_list(chapter_links)

        return MangaInfo(
            name=name,
            description=description,
            url=url,
            score=score,
            thumbnail_urls=thumbnails,
            chapter_list=chapter_list
        )

    # async def get_entry_point(self, url: URL) -> URL:
    #     entry_point = None
    #     try:
    #         response = await self.session.get(url)
    #         dom = BeautifulSoup(await response.text(), features="html.parser")
    #         entry_point = dom.select_one('.btn-block').get_attribute_list('href')[0]
    #     except Exception as e:
    #         print(e)
    #     return URL(entry_point)

    async def get_chapter_pages(self, url: URL) -> List[Page]:
        """
        Возвращает страницы главы по ссылке на нее.
        :param url: Ссылка на главу манги.
        :return: Список страниц главы.
        """
        # Это проверка для 18+ контента
        url = url.with_query({"mtr": True})
        response = await self.session.get(url)
        pages = []
        # Этот код ужасен, но как сделать его лучше я не придумал.
        # Идея: Ссылки на страницы манги находятся в раздробленном состоянии
        # в JS массиве, этот код их оттуда достает.
        if response.ok:
            start_token = 'rm_h.init('
            text = await response.text()
            start = text.find(start_token) + len(start_token)
            end = text.find(');', start)
            text = '[' + text[start:end] + ']'
            text = text.replace("'", '"')
            pages_info = json.loads(text)[0]
            pages = [Page(number, URL(page[0] + page[2])) for number, page in enumerate(pages_info, 1)]
        return pages

    async def search(self, query: str) -> List[SearchResult]:
        """
        Выполняет поиск по запросу `query`.
        :param query: Запрос для поиска.
        :return: Список результатов.
        """
        url = self.DOMAIN / "search/suggestion"
        try:
            response = await self.session.post(url, data={
                'query': query,
            })
            if not response.ok:
                raise Exception(f"Response failed with status code {response.status}")
            json_data = await response.json()
            search_result = []
            for sug in json_data['suggestions']:
                search_result.append(SearchResult(
                    value=sug.get('value', ''),
                    url=self.DOMAIN / sug.get('link', '').lstrip('/'),
                    names=sug.get('names'),
                    thumbnail=sug.get('thumbnail'),
                    additional=sug.get('additional')
                ))
            return search_result
        except Exception as e:
            print(e)
            return []

    async def close(self):
        await self.session.close()

    def get_url(self, url: URL = None, path: str = None) -> URL:
        if (url is None) == (path is None):
            raise ValueError("You must use either url or path, not both.")
        elif path:
            return self.DOMAIN / path
        else:
            return url

    def parse_chapter_list(self, link_list: List[BeautifulSoup]) -> List[ChapterInfo]:
        """
        Вспомогательная функция. Парсит список глав с основой страницы манги.
        :param link_list:
        :return:
        """
        chapter_list = []
        for index, link in enumerate(reversed(link_list), 1):
            link_text = ' '.join(link.text.split())
            match = self.CHAPTER_NAME_REGEX.search(link_text)
            if match:
                groups = match.groupdict()
                info = ChapterInfo(
                    name=groups.get('chapter_name', ''),
                    url=self.DOMAIN / link.get_attribute_list('href')[0].lstrip('/'),
                    number=index,
                    raw_number=groups.get('chapter_number'),
                    volume_number=int(groups.get('volume_number', 1))
                )
                chapter_list.append(info)

        return chapter_list

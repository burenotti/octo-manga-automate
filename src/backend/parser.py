import json
import re
from yarl import URL
from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag
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

    DOMAIN = URL("https://readmanga.io/")

    CHAPTER_NAME_REGEX = re.compile(r"(?P<volume_number>\d+)( - (?P<chapter_number>\d+))? (?P<chapter_name>.+)",
                                    re.MULTILINE)

    PAGES_REGEX = re.compile(
        r"['\"](?P<link0>http(s)?://[a-zA-Z0-9./-_?]+)\s*['\"],"
        r"\s*['\"]['\"]\s*,\s*['\"](?P<link1>[a-zA-Z0-9./-_?&]+)['\"]"
    )

    def __init__(self, session=None, headers: dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if session is None:
            session = ClientSession()
        self.session = session
        self.headers = headers

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
        response = await self.session.get(url, headers=self.headers)
        if not response.ok:
            raise HttpError(response.status, "")

        dom = BeautifulSoup(await response.text(), features="html.parser")

        # Parse main info
        name = dom.select_one('span.name').text
        description = dom.select_one('div.manga-description').get_text(strip=True)
        score = dom.select_one('.rating-block').get_attribute_list('data-score')[0]
        if node := dom.select_one('.elem_author'):
            author = node.get_text(strip=True)
        else:
            author = None

        # Parse thumbnail pictures
        thumbnails = []
        thumbnails_img_tags = dom.select_one('.picture-fotorama').select('img')
        for img in thumbnails_img_tags:
            thumbnails.append(img.get_attribute_list('src')[0])

        # Parse chapter list
        chapter_links = dom.select('.chapters-link>table>tr>td>a')
        chapter_list = self.parse_chapter_list(url.origin(), chapter_links)

        return MangaInfo(
            name=name,
            description=description,
            url=url,
            score=score,
            thumbnail_urls=thumbnails,
            chapter_list=chapter_list,
            author=author
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
        url = url.with_query({"mtr": 1})
        response = await self.session.get(url, headers=self.headers)
        # Этот код ужасен, но как сделать его лучше я не придумал.
        # Идея: Ссылки на страницы манги находятся в раздробленном состоянии
        # в JS массиве, этот код их оттуда достает.
        # if response.ok:
        #     start_token = 'rm_h.initReader('
        #     text = await response.text()
        #     start = text.find(start_token) + len(start_token)
        #     end = text.find(');', start)
        #     text = '[' + text[start:end] + ']'
        #     text = text.replace("'", '"')
        #     pages_info = json.loads(text)[1]
        #     pages = [Page(number, URL(page[0] + page[2])) for number, page in enumerate(pages_info, 1)]
        # return pages

        if response.ok:
            matches = self.PAGES_REGEX.findall(await response.text())
            return [Page(number, URL(page[0] + page[2])) for number, page in enumerate(matches)]

        else:
            raise HttpError(response.status, "")

    async def search(self, query: str) -> List[SearchResult]:
        """
        Выполняет поиск по запросу `query`.
        :param query: Запрос для поиска.
        :return: Список результатов.
        """
        url = self.DOMAIN / "search/suggestion"
        try:
            response = await self.session.get(url, headers=self.headers, params={
                'query': query,
            })
            if not response.ok:
                raise Exception(f"Response failed with status code {response.status}")
            json_data = await response.json()
            search_result = []
            for sug in json_data['suggestions']:

                link = sug.get('link', '').lstrip('/')
                if not URL(link).is_absolute():
                    url = self.DOMAIN / link
                else:
                    url = URL(link)

                search_result.append(SearchResult(
                    value=sug.get('value', ''),
                    url=url,
                    names=sug.get('names'),
                    thumbnail=sug.get('thumbnail'),
                    additional=sug.get('additional')
                ))
            return search_result
        except Exception as e:
            raise e

    async def close(self):
        await self.session.close()

    def get_url(self, url: URL = None, path: str = None) -> URL:
        if (url is None) == (path is None):
            raise ValueError("You must use either url or path, not both.")
        elif path:
            return self.DOMAIN / path
        else:
            return url

    def parse_chapter_list(self, host: URL, link_list: List[Tag]) -> List[ChapterInfo]:
        """
        Вспомогательная функция. Парсит список глав с основой страницы манги.
        :param host:
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
                    url=host / link.get_attribute_list('href')[0].lstrip('/'),
                    number=index,
                    raw_number=groups.get('chapter_number'),
                    volume_number=int(groups.get('volume_number', 1))
                )
                chapter_list.append(info)

        return chapter_list


class HttpError(Exception):

    def __init__(self, status_code: int, comment: str):
        super().__init__(f"http request failed with f{status_code} status code. {comment}")

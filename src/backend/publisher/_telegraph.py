from telegraph import Telegraph
from aiohttp import ClientSession
from backend.entities import Chapter
from bs4 import BeautifulSoup


class TelegraphPublisher:

    def __init__(self, access_token=None, telegraph=None):
        if telegraph is not None:
            self.telegraph = telegraph
        else:
            self.telegraph = Telegraph(access_token=access_token)

    def publish(self, chapter: Chapter):
        dom = BeautifulSoup(features='html.parser')
        for page in chapter.page_list:
            tag = dom.new_tag('img', attrs={'src': str(page.url)})
            dom.append(tag)
        response = self.telegraph.create_page(title=chapter.info.name,
                                              html_content=''.join(map(str, dom.contents)),
                                              author_url='https://t.me/mnrdbot',
                                              author_name="octo-manga-automate")
        return response
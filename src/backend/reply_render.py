import dataclasses

import jinja2
from backend.entities import MangaInfo, Chapter, ChapterInfo


class ReplyRenderer:

    def __init__(self):
        self._environment = jinja2.Environment(
            loader=jinja2.PackageLoader("backend"),
            autoescape=jinja2.select_autoescape(),
        )

        self._environment.trim_blocks = True
        self._environment.lstrip_blocks = True
        self._environment.keep_trailing_newline = False
        self._environment.filters["as_stars"] = self.get_stars_score

        self.templates = {
            'manga_info': self._environment.get_template("manga_info.html"),
            'ready_chapter_reply': self._environment.get_template("ready_chapter_reply.html"),
        }

    @staticmethod
    def get_stars_score(score: float, max_score: float = 5.0):
        decimal_score = int(float(score) / max_score * 10)
        stars = '💛' * decimal_score
        moons = '🖤' * (10 - decimal_score)
        return f"{stars}{moons} ({score} / {max_score})"

    def render(self, template_name: str, *args, language='ru', **kwargs):
        if template := self.templates.get(template_name):
            return template.render(*args, **kwargs)
        else:
            raise ValueError(f"Don't have template `{template_name}`.")

    def manga_info(self, manga_info: MangaInfo, language='ru') -> str:
        return self.render('manga_info', dataclasses.asdict(manga_info), language=language)

    def ready_chapter(self, ready_url: str, chapter: ChapterInfo, language='ru'):
        return self.render(
            'ready_chapter_reply',
            chapter=chapter,
            ready_url=ready_url,
            language=language
        )

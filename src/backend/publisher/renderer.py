from backend.entities import Chapter
from jinja2 import Environment, PackageLoader, select_autoescape


class Renderer:

    def __init__(self):
        self._environment = Environment(
            loader=PackageLoader("backend"),
            autoescape=select_autoescape(),
        )

        self.templates = {
            'chapter.html': self._environment.get_template("chapter.html"),
        }

    def render_chapter(self, chapter: Chapter, template_name="chapter.html") -> str:
        if template_name in self.templates:
            template = self.templates[template_name]
        else:
            template = self._environment.get_template(template_name)
            self.templates[template_name] = template

        return template.render(chapter=chapter)

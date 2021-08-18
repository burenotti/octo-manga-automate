from backend.entities import Chapter
from jinja2 import Environment, PackageLoader, select_autoescape


jinja_environment = Environment(
    loader=PackageLoader("backend"),
    autoescape=select_autoescape(),
)


templates = {
    'chapter.html': jinja_environment.get_template("chapter.html"),
}


def render_chapter(chapter: Chapter, template_name="chapter.html") -> str:
    if template_name in templates:
        template = templates[template_name]
    else:
        template = jinja_environment.get_template(template_name)
        templates[template_name] = template

    return template.render(chapter=chapter)

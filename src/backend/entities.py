import json
import dataclasses
from dataclasses import dataclass, field, InitVar
from enum import Enum
from typing import List, Optional
from yarl import URL


@dataclass
class Page:
    number: int
    url: URL


@dataclass
class ChapterInfo:
    name: str
    url: URL
    number: int
    manga_shortname: str = field(init=False)
    raw_number: Optional[str] = None
    volume_number: int = 1

    def __post_init__(self):
        self.manga_shortname = self.url.parts[1]


@dataclass
class Chapter:
    info: ChapterInfo
    page_list: List[Page]


@dataclass
class MangaInfo:
    name: str
    url: URL
    score: int
    chapter_list: List[ChapterInfo]
    shortname: str = field(init=False)
    description: Optional[str] = None
    thumbnail_urls: Optional[List[URL]] = field(default_factory=list)

    def __post_init__(self):
        self.shortname = self.url.parts[1]


class ResultType(Enum):
    Person = 0
    Manga = 1


@dataclass
class SearchResult:
    value: str
    url: URL
    type: ResultType = None
    names: Optional[List[str]] = None
    thumbnail: Optional[URL] = None
    additional: Optional[str] = None

    def __post_init__(self):
        if self.url.path.startswith('/list/person'):
            self.type = ResultType.Person
        else:
            self.type = ResultType.Manga


class EntityJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, URL):
            return str(o)
        return super().default(o)


class EntityJsonDecoder:

    @staticmethod
    def process_urls(d, *names):
        for name in names:
            if name in d:
                if isinstance(d[name], str):
                    d[name] = URL(d[name])
                if isinstance(d[name], list):
                    for index, value in enumerate(d[name]):
                        d[name][index] = URL(value)
        if d.get("shortname"):
            del d["shortname"]
        return d

    def __call__(self, d):
        self.process_urls(d, 'url', 'thumbnail', 'thumbnail_urls')
        return d

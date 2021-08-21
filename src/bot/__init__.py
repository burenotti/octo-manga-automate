import importlib
from typing import List


def include_default_handlers(prefix="bot.handlers"):
    from . import handlers

    include_handlers(list(map(
        lambda pack: f"{prefix.rstrip('.')}.{pack}",
        handlers.__all__
    )))


def include_handlers(package_list: List[str]):

    for package in package_list:
        importlib.import_module(package)

import os
from dotenv import dotenv_values


config = {**dotenv_values(".env"), **os.environ}

BOT_TOKEN = config.get("BOT_TOKEN")

TELEGRAPH_TOKEN = config.get("TELEGRAPH_TOKEN")
TELEGRAPH_AUTHOR_NAME = config.get("TELEGRAPH_AUTHOR_NAME")
TELEGRAPH_AUTHOR_URL = config.get("TELEGRAPH_AUTHOR_URL")

if config.get("ADMINS_LIST"):
    ADMINS_LIST = list(map(int, config.get("ADMINS_LIST").split(',')))
else:
    ADMINS_LIST = []

REDIS_HOST = config.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = config.get("REDIS_PORT", 6379)


POSTGRES_HOST = config.get("POSTGRES_HOST")
POSTGRES_PORT = config.get("POSTGRES_PORT")
POSTGRES_USER = config.get("POSTGRES_USER")
POSTGRES_PASSWORD = config.get("POSTGRES_PASSWORD")
POSTGRES_DB = config.get("POSTGRES_DB")

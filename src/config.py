from dotenv import dotenv_values


config = dotenv_values(".env")

BOT_TOKEN = config.get("BOT_TOKEN")

TELEGRAPH_TOKEN = config.get("TELEGRAPH_TOKEN")
TELEGRAPH_AUTHOR_NAME = config.get("TELEGRAPH_AUTHOR_NAME")
TELEGRAPH_AUTHOR_URL = config.get("TELEGRAPH_AUTHOR_URL")

ADMINS_LIST = list(map(int, config.get("ADMINS_LIST").split(',')))

REDIS_HOST = config.get("REDIS_HOST")
REDIS_PORT = config.get("REDIS_PORT")

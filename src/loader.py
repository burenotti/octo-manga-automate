import aioredis
import config
from aiohttp import ClientSession
from aiogram import Dispatcher, Bot
from config import BOT_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from backend.driver import Driver

bot = Bot(token=BOT_TOKEN, parse_mode="html")

fsm_storage = MemoryStorage()


redis = aioredis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
)

session = ClientSession()

dispatcher = Dispatcher(bot, storage=fsm_storage)

driver = Driver(
    session=session,
    telegraph_access_token=config.TELEGRAPH_TOKEN,
    author_name=config.TELEGRAPH_AUTHOR_NAME,
    author_url=config.TELEGRAPH_AUTHOR_URL,
)

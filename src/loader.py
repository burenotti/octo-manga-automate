import redis
import config
from aiohttp import ClientSession
from backend.publisher import TelegraphPublisher
from aiogram import Dispatcher, Bot, types
from config import BOT_TOKEN
from aiogram.contrib.fsm_storage.redis import RedisStorage
from backend.driver import Driver

bot = Bot(token=BOT_TOKEN, parse_mode="html")

fsm_storage = RedisStorage(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
)

local_storage = {}

redis = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
)

session = ClientSession()

dispatcher = Dispatcher(bot, storage=fsm_storage)

driver = Driver(session=session)
publisher = TelegraphPublisher(access_token=config.TELEGRAPH_TOKEN)

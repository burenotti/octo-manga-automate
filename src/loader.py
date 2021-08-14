from aiogram import Dispatcher, Bot, types
from config import BOT_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage()

dispatcher = Dispatcher(bot, storage=storage)

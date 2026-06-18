import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import register_all_handlers

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    register_all_handlers(dp)

    print("🔥 FITNESS AI V10 STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
import asyncio
import os

print("BOT START")

TOKEN = os.getenv("BOT_TOKEN")
print("TOKEN =", TOKEN)

if not TOKEN:
    print("❌ BOT_TOKEN НЕ НАЙДЕН В ENV")
    exit()

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Бот на сервере работает! 💪")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

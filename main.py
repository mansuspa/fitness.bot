import os
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Ты профессиональный фитнес тренер.
Давай краткие, понятные и практичные советы.
Составляй тренировки, питание, похудение и набор массы.
Без лишней воды.
"""

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("💪 Я твой mans тренер. Напиши вопрос!")

@dp.message()
async def chat(message: Message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )

        await message.answer(response.choices[0].message.content)

    except Exception as e:
        await message.answer(f"Ошибка: {e}")

async def main():
    print("AI FITNESS BOT STARTED")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
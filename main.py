import os
import asyncio
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = "Ты профессиональный фитнес тренер. Отвечай кратко, чётко и по делу."

# --- меню ---
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💪 Тренировка"), KeyboardButton(text="🔥 Похудение")],
        [KeyboardButton(text="⚖️ Масса"), KeyboardButton(text="🥗 Питание")]
    ],
    resize_keyboard=True
)

# --- старт ---
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "💪 Привет mans! Я твой mans фитнес тренер.\nВыбери режим или напиши вопрос.",
        reply_markup=menu
    )

# --- основной AI ---
@dp.message()
async def chat(message: Message):
    text = message.text

    # режимы кнопок
    if text == "💪 Тренировка":
        text = "Составь тренировку на сегодня"
    elif text == "🔥 Похудение":
        text = "Дай план похудения"
    elif text == "⚖️ Масса":
        text = "Дай план набора массы"
    elif text == "🥗 Питание":
        text = "Составь план питания на день"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": text}
                    ]
                }
            ) as resp:
                data = await resp.json()

        answer = data["choices"][0]["message"]["content"]
        await message.answer(answer)

    except Exception as e:
        await message.answer(f"Ошибка: {e}")

# --- запуск ---
async def main():
    print("💪 FITNESS AI BOT STARTED")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
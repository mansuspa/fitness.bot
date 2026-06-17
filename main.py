import os
import asyncio
import aiohttp
import json
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DB_FILE = "users.json"

# --- база ---
def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

users = load_users()

SYSTEM_PROMPT = """
Ты TOP level AI фитнес коуч SaaS продукта.

Ты создаёшь:
- 7-дневные планы тренировок
- персональное питание
- адаптацию под цель
- чёткие структурированные ответы

Формат:
1. Цель
2. План тренировок
3. Питание
4. Рекомендации

Будь максимально конкретным.
"""

# --- меню ---
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔥 Похудение"), KeyboardButton(text="⚖️ Масса")],
        [KeyboardButton(text="💪 Тренировка"), KeyboardButton(text="🥗 Питание")],
        [KeyboardButton(text="💎 VIP статус")]
    ],
    resize_keyboard=True
)

FREE_LIMIT = 5

# --- старт ---
@dp.message(CommandStart())
async def start(message: Message):
    user_id = str(message.from_user.id)

    if user_id not in users:
        users[user_id] = {
            "name": message.from_user.first_name,
            "goal": None,
            "vip": False,
            "requests": 0
        }
        save_users(users)

    await message.answer(
        f"💪 Привет {users[user_id]['name']}! TOP FITNESS AI готов.",
        reply_markup=menu
    )

# --- логика ---
@dp.message()
async def chat(message: Message):
    user_id = str(message.from_user.id)
    text = message.text

    if user_id not in users:
        users[user_id] = {
            "name": "user",
            "goal": None,
            "vip": False,
            "requests": 0
        }

    user = users[user_id]

    # --- VIP ---
    if text == "💎 VIP статус":
        status = "VIP 💎" if user["vip"] else "FREE 🆓"
        await message.answer(
            f"👤 Статус: {status}\n"
            f"Запросов: {user['requests']}/{FREE_LIMIT if not user['vip'] else '∞'}"
        )
        return

    # --- лимит ---
    if not user["vip"]:
        if user["requests"] >= FREE_LIMIT:
            await message.answer("🚫 Лимит исчерпан. Перейди на VIP 💎")
            return
        user["requests"] += 1

    # --- режимы ---
    if text == "🔥 Похудение":
        user["goal"] = "похудение"
        text = "Сделай 7-дневный план похудения"

    elif text == "⚖️ Масса":
        user["goal"] = "набор массы"
        text = "Сделай 7-дневный план набора массы"

    elif text == "💪 Тренировка":
        text = "Сделай тренировку на сегодня"

    elif text == "🥗 Питание":
        text = "Сделай питание на день"

    users[user_id] = user
    save_users(users)

    # --- AI ---
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

async def main():
    print("🚀 TOP FITNESS BUSINESS BOT STARTED")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
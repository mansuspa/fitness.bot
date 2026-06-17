import os
import asyncio
import aiohttp
import json

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DB_FILE = "users.json"

# -------------------
# DB
# -------------------

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

users = load_db()

# -------------------
# PLANS CORE
# -------------------

PLANS = {
    "похудение": {
        "training": "Бег 25 мин + пресс + планка + присед",
        "food": "яйца, курица, рис, овощи, рыба"
    },
    "масса": {
        "training": "жим лёжа, тяга, присед, бицепс, трицепс",
        "food": "яйца, овсянка, рис, мясо, макароны"
    }
}

SYSTEM = """
Ты фитнес AI коуч уровня приложения.

Ты даёшь:
- простые понятные советы
- улучшаешь планы
- адаптируешь под пользователя

Формат:
1. Суть
2. Улучшение
3. Совет
"""

# -------------------
# MENU
# -------------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔥 Похудение"), KeyboardButton(text="⚖️ Масса")],
        [KeyboardButton(text="📊 Профиль"), KeyboardButton(text="💪 Тренировка")],
        [KeyboardButton(text="🥗 Питание")]
    ],
    resize_keyboard=True
)

# -------------------
# AI
# -------------------

async def ai(text):
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
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": text}
                ]
            }
        ) as r:
            data = await r.json()

    # 🔥 если ошибка от API — покажет её полностью
    if "choices" not in data:
        return f"❌ API ERROR:\n{data}"

    return data["choices"][0]["message"]["content"]

# -------------------
# START
# -------------------

@dp.message(CommandStart())
async def start(message: Message):
    uid = str(message.from_user.id)

    if uid not in users:
        users[uid] = {
            "name": message.from_user.first_name,
            "goal": None,
            "history": []
        }
        save_db(users)

    await message.answer(
        f"💪 Привет {users[uid]['name']}! Это FITNESS APP v1",
        reply_markup=menu
    )

# -------------------
# LOGIC
# -------------------

@dp.message()
async def chat(message: Message):
    uid = str(message.from_user.id)
    text = message.text

    if uid not in users:
        users[uid] = {"name": "user", "goal": None, "history": []}

    user = users[uid]

    # -------------------
    # PROFILE
    # -------------------
    if text == "📊 Профиль":
        await message.answer(
            f"👤 Имя: {user['name']}\n"
            f"🎯 Цель: {user['goal']}\n"
            f"📈 Запросов: {len(user['history'])}"
        )
        return

    # -------------------
    # MODES
    # -------------------

    if text == "🔥 Похудение":
        user["goal"] = "похудение"
        plan = PLANS["похудение"]

    elif text == "⚖️ Масса":
        user["goal"] = "масса"
        plan = PLANS["масса"]

    elif text == "💪 Тренировка":
        plan = {"training": PLANS["масса"]["training"], "food": None}

    elif text == "🥗 Питание":
        plan = {"training": None, "food": PLANS["похудение"]["food"]}

    else:
        # обычный AI чат
        answer = await ai(text)
        await message.answer(answer)
        return

    # -------------------
    # BUILD RESPONSE
    # -------------------

    result = ""

    if plan.get("training"):
        result += "💪 ТРЕНИРОВКА:\n" + plan["training"]

    if plan.get("food"):
        result += "\n\n🥗 ПИТАНИЕ:\n" + plan["food"]

    # AI улучшает
    comment = await ai("Улучши этот фитнес план:\n" + result)

    await message.answer(result)
    await message.answer("🧠 AI тренер:\n" + comment)

    # history
    user["history"].append(text)
    users[uid] = user
    save_db(users)

# -------------------
# RUN
# -------------------

async def main():
    print("🚀 FITNESS APP v1 STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
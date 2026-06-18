import os
import json
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

# ---------------- CONFIG ----------------

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN NOT FOUND")
    exit()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DB_FILE = "users.json"

# ---------------- DB ----------------

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

users = load_db()

# ---------------- MENU (APP STYLE) ----------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 СТАРТ")],
        [KeyboardButton(text="🔥 ПОХУДЕНИЕ"), KeyboardButton(text="⚖️ МАССА")],
        [KeyboardButton(text="🏋️ ТРЕНИРОВКИ"), KeyboardButton(text="🥗 ПИТАНИЕ")],
        [KeyboardButton(text="📊 ПРОФИЛЬ"), KeyboardButton(text="💎 PREMIUM")],
        [KeyboardButton(text="📝 АНКЕТА")]
    ],
    resize_keyboard=True
)

# ---------------- TRAINING ----------------

TRAININGS = {
    "похудение": {
        "home": "🏃 Дом: прыжки + планка + присед",
        "gym": "🔥 Зал: дорожка + эллипс + пресс",
        "cardio": "🚴 Кардио: бег 30-40 мин"
    },
    "масса": {
        "home": "💪 Отжимания + присед + брусья",
        "gym": "🏋️ Жим + тяга + присед + бицепс",
        "cardio": "⚡ Лёгкое кардио 15 мин"
    }
}

# ---------------- FOOD WITH IMAGES ----------------

FOOD = {
    "похудение": [
        ("🥗 Овощи", "https://images.unsplash.com/photo-1556911220-e15b29be8c8f"),
        ("🐟 Рыба", "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2"),
        ("🍎 Фрукты", "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce")
    ],
    "масса": [
        ("🍗 Курица", "https://images.unsplash.com/photo-1604908177223-8d7c6c5a3f63"),
        ("🍚 Рис", "https://images.unsplash.com/photo-1600628422019-6d5a2a5f8c6d"),
        ("🥚 Яйца", "https://images.unsplash.com/photo-1587049352851-8d4e89133924")
    ]
}

# ---------------- START ----------------

@dp.message(CommandStart())
async def start(message: Message):

    uid = str(message.from_user.id)

    if uid not in users:
        users[uid] = {
            "name": message.from_user.first_name,
            "goal": None,
            "premium": False,
            "step": None
        }
        save_db(users)

    await message.answer(
        f"🔥 FITNESS V14 APP\nПривет {users[uid]['name']} 💪",
        reply_markup=menu
    )

# ---------------- ROUTER ----------------

@dp.message()
async def router(message: Message):

    uid = str(message.from_user.id)
    text = message.text

    if uid not in users:
        return

    user = users[uid]

    # ---------------- START ----------------
    if text == "🏠 СТАРТ":
        await message.answer("🏠 Главное меню 🔥", reply_markup=menu)
        return

    # ---------------- GOALS ----------------
    if text == "🔥 ПОХУДЕНИЕ":
        user["goal"] = "похудение"
        save_db(users)
        await message.answer("🎯 ЦЕЛЬ: ПОХУДЕНИЕ")
        return

    if text == "⚖️ МАССА":
        user["goal"] = "масса"
        save_db(users)
        await message.answer("🎯 ЦЕЛЬ: МАССА")
        return

    # ---------------- TRAINING ----------------
    if text == "🏋️ ТРЕНИРОВКИ":

        if not user.get("goal"):
            await message.answer("❗ Сначала выбери цель")
            return

        t = TRAININGS[user["goal"]]

        await message.answer(
            "🏋️ ТРЕНИРОВКИ:\n\n"
            f"🏠 Дом:\n{t['home']}\n\n"
            f"🏋️ Зал:\n{t['gym']}\n\n"
            f"🚴 Кардио:\n{t['cardio']}"
        )
        return

    # ---------------- FOOD ----------------
    if text == "🥗 ПИТАНИЕ":

        if not user.get("goal"):
            await message.answer("❗ Сначала выбери цель")
            return

        items = FOOD[user["goal"]]

        msg = "🥗 ПИТАНИЕ:\n\n"

        for name, img in items:
            msg += f"{name}\n{img}\n\n"

        await message.answer(msg)
        return

    # ---------------- PROFILE ----------------
    if text == "📊 ПРОФИЛЬ":
        await message.answer(
            f"👤 {user['name']}\n"
            f"🎯 {user.get('goal')}\n"
            f"💎 Premium: {user.get('premium', False)}"
        )
        return

    # ---------------- PREMIUM ----------------
    if text == "💎 PREMIUM":
        if user.get("premium"):
            await message.answer("💎 Premium активен 🔥")
        else:
            await message.answer("💎 Premium: BUY")
        return

    if text == "BUY":
        user["premium"] = True
        save_db(users)
        await message.answer("💎 Premium активирован!")
        return

    # ---------------- ANKETA ----------------
    if text == "📝 АНКЕТА":
        user["step"] = "weight"
        save_db(users)
        await message.answer("⚖️ Введи вес")
        return

    if user.get("step") == "weight":
        user["weight"] = text
        user["step"] = "height"
        save_db(users)
        await message.answer("📏 Введи рост")
        return

    if user.get("step") == "height":
        user["height"] = text
        user["step"] = "age"
        save_db(users)
        await message.answer("🎂 Введи возраст")
        return

    if user.get("step") == "age":
        user["age"] = text
        user["step"] = None
        save_db(users)
        await message.answer("✅ АНКЕТА ГОТОВА 🔥")
        return

    # ---------------- FALLBACK ----------------
    await message.answer("👇 Используй меню", reply_markup=menu)

# ---------------- RUN ----------------

async def main():
    print("🚀 FITNESS V14 APP STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
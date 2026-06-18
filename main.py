import os
import json
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DB_FILE = "users.json"

# ---------------- DB ----------------

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

users = load_db()

# ---------------- MENU ----------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔥 Похудение"), KeyboardButton(text="⚖️ Масса")],
        [KeyboardButton(text="💪 Тренировки"), KeyboardButton(text="🥗 Питание")],
        [KeyboardButton(text="💎 Premium"), KeyboardButton(text="📊 Профиль")],
        [KeyboardButton(text="📝 Анкета")]
    ],
    resize_keyboard=True
)

# ---------------- TRAINING ----------------

def get_training(goal, premium):
    base = {
        "похудение": "🏃 Бег 25-30 мин\n🏋️ Присед 3x15\n🔥 Планка 60 сек",
        "масса": "🏋️ Жим 4x8\n🏋️ Присед 4x10\n💪 Тяга 4x10"
    }

    pro = {
        "похудение": base["похудение"] + "\n🔥 HIIT интервалы + ускорения",
        "масса": base["масса"] + "\n💪 PUSH/PULL/LEGS система + прогрессия"
    }

    return pro if premium else base

# ---------------- START ----------------

@dp.message(CommandStart())
async def start(message: Message):
    uid = str(message.from_user.id)

    if uid not in users:
        users[uid] = {
            "name": message.from_user.first_name,
            "goal": None,
            "weight": None,
            "height": None,
            "age": None,
            "premium": False,
            "step": None,
            "history": []
        }
        save_db(users)

    await message.answer(
        f"💪 Привет {users[uid]['name']}!\n"
        f"Mans Fitness V9 🔥",
        reply_markup=menu
    )

# ---------------- ROUTER (ВАЖНО) ----------------

@dp.message()
async def router(message: Message):
    uid = str(message.from_user.id)
    text = message.text

    print("DEBUG:", uid, text)

    if uid not in users:
        return

    user = users[uid]

    # ---------------- PREMIUM ----------------
    if text == "💎 Premium":
        if user["premium"]:
            await message.answer("💎 Premium уже активен 🔥")
        else:
            await message.answer("💎 Premium: BUY чтобы активировать")
        return

    if text == "BUY":
        user["premium"] = True
        save_db(users)
        await message.answer("💎 Premium активирован!")
        return

    # ---------------- GOALS ----------------
    if text == "🔥 Похудение":
        user["goal"] = "похудение"
        await message.answer("🎯 Цель: похудение сохранена")
        return

    if text == "⚖️ Масса":
        user["goal"] = "масса"
        await message.answer("🎯 Цель: масса сохранена")
        return

    # ---------------- TRAINING (ВАЖНО ФИКС) ----------------
    if text == "💪 Тренировки":
        training = get_training(user.get("goal"), user.get("premium", False))
        result = training.get(user.get("goal", "похудение"))

        await message.answer("💪 ТВОЯ ТРЕНИРОВКА:\n\n" + result)
        return

    # ---------------- FOOD ----------------
    if text == "🥗 Питание":
        await message.answer(
            "🥗 Питание:\n\n"
            "🍗 Белок: курица, яйца, рыба\n"
            "🍚 Углеводы: рис, овсянка\n"
            "🥑 Жиры: орехи, авокадо\n"
        )
        return

    # ---------------- PROFILE ----------------
    if text == "📊 Профиль":
        await message.answer(
            f"👤 {user['name']}\n"
            f"🎯 {user['goal']}\n"
            f"💎 Premium: {user['premium']}"
        )
        return

    # ---------------- ANKETA ----------------
    if text == "📝 Анкета":
        user["step"] = "weight"
        await message.answer("⚖️ Введи вес:")
        save_db(users)
        return

    if user.get("step") == "weight":
        user["weight"] = text
        user["step"] = "height"
        await message.answer("📏 Введи рост:")
        save_db(users)
        return

    if user.get("step") == "height":
        user["height"] = text
        user["step"] = "age"
        await message.answer("🎂 Введи возраст:")
        save_db(users)
        return

    if user.get("step") == "age":
        user["age"] = text
        user["step"] = None
        save_db(users)
        await message.answer("✅ Анкета готова!")
        return

    # ---------------- DEFAULT ----------------
    await message.answer("❗ Выбери кнопку из меню 👇", reply_markup=menu)

    user["history"].append(text)
    users[uid] = user
    save_db(users)

# ---------------- RUN ----------------

async def main():
    print("🚀 MANS FITNESS V9 STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
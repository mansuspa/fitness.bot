import os
import json
import asyncio
from aiogram import Bot, Dispatcher
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

# ---------------- PREMIUM ----------------

def is_premium(user):
    return user.get("premium", False)

# ---------------- CALCULATIONS ----------------

def calc_calories(w, h, a, goal):
    bmr = 10*w + 6.25*h - 5*a + 5

    if goal == "похудение":
        return int(bmr * 1.2 - 450)
    if goal == "масса":
        return int(bmr * 1.2 + 450)
    return int(bmr * 1.2)

def calc_bju(cal):
    return (
        int(cal * 0.30 / 4),
        int(cal * 0.25 / 9),
        int(cal * 0.45 / 4)
    )

# ---------------- TRAINING ENGINE ----------------

def get_training(goal, premium):
    base = {
        "похудение": "🏃 Кардио 30 мин\n🏋️ Присед 3x15\n🔥 Планка 60 сек",
        "масса": "🏋️ Жим 4x8\n🏋️ Присед 4x10\n💪 Тяга 4x10"
    }

    pro = {
        "похудение": base["похудение"] + "\n🔥 HIIT + интервалы + ускорения",
        "масса": base["масса"] + "\n💪 PUSH/PULL/LEGS + прогрессия веса"
    }

    return pro if premium else base

# ---------------- MENU ----------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔥 Похудение"), KeyboardButton(text="⚖️ Масса")],
        [KeyboardButton(text="💪 Тренировки"), KeyboardButton(text="📊 Профиль")],
        [KeyboardButton(text="💎 Premium"), KeyboardButton(text="📝 Анкета")]
    ],
    resize_keyboard=True
)

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
            "weight_history": [],
            "premium": False,
            "step": None
        }
        save_db(users)

    await message.answer(
        f"💪 Привет {users[uid]['name']}!\n"
        f"Mans Fitness V8 🔥",
        reply_markup=menu
    )

# ---------------- MAIN LOGIC ----------------

@dp.message()
async def handler(message: Message):
    uid = str(message.from_user.id)
    text = message.text

    if uid not in users:
        return

    user = users[uid]

    # -------- PREMIUM --------
    if text == "💎 Premium":
        if user["premium"]:
            await message.answer("💎 Premium уже активен 🔥")
        else:
            await message.answer(
                "💎 PREMIUM\n\n"
                "🔥 PRO тренировки\n"
                "🥗 расширенное питание\n"
                "📊 аналитика тела\n\n"
                "💰 Цена: 5$/мес\n"
                "👉 Напиши BUY"
            )
        return

    if text == "BUY":
        user["premium"] = True
        save_db(users)
        await message.answer("💎 Premium активирован!")
        return

    # -------- GOALS --------
    if text == "🔥 Похудение":
        user["goal"] = "похудение"

    if text == "⚖️ Масса":
        user["goal"] = "масса"

    # -------- ANKETA FLOW --------
    if text == "📝 Анкета":
        user["step"] = "weight"
        await message.answer("⚖️ Введи вес (кг):")
        save_db(users)
        return

    if user.get("step") == "weight":
        user["weight"] = int(text)
        user["step"] = "height"
        await message.answer("📏 Введи рост (см):")
        save_db(users)
        return

    if user.get("step") == "height":
        user["height"] = int(text)
        user["step"] = "age"
        await message.answer("🎂 Введи возраст:")
        save_db(users)
        return

    if user.get("step") == "age":
        user["age"] = int(text)
        user["step"] = None

        # сохраняем вес в историю
        user["weight_history"].append(user["weight"])

        save_db(users)
        await message.answer("✅ Анкета заполнена!")
        return

    # -------- PROFILE --------
    if text == "📊 Профиль":
        if None in [user["weight"], user["height"], user["age"]]:
            await message.answer("❗ Сначала заполни анкету")
            return

        cal = calc_calories(
            user["weight"],
            user["height"],
            user["age"],
            user["goal"]
        )

        b, f, c = calc_bju(cal)

        await message.answer(
            f"👤 {user['name']}\n"
            f"🎯 {user['goal']}\n"
            f"💎 Premium: {user['premium']}\n\n"
            f"⚖️ Вес: {user['weight']} кг\n"
            f"📏 Рост: {user['height']} см\n"
            f"🎂 Возраст: {user['age']}\n\n"
            f"🔥 Калории: {cal}\n"
            f"🥩 Б:{b} Ж:{f} У:{c}\n\n"
            f"📈 История веса: {user['weight_history']}"
        )
        return

    # -------- TRAINING --------
    if text == "💪 Тренировки":
        training = get_training(user.get("goal"), user.get("premium", False))
        await message.answer(training)
        return

    # fallback
    await message.answer("Выбери меню 👇", reply_markup=menu)

    user["history"] = user.get("history", []) + [text]
    users[uid] = user
    save_db(users)

# ---------------- RUN ----------------

async def main():
    print("🚀 MANS FITNESS V8 STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
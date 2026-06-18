import os
import json
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

# ---------------- LOGGING ----------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ---------------- BOT ----------------

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN NOT FOUND")
    exit()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------------- DB ----------------

DB_FILE = "users.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        logging.error(f"DB ERROR: {e}")

users = load_db()

# ---------------- USER ----------------

def get_user(uid, name):
    if uid not in users:
        users[uid] = {
            "name": name,
            "goal": None,
            "premium": False
        }
        save_db(users)
    return users[uid]

# ---------------- MENU ----------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 СТАРТ")],
        [KeyboardButton(text="🔥 ПОХУДЕНИЕ"), KeyboardButton(text="⚖️ МАССА")],
        [KeyboardButton(text="🏋️ ТРЕНИРОВКИ"), KeyboardButton(text="🥗 ПИТАНИЕ")],
        [KeyboardButton(text="📊 ПРОФИЛЬ"), KeyboardButton(text="💎 PREMIUM")]
    ],
    resize_keyboard=True
)

# ---------------- AI TRAINER ----------------

def ai_trainer(user, text):

    goal = user.get("goal")

    if not goal:
        return "❗ Сначала выбери цель: похудение или масса"

    if goal == "fat_loss":
        return (
            "🤖 ТВОЙ ТРЕНЕР\n\n"
            f"Ты написал: {text}\n\n"
            "🔥 ПОХУДЕНИЕ:\n"
            "• Кардио 25–35 минут\n"
            "• 3–4 силовые тренировки в неделю\n"
            "• Дефицит калорий\n\n"
            "💡 Держи пульс 120–140"
        )

    return (
        "🤖 ТВОЙ ТРЕНЕР\n\n"
        f"Ты написал: {text}\n\n"
        "💪 МАССА:\n"
        "• База: жим / присед / тяга\n"
        "• 8–12 повторений\n"
        "• Профицит калорий\n\n"
        "📈 Прогрессия веса каждую неделю"
    )

# ---------------- START ----------------

@dp.message(CommandStart())
async def start(message: Message):

    try:
        uid = str(message.from_user.id)
        user = get_user(uid, message.from_user.first_name)

        await message.answer(
            f"💪 FITNESS AI TRAINER PRO\n"
            f"Привет {user['name']} 🔥",
            reply_markup=menu
        )

    except Exception as e:
        logging.error(f"START ERROR: {e}")

# ---------------- ROUTER ----------------

@dp.message()
async def router(message: Message):

    try:
        uid = str(message.from_user.id)
        text = message.text or ""

        user = get_user(uid, message.from_user.first_name)

        # ---------------- MENU ----------------
        if text == "🏠 СТАРТ":
            await message.answer("🏠 Главное меню", reply_markup=menu)
            return

        # ---------------- GOALS ----------------
        if text == "🔥 ПОХУДЕНИЕ":
            user["goal"] = "fat_loss"
            save_db(users)
            await message.answer("🎯 Цель: ПОХУДЕНИЕ")
            return

        if text == "⚖️ МАССА":
            user["goal"] = "mass"
            save_db(users)
            await message.answer("🎯 Цель: МАССА")
            return

        # ---------------- TRAINING ----------------
        if text == "🏋️ ТРЕНИРОВКИ":

            if not user.get("goal"):
                await message.answer("❗ Сначала выбери цель")
                return

            if user["goal"] == "fat_loss":
                plan = (
                    "🔥 ЖИРОСЖИГАНИЕ\n\n"
                    "🏃 Кардио — 25–35 мин\n\n"
                    "🏋️ Приседания — 4 × 15\n"
                    "⏱ Отдых: 60 сек\n\n"
                    "🧱 Планка — 3 × 60 сек"
                )
            else:
                plan = (
                    "💪 МАССА\n\n"
                    "🏋️ Жим — 4 × 8–10\n"
                    "⏱ Отдых: 90–120 сек\n\n"
                    "🏋️ Присед — 4 × 8–10\n"
                    "💪 Тяга — 4 × 8"
                )

            if user.get("premium"):
                plan += "\n\n💎 PREMIUM: PUSH/PULL/LEGS"

            await message.answer(plan)
            return

        # ---------------- FOOD ----------------
        if text == "🥗 ПИТАНИЕ":

            if user.get("goal") == "mass":
                food = (
                    "🍗 Курица — 200–250 г\n"
                    "🍚 Рис — 150–200 г\n"
                    "🥚 Яйца — 3–5 шт\n"
                    "🥛 Творог — 150 г"
                )
            else:
                food = (
                    "🥗 Овощи — 300–500 г\n"
                    "🐟 Рыба — 150–200 г\n"
                    "🍎 Фрукты — 1–2 шт"
                )

            await message.answer("🥗 ПИТАНИЕ:\n\n" + food)
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
                await message.answer("💎 Уже активен")
            else:
                await message.answer("💎 Напиши BUY")
            return

        if text == "BUY":
            user["premium"] = True
            save_db(users)
            await message.answer("💎 PREMIUM АКТИВИРОВАН 🚀")
            return

        # ---------------- AI TRAINER ----------------
        answer = ai_trainer(user, text)
        await message.answer(answer)
        return

    except Exception as e:
        logging.error(f"ROUTER ERROR: {e}")
        await message.answer("⚠️ Ошибка, попробуй снова")

# ---------------- RUN ----------------

async def main():
    logging.info("🚀 FITNESS AI TRAINER PRO STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
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

# ---------------- GLOBAL ERROR HANDLER ----------------

@dp.errors()
async def error_handler(update, exception):
    logging.error(f"GLOBAL ERROR: {exception}")
    return True

# ---------------- DB SAFE ----------------

DB_FILE = "users.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"DB LOAD ERROR: {e}")
        return {}

def save_db(data):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        logging.error(f"DB SAVE ERROR: {e}")

users = load_db()

# ---------------- SAFE USER ----------------

def get_user(uid, name):
    if uid not in users:
        users[uid] = {
            "name": name,
            "goal": None,
            "premium": False,
            "step": None
        }
        save_db(users)

    return users[uid]

# ---------------- MENU ----------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 HOME")],
        [KeyboardButton(text="🔥 FAT LOSS"), KeyboardButton(text="⚖️ MASS")],
        [KeyboardButton(text="🏋️ WORKOUT"), KeyboardButton(text="🥗 FOOD")],
        [KeyboardButton(text="📊 PROFILE"), KeyboardButton(text="💎 PREMIUM")]
    ],
    resize_keyboard=True
)

# ---------------- START ----------------

@dp.message(CommandStart())
async def start(message: Message):

    try:
        uid = str(message.from_user.id)
        user = get_user(uid, message.from_user.first_name)

        await message.answer(
            f"🚀 SAAS FITNESS BOT V2\n"
            f"Привет {user['name']} 💪",
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

        # ---------------- HOME ----------------
        if text == "🏠 HOME":
            await message.answer("🏠 Menu", reply_markup=menu)
            return

        # ---------------- GOALS ----------------
        if text == "🔥 FAT LOSS":
            user["goal"] = "fat_loss"
            save_db(users)
            await message.answer("🎯 FAT LOSS selected")
            return

        if text == "⚖️ MASS":
            user["goal"] = "mass"
            save_db(users)
            await message.answer("🎯 MASS selected")
            return

        # ---------------- WORKOUT ----------------
        if text == "🏋️ WORKOUT":

            if not user.get("goal"):
                await message.answer("❗ Choose goal first")
                return

            if user["goal"] == "fat_loss":
                plan = "🏃 Cardio 30 min\n🔥 Squats\n🧱 Plank"
            else:
                plan = "🏋️ Bench press\n🏋️ Squats\n💪 Deadlift"

            if user.get("premium", False):
                plan += "\n\n💎 PREMIUM:\nHIIT + advanced split"

            await message.answer("💪 WORKOUT:\n\n" + plan)
            return

        # ---------------- FOOD ----------------
        if text == "🥗 FOOD":

            if user.get("goal") == "mass":
                food = "🍗 Chicken\n🍚 Rice\n🥚 Eggs"
            else:
                food = "🥗 Vegetables\n🐟 Fish\n🍎 Fruits"

            await message.answer("🥗 FOOD:\n\n" + food)
            return

        # ---------------- PROFILE ----------------
        if text == "📊 PROFILE":

            await message.answer(
                f"👤 {user.get('name')}\n"
                f"🎯 {user.get('goal')}\n"
                f"💎 Premium: {user.get('premium', False)}"
            )
            return

        # ---------------- PREMIUM ----------------
        if text == "💎 PREMIUM":

            if user.get("premium"):
                await message.answer("💎 Already active 🔥")
            else:
                await message.answer("💎 Type BUY to activate")
            return

        if text == "BUY":
            user["premium"] = True
            save_db(users)
            await message.answer("💎 Premium ACTIVATED 🚀")
            return

        # ---------------- FALLBACK ----------------
        await message.answer("👇 Use menu", reply_markup=menu)

    except Exception as e:
        logging.error(f"ROUTER ERROR: {e}")
        await message.answer("⚠️ Error, try again")

# ---------------- MAIN ----------------

async def main():
    logging.info("🚀 SAAS FITNESS BOT V2 STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())